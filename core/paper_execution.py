"""Deterministic paper entry, activation, and settlement helpers."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.models import (
    BankrollSnapshot,
    PaperPositionRecord,
    PaperPositionStatus,
    PaperTradeEvent,
    RiskDecisionRecord,
    RiskDecisionStatus,
)
from core.trade_logger import (
    BANKROLL_SNAPSHOT_EVENT,
    PAPER_ENTRY_EVENT,
    PAPER_OPEN_EVENT,
    PAPER_RESOLUTION_EVENT,
)


def create_paper_entry(
    *,
    risk_decision: RiskDecisionRecord,
    no_price: float,
    captured_at: str,
    bankroll_snapshot: BankrollSnapshot | None = None,
    position_id: str | None = None,
    risk_decision_id: int | None = None,
) -> tuple[PaperPositionRecord, list[PaperTradeEvent], list[BankrollSnapshot]]:
    """Create an immediate paper fill from an allowed risk decision."""

    if risk_decision.decision_status is not RiskDecisionStatus.ALLOWED:
        raise ValueError("paper entry requires an allowed risk decision")
    if no_price <= 0.0:
        raise ValueError("paper entry requires a positive no_price")

    stake_usd = risk_decision.allowed_stake_usd
    contract_count = stake_usd / no_price
    paper_position_id = position_id or _paper_position_id(risk_decision.market_id)
    side = str(risk_decision.evidence.get("position_side", "no"))

    position = PaperPositionRecord(
        position_id=paper_position_id,
        market_id=risk_decision.market_id,
        risk_decision_id=risk_decision_id,
        signal_evaluation_id=risk_decision.signal_evaluation_id,
        entry_price=no_price,
        stake_usd=stake_usd,
        contract_count=contract_count,
        status=PaperPositionStatus.ENTERED,
        entered_at=captured_at,
        evidence={
            **risk_decision.evidence,
            "position_side": side,
            "status": PaperPositionStatus.ENTERED.value,
        },
    )
    event = PaperTradeEvent(
        position_id=paper_position_id,
        event_type=PAPER_ENTRY_EVENT,
        event_timestamp=captured_at,
        details={
            "status": PaperPositionStatus.ENTERED.value,
            "entry_price": no_price,
            "stake_usd": stake_usd,
            "contract_count": contract_count,
            "position_side": side,
        },
    )
    starting_snapshot = bankroll_snapshot or BankrollSnapshot(
        current_bankroll_usd=risk_decision.current_bankroll_usd,
        peak_bankroll_usd=risk_decision.peak_bankroll_usd,
        available_cash_usd=risk_decision.current_bankroll_usd,
        open_exposure_usd=risk_decision.open_exposure_usd,
        snapshot_reason=BANKROLL_SNAPSHOT_EVENT,
        captured_at=captured_at,
    )
    snapshot = BankrollSnapshot(
        current_bankroll_usd=starting_snapshot.current_bankroll_usd,
        peak_bankroll_usd=starting_snapshot.peak_bankroll_usd,
        available_cash_usd=starting_snapshot.available_cash_usd - stake_usd,
        open_exposure_usd=starting_snapshot.open_exposure_usd + stake_usd,
        snapshot_reason=BANKROLL_SNAPSHOT_EVENT,
        captured_at=captured_at,
    )
    return position, [event], [snapshot]


def activate_position(
    *,
    position: PaperPositionRecord,
    bankroll_snapshot: BankrollSnapshot,
    activated_at: str,
) -> tuple[PaperPositionRecord, list[PaperTradeEvent], list[BankrollSnapshot]]:
    """Transition a paper position from entered to open without moving cash again."""

    if position.status is not PaperPositionStatus.ENTERED:
        raise ValueError("only entered paper positions can be activated")

    activated_position = replace(
        position,
        status=PaperPositionStatus.OPEN,
        opened_at=activated_at,
        evidence={**position.evidence, "status": PaperPositionStatus.OPEN.value},
    )
    event = PaperTradeEvent(
        position_id=position.position_id,
        event_type=PAPER_OPEN_EVENT,
        event_timestamp=activated_at,
        details={
            "prior_status": PaperPositionStatus.ENTERED.value,
            "status": PaperPositionStatus.OPEN.value,
        },
    )
    snapshot = BankrollSnapshot(
        current_bankroll_usd=bankroll_snapshot.current_bankroll_usd,
        peak_bankroll_usd=bankroll_snapshot.peak_bankroll_usd,
        available_cash_usd=bankroll_snapshot.available_cash_usd,
        open_exposure_usd=bankroll_snapshot.open_exposure_usd,
        snapshot_reason=BANKROLL_SNAPSHOT_EVENT,
        captured_at=activated_at,
    )
    return activated_position, [event], [snapshot]


def settle_position(
    *,
    position: PaperPositionRecord,
    bankroll_snapshot: BankrollSnapshot,
    settled_yes: bool,
    settled_at: str,
) -> tuple[PaperPositionRecord, list[PaperTradeEvent], list[BankrollSnapshot]]:
    """Resolve an open paper position against a terminal market outcome."""

    if position.status is not PaperPositionStatus.OPEN:
        raise ValueError("only open paper positions can be settled")

    side = str(position.evidence.get("position_side", "no"))
    resolution_price = _resolution_price(side=side, settled_yes=settled_yes)
    proceeds_usd = position.contract_count * resolution_price
    realized_pnl_usd = proceeds_usd - position.stake_usd
    current_bankroll_usd = bankroll_snapshot.current_bankroll_usd + realized_pnl_usd
    resolved_position = replace(
        position,
        status=PaperPositionStatus.RESOLVED,
        resolved_at=settled_at,
        resolution_price=resolution_price,
        realized_pnl_usd=realized_pnl_usd,
        evidence={
            **position.evidence,
            "status": PaperPositionStatus.RESOLVED.value,
            "settled_yes": settled_yes,
        },
    )
    event = PaperTradeEvent(
        position_id=position.position_id,
        event_type=PAPER_RESOLUTION_EVENT,
        event_timestamp=settled_at,
        details={
            "status": PaperPositionStatus.RESOLVED.value,
            "resolution_price": resolution_price,
            "realized_pnl_usd": realized_pnl_usd,
            "settled_yes": settled_yes,
        },
    )
    snapshot = BankrollSnapshot(
        current_bankroll_usd=current_bankroll_usd,
        peak_bankroll_usd=max(bankroll_snapshot.peak_bankroll_usd, current_bankroll_usd),
        available_cash_usd=bankroll_snapshot.available_cash_usd + proceeds_usd,
        open_exposure_usd=max(bankroll_snapshot.open_exposure_usd - position.stake_usd, 0.0),
        snapshot_reason=BANKROLL_SNAPSHOT_EVENT,
        captured_at=settled_at,
    )
    return resolved_position, [event], [snapshot]


def _paper_position_id(market_id: str) -> str:
    return f"paper-{market_id}-{uuid4().hex[:8]}"


def _resolution_price(*, side: str, settled_yes: bool) -> float:
    if side == "yes":
        return 1.0 if settled_yes else 0.0
    return 0.0 if settled_yes else 1.0
