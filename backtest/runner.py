"""Thin backtest runner boundary for future historical replay work."""

from __future__ import annotations

from core import describe_runtime


def main() -> int:
    """Report the current scaffold status for the backtest boundary."""
    print(describe_runtime("backtest"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

