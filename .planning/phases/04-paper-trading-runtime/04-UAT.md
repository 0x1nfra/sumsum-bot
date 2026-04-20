---
status: testing
phase: 04-paper-trading-runtime
source:
  - 04-paper-trading-runtime-01-SUMMARY.md
  - 04-paper-trading-runtime-02-SUMMARY.md
  - 04-paper-trading-runtime-03-SUMMARY.md
started: 2026-04-20T00:00:00Z
updated: 2026-04-20T00:00:00Z
---

## Current Test

number: 1
name: Cold Start Smoke Test
expected: |
  Kill any running paper-trader process and start the app from scratch. Running the paper CLI from a clean start should boot without errors, initialize storage if needed, and return a valid JSON summary instead of crashing on startup.
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running paper-trader process and start the app from scratch. Running the paper CLI from a clean start should boot without errors, initialize storage if needed, and return a valid JSON summary instead of crashing on startup.
result: pending

### 2. Paper Once Run
expected: Running `paper-once` should execute the paper-only flow end to end, avoid any live-order path, and print a JSON summary with accepted candidates, allowed decisions, entered positions, resolved positions, and bankroll/return metrics.
result: pending

### 3. Open Position Restoration
expected: If an open paper position already exists in SQLite, the next paper runtime run should restore it before the resolution pass instead of losing it or recreating it from scratch.
result: pending

### 4. Fail-Closed Settlement
expected: If a market payload is missing trustworthy terminal resolution data, the runtime should leave the paper position open rather than settling it to the wrong outcome.
result: pending

### 5. Forward-Test Metrics Output
expected: Paper runtime output should include cumulative return, bankroll delta, max drawdown, drawdown recovery, and resolved trade count derived from durable storage history.
result: pending

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps

