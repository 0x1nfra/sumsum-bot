# Codebase Concerns

**Analysis Date:** 2026-04-17

## Tech Debt

**Documentation-only repository:**
- Issue: The repository contains only planning material in `docs/prd.md` and `docs/strategy.md`; none of the proposed implementation paths in `docs/prd.md` such as `core/clob_client.py`, `core/risk_manager.py`, `backtest/runner.py`, or `main.py` exist.
- Files: `docs/prd.md`, `docs/strategy.md`
- Impact: There is no executable baseline for validating architecture, no place to enforce conventions, and no runnable surface for backtesting or paper trading.
- Fix approach: Bootstrap the smallest runnable Python project first with a package root, dependency manifest, entrypoint, and test harness before strategy-specific modules are added.

**Planned architecture is still speculative:**
- Issue: The tree in `docs/prd.md` presents a concrete package layout, but the repo has no implementation proving those boundaries are correct for exchange clients, backtesting, persistence, or risk controls.
- Files: `docs/prd.md`
- Impact: Future work can hard-code against a folder structure that may not survive real execution constraints, causing churn once live adapters and simulations are introduced.
- Fix approach: Treat the `docs/prd.md` tree as a proposal. Lock down only the first working package boundaries after a thin executable spike.

**No engineering control plane exists:**
- Issue: The repo has no `requirements.txt`, `pyproject.toml`, `pytest` config, linter config, formatter config, Makefile, or CI workflow.
- Files: `docs/prd.md`, `docs/strategy.md`
- Impact: Risk, pricing, and execution code can be introduced without repeatable installs, static checks, test gates, or reproducible commands.
- Fix approach: Add project bootstrap files and a minimal CI path before exchange-facing logic is implemented.

**Strategy documents disagree on integration scope:**
- Issue: `docs/prd.md` defines NOAA, Polymarket CLOB, and The Odds API as MVP dependencies, while `docs/strategy.md` additionally assumes Gamma API and Open-Meteo without updating the architecture section.
- Files: `docs/prd.md`, `docs/strategy.md`
- Impact: Implementation can drift into unplanned provider coupling, hidden configuration needs, and unsupported fallback logic.
- Fix approach: Publish one canonical MVP integration list and map each provider to a documented module path before coding begins.

## Known Bugs

**The documented architecture cannot be executed:**
- Symptoms: Importing or running any planned module path from `docs/prd.md` fails because those files are absent.
- Files: `docs/prd.md`
- Trigger: Any attempt to run `main.py`, start a backtest, or build against the proposed module layout.
- Workaround: None in-repo. The current repo state is planning-only.

**Backtesting-first requirement has no implementation path:**
- Symptoms: Both docs emphasize backtesting before risking capital, but there is no dataset layout, fixture format, simulator contract, or example replay script in the repository.
- Files: `docs/prd.md`, `docs/strategy.md`
- Trigger: Any attempt to validate edge thresholds, Kelly sizing, or kill-switch criteria against historical data.
- Workaround: Manual reasoning only, which is not sufficient for automated trading.

## Security Considerations

**Credential management is undefined:**
- Risk: The planned Polymarket trading flow will require credentials, signing material, or wallet access, and `docs/prd.md` defines no secret-loading, storage, rotation, or environment-separation pattern.
- Files: `docs/prd.md`
- Current mitigation: None detected.
- Recommendations: Define a secrets contract before any trading client is written. Keep credentials outside the repo, add a non-secret example config, and isolate order-signing concerns from strategy logic.

**No controls for destructive live trading:**
- Risk: `docs/prd.md` describes automatic order execution, but there is no documented live/paper mode separation, approval flow, dry-run guard, or immutable simulation mode.
- Files: `docs/prd.md`, `docs/strategy.md`
- Current mitigation: Conceptual kill switches in `docs/strategy.md`.
- Recommendations: Require explicit environment-based mode selection and block live execution until the same code path passes paper-trading and replay tests.

**External data trust is too optimistic:**
- Risk: The trading thesis assumes NOAA, Polymarket, and The Odds API provide sufficiently fresh and correctly mapped data, but neither `docs/prd.md` nor `docs/strategy.md` defines freshness checks, schema validation, or stale-feed handling.
- Files: `docs/prd.md`, `docs/strategy.md`
- Current mitigation: None tied to feed integrity.
- Recommendations: Add provider adapters with timestamp validation, schema guards, market-status checks, and rejection paths for stale or partial data.

**Operational auditability is missing:**
- Risk: A trading bot handling real money needs an immutable audit trail for signals, prices, fees, fills, and kill-switch activations, but only a placeholder `core/trade_logger.py` is mentioned in `docs/prd.md`.
- Files: `docs/prd.md`
- Current mitigation: None implemented.
- Recommendations: Define event schemas and durable storage requirements before execution logic is introduced.

