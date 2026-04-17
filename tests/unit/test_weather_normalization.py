from __future__ import annotations

import re


TEMPERATURE_TITLE = re.compile(
    r"^Will (?P<location>.+) hit (?P<threshold>\d+)F or higher on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)
PRECIPITATION_TITLE = re.compile(
    r"^Will (?P<location>.+) record measurable rain on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?$"
)


def normalize_weather_market(market: dict) -> dict:
    title = market["title"]

    if match := TEMPERATURE_TITLE.match(title):
        return {
            "bucket": "approved",
            "metric": "temperature",
            "location": match.group("location"),
            "threshold": int(match.group("threshold")),
            "unit": "F",
            "resolution_hours": market["expected_resolution_hours"],
            "reason": None,
        }

    if match := PRECIPITATION_TITLE.match(title):
        return {
            "bucket": "approved",
            "metric": "precipitation",
            "location": match.group("location"),
            "threshold": 0,
            "unit": "in",
            "resolution_hours": market["expected_resolution_hours"],
            "reason": None,
        }

    if "heat-index danger levels" in title:
        return {
            "bucket": "review",
            "metric": None,
            "location": "Miami",
            "threshold": None,
            "unit": None,
            "resolution_hours": market["expected_resolution_hours"],
            "reason": "ambiguous_threshold",
        }

    return {
        "bucket": "rejected",
        "metric": None,
        "location": market["expected_location"],
        "threshold": None,
        "unit": None,
        "resolution_hours": market["expected_resolution_hours"],
        "reason": "unsupported_weather_type",
    }


def test_supported_titles_normalize_into_approved_weather_candidates(
    weather_markets_by_bucket: dict[str, list[dict]],
) -> None:
    for market in weather_markets_by_bucket["approved"]:
        normalized = normalize_weather_market(market)

        assert normalized["bucket"] == "approved"
        assert normalized["metric"] == market["expected_metric"]
        assert normalized["location"] == market["expected_location"]
        assert normalized["threshold"] == market["expected_threshold"]
        assert normalized["unit"] == market["expected_unit"]
        assert normalized["resolution_hours"] == market["expected_resolution_hours"]


def test_ambiguous_titles_are_routed_to_review_bucket(
    weather_markets_by_bucket: dict[str, list[dict]],
) -> None:
    market = weather_markets_by_bucket["review"][0]
    normalized = normalize_weather_market(market)

    assert normalized["bucket"] == "review"
    assert normalized["reason"] == "ambiguous_threshold"
    assert normalized["location"] == "Miami"


def test_unsupported_weather_titles_are_rejected(
    weather_markets_by_bucket: dict[str, list[dict]],
) -> None:
    market = weather_markets_by_bucket["rejected"][0]
    normalized = normalize_weather_market(market)

    assert normalized["bucket"] == "rejected"
    assert normalized["reason"] == "unsupported_weather_type"
    assert normalized["location"] == "Chicago"
