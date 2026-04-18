from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from config.settings import ScanSettings
from core.models import CandidateRecord, CandidateStatus
from core.storage import CandidateStorage
from strategies.weather.edge_calculator import WeatherEdgeCalculator
from strategies.weather.noaa_client import NoaaDataError
from strategies.weather.signal_engine import SignalEngine
from strategies.weather.types import NoaaForecastWindow


class StubNoaaForecastClient:
    def __init__(self, windows: dict[str, NoaaForecastWindow], errors: dict[str, str] | None = None) -> None:
        self.windows = windows
        self.errors = errors or {}

    def fetch_forecast_window(self, signal_input):  # noqa: ANN001
        if signal_input.market_id in self.errors:
            raise NoaaDataError(self.errors[signal_input.market_id])
        return self.windows[signal_input.market_id]


def test_signal_engine_persists_mapping_forecast_edge_and_reason_fields(
    temp_sqlite_db_path: Path,
) -> None:
    settings = ScanSettings(
        database_path=str(temp_sqlite_db_path),
        minimum_edge_to_trade=0.10,
    )
    storage = CandidateStorage.from_settings(settings)
    approved = _approved_candidate(
        market_id="wx-temp-phx-001",
        location="Phoenix",
        location_key="phoenix",
        threshold=110.0,
        no_price=0.42,
    )
    low_edge = _approved_candidate(
        market_id="wx-rain-nyc-004",
        location="New York",
        location_key="new-york",
        contract_family="precipitation",
        title="Will New York record measurable rain on April 18?",
        threshold=None,
        unit=None,
        no_price=0.55,
    )
    stale = _approved_candidate(
        market_id="wx-temp-mia-005",
        location="Miami",
        location_key="miami",
        threshold=95.0,
        no_price=0.48,
    )
    for candidate in (approved, low_edge, stale):
        storage.save_candidate(candidate)

    engine = SignalEngine(
        noaa_client=StubNoaaForecastClient(
            windows={
                approved.market_id: _temperature_window("phoenix", 112.0, 111.0),
                low_edge.market_id: _precipitation_window("new-york", 40.0, 0.0),
            },
            errors={stale.market_id: "noaa_data_stale"},
        ),
        edge_calculator=WeatherEdgeCalculator(settings=settings),
        storage=storage,
        settings=settings,
    )

    result = engine.evaluate_candidates()

    assert result.inserted_count == 3
    assert [record.market_id for record in result.accepted] == ["wx-temp-phx-001"]
    assert [record.market_id for record in result.rejected] == ["wx-rain-nyc-004", "wx-temp-mia-005"]

    persisted = storage.list_signal_evaluations()
    assert [record.market_id for record in persisted] == [
        "wx-rain-nyc-004",
        "wx-temp-mia-005",
        "wx-temp-phx-001",
    ]

    accepted = next(record for record in persisted if record.market_id == approved.market_id)
    assert accepted.mapping_city_key == "phoenix"
    assert accepted.forecast_update_time == "2026-04-18T04:00:00+00:00"
    assert accepted.forecast_source_url == "https://api.weather.gov/gridpoints/PHX/1,1"
    assert accepted.no_price == 0.42
    assert accepted.derived_yes_probability == 0.3
    assert accepted.derived_no_probability == 0.7
    assert accepted.edge_against_no_price == 0.27999999999999997
    assert accepted.status.value == "accepted"
    assert accepted.decision_reason == "edge_threshold_passed"

    low_edge_record = next(record for record in persisted if record.market_id == low_edge.market_id)
    assert low_edge_record.mapping_city_key == "new-york"
    assert low_edge_record.forecast_update_time == "2026-04-18T04:00:00+00:00"
    assert low_edge_record.forecast_source_url == "https://api.weather.gov/gridpoints/NYC/1,1"
    assert low_edge_record.no_price == 0.55
    assert low_edge_record.edge_against_no_price == -0.15000000000000002
    assert low_edge_record.status.value == "rejected"
    assert low_edge_record.decision_reason == "edge_below_threshold"
    assert low_edge_record.evidence["probability_of_precipitation"] == (40.0,)

    stale_record = next(record for record in persisted if record.market_id == stale.market_id)
    assert stale_record.mapping_city_key == "miami"
    assert stale_record.forecast_update_time is None
    assert stale_record.forecast_source_url is None
    assert stale_record.no_price == 0.48
    assert stale_record.edge_against_no_price is None
    assert stale_record.status.value == "rejected"
    assert stale_record.decision_reason == "noaa_data_stale"
    assert stale_record.evidence["reason_codes"] == ["noaa_data_stale"]


def _approved_candidate(
    *,
    market_id: str,
    location: str,
    location_key: str,
    threshold: float | None,
    no_price: float,
    contract_family: str = "temperature",
    title: str | None = None,
    unit: str | None = "F",
) -> CandidateRecord:
    return CandidateRecord(
        market_id=market_id,
        title=title or f"Will {location} hit 110F or higher on April 18?",
        status=CandidateStatus.APPROVED,
        location=location,
        contract_family=contract_family,
        metric=contract_family,
        threshold=threshold,
        unit=unit,
        no_price=no_price,
        liquidity_usd=8000.0,
        resolution_hours=36,
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
        location_key=location_key,
        normalization_status=CandidateStatus.APPROVED,
    )


def _temperature_window(location_key: str, *values: float) -> NoaaForecastWindow:
    return NoaaForecastWindow(
        location_key=location_key,
        contract_family="temperature",
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
        temperature_overlap_values=values,
        probability_of_precipitation=(),
        quantitative_precipitation=(),
        update_time=datetime(2026, 4, 18, 4, 0, tzinfo=UTC),
        forecast_source_url="https://api.weather.gov/gridpoints/PHX/1,1",
    )


def _precipitation_window(location_key: str, pop: float, qpf: float) -> NoaaForecastWindow:
    return NoaaForecastWindow(
        location_key=location_key,
        contract_family="precipitation",
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-04:00",
        market_window_end_local="2026-04-19T00:00:00-04:00",
        temperature_overlap_values=(),
        probability_of_precipitation=(pop,),
        quantitative_precipitation=(qpf,),
        update_time=datetime(2026, 4, 18, 4, 0, tzinfo=UTC),
        forecast_source_url="https://api.weather.gov/gridpoints/NYC/1,1",
    )
