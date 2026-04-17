"""Shared market-discovery orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from config.settings import ScanSettings, get_settings
from core.clob_client import PolymarketDiscoveryClient, RawMarketRecord
from core.models import CandidateRecord
from core.storage import CandidateStorage
from strategies.weather.scanner import scan_weather_markets


@dataclass(frozen=True)
class MarketScanHandoff:
    """Scanner-ready raw market payload groups."""

    source: str
    settings: ScanSettings
    weather_markets: tuple[RawMarketRecord, ...]
    skipped_markets: tuple[RawMarketRecord, ...]


@dataclass(frozen=True)
class MarketScanResult:
    """Normalized scan output used by downstream filter and persistence stages."""

    source: str
    approved: tuple[CandidateRecord, ...]
    review: tuple[CandidateRecord, ...]
    rejected: tuple[CandidateRecord, ...]
    scan_run_id: int | None = None

    @property
    def non_approved(self) -> tuple[CandidateRecord, ...]:
        return self.review + self.rejected

    @property
    def all_candidates(self) -> tuple[CandidateRecord, ...]:
        return self.approved + self.review + self.rejected

    @property
    def counts(self) -> dict[str, int]:
        return {
            "accepted": len(self.approved),
            "review": len(self.review),
            "rejected": len(self.rejected),
        }


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
        weather_scanner: Callable[[Iterable[RawMarketRecord]], object] | None = None,
    ) -> object:
        handoff = self.prepare_weather_scan(payload)
        if weather_scanner is not None:
            return weather_scanner(handoff.weather_markets)

        weather_result = scan_weather_markets(handoff.weather_markets, apply_filters=False)
        return MarketScanResult(
            source=handoff.source,
            approved=weather_result.approved,
            review=weather_result.review,
            rejected=weather_result.rejected,
        )

    def run_scan(
        self,
        payload: dict | list[dict],
        storage: CandidateStorage | None = None,
    ) -> MarketScanResult:
        handoff = self.prepare_weather_scan(payload)
        weather_result = scan_weather_markets(
            handoff.weather_markets,
            settings=self.settings,
            apply_filters=True,
        )
        result = MarketScanResult(
            source=handoff.source,
            approved=weather_result.approved,
            review=weather_result.review,
            rejected=weather_result.rejected,
        )

        if storage is None:
            return result

        scan_run_id = storage.persist_scan_result(result.source, result.all_candidates)
        return MarketScanResult(
            source=result.source,
            approved=result.approved,
            review=result.review,
            rejected=result.rejected,
            scan_run_id=scan_run_id,
        )
