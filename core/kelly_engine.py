"""Deterministic Kelly sizing with conservative Phase 3 clamps."""

from __future__ import annotations

from dataclasses import dataclass

from config.settings import ScanSettings, get_settings


@dataclass(frozen=True)
class KellySizingDecision:
    """Inspectable Kelly sizing result before portfolio headroom checks."""

    derived_no_probability: float
    adjusted_no_probability: float
    no_price: float
    bankroll_usd: float
    raw_kelly_fraction: float
    kelly_fraction: float
    proposed_stake_usd: float
    capped_stake_usd: float
    allowed_stake_usd: float
    minimum_trade_stake_usd: float
    clamp_reasons: tuple[str, ...]


class KellyEngine:
    """Apply haircut, Kelly math, and per-trade caps to a signal edge."""

    def __init__(self, settings: ScanSettings | None = None) -> None:
        self.settings = settings or get_settings()

    def calculate_position_size(
        self,
        derived_no_probability: float,
        no_price: float,
        bankroll_usd: float,
    ) -> KellySizingDecision:
        clamp_reasons: list[str] = []
        safe_probability = min(max(derived_no_probability, 1e-6), 1.0 - 1e-6)
        if safe_probability != derived_no_probability:
            clamp_reasons.append("probability_clamped")

        safe_no_price = min(max(no_price, 1e-6), 1.0 - 1e-6)
        if safe_no_price != no_price:
            clamp_reasons.append("no_price_clamped")

        adjusted_no_probability = max(
            safe_probability - self.settings.probability_haircut_pct,
            1e-6,
        )
        if adjusted_no_probability != safe_probability - self.settings.probability_haircut_pct:
            clamp_reasons.append("probability_haircut_floor_applied")

        q = 1.0 - adjusted_no_probability
        b = (1.0 / safe_no_price) - 1.0
        raw_kelly_fraction = adjusted_no_probability - (q / b)
        kelly_fraction = max(raw_kelly_fraction * self.settings.kelly_fraction, 0.0)
        if kelly_fraction == 0.0 and raw_kelly_fraction < 0.0:
            clamp_reasons.append("negative_edge_clamped")

        proposed_stake_usd = bankroll_usd * kelly_fraction
        per_trade_cap_usd = bankroll_usd * self.settings.per_trade_exposure_cap_pct
        capped_stake_usd = min(proposed_stake_usd, per_trade_cap_usd)
        if capped_stake_usd < proposed_stake_usd:
            clamp_reasons.append("per_trade_cap_exceeded")

        allowed_stake_usd = capped_stake_usd
        if 0.0 < capped_stake_usd < self.settings.minimum_trade_stake_usd:
            clamp_reasons.append("stake_below_minimum")
            allowed_stake_usd = 0.0

        return KellySizingDecision(
            derived_no_probability=safe_probability,
            adjusted_no_probability=adjusted_no_probability,
            no_price=safe_no_price,
            bankroll_usd=bankroll_usd,
            raw_kelly_fraction=raw_kelly_fraction,
            kelly_fraction=kelly_fraction,
            proposed_stake_usd=proposed_stake_usd,
            capped_stake_usd=capped_stake_usd,
            allowed_stake_usd=allowed_stake_usd,
            minimum_trade_stake_usd=self.settings.minimum_trade_stake_usd,
            clamp_reasons=tuple(clamp_reasons),
        )
