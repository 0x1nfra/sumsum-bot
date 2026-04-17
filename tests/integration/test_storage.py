from __future__ import annotations

from pathlib import Path

from core.storage import bootstrap_storage, save_approved_candidate, save_rejected_candidate


def test_storage_bootstrap_creates_phase_one_candidate_tables(temp_sqlite_db_path: Path) -> None:
    connection = bootstrap_storage(temp_sqlite_db_path)

    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    }

    assert "accepted_candidates" in tables
    assert "review_candidates" in tables
    assert "rejected_candidates" in tables
    assert "scan_runs" in tables


def test_storage_persists_approved_candidate_rows(
    temp_sqlite_db_path: Path, weather_markets_by_bucket: dict[str, list[dict]]
) -> None:
    connection = bootstrap_storage(temp_sqlite_db_path)
    market = weather_markets_by_bucket["approved"][0]
    save_approved_candidate(connection, market)

    row = connection.execute(
        "SELECT market_id, metric, location, no_price FROM accepted_candidates"
    ).fetchone()

    assert tuple(row) == (
        market["id"],
        market["expected_metric"],
        market["expected_location"],
        market["no_price"],
    )


def test_storage_persists_review_and_rejected_rows_with_reason(
    temp_sqlite_db_path: Path, weather_markets_by_bucket: dict[str, list[dict]]
) -> None:
    connection = bootstrap_storage(temp_sqlite_db_path)
    review_market = weather_markets_by_bucket["review"][0]
    rejected_market = weather_markets_by_bucket["rejected"][0]

    save_rejected_candidate(connection, review_market)
    save_rejected_candidate(connection, rejected_market)

    review_rows = connection.execute(
        "SELECT market_id, reason FROM review_candidates ORDER BY market_id"
    ).fetchall()
    rejected_rows = connection.execute(
        "SELECT market_id, reason FROM rejected_candidates ORDER BY market_id"
    ).fetchall()

    assert [tuple(row) for row in review_rows] == [
        (
            review_market["id"],
            review_market["expected_rejection_reason"],
        )
    ]
    assert [tuple(row) for row in rejected_rows] == [
        (
            rejected_market["id"],
            rejected_market["expected_rejection_reason"],
        ),
    ]
