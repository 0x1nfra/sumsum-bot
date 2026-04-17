"""BTC 5-minute signal boundary for later strategy work.

Phase 01 keeps the documented package path in place without adding any live
market logic.
"""

from __future__ import annotations


class BtcSignalEngine:
    """Placeholder BTC signal engine interface for future implementation."""

    def score_market(self, *_args: object, **_kwargs: object) -> None:
        """Reject Phase 1 usage until BTC signal logic is implemented."""
        raise NotImplementedError("BTC strategy logic is out of scope in Phase 1.")
