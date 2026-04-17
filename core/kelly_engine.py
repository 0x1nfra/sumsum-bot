"""Kelly sizing boundary reserved for later risk phases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KellySizingDecision:
    """Placeholder shape for future bankroll sizing results."""

    fraction: float = 0.0
    rationale: str = "kelly sizing not implemented yet"
