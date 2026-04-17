"""Tiered normalization for weather-market contracts."""

from __future__ import annotations

from datetime import datetime
import re

from core.clob_client import RawMarketRecord
from core.models import CandidateStatus, RejectionReason
from strategies.weather.types import WeatherMarketCandidate

TEMPERATURE_TITLE = re.compile(
    r"^Will (?P<location>.+) hit (?P<threshold>\d+)F or higher on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)
PRECIPITATION_TITLE = re.compile(
    r"^Will (?P<location>.+) record measurable rain on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)


def normalize_weather_market(market: RawMarketRecord) -> WeatherMarketCandidate:
    title = market.title
    resolution_at = _parse_resolution_time(market.end_iso)

    if match := TEMPERATURE_TITLE.match(title):
        return WeatherMarketCandidate(
            market_id=market.market_id,
            title=market.title,
            status=CandidateStatus.APPROVED,
            contract_family="temperature",
            location=match.group("location"),
            threshold=float(match.group("threshold")),
            unit="F",
            resolution_at=resolution_at,
            no_price=market.no_price,
            liquidity_usd=market.liquidity_usd,
        )

    if match := PRECIPITATION_TITLE.match(title):
        return WeatherMarketCandidate(
            market_id=market.market_id,
            title=market.title,
            status=CandidateStatus.APPROVED,
            contract_family="precipitation",
            location=match.group("location"),
            threshold=0.0,
            unit="in",
            resolution_at=resolution_at,
            no_price=market.no_price,
            liquidity_usd=market.liquidity_usd,
        )

    if _looks_weather_related(title):
        location = _extract_review_location(title)
        return WeatherMarketCandidate(
            market_id=market.market_id,
            title=market.title,
            status=CandidateStatus.REVIEW,
            contract_family=None,
            location=location,
            threshold=None,
            unit=None,
            resolution_at=resolution_at,
            no_price=market.no_price,
            liquidity_usd=market.liquidity_usd,
            reason_codes=(RejectionReason.AMBIGUOUS_THRESHOLD.value,),
        )

    return WeatherMarketCandidate(
        market_id=market.market_id,
        title=market.title,
        status=CandidateStatus.REJECTED,
        contract_family=None,
        location=_extract_fallback_location(title),
        threshold=None,
        unit=None,
        resolution_at=resolution_at,
        no_price=market.no_price,
        liquidity_usd=market.liquidity_usd,
        reason_codes=(RejectionReason.UNSUPPORTED_WEATHER_TYPE.value,),
    )


def _parse_resolution_time(value: str) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _looks_weather_related(title: str) -> bool:
    title_lower = title.lower()
    if "heat-index" in title_lower or "heat index" in title_lower:
        return True
    return False


def _extract_review_location(title: str) -> str:
    match = re.match(r"^Will (?P<location>.+?) see ", title)
    if match:
        return match.group("location")
    return _extract_fallback_location(title)


def _extract_fallback_location(title: str) -> str:
    windy_match = re.search(r"in (?P<location>.+?) (?:tomorrow|\?|on )", title)
    if windy_match:
        return windy_match.group("location")
    initial_match = re.match(r"^Will (?P<location>.+?) ", title)
    if initial_match:
        return initial_match.group("location")
    return "unknown"
