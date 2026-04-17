"""Paper-runtime wrapper around the shared market discovery CLI."""

from __future__ import annotations

from typing import Sequence

from main import main as discovery_main


def main(argv: Sequence[str] | None = None) -> int:
    """Reuse the shared scanner CLI for paper-runtime invocation."""

    return discovery_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
