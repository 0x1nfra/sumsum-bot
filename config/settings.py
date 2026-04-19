"""Typed runtime settings for market discovery and persistence."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


@dataclass(frozen=True)
class ScanSettings:
    """Scanner and storage thresholds used during market discovery."""

    database_path: str = "data/trades.db"
    min_market_liquidity_usd: int = 5000
    max_entry_price: float = 0.85
    max_resolution_hours: int = 72
    scan_interval_seconds: int = 300
    noaa_user_agent: str = "(sumsum-bot, contact@example.com)"
    noaa_request_timeout_seconds: float = 10.0
    noaa_max_data_age_minutes: int = 180
    minimum_edge_to_trade: float = 0.10
    kelly_fraction: float = 0.25
    probability_haircut_pct: float = 0.05
    per_trade_exposure_cap_pct: float = 0.05
    global_max_open_exposure_pct: float = 0.30
    window_max_open_exposure_pct: float = 0.15
    minimum_trade_stake_usd: float = 1.00
    paper_starting_bankroll_usd: float = 100.0
    paper_poll_interval_seconds: int = 300
    paper_resolution_poll_seconds: int = 300

    @property
    def max_no_price(self) -> float:
        """Backward-compatible alias for older tests and callers."""

        return self.max_entry_price


def load_settings(
    overrides: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> ScanSettings:
    """Build settings from code defaults plus environment-style overrides."""

    raw_env = dict(os.environ if environ is None else environ)
    if overrides:
        raw_env.update(overrides)

    return ScanSettings(
        database_path=raw_env.get("DATABASE_PATH", ScanSettings.database_path),
        min_market_liquidity_usd=int(
            raw_env.get(
                "MIN_MARKET_LIQUIDITY_USD",
                str(ScanSettings.min_market_liquidity_usd),
            )
        ),
        max_entry_price=float(
            raw_env.get(
                "MAX_ENTRY_PRICE",
                raw_env.get("MAX_NO_PRICE", str(ScanSettings.max_entry_price)),
            )
        ),
        max_resolution_hours=int(
            raw_env.get(
                "MAX_RESOLUTION_HOURS",
                str(ScanSettings.max_resolution_hours),
            )
        ),
        scan_interval_seconds=int(
            raw_env.get(
                "SCAN_INTERVAL_SECONDS",
                str(ScanSettings.scan_interval_seconds),
            )
        ),
        noaa_user_agent=raw_env.get("NOAA_USER_AGENT", ScanSettings.noaa_user_agent),
        noaa_request_timeout_seconds=float(
            raw_env.get(
                "NOAA_REQUEST_TIMEOUT_SECONDS",
                str(ScanSettings.noaa_request_timeout_seconds),
            )
        ),
        noaa_max_data_age_minutes=int(
            raw_env.get(
                "NOAA_MAX_DATA_AGE_MINUTES",
                str(ScanSettings.noaa_max_data_age_minutes),
            )
        ),
        minimum_edge_to_trade=float(
            raw_env.get(
                "MINIMUM_EDGE_TO_TRADE",
                str(ScanSettings.minimum_edge_to_trade),
            )
        ),
        kelly_fraction=float(
            raw_env.get(
                "KELLY_FRACTION",
                str(ScanSettings.kelly_fraction),
            )
        ),
        probability_haircut_pct=float(
            raw_env.get(
                "PROBABILITY_HAIRCUT_PCT",
                str(ScanSettings.probability_haircut_pct),
            )
        ),
        per_trade_exposure_cap_pct=float(
            raw_env.get(
                "PER_TRADE_EXPOSURE_CAP_PCT",
                str(ScanSettings.per_trade_exposure_cap_pct),
            )
        ),
        global_max_open_exposure_pct=float(
            raw_env.get(
                "GLOBAL_MAX_OPEN_EXPOSURE_PCT",
                str(ScanSettings.global_max_open_exposure_pct),
            )
        ),
        window_max_open_exposure_pct=float(
            raw_env.get(
                "WINDOW_MAX_OPEN_EXPOSURE_PCT",
                str(ScanSettings.window_max_open_exposure_pct),
            )
        ),
        minimum_trade_stake_usd=float(
            raw_env.get(
                "MINIMUM_TRADE_STAKE_USD",
                str(ScanSettings.minimum_trade_stake_usd),
            )
        ),
        paper_starting_bankroll_usd=float(
            raw_env.get(
                "PAPER_STARTING_BANKROLL_USD",
                str(ScanSettings.paper_starting_bankroll_usd),
            )
        ),
        paper_poll_interval_seconds=int(
            raw_env.get(
                "PAPER_POLL_INTERVAL_SECONDS",
                str(ScanSettings.paper_poll_interval_seconds),
            )
        ),
        paper_resolution_poll_seconds=int(
            raw_env.get(
                "PAPER_RESOLUTION_POLL_SECONDS",
                str(ScanSettings.paper_resolution_poll_seconds),
            )
        ),
    )


def get_settings() -> ScanSettings:
    """Load settings from the process environment."""

    return load_settings()
