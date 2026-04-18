"""NOAA forecast client using the NWS points-to-grid workflow."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
import re
import urllib.error
import urllib.request
from typing import Any, Mapping, Sequence

from config.settings import ScanSettings, get_settings
from config.weather_locations import get_weather_location
from strategies.weather.types import NoaaForecastPoint, NoaaForecastWindow, WeatherSignalInput

VALID_TIME_PATTERN = re.compile(
    r"^(?P<start>[^/]+)/P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?)?$"
)


class NoaaDataError(ValueError):
    """Raised when NOAA data is unsupported, stale, or malformed."""


class NoaaForecastClient:
    """Fetch NOAA forecast data for explicit supported-city weather markets."""

    def __init__(self, settings: ScanSettings | None = None) -> None:
        self.settings = settings or get_settings()

    def lookup_points(self, city_key: str) -> NoaaForecastPoint:
        location = get_weather_location(city_key)
        if location is None:
            raise NoaaDataError("noaa_city_unsupported")

        points_url = f"https://api.weather.gov/points/{location.latitude:.4f},{location.longitude:.4f}"
        payload = self._get_json(points_url)
        properties = self._require_mapping(payload.get("properties"), "properties")
        forecast_grid_url = self._require_string(properties.get("forecastGridData"), "forecastGridData")
        forecast_hourly_url = properties.get("forecastHourly")
        if forecast_hourly_url is not None and not isinstance(forecast_hourly_url, str):
            raise NoaaDataError("noaa_payload_incomplete")

        return NoaaForecastPoint(
            city_key=location.city_key,
            market_label=location.market_label,
            latitude=location.latitude,
            longitude=location.longitude,
            timezone=location.timezone,
            forecast_grid_url=forecast_grid_url,
            forecast_hourly_url=forecast_hourly_url,
        )

    def fetch_forecast_window(self, signal_input: WeatherSignalInput) -> NoaaForecastWindow:
        forecast_point = self.lookup_points(signal_input.location_key)
        grid_payload = self._get_json(forecast_point.forecast_grid_url)
        properties = self._require_mapping(grid_payload.get("properties"), "properties")
        market_start = datetime.fromisoformat(signal_input.market_window_start_local)
        market_end = datetime.fromisoformat(signal_input.market_window_end_local)

        update_time = self._parse_datetime(properties.get("updateTime"))
        if self._is_stale(update_time, market_start):
            raise NoaaDataError("noaa_data_stale")

        temperature_values = self._extract_values(properties, "temperature", require_non_empty=True)
        precipitation_probability_values = self._extract_values(properties, "probabilityOfPrecipitation")
        precipitation_amount_values = self._extract_values(properties, "quantitativePrecipitation")

        overlapping_temperatures = self._overlapping_values(temperature_values, market_start, market_end)
        if not overlapping_temperatures:
            raise NoaaDataError("noaa_window_mismatch")

        overlapping_probability = self._overlapping_values(
            precipitation_probability_values,
            market_start,
            market_end,
        )
        overlapping_qpf = self._overlapping_values(
            precipitation_amount_values,
            market_start,
            market_end,
        )

        return NoaaForecastWindow(
            location_key=signal_input.location_key,
            contract_family=signal_input.contract_family,
            market_date_local=signal_input.market_date_local,
            market_window_start_local=signal_input.market_window_start_local,
            market_window_end_local=signal_input.market_window_end_local,
            temperature_overlap_values=tuple(overlapping_temperatures),
            probability_of_precipitation=tuple(overlapping_probability),
            quantitative_precipitation=tuple(overlapping_qpf),
            update_time=update_time,
            forecast_source_url=forecast_point.forecast_grid_url,
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/geo+json, application/json",
                "User-Agent": self.settings.noaa_user_agent,
            },
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.noaa_request_timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise NoaaDataError("noaa_payload_incomplete") from exc

        if not isinstance(payload, dict):
            raise NoaaDataError("noaa_payload_incomplete")
        return payload

    def _extract_values(
        self,
        properties: Mapping[str, Any],
        layer_name: str,
        *,
        require_non_empty: bool = False,
    ) -> Sequence[Mapping[str, Any]]:
        layer = self._require_mapping(properties.get(layer_name), layer_name)
        values = layer.get("values")
        if not isinstance(values, Sequence) or isinstance(values, str | bytes):
            raise NoaaDataError("noaa_payload_incomplete")
        if require_non_empty and not values:
            raise NoaaDataError("noaa_payload_incomplete")
        typed_values: list[Mapping[str, Any]] = []
        for value in values:
            if not isinstance(value, Mapping):
                raise NoaaDataError("noaa_payload_incomplete")
            typed_values.append(value)
        return typed_values

    def _overlapping_values(
        self,
        values: Sequence[Mapping[str, Any]],
        market_start: datetime,
        market_end: datetime,
    ) -> list[float]:
        overlapping: list[float] = []
        for value in values:
            interval_start, interval_end = self._parse_valid_time(
                self._require_string(value.get("validTime"), "validTime")
            )
            if interval_end <= market_start or interval_start >= market_end:
                continue
            numeric_value = value.get("value")
            if numeric_value is None:
                continue
            if not isinstance(numeric_value, int | float):
                raise NoaaDataError("noaa_payload_incomplete")
            overlapping.append(float(numeric_value))
        return overlapping

    def _is_stale(self, update_time: datetime, reference_time: datetime) -> bool:
        max_age = timedelta(minutes=self.settings.noaa_max_data_age_minutes)
        return reference_time.astimezone(UTC) - update_time.astimezone(UTC) > max_age

    def _parse_datetime(self, value: object) -> datetime:
        return datetime.fromisoformat(self._require_string(value, "updateTime"))

    def _parse_valid_time(self, value: str) -> tuple[datetime, datetime]:
        match = VALID_TIME_PATTERN.match(value)
        if match is None:
            raise NoaaDataError("noaa_payload_incomplete")

        start = datetime.fromisoformat(match.group("start"))
        duration = timedelta(
            days=int(match.group("days") or 0),
            hours=int(match.group("hours") or 0),
            minutes=int(match.group("minutes") or 0),
        )
        if duration <= timedelta(0):
            raise NoaaDataError("noaa_payload_incomplete")
        return start, start + duration

    def _require_mapping(self, value: object, _field_name: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise NoaaDataError("noaa_payload_incomplete")
        return value

    def _require_string(self, value: object, _field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise NoaaDataError("noaa_payload_incomplete")
        return value.strip()
