# Sumsum Bot

## What This Is

Sumsum Bot is a Python-based Polymarket trading bot project focused first on one strategy: weather market paper trading. The initial product is not a multi-strategy live bot; it is a weather-only forward-testing system that runs continuously, simulates trades, logs every decision, and shows whether the strategy can grow capital and recover from drawdowns before real money is used.

## Core Value

Prove that the weather strategy can preserve capital, recover from drawdowns, and produce positive paper-trading returns over a 2-week forward test before any live deployment.

## Requirements

### Validated

- Scan Polymarket weather markets continuously and identify candidate opportunities.
  Validated across Phases 01-02: Market Discovery Foundation and NOAA Signal Engine.
- Apply disciplined bankroll management, sizing, and kill switches during paper trading.
  Validated in Phase 03: Risk and Portfolio Controls.
- Run a 24/7 paper trader that records every simulated trade and portfolio change.
  Validated in Phase 04: Paper Trading Runtime.
- Weather-market edge can be computed from NOAA forecast data with explicit entry filters.
  Validated in Phase 02: NOAA Signal Engine.

### Active

- [ ] Provide a dashboard and logs that make forward-test performance and failure modes easy to inspect.
- [ ] Package the bot for cheap VPS deployment with Docker and a later path to live trading.

### Out of Scope

- BTC, sports, and intra-market arbitrage strategies — deferred until weather profitability is proven.
- Live order execution with real funds — blocked on successful paper-trading validation.
- Large-scale strategy expansion or portfolio balancing across multiple strategies — premature before a weather-only proof point exists.
- PostgreSQL as required infrastructure from day one — SQLite is sufficient for the first single-bot deployment and keeps ops simple.

## Context

- The repository now contains executable implementation through Phase 04: market discovery, NOAA signal evaluation, append-only risk controls, a paper-trading runtime, and durable forward-test metrics.
- The original concept covered weather, BTC, sports, and arbitrage. The scoped milestone is narrower: weather only until the strategy shows paper-trading profitability.
- Backtesting is useful for shaping the strategy, but the gating validation is a 2-week paper-trading run measured against starting capital and drawdown recovery behavior.
- The operator is a solo developer/trader optimizing for low capital, low monthly cost, and fast iteration.
- NOAA is the primary external signal source for the first strategy. Polymarket market data remains the execution-side market input.
- The system needs to run 24/7 in the cloud during the forward test, with Docker-based deployment that can later be promoted to live trading on the same operational model.
- Paper-trading output is now persisted as SQLite positions, lifecycle events, bankroll snapshots, and forward-test performance summaries, so the next phase can focus on operator visibility rather than core execution semantics.

## Constraints

- **Capital**: Small starting bankroll ($50-$100) — risk controls and capital preservation matter more than maximizing throughput.
- **Strategy scope**: Weather only for v1 — avoid multi-strategy architecture decisions that slow validation.
- **Validation**: Paper trading for 2 weeks before live trading — no real-funds execution in the first milestone.
- **Data**: Free data sources only — NOAA is the required weather input.
- **Deployment**: Cheapest practical VPS with Docker image distribution — must support always-on simulation and straightforward redeploys.
- **Storage**: SQLite first, PostgreSQL-ready design — keep the first deployment simple while preserving a clean migration path.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Start with weather strategy only | Reduces scope and focuses validation on the strongest documented edge | — Pending |
| Gate live trading on a 2-week paper-trading result | Forward testing is the actual proof threshold, not backtest-only results | — Pending |
| Include dashboard and full trade logging in v1 | The strategy needs inspection data to understand wins, losses, and drawdown recovery | Dashboard/logging remains active for Phase 05; durable runtime summaries and ledger history are complete in Phase 04 |
| Support 24/7 cloud deployment in the first milestone | Continuous paper trading is required to gather enough simulation data | Runtime loop and paper-only CLI are complete; deployment packaging remains active |
| Use SQLite first with PostgreSQL-ready abstractions | Single-bot VPS deployment does not justify database overhead yet | Confirmed through Phase 04 paper ledger and analytics storage |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check -> still the right priority?
3. Audit Out of Scope -> reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-20 after Phase 04 completion*
