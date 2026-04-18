---
phase: 02-noaa-signal-engine
plan: 03
subsystem: api
tags: [python, noaa, sqlite, signal-engine, pytest]
requires:
  - phase: 02-noaa-signal-engine
    provides: contract-family NOAA edge evaluation and explicit local-window candidate fields
provides:
  - append-only signal_evaluations audit history
  - NOAA signal orchestration from approved candidates to persisted evaluations
  - accepted and rejected signal records with mapping, forecast, probability, edge, and reason evidence
affects: [paper-trading, signal-persistence, risk-controls]
tech-stack:
  added: []
  patterns: [append-only-audit-history, thin-orchestrator-signal-engine, json-evidence-persistence]
key-files:
  created: [tests/integration/test_signal_storage.py, strategies/weather/signal_engine.py]
  modified: [core/models.py, core/storage.py, tests/integration/test_noaa_signal_engine.py]
key-decisions:
  - "SignalEngine reads only approved CandidateRecord handoff fields and never reparses market titles or raw payloads."
  - "Signal evaluation history stays append-only in a dedicated table instead of reusing Phase 1 latest-state buckets."
  - "Rejected NOAA fetches are persisted as first-class signal records with explicit reason codes."
patterns-established:
  - "Signal persistence boundary: repository methods accept shared SignalEvaluationRecord objects and serialize evidence as JSON."
  - "Signal orchestration boundary: fetch NOAA -> calculate edge -> persist accepted/rejected records in one deterministic pass."
requirements-completed: [WEAT-01, WEAT-03]
duration: 4min
completed: 2026-04-18
---

# Phase 2 Plan 3: NOAA Signal Engine Summary

**Append-only NOAA signal evaluation history with a thin engine that persists accepted and rejected weather signals**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-18T11:48:39Z
- **Completed:** 2026-04-18T11:52:04Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Added red-first integration coverage for append-only signal storage and end-to-end NOAA signal evaluation.
- Introduced shared signal evaluation models plus a dedicated `signal_evaluations` SQLite history table.
- Implemented a real `SignalEngine` that turns approved candidates into persisted accepted/rejected audit rows.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add integration tests for append-only signal storage and end-to-end signal evaluation** - `5d82ea8` (test)
2. **Task 2: Extend shared models and storage with append-only signal evaluation records** - `5e18026` (feat)
3. **Task 3: Implement the signal engine that evaluates approved candidates and persists both outcomes** - `a2ee4eb` (feat)

## Files Created/Modified
- `tests/integration/test_signal_storage.py` - Verifies append-only accepted/rejected evaluation storage and row shape.
- `tests/integration/test_noaa_signal_engine.py` - Exercises the full approved-candidate to persisted-signal flow with deterministic NOAA stubs.
- `core/models.py` - Defines `SignalEvaluationStatus` and `SignalEvaluationRecord`.
- `core/storage.py` - Creates and queries append-only `signal_evaluations` history.
- `strategies/weather/signal_engine.py` - Orchestrates approved candidates through NOAA fetch, edge scoring, and persistence.

## Decisions Made
- Kept `SignalEngine` dependency-injected and storage-backed so tests can run without live NOAA calls.
- Stored signal evidence as JSON to preserve inspectable forecast and decision context without inventing a raw-payload archive.
- Used `decision_reason` as the first rejection code for failures and `edge_threshold_passed` for accepted trades.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected inconsistent accepted-path expectations in the new integration spec**
- **Found during:** Task 2 / Task 3
- **Issue:** The initial accepted-path fixture and assertions implied a negative-edge NO trade while expecting acceptance.
- **Fix:** Reworked the deterministic temperature fixture and expected probability/edge values to match the calculator's threshold bands.
- **Files modified:** `tests/integration/test_noaa_signal_engine.py`
- **Verification:** `uv run --extra dev pytest tests/integration/test_signal_storage.py tests/integration/test_noaa_signal_engine.py -q`
- **Committed in:** `a2ee4eb`

**2. [Rule 1 - Bug] Corrected JSON evidence expectations for persisted signal records**
- **Found during:** Task 3
- **Issue:** The test expected tuple values after JSON persistence even though stored evidence round-trips as JSON arrays.
- **Fix:** Updated the integration assertion to validate JSON-shaped evidence and kept engine evidence serialization deterministic.
- **Files modified:** `tests/integration/test_noaa_signal_engine.py`, `strategies/weather/signal_engine.py`
- **Verification:** `uv run --extra dev pytest tests/integration/test_signal_storage.py tests/integration/test_noaa_signal_engine.py -q`
- **Committed in:** `a2ee4eb`

---

**Total deviations:** 2 auto-fixed (2 bug fixes)
**Impact on plan:** Both fixes were test-contract corrections directly exposed by the plan implementation. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Paper-trading work can now consume a durable accepted/rejected signal history without touching Phase 1 candidate buckets.
- The weather strategy has a stable inspection boundary for mapping, forecast freshness failures, derived probabilities, and edge outcomes.

## Self-Check: PASSED
