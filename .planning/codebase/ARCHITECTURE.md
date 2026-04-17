# Architecture

**Analysis Date:** 2026-04-17

## Pattern Overview

**Overall:** Documentation-first planned modular Python bot architecture

**Key Characteristics:**
- The current repository is documentation-only. The only product artifacts are `docs/prd.md` and `docs/strategy.md`; no executable source tree exists yet.
- The intended runtime design is a layered Python module layout defined in the architecture tree embedded in `docs/prd.md`.
- Strategy modules are planned as separate domain packages under `strategies/`, with shared execution, sizing, storage, and risk controls centralized under `core/`.

## Layers

**Documentation layer:**
- Purpose: Capture product intent, strategy selection, and the proposed runtime layout.
- Location: `docs/`
- Contains: Requirements and system design notes in `docs/prd.md` and `docs/strategy.md`
- Depends on: None inside the repo
- Used by: Planning documents in `.planning/codebase/` and future implementation work

**Planning layer:**
- Purpose: Convert repo analysis into operational guidance for future implementation.
- Location: `.planning/codebase/`
- Contains: Reference docs such as `STACK.md`, `INTEGRATIONS.md`, `CONCERNS.md`, and these architecture documents
- Depends on: Repository contents, especially `docs/prd.md` and `docs/strategy.md`
- Used by: GSD planning and execution workflows

**Planned core engine layer:**
- Purpose: Centralize exchange access, risk controls, market discovery, persistence, and backtesting.
- Location: Planned under `core/` in `docs/prd.md`
- Contains: `core/clob_client.py`, `core/kelly_engine.py`, `core/risk_manager.py`, `core/trade_logger.py`, `core/backtester.py`, `core/market_scanner.py`, `core/storage.py`
- Depends on: External market/data APIs and runtime configuration from the planned `config/` package
- Used by: Planned strategy packages under `strategies/` plus root entrypoints `main.py` and `paper_trader.py`

**Planned strategy layer:**
- Purpose: Encapsulate market-specific signal generation and source-specific parsing.
- Location: Planned under `strategies/` in `docs/prd.md`
- Contains: `strategies/weather/noaa_client.py`, `strategies/weather/edge_calculator.py`, `strategies/weather/scanner.py`, `strategies/btc_5min/signal_engine.py`, `strategies/btc_5min/scanner.py`, `strategies/sports/odds_client.py`, `strategies/sports/comparator.py`, `strategies/sports/scanner.py`
- Depends on: Shared market data and risk primitives in the planned `core/` package
- Used by: Planned orchestrators `main.py`, `paper_trader.py`, and `backtest/runner.py`

**Planned configuration and state layer:**
- Purpose: Hold runtime settings, kill-switch thresholds, and local trade history.
- Location: Planned under `config/`, `data/`, and `backtest/` in `docs/prd.md`
- Contains: `config/settings.py`, `config/kill_switches.py`, `data/trades.db`, `backtest/runner.py`, `backtest/historical/`
- Depends on: Filesystem and external market/history inputs
- Used by: Planned core modules and entrypoints

## Data Flow

**Current repository flow:**

1. Product and architecture intent is documented in `docs/prd.md`.
2. Strategy prioritization and operating constraints are refined in `docs/strategy.md`.
3. Repository analysis is captured under `.planning/codebase/` for later implementation phases.

**Planned live trading flow from `docs/prd.md`:**

1. `main.py` invokes shared market discovery through the planned `core/market_scanner.py` and strategy scanners.
2. Strategy modules under the planned `strategies/` tree pull authoritative external inputs such as Polymarket, NOAA, or sports odds feeds and compute edge signals.
3. Shared controls in the planned `core/kelly_engine.py` and `core/risk_manager.py` decide whether and how much to trade.
4. Exchange execution is routed through the planned `core/clob_client.py`.
5. Outcomes, trades, and diagnostics are persisted through the planned `core/trade_logger.py` and `core/storage.py` into `data/trades.db`.

**Planned backtesting flow from `docs/prd.md`:**

1. `backtest/runner.py` loads historical datasets from `backtest/historical/`.
2. Strategy modules under the planned `strategies/` tree replay signal logic against historical inputs.
3. Shared sizing and risk logic from the planned `core/kelly_engine.py` and `core/risk_manager.py` are applied to simulated trades.
4. Results are recorded through the planned storage and logging modules for analysis before live deployment.

