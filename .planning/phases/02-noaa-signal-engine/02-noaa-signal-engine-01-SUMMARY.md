---
phase: 02-noaa-signal-engine
plan: 01
subsystem: api
tags: [python, noaa, weather, sqlite, pytest]
requires: []
provides:
  - curated NOAA city mapping for supported weather markets
  - explicit local-window signal input contracts and persisted candidate fields
  - NOAA points-to-grid forecast retrieval with fail-closed rejection codes
affects: [02-02, signal-engine, weather-evaluation]
tech-stack:
  added: []
  patterns: [typed-settings, curated-location-mapping, fail-closed-noaa-client]
key-files:
  created: [config/weather_locations.py, tests/unit/test_noaa_client.py]
  modified: [config/settings.py, core/models.py, core/storage.py, strategies/weather/noaa_client.py, strategies/weather/scanner.py, strategies/weather/types.py, tests/integration/test_storage.py, tests/unit/test_settings.py]
key-decisions:
  - "Supported NOAA coverage stays explicit and config-backed; unsupported cities raise noaa_city_unsupported."
  - "Forecast freshness is evaluated against the contract window boundary, not wall-clock runtime."
  - "Candidate persistence now carries explicit local market-window fields for downstream signal evaluation."
patterns-established:
  - "Curated city mapping: normalize city names to explicit NOAA lat/lon/timezone entries in config."
  - "NOAA client boundary: validate payload shape before extracting forecast evidence and raise explicit rejection codes."
requirements-completed: [WEAT-01]
duration: 7min
completed: 2026-04-18
---

# Phase 2 Plan 1: NOAA Signal Engine Summary

**Curated NOAA city mapping, explicit contract-window handoff fields, and a fail-closed points-to-grid forecast client for supported weather markets**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-18T11:31:42Z
- **Completed:** 2026-04-18T11:38:30Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments
- Added red-first NOAA contract tests covering supported lookup, overlap evidence, and hard rejection paths.
- Extended settings, storage, and shared weather contracts to preserve explicit local contract-day fields.
- Implemented the NOAA points-to-grid client with explicit stale, unsupported, mismatch, and malformed-payload rejections.

## Task Commits

1. **Task 1: Add NOAA client contract tests and fixture-backed rejection cases** - `b6f662f` (test)
2. **Task 2: Extend settings and define explicit supported-city + signal-input contracts** - `0448825` (feat)
3. **Task 3: Implement the NOAA points and forecast-window client with hard rejection paths** - `8a8e382` (feat)

## Files Created/Modified
- `config/weather_locations.py` - Curated supported-city NOAA lookup table and normalized city-key helper.
- `config/settings.py` - NOAA user agent, timeout, freshness, and minimum-edge config fields.
- `core/models.py` - Shared candidate record fields for contract family and explicit local market windows.
- `core/storage.py` - SQLite persistence and schema migration support for the new candidate handoff fields.
- `strategies/weather/types.py` - Signal input, NOAA forecast dataclasses, and candidate-to-signal helpers.
- `strategies/weather/noaa_client.py` - Real NOAA points/grid client with fail-closed validation and overlap extraction.
- `strategies/weather/scanner.py` - Filter path now preserves the extended candidate handoff fields after rejection.
- `tests/unit/test_noaa_client.py` - Deterministic NOAA contract tests for happy path and rejection paths.
- `tests/unit/test_settings.py` - Settings coverage for NOAA env overrides.
- `tests/integration/test_storage.py` - Storage round-trip coverage for contract family and local-window fields.

## Decisions Made
- Used stdlib `urllib.request` for NOAA access to keep the client dependency-free.
- Kept supported NOAA coverage narrow to the approved fixture cities instead of adding dynamic lookup or coordinate guessing.
- Treated the local contract window as the authoritative Phase 2 handoff for downstream signal work.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed NOAA payload extraction after the points/grid client landed**
- **Found during:** Task 3
- **Issue:** The initial client implementation read NOAA payload roots instead of their nested `properties` blocks, which caused false `noaa_payload_incomplete` failures.
- **Fix:** Corrected the client to validate and read nested `properties` payloads before extracting URLs and forecast layers.
- **Files modified:** `strategies/weather/noaa_client.py`
- **Verification:** `uv run --extra dev pytest tests/unit/test_noaa_client.py -q`
- **Committed in:** `8a8e382`

**2. [Rule 1 - Bug] Fixed downstream scanner rejection handling exposed by the Phase 2 contract changes**
- **Found during:** Task 3
- **Issue:** The rejection branch in `apply_candidate_filters()` returned `None` because of a bad indentation path, which broke existing unit tests.
- **Fix:** Restored the explicit rejected `CandidateRecord` return and preserved the new Phase 2 handoff fields through rejected candidates.
- **Files modified:** `strategies/weather/scanner.py`
- **Verification:** `uv run --extra dev pytest tests/unit -q`
- **Committed in:** `8a8e382`

**3. [Rule 1 - Bug] Made NOAA freshness tests deterministic against the contract window**
- **Found during:** Task 3
- **Issue:** The original happy-path and stale-path test timestamps were fixed literals and could become stale depending on runtime date.
- **Fix:** Derived test `updateTime` values from the signal window so the stale-path behavior stays strict while the suite remains deterministic.
- **Files modified:** `tests/unit/test_noaa_client.py`
- **Verification:** `uv run --extra dev pytest tests/unit/test_noaa_client.py -q`
- **Committed in:** `8a8e382`

---

**Total deviations:** 3 auto-fixed (3 bug fixes)
**Impact on plan:** All deviations were correctness fixes directly caused by the new Phase 2 boundary work. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 2 now has a deterministic NOAA lookup boundary and the explicit local-window evidence needed for contract-family signal math.
- Plan `02-02` can consume `WeatherSignalInput` and `NoaaForecastWindow` directly without reparsing titles or raw NOAA payloads.

## Self-Check: PASSED
