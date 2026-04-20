# Phase 04: Paper Trading Runtime - Pattern Map

**Mapped:** 2026-04-19
**Files analyzed:** 11
**Analogs found:** 11 / 11

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `config/settings.py` | config | request-response | `config/settings.py` | exact |
| `core/models.py` | model | transform | `core/models.py` | exact |
| `core/storage.py` | service | CRUD | `core/storage.py` | exact |
| `core/trade_logger.py` | service | append-only events | `core/storage.py` | role+flow |
| `core/paper_execution.py` | service | transform | `core/risk_manager.py` | role+flow |
| `core/performance.py` | service | transform | `core/kelly_engine.py` | role+flow |
| `paper_trader.py` | entrypoint | orchestration | `main.py` | exact |
| `tests/unit/test_paper_execution.py` | test | transform | `tests/unit/test_risk_manager.py` | role+flow |
| `tests/unit/test_performance_metrics.py` | test | transform | `tests/unit/test_kelly_engine.py` | role+flow |
| `tests/integration/test_paper_storage.py` | test | CRUD | `tests/integration/test_risk_storage.py` | exact |
| `tests/integration/test_paper_runtime.py` | test | orchestration | `tests/integration/test_signal_risk_gate.py` | role+flow |

## Pattern Assignments

### `config/settings.py` (config, request-response)

**Analog:** `config/settings.py`

**Frozen dataclass + env loader pattern** ([config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:1)):
```python
@dataclass(frozen=True)
class ScanSettings:
    ...

def load_settings(
    overrides: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> ScanSettings:
```

**Use for Phase 4:** add paper-runtime settings such as a paper bankroll default, runtime interval, and resolution polling interval here rather than introducing module-level constants in `paper_trader.py`.

---

### `core/models.py` (model, transform)

**Analog:** `core/models.py`

**Enum + immutable record pattern** ([core/models.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/models.py:9)):
```python
class RiskDecisionStatus(StrEnum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"

@dataclass(frozen=True)
class RiskDecisionRecord:
    ...
```

**Use for Phase 4:** introduce paper-trade state enums and immutable records for positions, lifecycle events, bankroll snapshots, and performance summaries in the same vocabulary-first style.

---

### `core/storage.py` (service, CRUD)

**Analog:** `core/storage.py`

**Repository + bootstrap schema pattern** ([core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:40)):
```python
class CandidateStorage:
    def connect(self) -> sqlite3.Connection:
        ...

    def bootstrap(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS ...
                """
            )
```

**Append-only insert/list pattern** ([core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:279)):
```python
def persist_risk_decisions(self, source: str, decisions: Iterable[RiskDecisionRecord]) -> int:
    ...

def list_risk_decisions(self, market_id: str | None = None) -> list[RiskDecisionRecord]:
    ...
```

**Use for Phase 4:** extend the same repository with dedicated tables and methods for paper positions, paper lifecycle events, and bankroll snapshots instead of inventing a parallel storage class.

---

### `core/trade_logger.py` (service, append-only events)

**Analog:** `core/storage.py`

**Current boundary placeholder** ([core/trade_logger.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/trade_logger.py:1)):
```python
@dataclass(frozen=True)
class TradeLogEntry:
    event_type: str = "placeholder"
    message: str = "trade logger not implemented yet"
```

**Use for Phase 4:** keep this module as a thin event-shaping boundary that emits typed lifecycle entries or delegates storage writes, rather than turning it into an unrelated logging framework.

---

### `core/paper_execution.py` (service, transform)

**Analog:** `core/risk_manager.py`

**Pure domain logic over immutable inputs pattern** ([core/risk_manager.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/risk_manager.py:18)):
```python
class RiskManager:
    def evaluate_risk_for_signal(... ) -> RiskDecisionRecord:
        ...
```

**Use for Phase 4:** keep entry and settlement math in a dedicated backend module that consumes immutable records and returns immutable paper-trade or settlement records. Do not bury this logic inside the CLI loop.

---

### `core/performance.py` (service, transform)

**Analog:** `core/kelly_engine.py`

**Deterministic calculation helper pattern** ([core/kelly_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/kelly_engine.py:1)):
```python
@dataclass(frozen=True)
class KellySizingDecision:
    ...

class KellyEngine:
    def calculate_position_size(...) -> KellySizingDecision:
        ...
```

**Use for Phase 4:** compute cumulative return, drawdown, and recovery metrics in one deterministic metrics module with pure inputs and outputs so unit tests can pin exact numbers.

---

### `paper_trader.py` (entrypoint, orchestration)

**Analog:** `main.py`

**Thin parser/main pattern** ([main.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/main.py:14)):
```python
def build_parser() -> argparse.ArgumentParser:
    ...

def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
```

**Use for Phase 4:** preserve this CLI structure and add dedicated `paper-once` / `paper-loop` style commands or equivalent flags rather than placing business logic directly in `if __name__ == "__main__"` blocks.

---

### `tests/unit/test_paper_execution.py` (test, transform)

**Analog:** `tests/unit/test_risk_manager.py`

**Direct record-construction assertion style** ([tests/unit/test_risk_manager.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_risk_manager.py:1)):
```python
def test_...() -> None:
    settings = ScanSettings(...)
    ...
    assert result.allowed_stake_usd == ...
```

**Use for Phase 4:** build deterministic unit tests that construct explicit allowed decisions, paper positions, and resolution outcomes, then assert exact lifecycle and bankroll values.

---

### `tests/unit/test_performance_metrics.py` (test, transform)

**Analog:** `tests/unit/test_kelly_engine.py`

**Pure-calculation test style** ([tests/unit/test_kelly_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/unit/test_kelly_engine.py:1)):
```python
def test_...() -> None:
    decision = engine.calculate_position_size(...)
    assert decision.proposed_stake_usd == ...
```

**Use for Phase 4:** keep metrics tests numeric and explicit, asserting exact cumulative return, drawdown percentages, and recovery markers from small ledger fixtures.

---

### `tests/integration/test_paper_storage.py` (test, CRUD)

**Analog:** `tests/integration/test_risk_storage.py`

**Real SQLite round-trip pattern** ([tests/integration/test_risk_storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_risk_storage.py:1)):
```python
storage = CandidateStorage(temp_sqlite_db_path)
inserted = storage.persist_...( ... )
with storage.connect() as connection:
    rows = connection.execute(...).fetchall()
```

**Use for Phase 4:** verify tables exist, direct SQL values match expected lifecycle state, and repository listing methods round-trip paper trades and bankroll snapshots correctly.

---

### `tests/integration/test_paper_runtime.py` (test, orchestration)

**Analog:** `tests/integration/test_signal_risk_gate.py`

**Real storage + thin orchestration integration style** ([tests/integration/test_signal_risk_gate.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests/integration/test_signal_risk_gate.py:1)):
```python
storage = CandidateStorage.from_settings(settings)
engine = SignalEngine(storage=storage, settings=settings)
...
result = engine.evaluate_risk_for_signal(...)
```

**Use for Phase 4:** exercise the once-mode paper runtime over real storage and stubbed external dependencies, asserting that the flow enters, persists, settles, and reports without touching any live-order path.

---

## Reuse Guidance

- Extend `CandidateStorage`; do not create a second SQLite repository abstraction for paper trading.
- Keep new domain records in `core/models.py` and calculation logic in new `core/` modules, not in scripts.
- Preserve thin entrypoints and deterministic tests with explicit numeric assertions.
- Favor append-only rows plus list/query helpers over mutable “latest only” state.
