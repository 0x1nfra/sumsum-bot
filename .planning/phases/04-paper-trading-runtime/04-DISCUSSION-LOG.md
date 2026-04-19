# Phase 4: Paper Trading Runtime - Discussion Log

**Gathered:** 2026-04-19
**Status:** Complete

## Summary

Discussion focused on the key runtime gray areas for the paper trader. The user locked immediate paper fills and explicitly delegated resolution mechanics, runtime structure, and ledger granularity to planner/implementation judgment.

## Questions And Answers

### Paper entry behavior
**Question:** Which paper-fill behavior do you want?

**Options presented:**
- `1` — Enter immediately at the current market `no_price` once the signal passes risk.
- `2` — Enter conservatively: apply a fixed paper slippage penalty on entry.
- `3` — Enter only if a later scan still shows the price at or better than the approved entry.
- `4` — Let the agent choose.

**User selection:** `1`

**Captured decision:** Paper trades enter immediately at the current `no_price` after risk approval.

### Resolution source of truth
**Question:** How should open paper trades resolve?

**Options presented:**
- `1` — Resolve only from Polymarket’s final market outcome/status.
- `2` — Resolve from Polymarket when available, but allow a manual fallback path for edge cases.
- `3` — Resolve from a local rule based on the stored market window and forecast inputs, without depending on Polymarket finalization.
- `4` — Let the agent choose.

**User selection:** `4`

**Captured decision:** Leave settlement mechanics to implementation judgment.

### Runtime loop shape
**Question:** How should the always-on paper trader be structured?

**Options presented:**
- `1` — One simple sequential loop: `scan -> signal -> risk -> enter -> resolve open positions -> sleep`.
- `2` — Two distinct runtime passes in the same process: one for finding new entries, one for checking/resolving open positions.
- `3` — A more explicit scheduler with separate jobs/timers for scanning, entry, and resolution work.
- `4` — Let the agent choose.

**User selection:** `4`

**Captured decision:** Leave runtime orchestration shape to implementation judgment.

### Performance ledger granularity
**Question:** How should Phase 4 track forward-test performance?

**Options presented:**
- `1` — Update bankroll and performance only when trades resolve.
- `2` — Keep resolution-based PnL, but also store periodic equity snapshots while positions are open.
- `3` — Keep a fuller event ledger with periodic snapshots plus every entry/open/resolution bankroll transition.
- `4` — Let the agent choose.

**User selection:** `4`

**Captured decision:** Leave performance-ledger detail to implementation judgment.

## Deferred Or Out-Of-Scope Items

- None raised during discussion beyond already-known phase boundaries.

---

*Phase: 04-paper-trading-runtime*
*Discussion logged: 2026-04-19*
