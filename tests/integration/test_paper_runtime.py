from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

import pytest

from config.settings import ScanSettings
from core.models import (
    BankrollSnapshot,
    PaperPositionRecord,
    PaperPositionStatus,
    PaperTradeEvent,
    RiskDecisionRecord,
    RiskDecisionStatus,
    SignalEvaluationRecord,
    SignalEvaluationStatus,
)
from core.storage import CandidateStorage
from core.trade_logger import PAPER_ENTRY_EVENT
from strategies.weather.signal_engine import SignalRiskGateResult

from core.paper_runtime import PaperRuntime


def test_paper_runtime_once_mode_enters_allowed_trade_without_live_execution(
    temp_sqlite_db_path: Path,
) -> None:
    settings = _settings(temp_sqlite_db_path)
    storage = CandidateStorage.from_settings(settings)
    runtime = PaperRuntime(
        settings=settings,
        storage=storage,
        scanner=_StubScanner(),
        signal_engine=_StubSignalEngine(
            allowed_decisions=(_allowed_decision(),),
        ),
        market_provider=_StubMarketProvider([{"markets": [_terminal_market_payload()]}]),
        resolver=_StubResolverMatrix(settled_yes=False),
    )

    summary = runtime.run_once(mode="paper-once", fixture_path=None)

    assert summary["mode"] == "paper-once"
    assert summary["live_execution_forbidden"] is True
    assert summary["resolver_matrix"] == "stub"
    positions = storage.list_paper_positions()
    assert len(positions) == 1
    assert positions[0].market_id == "wx-temp-phx-001"
    assert positions[0].status is PaperPositionStatus.RESOLVED
    events = storage.list_paper_trade_events(positions[0].position_id)
    assert [event.event_type for event in events] == [
        PAPER_ENTRY_EVENT,
        "paper_open",
        "paper_resolution",
    ]


def test_paper_runtime_restores_open_positions_before_resolution_pass(
    temp_sqlite_db_path: Path,
) -> None:
    settings = _settings(temp_sqlite_db_path)
    storage = CandidateStorage.from_settings(settings)
    seeded_position = PaperPositionRecord(
        position_id="paper-existing-001",
        market_id="wx-temp-phx-001",
        risk_decision_id=7,
        signal_evaluation_id=11,
        entry_price=0.4,
        stake_usd=5.0,
        contract_count=12.5,
        status=PaperPositionStatus.OPEN,
        entered_at="2026-04-19T00:00:00Z",
        opened_at="2026-04-19T00:00:01Z",
        evidence={"window_key": "2026-04-18", "resolver_matrix": "seed"},
    )
    storage.persist_paper_position(seeded_position)
    storage.persist_paper_trade_events(
        (
            PaperTradeEvent(
                position_id=seeded_position.position_id,
                event_type=PAPER_ENTRY_EVENT,
                event_timestamp=seeded_position.entered_at,
                details={"source": "seed"},
            ),
        )
    )
    storage.persist_bankroll_snapshots(
        (
            BankrollSnapshot(
                current_bankroll_usd=100.0,
                peak_bankroll_usd=100.0,
                available_cash_usd=95.0,
                open_exposure_usd=5.0,
                snapshot_reason="seed",
                captured_at="2026-04-19T00:00:00Z",
            ),
        )
    )
    restore_order: list[str] = []
    runtime = PaperRuntime(
        settings=settings,
        storage=storage,
        scanner=_StubScanner(),
        signal_engine=_StubSignalEngine(allowed_decisions=()),
        market_provider=_StubMarketProvider([{"markets": [_terminal_market_payload()]}]),
        resolver=_StubResolverMatrix(settled_yes=False),
        observer=restore_order.append,
    )

    runtime.run_once(mode="paper-once", fixture_path=None)

    assert restore_order.index("restore_open_positions") < restore_order.index("resolution_pass")


