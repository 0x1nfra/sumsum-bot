# Polymarket Bot MVP: Strategy Landscape & Recommendation

Synthesized from `polymarket-strategies.md`, `technical-architecture.md`, `data-sources.md`, and live volume verification.

**Calibrated to:**

- $50–$100 capital
- Capital preservation priority
- Binary markets
- Sports + Crypto focus
- Quick flips
- Free data sources only
- Python
- Backtesting-first

---

## Part 1: Volume Verification (Your Question Answered)

You asked whether sports and crypto have the biggest volume. **Sports: yes. Crypto: partially.**

| Category | Top Market                | Volume | Binary-Friendly?              |
| -------- | ------------------------- | ------ | ----------------------------- |
| Sports   | Super Bowl 2026 Winner    | $704M  | YES (individual matchups)     |
| Sports   | FIFA World Cup Winner     | $537M  | YES (match outcomes)          |
| Sports   | EPL Winner                | $314M  | YES (match outcomes)          |
| Politics | Dem Nominee 2028          | $1B    | Multi-outcome (defer)         |
| Crypto   | BTC 5-Min Up/Down         | $150M  | YES (perfect for quick flips) |
| Crypto   | BTC Price Target Jan 2026 | $108M  | Multi-outcome (defer)         |
| Crypto   | BTC Price Target 2026     | $30M   | Multi-outcome (defer)         |

---

## Part 2: Strategy Landscape (All 10 Strategies Assessed)

### Strategy 1: BTC 5-Minute Cycle Trading

- **Profit:** $15–$60/month at $75 capital
- **Complexity:** Medium
- **Data:** Free (CLOB WebSocket + Gamma API)
- **Edge Durability:** Medium
- **Capital Fit:** Excellent (288 cycles/day)

### Strategy 2: Sports Odds Mispricing

- **Profit:** $10–$40/month
- **Complexity:** Medium-Low
- **Data:** Free (The Odds API – 500 req/month)
- **Edge Durability:** High
- **Capital Fit:** Good

### Strategy 3: Endgame / High-Probability Resolution

- **Profit:** $5–$20/month
- **Capital Fit:** Poor at $50–$100 (needs $500+)
- **Verdict:** Defer to Phase 2

### Strategy 4: Copy Trading / Whale Tracking

- **Edge Durability:** Low (always enter after whale)
- **Verdict:** Signal layer only, not primary strategy

### Strategy 5: LLM/AI-Driven Signals

- **Cost:** $30–$300/month in API calls
- **Verdict:** Cost exceeds capital. Adopt methodology manually for free.

### Strategy 6: Cross-Platform Arbitrage (Polymarket vs Kalshi)

- **Capital Fit:** Not viable (needs $5K+ on each platform)
- **Verdict:** Defer to Phase 3

### Strategy 7: Market Making

- **Capital Fit:** Not viable (needs $5K+)
- **Verdict:** Defer to Phase 3

### Strategy 8: Weather Bot

- **Profit:** $20–$80/month
- **Edge Durability:** Highest of all strategies
- **Data:** Free (NOAA, Open-Meteo)
- **Verdict:** Strongest single strategy overall

### Strategy 9: Niche / Esports

- **Verdict:** Not enough volume. Defer.

### Strategy 10: Intra-Market Arbitrage

- **Verdict:** Keep as opportunistic overlay (YES + NO < $0.97)

---

## Part 3: Comparison Table

| #   | Strategy               | Profit/Mo  | Complexity | Data Cost  | Edge Durability | Capital Fit | Verdict     |
| --- | ---------------------- | ---------- | ---------- | ---------- | --------------- | ----------- | ----------- |
| 1   | BTC 5-Min Cycle        | $15–$60    | Medium     | Free       | Medium          | Excellent   | MVP Core    |
| 2   | Sports Odds Mispricing | $10–$40    | Medium-Low | Free       | High            | Good        | MVP Core    |
| 3   | Endgame / High-Prob    | $5–$20     | Low        | Free       | Low-Med         | Poor        | Phase 2     |
| 4   | Copy Trading           | Variable   | Low        | Free       | Low             | Good        | Signal only |
| 5   | LLM/AI Signals         | $10–$50    | High       | $30–300/mo | Med-High        | Poor        | Phase 2     |
| 6   | Cross-Platform Arb     | 2–6%/trade | Medium     | Free       | Medium          | Not viable  | Phase 3     |
| 7   | Market Making          | Consistent | Very High  | Free       | High            | Not viable  | Phase 3     |
| 8   | Weather Bot            | $20–$80    | Medium     | Free       | High            | Good        | MVP Core    |
| 9   | Esports / Niche        | Asymmetric | Low        | Free       | High            | Marginal    | Defer       |
| 10  | Intra-Market Arb       | Rare       | Low        | Free       | Low             | Good        | Overlay     |

---

## Part 4: Recommended MVP — Weather First (v2.1)

| Priority  | Strategy               | Allocation | Capital ($75) | Expected Monthly |
| --------- | ---------------------- | ---------- | ------------- | ---------------- |
| #1        | Weather Endgame NO     | 50%        | $37.50        | $15–$45          |
| #2        | BTC 5-Min Cycle        | 25%        | $18.75        | $8–$25           |
| #3        | Sports Odds Mispricing | 15%        | $11.25        | $4–$15           |
| Overlay   | Intra-Market Arb       | 10%        | $7.50         | $1–$5            |
| **Total** |                        | **100%**   | **$75**       | **$28–$90**      |

---

## Part 5: Risk Framework

- **Reserve (30%):** $22.50 — _never touch_
- **Max single trade:** $3.75 (5% of total)
- **Max exposure:** $30.00 (40% of total)
- **Kelly fraction:** Quarter Kelly
- **Drawdown halt:** 30% from peak

### Kill Switches

| Trigger                       | Action                 |
| ----------------------------- | ---------------------- |
| Capital drops below $52.50    | Halt all trading       |
| 5 consecutive losses          | Pause strategy 24h     |
| Win rate < 55% over 50 trades | Re-backtest            |
| Fee structure changes         | Recalculate thresholds |

---

## Part 6: Build Phases

| Phase                      | Days  | Deliverable                                                           |
| -------------------------- | ----- | --------------------------------------------------------------------- |
| 1: Foundation + Weather    | 1–8   | CLOB client, NOAA client, weather scanner, Kelly engine, risk manager |
| 2: Backtest + Weather Live | 9–13  | Backtesting framework, weather goes live ($37.50)                     |
| 3: BTC 5-Min               | 14–17 | Signal engine, BTC goes live ($18.75)                                 |
| 4: Sports                  | 18–21 | Odds client, all 3 live + arb overlay                                 |
| 5: Optimization            | 22–28 | Correlation analysis, parameter tuning, performance improvements      |
