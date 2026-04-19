from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from config.kill_switches import KillSwitchSettings
from config.settings import ScanSettings
from core.models import (
    PortfolioSnapshot,
    RiskDecisionStatus,
    SignalEvaluationRecord,
    SignalEvaluationStatus,
)
from core.risk_manager import RiskManager
from core.storage import CandidateStorage
from strategies.weather.signal_engine import SignalEngine


def test_signal_risk_gate_persists_allowed_decision_with_linked_signal_reference(
    temp_sqlite_db_path: Path,
) -> None:
    settings = _settings(temp_sqlite_db_path)
    storage = CandidateStorage.from_settings(settings)
    engine = SignalEngine(storage=storage, settings=settings)
    storage.persist_signal_evaluations("signal-engine", [_accepted_signal_record()])
    persisted_signal = storage.list_signal_evaluations("wx-temp-phx-001")[0]

    result = engine.evaluate_risk_for_signal(
        [persisted_signal],
        portfolio=PortfolioSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=120.0,
            open_exposure_usd=10.0,
            open_exposure_by_window={"2026-04-18T00:00:00-07:00": 4.0},
            captured_at="2026-04-19T00:00:00Z",
        ),
        risk_manager=RiskManager(settings=settings),
    )

    assert result.risk_decision_count == 1
    assert len(result.allowed) == 1
    assert len(result.blocked) == 0
    allowed = result.allowed[0]
    assert allowed.signal_evaluation_id == persisted_signal.signal_evaluation_id
    assert allowed.decision_reason == "edge_threshold_passed"
    assert allowed.allowed_stake_usd == 5.0

    persisted = storage.list_risk_decisions("wx-temp-phx-001")
    assert persisted[0].signal_evaluation_id == persisted_signal.signal_evaluation_id
    assert persisted[0].decision_status is RiskDecisionStatus.ALLOWED


def test_signal_risk_gate_persists_blocked_decision_with_drawdown_reason(
    temp_sqlite_db_path: Path,
) -> None:
    settings = _settings(temp_sqlite_db_path)
    storage = CandidateStorage.from_settings(settings)
    engine = SignalEngine(storage=storage, settings=settings)
    storage.persist_signal_evaluations("signal-engine", [_accepted_signal_record()])
    persisted_signal = storage.list_signal_evaluations("wx-temp-phx-001")[0]

    result = engine.evaluate_risk_for_signal(
        [persisted_signal],
        portfolio=PortfolioSnapshot(
            current_bankroll_usd=80.0,
            peak_bankroll_usd=120.0,
            open_exposure_usd=10.0,
            open_exposure_by_window={"2026-04-18T00:00:00-07:00": 4.0},
            captured_at="2026-04-19T00:00:00Z",
        ),
        risk_manager=RiskManager(
            settings=settings,
            kill_switches=KillSwitchSettings(max_drawdown_pct=0.20, cooldown_minutes=60),
        ),
    )

    assert result.risk_decision_count == 1
    assert len(result.allowed) == 0
    assert len(result.blocked) == 1
    blocked = result.blocked[0]
    assert blocked.decision_reason == "drawdown_halt_active"
    assert blocked.allowed_stake_usd == 0.0
    assert blocked.evidence["proposed_stake_usd"] > 0.0
    assert blocked.evidence["allowed_stake_usd"] == 0.0

    persisted = storage.list_risk_decisions("wx-temp-phx-001")
    assert persisted[0].triggered_rule_codes == ("drawdown_halt_active",)


def test_signal_risk_gate_blocks_when_cooldown_is_active(
    temp_sqlite_db_path: Path,
) -> None:
    settings = _settings(temp_sqlite_db_path)
    storage = CandidateStorage.from_settings(settings)
    engine = SignalEngine(storage=storage, settings=settings)
    storage.persist_signal_evaluations("signal-engine", [_accepted_signal_record()])
    persisted_signal = storage.list_signal_evaluations("wx-temp-phx-001")[0]

    result = engine.evaluate_risk_for_signal(
        [persisted_signal],
        portfolio=PortfolioSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=120.0,
            open_exposure_usd=10.0,
            open_exposure_by_window={"2026-04-18T00:00:00-07:00": 4.0},
            captured_at="2026-04-19T00:00:00Z",
        ),
        risk_manager=RiskManager(settings=settings),
        cooldown_active_until="2026-04-19T01:00:00+00:00",
        now=datetime(2026, 4, 19, 0, 30, tzinfo=UTC),
    )

    assert result.blocked[0].decision_reason == "cooldown_active"
    assert "cooldown_active" in result.blocked[0].triggered_rule_codes


def _settings(database_path: Path) -> ScanSettings:
    return ScanSettings(
        database_path=str(database_path),
        minimum_edge_to_trade=0.10,
        kelly_fraction=0.25,
        probability_haircut_pct=0.05,
        per_trade_exposure_cap_pct=0.05,
        global_max_open_exposure_pct=0.30,
        window_max_open_exposure_pct=0.15,
        minimum_trade_stake_usd=1.0,
    )


def _accepted_signal_record() -> SignalEvaluationRecord:
    return SignalEvaluationRecord(
        market_id="wx-temp-phx-001",
        scan_run_id=1,
        location="Phoenix",
        mapping_city_key="phoenix",
        contract_family="temperature",
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
        forecast_update_time="2026-04-18T04:00:00+00:00",
        forecast_source_url="https://api.weather.gov/gridpoints/PSR/1,1",
        no_price=0.40,
        derived_yes_probability=0.20,
        derived_no_probability=0.80,
        edge_against_no_price=0.40,
        decision_reason="edge_threshold_passed",
        status=SignalEvaluationStatus.ACCEPTED,
        evidence={"reason_codes": ["edge_threshold_passed"]},
    )
