# Phase 3: Risk and Portfolio Controls - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Add bankroll-aware sizing, exposure controls, hard trade gates, and inspectable rejection reasons around the existing weather signal flow. This phase decides whether an accepted weather signal is tradable and at what size. It does not add paper-order execution, resolved-trade lifecycle tracking, or dashboard/reporting work.

</domain>

<decisions>
## Implementation Decisions

### Sizing policy
- **D-01:** Keep quarter-Kelly as the core sizing model, but treat it as an input to the final stake rather than the final authority.
- **D-02:** Apply a small conservative haircut to the derived signal probability before running Kelly sizing.
- **D-03:** Clamp every proposed trade by a hard per-trade cap of 5% of current bankroll.
- **D-04:** Final allowed stake should be the minimum of adjusted quarter-Kelly stake, the 5% per-trade cap, and remaining exposure capacity.
- **D-05:** If the final allowed stake falls below the minimum practical stake, the trade must be blocked with an explicit reason code.

### Exposure controls
- **D-06:** Phase 3 should enforce three exposure layers: per-trade cap, per-resolution-window cap, and global max open exposure.
- **D-07:** Global max open exposure should be capped at 30% of current bankroll.
- **D-08:** Exposure tied to the same resolution window should be capped at 15% of current bankroll.
- **D-09:** Phase 3 should not yet add more granular city-level or contract-family-level correlation caps.

### Kill switches and trade gating
- **D-10:** Phase 3 should include drawdown halts, exposure-cap hard blocks, market/signal safety blocks, and cooldown behavior after a trigger.
- **D-11:** Drawdown halts should trigger when bankroll falls 20% from peak bankroll.
- **D-12:** Consecutive-loss pause logic should be deferred to Phase 4 because it depends on resolved paper-trade outcomes that do not exist yet.
- **D-13:** Risk policy must preserve the existing fail-closed NOAA/signal safety posture; risk controls must never override missing, stale, or invalid signal inputs into tradable approvals.

### Risk audit trail
- **D-14:** Blocked trades should persist a rich but bounded audit record rather than only a reason code.
- **D-15:** The blocked-trade record should include candidate or market id, signal evaluation reference, current bankroll, peak bankroll, proposed Kelly stake before clamps, final allowed stake if any, triggered rule codes, a human-readable rejection reason, an exposure snapshot relevant to the decision, and a timestamp.
- **D-16:** Phase 3 should not attempt to build the full portfolio-event or paper-trading ledger in this audit record; that belongs in later runtime phases.

### Capital baseline
- **D-17:** Use current bankroll for stake sizing and exposure-cap calculations.
- **D-18:** Use peak bankroll only for drawdown calculations.

### the agent's Discretion
- Exact minimum practical stake threshold, provided blocked undersized trades remain inspectable.
- Exact probability haircut formula, provided it is conservative and explicit in code/tests.
- Exact cooldown duration and resume semantics after a kill-switch trigger, provided they are config-backed and auditable.
- Exact schema shape for blocked-trade persistence, provided all locked audit fields above are retained.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Defines Phase 3 goal, success criteria, and the two plan slices for sizing/exposure policy and kill switches/rejection logging.
- `.planning/PROJECT.md` — Defines the weather-only milestone scope, small-bankroll posture, paper-trading validation goal, and capital-preservation priority that should shape risk controls.
- `.planning/REQUIREMENTS.md` — Defines `RISK-01`, `RISK-02`, and `RISK-03`, which Phase 3 must satisfy.
- `.planning/STATE.md` — Confirms the project is at the Phase 3 planning boundary and records the current milestone posture.

### Prior phase decisions
- `.planning/phases/01-market-discovery-foundation/01-CONTEXT.md` — Locks in typed settings, strict candidate approval boundaries, and auditability expectations that Phase 3 must preserve.
- `.planning/phases/02-noaa-signal-engine/02-CONTEXT.md` — Locks in explicit fail-closed NOAA handling, append-only signal evaluation history, and inspectable rejection reasons that risk controls must build on rather than replace.

