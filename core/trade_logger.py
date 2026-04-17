"""Trade logging boundary reserved for paper-trading phases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeLogEntry:
    """Placeholder log entry shape for later execution phases."""

    event_type: str = "placeholder"
    message: str = "trade logger not implemented yet"
