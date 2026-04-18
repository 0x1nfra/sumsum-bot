# Phase 2: NOAA Signal Engine - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn Phase 1's approved weather market candidates into NOAA-backed, inspectable weather trade signals. This phase covers location-to-NOAA mapping, forecast retrieval, contract-family-specific probability derivation, edge calculation, and persistence of accepted/rejected signal evaluations. It does not add multi-source weather consensus, bankroll sizing, or paper-trade execution.

</domain>

<decisions>
## Implementation Decisions

### Forecast mapping
- **D-01:** Phase 2 should map supported market locations to NOAA using a curated configuration-backed city mapping table rather than dynamic lookup.
- **D-02:** Location coverage should remain intentionally narrow and explicit in v1 so unsupported or ambiguous locations fail safely instead of being guessed.

### Probability derivation
- **D-03:** NOAA probability derivation should be contract-family-specific rather than one shared rule for all weather markets.
- **D-04:** Temperature and precipitation markets may use different derivation logic as long as each rule is reproducible and inspectable.

### Missing or fuzzy NOAA data
- **D-05:** If NOAA data is incomplete, stale, or does not line up cleanly with the market window, the signal must be hard rejected.
- **D-06:** Hard rejections must retain explicit rejection reasons so weak NOAA inputs never silently become tradable signals.

### Signal evidence retention
- **D-07:** Phase 2 should retain a structured signal-evaluation record for both accepted and rejected signals.
- **D-08:** The retained evidence should include the market-to-NOAA mapping used, key forecast inputs, derived probability, market price, computed edge, and the acceptance or rejection reason.

### the agent's Discretion
- Exact schema shape for the structured evaluation record, as long as the retained fields remain inspectable.
- Exact representation of staleness and mismatch rejection codes.
- Exact contract-family derivation formulas, provided they remain consistent with the documented strategy thresholds and are reproducible from stored inputs.

</decisions>

<specifics>
## Specific Ideas

- The supported NOAA mapping should start from a maintained city mapping table rather than free-text lookup.
- Probability derivation should reflect how each contract family resolves instead of forcing one rule across all weather markets.
- Evidence retention should be audit-friendly but stop short of storing a full raw NOAA payload for every signal in Phase 2.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Defines Phase 2 goal, success criteria, and the three plan slices for NOAA client/mapping, edge rules, and signal persistence.
- `.planning/PROJECT.md` — Defines the weather-only scope, NOAA-first data constraint, small-bankroll posture, and paper-trading-first validation goal.
- `.planning/REQUIREMENTS.md` — Defines `WEAT-01`, `WEAT-02`, and `WEAT-03`, which Phase 2 must satisfy.
- `.planning/STATE.md` — Confirms the project is at the Phase 2 planning boundary.

### Prior phase decisions
- `.planning/phases/01-market-discovery-foundation/01-CONTEXT.md` — Locks in strict candidate approval boundaries, typed settings, and auditability expectations that Phase 2 must carry forward.

### Product and strategy source material
- `docs/prd.md` §3.1 — Defines the weather strategy, NOAA as the source, and the documented edge framing against Polymarket pricing.
- `docs/prd.md` §4 — Defines the intended module boundaries including `strategies/weather/noaa_client.py` and `strategies/weather/edge_calculator.py`.
- `docs/strategy.md` — Reinforces the weather-first scope and the need for conservative, capital-preserving signal quality.

### Existing implementation context
- `strategies/weather/noaa_client.py` — Current placeholder boundary for NOAA forecast integration that Phase 2 will replace with real behavior.
- `strategies/weather/edge_calculator.py` — Current placeholder boundary for signal math that Phase 2 will implement.
- `strategies/weather/normalization.py` — Existing weather market normalization rules and extracted location/contract-family fields that Phase 2 will build on.
- `strategies/weather/types.py` — Existing weather candidate shape, including resolution timing and normalized weather fields.
- `strategies/weather/scanner.py` — Existing candidate filtering flow and candidate-status semantics that Phase 2 signal evaluation should respect.
- `core/models.py` — Shared candidate vocabulary and status/rejection modeling already used by discovery.
- `core/storage.py` — Existing SQLite-first persistence patterns and audit-oriented scan history structures that Phase 2 can extend.
- `config/settings.py` — Existing typed settings pattern for configurable thresholds and runtime behavior.
- `tests/fixtures/polymarket_weather_markets.json` — Current supported market examples that imply the initial city-based mapping surface for Phase 2.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `strategies/weather/normalization.py`: Already extracts normalized location, contract family, threshold, and resolution timing from supported weather markets.
- `strategies/weather/types.py`: Already defines the weather candidate object that Phase 2 can enrich into signal inputs.
- `core/storage.py`: Already has SQLite-first persistence and audit-oriented patterns for accepted, review, rejected, and per-run records.
- `config/settings.py`: Already establishes the typed-settings pattern that NOAA mapping and threshold settings should follow.

### Established Patterns
- Supported weather coverage is intentionally conservative: approved candidates are explicit, ambiguous ones go to review, and unsupported ones are rejected.
- Runtime configuration lives in typed Python settings rather than scattered constants.
- Auditability matters: accepted and rejected outcomes should both preserve inspectable reasons.

### Integration Points
- Phase 2 should consume approved candidates coming out of `strategies/weather/scanner.py`.
- NOAA retrieval belongs behind `strategies/weather/noaa_client.py`.
- Edge logic belongs behind `strategies/weather/edge_calculator.py`.
- Signal evaluation details should extend the existing SQLite-first storage flow in `core/storage.py`.

</code_context>

<deferred>
## Deferred Ideas

- Multi-source weather consensus or averaging NOAA with other providers would be a new capability and is deferred beyond Phase 2. The current phase stays NOAA-only to preserve a clean validation baseline.

</deferred>

---

*Phase: 02-noaa-signal-engine*
*Context gathered: 2026-04-18*
