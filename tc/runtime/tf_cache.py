from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from tc.normalizer.normalizer import NormalizedTCState


_TF_SECONDS = {"D1": 86400, "H4": 14400, "H1": 3600, "M15": 900}


def _utc(value: datetime | None = None) -> datetime:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc)


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def candle_id(timeframe: str, now: datetime | None = None) -> int:
    """Return a UTC candle bucket id used only as provenance.

    TC5-15 does not invalidate D1/H4 merely because a bucket changed. Freshness
    is a Resolver responsibility because the periodic policy intentionally reuses
    e.g. the 21:03 H4 result at 05:03 when no H4 refresh is scheduled.
    """
    if timeframe not in _TF_SECONDS:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    return int(_utc(now).timestamp()) // _TF_SECONDS[timeframe]


def _source_time(raw: Mapping[str, Any], fallback: datetime) -> datetime:
    original = raw.get("original_response")
    if isinstance(original, Mapping):
        value = original.get("timestamp")
        if isinstance(value, str):
            try:
                return _parse_iso(value)
            except (TypeError, ValueError):
                pass
    return fallback


def _artifact_ref(raw: Mapping[str, Any]) -> str | None:
    identity = raw.get("record_identity")
    if isinstance(identity, Mapping):
        value = identity.get("source_raw_artifact")
        if isinstance(value, str) and value:
            return value
    return None


def _record_id(raw: Mapping[str, Any], normalized: NormalizedTCState) -> str:
    identity = raw.get("record_identity")
    if isinstance(identity, Mapping) and identity.get("record_id"):
        return str(identity["record_id"])
    return normalized.record_id


def _source_run_id(raw: Mapping[str, Any]) -> str | None:
    identity = raw.get("record_identity")
    if isinstance(identity, Mapping) and identity.get("source_run_id"):
        return str(identity["source_run_id"])
    return None


def _normalized_from_dict(value: Mapping[str, Any]) -> NormalizedTCState:
    payload = dict(value)
    payload["take_profits"] = tuple(payload.get("take_profits") or ())
    return NormalizedTCState(**payload)


@dataclass(frozen=True)
class CachedTFResult:
    canonical_symbol: str
    provider: str
    provider_symbol: str
    timeframe: str
    source_profile: str
    candle_id: int
    fetched_at: str
    source_run_id: str | None
    record_id: str
    raw_artifact_ref: str | None
    cache_status: str
    raw: Mapping[str, Any]
    normalized: NormalizedTCState


@dataclass(frozen=True)
class CacheLookup:
    item: CachedTFResult
    cache_age_seconds: int
    cache_status: str


@dataclass(frozen=True)
class RetryPending:
    canonical_symbol: str
    provider: str
    provider_symbol: str
    timeframe: str
    last_failure_at: str
    failure_code: str


