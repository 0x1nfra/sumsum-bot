# Phase 3: Risk and Portfolio Controls - Research

**Researched:** 2026-04-19
**Domain:** bankroll-aware sizing, exposure controls, kill switches, and blocked-trade auditability for the weather-only paper-trading path [VERIFIED: .planning/phases/03-risk-and-portfolio-controls/03-CONTEXT.md] [VERIFIED: docs/strategy.md] [VERIFIED: docs/prd.md] [VERIFIED: core/storage.py]
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Quarter-Kelly remains the sizing input, but never the final authority.
- **D-02:** Apply a conservative probability haircut before Kelly sizing.
- **D-03:** Hard-cap every trade at 5% of current bankroll.
- **D-04:** Final stake is the minimum of adjusted quarter-Kelly stake, per-trade cap, and remaining exposure capacity.
- **D-05:** Stakes below the minimum practical size must be blocked with an explicit reason.
- **D-06:** Enforce per-trade, per-resolution-window, and global open-exposure limits.
- **D-07:** Global open exposure is capped at 30% of current bankroll.
- **D-08:** Exposure in the same resolution window is capped at 15% of current bankroll.
- **D-09:** Do not add city-level or contract-family correlation caps yet.
- **D-10:** Include drawdown halts, exposure-cap hard blocks, market/signal safety blocks, and cooldown behavior.
- **D-11:** Drawdown halt triggers at 20% below peak bankroll.
- **D-12:** Consecutive-loss pause is deferred to Phase 4.
- **D-13:** Risk policy must preserve the existing fail-closed NOAA and signal-safety posture.
- **D-14:** Blocked trades persist a rich but bounded audit record.
- **D-15:** The blocked-trade record must include signal reference, bankroll state, proposed and final stake, triggered rules, human-readable reason, exposure snapshot, and timestamp.
- **D-16:** Do not build the full paper-trading ledger in this phase.
- **D-17:** Use current bankroll for sizing and exposure-cap calculations.
- **D-18:** Use peak bankroll only for drawdown calculations.

### the agent's Discretion
- Exact minimum practical stake threshold, if it is config-backed and produces inspectable blocks.
- Exact haircut formula, if it is deterministic and explicit in evidence.
- Exact cooldown duration and resume semantics, if they are config-backed and auditable.
- Exact risk-decision storage schema, if all locked audit fields survive round-trip.

### Deferred Ideas (OUT OF SCOPE)
- Loss-streak pauses that depend on resolved trade history.
- Finer-grained correlation controls by city, contract family, or region.
- Real order placement, fill management, and trade resolution lifecycle work.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RISK-01 | Operator can apply bankroll-based position sizing using the configured Kelly fraction and per-trade exposure caps. [VERIFIED: .planning/REQUIREMENTS.md] | Implement a sizing pipeline that starts from signal-derived probability, applies a conservative haircut, calculates quarter-Kelly, and clamps by minimum stake, 5% per-trade cap, 15% same-window exposure headroom, and 30% global headroom. [VERIFIED: 03-CONTEXT.md] [VERIFIED: docs/strategy.md] |
| RISK-02 | Operator can enforce kill switches for conditions such as max drawdown, loss streaks, or invalid market conditions. [VERIFIED: .planning/REQUIREMENTS.md] | Phase 3 should implement drawdown halt, cooldown, exposure-cap hard blocks, and safety blocks for invalid signals or unsupported statuses, while explicitly deferring loss-streak logic until paper trade outcomes exist in Phase 4. [VERIFIED: 03-CONTEXT.md] [VERIFIED: strategies/weather/signal_engine.py] |
| RISK-03 | Operator can review why a candidate trade was blocked by risk controls. [VERIFIED: .planning/REQUIREMENTS.md] | Add append-only risk-decision persistence with rule codes, bankroll and exposure snapshot fields, proposed/final stake amounts, and the linked signal evaluation reference so later phases can explain every blocked trade. [VERIFIED: 03-CONTEXT.md] [VERIFIED: core/storage.py] |
</phase_requirements>

