# Testing Patterns

**Analysis Date:** 2026-04-17

## Test Framework

**Runner:**
- Not detected.
- Config: Not detected. Files such as `pytest.ini`, `pyproject.toml`, `tox.ini`, `noxfile.py`, `jest.config.*`, `vitest.config.*`, `playwright.config.*`, and `conftest.py` are absent from the repository.

**Assertion Library:**
- Not detected.

**Run Commands:**
```bash
Not detected              # Run all tests
Not detected              # Watch mode
Not detected              # Coverage
```

## Test File Organization

**Location:**
- No test files exist. Patterns such as co-located tests, `tests/`, `spec/`, or integration suites are not present in the current repository.

**Naming:**
- No `*.test.*`, `*.spec.*`, or `test_*.py` files are present.

**Structure:**
```text
No test directory or test file structure exists in the current repository.
```

## Test Structure

**Suite Organization:**
```typescript
Not detected. The repository contains no executable code and no test suites.
```

**Patterns:**
- Setup pattern: Not detected.
- Teardown pattern: Not detected.
- Assertion pattern: Not detected.

## Mocking

**Framework:** Not detected.

**Patterns:**
```typescript
Not detected. No mocking library or fixture system is present.
```

**What to Mock:**
- No project-standard mock boundaries are established.
- The documentation in `docs/prd.md` suggests likely future seams for test doubles:
  - `core/clob_client.py` for Polymarket transport
  - `strategies/weather/noaa_client.py` for NOAA responses
  - `strategies/sports/odds_client.py` for The Odds API responses
  - `core/storage.py` for persistence isolation

**What NOT to Mock:**
- No explicit rule exists today.
- Given the documented backtesting-first workflow in `docs/prd.md`, strategy calculations such as `strategies/weather/edge_calculator.py` and `core/kelly_engine.py` should eventually be exercised with deterministic inputs rather than heavily mocked internals.

## Fixtures and Factories

**Test Data:**
```typescript
Not detected. No fixtures, factories, or sample payloads exist in the repository.
```

**Location:**
- Not applicable. No test support directories are present.

## Coverage

**Requirements:** None enforced.

**View Coverage:**
```bash
Not detected
```

## Test Types

**Unit Tests:**
- Not present.
- The repo documentation indicates good candidate unit-test targets once code exists:
  - `core/kelly_engine.py` for sizing calculations in `docs/prd.md`
  - `strategies/weather/edge_calculator.py` for edge threshold logic in `docs/prd.md`
  - `strategies/sports/comparator.py` for implied probability comparisons in `docs/prd.md`
  - `config/kill_switches.py` for halt thresholds referenced in `docs/prd.md`

**Integration Tests:**
- Not present.
- Likely future integration boundaries, based on `docs/prd.md`, are:
  - Polymarket API and WebSocket interaction via `core/clob_client.py`
  - NOAA forecast ingestion via `strategies/weather/noaa_client.py`
  - Trade persistence via `core/storage.py` and the planned `data/trades.db`

**E2E Tests:**
- Not used.
- No CLI flow, daemon flow, or paper-trading execution harness is implemented yet, even though `main.py` and `paper_trader.py` are planned in `docs/prd.md`.

## Common Patterns

**Async Testing:**
```typescript
Not detected.
```

**Error Testing:**
```typescript
Not detected.
```

## Testing Signals From Documentation

- `docs/prd.md` explicitly states a "backtesting-first methodology" and includes planned modules `core/backtester.py` and `backtest/runner.py`.
- `docs/strategy.md` repeatedly ties strategy rollout to validation gates such as re-backtesting, drawdown halts, and threshold tuning.
- Those documents establish testing intent, but they do not establish an implemented framework, fixture style, command set, or minimum coverage target.

## Coverage Posture

- Current effective coverage is 0% because no application code or tests are present.
- No CI job, pre-commit hook, or local script enforces test execution.
- No regression safety net exists for future implementation work.

## Practical Guidance For First Test Setup

- Add a Python-native test runner alongside the first implementation files, because the planned project layout in `docs/prd.md` is Python-based.
- Keep tests aligned with the planned module boundaries from `docs/prd.md`:
  - put pure calculation tests near or under the corresponding modules for `core/kelly_engine.py`, `strategies/weather/edge_calculator.py`, and `strategies/sports/comparator.py`
  - add integration tests around `core/clob_client.py`, `strategies/weather/noaa_client.py`, `strategies/sports/odds_client.py`, and `core/storage.py`
  - add backtest verification around `core/backtester.py` and `backtest/runner.py`
- Treat risk controls from `docs/prd.md` and `docs/strategy.md` as mandatory test targets, especially reserve capital handling, max exposure caps, consecutive-loss pauses, and drawdown halts.

## Current Testing Posture

- Observed testing framework: none.
- Observed test files: none.
- Observed coverage tooling: none.
- Observed automation hooks: none.
- The repository is documentation-only today, so testing patterns remain entirely unestablished until the first implementation phase creates real code and a test harness.

---

*Testing analysis: 2026-04-17*