class TimeframeCache:
    """Shared TC result cache with optional JSON persistence.

    Key identity is canonical_symbol/provider/provider_symbol/timeframe. Profile
    is provenance only; role assignment is performed later by the common
    Aggregator. A storage_path makes the cache reusable by separate periodic and
    Spot processes instead of limiting reuse to one Python process.
    """

    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = Path(storage_path) if storage_path is not None else None
        self._items: dict[tuple[str, str, str, str], CachedTFResult] = {}
        self._retry: dict[tuple[str, str, str, str], RetryPending] = {}
        self._load()

    @staticmethod
    def _key(
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        timeframe: str,
    ) -> tuple[str, str, str, str]:
        return canonical_symbol, provider, provider_symbol, timeframe

    def _load(self) -> None:
        if self.storage_path is None or not self.storage_path.exists():
            return
        payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
        for value in payload.get("records", []):
            normalized = _normalized_from_dict(value["normalized"])
            item = CachedTFResult(
                canonical_symbol=value["canonical_symbol"],
                provider=value["provider"],
                provider_symbol=value["provider_symbol"],
                timeframe=value["timeframe"],
                source_profile=value["source_profile"],
                candle_id=int(value["candle_id"]),
                fetched_at=value["fetched_at"],
                source_run_id=value.get("source_run_id"),
                record_id=value["record_id"],
                raw_artifact_ref=value.get("raw_artifact_ref"),
                cache_status=value.get("cache_status", "AVAILABLE"),
                raw=value["raw"],
                normalized=normalized,
            )
            self._items[self._key(item.canonical_symbol, item.provider, item.provider_symbol, item.timeframe)] = item
        for value in payload.get("retry_pending", []):
            retry = RetryPending(**value)
            self._retry[self._key(retry.canonical_symbol, retry.provider, retry.provider_symbol, retry.timeframe)] = retry

    def _persist(self) -> None:
        if self.storage_path is None:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "TC5_15_CACHE_V1",
            "records": [
                {
                    **{k: v for k, v in asdict(item).items() if k != "normalized"},
                    "normalized": asdict(item.normalized),
                }
                for item in self._items.values()
            ],
            "retry_pending": [asdict(item) for item in self._retry.values()],
        }
        temporary = self.storage_path.with_suffix(self.storage_path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self.storage_path)

    def get_last_successful_current(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        timeframe: str,
        now: datetime | None = None,
    ) -> CacheLookup | None:
        """Return the last successfully persisted CURRENT for one symbol/TF.

        Resolution is intentionally global across run/cycle boundaries. A later
        cycle must not require the evidence to have been produced inside that
        same cycle. Failed LIVE attempts are tracked separately in retry state
        and never overwrite this last successful value.
        """
        item = self._items.get(self._key(canonical_symbol, provider, provider_symbol, timeframe))
        if item is None:
            return None
        age = max(0, int((_utc(now) - _parse_iso(item.fetched_at)).total_seconds()))
        return CacheLookup(item=item, cache_age_seconds=age, cache_status=item.cache_status)

    def get_latest(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        timeframe: str,
        now: datetime | None = None,
    ) -> CacheLookup | None:
        """Backward-compatible alias for get_last_successful_current()."""
        return self.get_last_successful_current(
            canonical_symbol=canonical_symbol,
            provider=provider,
            provider_symbol=provider_symbol,
            timeframe=timeframe,
            now=now,
        )

    def put(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        profile: str,
        timeframe: str,
        raw: Mapping[str, Any],
        normalized: NormalizedTCState,
        now: datetime | None = None,
    ) -> CachedTFResult:
        current = _utc(now)
        source_time = _source_time(raw, current)
        item = CachedTFResult(
            canonical_symbol=canonical_symbol,
            provider=provider,
            provider_symbol=provider_symbol,
            timeframe=timeframe,
            source_profile=profile,
            candle_id=candle_id(timeframe, source_time),
            fetched_at=current.isoformat(),
            source_run_id=_source_run_id(raw),
            record_id=_record_id(raw, normalized),
            raw_artifact_ref=_artifact_ref(raw),
            cache_status="AVAILABLE",
            raw=dict(raw),
            normalized=normalized,
        )
        key = self._key(canonical_symbol, provider, provider_symbol, timeframe)
        self._items[key] = item
        self._retry.pop(key, None)
        self._persist()
        return item

    def mark_failure(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        timeframe: str,
        failure_code: str,
        now: datetime | None = None,
    ) -> RetryPending:
        retry = RetryPending(
            canonical_symbol=canonical_symbol,
            provider=provider,
            provider_symbol=provider_symbol,
            timeframe=timeframe,
            last_failure_at=_utc(now).isoformat(),
            failure_code=failure_code,
        )
        self._retry[self._key(canonical_symbol, provider, provider_symbol, timeframe)] = retry
        self._persist()
        return retry

    def retry_pending(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        timeframe: str,
    ) -> RetryPending | None:
        return self._retry.get(self._key(canonical_symbol, provider, provider_symbol, timeframe))

    def clear_retry(
        self,
        *,
        canonical_symbol: str,
        provider: str,
        provider_symbol: str,
        timeframe: str,
    ) -> None:
        self._retry.pop(self._key(canonical_symbol, provider, provider_symbol, timeframe), None)
        self._persist()

    def clear(self) -> None:
        self._items.clear()
        self._retry.clear()
        self._persist()
