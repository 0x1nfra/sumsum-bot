"""Trade logging vocabulary for paper-trading lifecycle events."""

from __future__ import annotations

from dataclasses import dataclass

PAPER_ENTRY_EVENT = "paper_entry"
PAPER_OPEN_EVENT = "paper_open"
PAPER_RESOLUTION_EVENT = "paper_resolution"
BANKROLL_SNAPSHOT_EVENT = "bankroll_snapshot"


@dataclass(frozen=True)
class TradeLogEntry:
    """Typed trade log entry used by the paper ledger boundary."""

    event_type: str
    message: str


def lifecycle_log_entry(event_type: str, position_id: str) -> TradeLogEntry:
    """Create a typed paper lifecycle log entry."""

    return TradeLogEntry(
        event_type=event_type,
        message=f"{event_type} recorded for {position_id}",
    )


def bankroll_log_entry(position_id: str) -> TradeLogEntry:
    """Create a typed bankroll snapshot log entry."""

    return lifecycle_log_entry(BANKROLL_SNAPSHOT_EVENT, position_id)
