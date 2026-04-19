# Phase 4: Paper Trading Runtime - Research

**Researched:** 2026-04-19
**Domain:** weather-only paper execution, position lifecycle tracking, runtime orchestration, and forward-test performance measurement over append-only SQLite records [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md] [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: docs/prd.md] [VERIFIED: core/storage.py]
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** When a weather signal clears risk, the paper trader should enter immediately at the current market `no_price`.
- **D-02:** Phase 4 must not simulate slippage, queueing, or delayed fills as a prerequisite to recording paper entries.
- **D-03:** Paper trades must move through explicit entry, open, and resolution states with bankroll updates at the correct lifecycle boundaries.
- **D-04:** Phase 4 stays fully paper-only. No live-order execution path, credentials, or promotion-to-live behavior belongs here.
- **D-05:** Only accepted NOAA-backed weather signals that also pass Phase 3 risk gating may create paper positions.
- **D-06:** Missing NOAA support, rejected signals, or blocked risk decisions must never become open paper trades.
- **D-07:** Weather-only scope remains locked. BTC, sports, and multi-strategy orchestration stay out of scope.
- **D-08:** Phase 4 must persist enough runtime data to measure bankroll change, cumulative return, and drawdown-recovery behavior over the forward-test window.
- **D-09:** The runtime data model should support Phase 5 dashboard/logging work without forcing Phase 4 to build the dashboard itself.

### the agent's Discretion
- Exact settlement polling mechanism, if it stays Polymarket-first and fails closed when outcome data is missing.
- Runtime loop shape, if the result remains a thin entrypoint over reusable core modules.
- Exact ledger granularity, if the stored records still support bankroll, return, drawdown, and recovery analysis.
- Exact paper-position record shape, if lifecycle states and bankroll effects remain explicit and inspectable.

### Deferred Ideas (OUT OF SCOPE)
- Live execution, API credentials, and later promotion-to-live wiring.
- Slippage, queue position, or order-book simulation.
- Dashboard screens, historical event browsing UX, and broader operator presentation concerns.
- VPS and Docker runtime packaging.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PAPR-01 | Operator can run the bot in paper-trading mode without sending live orders. [VERIFIED: .planning/REQUIREMENTS.md] | Add a dedicated paper-runtime entrypoint and orchestration service that reuses the existing scanner, signal engine, and risk gate but writes only local simulation records. [VERIFIED: paper_trader.py] [VERIFIED: main.py] [VERIFIED: strategies/weather/signal_engine.py] |
| PAPR-02 | Operator can simulate order entry, open-position tracking, and market resolution for weather trades. [VERIFIED: .planning/REQUIREMENTS.md] | Introduce explicit paper-trade records plus ledger-style lifecycle events so allowed risk decisions become entered positions, remain open until resolution, then settle into realized bankroll updates. [VERIFIED: core/models.py] [VERIFIED: core/storage.py] [VERIFIED: core/trade_logger.py] |
| PAPR-03 | Operator can measure bankroll change, PnL percentage, and recovery from drawdown over a 2-week forward test. [VERIFIED: .planning/REQUIREMENTS.md] | Persist bankroll snapshots and resolved-trade outcomes in an append-only form that supports cumulative return, max drawdown, and recovery-duration calculations without adding the Phase 5 dashboard yet. [VERIFIED: core/storage.py] [VERIFIED: core/backtester.py] [VERIFIED: docs/strategy.md] |
</phase_requirements>

## Summary

Phase 4 should be planned as the first real execution layer, but it should stay intentionally narrow: consume persisted accepted candidates and Phase 3 risk decisions, create paper trades immediately at the current `no_price`, poll for resolution, and write enough append-only lifecycle and bankroll data to support forward-test analytics. The current repo already has the upstream seams needed for this: `main.py` is a thin CLI, `paper_trader.py` is a thin wrapper ready to diverge into paper-runtime orchestration, `SignalEngine` already owns NOAA plus signal evaluation and exposes a dedicated `evaluate_risk_for_signal(...)` method, and `CandidateStorage` already persists append-only scan, signal, and risk artifacts in SQLite. [VERIFIED: main.py] [VERIFIED: paper_trader.py] [VERIFIED: strategies/weather/signal_engine.py] [VERIFIED: core/storage.py]

The main planning gap is that the repo still lacks any durable paper-position or bankroll ledger abstraction. `core/models.py` stops at `RiskDecisionRecord`; `core/trade_logger.py` and `core/backtester.py` are placeholders; and no integration tests exist yet for lifecycle state, settlement, or performance rollups. That means Phase 4 needs to establish new durable vocabulary and storage tables before it can build the runtime loop. [VERIFIED: core/models.py] [VERIFIED: core/trade_logger.py] [VERIFIED: core/backtester.py] [VERIFIED: tests/]

