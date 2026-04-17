from __future__ import annotations

from pathlib import Path

from config.settings import ScanSettings
from core.market_scanner import MarketScanner
from core.storage import CandidateStorage


def _payload_for_task_two(weather_markets: list[dict]) -> dict[str, list[dict]]:
    selected_ids = {
        "wx-temp-phx-001",
        "wx-heat-miami-005",
        "wx-rain-nyc-004",
    }
    return {"markets": [market for market in weather_markets if market["id"] in selected_ids]}


def test_market_scan_persists_accepted_review_and_rejected_candidates(
    weather_markets: list[dict],
    temp_sqlite_db_path: Path,
) -> None:
    settings = ScanSettings(
        database_path=str(temp_sqlite_db_path),
        max_resolution_hours=200,
    )
    scanner = MarketScanner(settings=settings)
    storage = CandidateStorage.from_settings(settings)

    result = scanner.run_scan(_payload_for_task_two(weather_markets), storage=storage)

    assert result.scan_run_id is not None
    assert result.counts == {"accepted": 1, "review": 1, "rejected": 1}
    assert [candidate.market_id for candidate in result.approved] == ["wx-temp-phx-001"]
    assert [candidate.market_id for candidate in result.review] == ["wx-heat-miami-005"]
    assert [candidate.market_id for candidate in result.rejected] == ["wx-rain-nyc-004"]
    assert result.rejected[0].rejection_reasons == ("price_above_ceiling",)

    with storage.connect() as connection:
        run_row = connection.execute(
            """
            SELECT candidate_count, approved_count, review_count, rejected_count
            FROM scan_runs
            WHERE id = ?
            """,
            (result.scan_run_id,),
        ).fetchone()
        candidate_rows = connection.execute(
            """
            SELECT market_id, normalization_status, filter_status, primary_reason
            FROM scan_candidates
            WHERE scan_run_id = ?
            ORDER BY market_id
            """,
            (result.scan_run_id,),
        ).fetchall()

    assert tuple(run_row) == (3, 1, 1, 1)
    assert [tuple(row) for row in candidate_rows] == [
        ("wx-heat-miami-005", "review", "review", "ambiguous_threshold"),
        ("wx-rain-nyc-004", "approved", "rejected", "price_above_ceiling"),
        ("wx-temp-phx-001", "approved", "approved", None),
    ]


def test_market_scan_persists_bucket_tables_for_latest_scan(
    weather_markets: list[dict],
    temp_sqlite_db_path: Path,
) -> None:
    settings = ScanSettings(
        database_path=str(temp_sqlite_db_path),
        max_resolution_hours=200,
    )
    scanner = MarketScanner(settings=settings)
    storage = CandidateStorage.from_settings(settings)

    scanner.run_scan(_payload_for_task_two(weather_markets), storage=storage)

    approved = storage.list_candidates(status=result_status("approved"))
    review = storage.list_candidates(status=result_status("review"))
    rejected = storage.list_candidates(status=result_status("rejected"))

    assert [candidate.market_id for candidate in approved] == ["wx-temp-phx-001"]
    assert [candidate.market_id for candidate in review] == ["wx-heat-miami-005"]
    assert [candidate.market_id for candidate in rejected] == ["wx-rain-nyc-004"]
    assert rejected[0].rejection_reasons == ("price_above_ceiling",)


def result_status(value: str):
    from core.models import CandidateStatus

    return CandidateStatus(value)
