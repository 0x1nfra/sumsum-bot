"""Portfolio-aware risk policy for Phase 3 signal gating."""

from __future__ import annotations

from config.kill_switches import KillSwitchSettings
from config.settings import ScanSettings, get_settings
from core.kelly_engine import KellySizingDecision
from core.models import PortfolioSnapshot, RiskDecisionRecord, RiskDecisionStatus, SignalEvaluationRecord


class RiskManager:
    """Evaluate staking proposals against portfolio exposure constraints."""

    def __init__(
        self,
        settings: ScanSettings | None = None,
        kill_switches: KillSwitchSettings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.kill_switches = kill_switches or KillSwitchSettings()

    def evaluate_position_size(
        self,
        signal_evaluation: SignalEvaluationRecord,
        portfolio: PortfolioSnapshot,
        sizing: KellySizingDecision,
        window_key: str,
    ) -> RiskDecisionRecord:
        current_bankroll_usd = portfolio.current_bankroll_usd
        global_exposure_limit_usd = (
            current_bankroll_usd * self.settings.global_max_open_exposure_pct
        )
        window_exposure_limit_usd = (
            current_bankroll_usd * self.settings.window_max_open_exposure_pct
        )
        window_exposure_usd = portfolio.open_exposure_by_window.get(window_key, 0.0)
        global_headroom_usd = global_exposure_limit_usd - portfolio.open_exposure_usd
        window_headroom_usd = window_exposure_limit_usd - window_exposure_usd

        rule_codes = list(sizing.clamp_reasons)
        if global_headroom_usd <= 0.0:
            rule_codes.append("global_exposure_cap_exceeded")
        if window_headroom_usd <= 0.0:
            rule_codes.append("window_exposure_cap_exceeded")

        allowed_stake_usd = min(
            sizing.allowed_stake_usd,
            max(global_headroom_usd, 0.0),
            max(window_headroom_usd, 0.0),
        )
        decision_status = (
            RiskDecisionStatus.ALLOWED if allowed_stake_usd > 0.0 else RiskDecisionStatus.BLOCKED
        )
        decision_reason = rule_codes[0] if rule_codes else "position_size_approved"

        return RiskDecisionRecord(
            signal_evaluation_id=None,
            market_id=signal_evaluation.market_id,
            window_key=window_key,
            decision_status=decision_status,
            decision_reason=decision_reason,
            triggered_rule_codes=tuple(rule_codes),
            current_bankroll_usd=current_bankroll_usd,
            peak_bankroll_usd=portfolio.peak_bankroll_usd,
            open_exposure_usd=portfolio.open_exposure_usd,
            window_exposure_usd=window_exposure_usd,
            proposed_stake_usd=sizing.proposed_stake_usd,
            allowed_stake_usd=allowed_stake_usd,
            evidence={
                "market_id": signal_evaluation.market_id,
                "window_key": window_key,
                "current_bankroll_usd": current_bankroll_usd,
                "peak_bankroll_usd": portfolio.peak_bankroll_usd,
                "open_exposure_usd": portfolio.open_exposure_usd,
                "window_exposure_usd": window_exposure_usd,
                "global_headroom_usd": max(global_headroom_usd, 0.0),
                "window_headroom_usd": max(window_headroom_usd, 0.0),
                "proposed_stake_usd": sizing.proposed_stake_usd,
                "allowed_stake_usd": allowed_stake_usd,
                "triggered_rule_codes": tuple(rule_codes),
            },
        )