The safest architecture is to keep four concepts distinct: allowed risk decision, paper position, lifecycle event, and bankroll/performance snapshot. If those stay separate, Phase 5 can query and visualize them cleanly, and Phase 6 can package the same runtime without rewriting internals. If they are collapsed into one mutable table, later observability work will have to reconstruct history from partial state. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md] [VERIFIED: .planning/ROADMAP.md] [VERIFIED: core/storage.py]

**Primary recommendation:** plan Phase 4 around an append-only paper ledger with a thin runtime orchestrator: `scan -> signal -> risk -> enter paper position -> poll resolution -> settle bankroll -> compute performance summary`, with explicit stored records at each boundary and no live-execution affordances. [VERIFIED: .planning/ROADMAP.md] [VERIFIED: docs/prd.md] [VERIFIED: docs/strategy.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Paper trade state and bankroll vocabulary | API / Backend | Database / Storage | New immutable records belong in `core/models.py`, but they only matter if storage can round-trip them. [VERIFIED: core/models.py] [VERIFIED: core/storage.py] |
| Paper-trade and bankroll persistence | Database / Storage | API / Backend | SQLite-first storage is already the repo’s persistence boundary and should stay authoritative for lifecycle history. [VERIFIED: core/storage.py] |
| Runtime orchestration and loop control | API / Backend | Config | `paper_trader.py` should remain thin, with scan interval and bankroll defaults coming from typed settings. [VERIFIED: paper_trader.py] [VERIFIED: main.py] [VERIFIED: config/settings.py] |
| Resolution and settlement logic | API / Backend | Database / Storage | Resolution needs market outcome lookup plus durable updates to positions, events, and bankroll snapshots. [VERIFIED: docs/prd.md] [ASSUMED] |
| Forward-test metrics | API / Backend | Database / Storage | Metrics should be computed from persisted positions and bankroll history rather than transient runtime counters. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md] [VERIFIED: core/storage.py] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`dataclasses`, `sqlite3`, `datetime`, `argparse`, `time`) | Python `>=3.11` [VERIFIED: pyproject.toml] | Position records, timestamps, CLI/runtime loops, and SQLite persistence. | The repo already uses stdlib-first patterns throughout core, config, and CLI modules. [VERIFIED: main.py] [VERIFIED: config/settings.py] [VERIFIED: core/storage.py] |
| `pytest` | `8.x` [VERIFIED: pyproject.toml] | Unit and integration verification for lifecycle transitions and runtime persistence. | Earlier phases already rely on pytest plus `uv` commands for verification. [VERIFIED: .planning/phases/03-risk-and-portfolio-controls/03-VALIDATION.md] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None required | — | Phase 4 can stay dependency-free. | Existing runtime, storage, and CLI code already cover the needed primitives. [VERIFIED: pyproject.toml] |

## Architecture Patterns

### Pattern 1: Treat risk-approved decisions as the only entry contract into paper execution
**What:** Paper-entry code should consume `RiskDecisionRecord` rows or equivalent in-memory records that are already `ALLOWED`, rather than recomputing signal or risk logic. [VERIFIED: strategies/weather/signal_engine.py] [VERIFIED: core/risk_manager.py]
**Why:** D-05 and D-06 lock in a fail-closed handoff where rejected signals and blocked risk decisions must never become open positions. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md]
**Example shape:**
```python
@dataclass(frozen=True)
class PaperEntryRequest:
    risk_decision_id: int | None
    signal_evaluation_id: int | None
    market_id: str
    entry_price: float
    stake_usd: float
    contract_count: float
    entered_at: str
```

### Pattern 2: Separate mutable latest-state convenience from append-only lifecycle history
**What:** Keep one append-only events table for paper lifecycle transitions and, if needed, a separate latest-state table or query for open positions. [VERIFIED: core/storage.py] [ASSUMED]
**Why:** Phase 5 needs reviewable history, and Phase 4 needs deterministic recovery after restarts. Append-only events preserve both. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md]

### Pattern 3: Compute bankroll and performance from a ledger, not from ad hoc runtime variables
**What:** Persist entry cash usage, settlement proceeds, and bankroll snapshots so cumulative return and drawdown metrics can be recomputed from durable records. [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: docs/strategy.md]
**Why:** PAPR-03 is a forward-test measurement requirement, not just a printout requirement. A ledger-backed approach survives restarts and feeds later dashboard work. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md]

### Pattern 4: Keep `paper_trader.py` thin and move orchestration into reusable services
**What:** Mirror the repo’s current CLI posture by keeping script entrypoints small and pushing lifecycle logic into `core/` modules. [VERIFIED: main.py] [VERIFIED: paper_trader.py]
**Why:** The repo already favors thin entrypoints over embedded business logic, and the same runtime must later serve Phase 5 observability and Phase 6 deployment. [VERIFIED: .planning/codebase/ARCHITECTURE.md]

