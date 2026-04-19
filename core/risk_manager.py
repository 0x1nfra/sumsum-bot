"""Portfolio-aware risk policy for Phase 3 signal gating."""

from __future__ import annotations

from datetime import UTC, datetime

from config.kill_switches import KillSwitchSettings
from config.settings import ScanSettings, get_settings
from core.kelly_engine import KellyEngine, KellySizingDecision
from core.models import (
    PortfolioSnapshot,
    RiskDecisionRecord,
    RiskDecisionStatus,
    SignalEvaluationRecord,
    SignalEvaluationStatus,
)


class RiskManager:
    """Evaluate staking proposals against kill switches and exposure limits."""

    def __init__(
        self,
        settings: ScanSettings | None = None,
        kill_switches: KillSwitchSettings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.kill_switches = kill_switches or KillSwitchSettings()
        self.kelly_engine = KellyEngine(self.settings)

    def evaluate_risk_for_signal(
        self,
        signal_evaluation: SignalEvaluationRecord,
        portfolio: PortfolioSnapshot,
        *,
        window_key: str,
        cooldown_active_until: str | None = None,
        now: datetime | None = None,
    ) -> RiskDecisionRecord:
        sizing = self.kelly_engine.calculate_position_size(
            derived_no_probability=float(signal_evaluation.derived_no_probability or 0.0),
            no_price=signal_evaluation.no_price,
            bankroll_usd=portfolio.current_bankroll_usd,
        )
        rule_codes: list[str] = []

        if (
            self.kill_switches.block_unaccepted_signals
            and signal_evaluation.status is not SignalEvaluationStatus.ACCEPTED
        ):
            rule_codes.append("signal_not_accepted")

        drawdown_pct = self._calculate_drawdown_pct(
            current_bankroll_usd=portfolio.current_bankroll_usd,
            peak_bankroll_usd=portfolio.peak_bankroll_usd,
        )
        if drawdown_pct >= self.kill_switches.max_drawdown_pct:
            rule_codes.append("drawdown_halt_active")

        if self._cooldown_is_active(cooldown_active_until, now=now):
            rule_codes.append("cooldown_active")

        if rule_codes:
            return self._blocked_decision(
                signal_evaluation=signal_evaluation,
                portfolio=portfolio,
                window_key=window_key,
                sizing=sizing,
                rule_codes=tuple(rule_codes),
                drawdown_pct=drawdown_pct,
            )

        return self.evaluate_position_size(
            signal_evaluation=signal_evaluation,
            portfolio=portfolio,
            sizing=sizing,
            window_key=window_key,
        )

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
        decision_reason = (
            signal_evaluation.decision_reason
            if decision_status is RiskDecisionStatus.ALLOWED
            else (rule_codes[0] if rule_codes else signal_evaluation.decision_reason)
        )

        return RiskDecisionRecord(
            signal_evaluation_id=signal_evaluation.signal_evaluation_id,
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
                "signal_status": signal_evaluation.status.value,
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

    def _blocked_decision(
        self,
        *,
        signal_evaluation: SignalEvaluationRecord,
        portfolio: PortfolioSnapshot,
        window_key: str,
        sizing: KellySizingDecision,
        rule_codes: tuple[str, ...],
        drawdown_pct: float,
    ) -> RiskDecisionRecord:
        window_exposure_usd = portfolio.open_exposure_by_window.get(window_key, 0.0)
        return RiskDecisionRecord(
            signal_evaluation_id=signal_evaluation.signal_evaluation_id,
            market_id=signal_evaluation.market_id,
            window_key=window_key,
            decision_status=RiskDecisionStatus.BLOCKED,
            decision_reason=rule_codes[0],
            triggered_rule_codes=rule_codes,
            current_bankroll_usd=portfolio.current_bankroll_usd,
            peak_bankroll_usd=portfolio.peak_bankroll_usd,
            open_exposure_usd=portfolio.open_exposure_usd,
            window_exposure_usd=window_exposure_usd,
            proposed_stake_usd=sizing.proposed_stake_usd,
            allowed_stake_usd=0.0,
            evidence={
                "signal_status": signal_evaluation.status.value,
                "triggered_rule_codes": rule_codes,
                "current_bankroll_usd": portfolio.current_bankroll_usd,
                "peak_bankroll_usd": portfolio.peak_bankroll_usd,
                "open_exposure_usd": portfolio.open_exposure_usd,
                "window_exposure_usd": window_exposure_usd,
                "proposed_stake_usd": sizing.proposed_stake_usd,
                "allowed_stake_usd": 0.0,
                "drawdown_pct": drawdown_pct,
            },
        )

    def _calculate_drawdown_pct(
        self,
        *,
        current_bankroll_usd: float,
        peak_bankroll_usd: float,
    ) -> float:
        if peak_bankroll_usd <= 0.0:
            return 0.0
        drawdown_usd = max(peak_bankroll_usd - current_bankroll_usd, 0.0)
        return drawdown_usd / peak_bankroll_usd

    def _cooldown_is_active(
        self,
        cooldown_active_until: str | None,
        *,
        now: datetime | None,
    ) -> bool:
        if not cooldown_active_until:
            return False
        current_time = now or datetime.now(UTC)
        target = datetime.fromisoformat(cooldown_active_until.replace("Z", "+00:00"))
        return current_time < target
