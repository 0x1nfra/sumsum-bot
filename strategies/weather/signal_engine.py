"""Thin signal-evaluation orchestration over NOAA, edge math, and storage."""

from __future__ import annotations

from dataclasses import dataclass

from config.settings import ScanSettings, get_settings
from core.models import CandidateRecord, CandidateStatus, SignalEvaluationRecord, SignalEvaluationStatus
from core.storage import CandidateStorage
from strategies.weather.edge_calculator import SignalEvaluation, WeatherEdgeCalculator
from strategies.weather.noaa_client import NoaaDataError, NoaaForecastClient
from strategies.weather.types import WeatherSignalInput


@dataclass(frozen=True)
class SignalEngineResult:
    source: str
    accepted: tuple[SignalEvaluationRecord, ...]
    rejected: tuple[SignalEvaluationRecord, ...]
    inserted_count: int

    @property
    def all_evaluations(self) -> tuple[SignalEvaluationRecord, ...]:
        return self.accepted + self.rejected


class SignalEngine:
    """Evaluate approved candidates and persist append-only signal history."""

    def __init__(
        self,
        noaa_client: NoaaForecastClient | None = None,
        edge_calculator: WeatherEdgeCalculator | None = None,
        storage: CandidateStorage | None = None,
        settings: ScanSettings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.noaa_client = noaa_client or NoaaForecastClient(settings=self.settings)
        self.edge_calculator = edge_calculator or WeatherEdgeCalculator(settings=self.settings)
        self.storage = storage or CandidateStorage.from_settings(self.settings)

    def evaluate_candidates(
        self,
        candidates: tuple[CandidateRecord, ...] | list[CandidateRecord] | None = None,
    ) -> SignalEngineResult:
        approved_candidates = tuple(candidates or self.storage.list_candidates(CandidateStatus.APPROVED))
        evaluations: list[SignalEvaluationRecord] = []

        for candidate in approved_candidates:
            signal_input = WeatherSignalInput.from_candidate_record(candidate)
            try:
                forecast_window = self.noaa_client.fetch_forecast_window(signal_input)
            except NoaaDataError as exc:
                evaluations.append(self._rejected_noaa_evaluation(candidate, str(exc)))
                continue

            evaluation = self.edge_calculator.calculate(signal_input, forecast_window)
            evaluations.append(self._record_from_evaluation(candidate, evaluation))

        inserted_count = self.storage.persist_signal_evaluations("signal-engine", evaluations)
        accepted = tuple(
            evaluation for evaluation in evaluations if evaluation.status is SignalEvaluationStatus.ACCEPTED
        )
        rejected = tuple(
            evaluation for evaluation in evaluations if evaluation.status is SignalEvaluationStatus.REJECTED
        )
        return SignalEngineResult(
            source="signal-engine",
            accepted=accepted,
            rejected=rejected,
            inserted_count=inserted_count,
        )

    def _record_from_evaluation(
        self,
        candidate: CandidateRecord,
        evaluation: SignalEvaluation,
    ) -> SignalEvaluationRecord:
        decision_reason = (
            "edge_threshold_passed"
            if evaluation.accepted
            else (evaluation.reason_codes[0] if evaluation.reason_codes else "rejected")
        )
        return SignalEvaluationRecord(
            market_id=candidate.market_id,
            scan_run_id=None,
            location=candidate.location,
            mapping_city_key=candidate.location_key or "",
            contract_family=candidate.contract_family or candidate.metric,
            market_date_local=candidate.market_date_local,
            market_window_start_local=candidate.market_window_start_local,
            market_window_end_local=candidate.market_window_end_local,
            forecast_update_time=self._string_or_none(evaluation.evidence.get("forecast_update_time")),
            forecast_source_url=self._string_or_none(evaluation.evidence.get("forecast_source_url")),
            no_price=float(candidate.no_price or 0.0),
            derived_yes_probability=evaluation.derived_yes_probability,
            derived_no_probability=evaluation.derived_no_probability,
            edge_against_no_price=evaluation.edge_against_no_price,
            decision_reason=decision_reason,
            status=(
                SignalEvaluationStatus.ACCEPTED
                if evaluation.accepted
                else SignalEvaluationStatus.REJECTED
            ),
            evidence=self._json_ready_evidence(
                {
                    **evaluation.evidence,
                    "reason_codes": list(evaluation.reason_codes),
                }
            ),
        )

    def _rejected_noaa_evaluation(
        self,
        candidate: CandidateRecord,
        reason_code: str,
    ) -> SignalEvaluationRecord:
        return SignalEvaluationRecord(
            market_id=candidate.market_id,
            scan_run_id=None,
            location=candidate.location,
            mapping_city_key=candidate.location_key or "",
            contract_family=candidate.contract_family or candidate.metric,
            market_date_local=candidate.market_date_local,
            market_window_start_local=candidate.market_window_start_local,
            market_window_end_local=candidate.market_window_end_local,
            forecast_update_time=None,
            forecast_source_url=None,
            no_price=float(candidate.no_price or 0.0),
            derived_yes_probability=None,
            derived_no_probability=None,
            edge_against_no_price=None,
            decision_reason=reason_code,
            status=SignalEvaluationStatus.REJECTED,
            evidence=self._json_ready_evidence(
                {
                    "market_id": candidate.market_id,
                    "contract_family": candidate.contract_family,
                    "mapping_city_key": candidate.location_key,
                    "market_date_local": candidate.market_date_local,
                    "market_window_start_local": candidate.market_window_start_local,
                    "market_window_end_local": candidate.market_window_end_local,
                    "reason_codes": [reason_code],
                }
            ),
        )

    def _json_ready_evidence(self, value: object) -> object:
        if isinstance(value, dict):
            return {str(key): self._json_ready_evidence(item) for key, item in value.items()}
        if isinstance(value, tuple | list):
            return [self._json_ready_evidence(item) for item in value]
        return value

    def _string_or_none(self, value: object) -> str | None:
        return value if isinstance(value, str) else None
