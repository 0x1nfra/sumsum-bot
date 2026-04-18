# Phase 02: NOAA Signal Engine - Pattern Map

**Mapped:** 2026-04-18
**Files analyzed:** 12
**Analogs found:** 12 / 12

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `config/settings.py` | config | request-response | `config/settings.py` | exact |
| `config/weather_locations.py` | config | transform | `config/settings.py` | role-match |
| `core/models.py` | model | transform | `core/models.py` | exact |
| `core/storage.py` | service | CRUD | `core/storage.py` | exact |
| `strategies/weather/noaa_client.py` | service | request-response | `core/clob_client.py` | role+flow |
| `strategies/weather/edge_calculator.py` | service | transform | `strategies/weather/normalization.py` | role+flow |
| `strategies/weather/signal_engine.py` | service | transform | `core/market_scanner.py` | role+flow |
| `strategies/weather/types.py` | model | transform | `strategies/weather/types.py` | exact |
| `tests/unit/test_settings.py` | test | request-response | `tests/unit/test_settings.py` | exact |
| `tests/unit/test_noaa_client.py` | test | request-response | `tests/unit/test_weather_normalization.py` | role+flow |
| `tests/unit/test_weather_edge_calculator.py` | test | transform | `tests/unit/test_weather_normalization.py` | exact |
| `tests/integration/test_storage.py` | test | CRUD | `tests/integration/test_storage.py` | exact |
| `tests/integration/test_signal_storage.py` | test | CRUD | `tests/integration/test_storage.py` | exact |
| `tests/integration/test_noaa_signal_engine.py` | test | transform | `tests/integration/test_market_scan.py` | role+flow |

## Pattern Assignments

### `config/settings.py` (config, request-response)

**Analog:** `config/settings.py`

**Imports + frozen dataclass pattern** ([config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:1)):
```python
from dataclasses import dataclass
import os
from typing import Mapping


@dataclass(frozen=True)
class ScanSettings:
```

**Env override loader pattern** ([config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:27)):
```python
def load_settings(
    overrides: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> ScanSettings:
    raw_env = dict(os.environ if environ is None else environ)
    if overrides:
        raw_env.update(overrides)

    return ScanSettings(...)
```

**Use for Phase 2:** extend the same `ScanSettings` dataclass with NOAA freshness, minimum edge, and any evaluation toggles instead of adding loose module constants.

---

### `config/weather_locations.py` (config, transform)

**Analog:** `config/settings.py`

**Data-only config shape** ([config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:10)):
```python
@dataclass(frozen=True)
class ScanSettings:
    database_path: str = "data/trades.db"
    min_market_liquidity_usd: int = 5000
    max_entry_price: float = 0.85
```

**Use for Phase 2:** create a frozen dataclass like `WeatherLocationMapping` and a module-level curated mapping table keyed by normalized city name. Keep the file deterministic and explicit; do not introduce lookup I/O here.

---

### `core/models.py` (model, transform)

**Analog:** `core/models.py`

**Enum + dataclass vocabulary pattern** ([core/models.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/models.py:9)):
```python
class CandidateStatus(StrEnum):
    APPROVED = "approved"
    REVIEW = "review"
    REJECTED = "rejected"


class RejectionReason(StrEnum):
    AMBIGUOUS_THRESHOLD = "ambiguous_threshold"
    UNSUPPORTED_WEATHER_TYPE = "unsupported_weather_type"
```

**Stable shared record pattern** ([core/models.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/models.py:25)):
```python
@dataclass(frozen=True)
class ScanResultMetadata:
    source: str
    candidate_count: int
    approved_count: int
    review_count: int
    rejected_count: int


@dataclass(frozen=True)
class CandidateRecord:
```

**Use for Phase 2:** add `SignalEvaluationStatus` / rejection-code enums and any shared evaluation metadata here if multiple modules need the same vocabulary.

---

### `core/storage.py` (service, CRUD)

**Analog:** `core/storage.py`

**Repository-style class + settings constructor** ([core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:35)):
```python
class CandidateStorage:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_settings(cls, settings: ScanSettings | None = None) -> "CandidateStorage":
        runtime_settings = settings or get_settings()
        return cls(runtime_settings.database_path)
```

**Schema bootstrap pattern** ([core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:52)):
```python
def bootstrap(self) -> None:
    with self.connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS scan_runs (...);
            CREATE TABLE IF NOT EXISTS accepted_candidates (...);
            CREATE TABLE IF NOT EXISTS scan_candidates (...);
            """
        )
```

