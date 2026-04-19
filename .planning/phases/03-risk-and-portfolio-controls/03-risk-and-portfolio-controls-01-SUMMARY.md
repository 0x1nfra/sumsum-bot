---
phase: 03-risk-and-portfolio-controls
plan: 01
subsystem: api
tags: [python, sqlite, risk, kelly, pytest]
requires:
  - phase: 02-noaa-signal-engine
    provides: append-only signal evaluations with explicit reason fields
provides:
  - deterministic Kelly sizing with haircut and per-trade cap evidence
  - typed portfolio and risk-decision contracts for Phase 3
  - exposure-policy evaluation over bankroll and per-window headroom
affects: [03-02, paper-trader, risk-gate]
tech-stack:
  added: []
  patterns: [typed-risk-settings, deterministic-kelly-engine, explicit-risk-decision-records]
key-files:
  created: [tests/unit/test_kelly_engine.py, tests/unit/test_risk_manager.py]
  modified: [config/settings.py, config/kill_switches.py, core/models.py, core/kelly_engine.py, core/risk_manager.py, tests/unit/test_settings.py]
key-decisions:
  - "Sizing applies a fixed probability haircut before quarter-Kelly math."
  - "Per-trade cap and minimum-stake checks happen inside the Kelly engine so clamp reasons survive downstream."
  - "Risk policy keeps current-bankroll exposure math separate from peak-bankroll drawdown fields."
patterns-established:
  - "Deterministic sizing pipeline: adjusted probability -> Kelly fraction -> per-trade cap -> minimum stake block."
  - "Risk decisions are first-class records shared across policy and storage boundaries."
requirements-completed: [RISK-01]
duration: 17min
completed: 2026-04-19
---

# Phase 3 Plan 1: Risk and Portfolio Controls Summary

**Deterministic Kelly sizing, typed risk contracts, and portfolio exposure-policy evaluation for accepted weather signals**

## Performance

- **Duration:** 17 min
- **Started:** 2026-04-19T12:56:20Z
- **Completed:** 2026-04-19T13:13:24Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Added explicit Phase 3 risk settings and kill-switch config fields with environment override coverage.
- Introduced immutable portfolio and risk-decision contracts to carry bankroll, stake, and rule-code evidence.
- Replaced Kelly and risk-manager placeholders with deterministic sizing and exposure-policy logic backed by targeted unit tests.

## Task Commits

1. **Plan implementation and unit verification** - `6d3e6c6` (feat)

## Files Created/Modified
- `config/settings.py` - Added typed Kelly, haircut, exposure-cap, and minimum-stake settings.
- `config/kill_switches.py` - Defined the Phase 3 drawdown, cooldown, and unaccepted-signal controls.
- `core/models.py` - Added `PortfolioSnapshot`, `RiskDecisionStatus`, and `RiskDecisionRecord`.
- `core/kelly_engine.py` - Implemented the real Kelly sizing engine with clamp evidence.
- `core/risk_manager.py` - Implemented portfolio headroom evaluation and risk-decision creation.
- `tests/unit/test_settings.py` - Added env override coverage for the risk config surface.
- `tests/unit/test_kelly_engine.py` - Added deterministic Kelly sizing regression tests.
- `tests/unit/test_risk_manager.py` - Added explicit exposure-policy regression tests.

## Decisions Made
- Kept risk thresholds on `ScanSettings` so weather scanning and risk gating share one typed runtime config boundary.
- Treated minimum-stake failures as explicit blocked decisions instead of silent rounding.
- Left drawdown and cooldown execution hooks for the next plan while preserving the fields now.

## Deviations from Plan

None - plan executed as intended in a single implementation pass.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `03-02` can now persist risk decisions against a stable portfolio and sizing vocabulary.
- Accepted Phase 2 signal rows have a deterministic stake proposal path ready for kill-switch and storage integration.

## Self-Check: PASSED
