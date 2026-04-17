# Codebase Structure

**Analysis Date:** 2026-04-17

## Directory Layout

```text
sumsum-bot/
├── .planning/          # Generated planning and codebase analysis artifacts
│   └── codebase/       # Repository reference documents for later phases
├── docs/               # Product and strategy documentation
└── .codex              # Local tool metadata file present in workspace
```

## Directory Purposes

**`.planning/`:**
- Purpose: Stores planning artifacts produced by GSD workflows.
- Contains: Generated markdown references such as `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/CONCERNS.md`, plus the architecture files written here
- Key files: `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/CONCERNS.md`

**`.planning/codebase/`:**
- Purpose: Holds durable codebase reference documents consumed by later planning and execution tasks.
- Contains: High-level repo analyses, currently all markdown
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/CONCERNS.md`

**`docs/`:**
- Purpose: Holds the only project-authored source material for the bot at this stage.
- Contains: Product requirements and strategy analysis
- Key files: `docs/prd.md`, `docs/strategy.md`

## Key File Locations

**Entry Points:**
- `docs/prd.md`: Current architectural source of truth and the only place where a runtime file tree is defined
- `docs/strategy.md`: Current strategy-selection reference, including capital allocation and kill-switch rules
- Planned `main.py`: Intended live trading entrypoint described in `docs/prd.md`
- Planned `paper_trader.py`: Intended paper-trading entrypoint described in `docs/prd.md`
- Planned `backtest/runner.py`: Intended backtesting entrypoint described in `docs/prd.md`

**Configuration:**
- No concrete config files exist in the current repo.
- Planned `config/settings.py`: Intended runtime configuration module from `docs/prd.md`
- Planned `config/kill_switches.py`: Intended kill-switch and safety-threshold module from `docs/prd.md`

**Core Logic:**
- No implementation files exist in the current repo.
- Planned `core/clob_client.py`, `core/kelly_engine.py`, `core/risk_manager.py`, `core/trade_logger.py`, `core/backtester.py`, `core/market_scanner.py`, and `core/storage.py` are defined in `docs/prd.md`
- Planned strategy logic is split across `strategies/weather/`, `strategies/btc_5min/`, and `strategies/sports/` in `docs/prd.md`

**Testing:**
- No test directory, test files, or test runner config exist in the current repo.
- No planned test paths are named in `docs/prd.md` or `docs/strategy.md`

## Naming Conventions

**Files:**
- Current repo uses lowercase markdown filenames such as `docs/prd.md` and `docs/strategy.md`.
- Planned runtime files use `snake_case.py` names such as `core/risk_manager.py`, `strategies/weather/noaa_client.py`, and `backtest/runner.py` in `docs/prd.md`.

**Directories:**
- Current repo uses lowercase directories with dot-prefixed metadata folders: `docs/` and `.planning/`.
- Planned runtime directories are lowercase package-style folders such as `core/`, `strategies/`, `config/`, `data/`, and `backtest/` in `docs/prd.md`.

## Where to Add New Code

**New Feature:**
- Product or trading requirements: Add or update documentation in `docs/`
- Architecture and implementation guidance: Add or update analysis in `.planning/codebase/`
- Runtime implementation: Do not place executable code under `docs/` or `.planning/`; follow the planned package layout in `docs/prd.md` once the codebase is bootstrapped

**New Component/Module:**
- Shared trading infrastructure should go under the planned `core/` tree from `docs/prd.md`
- Strategy-specific code should go under the matching planned package:
  - Weather logic: planned `strategies/weather/`
  - BTC short-cycle logic: planned `strategies/btc_5min/`
  - Sports odds logic: planned `strategies/sports/`
- Runtime settings should go under the planned `config/` tree from `docs/prd.md`

**Utilities:**
- Cross-strategy helpers should live under the planned `core/` package rather than inside a single strategy directory
- Historical replay and evaluation helpers should live under the planned `backtest/` package rather than in root scripts

## Planned Runtime Layout

```text
polymarket-bot/
├── core/                      # Shared exchange, risk, logging, storage, and backtest services
│   ├── clob_client.py
│   ├── kelly_engine.py
│   ├── risk_manager.py
│   ├── trade_logger.py
│   ├── backtester.py
│   ├── market_scanner.py
│   └── storage.py
├── strategies/                # Strategy-specific adapters and signal logic
│   ├── weather/
│   │   ├── noaa_client.py
│   │   ├── edge_calculator.py
│   │   └── scanner.py
│   ├── btc_5min/
│   │   ├── signal_engine.py
│   │   └── scanner.py
│   └── sports/
│       ├── odds_client.py
│       ├── comparator.py
│       └── scanner.py
├── config/                    # Runtime settings and kill switches
│   ├── settings.py
│   └── kill_switches.py
├── data/                      # Local persistent trade state
│   └── trades.db
├── backtest/                  # Historical replay tooling
│   ├── runner.py
│   └── historical/
├── main.py                    # Live trading entrypoint
├── paper_trader.py            # Paper trading entrypoint
└── requirements.txt           # Planned Python dependencies
```

## Placement Rules

- Keep repository documentation in `docs/`; do not mix markdown requirements with executable modules.
- Keep generated planning artifacts in `.planning/`; do not treat `.planning/codebase/` as a source directory.
- When bootstrapping implementation, create the planned `core/`, `strategies/`, `config/`, `data/`, and `backtest/` directories at repo root rather than introducing a different parallel layout.
- Root-level scripts should remain orchestration entrypoints only. Shared behavior should live in modules under the planned `core/` or `strategies/` directories.

## Special Directories

**`.planning/`:**
- Purpose: GSD-generated planning state
- Generated: Yes
- Committed: Intended to be committed as project documentation

**`docs/`:**
- Purpose: Product requirements and strategy rationale
- Generated: No
- Committed: Yes

**Planned `data/`:**
- Purpose: Local trade database and runtime state
- Generated: Mixed; directory committed, runtime database contents likely generated
- Committed: Not defined in current repo docs

**Planned `backtest/historical/`:**
- Purpose: Historical input datasets for replay
- Generated: Likely yes
- Committed: Not defined in current repo docs

## Current-State Summary

- The actual repository contains no executable application code, no dependency manifest, no tests, and no runtime config files.
- The only stable navigation targets today are `docs/prd.md`, `docs/strategy.md`, and `.planning/codebase/`.
- Future implementation should follow the Python layout proposed in `docs/prd.md` unless that document is intentionally revised before code scaffolding begins.

---

*Structure analysis: 2026-04-17*
