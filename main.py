"""Thin live-runtime entrypoint for the Sumsum Bot scaffold."""

from __future__ import annotations

from config import DEFAULT_RUNTIME_MODE, PROJECT_NAME
from core import describe_runtime


def main() -> int:
    """Report the current scaffold status for the live runtime."""
    print(f"{PROJECT_NAME}: {describe_runtime(DEFAULT_RUNTIME_MODE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

