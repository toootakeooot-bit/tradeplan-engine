from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Tuple

from tc.normalizer.normalizer import NormalizedTCState
from tc.runtime.symbol import ResolvedSymbol
from tc.runtime.tf_cache import CacheLookup, TimeframeCache


JST = timezone(timedelta(hours=9))
SCHEDULED_SYMBOLS: Tuple[str, ...] = ("GOLD", "USDJPY", "US100")
H1_SPOT_MAX_AGE_SECONDS = 90 * 60
EARLY_SLOT_H4_REFRESH_AFTER_SECONDS = 6 * 60 * 60


@dataclass(frozen=True)
class PeriodicSlot:
    slot_id: str
    local_time: str
    live_timeframes: Tuple[str, ...]


PERIODIC_SLOTS: Tuple[PeriodicSlot, ...] = (
    PeriodicSlot("05:03", "05:03", ("H1",)),
    PeriodicSlot("09:03", "09:03", ("D1", "H4", "H1")),
    PeriodicSlot("12:03", "12:03", ("H1",)),
    PeriodicSlot("17:03", "17:03", ("H4", "H1")),
    PeriodicSlot("21:03", "21:03", ("H4", "H1")),
)

BASE_PERIODIC_CALLS_PER_DAY = sum(len(slot.live_timeframes) for slot in PERIODIC_SLOTS) * len(SCHEDULED_SYMBOLS)


@dataclass(frozen=True)
class AcquisitionDecision:
    timeframe: str
    source_mode: str  # LIVE | CACHE
    reason: str
    cache_lookup: CacheLookup | None = None


class MarketInputResolver:
    """Common Periodic/Spot acquisition policy.

    The Resolver decides CACHE vs LIVE before normalization/aggregation. It never
    infers TC evidence and never rewrites cached provenance.
    """

    def __init__(self, cache: TimeframeCache) -> None:
        self.cache = cache

    @staticmethod
    def periodic_slot(slot_id: str) -> PeriodicSlot:
        for slot in PERIODIC_SLOTS:
            if slot.slot_id == slot_id:
                return slot
        raise ValueError(f"unsupported periodic slot: {slot_id}")

    def _lookup(self, resolved_symbol: ResolvedSymbol, timeframe: str, now: datetime | None) -> CacheLookup | None:
        return self.cache.get_latest(
            canonical_symbol=resolved_symbol.canonical_symbol,
            provider=resolved_symbol.provider,
            provider_symbol=resolved_symbol.provider_symbol,
            timeframe=timeframe,
            now=now,
        )

    def _retry_pending(self, resolved_symbol: ResolvedSymbol, timeframe: str) -> bool:
        return self.cache.retry_pending(
            canonical_symbol=resolved_symbol.canonical_symbol,
            provider=resolved_symbol.provider,
            provider_symbol=resolved_symbol.provider_symbol,
            timeframe=timeframe,
        ) is not None

    def resolve_spot(
        self,
        *,
        resolved_symbol: ResolvedSymbol,
        timeframes: Iterable[str],
        now: datetime | None = None,
    ) -> Tuple[AcquisitionDecision, ...]:
        decisions = []
        for timeframe in timeframes:
            lookup = self._lookup(resolved_symbol, timeframe, now)
            if self._retry_pending(resolved_symbol, timeframe):
                decisions.append(AcquisitionDecision(timeframe, "LIVE", "RETRY_PENDING", lookup))
                continue

            if timeframe in {"D1", "H4"}:
                if lookup is not None:
                    decisions.append(AcquisitionDecision(timeframe, "CACHE", "LATEST_SCHEDULED_CACHE", lookup))
                else:
                    decisions.append(AcquisitionDecision(timeframe, "LIVE", "CACHE_MISSING"))
                continue

            if timeframe == "H1":
                if lookup is not None and lookup.cache_age_seconds <= H1_SPOT_MAX_AGE_SECONDS:
                    decisions.append(AcquisitionDecision(timeframe, "CACHE", "H1_CACHE_WITHIN_90_MIN", lookup))
                else:
                    reason = "H1_CACHE_EXPIRED" if lookup is not None else "CACHE_MISSING"
                    decisions.append(AcquisitionDecision(timeframe, "LIVE", reason, lookup))
                continue

            # M15 is not a standing cache substitute in NORMAL. It is fetched
            # only when the common aggregation explicitly requests confirmation.
            decisions.append(AcquisitionDecision(timeframe, "LIVE", "LOWER_TF_LIVE_REQUIRED", lookup))
        return tuple(decisions)

    def resolve_periodic(
        self,
        *,
        slot_id: str,
        resolved_symbol: ResolvedSymbol,
        required_timeframes: Iterable[str] = ("D1", "H4", "H1"),
        now: datetime | None = None,
    ) -> Tuple[AcquisitionDecision, ...]:
        slot = self.periodic_slot(slot_id)
        scheduled = set(slot.live_timeframes)
        decisions = []
        for timeframe in required_timeframes:
            lookup = self._lookup(resolved_symbol, timeframe, now)
            if timeframe in scheduled:
                decisions.append(AcquisitionDecision(timeframe, "LIVE", f"SCHEDULED_{slot_id}", lookup))
            elif self._retry_pending(resolved_symbol, timeframe):
                decisions.append(AcquisitionDecision(timeframe, "LIVE", "RETRY_PENDING_NEXT_SLOT", lookup))
            elif lookup is not None:
                decisions.append(AcquisitionDecision(timeframe, "CACHE", "PERIODIC_CACHE_REUSE", lookup))
            else:
                decisions.append(AcquisitionDecision(timeframe, "LIVE", "CACHE_MISSING_FALLBACK"))
        return tuple(decisions)

    def needs_0503_h4_refresh(
        self,
        *,
        resolved_symbol: ResolvedSymbol,
        h1: NormalizedTCState,
        now: datetime | None = None,
    ) -> bool:
        """Refresh stale H4 at 05:03 only for an H1 entry candidate.

        Six hours is a conservative stale threshold: the normal 21:03 -> 05:03
        gap is about eight hours, so ACTIONABLE H1 receives fresh H4 while WAIT
        does not spend an extra Native call.
        """
        if h1.trade_state != "ACTIONABLE":
            return False
        lookup = self._lookup(resolved_symbol, "H4", now)
        return lookup is None or lookup.cache_age_seconds > EARLY_SLOT_H4_REFRESH_AFTER_SECONDS
