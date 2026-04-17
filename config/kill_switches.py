"""Placeholder kill-switch configuration boundary for later risk phases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KillSwitchSettings:
    """Conservative default limits for future paper-trading safeguards."""

    max_drawdown_pct: float = 0.20
    max_loss_streak: int = 5
    pause_minutes_after_trigger: int = 60
