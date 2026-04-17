"""Weather scanner built on conservative normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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


def scan_weather_markets(markets: Iterable[RawMarketRecord]) -> WeatherScannerResult:
    approved: list[CandidateRecord] = []
    review: list[CandidateRecord] = []
    rejected: list[CandidateRecord] = []

    for market in markets:
        normalized = normalize_weather_market(market).to_candidate_record()
        if normalized.status is CandidateStatus.APPROVED:
            approved.append(normalized)
        elif normalized.status is CandidateStatus.REVIEW:
            review.append(normalized)
        else:
            rejected.append(normalized)

    return WeatherScannerResult(
        approved=tuple(approved),
        review=tuple(review),
        rejected=tuple(rejected),
    )
