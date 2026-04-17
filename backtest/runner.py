"""Thin backtest runner boundary for future historical replay work."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import describe_runtime


def main() -> int:
    """Report the current scaffold status for the backtest boundary."""
    print(describe_runtime("backtest"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
