from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Any

import pytest

from config.settings import ScanSettings
from strategies.weather.noaa_client import NoaaDataError, NoaaForecastClient
from strategies.weather.types import NoaaForecastWindow, WeatherSignalInput


class _FakeHttpResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeHttpResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


@pytest.fixture()
def noaa_settings() -> ScanSettings:
    return ScanSettings(
        noaa_user_agent="(sumsum-bot, contact@example.com)",
        noaa_request_timeout_seconds=10.0,
        noaa_max_data_age_minutes=180,
    )


@pytest.fixture()
def signal_input() -> WeatherSignalInput:
    return WeatherSignalInput(
        market_id="wx-temp-phx-001",
        title="Will Phoenix hit 110F or higher on April 18?",
        contract_family="temperature",
        location="Phoenix",
        location_key="phoenix",
        threshold=110.0,
        unit="F",
        no_price=0.42,
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
    )


@pytest.fixture()
def points_payload() -> dict[str, Any]:
    return {
        "properties": {
            "forecastGridData": "https://api.weather.gov/gridpoints/PSR/170,56",
            "forecastHourly": "https://api.weather.gov/gridpoints/PSR/170,56/forecast/hourly",
            "gridId": "PSR",
            "gridX": 170,
            "gridY": 56,
        }
    }


@pytest.fixture()
def grid_payload() -> dict[str, Any]:
    return {
        "properties": {
            "updateTime": "2026-04-18T08:00:00+00:00",
            "temperature": {
                "values": [
                    {"validTime": "2026-04-18T06:00:00+00:00/PT6H", "value": 101},
                    {"validTime": "2026-04-18T12:00:00+00:00/PT12H", "value": 112},
                    {"validTime": "2026-04-19T00:00:00+00:00/PT6H", "value": 108},
                ]
            },
            "probabilityOfPrecipitation": {
                "values": [
                    {"validTime": "2026-04-18T12:00:00+00:00/PT12H", "value": 15},
                ]
            },
            "quantitativePrecipitation": {
                "values": [
                    {"validTime": "2026-04-18T12:00:00+00:00/PT12H", "value": 0.0},
                ]
            },
        }
    }


def _install_urlopen_stub(
    monkeypatch: pytest.MonkeyPatch,
    payloads: dict[str, dict[str, Any]],
) -> None:
    def _fake_urlopen(request: object, timeout: float = 0.0) -> _FakeHttpResponse:
        assert timeout == 10.0
        full_url = getattr(request, "full_url", request)
        if full_url not in payloads:
            raise AssertionError(f"Unexpected NOAA URL: {full_url}")
        return _FakeHttpResponse(payloads[full_url])

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)


def test_points_lookup_uses_curated_city_mapping(
    monkeypatch: pytest.MonkeyPatch,
    noaa_settings: ScanSettings,
    signal_input: WeatherSignalInput,
    points_payload: dict[str, Any],
) -> None:
    client = NoaaForecastClient(noaa_settings)
    _install_urlopen_stub(
        monkeypatch,
        {
            "https://api.weather.gov/points/33.4484,-112.0740": points_payload,
        },
    )

    point = client.lookup_points(signal_input.location_key)

    assert point.city_key == "phoenix"
    assert point.latitude == pytest.approx(33.4484)
    assert point.longitude == pytest.approx(-112.0740)
    assert point.forecast_grid_url == "https://api.weather.gov/gridpoints/PSR/170,56"
    assert point.forecast_hourly_url == "https://api.weather.gov/gridpoints/PSR/170,56/forecast/hourly"
    assert point.timezone == "America/Phoenix"


