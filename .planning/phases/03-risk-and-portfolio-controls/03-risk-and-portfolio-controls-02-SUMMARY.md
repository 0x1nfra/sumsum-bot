---
phase: 03-risk-and-portfolio-controls
plan: 02
subsystem: api
tags: [python, sqlite, risk, signals, pytest]
requires:
  - phase: 03-risk-and-portfolio-controls
    provides: deterministic Kelly sizing and exposure-policy decisions
provides:
  - append-only risk-decision persistence for allowed and blocked outcomes
  - drawdown, cooldown, and unaccepted-signal hard gates
  - signal-to-risk orchestration that links decisions back to stored signal evaluations
affects: [paper-trader, dashboard, audit-trail]
tech-stack:
  added: []
  patterns: [append-only-risk-decisions, kill-switch-gating, signal-to-risk-seam]
key-files:
  created: [tests/integration/test_risk_storage.py, tests/integration/test_signal_risk_gate.py]
  modified: [core/models.py, core/risk_manager.py, core/storage.py, strategies/weather/signal_engine.py]
key-decisions:
  - "Risk decisions stay append-only and link back to the originating signal evaluation row."
  - "Kill switches evaluate before exposure approval, but still preserve proposed stake evidence for blocked decisions."
  - "Phase 3 adds a narrow signal-to-risk seam without changing Phase 2 candidate evaluation semantics."
patterns-established:
  - "Risk gate orchestration consumes stored signal records instead of rerunning NOAA or edge logic."
  - "Blocked risk decisions preserve structured bankroll, exposure, and proposed-vs-allowed stake evidence."
requirements-completed: [RISK-01, RISK-02, RISK-03]
duration: 18min
completed: 2026-04-19
---

# Phase 3 Plan 2: Risk and Portfolio Controls Summary

**Append-only risk-decision storage, kill-switch blocking, and a reusable signal-to-risk gate for accepted weather signals**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-19T13:13:24Z
- **Completed:** 2026-04-19T13:31:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Added a real `risk_decisions` SQLite table plus repository APIs for append-only persistence and listing.
- Extended the risk manager with drawdown, cooldown, and unaccepted-signal gates while preserving proposed stake evidence on blocked paths.
- Added a dedicated signal-to-risk orchestration path that persists allowed and blocked decisions without changing Phase 2 evaluation behavior.

## Task Commits

1. **Plan implementation and integration verification** - `71af010` (feat)

## Files Created/Modified
- `core/models.py` - Added stored signal-evaluation identifiers for risk linkage.
- `core/risk_manager.py` - Added kill-switch evaluation and signal-aware risk gating.
- `core/storage.py` - Added append-only risk-decision persistence and round-trip support.
- `strategies/weather/signal_engine.py` - Added the narrow `evaluate_risk_for_signal(...)` integration seam.
- `tests/integration/test_risk_storage.py` - Added append-only storage verification for allowed and blocked decisions.
- `tests/integration/test_signal_risk_gate.py` - Added end-to-end coverage for allowed, drawdown-blocked, and cooldown-blocked paths.

## Decisions Made
- Preserved the existing Phase 2 signal engine behavior and added a separate risk-evaluation entrypoint instead of mutating `evaluate_candidates()`.
- Kept `signal_evaluation_id` on the shared signal record so persisted risk decisions can point back to their source rows.
- Used structured rule-code arrays and JSON evidence instead of collapsing blocks into a single opaque message.

## Deviations from Plan

None - plan executed as intended in a single implementation pass.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 4 can reuse persisted allowed and blocked risk decisions without reimplementing bankroll policy.
- Operator-facing audit and dashboard work now has a stable storage surface for blocked-trade explanations.

## Self-Check: PASSED