**Persist aggregate + row-by-row detail pattern** ([core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:141)):
```python
def persist_scan_result(self, source: str, candidates: Iterable[CandidateRecord]) -> int:
    candidate_list = list(candidates)
    metadata = ScanResultMetadata(...)
    scan_run_id = self.save_scan_run(metadata)

    with self.connect() as connection:
        for candidate in candidate_list:
            self._insert_scan_candidate(connection, scan_run_id, candidate)
            self._upsert_bucket_candidate(connection, candidate)
        connection.commit()
```

**Detail-row insert pattern** ([core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:216)):
```python
def _insert_scan_candidate(...):
    reasons_csv = ",".join(candidate.rejection_reasons)
    primary_reason = candidate.rejection_reasons[0] if candidate.rejection_reasons else None
    connection.execute(
        """
        INSERT INTO scan_candidates (...)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (...),
    )
```

**Use for Phase 2:** keep the same `bootstrap -> persist_* -> private insert/upsert helpers` shape. Add a dedicated `signal_evaluations` table instead of overloading the latest-state candidate buckets.

---

### `strategies/weather/noaa_client.py` (service, request-response)

**Analog:** `core/clob_client.py`

**Imports + transport dataclass pattern** ([core/clob_client.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/clob_client.py:1)):
```python
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class RawMarketRecord:
```

**Dedicated client-specific error type** ([core/clob_client.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/clob_client.py:38)):
```python
class PolymarketPayloadError(ValueError):
    """Raised when a discovery payload is malformed or incomplete."""
```

**Validation before normalization pattern** ([core/clob_client.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/clob_client.py:56)):
```python
def load_markets(...) -> list[RawMarketRecord]:
    raw_markets = self._extract_market_payloads(payload)
    return [self._normalize_market(market) for market in raw_markets]

def _normalize_market(self, market: Mapping[str, object]) -> RawMarketRecord:
    missing = [field for field in self.required_fields if field not in market]
    if missing:
        raise PolymarketPayloadError(...)
```

**Use for Phase 2:** model NOAA responses with frozen dataclasses, raise a NOAA-specific `ValueError` subclass for malformed or incomplete responses, and keep request/parse/validate in one client boundary instead of spreading it across scanner code.

---

### `strategies/weather/edge_calculator.py` (service, transform)

**Analog:** `strategies/weather/normalization.py`

**Imports + regex/constants at module scope** ([strategies/weather/normalization.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/normalization.py:5)):
```python
from datetime import datetime
import re

from core.clob_client import RawMarketRecord
from core.models import CandidateStatus, RejectionReason
from strategies.weather.types import WeatherMarketCandidate
```

**Single entrypoint with branch-by-contract-family logic** ([strategies/weather/normalization.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/normalization.py:20)):
```python
def normalize_weather_market(market: RawMarketRecord) -> WeatherMarketCandidate:
    if match := TEMPERATURE_TITLE.match(title):
        return WeatherMarketCandidate(...)

    if match := PRECIPITATION_TITLE.match(title):
        return WeatherMarketCandidate(...)

    if _looks_weather_related(title):
        return WeatherMarketCandidate(..., reason_codes=(... ,))
```

**Use for Phase 2:** keep one public calculator entrypoint that dispatches to temperature and precipitation helpers, and return explicit reason codes for stale/misaligned/incomplete NOAA data rather than partial outputs.

---

### `strategies/weather/signal_engine.py` (service, transform)

**Analog:** `core/market_scanner.py`

**Frozen handoff/result dataclasses** ([core/market_scanner.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/market_scanner.py:15)):
```python
@dataclass(frozen=True)
class MarketScanHandoff:
    source: str
    settings: ScanSettings
    weather_markets: tuple[RawMarketRecord, ...]
    skipped_markets: tuple[RawMarketRecord, ...]


@dataclass(frozen=True)
class MarketScanResult:
```

**Thin orchestrator with injected dependencies** ([core/market_scanner.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/market_scanner.py:52)):
```python
class MarketScanner:
    def __init__(
        self,
        client: PolymarketDiscoveryClient | None = None,
        settings: ScanSettings | None = None,
    ) -> None:
        self.client = client or PolymarketDiscoveryClient()
        self.settings = settings or get_settings()
```

**Pipeline orchestration pattern** ([core/market_scanner.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/market_scanner.py:94)):
```python
def run_scan(..., storage: CandidateStorage | None = None) -> MarketScanResult:
    handoff = self.prepare_weather_scan(payload)
    weather_result = scan_weather_markets(...)
    result = MarketScanResult(...)

    if storage is None:
        return result

    scan_run_id = storage.persist_scan_result(result.source, result.all_candidates)
    return MarketScanResult(..., scan_run_id=scan_run_id)
```

