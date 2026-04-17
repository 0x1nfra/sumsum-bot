"""Sports odds-client boundary for later strategy work.

Phase 01 preserves the documented module path only. External odds ingestion is
deferred until the sports strategy is in scope.
"""

from __future__ import annotations


class SportsOddsClient:
    """Placeholder sports-odds client interface for future implementation."""

    def fetch_odds(self, *_args: object, **_kwargs: object) -> None:
        """Reject Phase 1 usage until sports odds ingestion is implemented."""
        raise NotImplementedError("Sports odds ingestion is out of scope in Phase 1.")
