from __future__ import annotations

import re
import sqlite3
from pathlib import Path


TEMPERATURE_TITLE = re.compile(
    r"^Will (?P<location>.+) hit (?P<threshold>\d+)F or higher on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)
PRECIPITATION_TITLE = re.compile(
    r"^Will (?P<location>.+) record measurable rain on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)


def bootstrap_scan_storage(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE approved_candidates (
            market_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            location TEXT NOT NULL
        );

        CREATE TABLE rejected_candidates (
            market_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            reason TEXT NOT NULL
        );
        """
    )
    return connection


def normalize_market(market: dict) -> dict:
    title = market["title"]

    if match := TEMPERATURE_TITLE.match(title):
        return {
            "bucket": "approved",
            "market_id": market["id"],
            "title": title,
            "location": match.group("location"),
            "reason": None,
        }

    if match := PRECIPITATION_TITLE.match(title):
        return {
            "bucket": "approved",
            "market_id": market["id"],
            "title": title,
            "location": match.group("location"),
            "reason": None,
        }

    if "heat-index danger levels" in title:
        return {
            "bucket": "review",
            "market_id": market["id"],
            "title": title,
            "location": "Miami",
            "reason": "ambiguous_threshold",
        }

    return {
        "bucket": "rejected",
        "market_id": market["id"],
        "title": title,
        "location": market["expected_location"],
        "reason": "unsupported_weather_type",
    }


def filter_market(market: dict, normalized: dict) -> list[str]:
    reasons: list[str] = []

    if normalized["bucket"] != "approved":
        reasons.append(f"normalization_{normalized['bucket']}")

    if market["liquidity_usd"] < 5000:
        reasons.append("insufficient_liquidity")

    if market["no_price"] >= 0.85:
        reasons.append("no_price_too_high")

    if market["expected_resolution_hours"] > 72:
        reasons.append("resolution_window_too_long")

    return reasons


def run_scan(markets: list[dict], database_path: Path) -> dict:
    connection = bootstrap_scan_storage(database_path)
    accepted_ids: list[str] = []
    rejected: list[tuple[str, str]] = []

    for market in markets:
        normalized = normalize_market(market)
        reasons = filter_market(market, normalized)

        if reasons:
            reason_text = ",".join(reasons)
            connection.execute(
                "INSERT INTO rejected_candidates (market_id, title, reason) VALUES (?, ?, ?)",
                (market["id"], market["title"], reason_text),
            )
            rejected.append((market["id"], reason_text))
            continue

        connection.execute(
            "INSERT INTO approved_candidates (market_id, title, location) VALUES (?, ?, ?)",
            (market["id"], market["title"], normalized["location"]),
        )
        accepted_ids.append(market["id"])

    connection.commit()

    approved_count = connection.execute("SELECT COUNT(*) FROM approved_candidates").fetchone()[0]
    rejected_count = connection.execute("SELECT COUNT(*) FROM rejected_candidates").fetchone()[0]

    return {
        "accepted_ids": accepted_ids,
        "rejected": rejected,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
    }


def test_scan_pipeline_persists_only_candidates_that_pass_all_filters(
    weather_markets: list[dict], temp_sqlite_db_path: Path
) -> None:
    result = run_scan(weather_markets, temp_sqlite_db_path)

    assert result["accepted_ids"] == ["wx-temp-phx-001", "wx-rain-sea-002"]
    assert result["approved_count"] == 2
    assert result["rejected_count"] == 4


def test_scan_pipeline_records_explicit_rejection_reasons(
    weather_markets: list[dict], temp_sqlite_db_path: Path
) -> None:
    result = run_scan(weather_markets, temp_sqlite_db_path)
    rejection_map = dict(result["rejected"])

    assert rejection_map["wx-temp-dal-003"] == "insufficient_liquidity"
    assert rejection_map["wx-rain-nyc-004"] == "no_price_too_high"
    assert rejection_map["wx-heat-miami-005"] == "normalization_review"
    assert rejection_map["wx-wind-chi-006"] == "normalization_rejected"