## Summary

Phase 3 should introduce a dedicated risk-decision layer between Phase 2 signal evaluation and Phase 4 paper execution. The existing `SignalEngine` already produces append-only `signal_evaluations` with explicit rejection reasons for NOAA or edge failures, but it does not yet determine stake size, exposure headroom, or whether an otherwise accepted signal is tradable under the bankroll rules. [VERIFIED: strategies/weather/signal_engine.py] [VERIFIED: tests/integration/test_noaa_signal_engine.py]

The current codebase gives this phase four strong seams. `core/kelly_engine.py` and `core/risk_manager.py` are still placeholders, so the plan can define their contracts without breaking established implementation. `config/settings.py` already carries typed thresholds and environment-style overrides. `config/kill_switches.py` exists as the natural home for cooldown and drawdown thresholds. `core/storage.py` already uses SQLite-first append-oriented persistence and dedicated tables for signal history, which matches the requirement to preserve blocked-trade evidence rather than mutating in-place status. [VERIFIED: core/kelly_engine.py] [VERIFIED: core/risk_manager.py] [VERIFIED: config/settings.py] [VERIFIED: config/kill_switches.py] [VERIFIED: core/storage.py]

The key planning decision is to separate three concepts that do not exist yet in the repo: portfolio state, sizing proposal, and final risk decision. If they stay conflated, the later paper-trading runtime will have to reverse-engineer why a signal was blocked or what caps altered the raw Kelly output. If they are first-class records now, Phase 4 can consume the same decision artifacts instead of rebuilding policy. [VERIFIED: 03-CONTEXT.md] [VERIFIED: docs/prd.md]

**Primary recommendation:** Plan Phase 3 around a `SignalEvaluationRecord -> PortfolioSnapshot -> KellySizingDecision -> RiskDecision -> RiskDecisionStorage` pipeline, and make append-only blocked-decision persistence a first-class deliverable rather than an afterthought. [VERIFIED: core/storage.py] [VERIFIED: strategies/weather/signal_engine.py]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Kelly math and probability haircut | API / Backend | — | Pure deterministic sizing logic belongs in `core/kelly_engine.py`, isolated from storage and orchestration. [VERIFIED: core/kelly_engine.py] |
| Exposure policy and kill-switch evaluation | API / Backend | — | The policy needs bankroll, open exposure, and signal metadata, but should remain independent of runtime orchestration. [VERIFIED: core/risk_manager.py] |
| Risk thresholds and cooldown settings | Config | API / Backend | Existing typed settings and the kill-switch module already define the repo’s configuration style. [VERIFIED: config/settings.py] [VERIFIED: config/kill_switches.py] |
| Append-only blocked-trade evidence | Database / Storage | API / Backend | Phase 3 needs durable operator review, not transient in-memory decisions. [VERIFIED: core/storage.py] |
| Risk gate integration with accepted signals | API / Backend | Database / Storage | `SignalEngine` currently emits accepted/rejected signal rows; risk gating should compose with that output without reparsing raw market data. [VERIFIED: strategies/weather/signal_engine.py] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`dataclasses`, `sqlite3`, `datetime`, `enum`) | Python `>=3.11` [VERIFIED: pyproject.toml] | Deterministic risk records, timestamps, and SQLite persistence. | The repo already uses these primitives everywhere in config, models, and storage. [VERIFIED: config/settings.py] [VERIFIED: core/models.py] [VERIFIED: core/storage.py] |
| `pytest` | `8.x` [VERIFIED: pyproject.toml] | Unit and integration verification for sizing, gating, and persistence. | Existing phases already rely on `pytest` with targeted unit and integration suites. [VERIFIED: .planning/phases/02-noaa-signal-engine/02-VALIDATION.md] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None required | — | Phase 3 can stay dependency-free. | The repo already implements Phase 1 and Phase 2 with stdlib plus pytest only. [VERIFIED: pyproject.toml] |

