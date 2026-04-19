"""Shared candidate-domain models for market discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CandidateStatus(StrEnum):
    APPROVED = "approved"
    REVIEW = "review"
    REJECTED = "rejected"


class SignalEvaluationStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class RiskDecisionStatus(StrEnum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"


class PaperPositionStatus(StrEnum):
    """Paper-trade lifecycle states for immediate-fill weather positions."""

    ENTERED = "entered"
    OPEN = "open"
    RESOLVED = "resolved"


class RejectionReason(StrEnum):
    AMBIGUOUS_THRESHOLD = "ambiguous_threshold"
    UNSUPPORTED_WEATHER_TYPE = "unsupported_weather_type"
    INSUFFICIENT_LIQUIDITY = "insufficient_liquidity"
    NO_PRICE_TOO_HIGH = "no_price_too_high"
    RESOLUTION_WINDOW_TOO_LONG = "resolution_window_too_long"
    NORMALIZATION_REVIEW = "normalization_review"
    NORMALIZATION_REJECTED = "normalization_rejected"


@dataclass(frozen=True)
class ScanResultMetadata:
    """Summary for one scanner run."""

    source: str
    candidate_count: int
    approved_count: int
    review_count: int
    rejected_count: int


@dataclass(frozen=True)
class CandidateRecord:
    """Stable shared vocabulary for normalized market candidates."""

    market_id: str
    title: str
    status: CandidateStatus
    location: str
    contract_family: str | None = None
    metric: str | None = None
    region: str | None = None
    threshold: float | None = None
    unit: str | None = None
    no_price: float | None = None
    liquidity_usd: float | None = None
    resolution_hours: int | None = None
    market_date_local: str | None = None
    market_window_start_local: str | None = None
    market_window_end_local: str | None = None
    location_key: str | None = None
    normalization_status: CandidateStatus | None = None
    rejection_reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SignalEvaluationRecord:
    """Append-only stored signal evaluation for one market decision."""

    market_id: str
    scan_run_id: int | None
    location: str
    mapping_city_key: str
    contract_family: str | None
    market_date_local: str | None
    market_window_start_local: str | None
    market_window_end_local: str | None
    forecast_update_time: str | None
    forecast_source_url: str | None
    no_price: float
    derived_yes_probability: float | None
    derived_no_probability: float | None
    edge_against_no_price: float | None
    decision_reason: str
    status: SignalEvaluationStatus
    evidence: dict[str, object] = field(default_factory=dict)
    signal_evaluation_id: int | None = None


@dataclass(frozen=True)
class PortfolioSnapshot:
    """Immutable bankroll and exposure state used by risk policy."""

    current_bankroll_usd: float
    peak_bankroll_usd: float
    open_exposure_usd: float
    open_exposure_by_window: dict[str, float] = field(default_factory=dict)
    captured_at: str = ""


@dataclass(frozen=True)
class RiskDecisionRecord:
    """Append-only risk decision emitted for one signal evaluation."""

    signal_evaluation_id: int | None
    market_id: str
    window_key: str
    decision_status: RiskDecisionStatus
    decision_reason: str
    triggered_rule_codes: tuple[str, ...]
    current_bankroll_usd: float
    peak_bankroll_usd: float
    open_exposure_usd: float
    window_exposure_usd: float
    proposed_stake_usd: float
    allowed_stake_usd: float
    evidence: dict[str, object] = field(default_factory=dict)
    evaluated_at: str | None = None


@dataclass(frozen=True)
class PaperPositionRecord:
    """Durable paper position.

    `entered` means the immediate paper fill has been created and reserved cash has
    been snapshotted. `open` means the persisted position has been activated for
    later polling and restoration without a second stake deduction. `resolved`
    means terminal settlement has completed and realized PnL is final.
    """

    position_id: str
    market_id: str
    risk_decision_id: int | None
    signal_evaluation_id: int | None
    entry_price: float
    stake_usd: float
    contract_count: float
    status: PaperPositionStatus
    entered_at: str
    opened_at: str | None = None
    resolved_at: str | None = None
    resolution_price: float | None = None
    realized_pnl_usd: float | None = None
    evidence: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class PaperTradeEvent:
    """Append-only paper lifecycle event such as paper_entry, paper_open, or paper_resolution."""

    position_id: str
    event_type: str
    event_timestamp: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class BankrollSnapshot:
    """Durable bankroll state recorded at each lifecycle boundary."""

    current_bankroll_usd: float
    peak_bankroll_usd: float
    available_cash_usd: float
    open_exposure_usd: float
    snapshot_reason: str
    captured_at: str