**Use for Phase 2:** build `SignalEngine` as a thin coordinator over `weather_locations`, `NoaaForecastClient`, `WeatherEdgeCalculator`, and storage. Keep domain logic in helpers, not in the entrypoint method.

---

### `strategies/weather/types.py` (model, transform)

**Analog:** `strategies/weather/types.py`

**Frozen typed record + computed property pattern** ([strategies/weather/types.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/types.py:11)):
```python
@dataclass(frozen=True)
class WeatherMarketCandidate:
    market_id: str
    title: str
    status: CandidateStatus
    contract_family: str | None
    ...

    @property
    def resolution_hours(self) -> int | None:
```

**Conversion-to-shared-model pattern** ([strategies/weather/types.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/types.py:35)):
```python
def to_candidate_record(self) -> CandidateRecord:
    return CandidateRecord(
        market_id=self.market_id,
        title=self.title,
        status=self.status,
        ...
    )
```

**Use for Phase 2:** add frozen dataclasses like `WeatherSignalInput`, `NoaaForecastWindow`, and `SignalEvaluation`, with small computed properties and explicit conversions to any shared core model only where needed.

---

### `tests/unit/test_settings.py` (test, request-response)

**Analog:** `tests/unit/test_settings.py`

**Default-load assertion pattern** ([tests/unit/test_settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_settings.py:1)):
```python
settings = load_settings(environ={})
assert settings.database_path == "data/trades.db"
```

**Environment override assertion pattern** ([tests/unit/test_settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_settings.py:10)):
```python
settings = load_settings(environ={"MAX_ENTRY_PRICE": "0.72"})
assert settings.max_entry_price == 0.72
```

**Use for Phase 2:** extend this file with direct `load_settings()` assertions for NOAA env vars so config verification stays independent of NOAA-client behavior.

---

### `tests/unit/test_noaa_client.py` (test, request-response)

**Analog:** `tests/unit/test_weather_normalization.py`

**Direct import + focused function tests** ([tests/unit/test_weather_normalization.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_weather_normalization.py:1)):
```python
from core.clob_client import PolymarketDiscoveryClient
from core.models import CandidateStatus
from strategies.weather.normalization import normalize_weather_market
```

**Small, scenario-named tests** ([tests/unit/test_weather_normalization.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_weather_normalization.py:8)):
```python
def test_supported_titles_normalize_into_approved_weather_candidates(...) -> None:
    ...

def test_ambiguous_titles_are_routed_to_review_bucket(...) -> None:
    ...
```

**Use for Phase 2:** mirror this style with NOAA fixtures and assert on parsed forecast metadata, freshness, and explicit error/rejection cases one scenario at a time.

---

### `tests/unit/test_weather_edge_calculator.py` (test, transform)

**Analog:** `tests/unit/test_weather_normalization.py`

**Assertions on domain fields instead of snapshots** ([tests/unit/test_weather_normalization.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_weather_normalization.py:13)):
```python
assert normalized.status is CandidateStatus.APPROVED
assert normalized.contract_family in {"temperature", "precipitation"}
assert normalized.reason_codes == ()
```

**Use for Phase 2:** assert on `weather_yes_probability`, `weather_no_probability`, `edge`, `accepted`, and `reason_codes` explicitly. Keep unit tests deterministic and independent of SQLite.

---

### `tests/integration/test_storage.py` (test, CRUD)

**Analog:** `tests/integration/test_storage.py`

**Bootstrap + repository assertion pattern** ([tests/integration/test_storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_storage.py:8)):
```python
storage = CandidateStorage.from_settings(settings)
storage.bootstrap()
```

**Round-trip assertion pattern** ([tests/integration/test_storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_storage.py:24)):
```python
stored = storage.list_candidates(CandidateStatus.APPROVED)
assert stored[0].market_id == candidate.market_id
```

**Use for Phase 2:** extend this file with one targeted round-trip test for `contract_family`, `location_key`, `market_date_local`, `market_window_start_local`, and `market_window_end_local` before signal-engine work begins.

---

### `tests/integration/test_signal_storage.py` (test, CRUD)

**Analog:** `tests/integration/test_storage.py`

**SQLite bootstrap test pattern** ([tests/integration/test_storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_storage.py:8)):
```python
def test_storage_bootstrap_creates_phase_one_candidate_tables(temp_sqlite_db_path: Path) -> None:
    connection = bootstrap_storage(temp_sqlite_db_path)
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    }
```

