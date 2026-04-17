"""Shared market-discovery orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from config.settings import ScanSettings, get_settings
from core.clob_client import PolymarketDiscoveryClient, RawMarketRecord


@dataclass(frozen=True)
class MarketScanHandoff:
    """Scanner-ready raw market payload groups."""

    source: str
    settings: ScanSettings
    weather_markets: tuple[RawMarketRecord, ...]
    skipped_markets: tuple[RawMarketRecord, ...]


class MarketScanner:
    """Load discovery payloads and expose weather-relevant raw markets."""

    def __init__(
        self,
        client: PolymarketDiscoveryClient | None = None,
        settings: ScanSettings | None = None,
    ) -> None:
        self.client = client or PolymarketDiscoveryClient()
        self.settings = settings or get_settings()

    def prepare_weather_scan(
        self,
        payload: dict | list[dict],
    ) -> MarketScanHandoff:
        markets = self.client.load_markets(payload)
        weather_markets = tuple(market for market in markets if market.is_weather_market)
        skipped_markets = tuple(market for market in markets if not market.is_weather_market)
        return MarketScanHandoff(
            source="polymarket",
            settings=self.settings,
            weather_markets=weather_markets,
            skipped_markets=skipped_markets,
        )

    def dispatch_weather_scan(
        self,
        payload: dict | list[dict],
        weather_scanner: Callable[[Iterable[RawMarketRecord]], object],
    ) -> object:
        handoff = self.prepare_weather_scan(payload)
        return weather_scanner(handoff.weather_markets)
