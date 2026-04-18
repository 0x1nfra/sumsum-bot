from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from config.settings import ScanSettings
from strategies.weather.edge_calculator import WeatherEdgeCalculator
from strategies.weather.types import NoaaForecastWindow, WeatherSignalInput


@pytest.fixture()
def edge_settings() -> ScanSettings:
    return ScanSettings(minimum_edge_to_trade=0.10)


@pytest.fixture()
def temperature_signal_input() -> WeatherSignalInput:
    return WeatherSignalInput(
        market_id="wx-temp-phx-001",
        title="Will Phoenix hit 110F or higher on April 18?",
        contract_family="temperature",
        location="Phoenix",
        location_key="phoenix",
        threshold=110.0,
        unit="F",
        no_price=0.12,
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
    )


@pytest.fixture()
def temperature_noaa_window() -> NoaaForecastWindow:
    return NoaaForecastWindow(
        location_key="phoenix",
        contract_family="temperature",
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
        temperature_overlap_values=(111.0, 113.0, 115.0),
        probability_of_precipitation=(10.0,),
        quantitative_precipitation=(0.0,),
        update_time=datetime(2026, 4, 18, 8, tzinfo=UTC),
        forecast_source_url="https://api.weather.gov/gridpoints/PSR/170,56",
    )


@pytest.fixture()
def precipitation_signal_input() -> WeatherSignalInput:
    return WeatherSignalInput(
        market_id="wx-rain-sea-001",
        title="Will Seattle record measurable rain on April 18?",
        contract_family="precipitation",
        location="Seattle",
        location_key="seattle",
        threshold=0.0,
        unit="in",
        no_price=0.12,
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
    )


@pytest.fixture()
def precipitation_noaa_window() -> NoaaForecastWindow:
    return NoaaForecastWindow(
        location_key="seattle",
        contract_family="precipitation",
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
        temperature_overlap_values=(58.0, 57.0),
        probability_of_precipitation=(65.0, 80.0),
        quantitative_precipitation=(0.08, 0.22),
        update_time=datetime(2026, 4, 18, 9, tzinfo=UTC),
        forecast_source_url="https://api.weather.gov/gridpoints/SEW/125,67",
    )


def test_temperature_signal_accepts_when_noaa_no_edge_exceeds_threshold(
    edge_settings: ScanSettings,
    temperature_signal_input: WeatherSignalInput,
    temperature_noaa_window: NoaaForecastWindow,
) -> None:
    calculator = WeatherEdgeCalculator(edge_settings)

    evaluation = calculator.calculate(temperature_signal_input, temperature_noaa_window)

    assert evaluation.accepted is True
    assert evaluation.derived_yes_probability == pytest.approx(0.70)
    assert evaluation.derived_no_probability == pytest.approx(0.30)
    assert evaluation.edge_against_no_price == pytest.approx(0.18)
    assert evaluation.reason_codes == ()
    assert evaluation.evidence["temperature_overlap_values"] == (111.0, 113.0, 115.0)
    assert evaluation.evidence["oriented_temperature_margin"] == pytest.approx(3.0)
    assert evaluation.evidence["temperature_band_label"] == ">= 2.0 and < 5.0"
    assert evaluation.evidence["market_date_local"] == date(2026, 4, 18).isoformat()
    assert evaluation.edge_against_no_price > edge_settings.minimum_edge_to_trade