**Row-level persistence assertion pattern** ([tests/integration/test_storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_storage.py:24)):
```python
row = connection.execute(
    "SELECT market_id, metric, location, no_price FROM accepted_candidates"
).fetchone()

assert tuple(row) == (...)
```

**Use for Phase 2:** add schema assertions for `signal_evaluations`, then assert persisted mapping, forecast freshness, derived probabilities, edge, and rejection reason columns/JSON fields directly through SQL queries.

---

### `tests/integration/test_noaa_signal_engine.py` (test, transform)

**Analog:** `tests/integration/test_market_scan.py`

**Settings override + injected storage pattern** ([tests/integration/test_market_scan.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_market_scan.py:19)):
```python
settings = ScanSettings(
    database_path=str(temp_sqlite_db_path),
    max_resolution_hours=200,
)
scanner = MarketScanner(settings=settings)
storage = CandidateStorage.from_settings(settings)
```

**Pipeline result + DB verification pattern** ([tests/integration/test_market_scan.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_market_scan.py:30)):
```python
result = scanner.run_scan(..., storage=storage)

assert result.scan_run_id is not None
assert result.counts == {"accepted": 1, "review": 1, "rejected": 1}

with storage.connect() as connection:
    run_row = connection.execute(...).fetchone()
    candidate_rows = connection.execute(...).fetchall()
```

**Use for Phase 2:** drive the whole candidate-to-NOAA-to-edge-to-storage flow in one test, then verify both in-memory result counts and persisted evaluation evidence.

## Shared Patterns

### Typed runtime settings
**Source:** [config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:10)
**Apply to:** `config/settings.py`, `config/weather_locations.py`, `strategies/weather/signal_engine.py`, `core/storage.py`
```python
@dataclass(frozen=True)
class ScanSettings:
    ...

def load_settings(...) -> ScanSettings:
    raw_env = dict(os.environ if environ is None else environ)
    if overrides:
        raw_env.update(overrides)
```

### Frozen domain models
**Source:** [core/models.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/models.py:25), [strategies/weather/types.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/types.py:11)
**Apply to:** `core/models.py`, `strategies/weather/types.py`, `strategies/weather/noaa_client.py`
```python
@dataclass(frozen=True)
class CandidateRecord:
    ...

@dataclass(frozen=True)
class WeatherMarketCandidate:
    ...
```

### Storage lifecycle
**Source:** [core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:52)
**Apply to:** `core/storage.py`, `tests/integration/test_signal_storage.py`, `tests/integration/test_noaa_signal_engine.py`
```python
def bootstrap(self) -> None: ...
def persist_scan_result(self, source: str, candidates: Iterable[CandidateRecord]) -> int: ...
```

### Service orchestration via dependency injection
**Source:** [core/market_scanner.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/market_scanner.py:52)
**Apply to:** `strategies/weather/signal_engine.py`, `tests/integration/test_noaa_signal_engine.py`
```python
class MarketScanner:
    def __init__(self, client: PolymarketDiscoveryClient | None = None, settings: ScanSettings | None = None) -> None:
        self.client = client or PolymarketDiscoveryClient()
        self.settings = settings or get_settings()
```

### Validation and error signaling
**Source:** [core/clob_client.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/clob_client.py:38)
**Apply to:** `strategies/weather/noaa_client.py`, `strategies/weather/edge_calculator.py`
```python
class PolymarketPayloadError(ValueError):
    ...

if missing:
    raise PolymarketPayloadError(...)
```

### Test posture
**Source:** [tests/unit/test_weather_normalization.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_weather_normalization.py:8), [tests/integration/test_market_scan.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_market_scan.py:19)
**Apply to:** all new Phase 2 tests
```python
def test_...() -> None:
    ...
    assert ...
```

### Missing shared pattern
There is no existing auth/guard pattern in this repo, and there is no centralized exception wrapper or logger middleware to copy for HTTP/network failures. For Phase 2, stay consistent with the current codebase: use explicit domain-specific `ValueError` subclasses and deterministic rejection codes rather than introducing a new global error framework.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| None | — | — | Every planned Phase 2 file has at least a role-match analog in the current repo. |

## Metadata

**Analog search scope:** `config/`, `core/`, `strategies/weather/`, `tests/unit/`, `tests/integration/`
**Files scanned:** 12 primary files, plus phase context in `02-CONTEXT.md` and `02-RESEARCH.md`
**Pattern extraction date:** 2026-04-18
