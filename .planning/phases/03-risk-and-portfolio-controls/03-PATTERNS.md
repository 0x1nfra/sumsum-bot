# Phase 03: Risk and Portfolio Controls - Pattern Map

**Mapped:** 2026-04-19
**Files analyzed:** 10
**Analogs found:** 10 / 10

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `config/settings.py` | config | request-response | `config/settings.py` | exact |
| `config/kill_switches.py` | config | transform | `config/settings.py` | role-match |
| `core/models.py` | model | transform | `core/models.py` | exact |
| `core/kelly_engine.py` | service | transform | `strategies/weather/edge_calculator.py` | role+flow |
| `core/risk_manager.py` | service | transform | `strategies/weather/signal_engine.py` | role+flow |
| `core/storage.py` | service | CRUD | `core/storage.py` | exact |
| `tests/unit/test_kelly_engine.py` | test | transform | `tests/unit/test_weather_edge_calculator.py` | role+flow |
| `tests/unit/test_risk_manager.py` | test | transform | `tests/integration/test_noaa_signal_engine.py` | role+flow |
| `tests/integration/test_risk_storage.py` | test | CRUD | `tests/integration/test_signal_storage.py` | role+flow |
| `tests/integration/test_signal_risk_gate.py` | test | transform | `tests/integration/test_noaa_signal_engine.py` | role+flow |

## Pattern Assignments

### `config/settings.py` (config, request-response)

**Analog:** [config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:1)

Use the same frozen-dataclass plus `load_settings()` override pattern already established for scanner and NOAA fields. Risk thresholds should become typed fields on `ScanSettings`, not loose module constants or ad hoc dictionaries.

### `config/kill_switches.py` (config, transform)

**Analog:** [config/kill_switches.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/kill_switches.py:1)

Keep this file as deterministic config only. It should expose small immutable settings or helper constructors, not storage reads, runtime clocks, or policy orchestration.

### `core/models.py` (model, transform)

**Analog:** [core/models.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/models.py:1)

Follow the enum-plus-frozen-dataclass vocabulary pattern. Risk-facing records such as `PortfolioSnapshot`, `RiskDecisionStatus`, and append-only `RiskDecisionRecord` should live here if they are shared across storage and orchestration.

### `core/kelly_engine.py` (service, transform)

**Analog:** [strategies/weather/edge_calculator.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/edge_calculator.py:1)

Use the same style as the edge calculator: one small public class with deterministic helper methods, explicit evidence fields, and no I/O. The Kelly engine should compute a result object, not mutate portfolio state directly.

### `core/risk_manager.py` (service, transform)

**Analog:** [strategies/weather/signal_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/signal_engine.py:1)

Use dependency injection plus thin orchestration. `RiskManager` should coordinate `KellySizingDecision`, portfolio state, kill-switch checks, and a resulting `RiskDecisionRecord`, just as `SignalEngine` coordinates NOAA, edge calculation, and storage-facing records.

### `core/storage.py` (service, CRUD)

**Analog:** [core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:1)

Retain the `bootstrap -> persist_* -> list_* -> private insert helpers` structure. Risk persistence should be a new append-only table and API, not an overload of `signal_evaluations` or candidate buckets.

### `tests/unit/test_kelly_engine.py` (test, transform)

**Analog:** [tests/unit/test_weather_edge_calculator.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_weather_edge_calculator.py:1)

Copy the existing unit-test style for pure deterministic logic: direct object construction, explicit numeric assertions, and one behavior per test.

### `tests/unit/test_risk_manager.py` (test, transform)

**Analog:** [tests/integration/test_noaa_signal_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_noaa_signal_engine.py:1)

Use small stubs or handcrafted records to drive the risk path and assert exact reason codes, stake values, and evidence fields. Avoid depending on real NOAA or scanner behavior in this suite.

### `tests/integration/test_risk_storage.py` (test, CRUD)

**Analog:** [tests/integration/test_signal_storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_signal_storage.py:1)

Follow the append-only storage test pattern: insert multiple records, query rows directly, then assert the repository round-trips statuses and evidence.

### `tests/integration/test_signal_risk_gate.py` (test, transform)

**Analog:** [tests/integration/test_noaa_signal_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_noaa_signal_engine.py:1)

Reuse the “stub dependency + real storage + real orchestrator” pattern. The integration test should construct accepted Phase 2 signal records, pass them through the risk manager with a controlled portfolio snapshot, and assert persisted approved or blocked decisions.

## Concrete Excerpts To Reuse

### Frozen settings loader
```python
@dataclass(frozen=True)
class ScanSettings:
    ...

def load_settings(
    overrides: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> ScanSettings:
    ...
```

### Append-only storage boundary
```python
def persist_signal_evaluations(
    self,
    source: str,
    evaluations: Iterable[SignalEvaluationRecord],
) -> int:
    ...
```

### Thin orchestrator with injected dependencies
```python
class SignalEngine:
    def __init__(
        self,
        noaa_client: NoaaForecastClient | None = None,
        edge_calculator: WeatherEdgeCalculator | None = None,
        storage: CandidateStorage | None = None,
        settings: ScanSettings | None = None,
    ) -> None:
        ...
```

## Pattern Notes For Phase 3

- Keep risk math deterministic and side-effect free until the storage boundary.
- Prefer first-class dataclasses for snapshots and decisions over free-form dictionaries.
- Preserve the repo’s explicit reason-code style. Do not invent opaque booleans where a code and evidence payload are required.
- Follow the existing append-only persistence posture from Phase 2 so later dashboard and paper-runtime work can reuse the same audit trail.

---
*Phase: 03-risk-and-portfolio-controls*
*Pattern map generated: 2026-04-19*
