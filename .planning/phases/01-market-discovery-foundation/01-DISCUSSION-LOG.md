# Phase 1: Market Discovery Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-17
**Phase:** 1-Market Discovery Foundation
**Areas discussed:** Bootstrap shape, Market normalization strictness, Filter configuration model, Persistence and scanner outputs

---

## Bootstrap shape

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal scanner slice | Build only the pieces needed to run one weather scan end to end. | |
| Full MVP skeleton | Create the broader app layout from `docs/prd.md` now, even if some modules are thin placeholders. | ✓ |
| Hybrid foundation | Create only Phase 1 modules now, but choose boundaries that match the longer-term weather-first architecture. | |

**User's choice:** Full MVP skeleton
**Notes:** The user chose to scaffold the broader architecture up front instead of starting from a narrow spike.

---

## Market normalization strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Narrow and strict | Support only a small set of clearly mappable weather contracts and reject all ambiguity. | |
| Broad first pass | Heuristically parse most weather markets now and tighten later. | |
| Tiered support | Approve fully parsed markets for downstream use while recording partial/unsupported markets separately for review. | ✓ |

**User's choice:** Tiered support
**Notes:** The user wants safe downstream candidates plus visibility into unsupported or partially parsed weather contracts.

---

## Filter configuration model

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded defaults | Keep thresholds directly in code for now. | |
| Env-var driven | Configure main thresholds through environment variables. | |
| Structured settings model | Create a typed/defaulted settings layer with scanner thresholds and override support. | ✓ |

**User's choice:** Structured settings model
**Notes:** The user wants configuration foundations established in Phase 1 rather than scattered threshold management.

---

## Persistence and scanner outputs

| Option | Description | Selected |
|--------|-------------|----------|
| Candidates only | Persist only approved normalized candidates. | |
| Candidates + rejection reasons | Persist approved and rejected candidates with clear rule-level rejection reasons. | ✓ |
| Full scan audit trail | Persist approved/rejected candidates plus raw payload snapshots and scan events. | |

**User's choice:** Candidates + rejection reasons
**Notes:** The user wants auditability for filtering behavior without taking on full raw-payload archiving in Phase 1.

---

## the agent's Discretion

- Exact tool/library choices for config, SQLite, and CLI scaffolding
- Exact module stub depth inside the selected full skeleton

## Deferred Ideas

- Full raw payload snapshot storage for every scan run