**Compliance and venue-policy risk is unaddressed:**
- Risk: The repo plans automated prediction-market trading but does not document jurisdiction assumptions, account eligibility, API terms constraints, or tax/audit record requirements.
- Files: `docs/prd.md`, `docs/strategy.md`
- Current mitigation: None detected.
- Recommendations: Capture operating assumptions and recordkeeping requirements before live trading features are built.

## Performance Bottlenecks

**Small edge thresholds are vulnerable to fee and slippage drag:**
- Problem: `docs/prd.md` uses thin thresholds such as 10% weather edge and 3% sports mispricing while `docs/strategy.md` assumes a bankroll as low as `$50–$100` with small order sizes.
- Files: `docs/prd.md`, `docs/strategy.md`
- Cause: The current plan optimizes for low capital and free data, but it does not document realistic fill quality, fee schedules, or partial-fill behavior.
- Improvement path: Make fees, spread crossing, and slippage first-class inputs in the backtester before any threshold is treated as actionable.

**Polling budgets and free-tier limits will bottleneck signal coverage:**
- Problem: `docs/strategy.md` explicitly cites The Odds API free tier at 500 requests/month while also recommending continuous scanning across sports and multiple strategy classes.
- Files: `docs/strategy.md`
- Cause: The plan assumes broad market coverage without a request budget or cache strategy.
- Improvement path: Allocate request budgets per provider and market type, then reduce scope until the scan loop fits within documented quotas.

**BTC cycle strategy requires low-latency behavior that is not designed yet:**
- Problem: The 5-minute BTC strategy in `docs/prd.md` depends on live order book/trade data and rapid execution, but no event loop, reconnect policy, buffering model, or degradation behavior is specified.
- Files: `docs/prd.md`
- Cause: The architecture section lists modules but not runtime coordination for streaming workloads.
- Improvement path: Design the runtime model early with explicit handling for websocket reconnects, backpressure, and state resynchronization.

**Backtest data collection is a hidden performance and storage problem:**
- Problem: `docs/prd.md` and `docs/strategy.md` rely on backtesting-first validation but do not specify how raw market data, forecast snapshots, or odds histories will be collected and stored.
- Files: `docs/prd.md`, `docs/strategy.md`
- Cause: Profit expectations are documented before the data ingestion and replay pipeline exists.
- Improvement path: Define narrow historical datasets for the first strategy and store raw provider payloads in a replay-friendly format before expanding scope.

## Fragile Areas

**Risk controls are central but only described in prose:**
- Files: `docs/prd.md`, `docs/strategy.md`
- Why fragile: Quarter-Kelly sizing, reserve capital, drawdown halts, max exposure, and kill switches are the main safety system, but there is no precedence order for conflicting rules or behavior for partial fills and concurrent signals.
- Safe modification: Implement risk policy as a single authoritative module before writing strategy-specific execution code, and keep the API narrow enough that every order path must pass through it.
- Test coverage: No tests exist for bankroll updates, exposure aggregation, fee-aware sizing, or kill-switch triggers.

**Weather market normalization is likely to fail on real contract text:**
- Files: `docs/prd.md`
- Why fragile: The weather strategy assumes contract wording can be mapped cleanly to NOAA gridpoints, thresholds, time windows, and local time zones, but the repo has no parsing rules or ambiguity handling.
- Safe modification: Build a dedicated normalization layer that can reject ambiguous markets instead of guessing.
- Test coverage: No fixtures exist for contract parsing, threshold extraction, or timezone conversion.

**Expected-profit claims are unsupported by reproducible evidence:**
- Files: `docs/strategy.md`
- Why fragile: The document lists monthly return ranges and priority ordering, but no notebooks, datasets, scripts, or saved reports in the repo support those claims.
- Safe modification: Treat the stated profit numbers as hypotheses only and require reproducible experiments before they influence capital allocation.
- Test coverage: No executable research artifacts exist.

**Repository metadata is too thin for safe collaboration:**
- Files: `docs/prd.md`, `docs/strategy.md`
- Why fragile: There is no `README`, contributor setup, project bootstrap file, or committed history; `git log` shows no commits and `git status` reports the repo as entirely uncommitted.
- Safe modification: Establish a first committed baseline with setup instructions and executable commands before growing the codebase.
- Test coverage: Not applicable; the repo has no runnable baseline to validate.

## Scaling Limits

**Capital size leaves no room for operational mistakes:**
- Current capacity: `docs/strategy.md` models a `$75` bankroll with a 30% reserve and roughly `$3.75` max single-trade sizing.
- Limit: A few bad fills, fee model errors, or incorrect market mappings can erase the usable bankroll before statistical edge has time to play out.
- Scaling path: Require paper-trading and cost-aware backtests to prove the smallest viable bankroll before any live deployment.

