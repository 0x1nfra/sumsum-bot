# Roadmap: Sumsum Bot

## Overview

The first milestone takes Sumsum Bot from a documentation-only repo to a deployable weather-strategy paper trader. The path is intentionally narrow: build weather market discovery first, add NOAA-based edge calculation and risk controls, turn that into a paper-trading loop, expose the results through logs and a dashboard, then package the system for 24/7 Dockerized VPS deployment so the 2-week forward test can begin.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Market Discovery Foundation** - Build the shared models, configuration, persistence, and weather market scanner.
- [x] **Phase 2: NOAA Signal Engine** - Turn market candidates into explicit weather trade signals.
- [ ] **Phase 3: Risk and Portfolio Controls** - Enforce bankroll-aware sizing, guardrails, and trade gating.
- [ ] **Phase 4: Paper Trading Runtime** - Run continuous simulated trading with position lifecycle tracking.
- [ ] **Phase 5: Dashboard and Logging** - Expose portfolio state, trade history, and operational diagnostics.
- [ ] **Phase 6: 24/7 Deployment Readiness** - Package and operate the paper trader on a cheap VPS with Docker.

## Phase Details

### Phase 1: Market Discovery Foundation
**Goal**: Establish the project skeleton, storage model, configuration surface, and scanning flow for weather markets.
**Depends on**: Nothing (first phase)
**Requirements**: [DISC-01, DISC-02]
**Success Criteria** (what must be TRUE):
  1. Operator can run a weather market scan and get normalized candidate markets from Polymarket data.
  2. Candidate markets are filtered by configurable liquidity, price, and resolution-window rules.
  3. Project storage and configuration foundations exist for later paper-trading and dashboard phases.
**Plans**: 6 plans

Plans:
- [x] 01-00: Create the Wave 0 validation harness, fixtures, and test files used by Phase 1.
- [x] 01-01: Create the full documented project skeleton with thin future-facing modules and entrypoints.
- [x] 01-02: Implement the settings layer, shared models, and storage abstractions with SQLite as the default backend.
- [x] 01-03: Create the deferred BTC and sports strategy package skeletons as thin placeholders.
- [x] 01-04: Implement Polymarket weather market ingestion and normalization.
- [x] 01-05: Add candidate filtering rules, persisted scan outputs, and continuous scan entrypoints for downstream signal evaluation.

### Phase 2: NOAA Signal Engine
**Goal**: Integrate NOAA forecast data and convert market candidates into inspectable weather signals.
**Depends on**: Phase 1
**Requirements**: [WEAT-01, WEAT-02, WEAT-03]
**Success Criteria** (what must be TRUE):
  1. Operator can fetch NOAA forecast data mapped to each supported weather market candidate.
  2. Each candidate can be scored with a reproducible edge calculation using documented strategy thresholds.
  3. Accepted and rejected signals retain enough input detail for later review.
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Preserve contract-day signal inputs and implement curated NOAA mapping/client rejection paths.
- [x] 02-02-PLAN.md — Build contract-family edge calculation rules and explicit acceptance/rejection outputs.
- [x] 02-03-PLAN.md — Persist append-only signal evaluations and wire the end-to-end signal engine.

### Phase 3: Risk and Portfolio Controls
**Goal**: Add bankroll management, trade sizing, and hard risk controls around weather signals.
**Depends on**: Phase 2
**Requirements**: [RISK-01, RISK-02, RISK-03]
**Success Criteria** (what must be TRUE):
  1. Position sizing reflects configured bankroll, Kelly fraction, and max-exposure limits.
  2. Kill switches block trades when drawdown, streak, or safety thresholds are hit.
  3. Blocked trades include a clear reason that the operator can review later.
**Plans**: 2 plans

Plans:
- [ ] 03-01: Implement bankroll, sizing, and exposure-policy logic.
- [ ] 03-02: Add kill switches, trade gating, and rejection logging.

### Phase 4: Paper Trading Runtime
**Goal**: Execute weather signals in simulation mode and measure forward-test performance over time.
**Depends on**: Phase 3
**Requirements**: [PAPR-01, PAPR-02, PAPR-03]
**Success Criteria** (what must be TRUE):
  1. Operator can run the system continuously in paper-trading mode without sending live orders.
  2. Simulated trades move through entry, open, and resolution states with bankroll updates.
  3. The system can report cumulative return and drawdown-recovery behavior over the forward-test window.
**Plans**: 3 plans

Plans:
- [ ] 04-01: Implement the paper execution engine and trade lifecycle state machine.
- [ ] 04-02: Build scheduling/runtime orchestration for continuous scanning and simulated execution.
- [ ] 04-03: Add forward-test performance calculations over bankroll history and resolved trades.

### Phase 5: Dashboard and Logging
**Goal**: Make the simulation observable through a usable dashboard and comprehensive event logs.
**Depends on**: Phase 4
**Requirements**: [OBSV-01, OBSV-02, OBSV-03]
**Success Criteria** (what must be TRUE):
  1. Operator can view bankroll, open positions, resolved trades, win rate, drawdown, and cumulative PnL percentage in one place.
  2. Every simulated trade is stored with signal context, sizing, rationale, and outcome.
  3. Operational issues such as data failures and kill-switch events are visible without digging through raw code.
**Plans**: 3 plans

Plans:
- [ ] 05-01: Design the metrics and event schema for dashboard and audit logging.
- [ ] 05-02: Implement trade and system event logging with queryable history.
- [ ] 05-03: Build the dashboard/API surface for forward-test monitoring.

### Phase 6: 24/7 Deployment Readiness
**Goal**: Package the paper trader for cheap VPS deployment and make the runtime promotable to later live trading.
**Depends on**: Phase 5
**Requirements**: [DEPL-01, DEPL-02, DEPL-03]
**Success Criteria** (what must be TRUE):
  1. Operator can build and publish a Docker image that runs the paper trader predictably.
  2. Runtime data survives restarts and redeploys on a low-cost VPS.
  3. Deployment and configuration choices do not block a later switch from paper trading to live trading.
**Plans**: 3 plans

Plans:
- [ ] 06-01: Add Docker packaging and environment-based runtime configuration.
- [ ] 06-02: Define persistence, volumes, and restart behavior for always-on VPS operation.
- [ ] 06-03: Document deployment workflow and promotion path from paper to live mode.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Market Discovery Foundation | 6/6 | Complete | 2026-04-17 |
| 2. NOAA Signal Engine | 3/3 | Complete | 2026-04-18 |
| 3. Risk and Portfolio Controls | 0/2 | Not started | - |
| 4. Paper Trading Runtime | 0/3 | Not started | - |
| 5. Dashboard and Logging | 0/3 | Not started | - |
| 6. 24/7 Deployment Readiness | 0/3 | Not started | - |
