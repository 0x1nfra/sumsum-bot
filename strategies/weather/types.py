"""Weather-market types used by normalization and scanner layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from core.models import CandidateRecord, CandidateStatus


@dataclass(frozen=True)
class WeatherMarketCandidate:
    """Parsed weather-market candidate with explicit support status."""

    market_id: str
    title: str
    status: CandidateStatus
    contract_family: str | None
    location: str
    threshold: float | None
    unit: str | None
    resolution_at: datetime | None
    no_price: float
    liquidity_usd: float
    reason_codes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def resolution_hours(self) -> int | None:
        if self.resolution_at is None:
            return None
        now = datetime.now(tz=self.resolution_at.tzinfo)
        delta = self.resolution_at - now
        return max(int(delta.total_seconds() // 3600), 0)

    def to_candidate_record(self) -> CandidateRecord:
        return CandidateRecord(
            market_id=self.market_id,
            title=self.title,
            status=self.status,
            location=self.location,
            metric=self.contract_family,
            threshold=self.threshold,
            unit=self.unit,
            no_price=self.no_price,
            liquidity_usd=self.liquidity_usd,
            resolution_hours=self.resolution_hours,
            normalization_status=self.status,
            rejection_reasons=self.reason_codes,
        )
