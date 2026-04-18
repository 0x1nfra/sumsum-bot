---
phase: 02
slug: noaa-signal-engine
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-18
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest 8.x` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run --extra dev pytest tests/unit -q` |
| **Full suite command** | `uv run --extra dev pytest` |
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
| 02-01-01 | 01 | 1 | WEAT-01 | T-2-01 | NOAA mapping resolves only supported cities, rejects stale or mismatched windows, and requires explicit NOAA metadata before scoring. | unit + integration | `uv run --extra dev pytest tests/unit/test_noaa_client.py -q` | Planned in 02-01 | ⬜ pending |
| 02-02-01 | 02 | 2 | WEAT-02 | T-2-02 | Contract-family evaluators produce reproducible probability and edge outputs from stored NOAA evidence and configured thresholds. | unit | `uv run --extra dev pytest tests/unit/test_weather_edge_calculator.py -q` | Planned in 02-02 | ⬜ pending |
| 02-03-01 | 03 | 3 | WEAT-03 | T-2-03 | Accepted and rejected signal evaluations persist inspectable evidence, market mapping, freshness data, market price, and explicit reasons. | integration | `uv run --extra dev pytest tests/integration/test_signal_storage.py -q` | Planned in 02-03 | ⬜ pending |
| 02-03-02 | 03 | 3 | WEAT-01, WEAT-02, WEAT-03 | T-2-01 / T-2-02 / T-2-03 | End-to-end candidate evaluation preserves the contract window, NOAA overlap, market price, edge decision, and persisted audit record. | integration | `uv run --extra dev pytest tests/integration/test_noaa_signal_engine.py -q` | Planned in 02-03 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all Phase 2 requirements.
- Phase 1 already established the shared `pytest` and `uv` command surface, so Phase 2 uses TDD sequencing inside each owning plan instead of a separate Wave 0 harness plan.
- `tests/unit/test_noaa_client.py` is seeded in `02-01`, `tests/unit/test_weather_edge_calculator.py` in `02-02`, and the two integration suites in `02-03`.
- `uv run --extra dev pytest ...` is the canonical dev dependency path for every Phase 2 verification step.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| NOAA service behavior still matches research assumptions close to implementation time | WEAT-01 | External API notices and service semantics can change independently of local tests | Re-check current NWS service notices and confirm `/points` plus `forecastGridData` flow still matches `02-RESEARCH.md` before implementation starts. |
| Temperature-threshold probability proxy is implemented exactly as planned | WEAT-02 | The rule is now resolved, but manual review should still confirm the implementation matches the documented bands and persisted evidence fields | Confirm the implementation uses the exact banding rule from `02-RESEARCH.md` and persists the oriented margin plus band label in signal evidence. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or inherited test harness support from Phase 1
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 coverage inherited from Phase 1; no extra Phase 2 bootstrap plan required
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
