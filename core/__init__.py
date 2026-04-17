"""Shared runtime helpers for thin entrypoints."""

from __future__ import annotations

from typing import Final


PHASE_STATUS: Final[str] = "market-discovery-foundation scaffold ready"


def describe_runtime(mode: str) -> str:
    """Return a placeholder runtime status for the requested mode."""
    return f"{PHASE_STATUS} ({mode})"

