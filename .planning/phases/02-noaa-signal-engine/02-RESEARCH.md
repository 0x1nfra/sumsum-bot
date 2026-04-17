# Phase 2: NOAA Signal Engine - Research

**Researched:** 2026-04-18
**Domain:** NOAA/NWS forecast integration, weather-signal derivation, and inspectable signal persistence [CITED: https://www.weather.gov/documentation/services-web-api] [VERIFIED: codebase grep]
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Phase 2 should map supported market locations to NOAA using a curated configuration-backed city mapping table rather than dynamic lookup.
- **D-02:** Location coverage should remain intentionally narrow and explicit in v1 so unsupported or ambiguous locations fail safely instead of being guessed.
- **D-03:** NOAA probability derivation should be contract-family-specific rather than one shared rule for all weather markets.
- **D-04:** Temperature and precipitation markets may use different derivation logic as long as each rule is reproducible and inspectable.
- **D-05:** If NOAA data is incomplete, stale, or does not line up cleanly with the market window, the signal must be hard rejected.
- **D-06:** Hard rejections must retain explicit rejection reasons so weak NOAA inputs never silently become tradable signals.
- **D-07:** Phase 2 should retain a structured signal-evaluation record for both accepted and rejected signals.
- **D-08:** The retained evidence should include the market-to-NOAA mapping used, key forecast inputs, derived probability, market price, computed edge, and the acceptance or rejection reason.

### Claude's Discretion
- Exact schema shape for the structured evaluation record, as long as the retained fields remain inspectable.
- Exact representation of staleness and mismatch rejection codes.
- Exact contract-family derivation formulas, provided they remain consistent with the documented strategy thresholds and are reproducible from stored inputs.

### Deferred Ideas (OUT OF SCOPE)
- Multi-source weather consensus or averaging NOAA with other providers would be a new capability and is deferred beyond Phase 2. The current phase stays NOAA-only to preserve a clean validation baseline.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WEAT-01 | Operator can fetch NOAA forecast data for each candidate weather market using the correct location and resolution window. [VERIFIED: REQUIREMENTS.md] | Use curated city-to-lat/lon mapping, cache `/points`, and fetch `forecastGridData` plus optional `forecastHourly`; preserve local contract-day window explicitly instead of relying on `end_iso` alone. [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://weather-gov.github.io/api/gridpoints] [VERIFIED: codebase grep] |
| WEAT-02 | Operator can calculate the implied weather-side edge versus Polymarket pricing using explicit strategy rules. [VERIFIED: REQUIREMENTS.md] | Implement contract-family evaluators; keep the project's documented edge gate of `noaa_no_probability - polymarket_no_price > 0.10`; treat temperature and precipitation as separate derivation paths. [VERIFIED: docs/prd.md] [VERIFIED: 02-CONTEXT.md] |
| WEAT-03 | Operator can inspect the forecast inputs and computed edge that caused a signal to fire or be rejected. [VERIFIED: REQUIREMENTS.md] | Add a dedicated signal-evaluation persistence model that stores mapping inputs, forecast freshness, overlapping periods, derived probabilities, edge, and rejection reasons for both accepted and rejected outcomes. [VERIFIED: 02-CONTEXT.md] [VERIFIED: codebase grep] |
</phase_requirements>

## Summary

Phase 2 is backend-only work centered on turning approved weather candidates into reproducible NOAA-backed signal evaluations. The official NWS flow is fixed: you cannot query by city name, you must resolve a latitude/longitude through `/points/{lat},{lon}`, then follow the returned forecast URLs, and every request should send a `User-Agent`. [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://www.weather.gov/documentation/services-web-api]

The existing Phase 1 code gives Phase 2 three strong seams: conservative weather normalization in `strategies/weather/normalization.py`, scanner orchestration in `core/market_scanner.py`, and SQLite audit persistence in `core/storage.py`. [VERIFIED: codebase grep] The main planning risk is that the current shared candidate shape loses the exact contract-day window needed for NOAA matching: `WeatherMarketCandidate` parses title dates, but `CandidateRecord` only preserves `resolution_hours`, and the sample fixtures show `end_iso` is not reliably the same thing as the local market day boundary. [VERIFIED: codebase grep]

The planner should structure Phase 2 around three hard responsibilities. First, create a curated location map that turns supported city names into canonical lat/lon and timezone metadata. [VERIFIED: 02-CONTEXT.md] Second, build a NOAA client that caches `/points` lookups, fetches grid forecast data, and rejects stale or incomplete data with explicit reason codes. [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://weather-gov.github.io/api/gridpoints] Third, persist one inspectable signal-evaluation record per candidate evaluation instead of trying to overload the Phase 1 accepted/review/rejected bucket tables. [VERIFIED: codebase grep]

**Primary recommendation:** Plan Phase 2 around a `SignalInput -> NOAAWindow -> ContractFamilyEvaluator -> SignalEvaluation -> Storage` pipeline, and treat contract-day preservation plus dedicated evaluation persistence as Wave 0 design constraints. [VERIFIED: codebase grep] [VERIFIED: 02-CONTEXT.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Curated supported-city mapping | API / Backend | — | The mapping is deterministic config and must fail closed for unsupported cities. [VERIFIED: 02-CONTEXT.md] |
| NOAA metadata lookup (`/points`) and forecast retrieval | API / Backend | — | NWS requires coordinate-based discovery before forecast access, plus request headers and cache-aware behavior. [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://www.weather.gov/documentation/services-web-api] |
| Contract-day/time-window normalization | API / Backend | — | The phase must convert market wording into a local window before forecast overlap can be judged correctly. [VERIFIED: codebase grep] |
| Signal evaluation persistence | Database / Storage | API / Backend | Evaluation details need durable audit records, but the backend owns schema creation and writes. [VERIFIED: 02-CONTEXT.md] [VERIFIED: codebase grep] |
| Operator inspection of accepted/rejected signals | Database / Storage | API / Backend | The operator requirement is durability plus later retrieval, not just in-memory scoring. [VERIFIED: REQUIREMENTS.md] [VERIFIED: codebase grep] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`dataclasses`, `json`, `sqlite3`, `zoneinfo`, `urllib.request`) | Python `>=3.11` from project metadata [VERIFIED: pyproject.toml] | Preserve the repo's existing no-runtime-dependency posture for models, storage, timezone handling, and fallback HTTP. [VERIFIED: codebase grep] | Phase 1 already uses dataclasses and `sqlite3`, so Phase 2 should extend the established style instead of replacing it. [VERIFIED: codebase grep] |
| `httpx` | `0.28.1` published 2024-12-06 [VERIFIED: PyPI JSON] | NOAA client transport with shared headers, client reuse, and explicit timeouts. [CITED: https://github.com/encode/httpx/blob/master/docs/advanced/clients.md] [CITED: https://github.com/encode/httpx/blob/master/docs/advanced/timeouts.md] | It gives a clean way to set the required `User-Agent` and a default timeout on a reusable client. [CITED: https://github.com/encode/httpx/blob/master/docs/advanced/clients.md] [CITED: https://github.com/encode/httpx/blob/master/docs/advanced/timeouts.md] |
| `pytest` | `8.4.2` pinned in the repo lockfile, published 2025-09-04 [VERIFIED: uv.lock] | Existing test framework. [VERIFIED: pyproject.toml] | Phase 1 already uses pytest layout and config; Phase 2 should extend that test harness. [VERIFIED: codebase grep] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest-httpx` | `0.36.2` published 2026-04-09 [VERIFIED: PyPI JSON] | Mock NOAA HTTP calls deterministically in unit and integration tests. [CITED: https://github.com/colin-b/pytest_httpx/blob/develop/README.md] | Use it if the implementation adopts `httpx`; otherwise fall back to `urllib` monkeypatching. [CITED: https://github.com/colin-b/pytest_httpx/blob/develop/README.md] [ASSUMED] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `httpx` [VERIFIED: PyPI JSON] | stdlib `urllib.request` | `urllib` keeps dependencies lower, but `httpx` is cleaner for shared headers, timeouts, and test mocks. [CITED: https://github.com/encode/httpx/blob/master/docs/advanced/clients.md] [CITED: https://github.com/encode/httpx/blob/master/docs/advanced/timeouts.md] |
| `pytest-httpx` [VERIFIED: PyPI JSON] | `pytest` monkeypatch around `urllib` [VERIFIED: pyproject.toml] | The stdlib path avoids a new dev dependency, but fixtures become more verbose and less expressive for multi-request NOAA flows. [VERIFIED: pyproject.toml] [ASSUMED] |

**Installation:** [VERIFIED: codebase grep]
```bash
uv add httpx
uv add --dev pytest-httpx
```

**Version verification:** `httpx 0.28.1` and `pytest-httpx 0.36.2` were verified against the live PyPI JSON API on 2026-04-18. [VERIFIED: PyPI JSON]

## Architecture Patterns

### System Architecture Diagram

This flow matches the current repo boundaries plus the official NWS points-to-gridpoint discovery model. [VERIFIED: codebase grep] [CITED: https://weather-gov.github.io/api/general-faqs]

```text
approved weather candidate
    |
    v
signal input builder
  - canonical city key
  - contract family
  - threshold
  - local contract date/window
    |
    v
noaa client
  - lookup cached /points(lat,lon)
  - fetch forecastGridData
  - optionally fetch forecast/hourly snapshot
    |
    v
window overlap normalizer
  - expand validTime intervals
  - intersect with local market window
  - reject stale/incomplete coverage
    |
    +--> temperature evaluator
    |     -> derived yes/no probability
    |
    +--> precipitation evaluator
          -> derived yes/no probability
    |
    v
edge calculator
  - compare derived no-probability vs market no-price
  - apply configured minimum edge
    |
    v
signal evaluation persistence
  - accepted + rejected
  - mapping and forecast evidence
  - explicit reason codes
```

### Recommended Project Structure
```text
config/
  settings.py              # extend with NOAA and signal thresholds
  weather_locations.py     # curated supported-city mapping
core/
  models.py                # extend shared candidate/signal vocab where needed
  storage.py               # add signal-evaluation persistence
strategies/weather/
  noaa_client.py           # points/grid forecast retrieval + caching
  edge_calculator.py       # contract-family evaluators and edge math
  signal_engine.py         # candidate -> signal evaluation orchestration
  types.py                 # signal input/output dataclasses
tests/
  unit/test_noaa_client.py
  unit/test_weather_edge_calculator.py
  integration/test_signal_storage.py
  integration/test_noaa_signal_engine.py
```

### Pattern 1: Preserve market day separately from market close
**What:** Add a normalized `market_date_local` or `contract_window_local` field instead of relying on `end_iso` or `resolution_hours` alone. [VERIFIED: codebase grep]
**When to use:** For every Phase 2 signal evaluation. [VERIFIED: 02-CONTEXT.md]
**Why:** The current normalized candidate keeps only `resolution_hours` downstream, while the fixtures show titles such as "on April 18" paired with `end_iso` values that are not the local end of day for the named city. [VERIFIED: codebase grep]
**Example:**
```python
# Source: repo normalization + fixture evidence
@dataclass(frozen=True)
class WeatherSignalInput:
    market_id: str
    contract_family: str
    location_key: str
    threshold: float | None
    no_price: float
    market_date_local: date
    market_window_start_local: datetime
    market_window_end_local: datetime
```

### Pattern 2: Cache `/points`, not city strings
**What:** Use a curated location table that maps supported market locations to lat/lon/timezone, then cache the `/points` response because grid mappings change infrequently. [CITED: https://weather-gov.github.io/api/general-faqs] [VERIFIED: 02-CONTEXT.md]
**When to use:** For every supported city in v1. [VERIFIED: 02-CONTEXT.md]
**Example:**
```python
# Source: https://weather-gov.github.io/api/general-faqs
with httpx.Client(
    headers={"User-Agent": "(sumsum-bot, contact@example.com)"},
    timeout=10.0,
) as client:
    points = client.get(f"https://api.weather.gov/points/{lat},{lon}")
    points.raise_for_status()
    forecast_grid_url = points.json()["properties"]["forecastGridData"]
```

### Pattern 3: Expand NOAA `validTime` intervals before scoring
**What:** `forecastGridData` values are interval-based time series, and consecutive equal values may be merged, so the signal engine must intersect those intervals with the market window instead of assuming one row equals one hour. [CITED: https://weather-gov.github.io/api/gridpoints]
**When to use:** For precipitation and temperature scoring against local contract windows. [CITED: https://weather-gov.github.io/api/gridpoints]
**Example:**
```python
# Source: https://weather-gov.github.io/api/gridpoints
def iter_overlapping_values(values, market_start, market_end):
    for point in values:
        start, end = parse_valid_time_interval(point["validTime"])
        if end <= market_start or start >= market_end:
            continue
        yield point
```

### Pattern 4: Contract-family evaluators, not one shared rule
**What:** Implement separate evaluators for temperature and precipitation so each can produce inspectable inputs, probabilities, and rejection reasons. [VERIFIED: 02-CONTEXT.md]
**When to use:** Always; Phase 2 explicitly forbids one shared derivation rule. [VERIFIED: 02-CONTEXT.md]
**Example:**
```python
# Source: 02-CONTEXT.md + docs/prd.md
class SignalEvaluation(NamedTuple):
    weather_yes_probability: float | None
    weather_no_probability: float | None
    edge: float | None
    accepted: bool
    reason_codes: tuple[str, ...]
    evidence: dict[str, object]
```

### Anti-Patterns to Avoid
- **Deriving the NOAA window from `resolution_hours` only:** That drops the local market date and can misalign same-day weather markets. [VERIFIED: codebase grep]
- **Querying NOAA by free-text city names:** NWS explicitly requires lat/lon first and does not provide direct city lookup. [CITED: https://weather-gov.github.io/api/general-faqs]
- **Reusing only `accepted_candidates` / `rejected_candidates` for Phase 2 evidence:** Those bucket tables are latest-state summaries and will not preserve repeated signal evaluations over time. [VERIFIED: codebase grep]
- **Silently soft-failing stale or partial NOAA data:** Phase decisions require hard rejection with stored reason codes. [VERIFIED: 02-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| City-to-NOAA resolution | ad hoc fuzzy city matching against NOAA | curated config-backed location map | The phase explicitly requires narrow supported coverage and safe failure for ambiguity. [VERIFIED: 02-CONTEXT.md] |
| NWS transport policy | per-call manual header/timeout code | one shared NOAA client | NWS requires `User-Agent`, and the API is cache-aware with rate limits. [CITED: https://www.weather.gov/documentation/services-web-api] [CITED: https://weather-gov.github.io/api/general-faqs] |
| Interval alignment | naive "take first period" forecast logic | reusable `validTime` overlap helper | Gridpoint layers are interval series and may merge equal spans. [CITED: https://weather-gov.github.io/api/gridpoints] |
| Audit persistence | packing signal details into a single reason string | structured signal-evaluation row with JSON evidence fields | WEAT-03 and Phase 2 decisions require later inspection of inputs and outcomes. [VERIFIED: REQUIREMENTS.md] [VERIFIED: 02-CONTEXT.md] |

**Key insight:** The hard part of Phase 2 is not HTTP transport; it is preserving enough normalized market context to compare the right NOAA interval against the right contract family and then storing that decision transparently. [VERIFIED: codebase grep] [VERIFIED: 02-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: The current shared candidate model drops the contract window you need
**What goes wrong:** Phase 2 tries to operate on `CandidateRecord` alone and discovers that only `resolution_hours` survived from normalization. [VERIFIED: codebase grep]
**Why it happens:** `WeatherMarketCandidate` contains `resolution_at`, but `to_candidate_record()` only keeps derived hours, and title month/day information is not persisted anywhere. [VERIFIED: codebase grep]
**How to avoid:** Add a Phase 2 signal-input model or extend shared models to keep `market_date_local` and explicit local window boundaries. [VERIFIED: codebase grep] [ASSUMED]
**Warning signs:** Evaluator code starts reconstructing dates from titles late in the pipeline, or it treats `end_iso` as the settlement window. [VERIFIED: codebase grep]

### Pitfall 2: `end_iso` and local market day are not interchangeable
**What goes wrong:** The planner assumes `end_iso` is the exact contract-day cutoff in the city's local timezone. [VERIFIED: codebase grep]
**Why it happens:** The current fixtures use `end_iso` for scanner filtering, but weather contract wording resolves on a local calendar date such as "on April 18". [VERIFIED: codebase grep]
**How to avoid:** Treat `end_iso` as market-close metadata and derive the local market day from title parsing plus city timezone mapping. [VERIFIED: codebase grep] [ASSUMED]
**Warning signs:** Phoenix or Seattle examples produce windows that end mid-afternoon local time when converted directly from the fixture's UTC timestamp. [VERIFIED: codebase grep]

### Pitfall 3: Misreading NOAA PoP
**What goes wrong:** A precipitation evaluator interprets PoP as rain amount, duration, or area coverage. [CITED: https://www.weather.gov/pdt/glossary] [CITED: https://www.weather.gov/ppg/forecast_terms]
**Why it happens:** PoP is often misunderstood outside NWS documentation. [CITED: https://www.weather.gov/pdt/glossary]
**How to avoid:** Document that PoP is the chance of measurable precipitation at a point during the specified period, then make the evaluator's rule explicit in code and stored evidence. [CITED: https://www.weather.gov/pdt/glossary] [VERIFIED: 02-CONTEXT.md]
**Warning signs:** The signal explanation equates 40% PoP with "rain for 40% of the day" or "40% of the area gets rain." [CITED: https://www.weather.gov/pdt/glossary]

### Pitfall 4: Ignoring cache and freshness signals from NWS
**What goes wrong:** The bot either over-requests the API or scores stale data without noticing. [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://weather-gov.github.io/api/gridpoints]
**Why it happens:** The NWS API exposes `Cache-Control`, `Last-Modified`, and `updateTime`, but they are easy to ignore in an MVP. [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://weather-gov.github.io/api/gridpoints] [VERIFIED: live NWS API sample]
**How to avoid:** Store forecast `updateTime`, optionally `Last-Modified`, and reject evaluations whose freshness falls outside a configured tolerance. [CITED: https://weather-gov.github.io/api/gridpoints] [VERIFIED: 02-CONTEXT.md] [ASSUMED]
**Warning signs:** Two runs score the same market differently with unchanged NOAA `updateTime`, or the client never records freshness metadata. [VERIFIED: live NWS API sample] [ASSUMED]

### Pitfall 5: Bucket tables erase signal history
**What goes wrong:** The latest accepted/rejected state overwrites earlier evaluations, so the operator cannot inspect how a signal evolved over repeated scans. [VERIFIED: codebase grep]
**Why it happens:** Phase 1 bucket tables are keyed by `market_id` and are designed as latest-state summaries, not append-only evaluation history. [VERIFIED: codebase grep]
**How to avoid:** Add a dedicated append-only `signal_evaluations` table keyed by evaluation id or `(scan_run_id, market_id, evaluated_at)`. [VERIFIED: codebase grep] [ASSUMED]
**Warning signs:** Schema design discussions mention only altering `accepted_candidates` / `rejected_candidates` columns. [VERIFIED: codebase grep]

## Code Examples

Verified patterns from official sources:

### Set a default `User-Agent` and timeout on a shared HTTP client
```python
# Source: https://github.com/encode/httpx/blob/master/docs/advanced/clients.md
# Source: https://github.com/encode/httpx/blob/master/docs/advanced/timeouts.md
with httpx.Client(
    headers={"User-Agent": "(sumsum-bot, contact@example.com)"},
    timeout=10.0,
) as client:
    response = client.get("https://api.weather.gov/points/47.6062,-122.3321")
    response.raise_for_status()
```

### Follow the official NWS points-to-forecast flow
```python
# Source: https://weather-gov.github.io/api/general-faqs
points = client.get(f"https://api.weather.gov/points/{lat},{lon}").json()
forecast_grid_url = points["properties"]["forecastGridData"]
forecast_hourly_url = points["properties"]["forecastHourly"]

grid = client.get(forecast_grid_url).json()
hourly = client.get(forecast_hourly_url).json()
```

### Mock NOAA responses with `pytest-httpx`
```python
# Source: https://github.com/colin-b/pytest_httpx/blob/develop/README.md
def test_points_lookup(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://api.weather.gov/points/47.6062,-122.3321",
        json={"properties": {"forecastGridData": "https://api.weather.gov/gridpoints/SEW/125,68"}},
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Legacy `forecast.weather.gov` JSON/DWML integrations [CITED: https://weather-gov.github.io/api/general-faqs] | `api.weather.gov` with `/points` discovery and JSON forecast endpoints is the supported path. [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://www.weather.gov/documentation/services-web-api] | Current official guidance as of 2026-04-18. [CITED: https://weather-gov.github.io/api/general-faqs] | Phase 2 should build on `api.weather.gov` and not design around legacy forecast JSON services. [CITED: https://weather-gov.github.io/api/general-faqs] |
| Assuming `/forecast/hourly` may include past hours [CITED: https://www.weather.gov/documentation/services-web-api] | NWS reports that `/forecast` and `/forecast/hourly` no longer include past data after the 2026-01-07 fix. [CITED: https://www.weather.gov/documentation/services-web-api] | 2026-01-07. [CITED: https://www.weather.gov/documentation/services-web-api] | Freshness checks should still exist, but the client no longer needs a workaround for trimming past hourly periods. [CITED: https://www.weather.gov/documentation/services-web-api] |

**Deprecated/outdated:**
- Designing direct city-name NOAA lookups is outdated for this phase because the public NWS API explicitly requires geocoded coordinates first and does not provide direct city-name lookup. [CITED: https://weather-gov.github.io/api/general-faqs]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Temperature contracts should use a documented proxy-probability rule derived from forecast-vs-threshold margin because the public API research in this session did not verify a direct arbitrary temperature-threshold probability endpoint in `api.weather.gov`. [ASSUMED] | Architecture Patterns / Open Questions | Medium: the planner may overfit a formula that needs later replacement or calibration. |
| A2 | Precipitation YES probability should be derived from overlapping PoP plus QPF confirmation inside the market window, with the exact aggregation rule locked in code and evidence. [ASSUMED] | Common Pitfalls / Open Questions | Medium: a poor proxy can distort edge calculations even if transport and storage are correct. |
| A3 | A dedicated append-only `signal_evaluations` table is preferable to extending only the Phase 1 bucket tables. [ASSUMED] | Common Pitfalls / Standard Stack | Low-Medium: schema shape can still change, but using only bucket tables would likely undercut WEAT-03 auditability. |

## Open Questions

1. **What is the authoritative source of the contract day window for live Polymarket weather markets?**
   - What we know: Fixtures encode titles like "on April 18" and also include `end_iso`, but the UTC timestamp does not line up with the local end of day for several cities. [VERIFIED: codebase grep]
   - What's unclear: Whether live Polymarket payloads expose a separate resolution rule or whether title wording is the only reliable day-window source in practice. [VERIFIED: codebase grep] [ASSUMED]
   - Recommendation: Plan a Wave 0 normalization update that persists explicit `market_date_local` and local window bounds, using title date plus city timezone until a better live-market field is verified. [VERIFIED: codebase grep] [ASSUMED]

2. **What exact probability proxy should Phase 2 lock for temperature threshold markets?**
   - What we know: The project PRD requires explicit edge math and the NWS API exposes temperature layers, but this research did not verify a direct public endpoint for arbitrary threshold-hit probability in the main API flow. [VERIFIED: docs/prd.md] [CITED: https://weather-gov.github.io/api/gridpoints] [ASSUMED]
   - What's unclear: Whether the team wants a deterministic banded proxy, a percentile-style proxy, or a conservative binary pass/fail signal for v1. [ASSUMED]
   - Recommendation: Keep the first Phase 2 implementation conservative and explicitly provisional: use a small, documented banding rule and store all intermediate values so later calibration is possible. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Phase 2 runtime and tests | ✓ [VERIFIED: local command] | `3.13.3` [VERIFIED: local command] | — |
| `uv` | Dependency and test execution in this repo | ✓ [VERIFIED: local command] | `0.9.29` [VERIFIED: local command] | `pip` for installs, but `uv` is already present and matches repo usage. [VERIFIED: local command] |
| SQLite CLI | Storage inspection and manual debugging | ✓ [VERIFIED: local command] | `3.43.2` [VERIFIED: local command] | Python `sqlite3` module is already in use. [VERIFIED: codebase grep] |
| NOAA API (`api.weather.gov`) | Forecast lookup for Phase 2 | ✓ reachable during research [VERIFIED: live NWS API sample] | — | No fallback; NOAA is a locked project data source. [VERIFIED: AGENTS.md] |
| Global `pytest` CLI | Direct test command from shell | ✗ [VERIFIED: local command] | — | `uv run --extra dev pytest` works. [VERIFIED: local command] |
| `httpx` | Recommended NOAA client transport | ✗ installed in current environment [VERIFIED: local command] | Recommended `0.28.1` [VERIFIED: PyPI JSON] | Use stdlib `urllib.request` if Phase 2 avoids new runtime deps. [VERIFIED: codebase grep] [ASSUMED] |
| `pytest-httpx` | Recommended NOAA client HTTP mocking | ✗ installed in current environment [VERIFIED: local command] | Recommended `0.36.2` [VERIFIED: PyPI JSON] | Use `pytest` monkeypatch around stdlib HTTP calls. [ASSUMED] |

**Missing dependencies with no fallback:**
- None. NOAA is reachable and all required local runtime tools are present. [VERIFIED: live NWS API sample] [VERIFIED: local command]

**Missing dependencies with fallback:**
- `httpx` and `pytest-httpx` are not installed yet; the repo can still implement Phase 2 with stdlib HTTP, but the recommended plan should add them if the team wants cleaner client/test ergonomics. [VERIFIED: local command] [ASSUMED]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 8.4.2` via repo dev dependency. [VERIFIED: pyproject.toml] [VERIFIED: uv.lock] |
| Config file | `pyproject.toml`. [VERIFIED: pyproject.toml] |
| Quick run command | `uv run --extra dev pytest tests/unit -q`. [VERIFIED: local command] [ASSUMED] |
| Full suite command | `uv run --extra dev pytest`. [VERIFIED: local command] [ASSUMED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WEAT-01 | Curated city mapping resolves to correct NOAA endpoints and overlapping market window, with hard rejection for stale/misaligned data. [VERIFIED: REQUIREMENTS.md] [VERIFIED: 02-CONTEXT.md] | unit + integration | `uv run --extra dev pytest tests/unit/test_noaa_client.py -q` [ASSUMED] | ❌ Wave 0 [VERIFIED: codebase grep] |
| WEAT-02 | Contract-family evaluator calculates reproducible probabilities and edge using explicit thresholds. [VERIFIED: REQUIREMENTS.md] [VERIFIED: docs/prd.md] | unit | `uv run --extra dev pytest tests/unit/test_weather_edge_calculator.py -q` [ASSUMED] | ❌ Wave 0 [VERIFIED: codebase grep] |
| WEAT-03 | Accepted and rejected evaluations persist inspectable evidence and reasons. [VERIFIED: REQUIREMENTS.md] [VERIFIED: 02-CONTEXT.md] | integration | `uv run --extra dev pytest tests/integration/test_signal_storage.py -q` [ASSUMED] | ❌ Wave 0 [VERIFIED: codebase grep] |

### Sampling Rate
- **Per task commit:** `uv run --extra dev pytest tests/unit -q`. [ASSUMED]
- **Per wave merge:** `uv run --extra dev pytest tests/unit tests/integration -q`. [ASSUMED]
- **Phase gate:** `uv run --extra dev pytest`. [ASSUMED]

### Wave 0 Gaps
- [ ] `tests/unit/test_noaa_client.py` — cover `WEAT-01`. [VERIFIED: codebase grep]
- [ ] `tests/unit/test_weather_edge_calculator.py` — cover `WEAT-02`. [VERIFIED: codebase grep]
- [ ] `tests/integration/test_signal_storage.py` — cover `WEAT-03`. [VERIFIED: codebase grep]
- [ ] `tests/integration/test_noaa_signal_engine.py` — cover end-to-end candidate-to-evaluation flow. [VERIFIED: codebase grep] [ASSUMED]
- [ ] Dev dependency install path for CI/local: `uv sync --extra dev` or `uv run --extra dev pytest`. [VERIFIED: local command]

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no [VERIFIED: REQUIREMENTS.md] | No user auth surface in Phase 2. [VERIFIED: REQUIREMENTS.md] |
| V3 Session Management | no [VERIFIED: REQUIREMENTS.md] | No session surface in Phase 2. [VERIFIED: REQUIREMENTS.md] |
| V4 Access Control | no [VERIFIED: REQUIREMENTS.md] | No multi-user authorization surface in Phase 2. [VERIFIED: REQUIREMENTS.md] |
| V5 Input Validation | yes [VERIFIED: REQUIREMENTS.md] | Validate NOAA payload fields, market mapping inputs, and stored reason codes before scoring/persisting. [CITED: https://www.weather.gov/documentation/services-web-api] [VERIFIED: codebase grep] |
| V6 Cryptography | no [VERIFIED: REQUIREMENTS.md] | HTTPS transport is provided by the HTTP client and NWS endpoint; Phase 2 should not add custom cryptography. [CITED: https://www.weather.gov/documentation/services-web-api] |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed or incomplete NOAA payload leads to wrong signal score | Tampering | Validate required fields, reject incomplete windows, and persist rejection reasons instead of guessing. [VERIFIED: 02-CONTEXT.md] [CITED: https://weather-gov.github.io/api/gridpoints] |
| Overly permissive external URL handling | Spoofing / SSRF | Hardcode `api.weather.gov` base URLs and derive downstream URLs only from vetted `/points` responses. [CITED: https://weather-gov.github.io/api/general-faqs] [ASSUMED] |
| SQL writes lose audit fidelity or allow malformed evidence blobs | Tampering | Keep structured schema with parameterized writes through `sqlite3` and avoid dynamic SQL from untrusted values. [VERIFIED: codebase grep] [ASSUMED] |
| Silent staleness causes bad trades | Integrity / Repudiation | Store `updateTime`/`Last-Modified`, evaluation timestamp, and freshness rejection codes. [CITED: https://weather-gov.github.io/api/gridpoints] [VERIFIED: live NWS API sample] [ASSUMED] |

## Sources

### Primary (HIGH confidence)
- `AGENTS.md` - project scope, NOAA-only constraint, SQLite-first posture. [VERIFIED: codebase grep]
- `.planning/phases/02-noaa-signal-engine/02-CONTEXT.md` - locked Phase 2 decisions and deferred scope. [VERIFIED: codebase grep]
- `.planning/REQUIREMENTS.md` - `WEAT-01`, `WEAT-02`, `WEAT-03`. [VERIFIED: codebase grep]
- `docs/prd.md` - documented weather edge rule and module boundaries. [VERIFIED: codebase grep]
- `strategies/weather/*.py`, `core/storage.py`, `core/models.py`, `config/settings.py` - current implementation seams and risks. [VERIFIED: codebase grep]
- https://www.weather.gov/documentation/services-web-api - official NWS API overview, rate-limit guidance, `User-Agent` requirement, `/points` and forecast flow, and 2026 endpoint updates. [CITED: https://www.weather.gov/documentation/services-web-api]
- https://weather-gov.github.io/api/general-faqs - official NWS FAQ for geocoding, `/points` caching, and cache headers. [CITED: https://weather-gov.github.io/api/general-faqs]
- https://weather-gov.github.io/api/gridpoints - official NWS gridpoint data model, `validTime`, layer list, and freshness semantics. [CITED: https://weather-gov.github.io/api/gridpoints]
- https://www.weather.gov/pdt/glossary and https://www.weather.gov/ppg/forecast_terms - official PoP definition and measurable precipitation threshold. [CITED: https://www.weather.gov/pdt/glossary] [CITED: https://www.weather.gov/ppg/forecast_terms]

### Secondary (MEDIUM confidence)
- PyPI JSON for `httpx` and `pytest-httpx` version verification; `uv.lock` for the repo-pinned `pytest` version and upload timestamp. [VERIFIED: PyPI JSON] [VERIFIED: uv.lock]
- Context7 CLI output for HTTPX client headers/timeouts, pydantic-settings docs lookup, and pytest-httpx mocking examples. [VERIFIED: Context7 CLI]
- Live `api.weather.gov` samples and headers collected during research for `/points`, `/forecast/hourly`, and `/forecastGridData`. [VERIFIED: live NWS API sample]

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - NWS transport and repo test harness are verified, but the project still has a real dependency choice between stdlib HTTP and `httpx`. [VERIFIED: codebase grep] [VERIFIED: PyPI JSON] [CITED: https://github.com/encode/httpx/blob/master/docs/advanced/clients.md]
- Architecture: MEDIUM - The repo seams and NOAA API flow are verified, but the exact temperature-probability proxy remains an explicit assumption. [VERIFIED: codebase grep] [CITED: https://weather-gov.github.io/api/gridpoints] [ASSUMED]
- Pitfalls: HIGH - The current model/schema gaps and NWS API semantics were directly verified from code and official docs. [VERIFIED: codebase grep] [CITED: https://weather-gov.github.io/api/general-faqs] [CITED: https://weather-gov.github.io/api/gridpoints]

**Research date:** 2026-04-18
**Valid until:** 2026-05-18 for repo structure and PyPI versions; re-check NWS service notices within 7 days before implementation if Phase 2 slips. [CITED: https://www.weather.gov/notification/] [ASSUMED]
