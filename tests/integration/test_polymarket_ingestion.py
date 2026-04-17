from __future__ import annotations

import pytest

from core.clob_client import PolymarketDiscoveryClient, PolymarketPayloadError
from core.market_scanner import MarketScanner


def test_discovery_client_normalizes_fixture_payload(weather_market_payloads: dict) -> None:
    client = PolymarketDiscoveryClient()

    records = client.load_markets(weather_market_payloads)

    assert len(records) == 6
    assert records[0].market_id == "wx-temp-phx-001"
    assert records[0].title == "Will Phoenix hit 110F or higher on April 18?"
    assert records[0].is_weather_market is True


def test_discovery_client_rejects_malformed_payloads() -> None:
    client = PolymarketDiscoveryClient()

    with pytest.raises(PolymarketPayloadError, match="missing required fields: end_iso"):
        client.load_markets(
            {
                "markets": [
                    {
                        "id": "broken-001",
                        "slug": "broken-001",
                        "title": "Will Phoenix hit 110F or higher on April 18?",
                        "description": "broken payload missing end_iso",
                        "liquidity_usd": 8500,
                        "volume_usd": 24000,
                        "no_price": 0.42,
                    }
                ]
            }
        )


def test_market_scanner_hands_off_only_weather_records(weather_market_payloads: dict) -> None:
    scanner = MarketScanner()

    handoff = scanner.prepare_weather_scan(weather_market_payloads)

    assert handoff.source == "polymarket"
    assert len(handoff.weather_markets) == 6
    assert handoff.skipped_markets == ()


def test_market_scanner_dispatches_valid_weather_records_to_consumer(
    weather_market_payloads: dict,
) -> None:
    scanner = MarketScanner()
    received_ids: list[str] = []

    def consume(markets) -> list[str]:
        received_ids.extend(market.market_id for market in markets)
        return received_ids

    result = scanner.dispatch_weather_scan(weather_market_payloads, consume)

    assert result == [
        "wx-temp-phx-001",
        "wx-rain-sea-002",
        "wx-temp-dal-003",
        "wx-rain-nyc-004",
        "wx-heat-miami-005",
        "wx-wind-chi-006",
    ]


def test_market_scanner_returns_grouped_normalized_candidates(
    weather_market_payloads: dict,
) -> None:
    scanner = MarketScanner()

    result = scanner.dispatch_weather_scan(weather_market_payloads)

    assert result.source == "polymarket"
    assert [candidate.market_id for candidate in result.approved] == [
        "wx-temp-phx-001",
        "wx-rain-sea-002",
        "wx-temp-dal-003",
        "wx-rain-nyc-004",
    ]
    assert [candidate.market_id for candidate in result.review] == ["wx-heat-miami-005"]
    assert [candidate.market_id for candidate in result.rejected] == ["wx-wind-chi-006"]
    assert {candidate.market_id for candidate in result.non_approved} == {
        "wx-heat-miami-005",
        "wx-wind-chi-006",
    }
