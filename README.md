**Why this project exists**

I kept seeing posts about passive income from Polymarket bots and wanted to know if the edge was real — not theoretically, but with my own money on the line. Polymarket's CLOB API is fully open, retail crowds demonstrably misprice binary outcomes against authoritative data sources, and I had $75 and a hypothesis worth testing.

---

# Sumsum Bot

Work in progress — weather strategy and paper-trading runtime are implemented; live execution is locked behind a 2-week forward-test gate. Sumsum Bot is a Python bot that scans Polymarket prediction markets, computes edge against NOAA weather forecasts, and sizes trades with quarter-Kelly criterion and hard kill switches. The stack is pure Python 3.11+ stdlib (zero runtime dependencies), SQLite for all persistence, and Polymarket's CLOB REST API plus NOAA's free weather API as the two external signal sources. The most deliberate engineering choice: no real capital touches the system until it clears a 2-week continuous paper-trading forward test — backtests overfit, forward tests don't.

---

## Strategy Priorities

| # | Strategy | Allocation | Edge Source | Status |
|---|----------|------------|-------------|--------|
| 1 | Weather Endgame NO | 50% | NOAA forecast vs. Polymarket price | **Implemented** |
| 2 | BTC 5-Min Cycle | 25% | CLOB order imbalance + VWAP | Deferred |
| 3 | Sports Odds Mispricing | 15% | Sharp sportsbook lines vs. Polymarket | Deferred |
| 4 | Intra-Market Arbitrage | 10% overlay | YES + NO < $0.97 | Deferred |

BTC and sports strategies are stubbed but blocked until the weather strategy proves paper-trading profitability.

---

## Architecture

```
sumsum-bot/
├── core/
│   ├── clob_client.py        # Polymarket CLOB REST API wrapper
│   ├── kelly_engine.py       # Quarter-Kelly position sizing
│   ├── risk_manager.py       # Kill switches + exposure limits
│   ├── paper_runtime.py      # Paper-trading loop orchestration
│   ├── paper_execution.py    # Simulated order fills
│   ├── performance.py        # Forward-test metrics (drawdown, win rate, return)
│   ├── storage.py            # SQLite-first append-only event log
│   ├── trade_logger.py       # Trade persistence
│   ├── market_scanner.py     # Polymarket market discovery
│   └── models.py             # Shared domain types
├── strategies/
│   └── weather/
│       ├── noaa_client.py    # NOAA forecast fetcher
│       ├── edge_calculator.py
│       ├── signal_engine.py  # Edge evaluation + signal gating
│       ├── scanner.py        # Weather market filter
│       └── types.py
├── config/
│   ├── settings.py           # All tunable parameters
│   └── kill_switches.py      # Halt conditions
├── tests/
│   ├── unit/                 # Kelly, edge calc, risk, NOAA client
│   └── integration/          # Full scan → signal → risk → paper fill flow
├── paper_trader.py           # Paper-trading CLI entrypoint
└── main.py                   # Live trading entrypoint (locked)
```

---

## Risk Controls

- **Reserve**: 30% of bankroll — never touched
- **Max single trade**: 5% of total capital
- **Max exposure**: 40% of total capital
- **Position sizing**: Quarter Kelly
- **Drawdown halt**: 30% from peak

### Kill Switches

| Trigger | Action |
|---------|--------|
| Capital drops below $52.50 | Halt all trading |
| 5 consecutive losses | Pause strategy 24h |
| Win rate < 55% over 50 trades | Re-backtest |
| Fee structure changes | Recalculate thresholds |

---

## Validation Gate

Before any live deployment, the bot must complete a **2-week continuous paper-trading forward test** at $75 simulated capital. Pass criteria:

- Capital preserved (no net loss)
- At least one drawdown recovered
- Positive cumulative return after fees

`paper_trader.py` and `main.py` share identical signal and risk logic — the only difference is simulated fills vs. real CLOB orders.

---

## Data Sources

All free, no paid subscriptions:

| Source | Used For |
|--------|----------|
| `api.weather.gov` | NOAA hourly forecast probabilities |
| `clob.polymarket.com` | Market prices, order book |
| `api.the-odds-api.com` | Sharp sportsbook lines (deferred, 500 req/month free tier) |

---

## Setup

```bash
# requires Python 3.11+ — no pip dependencies beyond dev tooling
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# run paper trading (one pass)
python paper_trader.py paper-once

# run paper trading loop
python paper_trader.py paper-loop --iterations 100

# run tests
pytest
```