### Product and strategy source material
- `docs/prd.md` §1-4 — Defines the product vision, small-capital operating posture, quarter-Kelly sizing intent, and the documented runtime module boundaries including `core/kelly_engine.py`, `core/risk_manager.py`, and `config/kill_switches.py`.
- `docs/strategy.md` §Part 5 — Defines the recommended risk framework, including reserve capital, max single-trade exposure, max total exposure, quarter-Kelly posture, and kill-switch examples.

### Existing implementation context
- `config/settings.py` — Current typed runtime settings pattern that Phase 3 risk and sizing thresholds should extend.
- `config/kill_switches.py` — Existing placeholder boundary for kill-switch configuration that Phase 3 should turn into real policy settings.
- `core/kelly_engine.py` — Existing placeholder boundary for Kelly sizing logic that Phase 3 should implement.
- `core/risk_manager.py` — Existing placeholder boundary for trade approval and blocking logic that Phase 3 should implement.
- `core/storage.py` — Existing SQLite-first persistence layer and append-only signal evaluation storage that Phase 3 should extend with risk-decision audit records.
- `core/models.py` — Existing shared candidate and signal-evaluation vocabulary that Phase 3 should extend or compose with rather than bypass.
- `strategies/weather/signal_engine.py` — Existing accepted/rejected signal flow that Phase 3 should gate with risk policy before paper execution exists.
- `paper_trader.py` — Confirms paper runtime is still a thin wrapper, so Phase 3 should stop at policy gating rather than inventing full paper-trade lifecycle logic early.
- `tests/integration/test_noaa_signal_engine.py` — Shows the current signal-engine expectations and append-only evaluation behavior that Phase 3 should preserve.
- `tests/integration/test_signal_storage.py` — Shows the existing storage expectations for accepted and rejected signal records that Phase 3 audit persistence should follow.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config/settings.py`: Already provides the typed, override-friendly configuration pattern that risk thresholds and sizing controls should reuse.
- `config/kill_switches.py`: Exists as a placeholder boundary for safety thresholds, so Phase 3 can fill in real fields instead of creating a parallel config surface.
- `core/kelly_engine.py`: Exists as the natural home for adjusted Kelly sizing logic.
- `core/risk_manager.py`: Exists as the natural home for trade gating, exposure checks, and kill-switch decisions.
- `core/storage.py`: Already provides SQLite-first persistence and append-only evaluation storage patterns that can be extended for blocked-trade audit records.
- `strategies/weather/signal_engine.py`: Already turns approved candidates into accepted/rejected signal evaluations, which gives Phase 3 a clean integration point for risk gating.

### Established Patterns
- Runtime configuration is typed and code-defaulted rather than scattered across ad hoc constants.
- The system already fails closed on weak NOAA or invalid signal inputs; risk logic should preserve that posture.
- Auditability matters: accepted and rejected outcomes already preserve inspectable reasons, and Phase 3 should extend that discipline to blocked trades.
- Persistence is SQLite-first and append-oriented, which favors storing explicit decision records over mutating in-place status state.

### Integration Points
- Phase 3 should consume the signal-evaluation output produced by `strategies/weather/signal_engine.py`.
- Sizing logic should live behind `core/kelly_engine.py`.
- Approval/block decisions should live behind `core/risk_manager.py`.
- Risk decisions and blocked-trade evidence should extend `core/storage.py`.
- Thresholds and cooldown settings should be wired through `config/settings.py` and `config/kill_switches.py`.

</code_context>

<specifics>
## Specific Ideas

- Keep Kelly in the system, but never let it exceed hard small-bankroll guardrails.
- Favor current-bankroll-based sizing so the system naturally scales down after losses.
- Treat per-resolution-window caps as the first correlation-control mechanism before introducing finer-grained exposure categories.
- Persist enough blocked-trade evidence that later paper-runtime and dashboard phases can explain exactly why a valid signal was not allowed to trade.

</specifics>

<deferred>
## Deferred Ideas

- Consecutive-loss pause based on resolved trade history is deferred to Phase 4, when paper-trade outcomes and streak calculations exist.
- More granular exposure segmentation by city, contract family, or other correlation buckets is deferred beyond Phase 3 unless planning finds a concrete need.

</deferred>

---

*Phase: 03-risk-and-portfolio-controls*
*Context gathered: 2026-04-19*
