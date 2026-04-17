from __future__ import annotations

import sqlite3
from pathlib import Path


def bootstrap_storage(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS approved_candidates (
            market_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            metric TEXT NOT NULL,
            location TEXT NOT NULL,
            no_price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS rejected_candidates (
            market_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            bucket TEXT NOT NULL,
            reason TEXT NOT NULL
        );
        """
    )
    return connection


def save_approved_candidate(connection: sqlite3.Connection, market: dict) -> None:
    connection.execute(
        """
        INSERT INTO approved_candidates (market_id, title, metric, location, no_price)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            market["id"],
            market["title"],
            market["expected_metric"],
            market["expected_location"],
            market["no_price"],
        ),
    )
    connection.commit()


def save_rejected_candidate(connection: sqlite3.Connection, market: dict) -> None:
    connection.execute(
        """
        INSERT INTO rejected_candidates (market_id, title, bucket, reason)
        VALUES (?, ?, ?, ?)
        """,
        (
            market["id"],
            market["title"],
            market["expected_bucket"],
            market["expected_rejection_reason"] or market["expected_bucket"],
        ),
    )
    connection.commit()


def test_storage_bootstrap_creates_phase_one_candidate_tables(temp_sqlite_db_path: Path) -> None:
    connection = bootstrap_storage(temp_sqlite_db_path)

    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    }

    assert "approved_candidates" in tables
    assert "rejected_candidates" in tables


def test_storage_persists_approved_candidate_rows(
    temp_sqlite_db_path: Path, weather_markets_by_bucket: dict[str, list[dict]]
) -> None:
    connection = bootstrap_storage(temp_sqlite_db_path)
    market = weather_markets_by_bucket["approved"][0]
    save_approved_candidate(connection, market)

    row = connection.execute(
        "SELECT market_id, metric, location, no_price FROM approved_candidates"
    ).fetchone()

    assert row == (
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

    rows = connection.execute(
        "SELECT market_id, bucket, reason FROM rejected_candidates ORDER BY market_id"
    ).fetchall()

    assert rows == [
        (
            review_market["id"],
            review_market["expected_bucket"],
            review_market["expected_rejection_reason"],
        ),
        (
            rejected_market["id"],
            rejected_market["expected_bucket"],
            rejected_market["expected_rejection_reason"],
        ),
    ]
