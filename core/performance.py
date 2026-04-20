"""Durable forward-test analytics over paper-trading ledger history."""

from __future__ import annotations

from core.models import BankrollSnapshot, ForwardTestMetrics, PaperPositionRecord


def calculate_forward_test_metrics(
    bankroll_snapshots: list[BankrollSnapshot],
    resolved_positions: list[PaperPositionRecord],
    *,
    starting_bankroll_usd: float = 0.0,
) -> ForwardTestMetrics:
    if bankroll_snapshots:
        starting_bankroll = bankroll_snapshots[0].current_bankroll_usd
        current_bankroll_usd = bankroll_snapshots[-1].current_bankroll_usd
    else:
        starting_bankroll = starting_bankroll_usd
        current_bankroll_usd = starting_bankroll_usd

    bankroll_delta_usd = current_bankroll_usd - starting_bankroll
    cumulative_return_pct = _pct_change(
        base_value=starting_bankroll,
        current_value=current_bankroll_usd,
    )
    max_drawdown_pct, drawdown_recovery_steps = _drawdown_metrics(bankroll_snapshots)
    resolved_trade_count = len(resolved_positions)
    winning_positions = sum(
        1
        for position in resolved_positions
        if (position.realized_pnl_usd or 0.0) > 0.0
    )
    win_rate_pct = _ratio_pct(winning_positions, resolved_trade_count)

    return ForwardTestMetrics(
        starting_bankroll_usd=round(starting_bankroll, 4),
        current_bankroll_usd=round(current_bankroll_usd, 4),
        bankroll_delta_usd=round(bankroll_delta_usd, 4),
        cumulative_return_pct=round(cumulative_return_pct, 4),
        max_drawdown_pct=round(max_drawdown_pct, 4),
        drawdown_recovery_steps=drawdown_recovery_steps,
        resolved_trade_count=resolved_trade_count,
        win_rate_pct=round(win_rate_pct, 4),
    )


def _pct_change(*, base_value: float, current_value: float) -> float:
    if base_value == 0.0:
        return 0.0
    return ((current_value - base_value) / base_value) * 100.0


def _ratio_pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100.0


def _drawdown_metrics(bankroll_snapshots: list[BankrollSnapshot]) -> tuple[float, int]:
    peak_value = 0.0
    peak_index = -1
    max_drawdown_pct = 0.0
    drawdown_recovery_steps = 0

    for index, snapshot in enumerate(bankroll_snapshots):
        current_value = snapshot.current_bankroll_usd
        if current_value > peak_value:
            peak_value = current_value
            peak_index = index
            continue

        if peak_value <= 0.0:
            continue

        drawdown_pct = ((peak_value - current_value) / peak_value) * 100.0
        if drawdown_pct <= max_drawdown_pct:
            continue

        max_drawdown_pct = drawdown_pct
        drawdown_recovery_steps = 0
        for recovery_index in range(index + 1, len(bankroll_snapshots)):
            recovery_value = bankroll_snapshots[recovery_index].current_bankroll_usd
            if recovery_value >= peak_value:
                drawdown_recovery_steps = recovery_index - index
                break

    return max_drawdown_pct, drawdown_recovery_steps
