"""Polymarket discovery adapter for public market payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class RawMarketRecord:
    """Transport-safe market payload consumed by scanner layers."""

    market_id: str
    slug: str
    title: str
    description: str
    end_iso: str
    liquidity_usd: float
    volume_usd: float
    no_price: float

    @property
    def is_weather_market(self) -> bool:
        text = f"{self.title} {self.description}".lower()
        weather_terms = (
            "temperature",
            "rain",
            "snow",
            "weather",
            "precip",
            "wind",
            "heat-index",
            "heat index",
        )
        return any(term in text for term in weather_terms)


class PolymarketPayloadError(ValueError):
    """Raised when a discovery payload is malformed or incomplete."""


class PolymarketDiscoveryClient:
    """Validate Polymarket discovery payloads and expose raw market records."""

    required_fields = (
        "id",
        "slug",
        "title",
        "description",
        "end_iso",
        "liquidity_usd",
        "volume_usd",
        "no_price",
    )

    def load_markets(
        self,
        payload: Mapping[str, object] | Sequence[Mapping[str, object]],
    ) -> list[RawMarketRecord]:
        raw_markets = self._extract_market_payloads(payload)
        return [self._normalize_market(market) for market in raw_markets]

    def _extract_market_payloads(
        self,
        payload: Mapping[str, object] | Sequence[Mapping[str, object]],
    ) -> Iterable[Mapping[str, object]]:
        if isinstance(payload, Mapping):
            markets = payload.get("markets")
            if not isinstance(markets, Sequence):
                raise PolymarketPayloadError("payload must contain a markets sequence")
            return markets

        if isinstance(payload, Sequence):
            return payload

        raise PolymarketPayloadError("payload must be a mapping or sequence")

    def _normalize_market(self, market: Mapping[str, object]) -> RawMarketRecord:
        missing = [field for field in self.required_fields if field not in market]
        if missing:
            missing_csv = ", ".join(sorted(missing))
            raise PolymarketPayloadError(f"market payload missing required fields: {missing_csv}")

        return RawMarketRecord(
            market_id=self._require_string(market["id"], "id"),
            slug=self._require_string(market["slug"], "slug"),
            title=self._require_string(market["title"], "title"),
            description=self._require_string(market["description"], "description"),
            end_iso=self._require_string(market["end_iso"], "end_iso"),
            liquidity_usd=self._require_number(market["liquidity_usd"], "liquidity_usd"),
            volume_usd=self._require_number(market["volume_usd"], "volume_usd"),
            no_price=self._require_number(market["no_price"], "no_price"),
        )

    def _require_string(self, value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise PolymarketPayloadError(f"{field} must be a non-empty string")
        return value.strip()

    def _require_number(self, value: object, field: str) -> float:
        if not isinstance(value, int | float):
            raise PolymarketPayloadError(f"{field} must be numeric")
        return float(value)
