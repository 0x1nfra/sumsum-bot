"""Operator-facing paper-trading CLI."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from config.settings import ScanSettings, get_settings
from core.paper_runtime import PaperRuntime
from main import add_runtime_arguments

PAPER_RUNTIME_ARGUMENTS = ("--fixture", "--database-path", "--interval")
FORWARD_TEST_METRIC_KEYS = (
    "starting_bankroll_usd",
    "current_bankroll_usd",
    "bankroll_delta_usd",
    "cumulative_return_pct",
    "max_drawdown_pct",
    "drawdown_recovery_steps",
    "resolved_trade_count",
    "win_rate_pct",
)


def build_parser() -> argparse.ArgumentParser:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run Sumsum Bot paper-trading runtime.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    paper_once = subcommands.add_parser("paper-once", help="Run one paper-trading pass.")
    add_runtime_arguments(paper_once, settings)

    paper_loop = subcommands.add_parser("paper-loop", help="Run the paper-trading loop.")
    add_runtime_arguments(paper_loop, settings)
    paper_loop.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of paper-loop iterations to run before exiting.",
    )

    return parser


def run_paper_once(args: argparse.Namespace) -> int:
    settings = _build_paper_runtime_settings(args)
    runtime = PaperRuntime(settings=settings)
    summary = runtime.run_once(mode="paper-once", fixture_path=args.fixture)
    print(json.dumps(_summary_payload(summary), sort_keys=True))
    return 0


def run_paper_loop(args: argparse.Namespace) -> int:
    settings = _build_paper_runtime_settings(args)
    runtime = PaperRuntime(settings=settings)
    run_summaries = runtime.run_loop(
        fixture_path=args.fixture,
        interval_seconds=args.interval,
        iterations=args.iterations,
    )
    for iteration, summary in enumerate(run_summaries, start=1):
        print(json.dumps({"iteration": iteration, **_summary_payload(summary)}, sort_keys=True))
    final_metrics = _summary_payload(run_summaries[-1]) if run_summaries else {}
    print(json.dumps({"mode": "paper-loop-summary", "iterations": len(run_summaries), **final_metrics}, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "paper-once":
        return run_paper_once(args)
    if args.command == "paper-loop":
        return run_paper_loop(args)

    parser.error(f"unsupported command: {args.command}")
    return 2


def _summary_payload(summary: dict[str, object]) -> dict[str, object]:
    return {
        **summary,
        **{
            key: summary[key]
            for key in FORWARD_TEST_METRIC_KEYS
            if key in summary
        },
    }


def _build_paper_runtime_settings(args: argparse.Namespace) -> ScanSettings:
    settings = get_settings()
    return ScanSettings(
        database_path=args.database_path,
        min_market_liquidity_usd=settings.min_market_liquidity_usd,
        max_entry_price=settings.max_entry_price,
        max_resolution_hours=settings.max_resolution_hours,
        scan_interval_seconds=args.interval,
        noaa_user_agent=settings.noaa_user_agent,
        noaa_request_timeout_seconds=settings.noaa_request_timeout_seconds,
        noaa_max_data_age_minutes=settings.noaa_max_data_age_minutes,
        minimum_edge_to_trade=settings.minimum_edge_to_trade,
        kelly_fraction=settings.kelly_fraction,
        probability_haircut_pct=settings.probability_haircut_pct,
        per_trade_exposure_cap_pct=settings.per_trade_exposure_cap_pct,
        global_max_open_exposure_pct=settings.global_max_open_exposure_pct,
        window_max_open_exposure_pct=settings.window_max_open_exposure_pct,
        minimum_trade_stake_usd=settings.minimum_trade_stake_usd,
        paper_starting_bankroll_usd=settings.paper_starting_bankroll_usd,
        paper_poll_interval_seconds=args.interval,
        paper_resolution_poll_seconds=settings.paper_resolution_poll_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