**State Management:**
- Current state is file-based documentation only under `docs/` and `.planning/codebase/`.
- Planned runtime state is local and explicit: settings in the planned `config/` package, trade persistence in the planned `data/trades.db`, and replay inputs in the planned `backtest/historical/`.

## Key Abstractions

**Market scanner:**
- Purpose: Identify tradable Polymarket opportunities before strategy-specific filtering.
- Examples: Planned `core/market_scanner.py`, planned `strategies/weather/scanner.py`, planned `strategies/btc_5min/scanner.py`, planned `strategies/sports/scanner.py`
- Pattern: Shared discovery in `core/`, narrowed by strategy-local scanning modules

**Risk and sizing engine:**
- Purpose: Apply quarter-Kelly sizing, exposure caps, and kill-switch logic described in `docs/prd.md` and `docs/strategy.md`.
- Examples: Planned `core/kelly_engine.py`, planned `core/risk_manager.py`, planned `config/kill_switches.py`
- Pattern: Centralized policy layer used by every strategy before execution

**Provider adapters:**
- Purpose: Encapsulate external source parsing and isolate provider-specific concerns from decision logic.
- Examples: Planned `core/clob_client.py`, planned `strategies/weather/noaa_client.py`, planned `strategies/sports/odds_client.py`
- Pattern: One module per provider, called by strategy or execution layers rather than imported broadly

**Execution modes:**
- Purpose: Separate live orchestration from paper trading and historical replay.
- Examples: Planned `main.py`, planned `paper_trader.py`, planned `backtest/runner.py`
- Pattern: Thin entrypoints over shared strategy and core modules

## Entry Points

**Documentation entrypoint:**
- Location: `docs/prd.md`
- Triggers: Human review and planning workflows
- Responsibilities: Defines the target package structure, core modules, and external integration points

**Strategy selection reference:**
- Location: `docs/strategy.md`
- Triggers: Human review and planning workflows
- Responsibilities: Defines strategy priority, capital allocation, and kill-switch constraints that the planned code should implement

**Planned live bot entrypoint:**
- Location: Planned `main.py` in `docs/prd.md`
- Triggers: Continuous live trading process
- Responsibilities: Initialize configuration, start scanners, route approved signals through risk controls, and execute trades

**Planned paper trading entrypoint:**
- Location: Planned `paper_trader.py` in `docs/prd.md`
- Triggers: Safe dry-run or simulation mode
- Responsibilities: Reuse live signal generation while replacing real execution with simulated order handling

**Planned backtesting entrypoint:**
- Location: Planned `backtest/runner.py` in `docs/prd.md`
- Triggers: Historical evaluation workflow
- Responsibilities: Replay historical inputs, compute simulated outcomes, and validate strategy thresholds before live use

## Error Handling

**Strategy:** Not implemented in code; only high-level guardrails are documented

**Patterns:**
- `docs/strategy.md` defines operational halts such as drawdown stops, loss streak pauses, and fee-change re-evaluation; these imply centralized failure handling in the planned `core/risk_manager.py` and `config/kill_switches.py`.
- `docs/prd.md` implies provider-specific fault isolation by splitting external access into separate planned modules such as `core/clob_client.py`, `strategies/weather/noaa_client.py`, and `strategies/sports/odds_client.py`.

## Cross-Cutting Concerns

**Logging:** Current repo has no runtime logging. Planned trade and event logging is called out via `core/trade_logger.py` in `docs/prd.md`.

**Validation:** Current validation is manual, through narrative rules in `docs/prd.md` and `docs/strategy.md`. Planned validation points include scanner filters, edge thresholds, and kill switches in the proposed `core/` and `config/` modules.

**Authentication:** No auth implementation exists in the repo. The planned architecture requires exchange credentials for Polymarket execution but does not yet define a concrete mechanism; NOAA is explicitly unauthenticated in `docs/prd.md`.

## Implementation Guidance

- Treat `docs/prd.md` as the architectural source of truth for the initial Python package boundaries until real code exists.
- Keep future trading logic inside the planned `strategies/` tree and reserve the planned `core/` tree for reusable cross-strategy services.
- Keep root scripts thin. Any behavior added to the planned `main.py`, `paper_trader.py`, or `backtest/runner.py` should delegate into reusable modules rather than accumulating business logic in entrypoints.
- Preserve the separation between current documentation artifacts (`docs/`, `.planning/codebase/`) and future executable code so planning files remain a reference layer, not an implementation layer.

---

*Architecture analysis: 2026-04-17*
