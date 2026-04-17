# External Integrations

**Analysis Date:** 2026-04-17

## APIs & External Services

**Trading & Market Data:**
- Polymarket CLOB - Primary trading venue and real-time order book/trade feed described in `docs/prd.md`.
  - SDK/Client: Not specified in tracked files; `docs/prd.md` proposes a custom client at `core/clob_client.py`.
  - Auth: Not documented in the repository.
- Polymarket Gamma API - Mentioned in `docs/strategy.md` as part of the free data stack for BTC cycle trading.
  - SDK/Client: Not specified in tracked files.
  - Auth: Not documented in the repository.
- Kalshi - Mentioned only in `docs/strategy.md` as a deferred comparison/arbitrage venue.
  - SDK/Client: Not specified.
  - Auth: Not documented.

**Weather Data:**
- NOAA Weather API - Planned authoritative weather data source for the weather strategy in `docs/prd.md`.
  - SDK/Client: Custom client proposed at `strategies/weather/noaa_client.py` in `docs/prd.md`.
  - Auth: None documented; `docs/prd.md` explicitly describes it as free with no auth.
- Open-Meteo - Mentioned in `docs/strategy.md` as an additional free weather source candidate.
  - SDK/Client: Not specified in tracked files.
  - Auth: Not documented.

**Sports Odds:**
- The Odds API - Planned sports pricing source in `docs/prd.md`.
  - SDK/Client: Custom client proposed at `strategies/sports/odds_client.py` in `docs/prd.md`.
  - Auth: API key implied by the service, but no environment variable name is documented in the repository.
- Pinnacle odds - Referenced in `docs/prd.md` as the underlying sharp line source accessed via The Odds API workflow.
  - SDK/Client: Not directly integrated in tracked files.
  - Auth: Not documented.

## Data Storage

**Databases:**
- SQLite (documented target only)
  - Connection: Local file path `data/trades.db` proposed in `docs/prd.md`.
  - Client: Not specified; `docs/prd.md` only proposes a storage module at `core/storage.py`.

**File Storage:**
- Local filesystem only. The planned repo structure in `docs/prd.md` stores historical backtest data under `backtest/historical/`.

**Caching:**
- None documented.

## Authentication & Identity

**Auth Provider:**
- Not detected in the current repository state.
  - Implementation: No user auth, OAuth, wallet auth, or secret management code is checked in.

## Monitoring & Observability

**Error Tracking:**
- None documented.

**Logs:**
- Trade and activity logging are planned via `core/trade_logger.py` in `docs/prd.md`, but no implementation exists in the repository.

## CI/CD & Deployment

**Hosting:**
- Not defined in tracked files.

**CI Pipeline:**
- None detected. No GitHub Actions, CI config, or deployment manifests are checked in.

## Environment Configuration

**Required env vars:**
- Not concretely defined in tracked files.
- A Polymarket credential set is likely required for live trading because `docs/prd.md` describes automatic trade execution, but no variable names are documented.
- A The Odds API key is likely required for `api.the-odds-api.com/v4/sports/{sport}/odds/` usage described in `docs/prd.md`, but no variable names are documented.

**Secrets location:**
- Not detected. No `.env` files, secret stores, or config loaders are checked in.

## Webhooks & Callbacks

**Incoming:**
- None documented.

**Outgoing:**
- WebSocket subscription to `wss://clob.polymarket.com/ws` is documented in `docs/prd.md` for BTC 5-minute market data.
- HTTP requests to `api.weather.gov/gridpoints/{office}/{x},{y}/forecast/hourly` are documented in `docs/prd.md`.
- HTTP requests to `api.the-odds-api.com/v4/sports/{sport}/odds/` are documented in `docs/prd.md`.

## Integration Notes

- All integrations above are documented intent from `docs/prd.md` and `docs/strategy.md`; none are implemented in checked-in source files.
- The repository contains no manifest or SDK declarations, so package-level integration choices remain open.
- The current repo state does not define retry policy, rate limiting, credential loading, or webhook verification.

---

*Integration audit: 2026-04-17*