@pytest.mark.parametrize(
    ("temperatures", "expected_probability", "expected_label", "expected_margin"),
    [
        ((115.0,), 0.85, ">= 5.0", 5.0),
        ((113.0,), 0.70, ">= 2.0 and < 5.0", 3.0),
        ((111.0,), 0.55, "> -2.0 and < 2.0", 1.0),
        ((108.0,), 0.30, "> -5.0 and <= -2.0", -2.0),
        ((104.0,), 0.15, "<= -5.0", -6.0),
    ],
)
def test_temperature_signal_uses_exact_margin_probability_bands(
    edge_settings: ScanSettings,
    temperature_signal_input: WeatherSignalInput,
    temperature_noaa_window: NoaaForecastWindow,
    temperatures: tuple[float, ...],
    expected_probability: float,
    expected_label: str,
    expected_margin: float,
) -> None:
    calculator = WeatherEdgeCalculator(edge_settings)
    forecast_window = NoaaForecastWindow(
        **{
            **temperature_noaa_window.__dict__,
            "temperature_overlap_values": temperatures,
        }
    )

    evaluation = calculator.calculate(temperature_signal_input, forecast_window)

    assert evaluation.derived_yes_probability == pytest.approx(expected_probability)
    assert evaluation.evidence["oriented_temperature_margin"] == pytest.approx(expected_margin)
    assert evaluation.evidence["temperature_band_label"] == expected_label


def test_temperature_signal_rejects_when_edge_below_threshold(
    edge_settings: ScanSettings,
    temperature_signal_input: WeatherSignalInput,
    temperature_noaa_window: NoaaForecastWindow,
) -> None:
    calculator = WeatherEdgeCalculator(edge_settings)
    low_edge_signal = WeatherSignalInput(
        **{**temperature_signal_input.__dict__, "no_price": 0.24}
    )

    evaluation = calculator.calculate(low_edge_signal, temperature_noaa_window)

    assert evaluation.accepted is False
    assert evaluation.derived_yes_probability == pytest.approx(0.70)
    assert evaluation.derived_no_probability == pytest.approx(0.30)
    assert evaluation.edge_against_no_price == pytest.approx(0.06)
    assert evaluation.reason_codes == ("edge_below_threshold",)
    assert evaluation.evidence["minimum_edge_to_trade"] == pytest.approx(0.10)


def test_precipitation_signal_uses_pop_and_qpf_evidence(
    edge_settings: ScanSettings,
    precipitation_signal_input: WeatherSignalInput,
    precipitation_noaa_window: NoaaForecastWindow,
) -> None:
    calculator = WeatherEdgeCalculator(edge_settings)

    evaluation = calculator.calculate(precipitation_signal_input, precipitation_noaa_window)

    assert evaluation.accepted is True
    assert evaluation.derived_yes_probability == pytest.approx(0.725)
    assert evaluation.derived_no_probability == pytest.approx(0.275)
    assert evaluation.edge_against_no_price == pytest.approx(0.155)
    assert evaluation.reason_codes == ()
    assert evaluation.evidence["probability_of_precipitation"] == (65.0, 80.0)
    assert evaluation.evidence["quantitative_precipitation"] == (0.08, 0.22)
    assert evaluation.evidence["maximum_probability_of_precipitation"] == pytest.approx(0.80)
    assert evaluation.evidence["maximum_quantitative_precipitation"] == pytest.approx(0.22)


def test_precipitation_signal_rejects_when_overlap_points_are_missing(
    edge_settings: ScanSettings,
    precipitation_signal_input: WeatherSignalInput,
    precipitation_noaa_window: NoaaForecastWindow,
) -> None:
    calculator = WeatherEdgeCalculator(edge_settings)
    missing_overlap_window = NoaaForecastWindow(
        **{
            **precipitation_noaa_window.__dict__,
            "probability_of_precipitation": (),
            "quantitative_precipitation": (),
        }
    )

    evaluation = calculator.calculate(precipitation_signal_input, missing_overlap_window)

    assert evaluation.accepted is False
    assert evaluation.derived_yes_probability is None
    assert evaluation.derived_no_probability is None
    assert evaluation.edge_against_no_price is None
    assert evaluation.reason_codes == ("insufficient_forecast_overlap", "noaa_payload_incomplete")
    assert evaluation.evidence["probability_of_precipitation"] == ()
    assert evaluation.evidence["quantitative_precipitation"] == ()
