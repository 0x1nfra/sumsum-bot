# Requirements: Sumsum Bot

**Defined:** 2026-04-17
**Core Value:** Prove that the weather strategy can preserve capital, recover from drawdowns, and produce positive paper-trading returns over a 2-week forward test before any live deployment.

## v1 Requirements

### Market Discovery

- [ ] **DISC-01**: Operator can continuously scan active Polymarket weather markets relevant to the configured weather strategy.
- [ ] **DISC-02**: Operator can filter candidate markets by configurable liquidity, price ceiling, and time-to-resolution rules.

### Weather Signal

- [x] **WEAT-01**: Operator can fetch NOAA forecast data for each candidate weather market using the correct location and resolution window.
- [x] **WEAT-02**: Operator can calculate the implied weather-side edge versus Polymarket pricing using explicit strategy rules.
- [x] **WEAT-03**: Operator can inspect the forecast inputs and computed edge that caused a signal to fire or be rejected.

### Risk and Sizing

- [x] **RISK-01**: Operator can apply bankroll-based position sizing using the configured Kelly fraction and per-trade exposure caps.
- [x] **RISK-02**: Operator can enforce kill switches for conditions such as max drawdown, loss streaks, or invalid market conditions.
- [x] **RISK-03**: Operator can review why a candidate trade was blocked by risk controls.

### Paper Trading

- [x] **PAPR-01**: Operator can run the bot in paper-trading mode without sending live orders.
- [x] **PAPR-02**: Operator can simulate order entry, open-position tracking, and market resolution for weather trades.
- [ ] **PAPR-03**: Operator can measure bankroll change, PnL percentage, and recovery from drawdown over a 2-week forward test.

### Observability

- [ ] **OBSV-01**: Operator can view a dashboard showing current bankroll, open positions, resolved trades, win rate, drawdown, and cumulative PnL percentage.
- [ ] **OBSV-02**: Operator can inspect every simulated trade in a durable log with signal inputs, sizing, decision rationale, and resolution outcome.
- [ ] **OBSV-03**: Operator can view operational events such as kill-switch activations, failed data fetches, and scanner health.

### Deployment

- [ ] **DEPL-01**: Operator can deploy the paper trader to a cheap VPS using Docker.
- [ ] **DEPL-02**: Operator can run the service continuously with persisted strategy data across restarts.
- [ ] **DEPL-03**: Operator can keep the runtime configuration and architecture ready for a later live-trading mode without rewriting core subsystems.

## v2 Requirements

### Live Trading

- **LIVE-01**: Operator can switch a validated strategy from paper trading to live trading with real Polymarket execution.
- **LIVE-02**: Operator can manage exchange credentials and live-order safeguards separately from paper mode.

### Additional Strategies

- **MULT-01**: Operator can run BTC 5-minute strategy modules in the same framework.
- **MULT-02**: Operator can run sports odds mispricing strategy modules in the same framework.
- **MULT-03**: Operator can evaluate arbitrage overlays once the core trading loop is proven.

### Infrastructure

- **DATA-01**: Operator can swap the persistence backend from SQLite to PostgreSQL without rewriting business logic.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Live-money trading in v1 | Paper-trading validation is the explicit gate before risking capital |
| BTC, sports, and arbitrage execution in v1 | Scope is intentionally constrained to weather until profitability is proven |
| Full portfolio allocation across multiple strategies | Not needed until more than one strategy is active |
| PostgreSQL-only deployment in v1 | Adds infrastructure cost and ops complexity before it is needed |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DISC-01 | Phase 1 | Pending |
| DISC-02 | Phase 1 | Pending |
| WEAT-01 | Phase 2 | Complete |
| WEAT-02 | Phase 2 | Complete |
| WEAT-03 | Phase 2 | Complete |
| RISK-01 | Phase 3 | Complete |
| RISK-02 | Phase 3 | Complete |
| RISK-03 | Phase 3 | Complete |
| PAPR-01 | Phase 4 | Complete |
| PAPR-02 | Phase 4 | Complete |
| PAPR-03 | Phase 4 | Pending |
| OBSV-01 | Phase 5 | Pending |
| OBSV-02 | Phase 5 | Pending |
| OBSV-03 | Phase 5 | Pending |
| DEPL-01 | Phase 6 | Pending |
| DEPL-02 | Phase 6 | Pending |
| DEPL-03 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-17*
*Last updated: 2026-04-19 after Phase 03 completion*
