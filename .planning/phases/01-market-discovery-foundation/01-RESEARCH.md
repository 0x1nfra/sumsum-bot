# Phase 1: Market Discovery Foundation - Research

**Researched:** 2026-04-17
**Domain:** Python weather-market discovery foundation for a docs-only Polymarket bot repo
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Project foundation
- **D-01:** Phase 1 should create the full MVP skeleton described in the product docs rather than a narrow scanner-only spike.
- **D-02:** The initial repo structure should include the broader Python layout up front, with thin but real modules in their documented locations so later phases build onto stable boundaries.

### Market normalization
- **D-03:** Weather-market parsing should use tiered support.
- **D-04:** Fully normalized and clearly mappable markets are approved candidates for downstream phases.
- **D-05:** Partially parsed or unsupported weather markets should still be captured for review, but must not be treated as tradable candidates.

### Configuration model
- **D-06:** Scanner thresholds should live in a structured settings model with typed/defaulted fields rather than hardcoded values or ad hoc environment variables.
- **D-07:** Defaults should live in code, with an override path suitable for later environment-based deployment.

### Persistence and scanner outputs
- **D-08:** Phase 1 persistence should store approved candidates and rejected candidates with explicit rule-level rejection reasons.
- **D-09:** Raw source payload archiving is not required in Phase 1.

### Claude's Discretion
- Exact Python packaging details within the chosen full skeleton
- Specific library choices for config validation, SQLite access, and CLI ergonomics
- Exact schema and naming for candidate/rejection records, as long as rejection reasons remain inspectable

