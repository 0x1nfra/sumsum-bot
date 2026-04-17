"""Shared candidate-domain models for market discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CandidateStatus(StrEnum):
    APPROVED = "approved"
    REVIEW = "review"
    REJECTED = "rejected"


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
    metric: str | None = None
    region: str | None = None
    threshold: float | None = None
    unit: str | None = None
    no_price: float | None = None
    liquidity_usd: float | None = None
    resolution_hours: int | None = None
    normalization_status: CandidateStatus | None = None
    rejection_reasons: tuple[str, ...] = field(default_factory=tuple)
