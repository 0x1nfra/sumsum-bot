from __future__ import annotations

import pytest

from config.settings import ScanSettings
from core.kelly_engine import KellyEngine


def test_kelly_engine_applies_probability_haircut_before_quarter_kelly() -> None:
    engine = KellyEngine(_risk_settings())

    decision = engine.calculate_position_size(
        derived_no_probability=0.80,
        no_price=0.40,
        bankroll_usd=40.0,
    )

    assert decision.adjusted_no_probability == pytest.approx(0.75)
    assert decision.raw_kelly_fraction == pytest.approx(0.5833333333)
    assert decision.kelly_fraction == pytest.approx(0.1458333333)
    assert decision.proposed_stake_usd == pytest.approx(5.8333333333)


def test_kelly_engine_caps_stake_by_per_trade_limit() -> None:
    engine = KellyEngine(_risk_settings())

    decision = engine.calculate_position_size(
        derived_no_probability=0.80,
        no_price=0.40,
        bankroll_usd=100.0,
    )

    assert decision.proposed_stake_usd == pytest.approx(14.5833333333)
    assert decision.capped_stake_usd == pytest.approx(5.0)
    assert decision.allowed_stake_usd == pytest.approx(5.0)
    assert "per_trade_cap_exceeded" in decision.clamp_reasons


def test_kelly_engine_blocks_stakes_below_minimum_practical_size() -> None:
    engine = KellyEngine(_risk_settings())

    decision = engine.calculate_position_size(
        derived_no_probability=0.57,
        no_price=0.50,
        bankroll_usd=20.0,
    )

    assert decision.proposed_stake_usd == pytest.approx(0.2)
    assert decision.capped_stake_usd == pytest.approx(0.2)
    assert decision.allowed_stake_usd == pytest.approx(0.0)
    assert "stake_below_minimum" in decision.clamp_reasons


def _risk_settings() -> ScanSettings:
    return ScanSettings(
        kelly_fraction=0.25,
        probability_haircut_pct=0.05,
        per_trade_exposure_cap_pct=0.05,
        minimum_trade_stake_usd=1.0,
    )
