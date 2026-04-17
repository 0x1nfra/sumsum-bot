from __future__ import annotations

from core.clob_client import PolymarketDiscoveryClient
from core.models import CandidateStatus
from strategies.weather.normalization import normalize_weather_market


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
