from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FilterSettings:
    min_market_liquidity_usd: int = 5000
    max_no_price: float = 0.85
    max_resolution_hours: int = 72


def evaluate_candidate(market: dict, settings: FilterSettings | None = None) -> dict:
    thresholds = settings or FilterSettings()
    reasons: list[str] = []

    if market["expected_bucket"] != "approved":
        reasons.append(f"normalization_{market['expected_bucket']}")

    if market["liquidity_usd"] < thresholds.min_market_liquidity_usd:
        reasons.append("insufficient_liquidity")

    if market["no_price"] >= thresholds.max_no_price:
        reasons.append("no_price_too_high")

    if market["expected_resolution_hours"] > thresholds.max_resolution_hours:
        reasons.append("resolution_window_too_long")

    return {"accepted": not reasons, "reasons": reasons}


def test_filter_rules_accept_candidate_that_meets_all_thresholds(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-temp-phx-001")
    result = evaluate_candidate(market)

    assert result["accepted"] is True
    assert result["reasons"] == []


def test_filter_rules_reject_candidate_with_low_liquidity(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-temp-dal-003")
    result = evaluate_candidate(market)

    assert result["accepted"] is False
    assert "insufficient_liquidity" in result["reasons"]


def test_filter_rules_reject_candidate_when_no_price_is_above_cap(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-rain-nyc-004")
    result = evaluate_candidate(market)

    assert result["accepted"] is False
    assert "no_price_too_high" in result["reasons"]


def test_filter_rules_keep_non_approved_candidates_out_of_tradable_set(weather_markets: list[dict]) -> None:
    market = next(market for market in weather_markets if market["id"] == "wx-heat-miami-005")
    result = evaluate_candidate(market)

    assert result["accepted"] is False
    assert "normalization_review" in result["reasons"]
