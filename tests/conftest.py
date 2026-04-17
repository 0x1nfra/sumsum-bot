from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def weather_market_fixture_path() -> Path:
    return Path(__file__).parent / "fixtures" / "polymarket_weather_markets.json"


@pytest.fixture(scope="session")
def weather_market_payloads(weather_market_fixture_path: Path) -> dict:
    return json.loads(weather_market_fixture_path.read_text())


@pytest.fixture(scope="session")
def weather_markets(weather_market_payloads: dict) -> list[dict]:
    return weather_market_payloads["markets"]


@pytest.fixture(scope="session")
def weather_markets_by_bucket(weather_markets: list[dict]) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = {"approved": [], "review": [], "rejected": []}
    for market in weather_markets:
        buckets[market["expected_bucket"]].append(market)
    return buckets


@pytest.fixture()
def temp_sqlite_db_path(tmp_path: Path) -> Path:
    return tmp_path / "scan-results.sqlite3"