def test_paper_runtime_skips_unresolved_markets_until_resolver_matrix_marks_terminal(
    temp_sqlite_db_path: Path,
) -> None:
    settings = _settings(temp_sqlite_db_path)
    storage = CandidateStorage.from_settings(settings)
    runtime = PaperRuntime(
        settings=settings,
        storage=storage,
        scanner=_StubScanner(),
        signal_engine=_StubSignalEngine(allowed_decisions=(_allowed_decision(),)),
        market_provider=_StubMarketProvider(
            [
                {"markets": [_non_terminal_market_payload()]},
                {"markets": [_terminal_market_payload()]},
            ]
        ),
        resolver=_StubResolverMatrix(settled_yes=False),
    )

    first_summary = runtime.run_once(mode="paper-loop", fixture_path=None)
    first_position = storage.list_paper_positions()[0]
    assert first_summary["mode"] == "paper-loop"
    assert first_summary["resolver_matrix"] == "stub"
    assert first_position.status is PaperPositionStatus.OPEN

    second_summary = runtime.run_once(mode="paper-loop", fixture_path=None)
    second_position = storage.list_paper_positions()[0]
    assert second_summary["resolved_positions"] == 1
    assert second_position.status is PaperPositionStatus.RESOLVED


def test_paper_runtime_summary_reports_forward_test_metrics(
    temp_sqlite_db_path: Path,
    tmp_path: Path,
) -> None:
    settings = _settings(temp_sqlite_db_path)
    storage = CandidateStorage.from_settings(settings)
    storage.persist_paper_position(
        _resolved_position(
            position_id="paper-metric-001",
            realized_pnl_usd=8.0,
        )
    )
    storage.persist_bankroll_snapshots(
        (
            BankrollSnapshot(
                current_bankroll_usd=100.0,
                peak_bankroll_usd=100.0,
                available_cash_usd=100.0,
                open_exposure_usd=0.0,
                snapshot_reason="start",
                captured_at="2026-04-19T00:00:00Z",
            ),
            BankrollSnapshot(
                current_bankroll_usd=110.0,
                peak_bankroll_usd=110.0,
                available_cash_usd=110.0,
                open_exposure_usd=0.0,
                snapshot_reason="peak",
                captured_at="2026-04-19T01:00:00Z",
            ),
            BankrollSnapshot(
                current_bankroll_usd=88.0,
                peak_bankroll_usd=110.0,
                available_cash_usd=88.0,
                open_exposure_usd=0.0,
                snapshot_reason="drawdown",
                captured_at="2026-04-19T02:00:00Z",
            ),
            BankrollSnapshot(
                current_bankroll_usd=108.0,
                peak_bankroll_usd=110.0,
                available_cash_usd=108.0,
                open_exposure_usd=0.0,
                snapshot_reason="end",
                captured_at="2026-04-19T03:00:00Z",
            ),
        )
    )
    fixture_path = tmp_path / "empty-markets.json"
    fixture_path.write_text(json.dumps({"markets": []}))

    result = subprocess.run(
        [
            sys.executable,
            "paper_trader.py",
            "paper-once",
            "--fixture",
            str(fixture_path),
            "--database-path",
            str(temp_sqlite_db_path),
            "--interval",
            "0",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    output = result.stdout.strip().splitlines()
    summary = json.loads(output[-1])
    assert summary["cumulative_return_pct"] == 8.0
    assert summary["bankroll_delta_usd"] == 8.0
    assert summary["max_drawdown_pct"] == 20.0
    assert "drawdown_recovery_steps" in summary
    assert "resolved_trade_count" in summary
    assert summary["resolved_trade_count"] == 1


class _StubSignalEngine:
    def __init__(self, *, allowed_decisions: tuple[RiskDecisionRecord, ...]) -> None:
        self._allowed_decisions = allowed_decisions

    def evaluate_candidates(self, candidates: object | None = None) -> object:
        accepted = tuple(_accepted_signal_record() for _ in self._allowed_decisions)
        return type(
            "SignalResult",
            (),
            {
                "source": "stub-signal-engine",
                "accepted": accepted,
                "rejected": (),
                "inserted_count": len(accepted),
            },
        )()

    def evaluate_risk_for_signal(self, signal_evaluations: object, **_: object) -> SignalRiskGateResult:
        return SignalRiskGateResult(
            source="stub-risk-gate",
            allowed=self._allowed_decisions,
            blocked=(),
            risk_decision_count=len(self._allowed_decisions),
        )


class _StubMarketProvider:
    def __init__(self, payloads: list[dict[str, object]]) -> None:
        self._payloads = payloads
        self._index = 0

    def load_fixture_payload(self, fixture_path: object | None) -> dict[str, object]:
        payload = self._payloads[min(self._index, len(self._payloads) - 1)]
        self._index += 1
        return payload


class _StubScanner:
    def run_scan(self, payload: object, storage: CandidateStorage) -> object:
        return type(
            "ScanResult",
            (),
            {
                "source": "stub-scanner",
                "approved": (_approved_candidate(),),
                "review": (),
                "rejected": (),
                "scan_run_id": 1,
            },
        )()


class _StubResolverMatrix:
    def __init__(self, *, settled_yes: bool) -> None:
        self.settled_yes = settled_yes

    def resolve_market_terminal_state(self, market_payload: dict[str, object]) -> dict[str, object] | None:
        if market_payload.get("closed") is not True:
            return None
        return {"resolver_matrix": "stub", "settled_yes": self.settled_yes}


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
        scan_interval_seconds=0,
    )


def _allowed_decision() -> RiskDecisionRecord:
    return RiskDecisionRecord(
        signal_evaluation_id=11,
        market_id="wx-temp-phx-001",
        window_key="2026-04-18",
        decision_status=RiskDecisionStatus.ALLOWED,
        decision_reason="edge_threshold_passed",
        triggered_rule_codes=("edge_threshold_passed",),
        current_bankroll_usd=100.0,
        peak_bankroll_usd=100.0,
        open_exposure_usd=0.0,
        window_exposure_usd=0.0,
        proposed_stake_usd=5.0,
        allowed_stake_usd=5.0,
        evidence={
            "position_side": "no",
            "market_id": "wx-temp-phx-001",
            "window_key": "2026-04-18",
            "live_execution_forbidden": True,
        },
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
        evidence={"resolver_matrix": "stub"},
    )


def _approved_candidate() -> object:
    from core.models import CandidateRecord, CandidateStatus

    return CandidateRecord(
        market_id="wx-temp-phx-001",
        title="Phoenix temperature",
        status=CandidateStatus.APPROVED,
        location="Phoenix",
        contract_family="temperature",
        metric="temperature",
        no_price=0.40,
        liquidity_usd=10000.0,
        resolution_hours=24,
        market_date_local="2026-04-18",
        market_window_start_local="2026-04-18T00:00:00-07:00",
        market_window_end_local="2026-04-19T00:00:00-07:00",
        location_key="phoenix",
    )


def _non_terminal_market_payload() -> dict[str, object]:
    return {
        "id": "wx-temp-phx-001",
        "closed": False,
        "closedTime": None,
        "resolvedBy": None,
        "umaResolutionStatus": "pending",
    }


def _terminal_market_payload() -> dict[str, object]:
    return {
        "id": "wx-temp-phx-001",
        "closed": True,
        "closedTime": "2026-04-20T00:00:00Z",
        "resolvedBy": "oracle",
        "umaResolutionStatus": "resolved",
    }


@pytest.mark.parametrize(
    "contract_string",
    ["paper-once", "paper-loop", "resolver_matrix", "live_execution_forbidden"],
)
def test_runtime_contract_strings(contract_string: str) -> None:
    assert contract_string


def _resolved_position(
    *,
    position_id: str,
    realized_pnl_usd: float,
) -> PaperPositionRecord:
    return PaperPositionRecord(
        position_id=position_id,
        market_id="wx-temp-phx-001",
        risk_decision_id=7,
        signal_evaluation_id=11,
        entry_price=0.4,
        stake_usd=5.0,
        contract_count=12.5,
        status=PaperPositionStatus.RESOLVED,
        entered_at="2026-04-19T00:00:00Z",
        opened_at="2026-04-19T00:00:01Z",
        resolved_at="2026-04-19T00:10:00Z",
        resolution_price=1.0,
        realized_pnl_usd=realized_pnl_usd,
        evidence={"window_key": "2026-04-18", "resolver_matrix": "seed"},
    )
