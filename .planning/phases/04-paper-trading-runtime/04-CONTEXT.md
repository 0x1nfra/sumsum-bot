# Phase 4: Paper Trading Runtime - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Run the existing weather scan, signal, and risk pipeline continuously in paper-trading mode so approved trades can be simulated without sending live orders. This phase covers paper entry, open-position tracking, resolution handling, bankroll updates, and forward-test performance calculation over time. It does not add dashboard UX, broad audit-log presentation, or deployment packaging.

</domain>

<decisions>
## Implementation Decisions

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

</decisions>

<specifics>
## Specific Ideas

- Immediate paper fill at the current `no_price` once a signal passes risk.
- Keep the runtime simple and weather-only rather than simulating exchange microstructure.
- Leave settlement mechanics, loop structure, and ledger detail open for the planner to choose pragmatically.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Defines Phase 4 goal, success criteria, and the three plan slices for paper execution, runtime orchestration, and forward-test performance.
- `.planning/PROJECT.md` — Defines the paper-trading-first validation goal, weather-only scope, small-bankroll posture, and SQLite-first constraint.
- `.planning/REQUIREMENTS.md` — Defines `PAPR-01`, `PAPR-02`, and `PAPR-03`, which Phase 4 must satisfy.
- `.planning/STATE.md` — Confirms Phase 4 is the current focus and that earlier phases are complete.

### Prior phase decisions
- `.planning/phases/01-market-discovery-foundation/01-CONTEXT.md` — Locks in typed settings, stable package boundaries, and audit-oriented persistence expectations.
- `.planning/phases/02-noaa-signal-engine/02-CONTEXT.md` — Locks in NOAA-backed explicit signal evaluation, evidence retention, and fail-closed rejection behavior.
- `.planning/phases/03-risk-and-portfolio-controls/03-CONTEXT.md` — Locks in quarter-Kelly-with-guardrails sizing, paper-trade gating through risk policy, and append-only risk-decision auditing.

### Product and strategy source material
- `docs/prd.md` §3.1 — Defines the weather strategy, entry criteria, and hold-to-resolution posture for weather trades.
- `docs/prd.md` §4 — Defines the intended runtime module boundaries including `paper_trader.py`, `core/trade_logger.py`, `core/backtester.py`, and shared storage.
- `docs/strategy.md` §Part 5 — Defines the broader risk framework and paper-trading motivation that the runtime must preserve.

### Existing implementation context
- `paper_trader.py` — Current thin runtime entrypoint boundary that Phase 4 should turn into real paper-trading orchestration.
- `main.py` — Existing CLI and scan-loop patterns that may inform the paper runtime shape.
- `strategies/weather/signal_engine.py` — Existing signal-evaluation and risk-gating orchestration that Phase 4 should consume rather than bypass.
- `core/risk_manager.py` — Existing risk gating behavior that remains authoritative before paper entry.
- `core/models.py` — Existing shared domain models and vocabulary that Phase 4 should extend for paper positions and bankroll state.
- `core/storage.py` — Existing SQLite-first append-oriented storage patterns that Phase 4 should extend for paper-trade lifecycle and performance tracking.
- `config/settings.py` — Existing typed settings pattern for runtime intervals and paper-trading configuration.
- `core/trade_logger.py` — Placeholder module boundary reserved for paper-trading events and worth reusing rather than inventing a parallel logging surface.
- `tests/integration/test_signal_risk_gate.py` — Confirms the current accepted-signal-to-risk-decision handoff that Phase 4 will build on.
- `tests/integration/test_risk_storage.py` — Shows the append-only persistence posture that lifecycle/runtime records should follow.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `strategies/weather/signal_engine.py`: Already converts approved candidates into persisted signal evaluations and persisted risk decisions.
- `core/risk_manager.py`: Already decides whether a trade is allowed and at what stake, which gives Phase 4 a clean handoff into paper execution.
- `core/storage.py`: Already provides SQLite-first append-only tables and repository methods that can be extended for paper positions, bankroll history, and performance records.
- `config/settings.py`: Already gives Phase 4 a typed runtime configuration pattern for loop timing and paper-mode settings.
- `main.py`: Already shows a simple operator-facing CLI shape with once/loop modes that may be reusable for paper runtime entrypoints.

### Established Patterns
- The codebase prefers thin entrypoints over business logic in scripts.
- Configuration is typed and code-defaulted rather than ad hoc.
- Persistence is append-oriented and audit-friendly, favoring explicit decision records over mutable hidden state.
- Risk policy is authoritative before any execution step; Phase 4 should consume risk-approved decisions rather than recompute approval logic.

### Integration Points
- Phase 4 should start from accepted risk decisions produced by `strategies/weather/signal_engine.py` and `core/risk_manager.py`.
- New paper-position and bankroll logic should extend `core/models.py` and `core/storage.py`.
- Runtime orchestration should live behind `paper_trader.py` while keeping it thin.
- Any paper-trade event recording should reuse `core/trade_logger.py` or its boundary rather than creating a duplicate logging subsystem.

</code_context>

<deferred>
## Deferred Ideas

- Dashboard presentation, operator-facing metrics views, and broader audit-log UX are deferred to Phase 5.
- Docker/VPS process management and restart behavior are deferred to Phase 6.
- Any live-order execution path is deferred until paper-trading validation succeeds.
- More realistic fill simulation such as slippage, queueing, or delayed execution is deferred beyond Phase 4 unless planning finds it is strictly necessary.

</deferred>

---

*Phase: 04-paper-trading-runtime*
*Context gathered: 2026-04-19*
