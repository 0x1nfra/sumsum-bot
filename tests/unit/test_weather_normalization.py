from __future__ import annotations

from datetime import UTC, datetime

import pytest

from core.clob_client import PolymarketDiscoveryClient
from core.models import CandidateStatus
from strategies.weather.normalization import normalize_weather_market
from strategies.weather.types import WeatherMarketCandidate


def test_supported_titles_normalize_into_approved_weather_candidates(
    weather_market_payloads: dict,
) -> None:
    records = PolymarketDiscoveryClient().load_markets(weather_market_payloads)

    for market in records[:4]:
        normalized = normalize_weather_market(market)

        assert normalized.status is CandidateStatus.APPROVED
        assert normalized.contract_family in {"temperature", "precipitation"}
        assert normalized.location
        assert normalized.threshold is not None
        assert normalized.unit in {"F", "in"}
        assert normalized.reason_codes == ()
        assert normalized.resolution_at is not None


def test_ambiguous_titles_are_routed_to_review_bucket(
    weather_market_payloads: dict,
) -> None:
    market = PolymarketDiscoveryClient().load_markets(weather_market_payloads)[4]
    normalized = normalize_weather_market(market)

    assert normalized.status is CandidateStatus.REVIEW
    assert normalized.reason_codes == ("ambiguous_threshold",)
    assert normalized.location == "Miami"
    assert normalized.contract_family is None


def test_unsupported_weather_titles_are_rejected(
    weather_market_payloads: dict,
) -> None:
    market = PolymarketDiscoveryClient().load_markets(weather_market_payloads)[5]
    normalized = normalize_weather_market(market)

    assert normalized.status is CandidateStatus.REJECTED
    assert normalized.reason_codes == ("unsupported_weather_type",)
    assert normalized.location == "Chicago"


def test_market_date_uses_next_year_for_january_titles_near_year_end() -> None:
    candidate = WeatherMarketCandidate(
        market_id="wx-temp-phx-ny-001",
        title="Will Phoenix hit 70F or higher on January 1?",
        status=CandidateStatus.APPROVED,
        contract_family="temperature",
        location="Phoenix",
        threshold=70.0,
        unit="F",
        resolution_at=datetime(2026, 12, 31, 18, 0, tzinfo=UTC),
        no_price=0.42,
        liquidity_usd=8000.0,
    )

    assert candidate.to_candidate_record().market_date_local == "2027-01-01"


def test_market_date_uses_prior_year_for_december_titles_near_year_start() -> None:
    candidate = WeatherMarketCandidate(
        market_id="wx-temp-phx-ny-002",
        title="Will Phoenix hit 70F or higher on December 31?",
        status=CandidateStatus.APPROVED,
        contract_family="temperature",
        location="Phoenix",
        threshold=70.0,
        unit="F",
        resolution_at=datetime(2026, 1, 1, 6, 0, tzinfo=UTC),
        no_price=0.42,
        liquidity_usd=8000.0,
    )

    assert candidate.to_candidate_record().market_date_local == "2025-12-31"


def test_resolution_hours_uses_current_time_not_utc_midnight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            current = cls(2026, 4, 18, 18, 30, tzinfo=UTC)
            return current if tz is None else current.astimezone(tz)

    monkeypatch.setattr("strategies.weather.types.datetime", FrozenDateTime)
    candidate = WeatherMarketCandidate(
        market_id="wx-temp-phx-ny-003",
        title="Will Phoenix hit 70F or higher on April 18?",
        status=CandidateStatus.APPROVED,
        contract_family="temperature",
        location="Phoenix",
        threshold=70.0,
        unit="F",
        resolution_at=datetime(2026, 4, 19, 7, 0, tzinfo=UTC),
        no_price=0.42,
        liquidity_usd=8000.0,
    )

    assert candidate.resolution_hours == 12
