"""Weather scanner built on conservative normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from config.settings import ScanSettings
from core.clob_client import RawMarketRecord
from core.models import CandidateRecord, CandidateStatus
from strategies.weather.normalization import normalize_weather_market


@dataclass(frozen=True)
class WeatherScannerResult:
    """Normalized weather candidates grouped by support tier."""

    approved: tuple[CandidateRecord, ...]
    review: tuple[CandidateRecord, ...]
    rejected: tuple[CandidateRecord, ...]

    @property
    def non_approved(self) -> tuple[CandidateRecord, ...]:
        return self.review + self.rejected


def apply_candidate_filters(
    candidate: CandidateRecord,
    settings: ScanSettings,
) -> CandidateRecord:
    """Convert normalized approved candidates into accepted or rejected records."""

    if candidate.status is not CandidateStatus.APPROVED:
        return candidate

    rejection_reasons: list[str] = []

    if candidate.liquidity_usd is not None and candidate.liquidity_usd < settings.min_market_liquidity_usd:
        rejection_reasons.append("liquidity_below_threshold")

    if candidate.no_price is not None and candidate.no_price >= settings.max_entry_price:
        rejection_reasons.append("price_above_ceiling")

    if candidate.resolution_hours is not None and candidate.resolution_hours > settings.max_resolution_hours:
        rejection_reasons.append("resolution_window_too_wide")

    if not rejection_reasons:
        return candidate

    return CandidateRecord(
        market_id=candidate.market_id,
        title=candidate.title,
        status=CandidateStatus.REJECTED,
        location=candidate.location,
        contract_family=candidate.contract_family,
        metric=candidate.metric,
        region=candidate.region,
        threshold=candidate.threshold,
        unit=candidate.unit,
        no_price=candidate.no_price,
        liquidity_usd=candidate.liquidity_usd,
        resolution_hours=candidate.resolution_hours,
        market_date_local=candidate.market_date_local,
        market_window_start_local=candidate.market_window_start_local,
        market_window_end_local=candidate.market_window_end_local,
        location_key=candidate.location_key,
        normalization_status=candidate.normalization_status or candidate.status,
        rejection_reasons=tuple(rejection_reasons),
    )


def scan_weather_markets(
    markets: Iterable[RawMarketRecord],
    settings: ScanSettings | None = None,
    *,
    apply_filters: bool = True,
) -> WeatherScannerResult:
    runtime_settings = settings or ScanSettings()
    approved: list[CandidateRecord] = []
    review: list[CandidateRecord] = []
    rejected: list[CandidateRecord] = []

    for market in markets:
        normalized = normalize_weather_market(market).to_candidate_record()
        filtered = apply_candidate_filters(normalized, runtime_settings) if apply_filters else normalized
        if filtered.status is CandidateStatus.APPROVED:
            approved.append(filtered)
        elif filtered.status is CandidateStatus.REVIEW:
            review.append(filtered)
        else:
            rejected.append(filtered)

    return WeatherScannerResult(
        approved=tuple(approved),
        review=tuple(review),
        rejected=tuple(rejected),
    )
