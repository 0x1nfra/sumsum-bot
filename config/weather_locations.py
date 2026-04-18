"""Curated NOAA location mappings for supported weather markets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherLocationMapping:
    city_key: str
    market_label: str
    latitude: float
    longitude: float
    timezone: str


SUPPORTED_WEATHER_LOCATIONS: dict[str, WeatherLocationMapping] = {
    "phoenix": WeatherLocationMapping(
        city_key="phoenix",
        market_label="Phoenix",
        latitude=33.4484,
        longitude=-112.0740,
        timezone="America/Phoenix",
    ),
    "seattle": WeatherLocationMapping(
        city_key="seattle",
        market_label="Seattle",
        latitude=47.6062,
        longitude=-122.3321,
        timezone="America/Los_Angeles",
    ),
    "dallas": WeatherLocationMapping(
        city_key="dallas",
        market_label="Dallas",
        latitude=32.7767,
        longitude=-96.7970,
        timezone="America/Chicago",
    ),
    "new-york-city": WeatherLocationMapping(
        city_key="new-york-city",
        market_label="New York City",
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
    ),
}


def normalize_city_key(value: str) -> str:
    return "-".join(value.strip().lower().replace(".", "").split())


def get_weather_location(city_key: str) -> WeatherLocationMapping | None:
    return SUPPORTED_WEATHER_LOCATIONS.get(normalize_city_key(city_key))