### Anti-Patterns to Avoid
- **Re-running NOAA fetch or risk evaluation inside settlement code:** paper runtime should consume upstream decisions, not fork business rules. [VERIFIED: strategies/weather/signal_engine.py]
- **Using one mutable “paper_trades” row as the only source of truth:** this hides lifecycle history and weakens forward-test analytics. [VERIFIED: core/storage.py] [ASSUMED]
- **Coupling Phase 4 to dashboard views or HTTP APIs:** observability UX belongs in Phase 5. [VERIFIED: .planning/ROADMAP.md]
- **Introducing live-order credentials, signer setup, or execution clients now:** D-04 explicitly forbids that scope. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md]
- **Tying runtime progression to fixtures only:** the runtime loop should still allow once/loop execution with injectable dependencies and test doubles, not only hardcoded fixture data. [VERIFIED: main.py] [ASSUMED]

## Common Pitfalls

### Pitfall 1: “Entry” and “open” become the same implicit state
**What goes wrong:** The runtime inserts one row and later mutates it in place, losing when and why the paper position was created. [ASSUMED]
**How to avoid:** Use explicit lifecycle states and timestamps for entry, open, and resolved transitions, plus a linked event trail or history rows. [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md]

### Pitfall 2: Bankroll math drifts because open stake and realized PnL are mixed together
**What goes wrong:** The runtime updates `current_bankroll_usd` inconsistently on entry and settlement, making drawdown and recovery numbers unreliable. [ASSUMED]
**How to avoid:** Decide and document the bankroll model up front: reserve stake at entry, release plus PnL at settlement, and persist snapshots after each lifecycle-changing event. [VERIFIED: docs/strategy.md] [VERIFIED: .planning/phases/04-paper-trading-runtime/04-CONTEXT.md]

### Pitfall 3: Resolution logic depends on future dashboard or deployment work
**What goes wrong:** The runtime cannot settle trades without Phase 5 or Phase 6 infrastructure. [ASSUMED]
**How to avoid:** Keep settlement self-contained in backend modules and use typed settings plus storage only. [VERIFIED: config/settings.py] [VERIFIED: core/storage.py]

### Pitfall 4: Restart recovery is impossible because open positions only exist in memory
**What goes wrong:** A process restart loses open paper positions and breaks the 2-week forward test. [VERIFIED: .planning/PROJECT.md]
**How to avoid:** Persist open positions and lifecycle events durably in SQLite, and build the runtime loop to reconstruct state from storage on startup. [VERIFIED: .planning/PROJECT.md] [VERIFIED: core/storage.py]

## Validation Architecture

### Required automated coverage
- `tests/unit/test_paper_execution.py` should cover paper entry math, lifecycle transitions, and settlement outcomes over deterministic allowed risk decisions.
- `tests/unit/test_performance_metrics.py` should cover cumulative return, drawdown percentage, peak bankroll tracking, and drawdown-recovery calculations from bankroll snapshots and resolved positions.
- `tests/integration/test_paper_storage.py` should cover append-only persistence and retrieval for paper positions, lifecycle events, and bankroll snapshots.
- `tests/integration/test_paper_runtime.py` should cover the end-to-end once-mode path from accepted candidate through signal, risk, paper entry, settlement, and persisted metrics using stubbed external dependencies.

### Validation focus by requirement
- **PAPR-01:** Assert paper mode does not call any live-execution path and can run the loop through a dedicated paper-runtime entrypoint.
- **PAPR-02:** Assert allowed decisions become entered positions, unresolved positions remain open across loop passes, and resolved positions settle exactly once with persisted bankroll effects.
- **PAPR-03:** Assert persisted bankroll and trade outcomes produce deterministic return, drawdown, and recovery metrics.

### Nyquist posture
- Existing `pytest` plus `uv` infrastructure is sufficient; no separate Wave 0 bootstrap plan is required.
- Each Phase 4 plan should include at least one automated verification command tied to new unit or integration coverage.
- The highest-value integration test is a once-mode runtime test over real SQLite storage with stubbed market-resolution dependencies so lifecycle persistence is verified, not only helper functions.

## Implementation Recommendation

Plan Phase 4 in the same three slices already listed in the roadmap:

1. `04-01` should introduce paper-trade domain vocabulary and append-only storage for positions, lifecycle events, and bankroll history.
2. `04-02` should build the thin paper-runtime orchestrator that reuses existing scan, signal, and risk seams in once/loop mode and restores open positions from storage.
3. `04-03` should add forward-test metrics and reporting helpers over the stored ledger so cumulative return and drawdown recovery become measurable without waiting for the Phase 5 dashboard.

That split keeps persistence and lifecycle semantics stable before the runtime loop depends on them, and it lets performance calculations build on real durable records rather than provisional in-memory counters. [VERIFIED: .planning/ROADMAP.md]

---
*Phase: 04-paper-trading-runtime*
*Research generated: 2026-04-19*
