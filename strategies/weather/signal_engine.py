"""Thin signal-evaluation orchestration over NOAA, edge math, storage, and risk gating."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from config.settings import ScanSettings, get_settings
from core.models import (
    CandidateRecord,
    CandidateStatus,
    PortfolioSnapshot,
    RiskDecisionRecord,
    RiskDecisionStatus,
    SignalEvaluationRecord,
    SignalEvaluationStatus,
)
from core.risk_manager import RiskManager
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


@dataclass(frozen=True)
class SignalRiskGateResult:
    source: str
    allowed: tuple[RiskDecisionRecord, ...]
    blocked: tuple[RiskDecisionRecord, ...]
    risk_decision_count: int


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
        approved_candidates = tuple(
            self.storage.list_candidates(CandidateStatus.APPROVED) if candidates is None else candidates
        )
        evaluations: list[SignalEvaluationRecord] = []

        for candidate in approved_candidates:
            try:
                signal_input = WeatherSignalInput.from_candidate_record(candidate)
            except ValueError as exc:
                evaluations.append(
                    self._rejected_candidate_evaluation(
                        candidate,
                        reason_code="invalid_signal_input",
                        detail=str(exc),
                    )
                )
                continue

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

    def evaluate_risk_for_signal(
        self,
        signal_evaluations: SignalEvaluationRecord | tuple[SignalEvaluationRecord, ...] | list[SignalEvaluationRecord],
        *,
        portfolio: PortfolioSnapshot,
        risk_manager: RiskManager | None = None,
        cooldown_active_until: str | None = None,
        now: datetime | None = None,
    ) -> SignalRiskGateResult:
        evaluation_batch = (
            (signal_evaluations,)
            if isinstance(signal_evaluations, SignalEvaluationRecord)
            else tuple(signal_evaluations)
        )
        manager = risk_manager or RiskManager(settings=self.settings)
        decisions = tuple(
            manager.evaluate_risk_for_signal(
                evaluation,
                portfolio,
                window_key=(
                    evaluation.market_window_start_local
                    or evaluation.market_date_local
                    or evaluation.market_id
                ),
                cooldown_active_until=cooldown_active_until,
                now=now,
            )
            for evaluation in evaluation_batch
        )
        risk_decision_count = self.storage.persist_risk_decisions(
            "signal-risk-gate",
            decisions,
        )
        allowed = tuple(
            decision for decision in decisions if decision.decision_status is RiskDecisionStatus.ALLOWED
        )
        blocked = tuple(
            decision for decision in decisions if decision.decision_status is RiskDecisionStatus.BLOCKED
        )
        return SignalRiskGateResult(
            source="signal-risk-gate",
            allowed=allowed,
            blocked=blocked,
            risk_decision_count=risk_decision_count,
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
        return self._rejected_candidate_evaluation(candidate, reason_code=reason_code)

    def _rejected_candidate_evaluation(
        self,
        candidate: CandidateRecord,
        *,
        reason_code: str,
        detail: str | None = None,
    ) -> SignalEvaluationRecord:
        evidence = {
            "market_id": candidate.market_id,
            "contract_family": candidate.contract_family,
            "mapping_city_key": candidate.location_key,
            "market_date_local": candidate.market_date_local,
            "market_window_start_local": candidate.market_window_start_local,
            "market_window_end_local": candidate.market_window_end_local,
            "reason_codes": [reason_code],
        }
        if detail:
            evidence["error_detail"] = detail

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
            evidence=self._json_ready_evidence(evidence),
        )

    def _json_ready_evidence(self, value: object) -> object:
        if isinstance(value, dict):
            return {str(key): self._json_ready_evidence(item) for key, item in value.items()}
        if isinstance(value, tuple | list):
            return [self._json_ready_evidence(item) for item in value]
        return value

    def _string_or_none(self, value: object) -> str | None:
        return value if isinstance(value, str) else None
