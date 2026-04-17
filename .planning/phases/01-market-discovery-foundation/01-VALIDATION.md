---
phase: 1
slug: market-discovery-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-17
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `python -m pytest tests/unit -q` |
| **Full suite command** | `python -m pytest -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/unit -q`
- **After every plan wave:** Run `python -m pytest -q`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-00-01 | 01-00 | 0 | DISC-01, DISC-02 | T-1-00 | Wave 0 test harness and fixtures exist before feature execution | unit | `test -f tests/conftest.py && test -f tests/fixtures/polymarket_weather_markets.json` | ✅ | ⬜ pending |
| 1-01-01 | 01-01 | 1 | DISC-01 | T-1-01 | The documented MVP file layout exists on disk with thin future-facing modules and entrypoints | unit | `python -m pytest tests/unit/test_project_layout.py -q` | ❌ W0 | ⬜ pending |
| 1-02-01 | 01-02 | 2 | DISC-01 | T-1-02 | Settings defaults and overrides resolve from controlled config sources and storage bootstraps schema safely | integration | `python -m pytest tests/unit/test_settings.py tests/integration/test_storage.py -q` | ❌ W0 | ⬜ pending |
| 1-03-01 | 01-03 | 3 | DISC-01 | T-1-03 | Deferred strategy package paths exist as thin placeholders in their documented locations | unit | `python -m pytest tests/unit/test_project_layout.py -q` | ❌ W0 | ⬜ pending |
| 1-04-01 | 01-04 | 4 | DISC-01 | T-1-04 | Polymarket client rejects malformed payloads and normalizes only supported weather markets | integration | `python -m pytest tests/unit/test_weather_normalization.py tests/integration/test_polymarket_ingestion.py -q` | ❌ W0 | ⬜ pending |
| 1-05-01 | 01-05 | 5 | DISC-01, DISC-02 | T-1-05 | Scanner can run continuously through a concrete entrypoint, apply configured filters, and persist accepted and rejected candidates with explicit reasons | integration | `python -m pytest tests/unit/test_filter_rules.py tests/integration/test_market_scan.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pyproject.toml` — define pytest command surface and Python project metadata
- [ ] `tests/unit/test_project_layout.py` — full documented skeleton is present
- [ ] `tests/unit/test_settings.py` — settings defaults and override parsing
- [ ] `tests/unit/test_weather_normalization.py` — approved and rejected market parsing fixtures
- [ ] `tests/integration/test_storage.py` — SQLite schema bootstrap and repository persistence
- [ ] `tests/integration/test_market_scan.py` — end-to-end scan pipeline against fixture payloads

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CLI output is readable for an operator running a scan command | DISC-01 | Exact ergonomics are easier to judge manually than via assertions | Run the documented scan command and confirm it prints accepted and rejected counts plus candidate identifiers and reasons. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all missing references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
