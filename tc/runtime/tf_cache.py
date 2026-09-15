from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


_TF_SECONDS = {"D1": 86400, "H4": 14400, "H1": 3600, "M15": 900}


def candle_id(timeframe: str, now: datetime | None = None) -> int:
    """Return a UTC candle bucket id for cache invalidation.

    D1/H4 are therefore reusable only while the caller remains in the same
    provider-independent UTC candle bucket. Provider/session-specific close
    rules can replace this function later without changing cache consumers.
    """
    if timeframe not in _TF_SECONDS:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return int(current.timestamp()) // _TF_SECONDS[timeframe]


@dataclass(frozen=True)
class CachedTFResult:
    canonical_symbol: str
    provider: str
    provider_symbol: str
    timeframe: str
    profile: str
    candle_id: int
    acquired_at: str
    raw: Mapping[str, Any]
    normalized: Any


class TimeframeCache:
    """In-process TC result cache keyed by symbol/profile/timeframe/candle."""

    def __init__(self) -> None:
        self._items: dict[tuple[str, str, str, str], CachedTFResult] = {}

    @staticmethod
    def _key(canonical_symbol: str, provider: str, profile: str, timeframe: str) -> tuple[str, str, str, str]:
        return canonical_symbol, provider, profile, timeframe

    def get_valid(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        profile: str,
        timeframe: str,
        now: datetime | None = None,
    ) -> CachedTFResult | None:
        item = self._items.get(self._key(canonical_symbol, provider, profile, timeframe))
        if item is None or item.candle_id != candle_id(timeframe, now):
            return None
        return item

    def put(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        profile: str,
        timeframe: str,
        raw: Mapping[str, Any],
        normalized: Any,
        now: datetime | None = None,
    ) -> CachedTFResult:
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        item = CachedTFResult(
            canonical_symbol=canonical_symbol,
            provider=provider,
            provider_symbol=provider_symbol,
            timeframe=timeframe,
            profile=profile,
            candle_id=candle_id(timeframe, current),
            acquired_at=current.astimezone(timezone.utc).isoformat(),
            raw=raw,
            normalized=normalized,
        )
        self._items[self._key(canonical_symbol, provider, profile, timeframe)] = item
        return item

    def clear(self) -> None:
        self._items.clear()
