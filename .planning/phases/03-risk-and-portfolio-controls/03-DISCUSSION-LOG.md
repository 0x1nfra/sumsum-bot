# Phase 3: Risk and Portfolio Controls - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-19
**Phase:** 03-risk-and-portfolio-controls
**Areas discussed:** sizing policy, exposure model, kill-switch behavior, blocked-trade audit trail, capital baseline

---

## Sizing policy

| Option | Description | Selected |
|--------|-------------|----------|
| Very conservative | Quarter-Kelly as an upper bound with a hard fixed-percent cap per trade | ✓ |
| Pure quarter-Kelly with caps | Quarter-Kelly drives sizing directly, then clamp by exposure limits | |
| Fixed-fraction only | Ignore Kelly and use a fixed-percent sizing rule only | |

**User's choice:** Very conservative posture with quarter-Kelly retained as the sizing input, a small probability haircut before Kelly, and a hard 5% of current bankroll cap per trade.
**Notes:** User wanted to preserve Kelly because it can help grow the account safely; discussion clarified that Kelly remains in place but is subordinate to hard survival caps for a $50-$100 bankroll.

---

## Exposure model

| Option | Description | Selected |
|--------|-------------|----------|
| Simple portfolio exposure only | Cap total open exposure overall, without narrower correlation controls | |
| Portfolio + per-trade + per-resolution-window | Cap total open exposure, each trade, and exposure concentrated in one resolution window | ✓ |
| Portfolio + per-trade + per-city/family/window | Add more granular correlation caps across several categories | |

**User's choice:** Portfolio + per-trade + per-resolution-window controls, with 30% global max open exposure and 15% per-resolution-window cap.
**Notes:** Discussion favored an anti-stacking rule that handles correlated weather windows without overcomplicating Phase 3 with city-level or contract-family limits.

---

## Kill-switch behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Include only clear capital-protection rules now | Drawdown halt, exposure-cap blocks, safety blocks, cooldown after trigger | ✓ |
| Add consecutive-loss pause now too | Include streak-based pauses even before paper-runtime resolution history exists | |
| Keep kill switches minimal until Phase 4 | Defer most automated halts until paper trading exists | |

**User's choice:** Accepted the recommendation to include drawdown halts, exposure-cap hard blocks, market/signal safety blocks, and cooldown behavior now, while deferring consecutive-loss pause logic to Phase 4.
**Notes:** Drawdown halt threshold locked at 20% from peak bankroll.

---

## Blocked-trade audit trail

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal | Reason code plus a few summary fields | |
| Rich but bounded | Store decision inputs, triggered rules, bankroll/exposure snapshot, and human-readable reason | ✓ |
| Full runtime snapshot | Capture a broad portfolio-event view in each blocked decision record | |

**User's choice:** Rich but bounded blocked-trade audit trail.
**Notes:** Discussion emphasized preserving enough context to explain rejections later without prematurely building the full paper-trading ledger in Phase 3.

---

## Capital baseline

| Option | Description | Selected |
|--------|-------------|----------|
| Current bankroll for sizing, peak bankroll for drawdown | Size dynamically off current capital while measuring drawdown from the high-water mark | ✓ |
| Current bankroll for everything | Use current capital for both sizing and drawdown tests | |
| Peak-adjusted bankroll for sizing and drawdown | Keep sizing and drawdown tied to historical highs | |

**User's choice:** Current bankroll for sizing and exposure caps, peak bankroll only for drawdown calculations.
**Notes:** This preserves automatic size reduction after losses while keeping drawdown halts anchored to the high-water mark.

---

## the agent's Discretion

- Exact minimum practical stake threshold.
- Exact probability haircut formula.
- Exact cooldown duration and resume semantics.
- Exact storage schema shape for blocked-trade persistence.

## Deferred Ideas

- Consecutive-loss pause logic after resolved paper trades exist in Phase 4.
- More granular correlation caps by city or contract family beyond the per-resolution-window rule.
