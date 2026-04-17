"""Thin paper-trading entrypoint for the Phase 1 scaffold."""

from __future__ import annotations

from config import PROJECT_NAME
from core import describe_runtime


def main() -> int:
    """Report the current scaffold status for the paper runtime."""
    print(f"{PROJECT_NAME}: {describe_runtime('paper')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

