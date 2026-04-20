from __future__ import annotations

import pytest

from core.models import (
    BankrollSnapshot,
    PaperPositionRecord,
    PaperPositionStatus,
    RiskDecisionRecord,
    RiskDecisionStatus,
)
from core.paper_execution import (
    activate_position,
    create_paper_entry,
    settle_position,
)
from core.trade_logger import (
    BANKROLL_SNAPSHOT_EVENT,
    PAPER_ENTRY_EVENT,
    PAPER_OPEN_EVENT,
    PAPER_RESOLUTION_EVENT,
)


def test_create_paper_entry_records_entered_state_at_current_no_price() -> None:
    decision = _allowed_risk_decision()

    position, events, snapshots = create_paper_entry(
        risk_decision=decision,
        no_price=0.40,
        captured_at="2026-04-19T00:00:00Z",
    )

    assert isinstance(position, PaperPositionRecord)
    assert position.market_id == "wx-temp-phx-001"
    assert position.risk_decision_id is None
    assert position.signal_evaluation_id == 11
    assert position.entry_price == pytest.approx(0.40)
    assert position.stake_usd == pytest.approx(5.0)
    assert position.contract_count == pytest.approx(12.5)
    assert position.status is PaperPositionStatus.ENTERED
    assert position.entered_at == "2026-04-19T00:00:00Z"
    assert position.opened_at is None
    assert position.resolved_at is None
    assert position.resolution_price is None
    assert position.realized_pnl_usd is None
    assert position.evidence["window_key"] == "2026-04-18T00:00:00-07:00"

    assert len(events) == 1
    assert events[0].event_type == PAPER_ENTRY_EVENT
    assert events[0].event_type == "paper_entry"
    assert events[0].event_timestamp == "2026-04-19T00:00:00Z"
    assert events[0].details["status"] == "entered"

    assert len(snapshots) == 1
    assert isinstance(snapshots[0], BankrollSnapshot)
    assert snapshots[0].current_bankroll_usd == pytest.approx(100.0)
    assert snapshots[0].peak_bankroll_usd == pytest.approx(120.0)
    assert snapshots[0].available_cash_usd == pytest.approx(95.0)
    assert snapshots[0].open_exposure_usd == pytest.approx(13.0)
    assert snapshots[0].snapshot_reason == BANKROLL_SNAPSHOT_EVENT
    assert snapshots[0].captured_at == "2026-04-19T00:00:00Z"


def test_activate_position_transitions_entered_position_to_open_without_second_cash_movement() -> None:
    entered_position, _, entry_snapshots = create_paper_entry(
        risk_decision=_allowed_risk_decision(),
        no_price=0.40,
        captured_at="2026-04-19T00:00:00Z",
    )

    position, events, snapshots = activate_position(
        position=entered_position,
        bankroll_snapshot=entry_snapshots[-1],
        activated_at="2026-04-19T00:05:00Z",
    )

    assert position.position_id == entered_position.position_id
    assert position.status is PaperPositionStatus.OPEN
    assert position.entered_at == entered_position.entered_at
    assert position.opened_at == "2026-04-19T00:05:00Z"
    assert position.resolved_at is None

    assert len(events) == 1
    assert events[0].event_type == PAPER_OPEN_EVENT
    assert events[0].event_type == "paper_open"
    assert events[0].details["prior_status"] == "entered"
    assert events[0].details["status"] == "open"

    assert len(snapshots) == 1
    assert snapshots[0].current_bankroll_usd == pytest.approx(entry_snapshots[-1].current_bankroll_usd)
    assert snapshots[0].peak_bankroll_usd == pytest.approx(entry_snapshots[-1].peak_bankroll_usd)
    assert snapshots[0].available_cash_usd == pytest.approx(entry_snapshots[-1].available_cash_usd)
    assert snapshots[0].open_exposure_usd == pytest.approx(entry_snapshots[-1].open_exposure_usd)
    assert snapshots[0].snapshot_reason == BANKROLL_SNAPSHOT_EVENT


def test_settle_paper_position_updates_realized_pnl_and_bankroll_snapshot() -> None:
    entered_position, _, entry_snapshots = create_paper_entry(
        risk_decision=_allowed_risk_decision(),
        no_price=0.40,
        captured_at="2026-04-19T00:00:00Z",
    )
    open_position, _, open_snapshots = activate_position(
        position=entered_position,
        bankroll_snapshot=entry_snapshots[-1],
        activated_at="2026-04-19T00:05:00Z",
    )

    position, events, snapshots = settle_position(
        position=open_position,
        bankroll_snapshot=open_snapshots[-1],
        settled_yes=False,
        settled_at="2026-04-19T10:00:00Z",
    )

    assert position.status is PaperPositionStatus.RESOLVED
    assert position.resolved_at == "2026-04-19T10:00:00Z"
    assert position.resolution_price == pytest.approx(1.0)
    assert position.realized_pnl_usd == pytest.approx(7.5)

    assert len(events) == 1
    assert events[0].event_type == PAPER_RESOLUTION_EVENT
    assert events[0].event_type == "paper_resolution"
    assert events[0].details["status"] == "resolved"
    assert events[0].details["resolution_price"] == pytest.approx(1.0)

    assert len(snapshots) == 1
    assert snapshots[0].current_bankroll_usd == pytest.approx(107.5)
    assert snapshots[0].peak_bankroll_usd == pytest.approx(120.0)
    assert snapshots[0].available_cash_usd == pytest.approx(107.5)
    assert snapshots[0].open_exposure_usd == pytest.approx(8.0)
    assert snapshots[0].snapshot_reason == BANKROLL_SNAPSHOT_EVENT


def _allowed_risk_decision() -> RiskDecisionRecord:
    return RiskDecisionRecord(
        signal_evaluation_id=11,
        market_id="wx-temp-phx-001",
        window_key="2026-04-18T00:00:00-07:00",
        decision_status=RiskDecisionStatus.ALLOWED,
        decision_reason="edge_threshold_passed",
        triggered_rule_codes=(),
        current_bankroll_usd=100.0,
        peak_bankroll_usd=120.0,
        open_exposure_usd=8.0,
        window_exposure_usd=3.0,
        proposed_stake_usd=5.0,
        allowed_stake_usd=5.0,
        evidence={
            "signal_status": "accepted",
            "position_side": "no",
            "market_id": "wx-temp-phx-001",
            "window_key": "2026-04-18T00:00:00-07:00",
        },
    )
