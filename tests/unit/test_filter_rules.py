from __future__ import annotations

from config.settings import ScanSettings
from core.clob_client import PolymarketDiscoveryClient
from core.models import CandidateStatus
from strategies.weather.scanner import scan_weather_markets

CLIENT = PolymarketDiscoveryClient()


def _scan_single_market(market: dict, settings: ScanSettings | None = None):
    raw_market = CLIENT.load_markets([market])[0]
    result = scan_weather_markets([raw_market], settings=settings)
    return result.approved, result.review, result.rejected

def test_filter_rules_accept_candidate_that_meets_all_thresholds(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-temp-phx-001")
    approved, review, rejected = _scan_single_market(market)

    assert [candidate.market_id for candidate in approved] == ["wx-temp-phx-001"]
    assert review == ()
    assert rejected == ()


def test_filter_rules_reject_candidate_with_low_liquidity(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-temp-dal-003")
    approved, review, rejected = _scan_single_market(
        market,
        ScanSettings(max_resolution_hours=200),
    )

    assert approved == ()
    assert review == ()
    assert rejected[0].status is CandidateStatus.REJECTED
    assert rejected[0].rejection_reasons == ("liquidity_below_threshold",)


def test_filter_rules_reject_candidate_when_price_is_above_cap(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-rain-nyc-004")
    approved, review, rejected = _scan_single_market(market)

    assert approved == ()
    assert review == ()
    assert rejected[0].rejection_reasons == ("price_above_ceiling",)


def test_filter_rules_reject_candidate_when_resolution_window_is_too_wide(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-temp-phx-001")
    approved, review, rejected = _scan_single_market(
        market,
        ScanSettings(max_resolution_hours=24),
    )

    assert approved == ()
    assert review == ()
    assert rejected[0].rejection_reasons == ("resolution_window_too_wide",)


def test_filter_rules_keep_non_approved_candidates_out_of_tradable_set(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-heat-miami-005")
    approved, review, rejected = _scan_single_market(market)

    assert approved == ()
    assert [candidate.market_id for candidate in review] == ["wx-heat-miami-005"]
    assert rejected == ()


def test_filter_rule_settings_are_not_hardcoded(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-temp-dal-003")
    approved, review, rejected = _scan_single_market(
        market,
        ScanSettings(min_market_liquidity_usd=1000, max_resolution_hours=200),
    )

    assert [candidate.market_id for candidate in approved] == ["wx-temp-dal-003"]
    assert review == ()
    assert rejected == ()
