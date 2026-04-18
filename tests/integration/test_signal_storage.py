from __future__ import annotations

from pathlib import Path

from core.models import SignalEvaluationRecord, SignalEvaluationStatus
from core.storage import CandidateStorage


def test_signal_storage_appends_accepted_and_rejected_evaluations(
    temp_sqlite_db_path: Path,
) -> None:
    storage = CandidateStorage(temp_sqlite_db_path)

    inserted = storage.persist_signal_evaluations(
        "signal-engine",
        [
            SignalEvaluationRecord(
                market_id="wx-temp-phx-001",
                scan_run_id=1,
                location="Phoenix",
                mapping_city_key="phoenix",
                contract_family="temperature",
                market_date_local="2026-04-18",
                market_window_start_local="2026-04-18T00:00:00-07:00",
                market_window_end_local="2026-04-19T00:00:00-07:00",
                forecast_update_time="2026-04-18T04:00:00+00:00",
                forecast_source_url="https://api.weather.gov/gridpoints/PSR/1,1",
                no_price=0.42,
                derived_yes_probability=0.30,
                derived_no_probability=0.70,
                edge_against_no_price=0.28,
                decision_reason="edge_threshold_passed",
                status=SignalEvaluationStatus.ACCEPTED,
                evidence={"temperature_overlap_values": [112.0]},
            ),
            SignalEvaluationRecord(
                market_id="wx-temp-phx-001",
                scan_run_id=1,
                location="Phoenix",
                mapping_city_key="phoenix",
                contract_family="temperature",
                market_date_local="2026-04-18",
                market_window_start_local="2026-04-18T00:00:00-07:00",
                market_window_end_local="2026-04-19T00:00:00-07:00",
                forecast_update_time="2026-04-18T04:00:00+00:00",
                forecast_source_url="https://api.weather.gov/gridpoints/PSR/1,1",
                no_price=0.42,
                derived_yes_probability=None,
                derived_no_probability=None,
                edge_against_no_price=None,
                decision_reason="noaa_data_stale",
                status=SignalEvaluationStatus.REJECTED,
                evidence={"error": "noaa_data_stale"},
            ),
        ],
    )

    assert inserted == 2

    with storage.connect() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
            ).fetchall()
        }
        rows = connection.execute(
            """
            SELECT market_id, status, mapping_city_key, forecast_update_time, no_price,
                   edge_against_no_price, decision_reason
            FROM signal_evaluations
            ORDER BY id
            """
        ).fetchall()

    assert "signal_evaluations" in tables
    assert [tuple(row) for row in rows] == [
        (
            "wx-temp-phx-001",
            "accepted",
            "phoenix",
            "2026-04-18T04:00:00+00:00",
            0.42,
            0.28,
            "edge_threshold_passed",
        ),
        (
            "wx-temp-phx-001",
            "rejected",
            "phoenix",
            "2026-04-18T04:00:00+00:00",
            0.42,
            None,
            "noaa_data_stale",
        ),
    ]

    assert [record.status for record in storage.list_signal_evaluations("wx-temp-phx-001")] == [
        SignalEvaluationStatus.ACCEPTED,
        SignalEvaluationStatus.REJECTED,
    ]