## Architecture Patterns

### Pattern 1: Preserve raw sizing math separately from final trade approval
**What:** Keep a dedicated sizing result that records adjusted probability, raw Kelly fraction, quarter-Kelly fraction, unclamped stake, and each clamp that changed the stake. [VERIFIED: 03-CONTEXT.md]
**Why:** The final trade stake is not equal to the Kelly output in this project; D-01 through D-04 require explicit clamp layering. [VERIFIED: 03-CONTEXT.md]
**Example shape:**
```python
@dataclass(frozen=True)
class KellySizingDecision:
    derived_no_probability: float
    probability_haircut: float
    adjusted_no_probability: float
    raw_kelly_fraction: float
    kelly_fraction: float
    bankroll_usd: float
    proposed_stake_usd: float
    capped_stake_usd: float
    minimum_stake_usd: float
    clamp_reasons: tuple[str, ...]
```

### Pattern 2: Model portfolio state explicitly instead of querying ad hoc values everywhere
**What:** Introduce immutable portfolio and exposure snapshot records that the risk manager can consume and persist. [VERIFIED: core/models.py] [ASSUMED]
**Why:** Drawdown checks use peak bankroll, exposure checks use current bankroll and open stake totals, and future phases need the same inputs without recomputing them from divergent sources. [VERIFIED: 03-CONTEXT.md]
**Example shape:**
```python
@dataclass(frozen=True)
class PortfolioSnapshot:
    current_bankroll_usd: float
    peak_bankroll_usd: float
    open_exposure_usd: float
    open_exposure_by_window: dict[str, float]
    captured_at: str
```

### Pattern 3: Append-only risk decisions, not mutable approval flags
**What:** Store one decision row per risk evaluation, including approved and blocked outcomes. [VERIFIED: core/storage.py] [VERIFIED: tests/integration/test_signal_storage.py]
**Why:** Phase 2 already uses append-only `signal_evaluations`, and Phase 3 needs operator-auditable reasoning rather than “latest state only.” [VERIFIED: strategies/weather/signal_engine.py]
**Recommended fields:**
- `signal_evaluation_id`
- `market_id`
- `decision_status`
- `decision_reason`
- `triggered_rule_codes`
- `current_bankroll_usd`
- `peak_bankroll_usd`
- `open_exposure_usd`
- `window_exposure_usd`
- `proposed_stake_usd`
- `allowed_stake_usd`
- `evidence_json`

### Pattern 4: Fail closed on unsafe upstream signal states
**What:** Only accepted Phase 2 signal evaluations should be eligible for risk sizing; rejected or incomplete signal rows should become immediate `signal_not_tradable` style risk blocks. [VERIFIED: strategies/weather/signal_engine.py]
**Why:** D-13 prohibits risk policy from turning weak or invalid signals into tradable approvals. [VERIFIED: 03-CONTEXT.md]

### Anti-Patterns to Avoid
- **Letting `RiskManager` re-run NOAA or edge logic:** Phase 2 already owns signal evaluation; Phase 3 should consume its output, not duplicate it. [VERIFIED: strategies/weather/signal_engine.py]
- **Encoding all block rationale in one free-text string:** The phase requires inspectable reason codes and structured audit evidence. [VERIFIED: 03-CONTEXT.md]
- **Using peak bankroll for sizing:** D-17 requires current-bankroll sizing so stake sizes scale down after losses. [VERIFIED: 03-CONTEXT.md]
- **Implementing loss-streak pauses now:** There is no resolved trade lifecycle yet, so this would force premature Phase 4 state into Phase 3. [VERIFIED: 03-CONTEXT.md] [VERIFIED: paper_trader.py]
- **Using mutable “latest risk status” records only:** That would erase why an earlier signal was blocked, which breaks RISK-03. [VERIFIED: .planning/REQUIREMENTS.md]

