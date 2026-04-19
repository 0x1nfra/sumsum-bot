"""Typed kill-switch thresholds for risk controls."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KillSwitchSettings:
    """Conservative runtime limits for Phase 3 risk gating."""

    max_drawdown_pct: float = 0.20
    cooldown_minutes: int = 60
    block_unaccepted_signals: bool = True
