# Phase 4: Paper Trading Runtime - Research

**Researched:** 2026-04-19 [VERIFIED: local env]
**Domain:** Python paper-trading runtime for weather-market simulation, settlement polling, and forward-test performance accounting [VERIFIED: codebase grep][VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md]
**Confidence:** MEDIUM [VERIFIED: codebase grep][CITED: https://docs.python.org/3/library/sqlite3.html][CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id]

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Paper entry behavior
- **D-01:** When a weather signal clears risk, the paper trader should enter immediately at the current market `no_price`.
- **D-02:** Phase 4 should not add delayed entry confirmation, simulated order-book waiting, or slippage penalties as a prerequisite for paper fills.

### Lifecycle scope
- **D-03:** Paper trades must move through explicit entry, open, and resolution states with bankroll updates at the appropriate lifecycle transitions.
- **D-04:** Phase 4 must stay fully paper-only. No live-order execution path, credentials, or promotion-to-live behavior belongs in this phase.

### Carried-forward runtime constraints
- **D-05:** Only accepted NOAA-backed weather signals that also pass Phase 3 risk gating may create paper positions.
- **D-06:** The fail-closed posture from Phases 2 and 3 remains locked: missing NOAA support, rejected signals, or blocked risk decisions must never become open paper trades.
- **D-07:** Weather-only scope remains locked for the runtime. BTC, sports, and multi-strategy orchestration stay out of scope.

### Performance measurement
- **D-08:** Phase 4 must produce enough stored runtime data to measure bankroll change, cumulative return, and drawdown-recovery behavior across the forward-test window.
- **D-09:** The runtime data model should support later dashboard and logging work in Phase 5 without forcing Phase 4 to implement the dashboard itself.

### the agent's Discretion
- Resolution mechanics, with a strong preference for a Polymarket-first and fail-closed settlement path unless planning finds a concrete reason a fallback is required.
- Runtime orchestration shape: one loop, split passes, or a lightweight scheduler may be chosen during planning based on the simplest reliable fit with the current codebase.
- Performance-ledger granularity: planner may choose the lightest data model that still supports bankroll, return, and drawdown-recovery analysis plus Phase 5 reporting needs.
- Exact paper-position schema and transition implementation, provided lifecycle states and bankroll effects remain inspectable.

### Deferred Ideas (OUT OF SCOPE)
- Dashboard presentation, operator-facing metrics views, and broader audit-log UX are deferred to Phase 5.
- Docker/VPS process management and restart behavior are deferred to Phase 6.
- Any live-order execution path is deferred until paper-trading validation succeeds.
- More realistic fill simulation such as slippage, queueing, or delayed execution is deferred beyond Phase 4 unless planning finds it is strictly necessary.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PAPR-01 | Operator can run the bot in paper-trading mode without sending live orders. [VERIFIED: .planning/REQUIREMENTS.md] | Use a dedicated `paper_trader.py` runtime path that consumes stored risk decisions and never imports or calls any authenticated trading client. [VERIFIED: codebase grep][ASSUMED] |
| PAPR-02 | Operator can simulate order entry, open-position tracking, and market resolution for weather trades. [VERIFIED: .planning/REQUIREMENTS.md] | Add explicit paper-position states plus append-only lifecycle events and poll Polymarket market status fields for settlement. [VERIFIED: codebase grep][CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED] |
| PAPR-03 | Operator can measure bankroll change, PnL percentage, and recovery from drawdown over a 2-week forward test. [VERIFIED: .planning/REQUIREMENTS.md] | Record bankroll snapshots and resolved trade outcomes in SQLite so cumulative return and drawdown/recovery can be derived without mutating hidden state. [VERIFIED: codebase grep][CITED: https://docs.python.org/3/library/sqlite3.html][ASSUMED] |
</phase_requirements>

## Summary

The repo already has the critical upstream handoff Phase 4 needs: approved weather candidates are normalized into `CandidateRecord`, NOAA-backed signal evaluations are appended into `signal_evaluations`, and risk-approved stakes are appended into `risk_decisions`. [VERIFIED: [strategies/weather/signal_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/signal_engine.py:1)][VERIFIED: [core/models.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/models.py:1)][VERIFIED: [core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:1)] Phase 4 should extend those boundaries rather than build a parallel runtime stack. [VERIFIED: codebase grep]

The simplest reliable architecture is a single-process, paper-only loop that performs three passes in order: evaluate new approved candidates through the existing signal and risk pipeline, open new paper positions for allowed risk decisions that have not already been consumed, and poll open markets for resolution before booking final bankroll impact. [VERIFIED: [main.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/main.py:1)][VERIFIED: [paper_trader.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/paper_trader.py:1)][CITED: https://docs.python.org/3.11/library/sched.html][CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED] This stays aligned with the current thin-entrypoint pattern, typed settings, and SQLite-first storage posture. [VERIFIED: [config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:1)][VERIFIED: [pyproject.toml](/Users/irfanmurad/Developer/vessl/sumsum-bot/pyproject.toml:1)]

The main planning risk is settlement semantics, not entry logic. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][CITED: https://help.polymarket.com/en/articles/13364518-how-are-prediction-markets-resolved][ASSUMED] Polymarket’s official docs expose `closed`, `closedTime`, `resolvedBy`, `umaResolutionStatus`, and outcome pricing fields, and the help docs say markets pay $1 to winning shares only after resolution is finalized. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][CITED: https://help.polymarket.com/en/articles/13364518-how-are-prediction-markets-resolved] Plan for a fail-closed resolver that leaves positions open or flags them for review when the market API fields do not unambiguously indicate a final outcome. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]

**Primary recommendation:** Build Phase 4 as a standard-library, single-process paper runtime that extends `core/models.py`, `core/storage.py`, and `paper_trader.py` with an idempotent position state machine, append-only lifecycle/ledger rows, and Polymarket-first fail-closed settlement polling. [VERIFIED: codebase grep][CITED: https://docs.python.org/3/library/sqlite3.html][CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Continuous paper-trading loop | API / Backend | Database / Storage | The repo is a local Python runtime with CLI entrypoints and no browser tier, so orchestration belongs in the Python process and persists its state to SQLite. [VERIFIED: codebase grep] |
| Risk-approved signal consumption | API / Backend | Database / Storage | Existing risk decisions are produced in Python and stored in `risk_decisions`; Phase 4 should consume those records rather than move approval logic elsewhere. [VERIFIED: [strategies/weather/signal_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/signal_engine.py:84)][VERIFIED: [core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:242)] |
| Paper trade lifecycle state | Database / Storage | API / Backend | Entry/open/resolution state must survive restarts and support later observability, so the source of truth should be persisted rows with Python services enforcing transitions. [VERIFIED: codebase grep][ASSUMED] |
| Market settlement lookup | API / Backend | External dependency | Polling Polymarket market metadata is an outbound API concern owned by the runtime process. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id] |
| Bankroll and drawdown analytics | Database / Storage | API / Backend | Durable snapshots and resolved trade rows should live in SQLite, with reporting calculations derived in Python. [VERIFIED: codebase grep][CITED: https://docs.python.org/3/library/sqlite3.html][ASSUMED] |
| Operator CLI | API / Backend | — | The current operator interface is `argparse`-based command execution in `main.py` and `paper_trader.py`. [VERIFIED: [main.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/main.py:1)][VERIFIED: [paper_trader.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/paper_trader.py:1)] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library [VERIFIED: codebase grep] | `>=3.11` required, `3.13.3` local [VERIFIED: [pyproject.toml](/Users/irfanmurad/Developer/vessl/sumsum-bot/pyproject.toml:1)][VERIFIED: local env] | `argparse`, `dataclasses`, `datetime`, `enum`, `json`, `time`, `urllib`, and `sqlite3` cover the current runtime shape. [VERIFIED: codebase grep] | The repo already implements Phase 1-3 entirely with stdlib modules, so continuing that pattern avoids dependency churn for a still-simple single-process runtime. [VERIFIED: codebase grep] |
| `sqlite3` / SQLite runtime [CITED: https://docs.python.org/3/library/sqlite3.html] | SQLite `3.49.2` via Python runtime, CLI binary `3.43.2` on PATH [VERIFIED: local env] | Durable append-only lifecycle rows, bankroll snapshots, and trade-resolution data. [VERIFIED: codebase grep][ASSUMED] | Python’s built-in `sqlite3` is explicitly suitable for lightweight on-disk storage and prototyping before porting to PostgreSQL. [CITED: https://docs.python.org/3/library/sqlite3.html] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `logging` stdlib [CITED: https://docs.python.org/3.11/library/logging.html] | bundled with Python `3.11+` [VERIFIED: [pyproject.toml](/Users/irfanmurad/Developer/vessl/sumsum-bot/pyproject.toml:1)] | Structured runtime logs with contextual fields per market/trade loop. [CITED: https://docs.python.org/3.11/library/logging.html][ASSUMED] | Use now for runtime health and lifecycle events behind `core/trade_logger.py`. [VERIFIED: [core/trade_logger.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/trade_logger.py:1)][ASSUMED] |
| `pytest` [VERIFIED: local env] | repo pin `>=8,<9`, installed `8.4.2`, latest `9.0.3` on PyPI [VERIFIED: [pyproject.toml](/Users/irfanmurad/Developer/vessl/sumsum-bot/pyproject.toml:14)][VERIFIED: local env] | Unit and integration coverage for runtime lifecycle, settlement, and performance math. [VERIFIED: codebase grep] | Use `uv run pytest` because `pytest` is not directly on PATH in this environment. [VERIFIED: local env] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Existing single-process monotonic loop [VERIFIED: [main.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/main.py:77)] | APScheduler `3.11.2` [VERIFIED: local env] | APScheduler is mature, but it adds a new dependency and job-store concepts the current runtime does not need for one weather loop. [VERIFIED: local env][ASSUMED] |
| Existing `urllib` HTTP pattern [VERIFIED: [strategies/weather/noaa_client.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/noaa_client.py:1)] | `requests 2.33.1` or `httpx 0.28.1` [VERIFIED: local env] | Third-party HTTP clients improve ergonomics, but reusing stdlib `urllib` keeps Phase 4 aligned with the existing NOAA client unless multiple providers or retries/backoff become painful. [VERIFIED: codebase grep][ASSUMED] |
| Default SQLite journal mode [CITED: https://sqlite.org/wal.html] | WAL mode [CITED: https://sqlite.org/wal.html] | WAL improves concurrent reads but adds checkpointing concerns and a recent documented WAL corruption bug exists for some multi-connection versions; Phase 4’s single-process workload does not require that complexity. [CITED: https://sqlite.org/wal.html][ASSUMED] |

**Installation:** [VERIFIED: [pyproject.toml](/Users/irfanmurad/Developer/vessl/sumsum-bot/pyproject.toml:1)]
```bash
uv sync --extra dev
```

**Version verification:** [VERIFIED: local env]
```bash
python3 -m pip index versions pytest
python3 - <<'PY'
import sqlite3, sys
print(sys.version.split()[0])
print(sqlite3.sqlite_version)
PY
```

## Architecture Patterns

### System Architecture Diagram
```text
approved candidates
    |
    v
SignalEngine.evaluate_candidates()
    |
    v
signal_evaluations (append-only)
    |
    v
SignalEngine.evaluate_risk_for_signal()
    |
    +--> blocked risk_decisions -> remain audit-only
    |
    v
allowed risk_decisions
    |
    v
Paper runtime entry pass
    |
    +--> idempotency check against existing paper positions
    |
    v
paper_trade_events / paper_positions
    |
    v
open-position resolver pass
    |
    +--> GET /markets/{id} on Gamma API
    |       |
    |       +--> ambiguous / not closed -> keep open
    |       |
    |       +--> resolved -> compute payout
    |
    v
resolved trade event + bankroll snapshot
    |
    v
forward-test metrics (return, drawdown, recovery)
```

### Recommended Project Structure
```text
core/
├── models.py                # Extend with paper-trade states, lifecycle events, bankroll snapshots
├── storage.py               # New SQLite tables and repository methods for paper runtime
├── trade_logger.py          # Runtime/logging boundary for structured lifecycle events
└── paper_runtime.py         # Service layer for entry/open/resolve orchestration
config/
└── settings.py              # Paper-loop interval, bankroll seed, settlement poll interval
paper_trader.py              # Thin CLI entrypoint for once/loop paper runtime modes
tests/
├── integration/
│   ├── test_paper_runtime.py
│   └── test_paper_performance.py
└── unit/
    ├── test_paper_settlement.py
    └── test_paper_metrics.py
```

### Pattern 1: Idempotent Risk-Decision Consumption
**What:** Open a paper position from an allowed `risk_decisions` row exactly once, and persist the linkage back to `signal_evaluation_id` and `risk_decision_id`. [VERIFIED: codebase grep][ASSUMED]
**When to use:** Every loop pass that transforms allowed risk decisions into simulated positions. [ASSUMED]
**Example:**
```typescript
// Source: repository pattern + sqlite3 placeholders
// https://docs.python.org/3/library/sqlite3.html
// inference: add a uniqueness constraint on consumed decisions
connection.execute(
    """
    INSERT INTO paper_positions (
        risk_decision_id, signal_evaluation_id, market_id, state, entry_no_price, stake_usd
    ) VALUES (?, ?, ?, ?, ?, ?)
    """,
    (risk_decision_id, signal_evaluation_id, market_id, "open", entry_no_price, stake_usd),
)
```

### Pattern 2: Append-Only Lifecycle Ledger
**What:** Record entry, resolution, and bankroll snapshots as immutable events, then derive current position state and performance metrics from those rows. [VERIFIED: codebase grep][ASSUMED]
**When to use:** For every bankroll-changing action and every trade transition. [ASSUMED]
**Example:**
```typescript
// Source: sqlite3 parameter binding guidance
// https://docs.python.org/3/library/sqlite3.html
cur.execute(
    "INSERT INTO bankroll_snapshots(event_type, bankroll_usd, peak_bankroll_usd, drawdown_pct) VALUES(?, ?, ?, ?)",
    ("trade_resolved", bankroll_usd, peak_bankroll_usd, drawdown_pct),
)
```

### Pattern 3: Monotonic Split-Pass Loop
**What:** Run a single loop with explicit phases: scan/evaluate, open eligible paper positions, resolve open positions, emit summary. [VERIFIED: [main.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/main.py:77)][CITED: https://docs.python.org/3.11/library/sched.html][ASSUMED]
**When to use:** Continuous runtime mode where simple predictable ordering matters more than parallel throughput. [ASSUMED]
**Example:**
```typescript
// Source: Python sched docs use monotonic time by default
// https://docs.python.org/3.11/library/sched.html
next_tick = time.monotonic()
while True:
    run_signal_and_risk_pass()
    run_entry_pass()
    run_resolution_pass()
    next_tick += interval_seconds
    time.sleep(max(0.0, next_tick - time.monotonic()))
```

### Anti-Patterns to Avoid
- **Recomputing risk during entry:** Risk approval is already authoritative in Phase 3; entry should consume stored allowed decisions instead of silently re-running gating with drifted bankroll inputs. [VERIFIED: [strategies/weather/signal_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/signal_engine.py:84)][ASSUMED]
- **Mutable singleton bankroll record:** A single overwrite-only `current_balance` row makes drawdown and recovery auditing brittle; use append-only snapshots or trade events. [VERIFIED: codebase grep][ASSUMED]
- **Settling from title parsing or end time alone:** Polymarket exposes market closure and resolution metadata directly; do not infer winners from market text after entry. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]
- **Adding async or multi-worker concurrency early:** SQLite allows only one writer at a time per database connection set, and the current repo is designed around synchronous single-process flows. [CITED: https://docs.python.org/3/library/sqlite3.html][VERIFIED: codebase grep]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Market resolution source | Outcome inference from title text or local heuristics [ASSUMED] | Polymarket market-detail polling via `/markets/{id}` with fail-closed handling when fields are ambiguous. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED] | Official market payloads already expose closure and resolution-related fields. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id] |
| SQL input handling | Interpolated SQL strings [CITED: https://docs.python.org/3/library/sqlite3.html] | Placeholder-bound `execute()` and `executemany()` calls. [CITED: https://docs.python.org/3/library/sqlite3.html] | Python’s sqlite docs explicitly recommend placeholders to avoid SQL injection and binding errors. [CITED: https://docs.python.org/3/library/sqlite3.html] |
| Trade consumption dedupe | In-memory `set()` only [ASSUMED] | Database-backed idempotency using consumed-decision linkage and unique constraints. [ASSUMED] | The runtime must survive restarts and repeated loops without duplicating fills. [ASSUMED] |
| Performance reporting | Only a mutable balance field [ASSUMED] | Append-only bankroll snapshots and resolved trade rows with derived metrics queries. [ASSUMED] | Drawdown recovery requires historical path data, not just latest state. [ASSUMED] |

**Key insight:** Phase 4 is mostly a durable-state problem, not a pricing problem; the hard part is preserving an auditable path from approved risk decision to resolved paper result without duplicates or hidden bankroll mutations. [VERIFIED: codebase grep][ASSUMED]

## Common Pitfalls

### Pitfall 1: Duplicate paper fills on repeated scans
**What goes wrong:** The same allowed risk decision opens multiple paper positions across loop iterations. [ASSUMED]
**Why it happens:** Phase 3 appends `risk_decisions`; without a consumed-decision marker or unique key, a later loop cannot distinguish new vs already-opened approvals. [VERIFIED: [core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:242)][ASSUMED]
**How to avoid:** Persist a one-time linkage from risk decision to paper position and enforce it with a DB constraint. [ASSUMED]
**Warning signs:** Open-position count rises while unique accepted-signal count does not. [ASSUMED]

### Pitfall 2: Settling too early
**What goes wrong:** A trade is marked resolved from end time alone even though UMA resolution is not finalized. [CITED: https://help.polymarket.com/en/articles/13364518-how-are-prediction-markets-resolved][ASSUMED]
**Why it happens:** Market end and market resolution are different events. [CITED: https://help.polymarket.com/en/articles/13364518-how-are-prediction-markets-resolved]
**How to avoid:** Poll official market fields and keep the position open or review-only until resolution is unambiguous. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]
**Warning signs:** Closed markets with missing/unclear resolution metadata or payout implied before official closure fields change. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]

### Pitfall 3: Bankroll drift from inconsistent lifecycle accounting
**What goes wrong:** Current bankroll differs from the sum of seed bankroll plus resolved trade payouts and reserved/open stakes. [ASSUMED]
**Why it happens:** Entry, resolution, and open exposure updates are handled in different places without a ledger. [ASSUMED]
**How to avoid:** Make every bankroll-affecting transition append a lifecycle event and optionally a snapshot row. [ASSUMED]
**Warning signs:** Recomputing bankroll from resolved trades does not match the stored current bankroll. [ASSUMED]

### Pitfall 4: Loop timing drift
**What goes wrong:** A nominal 5-minute loop gradually drifts or bunches calls after long iterations. [ASSUMED]
**Why it happens:** Naive `sleep(interval)` scheduling ignores work time. [ASSUMED]
**How to avoid:** Schedule against `time.monotonic()` and calculate next wake time from the prior target tick. [CITED: https://docs.python.org/3.11/library/sched.html][ASSUMED]
**Warning signs:** Logged iteration timestamps slowly slide later than the configured cadence. [ASSUMED]

## Code Examples

Verified patterns from official sources:

### SQLite placeholder binding
```typescript
// Source: https://docs.python.org/3/library/sqlite3.html
con.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
con.commit()
```

### Monotonic scheduler baseline
```typescript
// Source: https://docs.python.org/3.11/library/sched.html
import sched
import time

scheduler = sched.scheduler(time.monotonic, time.sleep)
```

### Contextual logging boundary
```typescript
// Source: https://docs.python.org/3.11/library/logging.html
import logging

logger = logging.getLogger("paper-runtime")
trade_logger = logging.LoggerAdapter(logger, {"market_id": market_id, "paper_position_id": position_id})
trade_logger.info("trade_resolved")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `sqlite3` transaction control primarily via `isolation_level` [CITED: https://docs.python.org/3/library/sqlite3.html] | `autocommit` parameter and attribute now exist, but legacy transaction control remains the default today. [CITED: https://docs.python.org/3/library/sqlite3.html] | Python `3.12` added `autocommit`. [CITED: https://docs.python.org/3/library/sqlite3.html] | Phase 4 should keep explicit commit boundaries and not rely on future default changes. [CITED: https://docs.python.org/3/library/sqlite3.html][ASSUMED] |

**Deprecated/outdated:**
- Relying on the future default transaction behavior of `sqlite3.connect()` is unsafe because the docs state the default will change in a future Python release. [CITED: https://docs.python.org/3/library/sqlite3.html]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `closed` + related market-resolution fields from Gamma can be combined into a reliable final-settlement rule for weather markets. [ASSUMED] | Summary, Pattern 2, Pitfall 2 | Wrong settlement logic would distort PnL and leave positions incorrectly resolved. |
| A2 | A single-process monotonic loop is sufficient for Phase 4 workload and avoids scheduler complexity. [ASSUMED] | Summary, Standard Stack, Pattern 3 | If throughput or blocking becomes a problem, the planner may need a more explicit job runner. |
| A3 | A lightweight append-only bankroll snapshot table is enough to satisfy Phase 5 reporting needs without a fuller double-entry ledger. [ASSUMED] | Summary, Requirements, Pitfall 3 | Phase 5 could need a schema extension or migration. |
| A4 | A DB uniqueness rule keyed to consumed risk decisions or signal evaluations is the right idempotency boundary. [ASSUMED] | Pattern 1, Don't Hand-Roll, Pitfall 1 | Duplicate trades could still slip through if the wrong uniqueness key is chosen. |

## Open Questions

1. **Which exact Polymarket field combination should mark a trade as finally settled?**
   - What we know: Official docs expose `closed`, `closedTime`, `resolvedBy`, `umaResolutionStatus`, `outcomePrices`, and related fields. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id]
   - What's unclear: The docs enumerate fields but do not define a canonical terminal-state truth table for paper accounting. [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]
   - Recommendation: Plan an explicit resolver matrix and cover it with fixture-based tests before implementation is considered complete. [ASSUMED]

2. **Should the performance ledger store snapshots only on bankroll-changing events or on every loop tick?**
   - What we know: PAPR-03 requires bankroll change, PnL percentage, and drawdown-recovery analysis over a 2-week window. [VERIFIED: .planning/REQUIREMENTS.md]
   - What's unclear: Phase 5 dashboard needs may prefer denser time-series points even when bankroll is unchanged. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md][ASSUMED]
   - Recommendation: Default to event-driven snapshots plus optional periodic heartbeat snapshots only if Phase 5 reporting clearly needs them. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime execution | ✓ [VERIFIED: local env] | `3.13.3` [VERIFIED: local env] | — |
| `uv` | Dependency sync and test execution | ✓ [VERIFIED: local env] | `0.9.29` [VERIFIED: local env] | `python3 -m pip` for installs only, but `uv` is preferred. [ASSUMED] |
| SQLite runtime via Python | Durable local persistence | ✓ [VERIFIED: local env] | `3.49.2` [VERIFIED: local env] | CLI binary exists too, but runtime persistence should use Python’s bundled library. [VERIFIED: local env][ASSUMED] |
| `sqlite3` CLI | Manual inspection only | ✓ [VERIFIED: local env] | `3.43.2` [VERIFIED: local env] | Use Python one-liners for DB inspection. [ASSUMED] |
| `pytest` on PATH | Validation command | ✗ [VERIFIED: local env] | — | `uv run pytest` [VERIFIED: local env] |
| NOAA HTTPS | Forecast reads in existing signal engine | ✓ [VERIFIED: local env] | HTTP 200 probe on 2026-04-19 [VERIFIED: local env] | None |
| Polymarket Gamma HTTPS | Settlement polling and optional discovery refresh | ✓ [VERIFIED: local env] | HTTP 200 probe on 2026-04-19 [VERIFIED: local env] | None |

**Missing dependencies with no fallback:**
- None for planning. [VERIFIED: local env]

**Missing dependencies with fallback:**
- `pytest` is not installed as a direct shell command, but `uv run pytest` works and the full suite passes. [VERIFIED: local env]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 8.4.2` installed, repo constraint `>=8,<9` [VERIFIED: [pyproject.toml](/Users/irfanmurad/Developer/vessl/sumsum-bot/pyproject.toml:14)][VERIFIED: local env] |
| Config file | [pyproject.toml](/Users/irfanmurad/Developer/vessl/sumsum-bot/pyproject.toml:20) [VERIFIED: codebase grep] |
| Quick run command | `uv run pytest tests/integration/test_signal_risk_gate.py -q` today; Phase 4 should add an equivalent paper-runtime-focused quick target. [VERIFIED: local env][ASSUMED] |
| Full suite command | `uv run pytest -q` [VERIFIED: local env] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PAPR-01 | Paper mode runs without any live-order side effects and stays paper-only. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `uv run pytest tests/integration/test_paper_runtime.py::test_paper_mode_never_calls_live_execution -q` [ASSUMED] | ❌ Wave 0 [VERIFIED: codebase grep] |
| PAPR-02 | Allowed signals create explicit paper trades that progress through entry, open, and resolution states with bankroll effects. [VERIFIED: .planning/REQUIREMENTS.md] | integration | `uv run pytest tests/integration/test_paper_runtime.py::test_paper_trade_lifecycle_and_bankroll_updates -q` [ASSUMED] | ❌ Wave 0 [VERIFIED: codebase grep] |
| PAPR-03 | Runtime can derive cumulative return, drawdown, and drawdown recovery from stored forward-test history. [VERIFIED: .planning/REQUIREMENTS.md] | unit + integration | `uv run pytest tests/unit/test_paper_metrics.py tests/integration/test_paper_performance.py -q` [ASSUMED] | ❌ Wave 0 [VERIFIED: codebase grep] |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/integration/test_paper_runtime.py -q` once Phase 4 tests exist. [ASSUMED]
- **Per wave merge:** `uv run pytest -q` [VERIFIED: local env]
- **Phase gate:** Full suite green plus fixture-based settlement edge cases before `/gsd-verify-work`. [ASSUMED]

### Wave 0 Gaps
- [ ] `tests/integration/test_paper_runtime.py` — covers PAPR-01 and core lifecycle flows for PAPR-02. [ASSUMED]
- [ ] `tests/unit/test_paper_settlement.py` — covers resolver truth table, ambiguous-status fail-closed behavior, and payout math. [ASSUMED]
- [ ] `tests/unit/test_paper_metrics.py` — covers cumulative return, drawdown depth, and drawdown-recovery duration. [ASSUMED]
- [ ] `tests/integration/test_paper_performance.py` — covers end-to-end bankroll history across multiple resolved trades. [ASSUMED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no [VERIFIED: codebase grep] | No authenticated trading path belongs in Phase 4 paper mode. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md] |
| V3 Session Management | no [VERIFIED: codebase grep] | No user/session layer exists in the current CLI runtime. [VERIFIED: codebase grep] |
| V4 Access Control | no [VERIFIED: codebase grep] | Single-user local CLI runtime; keep live execution code out of scope entirely. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md] |
| V5 Input Validation | yes [VERIFIED: codebase grep] | Reuse typed normalization, explicit enums, and parameterized SQL for market payloads and settlement records. [VERIFIED: [core/clob_client.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/clob_client.py:1)][CITED: https://docs.python.org/3/library/sqlite3.html] |
| V6 Cryptography | no [VERIFIED: codebase grep] | No crypto primitives are required for paper-only public-API reads. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed or partial market-resolution payloads | Tampering | Validate required fields and fail closed when settlement evidence is incomplete. [VERIFIED: [core/clob_client.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/clob_client.py:1)][ASSUMED] |
| Duplicate paper entries from repeated allowed decisions | Tampering | Database-backed idempotency constraint on consumed decisions. [ASSUMED] |
| SQL injection / bad binding | Tampering | Use SQLite placeholders, never string interpolation. [CITED: https://docs.python.org/3/library/sqlite3.html] |
| Accidental live-order code path in paper mode | Elevation of Privilege | Keep paper runtime isolated from any future authenticated trading client and add tests asserting no live execution calls occur. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md][ASSUMED] |

## Sources

### Primary (HIGH confidence)
- Repo codebase inspection of [core/models.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/models.py:1), [core/storage.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/storage.py:1), [core/risk_manager.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/core/risk_manager.py:1), [strategies/weather/signal_engine.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/strategies/weather/signal_engine.py:1), [config/settings.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/config/settings.py:1), [main.py](/Users/irfanmurad/Developer/vessl/sumsum-bot/main.py:1), and tests under [tests/](/Users/irfanmurad/Developer/vessl/sumsum-bot/tests:1) [VERIFIED: codebase grep]
- Python `sqlite3` documentation — transaction handling, placeholders, connection behavior, and threading notes: https://docs.python.org/3/library/sqlite3.html [CITED: https://docs.python.org/3/library/sqlite3.html]
- Python `sched` documentation — monotonic scheduler baseline: https://docs.python.org/3.11/library/sched.html [CITED: https://docs.python.org/3.11/library/sched.html]
- Python `logging` documentation — `LoggerAdapter` for contextual logs: https://docs.python.org/3.11/library/logging.html [CITED: https://docs.python.org/3.11/library/logging.html]
- Polymarket market docs — market fields and query parameters: https://docs.polymarket.com/api-reference/markets/get-market-by-id and https://docs.polymarket.com/api-reference/markets/list-markets [CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][CITED: https://docs.polymarket.com/api-reference/markets/list-markets]
- Polymarket rate limits — public endpoint budget: https://docs.polymarket.com/api-reference/rate-limits [CITED: https://docs.polymarket.com/api-reference/rate-limits]

### Secondary (MEDIUM confidence)
- Polymarket Help Center resolution overview — UMA-based resolution flow and dispute window: https://help.polymarket.com/en/articles/13364518-how-are-prediction-markets-resolved [CITED: https://help.polymarket.com/en/articles/13364518-how-are-prediction-markets-resolved]
- SQLite WAL documentation — concurrency tradeoffs and recent WAL bug note: https://sqlite.org/wal.html [CITED: https://sqlite.org/wal.html]

### Tertiary (LOW confidence)
- None. All externally sourced claims above were checked against official docs or the live repo. [VERIFIED: codebase grep][CITED: https://docs.python.org/3/library/sqlite3.html]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - The repo already uses Python stdlib + SQLite, and environment/runtime versions were verified locally. [VERIFIED: codebase grep][VERIFIED: local env]
- Architecture: MEDIUM - The extension points in code are clear, but settlement-state semantics still require planner-level policy decisions. [VERIFIED: codebase grep][CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]
- Pitfalls: MEDIUM - Duplicate-fill, settlement, and bankroll-ledger risks are strongly implied by the current append-only design, but final schema choices will affect exact failure modes. [VERIFIED: codebase grep][ASSUMED]

**Research date:** 2026-04-19 [VERIFIED: local env]
**Valid until:** 2026-05-19 for repo/code facts, and 2026-04-26 for Polymarket API behavior assumptions. [VERIFIED: codebase grep][CITED: https://docs.polymarket.com/api-reference/markets/get-market-by-id][ASSUMED]
