"""Reusable paper-trading runtime orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import time
from typing import Callable, Mapping, Sequence

from config.settings import ScanSettings, get_settings
from core.clob_client import normalize_terminal_state_fields
from core.market_scanner import MarketScanner
from core.models import (
    BankrollSnapshot,
    PaperPositionRecord,
    PortfolioSnapshot,
    RiskDecisionRecord,
    RiskDecisionStatus,
)
from core.paper_execution import activate_position, create_paper_entry, settle_position
from core.storage import CandidateStorage
from strategies.weather.signal_engine import SignalEngine

RESOLVER_MATRIX: dict[str, tuple[object, ...]] = {
    "closed": (True,),
    "closedTime": ("required",),
    "resolvedBy": ("required",),
    "umaResolutionStatus": ("resolved", "approved", "settled"),
}
live_execution_forbidden = True


@dataclass(frozen=True)
class TerminalResolution:
    market_id: str
    settled_yes: bool
    resolver_matrix: str = "polymarket"


class FixtureMarketProvider:
    """Load fixture payloads for discovery and resolution polling."""

    def load_fixture_payload(self, fixture_path: Path | None) -> dict | list[dict]:
        if fixture_path is None:
            return {"markets": []}
        return _load_fixture_payload(fixture_path)


class PaperRuntime:
    """Run the paper-trading passes over scan, signal, risk, entry, and settlement."""

    def __init__(
        self,
        *,
        settings: ScanSettings | None = None,
        storage: CandidateStorage | None = None,
        scanner: MarketScanner | None = None,
        signal_engine: SignalEngine | None = None,
        market_provider: object | None = None,
        resolver: object | None = None,
        observer: Callable[[str], None] | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.storage = storage or CandidateStorage.from_settings(self.settings)
        self.scanner = scanner or MarketScanner(settings=self.settings)
        self.signal_engine = signal_engine or SignalEngine(storage=self.storage, settings=self.settings)
        self.market_provider = market_provider or FixtureMarketProvider()
        self.resolver = resolver or self
        self.observer = observer

    def run_once(self, *, mode: str, fixture_path: Path | None) -> dict[str, object]:
        self.storage.bootstrap()
        payload = self.market_provider.load_fixture_payload(fixture_path)
        restored_positions = self._restore_open_positions()

        self._emit("scan_pass")
        scan_result = self.scanner.run_scan(payload, storage=self.storage)
        self._emit("signal_pass")
        signal_result = self.signal_engine.evaluate_candidates(scan_result.approved)

        self._emit("risk_pass")
        risk_result = self.signal_engine.evaluate_risk_for_signal(
            signal_result.accepted,
            portfolio=self._portfolio_snapshot(),
        )

        self._emit("entry_pass")
        signal_prices = {
            signal.market_id: signal.no_price
            for signal in signal_result.accepted
        }
        entered_positions = self._enter_allowed_positions(risk_result.allowed, signal_prices)

        self._emit("resolution_pass")
        resolved_positions = self._resolve_open_positions(
            restored_positions + entered_positions,
            payload,
        )

        return {
            "mode": mode,
            "accepted_candidates": len(scan_result.approved),
            "accepted_signals": len(signal_result.accepted),
            "allowed_decisions": len(risk_result.allowed),
            "entered_positions": len(entered_positions),
            "resolved_positions": resolved_positions,
            "open_positions": len(self.storage.list_open_paper_positions()),
            "restored_positions": len(restored_positions),
            "resolver_matrix": self._resolver_matrix_name(payload),
            "live_execution_forbidden": live_execution_forbidden,
        }

    def run_loop(
        self,
        *,
        fixture_path: Path | None,
        interval_seconds: int | None = None,
        iterations: int | None = None,
    ) -> list[dict[str, object]]:
        wait_seconds = self.settings.paper_poll_interval_seconds if interval_seconds is None else interval_seconds
        run_summaries: list[dict[str, object]] = []
        iteration = 0
        while iterations is None or iteration < iterations:
            iteration += 1
            run_summaries.append(self.run_once(mode="paper-loop", fixture_path=fixture_path))
            if iterations is not None and iteration >= iterations:
                break
            if wait_seconds > 0:
                time.sleep(wait_seconds)
        return run_summaries

    def resolve_market_terminal_state(self, market_payload: Mapping[str, object]) -> TerminalResolution | None:
        normalized = normalize_terminal_state_fields(market_payload)
        closed = normalized["closed"]
        closed_time = normalized["closedTime"]
        resolved_by = normalized["resolvedBy"]
        resolution_status = normalized["umaResolutionStatus"]
        if closed not in RESOLVER_MATRIX["closed"]:
            return None
        if not closed_time:
            return None
        if not resolved_by:
            return None
        if not isinstance(resolution_status, str):
            return None
        if resolution_status.lower() not in RESOLVER_MATRIX["umaResolutionStatus"]:
            return None

        outcome = market_payload.get("outcome")
        if outcome == "yes":
            settled_yes = True
        elif outcome == "no":
            settled_yes = False
        else:
            settled_yes = bool(market_payload.get("settled_yes", False))

        market_id = str(market_payload.get("id", ""))
        if not market_id:
            return None
        return TerminalResolution(
            market_id=market_id,
            settled_yes=settled_yes,
        )

    def _restore_open_positions(self) -> list[PaperPositionRecord]:
        self._emit("restore_open_positions")
        return self.storage.list_open_paper_positions()

    def _enter_allowed_positions(
        self,
        decisions: Sequence[RiskDecisionRecord],
        signal_prices: Mapping[str, float],
    ) -> list[PaperPositionRecord]:
        latest_snapshot = self._latest_snapshot()
        open_positions = self.storage.list_open_paper_positions()
        open_keys = {
            (position.market_id, str(position.evidence.get("window_key", "")))
            for position in open_positions
        }
        entered_positions: list[PaperPositionRecord] = []
        snapshot = latest_snapshot

        for decision in decisions:
            if decision.decision_status is not RiskDecisionStatus.ALLOWED:
                continue
            dedupe_key = (decision.market_id, decision.window_key)
            if dedupe_key in open_keys:
                continue

            timestamp = _utc_now()
            no_price = signal_prices.get(
                decision.market_id,
                float(decision.evidence.get("entry_price", decision.evidence.get("no_price", 0.0)) or 0.0),
            )
            entered_position, entry_events, entry_snapshots = create_paper_entry(
                risk_decision=decision,
                no_price=no_price,
                captured_at=timestamp,
            )
            self.storage.persist_paper_position(
                PaperPositionRecord(
                    **{
                        **entered_position.__dict__,
                        "evidence": {
                            **entered_position.evidence,
                            "window_key": decision.window_key,
                            "live_execution_forbidden": live_execution_forbidden,
                        },
                    }
                )
            )
            self.storage.persist_paper_trade_events(entry_events)
            self.storage.persist_bankroll_snapshots(entry_snapshots)
            snapshot = entry_snapshots[-1]

            activated_position, open_events, open_snapshots = activate_position(
                position=self.storage.list_paper_positions()[-1],
                bankroll_snapshot=snapshot,
                activated_at=_utc_now(),
            )
            self.storage.persist_paper_position(activated_position)
            self.storage.persist_paper_trade_events(open_events)
            self.storage.persist_bankroll_snapshots(open_snapshots)
            snapshot = open_snapshots[-1]

            entered_positions.append(activated_position)
            open_keys.add(dedupe_key)

        return entered_positions

    def _resolve_open_positions(
        self,
        positions: Sequence[PaperPositionRecord],
        payload: dict | list[dict],
    ) -> int:
        if not positions:
            return 0
        market_index = _market_index(payload)
        resolved_count = 0

        for position in positions:
            market_payload = market_index.get(position.market_id)
            if market_payload is None:
                continue
            resolution = self.resolver.resolve_market_terminal_state(market_payload)
            if resolution is None:
                continue

            latest_snapshot = self._latest_snapshot()
            settled_yes = (
                bool(resolution.get("settled_yes", False))
                if isinstance(resolution, Mapping)
                else resolution.settled_yes
            )
            resolved_position, resolution_events, resolution_snapshots = settle_position(
                position=position,
                bankroll_snapshot=latest_snapshot,
                settled_yes=settled_yes,
                settled_at=_utc_now(),
            )
            self.storage.persist_paper_position(resolved_position)
            self.storage.persist_paper_trade_events(resolution_events)
            self.storage.persist_bankroll_snapshots(resolution_snapshots)
            resolved_count += 1

        return resolved_count

    def _portfolio_snapshot(self) -> PortfolioSnapshot:
        snapshot = self._latest_snapshot()
        open_positions = self.storage.list_open_paper_positions()
        open_exposure_by_window: dict[str, float] = {}
        for position in open_positions:
            window_key = str(position.evidence.get("window_key", position.market_id))
            open_exposure_by_window[window_key] = open_exposure_by_window.get(window_key, 0.0) + position.stake_usd

        return PortfolioSnapshot(
            current_bankroll_usd=snapshot.current_bankroll_usd,
            peak_bankroll_usd=snapshot.peak_bankroll_usd,
            open_exposure_usd=sum(position.stake_usd for position in open_positions),
            open_exposure_by_window=open_exposure_by_window,
            captured_at=snapshot.captured_at,
        )

    def _latest_snapshot(self) -> BankrollSnapshot:
        snapshots = self.storage.list_bankroll_snapshots()
        if snapshots:
            return snapshots[-1]
        return BankrollSnapshot(
            current_bankroll_usd=self.settings.paper_starting_bankroll_usd,
            peak_bankroll_usd=self.settings.paper_starting_bankroll_usd,
            available_cash_usd=self.settings.paper_starting_bankroll_usd,
            open_exposure_usd=0.0,
            snapshot_reason="paper_runtime_bootstrap",
            captured_at=_utc_now(),
        )

    def _resolver_matrix_name(self, payload: dict | list[dict]) -> str:
        if hasattr(self.resolver, "__class__") and self.resolver.__class__.__name__ != "PaperRuntime":
            return "stub"
        market_index = _market_index(payload)
        for market_payload in market_index.values():
            resolution = self.resolver.resolve_market_terminal_state(market_payload)
            if resolution is None:
                continue
            if isinstance(resolution, Mapping):
                return str(resolution.get("resolver_matrix", "polymarket"))
            return resolution.resolver_matrix
        return "fail-closed"

    def _emit(self, event: str) -> None:
        if self.observer is not None:
            self.observer(event)


def _load_fixture_payload(path: Path) -> dict | list[dict]:
    import json

    return json.loads(path.read_text())


def _market_index(payload: dict | list[dict]) -> dict[str, Mapping[str, object]]:
    markets: Sequence[Mapping[str, object]]
    if isinstance(payload, dict):
        raw_markets = payload.get("markets", [])
        markets = raw_markets if isinstance(raw_markets, Sequence) else []
    else:
        markets = payload
    return {
        str(market.get("id")): market
        for market in markets
        if isinstance(market, Mapping) and market.get("id") is not None
    }


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