## Common Pitfalls

### Pitfall 1: Kelly produces negative or oversized stakes when edge is weak or near certainty bounds
**What goes wrong:** The implementation uses the textbook fraction directly and either emits a negative stake or a stake larger than the configured caps. [ASSUMED]
**How to avoid:** Clamp probabilities away from invalid ranges, apply the explicit haircut first, take quarter-Kelly, then layer the hard stake and exposure caps before final approval. [VERIFIED: 03-CONTEXT.md]

### Pitfall 2: Drawdown logic accidentally keys off current bankroll instead of high-water mark
**What goes wrong:** A large loss shrinks the halt threshold itself, making the system more permissive after losses. [VERIFIED: 03-CONTEXT.md]
**How to avoid:** Persist and pass both `current_bankroll_usd` and `peak_bankroll_usd`, and compute drawdown only from the peak baseline. [VERIFIED: 03-CONTEXT.md]

### Pitfall 3: Exposure caps cannot be explained later because only the final blocked reason is stored
**What goes wrong:** The operator sees “exposure cap exceeded” but cannot tell whether the per-trade, window, or portfolio cap triggered. [VERIFIED: 03-CONTEXT.md]
**How to avoid:** Persist a rule-code array plus a structured exposure snapshot and both proposed and allowed stake values. [VERIFIED: 03-CONTEXT.md]

### Pitfall 4: Phase 3 introduces pseudo-runtime state before the paper trader exists
**What goes wrong:** The risk layer starts creating open-position ledgers, fill-state transitions, or resolved trade bookkeeping. [VERIFIED: paper_trader.py]
**How to avoid:** Restrict Phase 3 to policy evaluation and append-only risk decisions; let Phase 4 own trade lifecycle state. [VERIFIED: .planning/ROADMAP.md]

## Validation Architecture

### Required automated coverage
- `tests/unit/test_kelly_engine.py` should cover haircut, quarter-Kelly, per-trade cap, minimum stake block, and zero-edge / negative-edge paths.
- `tests/unit/test_risk_manager.py` should cover global exposure cap, per-window cap, drawdown halt, cooldown gate, unsafe upstream signal status, and approved trade paths.
- `tests/integration/test_risk_storage.py` should cover append-only risk-decision persistence and list/query behavior.
- `tests/integration/test_signal_risk_gate.py` should cover the end-to-end handoff from an accepted Phase 2 signal evaluation into a persisted approved or blocked risk decision.

### Validation focus by requirement
- **RISK-01:** Assert deterministic sizing outputs from the same bankroll, signal probability, and exposure snapshot inputs.
- **RISK-02:** Assert that risk rules fail closed and return explicit rule codes for drawdown, cooldown, exposure, and invalid signal states.
- **RISK-03:** Assert that blocked decisions persist rich evidence and can be listed without losing prior decisions.

### Nyquist posture
- Existing pytest infrastructure is sufficient; no separate Wave 0 plan is needed.
- Each plan should carry at least one direct automated command in its `<verify>` blocks.
- The end-to-end risk gate test should verify the contract boundary, not just isolated helper methods.

## Implementation Recommendation

Plan Phase 3 as two slices that match the roadmap:

1. `03-01` should establish the deterministic sizing and exposure-policy core: settings, kill-switch config shape, sizing contracts, Kelly math, and unit coverage for clamp behavior.
2. `03-02` should add kill-switch evaluation, append-only risk-decision persistence, and the signal-to-risk integration path with explicit blocked-decision evidence.

That split keeps the first plan focused on pure deterministic policy and lets the second plan build the auditable gate around real Phase 2 signal outputs. [VERIFIED: .planning/ROADMAP.md]

---
*Phase: 03-risk-and-portfolio-controls*
*Research generated: 2026-04-19*
