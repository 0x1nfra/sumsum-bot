---
phase: 02
slug: noaa-signal-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| 02-01-01 | 01 | 1 | WEAT-01 | T-2-01 | NOAA mapping resolves only supported cities, rejects stale or mismatched windows, and requires explicit NOAA metadata before scoring. | unit + integration | `uv run --extra dev pytest tests/unit/test_noaa_client.py -q` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | WEAT-02 | T-2-02 | Contract-family evaluators produce reproducible probability and edge outputs from stored NOAA evidence and configured thresholds. | unit | `uv run --extra dev pytest tests/unit/test_weather_edge_calculator.py -q` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 2 | WEAT-03 | T-2-03 | Accepted and rejected signal evaluations persist inspectable evidence, market mapping, freshness data, and explicit reasons. | integration | `uv run --extra dev pytest tests/integration/test_signal_storage.py -q` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 2 | WEAT-01, WEAT-02, WEAT-03 | T-2-01 / T-2-02 / T-2-03 | End-to-end candidate evaluation preserves the contract window, NOAA overlap, edge decision, and persisted audit record. | integration | `uv run --extra dev pytest tests/integration/test_noaa_signal_engine.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_noaa_client.py` — NOAA points/grid fetch, freshness, and rejection-path coverage
- [ ] `tests/unit/test_weather_edge_calculator.py` — contract-family probability and edge rules
- [ ] `tests/integration/test_signal_storage.py` — append-only signal evaluation persistence
- [ ] `tests/integration/test_noaa_signal_engine.py` — candidate-to-signal end-to-end flow
- [ ] `uv sync --extra dev` or equivalent dev dependency path available before execution

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| NOAA service behavior still matches research assumptions close to implementation time | WEAT-01 | External API notices and service semantics can change independently of local tests | Re-check current NWS service notices and confirm `/points` plus `forecastGridData` flow still matches `02-RESEARCH.md` before implementation starts. |
| Temperature-threshold probability proxy is acceptable for v1 | WEAT-02 | The exact temperature probability method remains a research assumption, not a verified NOAA endpoint contract | Review the chosen formula in the first implementation plan and confirm it stays conservative, reproducible, and fully inspectable in stored evidence. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
