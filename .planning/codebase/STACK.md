# Technology Stack

**Analysis Date:** 2026-04-17

## Languages

**Primary:**
- Markdown - All tracked repository content is documentation in `docs/prd.md` and `docs/strategy.md`.

**Secondary:**
- Python (documented target only) - Planned application language described in `docs/prd.md` and reinforced by the proposed file tree in `docs/prd.md`.
- SQL/SQLite (documented target only) - `docs/prd.md` proposes local trade storage at `data/trades.db`.

## Runtime

**Environment:**
- No executable runtime is configured in the current repository state. No `package.json`, `pyproject.toml`, `requirements.txt`, `Dockerfile`, or runtime version file is checked in at the project root.
- Python runtime is the intended target environment according to `docs/prd.md`, but no pinned version is present.

**Package Manager:**
- Not detected in the current repository state.
- Lockfile: missing

## Frameworks

**Core:**
- None checked in. There is no application framework, SDK bootstrap, or importable source tree in the repository.
- Custom Python bot architecture is documented in `docs/prd.md` under the proposed `polymarket-bot/` layout.

**Testing:**
- Not detected. No test runner config, test files, or coverage tooling is checked in.
- Backtesting is a documented requirement in `docs/prd.md`, with planned modules `core/backtester.py` and `backtest/runner.py`, but those files do not exist in the repository.

**Build/Dev:**
- Not detected. No formatter, linter, bundler, task runner, or container config is checked in.

## Key Dependencies

**Critical:**
- No package dependencies are declared in the current repository state.
- The product spec in `docs/prd.md` implies a future Polymarket trading client via `core/clob_client.py`, but no SDK or library is named in tracked code.

**Infrastructure:**
- Local SQLite storage is implied by `data/trades.db` in the proposed tree in `docs/prd.md`.
- WebSocket support is implied by the planned Polymarket CLOB connection in `docs/prd.md`.

## Configuration

**Environment:**
- No `.env` files or config modules are checked in at the repository root.
- `docs/prd.md` proposes configuration modules at `config/settings.py` and `config/kill_switches.py`, but they are design artifacts only.

**Build:**
- No build configuration files are present.
- The only checked-in project files are `docs/prd.md` and `docs/strategy.md`.

## Platform Requirements

**Development:**
- Current repository requirements are minimal: a Markdown-capable editor is sufficient to work with `docs/prd.md` and `docs/strategy.md`.
- The intended implementation path requires Python plus local file/database access, based on the planned structure in `docs/prd.md`.

**Production:**
- Deployment target is not defined in code or config.
- The planned system is a long-running automated trading bot process, inferred from the continuous scanner and WebSocket workflows documented in `docs/prd.md`.

## Evidence Summary

- `docs/prd.md`: Source of the intended Python architecture, runtime shape, file layout, and local storage plan.
- `docs/strategy.md`: Source of the strategy-level service references and confirmation that the bot is planned around free data sources.
- Repository root: No manifest, lockfile, version file, or executable source tree is present.

---

*Stack analysis: 2026-04-17*
