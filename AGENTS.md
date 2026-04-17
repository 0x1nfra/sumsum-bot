<!-- GSD:project-start source:PROJECT.md -->
## Project

**Sumsum Bot**

Sumsum Bot is a Python-based Polymarket trading bot project focused first on one strategy: weather market paper trading. The initial product is not a multi-strategy live bot; it is a weather-only forward-testing system that runs continuously, simulates trades, logs every decision, and shows whether the strategy can grow capital and recover from drawdowns before real money is used.

**Core Value:** Prove that the weather strategy can preserve capital, recover from drawdowns, and produce positive paper-trading returns over a 2-week forward test before any live deployment.

### Constraints

- **Capital**: Small starting bankroll ($50-$100) — risk controls and capital preservation matter more than maximizing throughput.
- **Strategy scope**: Weather only for v1 — avoid multi-strategy architecture decisions that slow validation.
- **Validation**: Paper trading for 2 weeks before live trading — no real-funds execution in the first milestone.
- **Data**: Free data sources only — NOAA is the required weather input.
- **Deployment**: Cheapest practical VPS with Docker image distribution — must support always-on simulation and straightforward redeploys.
- **Storage**: SQLite first, PostgreSQL-ready design — keep the first deployment simple while preserving a clean migration path.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Markdown - All tracked repository content is documentation in `docs/prd.md` and `docs/strategy.md`.
- Python (documented target only) - Planned application language described in `docs/prd.md` and reinforced by the proposed file tree in `docs/prd.md`.
- SQL/SQLite (documented target only) - `docs/prd.md` proposes local trade storage at `data/trades.db`.
## Runtime
- No executable runtime is configured in the current repository state. No `package.json`, `pyproject.toml`, `requirements.txt`, `Dockerfile`, or runtime version file is checked in at the project root.
- Python runtime is the intended target environment according to `docs/prd.md`, but no pinned version is present.
- Not detected in the current repository state.
- Lockfile: missing
## Frameworks
- None checked in. There is no application framework, SDK bootstrap, or importable source tree in the repository.
- Custom Python bot architecture is documented in `docs/prd.md` under the proposed `polymarket-bot/` layout.
- Not detected. No test runner config, test files, or coverage tooling is checked in.
- Backtesting is a documented requirement in `docs/prd.md`, with planned modules `core/backtester.py` and `backtest/runner.py`, but those files do not exist in the repository.
- Not detected. No formatter, linter, bundler, task runner, or container config is checked in.
## Key Dependencies
- No package dependencies are declared in the current repository state.
- The product spec in `docs/prd.md` implies a future Polymarket trading client via `core/clob_client.py`, but no SDK or library is named in tracked code.
- Local SQLite storage is implied by `data/trades.db` in the proposed tree in `docs/prd.md`.
- WebSocket support is implied by the planned Polymarket CLOB connection in `docs/prd.md`.
## Configuration
- No `.env` files or config modules are checked in at the repository root.
- `docs/prd.md` proposes configuration modules at `config/settings.py` and `config/kill_switches.py`, but they are design artifacts only.
- No build configuration files are present.
- The only checked-in project files are `docs/prd.md` and `docs/strategy.md`.
## Platform Requirements
- Current repository requirements are minimal: a Markdown-capable editor is sufficient to work with `docs/prd.md` and `docs/strategy.md`.
- The intended implementation path requires Python plus local file/database access, based on the planned structure in `docs/prd.md`.
- Deployment target is not defined in code or config.
- The planned system is a long-running automated trading bot process, inferred from the continuous scanner and WebSocket workflows documented in `docs/prd.md`.
## Evidence Summary
- `docs/prd.md`: Source of the intended Python architecture, runtime shape, file layout, and local storage plan.
- `docs/strategy.md`: Source of the strategy-level service references and confirmation that the bot is planned around free data sources.
- Repository root: No manifest, lockfile, version file, or executable source tree is present.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- No executable source files are present. The only tracked project files are `docs/prd.md`, `docs/strategy.md`, `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/CONCERNS.md`.
- No repository-enforced naming convention can be verified from implementation because directories such as `src/`, `core/`, `strategies/`, `tests/`, or `app/` do not exist in the current checkout.
- Markdown files use lowercase filenames with hyphens, as shown by `docs/prd.md` and `docs/strategy.md`.
- Planning reference docs use uppercase filenames, as shown by `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/CONCERNS.md`.
- Documentation-implied future Python modules use `snake_case.py`, based on the planned paths embedded in `docs/prd.md`: `core/clob_client.py`, `core/risk_manager.py`, `strategies/weather/noaa_client.py`, `config/settings.py`.
- Not directly observable because no `.py`, `.ts`, or other source files exist.
- The planned module names in `docs/prd.md` imply descriptive function and method naming around domain actions such as market scanning, risk management, trade logging, and backtesting.
- Not observable from current repository contents.
- Not observable from current repository contents.
## Code Style
- No formatter configuration is present. Files such as `pyproject.toml`, `setup.cfg`, `.editorconfig`, `.prettierrc`, and `biome.json` are not present in the repository root.
- The only style that can be observed is Markdown authoring in `docs/prd.md` and `docs/strategy.md`:
- No linter configuration is present. `ruff`, `flake8`, `pylint`, `eslint`, and `mypy` config files are not detected.
- No CI checks or local lint commands are documented anywhere in the repo.
## Import Organization
- Not detected. There is no import alias configuration because no application manifest or runtime config exists.
## Error Handling
- No error-handling implementation is present.
- The strongest documented quality signal is risk containment rather than exception structure:
- For future code in the planned modules from `docs/prd.md`, treat operational failures as domain events that should map to the documented controls:
## Logging
- No logging library, logger setup, or log formatting standard is implemented.
- The only logging-related convention documented is the existence of `core/trade_logger.py` in the planned tree inside `docs/prd.md`.
- Until code exists, there is no confirmed split between audit logs, debug logs, and execution logs.
## Comments
- No source comments can be inspected because no implementation files exist.
- Documentation quality is high in `docs/prd.md` and `docs/strategy.md`; the project currently carries intent through prose rather than inline code comments.
- Not applicable. No JavaScript or TypeScript files exist.
- Python docstring style is also not yet established because no `.py` files exist.
## Function Design
- Not observable from implementation.
- The planned decomposition in `docs/prd.md` favors small, single-purpose modules over one large script:
- Not observable from implementation.
- The documented architecture suggests domain-specific inputs rather than framework objects, because the design is described as a custom Python bot with separate clients, calculators, scanners, and risk components in `docs/prd.md`.
- Not observable from implementation.
## Module Design
- Not observable because there are no importable modules in the repository.
- The planned file tree in `docs/prd.md` implies direct module imports rather than framework registration or code generation.
- Not detected.
- There is no evidence of `__init__.py` package export design yet, because the planned Python package layout remains unimplemented.
## Practical Guidance For New Implementation
- Treat `docs/prd.md` as the only repo-backed architectural naming source until real code exists.
- Match the documented Python-first layout when creating the first implementation files:
- Prefer `snake_case` filenames and descriptive domain module names, because every planned Python path in `docs/prd.md` follows that pattern.
- Do not assume any formatter, linter, import sorter, or type checker is already in place; add and document those tools explicitly when implementation begins.
## Current Convention Posture
- Confirmed conventions today are repository-level only: Markdown docs under `docs/`, uppercase codebase maps under `.planning/codebase/`, and documentation-driven architecture intent in `docs/prd.md`.
- No executable coding convention is enforced yet because the codebase contains no implementation files.
- The first implementation phase will establish the real convention baseline; until then, `docs/prd.md` is the only reliable reference for naming and module boundaries.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- The current repository is documentation-only. The only product artifacts are `docs/prd.md` and `docs/strategy.md`; no executable source tree exists yet.
- The intended runtime design is a layered Python module layout defined in the architecture tree embedded in `docs/prd.md`.
- Strategy modules are planned as separate domain packages under `strategies/`, with shared execution, sizing, storage, and risk controls centralized under `core/`.
## Layers
- Purpose: Capture product intent, strategy selection, and the proposed runtime layout.
- Location: `docs/`
- Contains: Requirements and system design notes in `docs/prd.md` and `docs/strategy.md`
- Depends on: None inside the repo
- Used by: Planning documents in `.planning/codebase/` and future implementation work
- Purpose: Convert repo analysis into operational guidance for future implementation.
- Location: `.planning/codebase/`
- Contains: Reference docs such as `STACK.md`, `INTEGRATIONS.md`, `CONCERNS.md`, and these architecture documents
- Depends on: Repository contents, especially `docs/prd.md` and `docs/strategy.md`
- Used by: GSD planning and execution workflows
- Purpose: Centralize exchange access, risk controls, market discovery, persistence, and backtesting.
- Location: Planned under `core/` in `docs/prd.md`
- Contains: `core/clob_client.py`, `core/kelly_engine.py`, `core/risk_manager.py`, `core/trade_logger.py`, `core/backtester.py`, `core/market_scanner.py`, `core/storage.py`
- Depends on: External market/data APIs and runtime configuration from the planned `config/` package
- Used by: Planned strategy packages under `strategies/` plus root entrypoints `main.py` and `paper_trader.py`
- Purpose: Encapsulate market-specific signal generation and source-specific parsing.
- Location: Planned under `strategies/` in `docs/prd.md`
- Contains: `strategies/weather/noaa_client.py`, `strategies/weather/edge_calculator.py`, `strategies/weather/scanner.py`, `strategies/btc_5min/signal_engine.py`, `strategies/btc_5min/scanner.py`, `strategies/sports/odds_client.py`, `strategies/sports/comparator.py`, `strategies/sports/scanner.py`
- Depends on: Shared market data and risk primitives in the planned `core/` package
- Used by: Planned orchestrators `main.py`, `paper_trader.py`, and `backtest/runner.py`
- Purpose: Hold runtime settings, kill-switch thresholds, and local trade history.
- Location: Planned under `config/`, `data/`, and `backtest/` in `docs/prd.md`
- Contains: `config/settings.py`, `config/kill_switches.py`, `data/trades.db`, `backtest/runner.py`, `backtest/historical/`
- Depends on: Filesystem and external market/history inputs
- Used by: Planned core modules and entrypoints
## Data Flow
- Current state is file-based documentation only under `docs/` and `.planning/codebase/`.
- Planned runtime state is local and explicit: settings in the planned `config/` package, trade persistence in the planned `data/trades.db`, and replay inputs in the planned `backtest/historical/`.
## Key Abstractions
- Purpose: Identify tradable Polymarket opportunities before strategy-specific filtering.
- Examples: Planned `core/market_scanner.py`, planned `strategies/weather/scanner.py`, planned `strategies/btc_5min/scanner.py`, planned `strategies/sports/scanner.py`
- Pattern: Shared discovery in `core/`, narrowed by strategy-local scanning modules
- Purpose: Apply quarter-Kelly sizing, exposure caps, and kill-switch logic described in `docs/prd.md` and `docs/strategy.md`.
- Examples: Planned `core/kelly_engine.py`, planned `core/risk_manager.py`, planned `config/kill_switches.py`
- Pattern: Centralized policy layer used by every strategy before execution
- Purpose: Encapsulate external source parsing and isolate provider-specific concerns from decision logic.
- Examples: Planned `core/clob_client.py`, planned `strategies/weather/noaa_client.py`, planned `strategies/sports/odds_client.py`
- Pattern: One module per provider, called by strategy or execution layers rather than imported broadly
- Purpose: Separate live orchestration from paper trading and historical replay.
- Examples: Planned `main.py`, planned `paper_trader.py`, planned `backtest/runner.py`
- Pattern: Thin entrypoints over shared strategy and core modules
## Entry Points
- Location: `docs/prd.md`
- Triggers: Human review and planning workflows
- Responsibilities: Defines the target package structure, core modules, and external integration points
- Location: `docs/strategy.md`
- Triggers: Human review and planning workflows
- Responsibilities: Defines strategy priority, capital allocation, and kill-switch constraints that the planned code should implement
- Location: Planned `main.py` in `docs/prd.md`
- Triggers: Continuous live trading process
- Responsibilities: Initialize configuration, start scanners, route approved signals through risk controls, and execute trades
- Location: Planned `paper_trader.py` in `docs/prd.md`
- Triggers: Safe dry-run or simulation mode
- Responsibilities: Reuse live signal generation while replacing real execution with simulated order handling
- Location: Planned `backtest/runner.py` in `docs/prd.md`
- Triggers: Historical evaluation workflow
- Responsibilities: Replay historical inputs, compute simulated outcomes, and validate strategy thresholds before live use
## Error Handling
- `docs/strategy.md` defines operational halts such as drawdown stops, loss streak pauses, and fee-change re-evaluation; these imply centralized failure handling in the planned `core/risk_manager.py` and `config/kill_switches.py`.
- `docs/prd.md` implies provider-specific fault isolation by splitting external access into separate planned modules such as `core/clob_client.py`, `strategies/weather/noaa_client.py`, and `strategies/sports/odds_client.py`.
## Cross-Cutting Concerns
## Implementation Guidance
- Treat `docs/prd.md` as the architectural source of truth for the initial Python package boundaries until real code exists.
- Keep future trading logic inside the planned `strategies/` tree and reserve the planned `core/` tree for reusable cross-strategy services.
- Keep root scripts thin. Any behavior added to the planned `main.py`, `paper_trader.py`, or `backtest/runner.py` should delegate into reusable modules rather than accumulating business logic in entrypoints.
- Preserve the separation between current documentation artifacts (`docs/`, `.planning/codebase/`) and future executable code so planning files remain a reference layer, not an implementation layer.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
