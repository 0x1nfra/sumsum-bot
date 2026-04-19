---
phase: 03
slug: risk-and-portfolio-controls
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-19
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest 8.x` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run --extra dev pytest tests/unit -q` |
| **Full suite command** | `uv run --extra dev pytest tests/unit tests/integration -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run --extra dev pytest tests/unit -q`
- **After every plan wave:** Run `uv run --extra dev pytest tests/unit tests/integration -q`
- **Before `$gsd-verify-work`:** Full suite must be green with `uv run --extra dev pytest`
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | RISK-01 | T-03-01 | Kelly sizing is haircut-aware, quarter-Kelly, and hard-clamped by minimum stake and per-trade limits. | unit | `uv run --extra dev pytest tests/unit/test_kelly_engine.py -q` | Planned in 03-01 | ⬜ pending |
| 03-01-02 | 01 | 1 | RISK-01 | T-03-02 | Exposure-policy evaluation blocks trades that exceed global or same-window headroom and explains the clamp. | unit | `uv run --extra dev pytest tests/unit/test_risk_manager.py -q` | Planned in 03-01 | ⬜ pending |
| 03-02-01 | 02 | 2 | RISK-02, RISK-03 | T-03-03 | Kill switches and blocked-trade evidence are persisted append-only with bankroll and exposure snapshot fields. | integration | `uv run --extra dev pytest tests/integration/test_risk_storage.py -q` | Planned in 03-02 | ⬜ pending |
| 03-02-02 | 02 | 2 | RISK-01, RISK-02, RISK-03 | T-03-01 / T-03-02 / T-03-03 | Accepted Phase 2 signals flow through the risk gate into explicit approved or blocked decisions with linked evidence. | integration | `uv run --extra dev pytest tests/integration/test_signal_risk_gate.py -q` | Planned in 03-02 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all Phase 3 requirements.
- Phase 1 and Phase 2 already established the `pytest` plus `uv` verification path, so Phase 3 can seed new risk suites inside plan-owned tasks.
- `tests/unit/test_kelly_engine.py`, `tests/unit/test_risk_manager.py`, `tests/integration/test_risk_storage.py`, and `tests/integration/test_signal_risk_gate.py` are created during execution rather than through a separate bootstrap plan.
- No extra dev dependencies are required for this phase.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Drawdown and cooldown defaults still reflect the intended small-bankroll operating posture | RISK-02 | Thresholds are product policy choices, not only correctness questions | After implementation, compare config defaults against `.planning/phases/03-risk-and-portfolio-controls/03-CONTEXT.md`, `docs/strategy.md`, and `docs/prd.md` before execution is approved. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or inherited test harness support
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 coverage inherited from prior phases; no extra bootstrap plan required
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
