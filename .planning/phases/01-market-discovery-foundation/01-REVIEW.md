---
phase: 01-market-discovery-foundation
reviewed: 2026-04-17T09:16:41Z
depth: standard
files_reviewed: 36
files_reviewed_list:
  - AGENTS.md
  - .planning/PROJECT.md
  - .planning/phases/01-market-discovery-foundation/01-00-SUMMARY.md
  - .planning/phases/01-market-discovery-foundation/01-01-SUMMARY.md
  - .planning/phases/01-market-discovery-foundation/01-02-SUMMARY.md
  - .planning/phases/01-market-discovery-foundation/01-03-SUMMARY.md
  - .planning/phases/01-market-discovery-foundation/01-04-SUMMARY.md
  - .planning/phases/01-market-discovery-foundation/01-05-SUMMARY.md
  - pyproject.toml
  - main.py
  - paper_trader.py
  - config/__init__.py
  - config/kill_switches.py
  - config/settings.py
  - core/__init__.py
  - core/backtester.py
  - core/clob_client.py
  - core/kelly_engine.py
  - core/market_scanner.py
  - core/models.py
  - core/risk_manager.py
  - core/storage.py
  - core/trade_logger.py
  - backtest/runner.py
  - strategies/weather/normalization.py
  - strategies/weather/scanner.py
  - strategies/weather/types.py
  - strategies/weather/noaa_client.py
  - strategies/weather/edge_calculator.py
  - tests/unit/test_filter_rules.py
  - tests/unit/test_project_layout.py
  - tests/unit/test_settings.py
  - tests/unit/test_weather_normalization.py
  - tests/integration/test_market_scan.py
  - tests/integration/test_polymarket_ingestion.py
  - tests/integration/test_storage.py
findings:
  critical: 0
  warning: 3
  info: 0
  total: 3
status: issues_found
---
# Phase 01: Code Review Report

**Reviewed:** 2026-04-17T09:16:41Z
**Depth:** standard
**Files Reviewed:** 36
**Status:** issues_found

## Summary

Reviewed the phase 01 market-discovery scaffold, storage, normalization, scanner, CLI entrypoints, and the shipped unit/integration tests. The main problems are a bucket-table state regression across repeated scans, a resolution-window filter that can approve markets past the configured cap, and an unvalidated `scan-loop` iteration count that lets the CLI exit successfully without scanning.

## Warnings

### WR-01: Bucket tables keep stale rows when a market changes status across scans

**File:** `core/storage.py:141-159`, `core/storage.py:253-302`
**Issue:** `persist_scan_result()` appends the latest scan to `scan_candidates`, but `_upsert_bucket_candidate()` only inserts into the destination bucket and never removes the same `market_id` from the other bucket tables. A market that was rejected in one run and approved in a later run ends up present in both `rejected_candidates` and `accepted_candidates`. I confirmed this by running two scans with different `max_entry_price` settings; after the second run, `wx-rain-nyc-004` remained in `rejected_candidates` while also appearing in `accepted_candidates`. The current tests only cover a single scan path, so this regression is not caught by `tests/integration/test_market_scan.py:66-86`.
**Fix:**
```python
def _upsert_bucket_candidate(self, connection: sqlite3.Connection, candidate: CandidateRecord) -> None:
    for table in ("accepted_candidates", "review_candidates", "rejected_candidates"):
        connection.execute(f"DELETE FROM {table} WHERE market_id = ?", (candidate.market_id,))

    # then insert into the one correct bucket table for candidate.status
```

### WR-02: Resolution-window filtering undercounts by up to 59 minutes

**File:** `strategies/weather/types.py:27-33`, `strategies/weather/scanner.py:39-45`
**Issue:** `resolution_hours` is computed with floor division on total seconds, then the filter rejects only when `resolution_hours > max_resolution_hours`. That means a market resolving in `72h 59m` is rounded down to `72` and incorrectly passes a `72`-hour cap. I reproduced this directly: a candidate at `now + 72h59m` is reported as `resolution_hours == 72` and stays approved. Existing coverage in `tests/unit/test_filter_rules.py:47-56` checks only whole-hour fixture values, so the boundary bug is untested.
**Fix:**
```python
from math import ceil

hours_until_resolution = delta.total_seconds() / 3600
return max(ceil(hours_until_resolution), 0)
```
Or avoid the lossy conversion entirely and compare timedeltas against the configured hour limit in the filter layer.

### WR-03: `scan-loop --iterations 0` succeeds without running any scans

**File:** `main.py:27-32`, `main.py:120-130`
**Issue:** The CLI accepts zero or negative `--iterations` values. With `--iterations 0`, the loop body never runs, no scan is persisted, and the command still exits `0` after printing `{"iterations": 0, "mode": "scan-loop-summary", "runs": []}`. For an operator-facing discovery command, silently doing nothing is a behavioral footgun. There is also no test coverage for the CLI surface in `main.py` or `paper_trader.py`, so this case is currently unchecked.
**Fix:**
```python
def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("iterations must be >= 1")
    return parsed

scan_loop.add_argument("--iterations", type=positive_int, default=1, ...)
```

---

_Reviewed: 2026-04-17T09:16:41Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
