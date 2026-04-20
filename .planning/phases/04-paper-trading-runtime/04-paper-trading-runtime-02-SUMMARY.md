---
phase: 04-paper-trading-runtime
plan: "02"
subsystem: runtime
tags: [python, sqlite, pytest, polymarket, paper-trading]
requires:
  - phase: 04-01
    provides: paper position storage, lifecycle events, and bankroll snapshots
provides:
  - reusable paper runtime orchestration over scan, signal, risk, entry, and settlement
  - fail-closed resolver matrix for Polymarket terminal-state fields
  - paper-once and paper-loop operator CLI entrypoints
affects: [phase-04-plan-03, observability, deployment]
tech-stack:
  added: []
  patterns: [thin cli over runtime service, fail-closed settlement matrix, restart-safe sqlite restoration]
key-files:
  created: [core/paper_runtime.py]
  modified: [core/clob_client.py, main.py, paper_trader.py, tests/integration/test_paper_runtime.py]
key-decisions:
  - "Paper runtime restores open positions from SQLite before running its settlement pass so restarts do not lose lifecycle state."
  - "Settlement inspects Polymarket terminal fields `closed`, `closedTime`, `resolvedBy`, and `umaResolutionStatus` and keeps positions open when any signal is ambiguous."
  - "The operator CLI stays paper-only and delegates all business logic to `PaperRuntime`."
patterns-established:
  - "Paper runtime pass order is restore -> scan -> signal -> risk -> entry -> resolution."
  - "CLI modules reuse shared parser helpers but keep discovery and paper runtime as separate command trees."
requirements-completed: [PAPR-01, PAPR-02]
duration: 4min
completed: 2026-04-20
---

# Phase 04 Plan 02: Paper Trading Runtime Summary

**Paper-only runtime orchestration with restart-safe SQLite restoration, fail-closed Polymarket settlement, and dedicated `paper-once` / `paper-loop` CLI entrypoints**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-20T10:01:36+08:00
- **Completed:** 2026-04-20T10:05:33+08:00
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Added integration coverage for once-mode paper entry, restart restoration, and fail-closed settlement behavior.
- Implemented `PaperRuntime` with ordered restore, scan, signal, risk, entry, and resolution passes plus explicit live-execution blocking.
- Replaced the placeholder `paper_trader.py` wrapper with real `paper-once` and `paper-loop` commands that emit JSON summaries.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add red-first runtime integration coverage for once-mode paper trading and restart-safe restoration** - `8e1434a` (test)
2. **Task 2: Implement reusable paper runtime orchestration with explicit settlement resolver rules** - `8218c61` (feat)
3. **Task 3: Replace the placeholder paper_trader CLI with real paper-once and paper-loop execution paths** - `e7178ab` (feat)

## Files Created/Modified
- `core/paper_runtime.py` - Reusable paper runtime service and settlement resolver matrix.
- `core/clob_client.py` - Terminal-state normalization helper for settlement polling.
- `paper_trader.py` - Real paper runtime CLI with `paper-once` and `paper-loop`.
- `main.py` - Shared CLI argument helpers reused by discovery and paper runtime entrypoints.
- `tests/integration/test_paper_runtime.py` - Real SQLite integration coverage for runtime entry, restoration, and settlement.

## Decisions Made
- Restored positions are loaded from SQLite at the start of each run and carried into the settlement pass before any new positions are resolved.
- Settlement fails closed unless all four Polymarket-oriented terminal fields are present and trustworthy.
- Paper CLI output is JSON-only so later observability work can rely on a stable console contract.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Recovered paper entry pricing from accepted signals instead of risk evidence**
- **Found during:** Task 2 (Implement reusable paper runtime orchestration with explicit settlement resolver rules)
- **Issue:** Phase 3 risk decisions do not persist `no_price`, so immediate paper entry could not rely on risk evidence alone.
- **Fix:** Derived entry pricing from the accepted signal batch keyed by `market_id`, with risk evidence only as fallback.
- **Files modified:** `core/paper_runtime.py`
- **Verification:** `uv run --extra dev pytest tests/integration/test_paper_runtime.py -q`
- **Committed in:** `8218c61` (part of task commit)

**2. [Rule 1 - Bug] Corrected the restoration test contract to match the planned pass order**
- **Found during:** Task 2 (Implement reusable paper runtime orchestration with explicit settlement resolver rules)
- **Issue:** The initial red test incorrectly required `resolution_pass` to run immediately after restoration, which contradicted the plan's ordered scan/signal/risk/entry passes.
- **Fix:** Updated the test to assert only that restoration happens before the resolution pass.
- **Files modified:** `tests/integration/test_paper_runtime.py`
- **Verification:** `uv run --extra dev pytest tests/integration/test_paper_runtime.py -q`
- **Committed in:** `8218c61` (part of task commit)

---

**Total deviations:** 2 auto-fixed (2 bug fixes)
**Impact on plan:** Both fixes were required to keep the runtime aligned with the existing Phase 3 data contract and the plan's ordered pass design.

## Issues Encountered
- `python` was not available directly in the shell path during an ad hoc compile check, so verification stayed on the plan's `uv run` commands.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 04 Plan 03 can build performance and drawdown reporting on top of the persisted runtime events and bankroll snapshots.
- The paper runtime now exposes a stable JSON CLI contract and restart-safe settlement path for later observability and deployment work.

## Self-Check: PASSED
- Verified summary file path exists.
- Verified task commits `8e1434a`, `8218c61`, and `e7178ab` exist in git history.

---
*Phase: 04-paper-trading-runtime*
*Completed: 2026-04-20*
