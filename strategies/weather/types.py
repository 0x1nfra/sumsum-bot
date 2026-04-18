"""Weather-market types used by normalization and scanner layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
import re
from zoneinfo import ZoneInfo

from config.weather_locations import get_weather_location, normalize_city_key
from core.models import CandidateRecord, CandidateStatus

MARKET_DATE_PATTERN = re.compile(r" on (?P<month>[A-Za-z]+) (?P<day>\d{1,2})\?")


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
        contract_family = self.contract_family
        market_date_local, market_window_start_local, market_window_end_local = self._contract_window_fields()
        location_key = normalize_city_key(self.location) if self.location else None
        return CandidateRecord(
            market_id=self.market_id,
            title=self.title,
            status=self.status,
            location=self.location,
            contract_family=contract_family,
            metric=contract_family,
            threshold=self.threshold,
            unit=self.unit,
            no_price=self.no_price,
            liquidity_usd=self.liquidity_usd,
            resolution_hours=self.resolution_hours,
            market_date_local=market_date_local,
            market_window_start_local=market_window_start_local,
            market_window_end_local=market_window_end_local,
            location_key=location_key,
            normalization_status=self.status,
            rejection_reasons=self.reason_codes,
        )

    def _contract_window_fields(self) -> tuple[str | None, str | None, str | None]:
        market_date = self._market_date_local()
        if market_date is None:
            return None, None, None

        mapping = get_weather_location(self.location)
        timezone_name = mapping.timezone if mapping is not None else "UTC"
        local_zone = ZoneInfo(timezone_name)
        start = datetime.combine(market_date, time.min, tzinfo=local_zone)
        end = start + timedelta(days=1)
        return market_date.isoformat(), start.isoformat(), end.isoformat()

    def _market_date_local(self) -> date | None:
        if self.status is not CandidateStatus.APPROVED or self.resolution_at is None:
            return None
        match = MARKET_DATE_PATTERN.search(self.title)
        if match is None:
            return None
        mapping = get_weather_location(self.location)
        local_zone = ZoneInfo(mapping.timezone) if mapping is not None else ZoneInfo("UTC")
        year = self.resolution_at.astimezone(local_zone).year
        return datetime.strptime(
            f"{match.group('month')} {match.group('day')} {year}",
            "%B %d %Y",
        ).date()


@dataclass(frozen=True)
class WeatherSignalInput:
    market_id: str
    title: str
    contract_family: str
    location: str
    location_key: str
    threshold: float | None
    unit: str | None
    no_price: float
    market_date_local: str
    market_window_start_local: str
    market_window_end_local: str

    @classmethod
    def from_candidate_record(cls, candidate: CandidateRecord) -> "WeatherSignalInput":
        missing_fields = [
            field_name
            for field_name in (
                "contract_family",
                "location_key",
                "market_date_local",
                "market_window_start_local",
                "market_window_end_local",
                "no_price",
            )
            if getattr(candidate, field_name) in (None, "")
        ]
        if missing_fields:
            missing_csv = ", ".join(missing_fields)
            raise ValueError(f"candidate record missing NOAA signal fields: {missing_csv}")

        return cls(
            market_id=candidate.market_id,
            title=candidate.title,
            contract_family=candidate.contract_family or candidate.metric or "",
            location=candidate.location,
            location_key=candidate.location_key or "",
            threshold=candidate.threshold,
            unit=candidate.unit,
            no_price=float(candidate.no_price),
            market_date_local=candidate.market_date_local or "",
            market_window_start_local=candidate.market_window_start_local or "",
            market_window_end_local=candidate.market_window_end_local or "",
        )


@dataclass(frozen=True)
class NoaaForecastPoint:
    city_key: str
    market_label: str
    latitude: float
    longitude: float
    timezone: str
    forecast_grid_url: str
    forecast_hourly_url: str | None = None


@dataclass(frozen=True)
class NoaaForecastWindow:
    location_key: str
    contract_family: str
    market_date_local: str
    market_window_start_local: str
    market_window_end_local: str
    temperature_overlap_values: tuple[float, ...]
    probability_of_precipitation: tuple[float, ...]
    quantitative_precipitation: tuple[float, ...]
    update_time: datetime
    forecast_source_url: str
