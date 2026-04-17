# PRD: Polymarket Trading Bot MVP

**Version 1.0 | Weather-first priority | April 2026**

---

## 1. Product Vision

**One-liner:**  
An automated trading bot that exploits mispricings on Polymarket binary prediction markets, starting with weather forecasts, to generate consistent returns on $50–$100 capital using only free data sources.

**Problem:**  
Polymarket's retail crowd consistently misprices binary outcomes relative to authoritative data sources (NOAA weather forecasts, sharp sportsbook lines, BTC order flow). Manual trading can't capture these edges at scale — the opportunities are frequent, small-margin, and time-sensitive.

**Solution:**  
A Python bot that continuously scans Polymarket markets, compares prices against authoritative data sources, and automatically executes +EV trades sized by Kelly criterion with strict risk management.

**Unique Constraints:**

- $50–$100 starting capital (not $10K+ like most trading bots)
- Capital preservation is priority #1 (can't afford to rebuild)
- Free data sources only (zero monthly cost)
- Solo developer, Python, backtesting-first methodology

---

## 2. User Persona

**Irfan — Solo developer/trader with:**

- $50–$100 to deploy on Polymarket
- Python proficiency, comfortable with APIs and data pipelines
- Wants "quick consistent flips" not long-term holds
- Risk-averse at this capital level (can't lose it all)
- Interested in weather, crypto, and sports markets
- Wants to backtest everything before risking real money

**Goal:**  
Prove the system works at small scale, then scale to $500–$5K.

---

## 3. Strategy Specifications

### 3.1 Weather Endgame NO (Priority 1 — 50% allocation)

**Signal Generation:**

- Market Scanner finds active weather markets (temp thresholds, precipitation, snow)
- NOAA Client pulls forecast for matching location + time window
- Edge Calculator compares NOAA probability vs. Polymarket price
- Signal fires when:  
  `noaa_no_probability - polymarket_no_price > 0.10` (10% edge minimum)

**Entry Criteria:**

- Edge > 10%
- Market resolution within 72 hours
- Market volume > $5K (liquidity check)
- NO price < $0.85 (room for profit after fees)

**Sizing:** Quarter Kelly based on estimated edge and win probability  
**Exit:** Hold to resolution

**Data Source:**  
`api.weather.gov/gridpoints/{office}/{x},{y}/forecast/hourly`

- Free, no auth
- JSON includes: probabilityOfPrecipitation, temperature, windSpeed

---

### 3.2 BTC 5-Minute Cycle (Priority 2 — 25% allocation)

**Signal Generation:**

- WebSocket connects to Polymarket CLOB (BTC 5-min market)
- Calculate:
  - Order imbalance ratio
  - VWAP deviation
  - Momentum score
- Composite score = weighted average

**Signal Fires When:**
`composite_score > entry_threshold` (backtested)

**Entry Criteria:**

- Score above threshold
- Spread < 3%
- No kill switch active

**Sizing:** Quarter Kelly, max 10% of strategy allocation  
**Exit:** Auto-resolution at 5 minutes

**Data Source:**  
`wss://clob.polymarket.com/ws`

- Free WebSocket
- Subscribe to book + trades

---

### 3.3 Sports Odds Mispricing (Priority 3 — 15% allocation)

**Signal Generation:**

- Pull Pinnacle odds via The Odds API
- Convert to implied probability (remove vig)
- Compare vs Polymarket price

**Signal Fires When:**
`|sharp_implied_prob - polymarket_price| > 0.03`

**Entry Criteria:**

- Edge > 3%
- Game starts within 24 hours
- Market volume > $10K

**Sizing:** Quarter Kelly  
**Exit:** Hold to resolution

**Data Source:**  
`api.the-odds-api.com/v4/sports/{sport}/odds/`

- Free tier (500 req/month)

---

### 3.4 Intra-Market Arbitrage (Overlay — 10%)

**Signal:**  
`YES_price + NO_price < 0.97`

**Entry:** Buy YES + NO simultaneously  
**Sizing:** Maximum available  
**Exit:** Hold to resolution (guaranteed profit)

---

## 4. System Architecture

```text
polymarket-bot/
├── core/
│   ├── clob_client.py
│   ├── kelly_engine.py
│   ├── risk_manager.py
│   ├── trade_logger.py
│   ├── backtester.py
│   ├── market_scanner.py
│   └── storage.py
├── strategies/
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
├── config/
│   ├── settings.py
│   └── kill_switches.py
├── data/
│   └── trades.db
├── backtest/
│   ├── runner.py
│   └── historical/
├── main.py
├── paper_trader.py
└── requirements.txt
```
