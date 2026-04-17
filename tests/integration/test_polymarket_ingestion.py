from __future__ import annotations

import re


TEMPERATURE_TITLE = re.compile(
    r"^Will (?P<location>.+) hit (?P<threshold>\d+)F or higher on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)
PRECIPITATION_TITLE = re.compile(
    r"^Will (?P<location>.+) record measurable rain on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)


def normalize_market(market: dict) -> dict:
    title = market["title"]

    if match := TEMPERATURE_TITLE.match(title):
        return {
            "market_id": market["id"],
            "bucket": "approved",
            "metric": "temperature",
            "location": match.group("location"),
            "threshold": int(match.group("threshold")),
            "reason": None,
        }

    if match := PRECIPITATION_TITLE.match(title):
        return {
            "market_id": market["id"],
            "bucket": "approved",
            "metric": "precipitation",
            "location": match.group("location"),
            "threshold": 0,
            "reason": None,
        }

    if "heat-index danger levels" in title:
        return {
            "market_id": market["id"],
            "bucket": "review",
            "metric": None,
            "location": "Miami",
            "threshold": None,
            "reason": "ambiguous_threshold",
        }

    return {
        "market_id": market["id"],
        "bucket": "rejected",
        "metric": None,
        "location": market["expected_location"],
        "threshold": None,
        "reason": "unsupported_weather_type",
    }


def ingest_markets(markets: list[dict]) -> dict[str, list[dict]]:
    results = {"approved": [], "review": [], "rejected": []}
    for market in markets:
        normalized = normalize_market(market)
        results[normalized["bucket"]].append(normalized)
    return results


def test_ingestion_splits_weather_fixture_into_expected_buckets(weather_markets: list[dict]) -> None:
    results = ingest_markets(weather_markets)

    assert len(results["approved"]) == 4
    assert len(results["review"]) == 1
    assert len(results["rejected"]) == 1


def test_ingestion_preserves_required_fields_for_supported_weather_markets(
    weather_markets: list[dict],
) -> None:
    results = ingest_markets(weather_markets)

    for candidate in results["approved"]:
        assert candidate["metric"] in {"temperature", "precipitation"}
        assert candidate["location"]
        assert candidate["threshold"] is not None
        assert candidate["reason"] is None


def test_ingestion_captures_review_and_rejection_reasons(weather_markets: list[dict]) -> None:
    results = ingest_markets(weather_markets)

    assert results["review"][0]["reason"] == "ambiguous_threshold"
    assert results["rejected"][0]["reason"] == "unsupported_weather_type"