**Single-operator system has no resilience margin:**
- Current capacity: `docs/prd.md` explicitly targets a solo developer/operator model.
- Limit: Monitoring, incident response, and market supervision all depend on one person noticing failures quickly enough.
- Scaling path: Keep the MVP operationally narrow, automate alerts early, and document recovery procedures before adding more strategies.

**Provider dependence creates immediate scaling ceilings:**
- Current capacity: The MVP plan in `docs/prd.md` depends on a few free external services, and `docs/strategy.md` already notes hard request limits for sports data.
- Limit: As scan breadth increases, the system will hit quota, freshness, and reliability ceilings before strategy complexity becomes the main issue.
- Scaling path: Prioritize the most durable single strategy first and add providers only when their cost and failure modes are explicitly budgeted.

## Dependencies at Risk

**Polymarket CLOB and websocket feeds are mission-critical single points of failure:**
- Risk: The planned system in `docs/prd.md` relies on Polymarket for both signal inputs and trade execution, but there is no adapter contract, outage handling, or fallback mode documented.
- Impact: Exchange-side degradation can halt the entire bot or, worse, produce decisions on stale market state.
- Migration plan: Hide venue-specific behavior behind a narrow client interface and support a hard read-only mode when venue state cannot be trusted.

**The Odds API quota and product dependency are mismatched:**
- Risk: Sports mispricing in `docs/prd.md` depends on an external paid/freemium provider, while `docs/strategy.md` cites a free tier that is likely too small for continuous scanning.
- Impact: The sports strategy can fail operationally before it is statistically validated.
- Migration plan: Reduce sports scope to a tiny monitored subset or defer implementation until a sustainable data plan exists.

**Research-only providers are listed without ownership boundaries:**
- Risk: `docs/strategy.md` mentions Gamma API and Open-Meteo, but neither provider is tied to a planned module path in `docs/prd.md`.
- Impact: Ad hoc integrations can leak provider logic into strategy code and increase swap cost later.
- Migration plan: Add every provider to the architecture doc before using it, and keep one adapter per provider with recorded raw responses for replay tests.

## Missing Critical Features

**No paper-trading layer exists:**
- Problem: `docs/prd.md` names `paper_trader.py`, but the file and its behavioral contract do not exist.
- Blocks: Safe verification of order lifecycle handling, risk guardrails, and reconciliation before live capital is used.

**No backtest runner or historical dataset contract exists:**
- Problem: `docs/prd.md` proposes `backtest/runner.py` and `backtest/historical/`, but neither the directories nor a data format are present.
- Blocks: Reproducible threshold tuning, cost modeling, and regression testing against prior market conditions.

**No configuration schema exists:**
- Problem: `docs/prd.md` mentions `config/settings.py` and `config/kill_switches.py`, but there is no declared source of truth for runtime settings, credentials, or environment separation.
- Blocks: Safe deployment, reproducible runs, and reviewable operational defaults.

**No observability baseline exists:**
- Problem: The repo does not define logs, metrics, alerts, or trade/audit records beyond the placeholder mention of `core/trade_logger.py` in `docs/prd.md`.
- Blocks: Root-cause analysis for losses, feed issues, execution failures, and kill-switch activations.

**No repository bootstrap or onboarding path exists:**
- Problem: The root contains no `README`, no setup instructions, and no committed executable example; only `docs/prd.md` and `docs/strategy.md` describe the intended product.
- Blocks: Consistent implementation, review, and future automation.

## Test Coverage Gaps

**All critical trading behaviors are untested because they are unimplemented:**
- What's not tested: Signal generation, market parsing, Kelly sizing, reserve enforcement, drawdown halts, order placement, fill reconciliation, persistence, and paper-trade flows described in `docs/prd.md` and `docs/strategy.md`.
- Files: `docs/prd.md`, `docs/strategy.md`
- Risk: The first implementation pass can encode unsafe assumptions with no regression protection.
- Priority: High

**Strategy claims have no reproducible validation artifacts:**
- What's not tested: The expected monthly profit ranges, volume assumptions, and prioritization in `docs/strategy.md` are not backed by scripts, notebooks, fixtures, or saved backtest reports.
- Files: `docs/strategy.md`
- Risk: Planning can proceed on unsupported profitability and liquidity assumptions.
- Priority: High

**Operational failure modes are not exercised anywhere:**
- What's not tested: Provider outage handling, stale data rejection, reconnect logic, quota exhaustion, duplicate signals, partial fills, and emergency shutdown behavior implied by `docs/prd.md` and `docs/strategy.md`.
- Files: `docs/prd.md`, `docs/strategy.md`
- Risk: The system can appear correct in happy-path reasoning and still fail unsafely in live conditions.
- Priority: High

---

*Concerns audit: 2026-04-17*
