# Phase 1: Market Discovery Foundation - Research

**Researched:** 2026-04-17
**Domain:** Python service bootstrap, market-data ingestion, normalization, and SQLite-first persistence
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Phase 1 should create the full MVP skeleton described in the product docs rather than a narrow scanner-only spike.
- **D-02:** The initial repo structure should include the broader Python layout up front, with thin but real modules in their documented locations so later phases build onto stable boundaries.
- **D-03:** Weather-market parsing should use tiered support.
- **D-04:** Fully normalized and clearly mappable markets are approved candidates for downstream phases.
- **D-05:** Partially parsed or unsupported weather markets should still be captured for review, but must not be treated as tradable candidates.
- **D-06:** Scanner thresholds should live in a structured settings model with typed/defaulted fields rather than hardcoded values or ad hoc environment variables.
- **D-07:** Defaults should live in code, with an override path suitable for later environment-based deployment.
- **D-08:** Phase 1 persistence should store approved candidates and rejected candidates with explicit rule-level rejection reasons.
- **D-09:** Raw source payload archiving is not required in Phase 1.

### the agent's Discretion
- Exact Python packaging details within the chosen full skeleton
- Specific library choices for config validation, SQLite access, and CLI ergonomics
- Exact schema and naming for candidate and rejection records, as long as rejection reasons remain inspectable

### Deferred Ideas (OUT OF SCOPE)
- Raw source payload snapshots for every scan
- NOAA signal evaluation
- Kelly sizing, bankroll controls, and trade gating
- Paper execution and dashboard work
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Project bootstrap and entrypoints | API/Backend | Database/Storage | The runtime is a Python worker process with thin CLI scripts. |
| Typed settings and config loading | API/Backend | — | Configuration needs to be centralized before later deployment work. |
| Market candidate persistence | Database/Storage | API/Backend | SQLite is the default state store, but persistence access should stay behind a backend module. |
| Polymarket weather market ingestion | API/Backend | — | Remote API fetching, payload validation, and normalization happen in service code. |
| Candidate filtering and rejection reasoning | API/Backend | Database/Storage | Filtering is domain logic; results and rejection reasons must be persisted. |
| Scan output for operators and downstream phases | API/Backend | Database/Storage | The scanner orchestrates the ingestion/filter/persist flow and produces inspectable outputs. |
</architectural_responsibility_map>

<research_summary>
## Summary

Phase 1 should establish a runnable Python baseline that future phases can extend without reshaping the repository. The strongest pattern for this repo is a thin CLI/runtime layer over explicit domain modules: configuration in `config/`, shared data models and storage in `core/`, weather-specific parsing in `strategies/weather/`, and tests that lock down parsing and filtering behavior before NOAA, sizing, or paper-trading logic arrives.

The implementation should prefer boring, inspectable building blocks. A typed settings layer keeps liquidity, price, and resolution-window thresholds explicit. A SQLite-first repository layer gives later phases durable state while keeping migration to PostgreSQL feasible. Market normalization should be intentionally conservative: fully understood weather contracts become approved candidates, while ambiguous contracts are captured as rejected or review-required records with explicit reasons instead of guessed mappings.

Testing and verification should focus on deterministic seams. Contract-title parsing, threshold extraction, time-window derivation, and filter decisions are the fragile parts of this phase. If those are backed by fixtures and a small scan command that produces structured output, Phase 1 will satisfy `DISC-01` and `DISC-02` while creating stable boundaries for later NOAA, risk, and runtime work.

**Primary recommendation:** Build the full Python skeleton now, but keep behavior narrow: a typed scan pipeline that ingests Polymarket weather markets, normalizes only what is trustworthy, records both approvals and rejections, and exposes a single scan command with deterministic outputs and tests.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Purpose | Why Standard |
|---------|---------|--------------|
| Python | Main runtime | Matches the documented project direction and keeps the worker/runtime simple. |
| `pydantic` + `pydantic-settings` | Typed settings and payload validation | Good fit for environment overrides, defaulted config, and normalizing remote payloads. |
| `sqlalchemy` | SQLite-first persistence abstraction | Keeps schema and repository logic explicit while preserving a migration path beyond SQLite. |
| `httpx` | HTTP client for remote APIs | Straightforward sync/async options and sensible timeout handling for API clients. |
| `pytest` | Test runner | Natural fit for deterministic parsing, filtering, and storage tests in Python. |

