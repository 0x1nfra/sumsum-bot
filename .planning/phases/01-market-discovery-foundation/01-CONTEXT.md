# Phase 1: Market Discovery Foundation - Context

**Gathered:** 2026-04-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the initial Python project skeleton, storage/configuration foundation, and weather-market scanning flow so an operator can run a scan against Polymarket weather markets and receive normalized, filterable candidate outputs. This phase covers discovery and persistence foundations only; it does not include NOAA signal evaluation, bankroll sizing, or paper-trade execution.

</domain>

<decisions>
## Implementation Decisions

### Project foundation
- **D-01:** Phase 1 should create the full MVP skeleton described in the product docs rather than a narrow scanner-only spike.
- **D-02:** The initial repo structure should include the broader Python layout up front, with thin but real modules in their documented locations so later phases build onto stable boundaries.

### Market normalization
- **D-03:** Weather-market parsing should use tiered support.
- **D-04:** Fully normalized and clearly mappable markets are approved candidates for downstream phases.
- **D-05:** Partially parsed or unsupported weather markets should still be captured for review, but must not be treated as tradable candidates.

### Configuration model
- **D-06:** Scanner thresholds should live in a structured settings model with typed/defaulted fields rather than hardcoded values or ad hoc environment variables.
- **D-07:** Defaults should live in code, with an override path suitable for later environment-based deployment.

### Persistence and scanner outputs
- **D-08:** Phase 1 persistence should store approved candidates and rejected candidates with explicit rule-level rejection reasons.
- **D-09:** Raw source payload archiving is not required in Phase 1.

### the agent's Discretion
- Exact Python packaging details within the chosen full skeleton
- Specific library choices for config validation, SQLite access, and CLI ergonomics
- Exact schema and naming for candidate/rejection records, as long as rejection reasons remain inspectable

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and delivery
- `.planning/ROADMAP.md` — Defines Phase 1 goal, success criteria, and plan breakdown for Market Discovery Foundation.
- `.planning/PROJECT.md` — Defines the weather-only scope, SQLite-first constraint, paper-trading validation goal, and operational constraints for the first milestone.
- `.planning/REQUIREMENTS.md` — Defines `DISC-01` and `DISC-02`, which this phase must satisfy.
- `.planning/STATE.md` — Confirms current project focus is Phase 1 and records current milestone posture.

### Product and architecture source material
- `docs/prd.md` §3.1 — Defines the weather strategy’s initial entry criteria and scanner expectations.
- `docs/prd.md` §4 — Defines the proposed Python module layout and initial architecture tree to scaffold.
- `docs/strategy.md` — Captures the broader strategy rationale, bankroll constraints, and weather-first prioritization that inform Phase 1 boundaries.

### Current repository analysis
- `.planning/codebase/STRUCTURE.md` — Describes the current docs-only repo and where new runtime code should be added.
- `.planning/codebase/STACK.md` — Confirms there is no executable runtime yet and that Python/SQLite are still planned targets.
- `.planning/codebase/ARCHITECTURE.md` — Summarizes intended layer boundaries between shared `core/`, strategy packages, config, and entrypoints.
- `.planning/codebase/INTEGRATIONS.md` — Lists planned external integrations and current uncertainty around provider/client choices.
- `.planning/codebase/CONCERNS.md` — Highlights bootstrap, normalization, auditability, and live-safety concerns that Phase 1 should account for.
- `.planning/codebase/CONVENTIONS.md` — Establishes current naming guidance and the docs-backed module naming pattern to follow.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/prd.md`: The only concrete source of the intended runtime module layout and initial package boundaries.
- `docs/strategy.md`: The only concrete source of the weather-first prioritization and small-bankroll operating posture.
- `.planning/codebase/*.md`: Existing repo maps that already summarize structure, stack, architecture, integrations, and concerns for downstream use.

### Established Patterns
- The repository is currently documentation-first; no implementation conventions exist beyond the planned Python module names and directory layout documented in `docs/prd.md`.
- Planned runtime naming follows `snake_case.py` module names under lowercase package directories.
- Root-level entrypoints are intended to stay thin, with reusable behavior pushed into `core/`, `strategies/`, and `config/`.

### Integration Points
- New executable code should be introduced at the repo root using the documented `core/`, `strategies/`, `config/`, `data/`, and `backtest/` layout.
- Phase 1 must connect to Polymarket market data for weather market ingestion and to SQLite-backed persistence for candidate/rejection storage.
- Later phases depend on Phase 1 creating stable hooks for NOAA mapping, risk controls, paper execution, and dashboard/logging layers.

</code_context>

<specifics>
## Specific Ideas

- Full MVP skeleton now, not a narrow spike that gets replaced in Phase 2.
- Tiered weather normalization: approved tradable candidates plus a review bucket for partially parsed or unsupported markets.
- Scanner settings should be modeled as a proper structured configuration surface from the beginning.
- Persistence should include both accepted and rejected candidates, with explicit rejection reasons for auditability.

</specifics>

<deferred>
## Deferred Ideas

- Raw source payload snapshots for every scan were considered, but deferred beyond Phase 1.
- No additional out-of-scope capabilities were added during discussion.

</deferred>

---

*Phase: 01-market-discovery-foundation*
*Context gathered: 2026-04-17*
