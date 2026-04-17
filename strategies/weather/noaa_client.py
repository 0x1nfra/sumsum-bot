"""NOAA client boundary for later weather-signal work.

Phase 01 preserves the documented module path only. Network access and
forecast parsing land in later phases.
"""

from __future__ import annotations


class NoaaForecastClient:
    """Placeholder NOAA client interface for future implementation."""

    def fetch_hourly_forecast(self, *_args: object, **_kwargs: object) -> None:
        """Reject Phase 1 usage until NOAA integration is implemented."""
        raise NotImplementedError("NOAA forecast access is out of scope in Phase 1.")