### Supporting
| Library | Purpose | When to Use |
|---------|---------|-------------|
| `typer` | CLI entrypoints | Useful for a scan command and inspectable operator-facing CLI surface. |
| `alembic` | Future schema migration support | Optional in Phase 1; helpful once schema evolution starts to matter. |
| `respx` or HTTP mocking fixtures | Remote API simulation in tests | Useful for ingestion tests without real network calls. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `sqlalchemy` | `sqlite3` standard library | Less setup, but weaker abstraction boundary for later PostgreSQL migration. |
| `typer` | `argparse` | Fewer dependencies, but less ergonomic command structure and help output. |
| `pydantic-settings` | Plain environment parsing | Simpler at first, but easier to drift into scattered, untyped config. |
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### System Architecture Diagram

```text
operator command
    |
    v
paper_trader.py / main.py / scan CLI
    |
    v
core.market_scanner
    |
    +--> config.settings -> scanner thresholds and database path
    |
    +--> core.clob_client -> Polymarket weather market payloads
    |
    +--> strategies.weather.scanner
            |
            +--> normalization rules
            +--> support tier classification
            +--> filter evaluation
            |
            +--> core.storage -> accepted candidates
            +--> core.storage -> rejected/review records
    |
    v
structured scan result for operator and later phases
```

### Recommended Project Structure

```text
config/
  settings.py
  kill_switches.py
core/
  clob_client.py
  market_scanner.py
  storage.py
  models.py
strategies/
  weather/
    scanner.py
    normalization.py
    types.py
tests/
  unit/
  integration/
data/
  trades.db
main.py
paper_trader.py
pyproject.toml
```

### Pattern 1: Thin orchestration over domain modules
**What:** Keep entrypoints and scan orchestration small; put parsing, filtering, and persistence into dedicated modules.  
**When to use:** Always for this repo, because later phases will reuse the same scan pipeline.  
**Implication for planning:** Plan tasks should create thin root scripts and move logic into `core/` and `strategies/weather/`.

### Pattern 2: Conservative normalization with explicit unsupported states
**What:** Model approved candidates, rejected candidates, and unsupported/review states explicitly instead of assuming every weather contract is parseable.  
**When to use:** For weather markets where title wording, thresholds, or locations may be ambiguous.  
**Implication for planning:** Persist rejection reasons and normalization status, not just happy-path candidates.

### Pattern 3: Storage behind repository-style methods
**What:** Hide SQLite interactions behind a storage module that exposes domain operations such as saving candidates and scan runs.  
**When to use:** From Phase 1 onward, because later dashboard and paper-trading work should not depend on raw SQL scattered across modules.  
**Implication for planning:** Bootstrap schema and repository methods now, not raw one-off inserts in the scanner.

### Anti-Patterns to Avoid
- **Guessing ambiguous market mappings:** Reject or downgrade to review instead of inventing unsupported NOAA mappings.
- **Hardcoding filter thresholds in scanner code:** Keep liquidity, price ceiling, and resolution window in typed settings.
- **Treating Phase 1 like a one-off spike:** The full skeleton is a locked decision; avoid throwaway scripts that later need replacement.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Typed config loading | ad hoc `os.getenv` calls everywhere | centralized settings model | Prevents silent config drift and missing-default bugs. |
| Persistence abstraction | direct SQL strings in scanner modules | a storage layer with explicit methods | Keeps schema evolution and testing manageable. |
| HTTP client retries/timeouts | hand-written request wrappers in each module | one shared API client policy | Makes feed failure handling consistent. |
| Command parsing | custom `sys.argv` parsing | `typer` or a thin CLI wrapper | Reduces boilerplate and makes operator commands inspectable. |

**Key insight:** Phase 1 should spend complexity budget on domain clarity, not on rebuilding generic config, storage, or CLI primitives.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Contract titles look parseable until they do not
**What goes wrong:** A parser handles a few weather title formats and then silently misclassifies new variants.  
**Why it happens:** Weather contracts encode location, threshold, units, and resolution windows in human phrasing, not a stable schema.  
**How to avoid:** Use support tiers, require explicit extracted fields for approved candidates, and store exact rejection reasons for everything else.  
**Warning signs:** New fixtures require regex exceptions, or approved candidates are missing one of location, threshold, side, or resolution time.

