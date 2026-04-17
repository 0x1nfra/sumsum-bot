# Coding Conventions

**Analysis Date:** 2026-04-17

## Naming Patterns

**Current repository state:**
- No executable source files are present. The only tracked project files are `docs/prd.md`, `docs/strategy.md`, `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/CONCERNS.md`.
- No repository-enforced naming convention can be verified from implementation because directories such as `src/`, `core/`, `strategies/`, `tests/`, or `app/` do not exist in the current checkout.

**Files:**
- Markdown files use lowercase filenames with hyphens, as shown by `docs/prd.md` and `docs/strategy.md`.
- Planning reference docs use uppercase filenames, as shown by `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, and `.planning/codebase/CONCERNS.md`.
- Documentation-implied future Python modules use `snake_case.py`, based on the planned paths embedded in `docs/prd.md`: `core/clob_client.py`, `core/risk_manager.py`, `strategies/weather/noaa_client.py`, `config/settings.py`.

**Functions:**
- Not directly observable because no `.py`, `.ts`, or other source files exist.
- The planned module names in `docs/prd.md` imply descriptive function and method naming around domain actions such as market scanning, risk management, trade logging, and backtesting.

**Variables:**
- Not observable from current repository contents.

**Types:**
- Not observable from current repository contents.

## Code Style

**Formatting:**
- No formatter configuration is present. Files such as `pyproject.toml`, `setup.cfg`, `.editorconfig`, `.prettierrc`, and `biome.json` are not present in the repository root.
- The only style that can be observed is Markdown authoring in `docs/prd.md` and `docs/strategy.md`:
  - ATX headings (`#`, `##`, `###`) are used consistently.
  - Tables are used for comparisons and rollout plans.
  - Code fences use language hints such as `text` in `docs/prd.md`.
  - Lists are short, flat, and domain-oriented.

**Linting:**
- No linter configuration is present. `ruff`, `flake8`, `pylint`, `eslint`, and `mypy` config files are not detected.
- No CI checks or local lint commands are documented anywhere in the repo.

## Import Organization

**Order:**
1. Not detectable from current repository contents because there are no source files with imports.
2. If implementation follows the planned architecture in `docs/prd.md`, expect imports to be organized by internal package boundaries such as `core/`, `strategies/`, and `config/`.
3. No third-party import grouping rules are established yet.

**Path Aliases:**
- Not detected. There is no import alias configuration because no application manifest or runtime config exists.

## Error Handling

**Patterns:**
- No error-handling implementation is present.
- The strongest documented quality signal is risk containment rather than exception structure:
  - `docs/prd.md` defines kill switches, drawdown halts, and strategy pauses.
  - `docs/strategy.md` defines reserve capital, max single-trade exposure, and re-backtest triggers.
- For future code in the planned modules from `docs/prd.md`, treat operational failures as domain events that should map to the documented controls:
  - `core/risk_manager.py` should enforce kill-switch thresholds from `docs/prd.md`.
  - `config/kill_switches.py` is the documented home for global stop conditions.
  - `core/trade_logger.py` is the documented place to persist failed and successful trade attempts.

## Logging

**Framework:** Not detected.

**Patterns:**
- No logging library, logger setup, or log formatting standard is implemented.
- The only logging-related convention documented is the existence of `core/trade_logger.py` in the planned tree inside `docs/prd.md`.
- Until code exists, there is no confirmed split between audit logs, debug logs, and execution logs.

## Comments

**When to Comment:**
- No source comments can be inspected because no implementation files exist.
- Documentation quality is high in `docs/prd.md` and `docs/strategy.md`; the project currently carries intent through prose rather than inline code comments.

**JSDoc/TSDoc:**
- Not applicable. No JavaScript or TypeScript files exist.
- Python docstring style is also not yet established because no `.py` files exist.

## Function Design

**Size:**
- Not observable from implementation.
- The planned decomposition in `docs/prd.md` favors small, single-purpose modules over one large script:
  - `core/backtester.py`
  - `core/market_scanner.py`
  - `strategies/weather/edge_calculator.py`
  - `strategies/sports/comparator.py`

**Parameters:**
- Not observable from implementation.
- The documented architecture suggests domain-specific inputs rather than framework objects, because the design is described as a custom Python bot with separate clients, calculators, scanners, and risk components in `docs/prd.md`.

**Return Values:**
- Not observable from implementation.

## Module Design

**Exports:**
- Not observable because there are no importable modules in the repository.
- The planned file tree in `docs/prd.md` implies direct module imports rather than framework registration or code generation.

**Barrel Files:**
- Not detected.
- There is no evidence of `__init__.py` package export design yet, because the planned Python package layout remains unimplemented.

## Practical Guidance For New Implementation

- Treat `docs/prd.md` as the only repo-backed architectural naming source until real code exists.
- Match the documented Python-first layout when creating the first implementation files:
  - Core engine code belongs under paths like `core/clob_client.py` and `core/risk_manager.py`.
  - Strategy-specific logic belongs under paths like `strategies/weather/` and `strategies/sports/`.
  - Configuration belongs under `config/settings.py` and `config/kill_switches.py`.
- Prefer `snake_case` filenames and descriptive domain module names, because every planned Python path in `docs/prd.md` follows that pattern.
- Do not assume any formatter, linter, import sorter, or type checker is already in place; add and document those tools explicitly when implementation begins.

## Current Convention Posture

- Confirmed conventions today are repository-level only: Markdown docs under `docs/`, uppercase codebase maps under `.planning/codebase/`, and documentation-driven architecture intent in `docs/prd.md`.
- No executable coding convention is enforced yet because the codebase contains no implementation files.
- The first implementation phase will establish the real convention baseline; until then, `docs/prd.md` is the only reliable reference for naming and module boundaries.

---

*Convention analysis: 2026-04-17*
