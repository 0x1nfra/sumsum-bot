from __future__ import annotations

from pathlib import Path

from core.models import (
    BankrollSnapshot,
    PaperPositionRecord,
    PaperPositionStatus,
    PaperTradeEvent,
)
from core.storage import CandidateStorage
from core.trade_logger import (
    BANKROLL_SNAPSHOT_EVENT,
    PAPER_ENTRY_EVENT,
    PAPER_OPEN_EVENT,
    PAPER_RESOLUTION_EVENT,
)


def test_paper_storage_round_trips_position_event_and_bankroll_snapshots(
    temp_sqlite_db_path: Path,
) -> None:
    storage = CandidateStorage(temp_sqlite_db_path)
    position = PaperPositionRecord(
        position_id="paper-wx-temp-phx-001",
        market_id="wx-temp-phx-001",
        risk_decision_id=21,
        signal_evaluation_id=11,
        entry_price=0.40,
        stake_usd=5.0,
        contract_count=12.5,
        status=PaperPositionStatus.ENTERED,
        entered_at="2026-04-19T00:00:00Z",
        opened_at=None,
        resolved_at=None,
        resolution_price=None,
        realized_pnl_usd=None,
        evidence={"side": "no", "status": "entered"},
    )
    events = [
        PaperTradeEvent(
            position_id="paper-wx-temp-phx-001",
            event_type=PAPER_ENTRY_EVENT,
            event_timestamp="2026-04-19T00:00:00Z",
            details={"status": "entered"},
        ),
        PaperTradeEvent(
            position_id="paper-wx-temp-phx-001",
            event_type=PAPER_OPEN_EVENT,
            event_timestamp="2026-04-19T00:05:00Z",
            details={"status": "open"},
        ),
        PaperTradeEvent(
            position_id="paper-wx-temp-phx-001",
            event_type=PAPER_RESOLUTION_EVENT,
            event_timestamp="2026-04-19T10:00:00Z",
            details={"status": "resolved"},
        ),
    ]
    snapshots = [
        BankrollSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=120.0,
            available_cash_usd=95.0,
            open_exposure_usd=13.0,
            snapshot_reason=BANKROLL_SNAPSHOT_EVENT,
            captured_at="2026-04-19T00:00:00Z",
        ),
        BankrollSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=120.0,
            available_cash_usd=95.0,
            open_exposure_usd=13.0,
            snapshot_reason=BANKROLL_SNAPSHOT_EVENT,
            captured_at="2026-04-19T00:05:00Z",
        ),
        BankrollSnapshot(
            current_bankroll_usd=107.5,
            peak_bankroll_usd=120.0,
            available_cash_usd=107.5,
            open_exposure_usd=8.0,
            snapshot_reason=BANKROLL_SNAPSHOT_EVENT,
            captured_at="2026-04-19T10:00:00Z",
        ),
    ]

    storage.persist_paper_position(position)
    storage.persist_paper_trade_events(events)
    storage.persist_bankroll_snapshots(snapshots)
    storage.activate_paper_position(
        position_id=position.position_id,
        opened_at="2026-04-19T00:05:00Z",
    )
    storage.update_paper_position_resolution(
        position_id=position.position_id,
        resolved_at="2026-04-19T10:00:00Z",
        resolution_price=1.0,
        realized_pnl_usd=7.5,
    )

    with storage.connect() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
            ).fetchall()
        }
        position_rows = connection.execute(
            """
            SELECT position_id, status, entry_price, stake_usd, contract_count, resolved_at, resolution_price, realized_pnl_usd
            FROM paper_positions
            ORDER BY position_id
            """
        ).fetchall()
        event_rows = connection.execute(
            """
            SELECT position_id, event_type, event_timestamp
            FROM paper_trade_events
            ORDER BY id
            """
        ).fetchall()
        snapshot_rows = connection.execute(
            """
            SELECT current_bankroll_usd, peak_bankroll_usd, available_cash_usd, open_exposure_usd, snapshot_reason, captured_at
            FROM bankroll_snapshots
            ORDER BY id
            """
        ).fetchall()

    assert "paper_positions" in tables
    assert "paper_trade_events" in tables
    assert "bankroll_snapshots" in tables
    assert [tuple(row) for row in position_rows] == [
        ("paper-wx-temp-phx-001", "resolved", 0.4, 5.0, 12.5, "2026-04-19T10:00:00Z", 1.0, 7.5),
    ]
    assert [tuple(row) for row in event_rows] == [
        ("paper-wx-temp-phx-001", "paper_entry", "2026-04-19T00:00:00Z"),
        ("paper-wx-temp-phx-001", "paper_open", "2026-04-19T00:05:00Z"),
        ("paper-wx-temp-phx-001", "paper_resolution", "2026-04-19T10:00:00Z"),
    ]
    assert [tuple(row) for row in snapshot_rows] == [
        (100.0, 120.0, 95.0, 13.0, "bankroll_snapshot", "2026-04-19T00:00:00Z"),
        (100.0, 120.0, 95.0, 13.0, "bankroll_snapshot", "2026-04-19T00:05:00Z"),
        (107.5, 120.0, 107.5, 8.0, "bankroll_snapshot", "2026-04-19T10:00:00Z"),
    ]

    open_positions = storage.list_open_paper_positions()
    assert open_positions == []
    assert [record.status for record in storage.list_paper_positions()] == [
        PaperPositionStatus.RESOLVED,
    ]
    assert [event.event_type for event in storage.list_paper_trade_events("paper-wx-temp-phx-001")] == [
        "paper_entry",
        "paper_open",
        "paper_resolution",
    ]
    assert [snapshot.snapshot_reason for snapshot in storage.list_bankroll_snapshots()] == [
        "bankroll_snapshot",
        "bankroll_snapshot",
        "bankroll_snapshot",
    ]