### Pitfall 2: Filter rules become entangled with normalization logic
**What goes wrong:** Price, liquidity, and resolution-window checks are embedded inside the parser, making future strategy work harder to audit.  
**Why it happens:** It is faster to write one pipeline function than clear domain stages.  
**How to avoid:** Separate normalization output from filter evaluation; persist both candidate state and filter reasons.  
**Warning signs:** The same function both parses titles and decides tradability.

### Pitfall 3: SQLite choices leak into the rest of the codebase
**What goes wrong:** Future PostgreSQL readiness is lost because the scanner writes raw SQLite-specific SQL or file paths directly.  
**Why it happens:** The first implementation optimizes for speed and forgets the documented migration path.  
**How to avoid:** Keep database path and engine wiring in `config` and `core/storage.py`, and expose repository methods to callers.  
**Warning signs:** Scanner modules import `sqlite3` directly or construct `data/trades.db` paths themselves.

### Pitfall 4: No verification harness is created with the bootstrap
**What goes wrong:** The project gets a skeleton and scanner code but no repeatable way to prove parsing/filter behavior.  
**Why it happens:** Bootstrap work is often treated as setup-only instead of execution-critical.  
**How to avoid:** Add `pytest`, representative fixtures, and at least one scan-path integration test in Phase 1.  
**Warning signs:** The plan mentions tests only as a later follow-up.
</common_pitfalls>

<validation_architecture>
## Validation Architecture

Phase 1 can be validated without live trading if the scan pipeline is deterministic under fixture-driven tests. The validation contract should include:

- Unit tests for typed settings defaults and override parsing.
- Unit tests for weather-market normalization covering approved, review-required, and rejected title examples.
- Unit tests for filter rules enforcing liquidity, price ceiling, and resolution-window thresholds from config.
- Integration tests for the scan pipeline using mocked Polymarket payloads and a temporary SQLite database.
- A CLI-level verification command that runs a scan against fixture data and prints structured results suitable for later operator inspection.

The first wave of work should also create the test harness itself so later phases inherit a stable verification path instead of retrofitting one after business logic expands.
</validation_architecture>

<open_questions>
## Open Questions (RESOLVED)

1. **Polymarket client choice**
   - Decision: Phase 1 should use a public market-discovery adapter in `core/clob_client.py`, with the first implementation shaped around a Gamma-style discovery payload and fixture-backed tests.
   - Why: The scanner needs stable discovery behavior more than exchange-execution features in this phase, and an adapter boundary keeps transport choice reversible if payload details change during execution.

2. **Initial supported weather-market scope**
   - Decision: Fully supported markets in Phase 1 should start with temperature-threshold and precipitation-style contracts that can be mapped cleanly to a location, threshold, and resolution window.
   - Why: This satisfies the tiered-support decision without guessing through ambiguous or niche weather contract language.

3. **Migration-tooling decision**
   - Decision: Phase 1 should defer dedicated migration tooling and instead bootstrap schema creation through the storage layer while keeping the database contract isolated for later PostgreSQL and migration adoption.
   - Why: The schema is still small, but the storage boundary must be real now so migration tooling can be introduced later without rewriting scanner logic.
</open_questions>

<sources>
## Sources

### Primary
- `AGENTS.md` - workflow and project constraints
- `.planning/ROADMAP.md` - phase goal, success criteria, and plan count
- `.planning/REQUIREMENTS.md` - `DISC-01` and `DISC-02`
- `.planning/phases/01-market-discovery-foundation/01-CONTEXT.md` - locked decisions and deferred scope
- `docs/prd.md` - proposed module layout and weather strategy inputs
- `docs/strategy.md` - weather-first prioritization and bankroll context

### Secondary
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/STACK.md`
- `.planning/codebase/INTEGRATIONS.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/codebase/CONVENTIONS.md`
- `.planning/codebase/TESTING.md`
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: Python worker bootstrap, typed config, SQLite-first persistence
- Ecosystem: settings validation, HTTP client, storage layer, test harness
- Patterns: conservative normalization, thin orchestration, repository persistence
- Pitfalls: ambiguous contract parsing, config drift, leaky SQLite coupling, missing verification

**Confidence breakdown:**
- Standard stack: HIGH - aligns directly with documented Python and SQLite constraints
- Architecture: HIGH - follows the repo's explicit planned package boundaries
- Pitfalls: HIGH - derived from current repository concerns and phase-specific ambiguity
- Validation: HIGH - deterministic parsing/filter logic is well suited to fixture-driven tests
