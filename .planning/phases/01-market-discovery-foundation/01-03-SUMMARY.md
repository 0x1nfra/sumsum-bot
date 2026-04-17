---
phase: 01-market-discovery-foundation
plan: "03"
subsystem: infra
tags: [python, strategies, placeholders, pytest, scaffold]
requires:
  - phase: "01-00"
    provides: "pytest layout contract for documented scaffold verification"
  - phase: "01-01"
    provides: "base strategy package anchors and root scaffold"
provides:
  - "Deferred BTC strategy package boundaries in documented locations"
  - "Deferred sports strategy package boundaries in documented locations"
  - "Layout verification coverage for placeholder strategy paths"
affects: [01-04, 01-05, phase-02, phase-03]
tech-stack:
  added: [python-stdlib]
  patterns: [placeholder-module-boundaries, explicit-not-implemented-guards, layout-contract-verification]
key-files:
  created:
    - strategies/weather/noaa_client.py
    - strategies/weather/edge_calculator.py
    - strategies/btc_5min/__init__.py
    - strategies/btc_5min/signal_engine.py
    - strategies/btc_5min/scanner.py
    - strategies/sports/__init__.py
    - strategies/sports/odds_client.py
    - strategies/sports/comparator.py
    - strategies/sports/scanner.py
  modified:
    - tests/unit/test_project_layout.py
key-decisions:
  - "Deferred strategy modules stay importable but raise NotImplementedError so Phase 1 preserves boundaries without implying active behavior."
  - "The layout test now verifies concrete deferred strategy paths instead of relying only on PRD text references."
patterns-established:
  - "Deferred strategy placeholder pattern: thin classes with explicit out-of-scope guards."
  - "Scaffold verification pattern: documented future paths are locked in with filesystem assertions."
requirements-completed: [DISC-01]
duration: 8 min
completed: 2026-04-17
---

# Phase 1 Plan 03: Deferred Strategy Skeleton Summary

**Deferred BTC and sports strategy package boundaries with explicit Phase 1 guardrails and filesystem-backed layout verification**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-17T08:44:00Z
- **Completed:** 2026-04-17T08:51:52Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- Added the remaining documented weather placeholder boundaries for `noaa_client.py` and `edge_calculator.py`.
- Created thin `strategies/btc_5min/` and `strategies/sports/` packages with placeholder classes that explicitly reject Phase 1 usage.
- Extended the layout verification spec so later phases inherit a hard check that deferred strategy paths already exist.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create thin BTC strategy placeholder modules** - `dc94adb` (feat)
2. **Task 2: Create thin sports strategy placeholder modules** - `efa5058` (test)

## Files Created/Modified
- `strategies/weather/noaa_client.py` - NOAA client boundary placeholder with an explicit Phase 1 guard.
- `strategies/weather/edge_calculator.py` - Weather edge-calculation boundary placeholder with an explicit Phase 1 guard.
- `strategies/btc_5min/__init__.py` - BTC strategy package anchor.
- `strategies/btc_5min/signal_engine.py` - BTC signal-engine placeholder boundary.
- `strategies/btc_5min/scanner.py` - BTC scanner placeholder boundary.
- `strategies/sports/__init__.py` - Sports strategy package anchor.
- `strategies/sports/odds_client.py` - Sports odds-client placeholder boundary.
- `strategies/sports/comparator.py` - Sports comparator placeholder boundary.
- `strategies/sports/scanner.py` - Sports scanner placeholder boundary.
- `tests/unit/test_project_layout.py` - Filesystem assertions covering all deferred strategy placeholder paths.

## Decisions Made
- Used placeholder classes with `NotImplementedError` instead of empty files so imports are stable while out-of-scope behavior stays explicit.
- Kept all deferred modules free of network, trading, or signal logic to satisfy the weather-only Phase 1 boundary.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Reused the isolated pytest runtime for verification**
- **Found during:** Task 2 (Create thin sports strategy placeholder modules)
- **Issue:** The plan-level verification command `python -m pytest tests/unit/test_project_layout.py -q` failed under the active interpreter because `pytest` is not installed globally in this environment.
- **Fix:** Reused the existing `/tmp/sumsum-bot-venv` runtime established by Plan `01-00` to execute the required layout verification.
- **Files modified:** None in the repository
- **Verification:** `/tmp/sumsum-bot-venv/bin/python -m pytest tests/unit/test_project_layout.py -q`
- **Committed in:** No repository changes required

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Verification environment handling stayed external to the repo. Planned deliverables and scope were unchanged.

## Issues Encountered
None

## User Setup Required

None - no external service configuration required.

## Known Stubs
- `strategies/weather/noaa_client.py:13` - `fetch_hourly_forecast` is a deliberate Phase 1 boundary stub until NOAA integration lands in Phase 2.
- `strategies/weather/edge_calculator.py:13` - `calculate` is a deliberate Phase 1 boundary stub until weather signal logic lands in Phase 2.
- `strategies/btc_5min/signal_engine.py:13` - `score_market` is a deliberate deferred-strategy stub because BTC remains out of scope for milestone 1.
- `strategies/btc_5min/scanner.py:13` - `scan` is a deliberate deferred-strategy stub because BTC remains out of scope for milestone 1.
- `strategies/sports/odds_client.py:13` - `fetch_odds` is a deliberate deferred-strategy stub because sports remain out of scope for milestone 1.
- `strategies/sports/comparator.py:13` - `compare` is a deliberate deferred-strategy stub because sports remain out of scope for milestone 1.
- `strategies/sports/scanner.py:13` - `scan` is a deliberate deferred-strategy stub because sports remain out of scope for milestone 1.

## Next Phase Readiness
- The documented strategy tree is now present on disk for weather, BTC, and sports paths, so later phases can implement behavior without reshaping package boundaries.
- Layout verification now catches drift if future work deletes or relocates deferred strategy modules.

## Self-Check: PASSED
- Verified `.planning/phases/01-market-discovery-foundation/01-03-SUMMARY.md` exists on disk.
- Verified task commits `dc94adb` and `efa5058` are present in git history.

---
*Phase: 01-market-discovery-foundation*
*Completed: 2026-04-17*
