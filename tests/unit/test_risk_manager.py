from __future__ import annotations

import pytest

from config.settings import ScanSettings
from core.kelly_engine import KellyEngine
from core.models import (
    PortfolioSnapshot,
    SignalEvaluationRecord,
    SignalEvaluationStatus,
)
from core.risk_manager import RiskManager


def test_risk_manager_blocks_when_global_exposure_headroom_is_exhausted() -> None:
    settings = _risk_settings()
    manager = RiskManager(settings=settings)
    sizing = KellyEngine(settings).calculate_position_size(0.80, 0.40, 100.0)

    decision = manager.evaluate_position_size(
        signal_evaluation=_signal_evaluation(),
        portfolio=PortfolioSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=120.0,
            open_exposure_usd=30.0,
            open_exposure_by_window={"2026-04-18": 5.0},
            captured_at="2026-04-19T00:00:00Z",
        ),
        sizing=sizing,
        window_key="2026-04-18",
    )

    assert decision.decision_status is decision.decision_status.BLOCKED
    assert decision.allowed_stake_usd == pytest.approx(0.0)
    assert decision.proposed_stake_usd == pytest.approx(14.5833333333)
    assert "global_exposure_cap_exceeded" in decision.triggered_rule_codes


def test_risk_manager_blocks_when_window_exposure_headroom_is_exhausted() -> None:
    settings = _risk_settings()
    manager = RiskManager(settings=settings)
    sizing = KellyEngine(settings).calculate_position_size(0.80, 0.40, 100.0)

    decision = manager.evaluate_position_size(
        signal_evaluation=_signal_evaluation(),
        portfolio=PortfolioSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=120.0,
            open_exposure_usd=10.0,
            open_exposure_by_window={"2026-04-18": 15.0},
            captured_at="2026-04-19T00:00:00Z",
        ),
        sizing=sizing,
        window_key="2026-04-18",
    )

    assert decision.decision_status is decision.decision_status.BLOCKED
    assert decision.allowed_stake_usd == pytest.approx(0.0)
    assert decision.window_exposure_usd == pytest.approx(15.0)
    assert "window_exposure_cap_exceeded" in decision.triggered_rule_codes


def test_risk_manager_returns_allowed_stake_when_policy_limits_do_not_block() -> None:
    settings = _risk_settings()
    manager = RiskManager(settings=settings)
    sizing = KellyEngine(settings).calculate_position_size(0.80, 0.40, 100.0)

    decision = manager.evaluate_position_size(
        signal_evaluation=_signal_evaluation(),
        portfolio=PortfolioSnapshot(
            current_bankroll_usd=100.0,
            peak_bankroll_usd=120.0,
            open_exposure_usd=10.0,
            open_exposure_by_window={"2026-04-18": 4.0},
            captured_at="2026-04-19T00:00:00Z",
        ),
        sizing=sizing,
        window_key="2026-04-18",
    )

    assert decision.decision_status is decision.decision_status.ALLOWED
    assert decision.proposed_stake_usd == pytest.approx(14.5833333333)
    assert decision.allowed_stake_usd == pytest.approx(5.0)
    assert decision.current_bankroll_usd == pytest.approx(100.0)
    assert decision.peak_bankroll_usd == pytest.approx(120.0)


def _risk_settings() -> ScanSettings:
    return ScanSettings(
        kelly_fraction=0.25,
        probability_haircut_pct=0.05,
        per_trade_exposure_cap_pct=0.05,
        global_max_open_exposure_pct=0.30,
        window_max_open_exposure_pct=0.15,
        minimum_trade_stake_usd=1.0,
    )


def _signal_evaluation() -> SignalEvaluationRecord:
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
