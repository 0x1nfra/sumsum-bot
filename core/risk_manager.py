"""Risk policy boundary reserved for later trading phases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskDecision:
    """Placeholder structure for future risk approvals and blocks."""

    allowed: bool = False
    reason: str = "risk manager not implemented yet"
