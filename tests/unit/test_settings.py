from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class ScanSettings:
    database_path: str = "data/trades.db"
    min_market_liquidity_usd: int = 5000
    max_no_price: float = 0.85
    max_resolution_hours: int = 72
    scan_interval_seconds: int = 300


def load_settings(overrides: dict[str, str] | None = None) -> ScanSettings:
    raw = overrides or {}
    return ScanSettings(
        database_path=raw.get("DATABASE_PATH", "data/trades.db"),
        min_market_liquidity_usd=int(raw.get("MIN_MARKET_LIQUIDITY_USD", "5000")),
        max_no_price=float(raw.get("MAX_NO_PRICE", "0.85")),
        max_resolution_hours=int(raw.get("MAX_RESOLUTION_HOURS", "72")),
        scan_interval_seconds=int(raw.get("SCAN_INTERVAL_SECONDS", "300")),
    )


def test_settings_defaults_match_phase_one_thresholds() -> None:
    settings = load_settings()

    assert settings.database_path == "data/trades.db"
    assert settings.min_market_liquidity_usd == 5000
    assert settings.max_no_price == pytest.approx(0.85)
    assert settings.max_resolution_hours == 72
    assert settings.scan_interval_seconds == 300


def test_settings_allow_environment_style_overrides() -> None:
    settings = load_settings(
        {
            "DATABASE_PATH": "/tmp/markets.sqlite3",
            "MIN_MARKET_LIQUIDITY_USD": "7500",
            "MAX_NO_PRICE": "0.78",
            "MAX_RESOLUTION_HOURS": "48",
            "SCAN_INTERVAL_SECONDS": "120",
        }
    )

    assert settings.database_path == "/tmp/markets.sqlite3"
    assert settings.min_market_liquidity_usd == 7500
    assert settings.max_no_price == pytest.approx(0.78)
    assert settings.max_resolution_hours == 48
    assert settings.scan_interval_seconds == 120


def test_settings_raise_for_invalid_numeric_overrides() -> None:
    with pytest.raises(ValueError):
        load_settings({"MIN_MARKET_LIQUIDITY_USD": "five-thousand"})
