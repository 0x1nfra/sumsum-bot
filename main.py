"""Operator-facing scan entrypoints for market discovery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Sequence

from config.settings import ScanSettings, get_settings
from core.market_scanner import MarketScanResult, MarketScanner
from core.storage import CandidateStorage


def build_parser() -> argparse.ArgumentParser:
    settings = get_settings()

    parser = argparse.ArgumentParser(description="Run Sumsum Bot market discovery scans.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    scan_once = subcommands.add_parser("scan-once", help="Run one scan using fixture payload data.")
    _add_scan_arguments(scan_once, settings)

    scan_loop = subcommands.add_parser("scan-loop", help="Run a bounded scan loop using fixture payload data.")
    _add_scan_arguments(scan_loop, settings)
    scan_loop.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of scan iterations to run before exiting.",
    )

    return parser


def _add_scan_arguments(parser: argparse.ArgumentParser, settings: ScanSettings) -> None:
    parser.add_argument(
        "--fixture",
        type=Path,
        required=True,
        help="Path to a Polymarket discovery fixture JSON file.",
    )
    parser.add_argument(
        "--database-path",
        default=settings.database_path,
        help="SQLite database path used for persisted scan output.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=settings.scan_interval_seconds,
        help="Seconds to wait between scan-loop iterations.",
    )
    parser.add_argument(
        "--min-liquidity",
        type=int,
        default=settings.min_market_liquidity_usd,
        help="Minimum market liquidity for approval.",
    )
    parser.add_argument(
        "--max-entry-price",
        type=float,
        default=settings.max_entry_price,
        help="Maximum entry price ceiling for approval.",
    )
    parser.add_argument(
        "--max-resolution-hours",
        type=int,
        default=settings.max_resolution_hours,
        help="Maximum allowed hours to resolution for approval.",
    )


def load_fixture_payload(path: Path) -> dict | list[dict]:
    return json.loads(path.read_text())


def build_runtime_settings(args: argparse.Namespace) -> ScanSettings:
    return ScanSettings(
        database_path=args.database_path,
        min_market_liquidity_usd=args.min_liquidity,
        max_entry_price=args.max_entry_price,
        max_resolution_hours=args.max_resolution_hours,
        scan_interval_seconds=args.interval,
    )


def summarize_result(result: MarketScanResult, iteration: int | None = None) -> dict[str, object]:
    summary: dict[str, object] = {
        "accepted": len(result.approved),
        "review": len(result.review),
        "rejected": len(result.rejected),
        "scan_run_id": result.scan_run_id,
        "accepted_ids": [candidate.market_id for candidate in result.approved],
        "review_ids": [candidate.market_id for candidate in result.review],
        "rejected_ids": [candidate.market_id for candidate in result.rejected],
    }
    if iteration is not None:
        summary["iteration"] = iteration
    return summary


def run_scan_once(args: argparse.Namespace) -> int:
    settings = build_runtime_settings(args)
    payload = load_fixture_payload(args.fixture)
    scanner = MarketScanner(settings=settings)
    storage = CandidateStorage.from_settings(settings)
    result = scanner.run_scan(payload, storage=storage)
    print(json.dumps({"mode": "scan-once", **summarize_result(result)}, sort_keys=True))
    return 0


def run_scan_loop(args: argparse.Namespace) -> int:
    settings = build_runtime_settings(args)
    payload = load_fixture_payload(args.fixture)
    scanner = MarketScanner(settings=settings)
    storage = CandidateStorage.from_settings(settings)

    runs: list[dict[str, object]] = []
    for iteration in range(1, args.iterations + 1):
        result = scanner.run_scan(payload, storage=storage)
        run_summary = summarize_result(result, iteration=iteration)
        runs.append(run_summary)
        print(json.dumps({"mode": "scan-loop", **run_summary}, sort_keys=True))
        if iteration < args.iterations and settings.scan_interval_seconds > 0:
            time.sleep(settings.scan_interval_seconds)

    print(json.dumps({"mode": "scan-loop-summary", "iterations": args.iterations, "runs": runs}, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan-once":
        return run_scan_once(args)
    if args.command == "scan-loop":
        return run_scan_loop(args)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
