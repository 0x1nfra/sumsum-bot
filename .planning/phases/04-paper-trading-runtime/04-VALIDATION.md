---
phase: 04
slug: paper-trading-runtime
status: audited
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-19
updated: 2026-04-20
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest 8.x` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run --extra dev pytest tests/unit -q` |
| **Full suite command** | `uv run --extra dev pytest tests/unit tests/integration -q` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run --extra dev pytest tests/unit -q`
- **After every plan wave:** Run `uv run --extra dev pytest tests/unit tests/integration -q`
- **Before `$gsd-verify-work`:** Full suite must be green with `uv run --extra dev pytest`
- **Max feedback latency:** 45 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | PAPR-02 | T-04-01 | Paper positions, lifecycle events, and bankroll snapshots persist append-only with explicit state transitions. | integration | `uv run --extra dev pytest tests/integration/test_paper_storage.py -q` | `tests/integration/test_paper_storage.py` | ✅ green |
| 04-01-02 | 01 | 1 | PAPR-02 | T-04-01 / T-04-02 | Entry and settlement rules update contract counts, reserved stake, and resolved proceeds deterministically. | unit | `uv run --extra dev pytest tests/unit/test_paper_execution.py -q` | `tests/unit/test_paper_execution.py` | ✅ green |
| 04-02-01 | 02 | 2 | PAPR-01, PAPR-02 | T-04-02 | Paper runtime runs once/loop mode without live execution, reuses upstream seams, and restores open positions from storage. | integration | `uv run --extra dev pytest tests/integration/test_paper_runtime.py -q` | `tests/integration/test_paper_runtime.py` | ✅ green |
| 04-03-01 | 03 | 3 | PAPR-03 | T-04-03 | Forward-test metrics compute cumulative return, drawdown, and drawdown recovery from durable bankroll/trade history. | unit | `uv run --extra dev pytest tests/unit/test_performance_metrics.py -q` | `tests/unit/test_performance_metrics.py` | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all Phase 4 requirements.
- Phase 1 through Phase 3 already established `pytest` plus `uv` execution paths, so Phase 4 can add its unit and integration suites inside the plan-owned tasks.
- `tests/unit/test_paper_execution.py`, `tests/unit/test_performance_metrics.py`, `tests/integration/test_paper_storage.py`, and `tests/integration/test_paper_runtime.py` are created during execution rather than through a separate bootstrap plan.
- No additional dev dependencies are required for this phase.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Resolution-source choice and fail-closed posture match the Phase 4 context decisions | PAPR-02 | Settlement-source selection is partly a product/runtime decision, not only a correctness assertion | Before approving execution, compare the chosen settlement source and fallback behavior against `.planning/phases/04-paper-trading-runtime/04-CONTEXT.md`, `docs/prd.md`, and `docs/strategy.md`. |
| Reported forward-test metrics are meaningful for the operator’s 2-week validation goal | PAPR-03 | Metric correctness in code does not guarantee the right operator-facing measurement set | Confirm the plan includes cumulative return, bankroll delta, max drawdown, and a concrete drawdown-recovery measure before execution is approved. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or inherited test harness support
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 coverage inherited from prior phases; no extra bootstrap plan required
- [x] No watch-mode flags
- [x] Feedback latency < 45s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved

## Validation Audit 2026-04-20

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 4 |
| Escalated | 0 |

- Confirmed existing Phase 4 validation coverage is `COVERED` for `PAPR-01`, `PAPR-02`, and `PAPR-03`.
- Verified `tests/unit/test_paper_execution.py`, `tests/unit/test_performance_metrics.py`, `tests/integration/test_paper_storage.py`, and `tests/integration/test_paper_runtime.py` exist and execute green.
- Audit run: `uv run --extra dev pytest tests/integration/test_paper_storage.py tests/unit/test_paper_execution.py tests/integration/test_paper_runtime.py tests/unit/test_performance_metrics.py -q` → `18 passed in 0.25s`.
