"""Backtesting boundary reserved for historical replay phases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestSummary:
    """Placeholder summary shape for future historical runs."""

    runs: int = 0
    message: str = "backtester not implemented yet"
