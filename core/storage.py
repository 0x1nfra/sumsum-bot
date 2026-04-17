"""SQLite-first storage boundary for scan runs and candidate persistence."""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Iterable

from config.settings import ScanSettings, get_settings
from core.models import CandidateRecord, CandidateStatus, ScanResultMetadata


def _candidate_from_market(market: dict, status: CandidateStatus, reasons: Iterable[str] = ()) -> CandidateRecord:
    return CandidateRecord(
        market_id=market["id"],
        title=market["title"],
        status=status,
        location=market.get("expected_location") or "unknown",
        metric=market.get("expected_metric"),
        region=market.get("expected_region"),
        threshold=market.get("expected_threshold"),
        unit=market.get("expected_unit"),
        no_price=market.get("no_price"),
        liquidity_usd=market.get("liquidity_usd"),
        resolution_hours=market.get("expected_resolution_hours"),
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
                    metric TEXT,
                    location TEXT NOT NULL,
                    region TEXT,
                    threshold_value REAL,
                    unit TEXT,
                    no_price REAL,
                    liquidity_usd REAL,
                    resolution_hours INTEGER
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
                """
            )

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
        reasons_csv = ",".join(candidate.rejection_reasons)
        primary_reason = candidate.rejection_reasons[0] if candidate.rejection_reasons else ""

        with self.connect() as connection:
            if candidate.status is CandidateStatus.APPROVED:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO accepted_candidates (
                        market_id, title, metric, location, region, threshold_value, unit,
                        no_price, liquidity_usd, resolution_hours
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        candidate.market_id,
                        candidate.title,
                        candidate.metric,
                        candidate.location,
                        candidate.region,
                        candidate.threshold,
                        candidate.unit,
                        candidate.no_price,
                        candidate.liquidity_usd,
                        candidate.resolution_hours,
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

    def list_candidates(self, status: CandidateStatus) -> list[CandidateRecord]:
        self.bootstrap()
        if status is CandidateStatus.APPROVED:
            query = """
                SELECT market_id, title, metric, location, region, threshold_value, unit,
                       no_price, liquidity_usd, resolution_hours
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
                        metric=row["metric"],
                        region=row["region"],
                        threshold=row["threshold_value"],
                        unit=row["unit"],
                        no_price=row["no_price"],
                        liquidity_usd=row["liquidity_usd"],
                        resolution_hours=row["resolution_hours"],
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
                        rejection_reasons=reasons,
                    )
                )
        return candidates


def bootstrap_storage(database_path: Path) -> sqlite3.Connection:
    storage = CandidateStorage(database_path)
    storage.bootstrap()
    connection = storage.connect()
    return connection


def save_approved_candidate(connection: sqlite3.Connection, market: dict) -> None:
    candidate = _candidate_from_market(market, CandidateStatus.APPROVED)
    connection.execute(
        """
        INSERT OR REPLACE INTO accepted_candidates (
            market_id, title, metric, location, region, threshold_value, unit,
            no_price, liquidity_usd, resolution_hours
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate.market_id,
            candidate.title,
            candidate.metric,
            candidate.location,
            candidate.region,
            candidate.threshold,
            candidate.unit,
            candidate.no_price,
            candidate.liquidity_usd,
            candidate.resolution_hours,
        ),
    )
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
    table_name = "review_candidates" if status is CandidateStatus.REVIEW else "rejected_candidates"
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
            candidate.rejection_reasons[0],
            ",".join(candidate.rejection_reasons),
        ),
    )
    connection.commit()