### Deferred Ideas (OUT OF SCOPE)
- Raw source payload snapshots for every scan were considered, but deferred beyond Phase 1.
- No additional out-of-scope capabilities were added during discussion.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DISC-01 | Operator can continuously scan active Polymarket weather markets relevant to the configured weather strategy. [VERIFIED: repo docs] | Use a Gamma-ingestion scanner with deterministic normalization tiers, client-side weather identification, and a Typer CLI/runtime entrypoint. [CITED: https://docs.polymarket.com/quickstart] |
| DISC-02 | Operator can filter candidate markets by configurable liquidity, price ceiling, and time-to-resolution rules. [VERIFIED: repo docs] | Use typed settings plus persisted acceptance/rejection records with explicit rule names and threshold values. [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- The repo is currently documentation-only; no executable runtime, manifest, lockfile, tests, or code directories are checked in. [VERIFIED: repo docs]
- Weather is the only in-scope strategy for v1 and this phase must not expand into BTC, sports, NOAA signal evaluation, risk sizing, or paper execution. [VERIFIED: repo docs]
- Storage must be SQLite-first with a PostgreSQL-ready design. [VERIFIED: repo docs]
- The documented target layout is the `core/`, `strategies/weather/`, `config/`, `data/`, `backtest/`, `main.py`, and `paper_trader.py` structure from `docs/prd.md`; new code should align to those boundaries. [VERIFIED: repo docs]
- Root entrypoints should stay thin and reusable logic should live in `core/`, `strategies/`, and `config/`. [VERIFIED: repo docs]
- Current naming guidance is lowercase package directories and `snake_case.py` modules. [VERIFIED: repo docs]

## Summary

Phase 1 should establish a thin but real Python application skeleton that matches the documented repo layout, uses typed settings, persists scan results through a database abstraction that runs on SQLite first, and exposes a single scanner CLI/runtime surface for weather-market discovery only. [VERIFIED: repo docs] [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] [CITED: https://docs.sqlalchemy.org/en/20/core/]

For Polymarket discovery, the lowest-risk Phase 1 path is to use the public Gamma API over plain HTTP rather than introduce authenticated trading clients early. Polymarket's official docs state Gamma is the primary public API for discovering markets and events, and the quickstart shows public `GET /markets` requests with `active`, `closed`, and `limit` parameters. [CITED: https://docs.polymarket.com/api-reference] [CITED: https://docs.polymarket.com/quickstart]

The main implementation risk is not connectivity; it is normalization quality. Current live Gamma payloads include rich market and event fields, but observed payloads do not prove a reliable server-side weather filter, so Phase 1 should assume client-side weather identification plus tiered normalization and auditable rejection reasons. [VERIFIED: live Gamma endpoint] [CITED: https://docs.polymarket.com/api-reference/markets/list-markets] [CITED: https://docs.polymarket.com/api-reference/events/list-events]

**Primary recommendation:** Use `pyproject.toml` + Python 3.12 + `pydantic-settings` + `httpx` + `SQLAlchemy 2.0` + `Typer`, with a scanner pipeline of `Gamma fetch -> weather classification -> normalization tiering -> configurable filters -> accepted/rejected persistence -> JSON/table output`. [VERIFIED: local environment] [VERIFIED: PyPI] [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] [CITED: https://www.python-httpx.org/quickstart/] [CITED: https://docs.sqlalchemy.org/en/20/core/] [CITED: https://typer.tiangolo.com/tutorial/commands/]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Scanner CLI invocation | Browser / Client | API / Backend | Local operator command entry is a client concern, but it delegates immediately into application logic. [ASSUMED] |
| Typed settings loading | API / Backend | — | Runtime configuration should be resolved inside the Python process so tests and later daemons share one configuration contract. [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] |
| Polymarket market/event fetch | API / Backend | — | Gamma is an external HTTP API and Phase 1 discovery logic lives in the Python app, not a browser. [CITED: https://docs.polymarket.com/api-reference] |
| Weather market classification and normalization | API / Backend | — | This is core business logic that transforms raw Polymarket data into supported and review-only candidates. [VERIFIED: repo docs] |
| Candidate filtering by thresholds | API / Backend | Database / Storage | Rule evaluation belongs in code; threshold inputs and scan artifacts belong in durable storage. [VERIFIED: repo docs] |
| Accepted/rejected candidate persistence | Database / Storage | API / Backend | SQLite stores the scan outputs; the Python process owns transaction boundaries and schemas. [VERIFIED: repo docs] [CITED: https://docs.sqlalchemy.org/en/20/core/] |
| Future PostgreSQL portability | Database / Storage | API / Backend | The portability concern is addressed by the storage abstraction and SQLAlchemy dialect support, not by scanner code. [VERIFIED: repo docs] [CITED: https://docs.sqlalchemy.org/en/20/core/] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.3 local runtime, SQLite 3.45.1 via stdlib `sqlite3` [VERIFIED: local environment] | Phase 1 runtime baseline | Python is the documented target language, and the local machine already has a suitable 3.12 runtime with built-in SQLite support. [VERIFIED: repo docs] [VERIFIED: local environment] |
| `pydantic` | 2.13.1, published 2026-04-15 [VERIFIED: PyPI] | Typed domain/config models | Current stable Pydantic provides type-driven validation and serialization, which fits normalization records and filter settings. [CITED: https://docs.pydantic.dev/] |
| `pydantic-settings` | 2.13.1, published 2026-02-19 [VERIFIED: PyPI] | Settings from code defaults plus env or dotenv overrides | Official docs show `BaseSettings` loading env and dotenv values while preserving typed defaults and per-test overrides. [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] |
| `httpx` | 0.28.1, published 2024-12-06 [VERIFIED: PyPI] | Polymarket Gamma HTTP client | Official docs show a simple request/params model plus timeout and exception guidance; that is enough for public Gamma ingestion. [CITED: https://www.python-httpx.org/quickstart/] [CITED: https://www.python-httpx.org/exceptions/] |
| `SQLAlchemy` | 2.0.49, published 2026-04-03 [VERIFIED: PyPI] | SQLite-first persistence abstraction with later PostgreSQL portability | Official docs position SQLAlchemy 2.0 as the current release and document both Core and SQLite dialect support. [CITED: https://docs.sqlalchemy.org/en/20/core/] [CITED: https://docs.sqlalchemy.org/21/dialects/sqlite.html] |
| `Typer` | 0.24.1, published 2026-02-21 [VERIFIED: PyPI] | Scanner CLI and operator-facing commands | Official docs cover multi-command CLIs and first-party test support through `typer.testing.CliRunner`. [CITED: https://typer.tiangolo.com/tutorial/commands/] [CITED: https://typer.tiangolo.com/tutorial/testing/] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 9.0.3, published 2026-04-07 [VERIFIED: PyPI] | Test runner and fixtures | Use for all unit and integration tests; fixtures are the documented default pattern for shared test setup. [CITED: https://docs.pytest.org/en/stable/how-to/fixtures.html] |
| `respx` | 0.23.1, published 2026-04-08 [VERIFIED: PyPI] | HTTPX transport mocking | Use for Gamma client tests so normalization and filtering tests do not depend on live network data. [ASSUMED] |
| `pytest-cov` | 7.1.0, published 2026-03-21 [VERIFIED: PyPI] | Coverage reporting | Use once the first test harness exists. [ASSUMED] |
| `ruff` | 0.15.11, published 2026-04-16 [VERIFIED: PyPI] | Formatting/lint baseline for the first Python code | Use to establish the first real code convention baseline, which the repo currently lacks. [VERIFIED: repo docs] |
| `mypy` | 1.20.1, published 2026-04-13 [VERIFIED: PyPI] | Static type checks on settings/models/storage boundaries | Use once typed models and repositories exist; Phase 1 is the right point to add it because settings and normalization contracts are central. [ASSUMED] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `httpx` + direct Gamma requests [CITED: https://docs.polymarket.com/quickstart] | `py-clob-client` 0.34.6 [VERIFIED: PyPI] | `py-clob-client` is Polymarket's official Python CLOB SDK, but Phase 1 only needs public market discovery and should avoid authenticated trading surface area. [CITED: https://docs.polymarket.com/api-reference/clients-sdks] [ASSUMED] |
| `SQLAlchemy` [CITED: https://docs.sqlalchemy.org/en/20/core/] | stdlib `sqlite3` only [CITED: https://docs.python.org/3.11/library/sqlite3.html] | `sqlite3` is lighter for a spike, but it pushes portability and query organization work into custom code that the roadmap explicitly wants to avoid later. [VERIFIED: repo docs] [ASSUMED] |
| `Typer` [CITED: https://typer.tiangolo.com/tutorial/commands/] | `argparse` in stdlib | `argparse` works, but Typer gives cleaner typed command signatures and official CLI testing support for the operator-facing scan command. [CITED: https://typer.tiangolo.com/tutorial/testing/] [ASSUMED] |

**Installation:** [ASSUMED]
```bash
uv init --package .
uv add pydantic pydantic-settings httpx sqlalchemy typer
uv add --dev pytest respx pytest-cov ruff mypy
```

**Version verification:** [VERIFIED: PyPI]
- `pydantic` 2.13.1 published 2026-04-15
- `pydantic-settings` 2.13.1 published 2026-02-19
- `sqlalchemy` 2.0.49 published 2026-04-03
- `typer` 0.24.1 published 2026-02-21
- `httpx` 0.28.1 published 2024-12-06
- `pytest` 9.0.3 published 2026-04-07
- `respx` 0.23.1 published 2026-04-08

## Architecture Patterns

### System Architecture Diagram

```text
Operator
  |
  v
Typer CLI command (`scan weather`)
  |
  v
Settings loader (`config/settings.py`)
  |
  v
Gamma client (`core/market_scanner.py` or provider adapter)
  |
  v
Raw market/event records
  |
  +--> Weather classifier
  |      |
  |      +--> not weather -> drop from Phase 1 scan set
  |
  v
Weather normalizer
  |
  +--> supported and mappable -> candidate record
  |
  +--> partial or unsupported -> review-only rejection record
  |
  v
Filter engine
  |
  +--> passes liquidity/price/resolution rules -> accepted candidate
  |
  +--> fails any rule -> rejected candidate with rule-level reasons
  |
  v
Storage repository (SQLite via SQLAlchemy)
  |
  +--> accepted_candidates table
  +--> rejected_candidates table
  +--> scan_runs table
  |
  v
CLI output
  +--> human table summary
  +--> machine JSON payload
```

### Recommended Project Structure

```text
config/
  settings.py          # Typed settings and defaults
core/
  market_scanner.py    # Gamma fetch orchestration and scan run entrypoint
  storage.py           # SQLAlchemy engine/session/repository boundary
strategies/
  weather/
    scanner.py         # Weather classification, normalization, filters
    models.py          # Candidate/rejection domain models
data/
  .gitkeep             # SQLite file location
tests/
  unit/
  integration/
main.py                # Thin Typer app bootstrap
pyproject.toml         # Packaging, tool config, pytest/ruff/mypy
```

### Pattern 1: Typed Nested Settings With Code Defaults
**What:** Use one settings object with nested scanner and database sections, code defaults, and env/dotenv override support. [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/]

**When to use:** Use for all Phase 1 thresholds and runtime file paths; do not scatter threshold constants across modules. [VERIFIED: repo docs]

**Example:**
```python
# Source: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScanRules(BaseModel):
    min_liquidity_usd: float = 5000
    max_no_price: float = 0.85
    max_hours_to_resolution: int = 72


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SUMSUM_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///data/trades.db"
    scan_rules: ScanRules = ScanRules()
```

### Pattern 2: Provider Adapter Over Plain HTTP
**What:** Keep Polymarket access behind a small adapter that returns raw dicts or typed transport models; normalize in a separate layer. [CITED: https://www.python-httpx.org/quickstart/] [VERIFIED: repo docs]

**When to use:** Use for Gamma `markets` and `events` fetches in Phase 1; do not mix HTTP calls with parsing and filtering rules in the same function. [ASSUMED]

**Example:**
```python
# Source: https://www.python-httpx.org/quickstart/
import httpx


def fetch_markets(limit: int) -> list[dict]:
    response = httpx.get(
        "https://gamma-api.polymarket.com/markets",
        params={"active": "true", "closed": "false", "limit": limit},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

### Pattern 3: Repository Boundary Over SQLAlchemy
**What:** Use SQLAlchemy for schema and transaction management, but keep Phase 1 repositories simple and scanner-focused. [CITED: https://docs.sqlalchemy.org/en/20/core/] [CITED: https://docs.sqlalchemy.org/21/dialects/sqlite.html]

**When to use:** Use for `scan_runs`, accepted candidates, and rejected candidates; do not expose SQLAlchemy objects directly to CLI presentation code. [ASSUMED]

**Example:**
```python
# Source: https://docs.sqlalchemy.org/en/20/core/
from sqlalchemy import create_engine, insert, MetaData, Table, Column, Integer, String

engine = create_engine("sqlite:///data/trades.db")
metadata = MetaData()

scan_runs = Table(
    "scan_runs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("status", String, nullable=False),
)

metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(insert(scan_runs), [{"status": "completed"}])
```

### Pattern 4: Machine-Readable CLI With Human Summary
**What:** The scan command should always be able to emit JSON for downstream automation and a concise table/summary for the operator. [ASSUMED]

**When to use:** Use on every scan invocation; later phases can consume the same normalized JSON contract. [ASSUMED]

**Recommended output shape:** [ASSUMED]
```json
{
  "run_id": "2026-04-17T04:30:00Z",
  "source": "gamma",
  "filters": {
    "min_liquidity_usd": 5000,
    "max_no_price": 0.85,
    "max_hours_to_resolution": 72
  },
  "accepted": [
    {
      "market_id": "123",
      "question": "Will rainfall in NYC exceed 0.5 inches on April 18?",
      "weather_type": "precipitation",
      "location_hint": "NYC",
      "resolution_time_utc": "2026-04-18T04:00:00Z",
      "no_price": 0.42,
      "liquidity_usd": 8240.11
    }
  ],
  "rejected": [
    {
      "market_id": "456",
      "question": "Will temperature in Boston exceed 75F?",
      "normalization_status": "partial",
      "reasons": ["unsupported_market_wording", "location_not_mappable"]
    }
  ]
}
```

### Anti-Patterns to Avoid

- **Fetching and parsing in the same function:** This makes live-data tests brittle and hides whether failures came from transport, classification, or filtering. [ASSUMED]
- **Using only `sqlite3` helpers with inline SQL everywhere:** This locks query logic to ad hoc strings and weakens the stated SQLite-to-PostgreSQL migration path. [VERIFIED: repo docs] [ASSUMED]
- **Treating every text parse as tradable:** Phase 1 decisions explicitly require unsupported or ambiguous weather markets to be review-only, not candidates. [VERIFIED: repo docs]
- **CLI-only output with no stable JSON contract:** That blocks downstream testing and later phases that need to reuse scan results. [ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Settings loading | Custom `.env` parser and manual type coercion | `pydantic-settings` [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] | Official settings support already handles env/dotenv sources and typed validation. [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] |
| Persistence abstraction | Homegrown SQL wrapper around raw sqlite cursors | `SQLAlchemy 2.0` [CITED: https://docs.sqlalchemy.org/en/20/core/] | This phase needs SQLite now and a clean PostgreSQL path later; SQLAlchemy already provides dialect and transaction handling. [CITED: https://docs.sqlalchemy.org/21/dialects/sqlite.html] |
| CLI argument parsing | Manual `sys.argv` parsing | `Typer` [CITED: https://typer.tiangolo.com/tutorial/commands/] | Typed command signatures and official test support lower the cost of a stable operator CLI. [CITED: https://typer.tiangolo.com/tutorial/testing/] |
| HTTP stubbing in tests | Ad hoc monkeypatches everywhere | `respx` plus pytest fixtures [ASSUMED] [CITED: https://docs.pytest.org/en/stable/how-to/fixtures.html] | Transport-level mocking keeps client tests deterministic and readable. [ASSUMED] |

**Key insight:** Hand-roll domain parsing for weather-market normalization because that is the product's unique logic, but do not hand-roll the configuration, database, CLI, or HTTP-testing infrastructure around it. [VERIFIED: repo docs] [ASSUMED]

## Common Pitfalls

### Pitfall 1: Assuming Gamma Can Server-Filter Weather Reliably
**What goes wrong:** The implementation assumes a query parameter like `category=weather` or `tag_slug=weather` will isolate weather markets, then silently processes unrelated markets. [VERIFIED: live Gamma endpoint]

**Why it happens:** Official docs document `markets` and `events`, but the current public endpoint behavior observed in this session did not prove server-side weather filtering; sampled responses to those parameters still returned unrelated markets. [VERIFIED: live Gamma endpoint] [CITED: https://docs.polymarket.com/api-reference/markets/list-markets] [CITED: https://docs.polymarket.com/api-reference/events/list-events]

**How to avoid:** Treat weather discovery as a client-side classification problem in Phase 1 and persist unsupported records for review. [VERIFIED: repo docs]

**Warning signs:** Accepted candidate set contains non-weather questions or zero accepted rows without any review-only records. [ASSUMED]

### Pitfall 2: Storing Only Accepted Candidates
**What goes wrong:** Operators cannot inspect why a market was excluded, so normalization and filter bugs look like "no opportunities found". [VERIFIED: repo docs]

**Why it happens:** Rejections feel temporary, but D-08 explicitly requires rule-level rejection reasons. [VERIFIED: repo docs]

**How to avoid:** Persist accepted and rejected candidate rows under the same scan run with explicit reason codes and threshold snapshots. [VERIFIED: repo docs] [ASSUMED]

**Warning signs:** Debugging requires rerunning the scan with print statements or live HTTP access. [ASSUMED]

### Pitfall 3: Mixing Discovery With NOAA Mapping Early
**What goes wrong:** Phase 1 grows into a signal engine and blocks planning with premature weather-source coupling. [VERIFIED: repo docs]

**Why it happens:** Weather normalization naturally invites location and forecast mapping, but that is Phase 2 scope. [VERIFIED: repo docs]

**How to avoid:** Limit Phase 1 normalization to what is needed for candidate discovery: market type, contract wording, threshold direction/value, location hint, and resolution window confidence. [ASSUMED]

**Warning signs:** The first scanner plan starts adding NOAA clients, gridpoint lookup, or probability calculations. [VERIFIED: repo docs]

### Pitfall 4: Building a CLI Without a Stable Output Contract
**What goes wrong:** Tests assert console strings instead of behavior, and later phases cannot reuse scan output. [ASSUMED]

**Why it happens:** Human-readable tables are quick to build, but they are not a durable integration surface. [ASSUMED]

**How to avoid:** Define one canonical result object and render it as JSON or table after the scan completes. [ASSUMED]

**Warning signs:** Filtering logic is exercised only through snapshot tests of terminal text. [ASSUMED]

## Code Examples

Verified patterns from official sources:

### HTTP Query Parameters for Gamma
```python
# Source: https://docs.polymarket.com/quickstart
import requests

response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"active": "true", "closed": "false", "limit": 1}
)
markets = response.json()
```

### Typed Settings With Env File Support
```python
# Source: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

### Multiple CLI Commands
```python
# Source: https://typer.tiangolo.com/tutorial/commands/
import typer

app = typer.Typer()


@app.command()
def scan():
    print("scan")


@app.command()
def health():
    print("health")
```

### Pytest Fixture Pattern
```python
# Source: https://docs.pytest.org/en/stable/how-to/fixtures.html
import pytest


@pytest.fixture
def sample_settings():
    return {"max_hours_to_resolution": 72}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 `BaseSettings` inside `pydantic` [CITED: https://docs.pydantic.dev/2.0/migration/] | `BaseSettings` moved to `pydantic-settings` [CITED: https://docs.pydantic.dev/2.0/migration/] | Pydantic 2.0 [CITED: https://docs.pydantic.dev/2.0/migration/] | Phase 1 should depend on `pydantic-settings`, not older Pydantic v1 patterns. [CITED: https://docs.pydantic.dev/2.0/migration/] |
| Raw DB-API scripts for quick SQLite apps [CITED: https://docs.python.org/3.11/library/sqlite3.html] | SQLAlchemy 2.0 typed/Core-first patterns for portable app persistence [CITED: https://docs.sqlalchemy.org/en/20/core/] | Current SQLAlchemy 2.0 series, current release 2.0.49 dated 2026-04-03 [CITED: https://docs.sqlalchemy.org/en/20/core/] | Better fit for the project's SQLite-first, PostgreSQL-ready constraint. [VERIFIED: repo docs] |
| Single-script CLIs with manual parser wiring [ASSUMED] | Typed command apps with testable command boundaries via Typer [CITED: https://typer.tiangolo.com/tutorial/commands/] [CITED: https://typer.tiangolo.com/tutorial/testing/] | Current Typer documentation and release line [VERIFIED: PyPI] | Cleaner scanner command surface and easier CLI verification. [ASSUMED] |

**Deprecated/outdated:**
- `BaseSettings` from `pydantic` itself is outdated for Pydantic 2.x; use `pydantic-settings` instead. [CITED: https://docs.pydantic.dev/2.0/migration/]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `respx` is the best HTTPX mocking companion for this repo's first test harness. | Standard Stack / Don't Hand-Roll | Low; another HTTPX-compatible mocking tool could be swapped without changing Phase 1 architecture. |
| A2 | Typer is the best CLI ergonomics choice versus stdlib `argparse` for this repo. | Standard Stack / Architecture Patterns | Low; the command surface could be implemented with `argparse`, but test ergonomics would be weaker. |
| A3 | The recommended JSON output contract is the right shape for downstream phases. | Architecture Patterns | Medium; planners may need minor field changes, but machine-readable accepted/rejected separation should remain. |

## Open Questions

1. **What live weather-market corpus should seed the first normalization fixtures?**
   - What we know: Gamma public market and event payloads are reachable and richly structured. [VERIFIED: live Gamma endpoint]
   - What's unclear: This session did not capture a guaranteed active weather-market sample from Gamma, and the public search endpoint returned `401 Unauthorized` when queried directly. [VERIFIED: live Gamma endpoint]
   - Recommendation: During implementation, save a small vetted fixture set of actual weather markets before writing the full parser matrix. [ASSUMED]

2. **Should Phase 1 persist one combined candidate table or separate accepted/rejected tables?**
   - What we know: D-08 requires both approved and rejected candidates with inspectable rule-level reasons. [VERIFIED: repo docs]
   - What's unclear: The exact schema split is left to agent discretion. [VERIFIED: repo docs]
   - Recommendation: Prefer separate accepted/rejected tables plus `scan_runs` unless a single-table design materially simplifies downstream querying. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Phase 1 runtime and tests | Yes [VERIFIED: local environment] | 3.12.3 [VERIFIED: local environment] | — |
| `pip` | Package installation | Yes [VERIFIED: local environment] | 24.0 [VERIFIED: local environment] | `uv` |
| `uv` | Recommended package manager/bootstrap | Yes [VERIFIED: local environment] | 0.10.11 [VERIFIED: local environment] | `pip` + virtualenv [ASSUMED] |
| SQLite library via stdlib | Local persistence | Yes [VERIFIED: local environment] | SQLite 3.45.1 [VERIFIED: local environment] | — |
| `sqlite3` shell CLI | Manual DB inspection | No [VERIFIED: local environment] | — | Use Python's `sqlite3` module or SQLAlchemy scripts [CITED: https://docs.python.org/3.11/library/sqlite3.html] |
| Public network access to Gamma docs/API | Polymarket discovery research and future scans | Yes [VERIFIED: live Gamma endpoint] | Current public endpoint [VERIFIED: live Gamma endpoint] | Fixture-based tests only |

**Missing dependencies with no fallback:**
- None for planning. [VERIFIED: local environment]

**Missing dependencies with fallback:**
- `sqlite3` shell CLI is missing, but Python stdlib SQLite is present and sufficient for the Phase 1 app and tests. [VERIFIED: local environment] [CITED: https://docs.python.org/3.11/library/sqlite3.html]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` 9.0.3 [VERIFIED: PyPI] |
| Config file | none - add in Wave 0 via `pyproject.toml` [VERIFIED: repo docs] |
| Quick run command | `pytest tests/unit -x` [ASSUMED] |
| Full suite command | `pytest -x --cov=sumsum_bot --cov-report=term-missing` [ASSUMED] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DISC-01 | Active Polymarket weather scan returns normalized accepted/rejected records from Gamma payloads. [VERIFIED: repo docs] | integration | `pytest tests/integration/test_weather_scan.py -x` [ASSUMED] | No - Wave 0 [VERIFIED: repo docs] |
| DISC-02 | Configurable liquidity, price ceiling, and time-to-resolution filters produce explicit rejection reasons. [VERIFIED: repo docs] | unit | `pytest tests/unit/test_candidate_filters.py -x` [ASSUMED] | No - Wave 0 [VERIFIED: repo docs] |

### Sampling Rate

- **Per task commit:** `pytest tests/unit -x` [ASSUMED]
- **Per wave merge:** `pytest -x` [ASSUMED]
- **Phase gate:** Full suite green before `/gsd-verify-work`. [VERIFIED: workflow config]

### Wave 0 Gaps

- [ ] `pyproject.toml` - define pytest, ruff, and mypy configuration. [VERIFIED: repo docs]
- [ ] `tests/unit/test_candidate_filters.py` - covers DISC-02. [ASSUMED]
- [ ] `tests/unit/test_weather_normalizer.py` - covers tiered support and review-only behavior. [ASSUMED]
- [ ] `tests/integration/test_weather_scan.py` - covers DISC-01 end-to-end scan flow against mocked Gamma responses. [ASSUMED]
- [ ] `tests/conftest.py` - shared settings and fixture data. [ASSUMED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no [VERIFIED: repo docs] | None in Phase 1; Gamma discovery is public. [CITED: https://docs.polymarket.com/api-reference] |
| V3 Session Management | no [VERIFIED: repo docs] | None in Phase 1. [VERIFIED: repo docs] |
| V4 Access Control | no [VERIFIED: repo docs] | None in Phase 1. [VERIFIED: repo docs] |
| V5 Input Validation | yes [VERIFIED: repo docs] | Pydantic models for settings and normalized records; reject malformed or ambiguous market text. [CITED: https://docs.pydantic.dev/] [VERIFIED: repo docs] |
| V6 Cryptography | no [VERIFIED: repo docs] | None in Phase 1 because no credentials or signing flow should be added yet. [VERIFIED: repo docs] |

### Known Threat Patterns for Python + Gamma + SQLite

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Upstream payload shape drift | Tampering | Validate transport payloads before normalization and preserve rejection reasons instead of guessing. [CITED: https://docs.pydantic.dev/] [ASSUMED] |
| Ambiguous market wording treated as tradable | Integrity | Tier supported vs review-only normalization exactly as D-03 to D-05 require. [VERIFIED: repo docs] |
| Stale or inactive markets entering the scan set | Integrity | Fetch only active/non-closed records and re-check active/closed flags in normalization. [CITED: https://docs.polymarket.com/quickstart] [CITED: https://docs.polymarket.com/api-reference/markets/list-markets] |
| Misconfigured thresholds from env | Tampering | Typed settings with defaults and validation on startup. [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/] |
| SQL injection through ad hoc string SQL | Tampering | Use SQLAlchemy statements/repositories instead of string-built SQL. [CITED: https://docs.sqlalchemy.org/en/20/core/] |

## Sources

### Primary (HIGH confidence)

- `docs.polymarket.com/api-reference` - Gamma/Data/CLOB API roles and auth posture. [CITED: https://docs.polymarket.com/api-reference]
- `docs.polymarket.com/quickstart` - public Gamma `markets` request pattern and token discovery example. [CITED: https://docs.polymarket.com/quickstart]
- `docs.polymarket.com/api-reference/markets/list-markets` - market response fields. [CITED: https://docs.polymarket.com/api-reference/markets/list-markets]
- `docs.polymarket.com/api-reference/events/list-events` - event response fields. [CITED: https://docs.polymarket.com/api-reference/events/list-events]
- `pydantic.dev/docs/validation/latest/concepts/pydantic_settings/` - typed settings, env, and dotenv support. [CITED: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/]
- `docs.sqlalchemy.org/en/20/core/` - SQLAlchemy 2.0 Core documentation and release line. [CITED: https://docs.sqlalchemy.org/en/20/core/]
- `docs.sqlalchemy.org/21/dialects/sqlite.html` - SQLite dialect support and behavior notes. [CITED: https://docs.sqlalchemy.org/21/dialects/sqlite.html]
- `www.python-httpx.org/quickstart/` and `www.python-httpx.org/exceptions/` - request patterns, timeout, and exception guidance. [CITED: https://www.python-httpx.org/quickstart/] [CITED: https://www.python-httpx.org/exceptions/]
- `typer.tiangolo.com/tutorial/commands/` and `typer.tiangolo.com/tutorial/testing/` - command organization and test runner support. [CITED: https://typer.tiangolo.com/tutorial/commands/] [CITED: https://typer.tiangolo.com/tutorial/testing/]
- `docs.pytest.org/en/stable/how-to/fixtures.html` - fixture patterns. [CITED: https://docs.pytest.org/en/stable/how-to/fixtures.html]
- Local repo planning docs and AGENTS instructions - scope, constraints, requirements, and current repo posture. [VERIFIED: repo docs]
- Live Gamma endpoint observations and local tool/runtime probes run during this session. [VERIFIED: live Gamma endpoint] [VERIFIED: local environment] [VERIFIED: PyPI]

### Secondary (MEDIUM confidence)

- `docs.python.org/3.11/library/sqlite3.html` - stdlib SQLite DB-API reference used for fallback guidance. [CITED: https://docs.python.org/3.11/library/sqlite3.html]
- `docs.pydantic.dev/2.0/migration/` - Pydantic v2 migration note for `BaseSettings`. [CITED: https://docs.pydantic.dev/2.0/migration/]

### Tertiary (LOW confidence)

- None. All low-confidence recommendations are isolated in the Assumptions Log instead of cited as facts. [VERIFIED: this document]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - core library versions were verified from PyPI and behavior was checked against official docs. [VERIFIED: PyPI] [CITED: https://docs.polymarket.com/api-reference]
- Architecture: MEDIUM - the recommended scanner and storage shapes fit the repo constraints and official docs, but live weather-market fixture availability remains unresolved. [VERIFIED: repo docs] [VERIFIED: live Gamma endpoint]
- Pitfalls: MEDIUM - the biggest failure modes are well supported by repo decisions and observed API behavior, but some CLI/testing ergonomics remain recommendation-level. [VERIFIED: repo docs] [VERIFIED: live Gamma endpoint] [ASSUMED]

**Research date:** 2026-04-17
**Valid until:** 2026-05-17 for library/version guidance; sooner if Polymarket Gamma response behavior changes
