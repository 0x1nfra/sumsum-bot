"""SQLite-first storage boundary for scan runs and candidate persistence."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Iterable

from config.settings import ScanSettings, get_settings
from core.models import (
    CandidateRecord,
    CandidateStatus,
    RiskDecisionRecord,
    RiskDecisionStatus,
    ScanResultMetadata,
    SignalEvaluationRecord,
    SignalEvaluationStatus,
)


def _candidate_from_market(market: dict, status: CandidateStatus, reasons: Iterable[str] = ()) -> CandidateRecord:
    return CandidateRecord(
        market_id=market["id"],
        title=market["title"],
        status=status,
        location=market.get("expected_location") or "unknown",
        contract_family=market.get("expected_metric"),
        metric=market.get("expected_metric"),
        region=market.get("expected_region"),
        threshold=market.get("expected_threshold"),
        unit=market.get("expected_unit"),
        no_price=market.get("no_price"),
        liquidity_usd=market.get("liquidity_usd"),
        resolution_hours=market.get("expected_resolution_hours"),
        normalization_status=(
            CandidateStatus(market["expected_bucket"])
            if market.get("expected_bucket") in {status.value for status in CandidateStatus}
            else status
        ),
        rejection_reasons=tuple(reason for reason in reasons if reason),
    )


class CandidateStorage:
    """Repository-style interface for scanner persistence."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_settings(cls, settings: ScanSettings | None = None) -> "CandidateStorage":
        runtime_settings = settings or get_settings()
        return cls(runtime_settings.database_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def bootstrap(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS scan_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    candidate_count INTEGER NOT NULL,
                    approved_count INTEGER NOT NULL,
                    review_count INTEGER NOT NULL,
                    rejected_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS accepted_candidates (
                    market_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    contract_family TEXT,
                    metric TEXT,
                    location TEXT NOT NULL,
                    region TEXT,
                    threshold_value REAL,
                    unit TEXT,
                    no_price REAL,
                    liquidity_usd REAL,
                    resolution_hours INTEGER,
                    market_date_local TEXT,
                    market_window_start_local TEXT,
                    market_window_end_local TEXT,
                    location_key TEXT
                );

                CREATE TABLE IF NOT EXISTS review_candidates (
                    market_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    reasons_csv TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS rejected_candidates (
                    market_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    reasons_csv TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS scan_candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_run_id INTEGER NOT NULL,
                    market_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    metric TEXT,
                    region TEXT,
                    threshold_value REAL,
                    unit TEXT,
                    no_price REAL,
                    liquidity_usd REAL,
                    resolution_hours INTEGER,
                    contract_family TEXT,
                    market_date_local TEXT,
                    market_window_start_local TEXT,
                    market_window_end_local TEXT,
                    location_key TEXT,
                    normalization_status TEXT NOT NULL,
                    filter_status TEXT NOT NULL,
                    primary_reason TEXT,
                    reasons_csv TEXT NOT NULL,
                    FOREIGN KEY (scan_run_id) REFERENCES scan_runs(id)
                );

                CREATE TABLE IF NOT EXISTS signal_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    market_id TEXT NOT NULL,
                    scan_run_id INTEGER,
                    location TEXT NOT NULL,
                    mapping_city_key TEXT NOT NULL,
                    contract_family TEXT,
                    market_date_local TEXT,
                    market_window_start_local TEXT,
                    market_window_end_local TEXT,
                    forecast_update_time TEXT,
                    forecast_source_url TEXT,
                    no_price REAL NOT NULL,
                    derived_yes_probability REAL,
                    derived_no_probability REAL,
                    edge_against_no_price REAL,
                    decision_reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS risk_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    signal_evaluation_id INTEGER,
                    market_id TEXT NOT NULL,
                    window_key TEXT NOT NULL,
                    decision_status TEXT NOT NULL,
                    decision_reason TEXT NOT NULL,
                    triggered_rule_codes_csv TEXT NOT NULL,
                    current_bankroll_usd REAL NOT NULL,
                    peak_bankroll_usd REAL NOT NULL,
                    open_exposure_usd REAL NOT NULL,
                    window_exposure_usd REAL NOT NULL,
                    proposed_stake_usd REAL NOT NULL,
                    allowed_stake_usd REAL NOT NULL,
                    evidence_json TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            self._ensure_column(connection, "accepted_candidates", "contract_family", "TEXT")
            self._ensure_column(connection, "accepted_candidates", "market_date_local", "TEXT")
            self._ensure_column(connection, "accepted_candidates", "market_window_start_local", "TEXT")
            self._ensure_column(connection, "accepted_candidates", "market_window_end_local", "TEXT")
            self._ensure_column(connection, "accepted_candidates", "location_key", "TEXT")
            self._ensure_column(connection, "scan_candidates", "contract_family", "TEXT")
            self._ensure_column(connection, "scan_candidates", "market_date_local", "TEXT")
            self._ensure_column(connection, "scan_candidates", "market_window_start_local", "TEXT")
            self._ensure_column(connection, "scan_candidates", "market_window_end_local", "TEXT")
            self._ensure_column(connection, "scan_candidates", "location_key", "TEXT")

    def save_scan_run(self, metadata: ScanResultMetadata) -> int:
        self.bootstrap()
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO scan_runs (
                    source, candidate_count, approved_count, review_count, rejected_count
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    metadata.source,
                    metadata.candidate_count,
                    metadata.approved_count,
                    metadata.review_count,
                    metadata.rejected_count,
                ),
            )
            return int(cursor.lastrowid)

    def save_candidate(self, candidate: CandidateRecord) -> None:
        self.bootstrap()
        with self.connect() as connection:
            self._upsert_bucket_candidate(connection, candidate)

    def persist_scan_result(self, source: str, candidates: Iterable[CandidateRecord]) -> int:
        self.bootstrap()
        candidate_list = list(candidates)
        metadata = ScanResultMetadata(
            source=source,
            candidate_count=len(candidate_list),
            approved_count=sum(candidate.status is CandidateStatus.APPROVED for candidate in candidate_list),
            review_count=sum(candidate.status is CandidateStatus.REVIEW for candidate in candidate_list),
            rejected_count=sum(candidate.status is CandidateStatus.REJECTED for candidate in candidate_list),
        )
        scan_run_id = self.save_scan_run(metadata)

        with self.connect() as connection:
            for candidate in candidate_list:
                self._insert_scan_candidate(connection, scan_run_id, candidate)
                self._upsert_bucket_candidate(connection, candidate)
            connection.commit()

        return scan_run_id

    def persist_signal_evaluations(
        self,
        source: str,
        evaluations: Iterable[SignalEvaluationRecord],
    ) -> int:
        self.bootstrap()
        evaluation_list = list(evaluations)
        with self.connect() as connection:
            for evaluation in evaluation_list:
                self._insert_signal_evaluation(connection, source, evaluation)
            connection.commit()
        return len(evaluation_list)

    def list_signal_evaluations(
        self,
        market_id: str | None = None,
    ) -> list[SignalEvaluationRecord]:
        self.bootstrap()
        query = """
            SELECT id, market_id, scan_run_id, location, mapping_city_key, contract_family,
                   market_date_local, market_window_start_local, market_window_end_local,
                   forecast_update_time, forecast_source_url, no_price,
                   derived_yes_probability, derived_no_probability, edge_against_no_price,
                   decision_reason, status, evidence_json
            FROM signal_evaluations
        """
        params: tuple[object, ...] = ()
        if market_id is not None:
            query += " WHERE market_id = ?"
            params = (market_id,)
        query += " ORDER BY market_id, id"

        with self.connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            SignalEvaluationRecord(
                market_id=row["market_id"],
                scan_run_id=row["scan_run_id"],
                location=row["location"],
                mapping_city_key=row["mapping_city_key"],
                contract_family=row["contract_family"],
                market_date_local=row["market_date_local"],
                market_window_start_local=row["market_window_start_local"],
                market_window_end_local=row["market_window_end_local"],
                forecast_update_time=row["forecast_update_time"],
                forecast_source_url=row["forecast_source_url"],
                no_price=float(row["no_price"]),
                derived_yes_probability=row["derived_yes_probability"],
                derived_no_probability=row["derived_no_probability"],
                edge_against_no_price=row["edge_against_no_price"],
                decision_reason=row["decision_reason"],
                status=SignalEvaluationStatus(row["status"]),
                evidence=json.loads(row["evidence_json"]),
                signal_evaluation_id=int(row["id"]),
            )
            for row in rows
        ]

    def persist_risk_decisions(
        self,
        source: str,
        decisions: Iterable[RiskDecisionRecord],
    ) -> int:
        self.bootstrap()
        decision_list = list(decisions)
        with self.connect() as connection:
            for decision in decision_list:
                self._insert_risk_decision(connection, source, decision)
            connection.commit()
        return len(decision_list)

    def list_risk_decisions(
        self,
        market_id: str | None = None,
    ) -> list[RiskDecisionRecord]:
        self.bootstrap()
        query = """
            SELECT signal_evaluation_id, market_id, window_key, decision_status, decision_reason,
                   triggered_rule_codes_csv, current_bankroll_usd, peak_bankroll_usd,
                   open_exposure_usd, window_exposure_usd, proposed_stake_usd,
                   allowed_stake_usd, evidence_json, evaluated_at
            FROM risk_decisions
        """
        params: tuple[object, ...] = ()
        if market_id is not None:
            query += " WHERE market_id = ?"
            params = (market_id,)
        query += " ORDER BY id"

        with self.connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            RiskDecisionRecord(
                signal_evaluation_id=row["signal_evaluation_id"],
                market_id=row["market_id"],
                window_key=row["window_key"],
                decision_status=RiskDecisionStatus(row["decision_status"]),
                decision_reason=row["decision_reason"],
                triggered_rule_codes=tuple(
                    filter(None, str(row["triggered_rule_codes_csv"]).split(","))
                ),
                current_bankroll_usd=float(row["current_bankroll_usd"]),
                peak_bankroll_usd=float(row["peak_bankroll_usd"]),
                open_exposure_usd=float(row["open_exposure_usd"]),
                window_exposure_usd=float(row["window_exposure_usd"]),
                proposed_stake_usd=float(row["proposed_stake_usd"]),
                allowed_stake_usd=float(row["allowed_stake_usd"]),
                evidence=json.loads(row["evidence_json"]),
                evaluated_at=row["evaluated_at"],
            )
            for row in rows
        ]

    def list_candidates(self, status: CandidateStatus) -> list[CandidateRecord]:
        self.bootstrap()
        if status is CandidateStatus.APPROVED:
            query = """
                SELECT market_id, title, metric, location, region, threshold_value, unit,
                       no_price, liquidity_usd, resolution_hours, contract_family,
                       market_date_local, market_window_start_local, market_window_end_local, location_key
                FROM accepted_candidates ORDER BY market_id
            """
        elif status is CandidateStatus.REVIEW:
            query = """
                SELECT market_id, title, location, reasons_csv
                FROM review_candidates ORDER BY market_id
            """
        else:
            query = """
                SELECT market_id, title, location, reasons_csv
                FROM rejected_candidates ORDER BY market_id
            """

        with self.connect() as connection:
            rows = connection.execute(query).fetchall()

        candidates: list[CandidateRecord] = []
        for row in rows:
            if status is CandidateStatus.APPROVED:
                candidates.append(
                    CandidateRecord(
                        market_id=row["market_id"],
                        title=row["title"],
                        status=status,
                        location=row["location"],
                        contract_family=row["contract_family"] or row["metric"],
                        metric=row["metric"],
                        region=row["region"],
                        threshold=row["threshold_value"],
                        unit=row["unit"],
                        no_price=row["no_price"],
                        liquidity_usd=row["liquidity_usd"],
                        resolution_hours=row["resolution_hours"],
                        market_date_local=row["market_date_local"],
                        market_window_start_local=row["market_window_start_local"],
                        market_window_end_local=row["market_window_end_local"],
                        location_key=row["location_key"],
                        normalization_status=status,
                    )
                )
            else:
                reasons = tuple(filter(None, row["reasons_csv"].split(",")))
                candidates.append(
                    CandidateRecord(
                        market_id=row["market_id"],
                        title=row["title"],
                        status=status,
                        location=row["location"],
                        normalization_status=status,
                        rejection_reasons=reasons,
                    )
                )
        return candidates

    def _insert_scan_candidate(
        self,
        connection: sqlite3.Connection,
        scan_run_id: int,
        candidate: CandidateRecord,
    ) -> None:
        reasons_csv = ",".join(candidate.rejection_reasons)
        primary_reason = candidate.rejection_reasons[0] if candidate.rejection_reasons else None
        normalization_status = (candidate.normalization_status or candidate.status).value

        connection.execute(
            """
            INSERT INTO scan_candidates (
                scan_run_id, market_id, title, location, metric, region, threshold_value, unit,
                no_price, liquidity_usd, resolution_hours, contract_family, market_date_local,
                market_window_start_local, market_window_end_local, location_key,
                normalization_status, filter_status, primary_reason, reasons_csv
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scan_run_id,
                candidate.market_id,
                candidate.title,
                candidate.location,
                candidate.metric,
                candidate.region,
                candidate.threshold,
                candidate.unit,
                candidate.no_price,
                candidate.liquidity_usd,
                candidate.resolution_hours,
                candidate.contract_family or candidate.metric,
                candidate.market_date_local,
                candidate.market_window_start_local,
                candidate.market_window_end_local,
                candidate.location_key,
                normalization_status,
                candidate.status.value,
                primary_reason,
                reasons_csv,
            ),
        )

    def _upsert_bucket_candidate(
        self,
        connection: sqlite3.Connection,
        candidate: CandidateRecord,
    ) -> None:
        reasons_csv = ",".join(candidate.rejection_reasons)
        primary_reason = candidate.rejection_reasons[0] if candidate.rejection_reasons else ""
        for table_name in ("accepted_candidates", "review_candidates", "rejected_candidates"):
            connection.execute(
                f"DELETE FROM {table_name} WHERE market_id = ?",
                (candidate.market_id,),
            )

        if candidate.status is CandidateStatus.APPROVED:
            connection.execute(
                """
                INSERT OR REPLACE INTO accepted_candidates (
                    market_id, title, contract_family, metric, location, region, threshold_value, unit,
                    no_price, liquidity_usd, resolution_hours, market_date_local,
                    market_window_start_local, market_window_end_local, location_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.market_id,
                    candidate.title,
                    candidate.contract_family or candidate.metric,
                    candidate.metric,
                    candidate.location,
                    candidate.region,
                    candidate.threshold,
                    candidate.unit,
                    candidate.no_price,
                    candidate.liquidity_usd,
                    candidate.resolution_hours,
                    candidate.market_date_local,
                    candidate.market_window_start_local,
                    candidate.market_window_end_local,
                    candidate.location_key,
                ),
            )
            return

        table_name = (
            "review_candidates"
            if candidate.status is CandidateStatus.REVIEW
            else "rejected_candidates"
        )
        connection.execute(
            f"""
            INSERT OR REPLACE INTO {table_name} (
                market_id, title, location, reason, reasons_csv
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                candidate.market_id,
                candidate.title,
                candidate.location,
                primary_reason,
                reasons_csv,
            ),
        )

    def _ensure_column(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        column_name: str,
        column_type: str,
    ) -> None:
        columns = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        if column_name in columns:
            return
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

    def _insert_signal_evaluation(
        self,
        connection: sqlite3.Connection,
        source: str,
        evaluation: SignalEvaluationRecord,
    ) -> None:
        connection.execute(
            """
            INSERT INTO signal_evaluations (
                source, market_id, scan_run_id, location, mapping_city_key, contract_family,
                market_date_local, market_window_start_local, market_window_end_local,
                forecast_update_time, forecast_source_url, no_price,
                derived_yes_probability, derived_no_probability, edge_against_no_price,
                decision_reason, status, evidence_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                evaluation.market_id,
                evaluation.scan_run_id,
                evaluation.location,
                evaluation.mapping_city_key,
                evaluation.contract_family,
                evaluation.market_date_local,
                evaluation.market_window_start_local,
                evaluation.market_window_end_local,
                evaluation.forecast_update_time,
                evaluation.forecast_source_url,
                evaluation.no_price,
                evaluation.derived_yes_probability,
                evaluation.derived_no_probability,
                evaluation.edge_against_no_price,
                evaluation.decision_reason,
                evaluation.status.value,
                json.dumps(evaluation.evidence, sort_keys=True),
            ),
        )

    def _insert_risk_decision(
        self,
        connection: sqlite3.Connection,
        source: str,
        decision: RiskDecisionRecord,
    ) -> None:
        connection.execute(
            """
            INSERT INTO risk_decisions (
                source, signal_evaluation_id, market_id, window_key, decision_status,
                decision_reason, triggered_rule_codes_csv, current_bankroll_usd,
                peak_bankroll_usd, open_exposure_usd, window_exposure_usd,
                proposed_stake_usd, allowed_stake_usd, evidence_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                decision.signal_evaluation_id,
                decision.market_id,
                decision.window_key,
                decision.decision_status.value,
                decision.decision_reason,
                ",".join(decision.triggered_rule_codes),
                decision.current_bankroll_usd,
                decision.peak_bankroll_usd,
                decision.open_exposure_usd,
                decision.window_exposure_usd,
                decision.proposed_stake_usd,
                decision.allowed_stake_usd,
                json.dumps(decision.evidence, sort_keys=True),
            ),
        )


def bootstrap_storage(database_path: Path) -> sqlite3.Connection:
    storage = CandidateStorage(database_path)
    storage.bootstrap()
    connection = storage.connect()
    return connection


def save_approved_candidate(connection: sqlite3.Connection, market: dict) -> None:
    candidate = _candidate_from_market(market, CandidateStatus.APPROVED)
    storage = CandidateStorage(Path(connection.execute("PRAGMA database_list").fetchone()["file"]))
    storage._upsert_bucket_candidate(connection, candidate)
    connection.commit()


def save_rejected_candidate(connection: sqlite3.Connection, market: dict) -> None:
    status = (
        CandidateStatus.REVIEW
        if market["expected_bucket"] == CandidateStatus.REVIEW.value
        else CandidateStatus.REJECTED
    )
    candidate = _candidate_from_market(
        market,
        status,
        reasons=(market.get("expected_rejection_reason") or market["expected_bucket"],),
    )
    storage = CandidateStorage(Path(connection.execute("PRAGMA database_list").fetchone()["file"]))
    storage._upsert_bucket_candidate(connection, candidate)
    connection.commit()
