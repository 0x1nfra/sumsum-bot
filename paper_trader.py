"""Operator-facing paper-trading CLI."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from config.settings import get_settings
from core.paper_runtime import PaperRuntime
from main import add_runtime_arguments, build_runtime_settings

PAPER_RUNTIME_ARGUMENTS = ("--fixture", "--database-path", "--interval")


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
    settings = build_runtime_settings(args)
    runtime = PaperRuntime(settings=settings)
    summary = runtime.run_once(mode="paper-once", fixture_path=args.fixture)
    print(json.dumps(summary, sort_keys=True))
    return 0


def run_paper_loop(args: argparse.Namespace) -> int:
    settings = build_runtime_settings(args)
    runtime = PaperRuntime(settings=settings)
    run_summaries = runtime.run_loop(
        fixture_path=args.fixture,
        interval_seconds=args.interval,
        iterations=args.iterations,
    )
    for iteration, summary in enumerate(run_summaries, start=1):
        print(json.dumps({"iteration": iteration, **summary}, sort_keys=True))
    print(json.dumps({"mode": "paper-loop-summary", "iterations": len(run_summaries)}, sort_keys=True))
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


if __name__ == "__main__":
    raise SystemExit(main())
