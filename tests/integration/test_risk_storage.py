from __future__ import annotations

from pathlib import Path

from core.models import RiskDecisionRecord, RiskDecisionStatus
from core.storage import CandidateStorage


def test_risk_storage_appends_allowed_and_blocked_decisions(
    temp_sqlite_db_path: Path,
) -> None:
    storage = CandidateStorage(temp_sqlite_db_path)

    inserted = storage.persist_risk_decisions(
        "signal-risk-gate",
        [
            RiskDecisionRecord(
                signal_evaluation_id=11,
                market_id="wx-temp-phx-001",
                window_key="2026-04-18T00:00:00-07:00",
                decision_status=RiskDecisionStatus.ALLOWED,
                decision_reason="edge_threshold_passed",
                triggered_rule_codes=(),
                current_bankroll_usd=100.0,
                peak_bankroll_usd=120.0,
                open_exposure_usd=8.0,
                window_exposure_usd=3.0,
                proposed_stake_usd=5.0,
                allowed_stake_usd=5.0,
                evidence={
                    "signal_status": "accepted",
                    "triggered_rule_codes": (),
                    "allowed_stake_usd": 5.0,
                },
            ),
            RiskDecisionRecord(
                signal_evaluation_id=12,
                market_id="wx-temp-phx-001",
                window_key="2026-04-18T00:00:00-07:00",
                decision_status=RiskDecisionStatus.BLOCKED,
                decision_reason="drawdown_halt_active",
                triggered_rule_codes=("drawdown_halt_active", "cooldown_active"),
                current_bankroll_usd=80.0,
                peak_bankroll_usd=120.0,
                open_exposure_usd=8.0,
                window_exposure_usd=3.0,
                proposed_stake_usd=4.0,
                allowed_stake_usd=0.0,
                evidence={
                    "signal_status": "accepted",
                    "triggered_rule_codes": ("drawdown_halt_active", "cooldown_active"),
                    "allowed_stake_usd": 0.0,
                },
            ),
        ],
    )

    assert inserted == 2

    with storage.connect() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
            ).fetchall()
        }
        rows = connection.execute(
            """
            SELECT signal_evaluation_id, decision_status, decision_reason, triggered_rule_codes_csv
            FROM risk_decisions
            ORDER BY id
            """
        ).fetchall()

    assert "risk_decisions" in tables
    assert [tuple(row) for row in rows] == [
        (11, "allowed", "edge_threshold_passed", ""),
        (12, "blocked", "drawdown_halt_active", "drawdown_halt_active,cooldown_active"),
    ]

    listed = storage.list_risk_decisions("wx-temp-phx-001")
    assert [record.decision_status for record in listed] == [
        RiskDecisionStatus.ALLOWED,
        RiskDecisionStatus.BLOCKED,
    ]
    assert listed[1].triggered_rule_codes == ("drawdown_halt_active", "cooldown_active")
