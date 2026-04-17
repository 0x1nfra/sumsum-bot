"""BTC 5-minute scanner boundary for later strategy work.

Phase 01 keeps the documented package path in place without adding scanning or
execution behavior.
"""

from __future__ import annotations


class BtcMarketScanner:
    """Placeholder BTC scanner interface for future implementation."""

    def scan(self, *_args: object, **_kwargs: object) -> None:
        """Reject Phase 1 usage until BTC scanning is implemented."""
        raise NotImplementedError("BTC market scanning is out of scope in Phase 1.")
