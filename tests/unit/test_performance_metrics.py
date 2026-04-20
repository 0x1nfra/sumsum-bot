from __future__ import annotations

from core.models import BankrollSnapshot, PaperPositionRecord, PaperPositionStatus
from core.performance import calculate_forward_test_metrics


def test_forward_test_metrics_compute_cumulative_return_and_bankroll_delta() -> None:
    bankroll_snapshots = [
        BankrollSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=100.0,
            available_cash_usd=100.0,
            open_exposure_usd=0.0,
            snapshot_reason="start",
            captured_at="2026-04-19T00:00:00Z",
        ),
        BankrollSnapshot(
            current_bankroll_usd=108.0,
            peak_bankroll_usd=108.0,
            available_cash_usd=108.0,
            open_exposure_usd=0.0,
            snapshot_reason="end",
            captured_at="2026-04-20T00:00:00Z",
        ),
    ]

    metrics = calculate_forward_test_metrics(
        bankroll_snapshots=bankroll_snapshots,
        resolved_positions=[_resolved_position(realized_pnl_usd=8.0)],
    )

    assert metrics.starting_bankroll_usd == 100.0
    assert metrics.current_bankroll_usd == 108.0
    assert metrics.bankroll_delta_usd == 8.0
    assert metrics.cumulative_return_pct == 8.0


def test_forward_test_metrics_compute_max_drawdown_and_recovery_duration() -> None:
    bankroll_snapshots = [
        BankrollSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=100.0,
            available_cash_usd=100.0,
            open_exposure_usd=0.0,
            snapshot_reason="start",
            captured_at="2026-04-19T00:00:00Z",
        ),
        BankrollSnapshot(
            current_bankroll_usd=110.0,
            peak_bankroll_usd=110.0,
            available_cash_usd=110.0,
            open_exposure_usd=0.0,
            snapshot_reason="peak",
            captured_at="2026-04-19T01:00:00Z",
        ),
        BankrollSnapshot(
            current_bankroll_usd=88.0,
            peak_bankroll_usd=110.0,
            available_cash_usd=88.0,
            open_exposure_usd=0.0,
            snapshot_reason="drawdown",
            captured_at="2026-04-19T02:00:00Z",
        ),
        BankrollSnapshot(
            current_bankroll_usd=111.0,
            peak_bankroll_usd=111.0,
            available_cash_usd=111.0,
            open_exposure_usd=0.0,
            snapshot_reason="recovery",
            captured_at="2026-04-19T03:00:00Z",
        ),
    ]

    metrics = calculate_forward_test_metrics(
        bankroll_snapshots=bankroll_snapshots,
        resolved_positions=[
            _resolved_position(position_id="paper-1", realized_pnl_usd=-22.0),
            _resolved_position(position_id="paper-2", realized_pnl_usd=23.0),
        ],
    )

    assert metrics.max_drawdown_pct == 20.0
    assert metrics.drawdown_recovery_steps > 0


def test_forward_test_metrics_default_to_starting_bankroll_when_ledger_is_empty() -> None:
    metrics = calculate_forward_test_metrics(
        bankroll_snapshots=[],
        resolved_positions=[],
        starting_bankroll_usd=100.0,
    )

    assert metrics.starting_bankroll_usd == 100.0
    assert metrics.current_bankroll_usd == 100.0
    assert metrics.bankroll_delta_usd == 0.0
    assert metrics.cumulative_return_pct == 0.0


def _resolved_position(
    *,
    position_id: str = "paper-001",
    realized_pnl_usd: float,
) -> PaperPositionRecord:
    return PaperPositionRecord(
        position_id=position_id,
        market_id=f"market-{position_id}",
        risk_decision_id=1,
        signal_evaluation_id=1,
        entry_price=0.4,
        stake_usd=5.0,
        contract_count=12.5,
        status=PaperPositionStatus.RESOLVED,
        entered_at="2026-04-19T00:00:00Z",
        opened_at="2026-04-19T00:00:01Z",
        resolved_at="2026-04-19T00:10:00Z",
        resolution_price=1.0 if realized_pnl_usd >= 0 else 0.0,
        realized_pnl_usd=realized_pnl_usd,
        evidence={},
    )
