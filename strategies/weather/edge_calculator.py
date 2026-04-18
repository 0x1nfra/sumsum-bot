"""Weather edge-calculation utilities for NOAA-backed signal evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from config.settings import ScanSettings, get_settings
from strategies.weather.types import NoaaForecastWindow, WeatherSignalInput


@dataclass(frozen=True)
class SignalEvaluation:
    accepted: bool
    derived_yes_probability: float | None
    derived_no_probability: float | None
    edge_against_no_price: float | None
    reason_codes: tuple[str, ...]
    evidence: dict[str, object]


class WeatherEdgeCalculator:
    """Derive inspectable weather probabilities from NOAA overlap evidence."""

    def __init__(self, settings: ScanSettings | None = None) -> None:
        self.settings = settings or get_settings()

    def calculate(
        self,
        signal_input: WeatherSignalInput,
        forecast_window: NoaaForecastWindow,
    ) -> SignalEvaluation:
        contract_family = signal_input.contract_family
        if contract_family == "temperature":
            return self._evaluate_temperature(signal_input, forecast_window)
        if contract_family == "precipitation":
            return self._evaluate_precipitation(signal_input, forecast_window)
        return SignalEvaluation(
            accepted=False,
            derived_yes_probability=None,
            derived_no_probability=None,
            edge_against_no_price=None,
            reason_codes=("unsupported_contract_family",),
            evidence=self._base_evidence(signal_input, forecast_window),
        )

    def _evaluate_temperature(
        self,
        signal_input: WeatherSignalInput,
        forecast_window: NoaaForecastWindow,
    ) -> SignalEvaluation:
        evidence = self._base_evidence(signal_input, forecast_window)
        overlap_values = forecast_window.temperature_overlap_values
        evidence["temperature_overlap_values"] = overlap_values

        if signal_input.threshold is None or not overlap_values:
            reason_codes = ("insufficient_forecast_overlap",)
            return self._reject(reason_codes, evidence)

        oriented_temperature_margin = max(overlap_values) - signal_input.threshold
        derived_yes_probability, temperature_band_label = self._temperature_probability_band(
            oriented_temperature_margin
        )

        evidence["oriented_temperature_margin"] = oriented_temperature_margin
        evidence["temperature_band_label"] = temperature_band_label

        return self._finalize_probability(derived_yes_probability, signal_input.no_price, evidence)

    def _evaluate_precipitation(
        self,
        signal_input: WeatherSignalInput,
        forecast_window: NoaaForecastWindow,
    ) -> SignalEvaluation:
        evidence = self._base_evidence(signal_input, forecast_window)
        probability_of_precipitation = forecast_window.probability_of_precipitation
        quantitative_precipitation = forecast_window.quantitative_precipitation

        evidence["probability_of_precipitation"] = probability_of_precipitation
        evidence["quantitative_precipitation"] = quantitative_precipitation

        if not probability_of_precipitation and not quantitative_precipitation:
            return self._reject(
                ("insufficient_forecast_overlap", "noaa_payload_incomplete"),
                evidence,
            )
        if not probability_of_precipitation or not quantitative_precipitation:
            return self._reject(("insufficient_forecast_overlap",), evidence)

        maximum_probability_of_precipitation = max(probability_of_precipitation) / 100.0
        maximum_quantitative_precipitation = max(quantitative_precipitation)

        evidence["maximum_probability_of_precipitation"] = maximum_probability_of_precipitation
        evidence["maximum_quantitative_precipitation"] = maximum_quantitative_precipitation

        average_pop_probability = mean(probability_of_precipitation) / 100.0
        if maximum_quantitative_precipitation <= 0.0:
            derived_yes_probability = min(average_pop_probability, 0.49)
        else:
            derived_yes_probability = average_pop_probability

        return self._finalize_probability(derived_yes_probability, signal_input.no_price, evidence)

    def _finalize_probability(
        self,
        derived_yes_probability: float,
        no_price: float,
        evidence: dict[str, object],
    ) -> SignalEvaluation:
        derived_no_probability = 1.0 - derived_yes_probability
        edge_against_no_price = derived_no_probability - no_price
        evidence["derived_yes_probability"] = derived_yes_probability
        evidence["derived_no_probability"] = derived_no_probability
        evidence["edge_against_no_price"] = edge_against_no_price

        if edge_against_no_price > self.settings.minimum_edge_to_trade:
            return SignalEvaluation(
                accepted=True,
                derived_yes_probability=derived_yes_probability,
                derived_no_probability=derived_no_probability,
                edge_against_no_price=edge_against_no_price,
                reason_codes=(),
                evidence=evidence,
            )

        evidence["minimum_edge_to_trade"] = self.settings.minimum_edge_to_trade
        return SignalEvaluation(
            accepted=False,
            derived_yes_probability=derived_yes_probability,
            derived_no_probability=derived_no_probability,
            edge_against_no_price=edge_against_no_price,
            reason_codes=("edge_below_threshold",),
            evidence=evidence,
        )

    def _reject(
        self,
        reason_codes: tuple[str, ...],
        evidence: dict[str, object],
    ) -> SignalEvaluation:
        return SignalEvaluation(
            accepted=False,
            derived_yes_probability=None,
            derived_no_probability=None,
            edge_against_no_price=None,
            reason_codes=reason_codes,
            evidence=evidence,
        )

    def _base_evidence(
        self,
        signal_input: WeatherSignalInput,
        forecast_window: NoaaForecastWindow,
    ) -> dict[str, object]:
        return {
            "market_id": signal_input.market_id,
            "contract_family": signal_input.contract_family,
            "location_key": signal_input.location_key,
            "market_date_local": signal_input.market_date_local,
            "market_window_start_local": signal_input.market_window_start_local,
            "market_window_end_local": signal_input.market_window_end_local,
            "forecast_source_url": forecast_window.forecast_source_url,
            "forecast_update_time": forecast_window.update_time.isoformat(),
        }

    def _temperature_probability_band(self, oriented_temperature_margin: float) -> tuple[float, str]:
        if oriented_temperature_margin >= 5.0:
            return 0.85, ">= 5.0"
        if oriented_temperature_margin >= 2.0:
            return 0.70, ">= 2.0 and < 5.0"
        if oriented_temperature_margin > -2.0:
            return 0.55, "> -2.0 and < 2.0"
        if oriented_temperature_margin > -5.0:
            return 0.30, "> -5.0 and <= -2.0"
        return 0.15, "<= -5.0"