def test_fetch_forecast_window_preserves_overlap_evidence(
    monkeypatch: pytest.MonkeyPatch,
    noaa_settings: ScanSettings,
    signal_input: WeatherSignalInput,
    points_payload: dict[str, Any],
    grid_payload: dict[str, Any],
) -> None:
    client = NoaaForecastClient(noaa_settings)
    _install_urlopen_stub(
        monkeypatch,
        {
            "https://api.weather.gov/points/33.4484,-112.0740": points_payload,
            "https://api.weather.gov/gridpoints/PSR/170,56": grid_payload,
        },
    )

    forecast_window = client.fetch_forecast_window(signal_input)

    assert isinstance(forecast_window, NoaaForecastWindow)
    assert forecast_window.temperature_overlap_values == (101, 112, 108)
    assert forecast_window.probability_of_precipitation == (15.0,)
    assert forecast_window.quantitative_precipitation == (0.0,)
    assert forecast_window.update_time == datetime(2026, 4, 18, 8, 0, tzinfo=UTC)
    assert forecast_window.forecast_source_url == "https://api.weather.gov/gridpoints/PSR/170,56"


def test_fetch_forecast_window_rejects_stale_grid_data(
    monkeypatch: pytest.MonkeyPatch,
    noaa_settings: ScanSettings,
    signal_input: WeatherSignalInput,
    points_payload: dict[str, Any],
    grid_payload: dict[str, Any],
) -> None:
    client = NoaaForecastClient(noaa_settings)
    stale_grid_payload = {
        **grid_payload,
        "properties": {
            **grid_payload["properties"],
            "updateTime": "2026-04-17T00:00:00+00:00",
        },
    }
    _install_urlopen_stub(
        monkeypatch,
        {
            "https://api.weather.gov/points/33.4484,-112.0740": points_payload,
            "https://api.weather.gov/gridpoints/PSR/170,56": stale_grid_payload,
        },
    )

    with pytest.raises(NoaaDataError, match="noaa_data_stale"):
        client.fetch_forecast_window(signal_input)


def test_fetch_forecast_window_rejects_missing_overlap(
    monkeypatch: pytest.MonkeyPatch,
    noaa_settings: ScanSettings,
    signal_input: WeatherSignalInput,
    points_payload: dict[str, Any],
    grid_payload: dict[str, Any],
) -> None:
    client = NoaaForecastClient(noaa_settings)
    mismatch_payload = {
        **grid_payload,
        "properties": {
            **grid_payload["properties"],
            "temperature": {
                "values": [
                    {"validTime": "2026-04-20T00:00:00+00:00/PT6H", "value": 99},
                ]
            },
            "probabilityOfPrecipitation": {"values": []},
            "quantitativePrecipitation": {"values": []},
        },
    }
    _install_urlopen_stub(
        monkeypatch,
        {
            "https://api.weather.gov/points/33.4484,-112.0740": points_payload,
            "https://api.weather.gov/gridpoints/PSR/170,56": mismatch_payload,
        },
    )

    with pytest.raises(NoaaDataError, match="noaa_window_mismatch"):
        client.fetch_forecast_window(signal_input)


def test_fetch_forecast_window_rejects_unsupported_city(
    noaa_settings: ScanSettings,
    signal_input: WeatherSignalInput,
) -> None:
    client = NoaaForecastClient(noaa_settings)
    unsupported_input = WeatherSignalInput(
        **{**signal_input.__dict__, "location_key": "unknown-city", "location": "Unknown City"}
    )

    with pytest.raises(NoaaDataError, match="noaa_city_unsupported"):
        client.fetch_forecast_window(unsupported_input)


def test_fetch_forecast_window_rejects_incomplete_payload(
    monkeypatch: pytest.MonkeyPatch,
    noaa_settings: ScanSettings,
    signal_input: WeatherSignalInput,
    points_payload: dict[str, Any],
) -> None:
    client = NoaaForecastClient(noaa_settings)
    incomplete_grid_payload = {
        "properties": {
            "updateTime": "2026-04-18T08:00:00+00:00",
            "temperature": {"values": []},
        }
    }
    _install_urlopen_stub(
        monkeypatch,
        {
            "https://api.weather.gov/points/33.4484,-112.0740": points_payload,
            "https://api.weather.gov/gridpoints/PSR/170,56": incomplete_grid_payload,
        },
    )

    with pytest.raises(NoaaDataError, match="noaa_payload_incomplete"):
        client.fetch_forecast_window(signal_input)
