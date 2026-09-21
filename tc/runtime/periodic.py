from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Tuple
from uuid import uuid4

from tc.adapter.adapter import native_interval
from tc.adapter.native_client import TradingCursorNativeClient
from tc.normalizer.normalizer import NormalizedTCState
from tc.runtime.acquisition import MarketInputResolver, SCHEDULED_SYMBOLS
from tc.runtime.aggregate import TCRoleAggregate, TimeframeResult, aggregate_role_profile
from tc.runtime.orchestrator import OrchestratorError, RawSink, TFProvenance, _execute_one
from tc.runtime.planner import NativeRequestPlan
from tc.runtime.symbol import ResolvedSymbol, resolve_symbol
from tc.runtime.tf_cache import TimeframeCache


@dataclass(frozen=True)
class PeriodicError:
    timeframe: str
    code: str
    message: str


@dataclass(frozen=True)
class PeriodicSymbolResult:
    slot_id: str
    source_run_id: str
    resolved_symbol: ResolvedSymbol
    raw_records: Tuple[Mapping[str, Any], ...]
    normalized_records: Tuple[NormalizedTCState, ...]
    timeframe_provenance: Tuple[TFProvenance, ...]
    aggregate: TCRoleAggregate | None
    errors: Tuple[PeriodicError, ...]


@dataclass(frozen=True)
class PeriodicSlotResult:
    slot_id: str
    symbol_results: Tuple[PeriodicSymbolResult, ...]


def _plan(resolved: ResolvedSymbol, timeframe: str, execution_order: int) -> NativeRequestPlan:
    roles = {"D1": "ENVIRONMENT", "H4": "SETUP", "H1": "DECISION", "M15": "CONFIRMATION"}
    return NativeRequestPlan(
        timeframe=timeframe,
        exchange=resolved.provider,
        symbol=resolved.provider_symbol,
        interval=native_interval(timeframe),
        execution_order=execution_order,
        role=roles[timeframe],
    )


def _tf_result(record: NormalizedTCState) -> TimeframeResult:
    return TimeframeResult(
        timeframe=record.timeframe,
        entry_direction=record.entry_direction,
        trade_state=record.trade_state,
        record_id=record.record_id,
        entry_price=record.entry_price,
        stop_loss=record.stop_loss,
        take_profits=record.take_profits,
        lower_tf_confirmation_required=record.lower_tf_confirmation_required,
    )


def _cache_provenance(timeframe: str, lookup, reason: str) -> TFProvenance:
    return TFProvenance(
        timeframe=timeframe,
        source_mode="CACHE",
        fetched_at=lookup.item.fetched_at,
        cache_age_seconds=lookup.cache_age_seconds,
        reason=reason,
    )


def _live_one(
    *,
    slot_id: str,
    run_id: str,
    resolved: ResolvedSymbol,
    timeframe: str,
    execution_order: int,
    reason: str,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    cache: TimeframeCache,
    now: datetime | None,
):
    plan = _plan(resolved, timeframe, execution_order)
    try:
        raw, normalized = _execute_one(
            source_run_id=run_id,
            plan=plan,
            profile="NORMAL",
            client=client,
            raw_sink=raw_sink,
        )
    except OrchestratorError as exc:
        cache.mark_failure(
            canonical_symbol=resolved.canonical_symbol,
            provider=resolved.provider,
            provider_symbol=resolved.provider_symbol,
            timeframe=timeframe,
            failure_code=exc.code,
            now=now,
        )
        raise

    item = cache.put(
        canonical_symbol=resolved.canonical_symbol,
        provider=resolved.provider,
        provider_symbol=resolved.provider_symbol,
        profile="NORMAL",
        timeframe=timeframe,
        raw=raw,
        normalized=normalized,
        now=now,
    )
    provenance = TFProvenance(
        timeframe=timeframe,
        source_mode="LIVE",
        fetched_at=item.fetched_at,
        cache_age_seconds=0,
        reason=reason,
    )
    return raw, normalized, provenance


def run_periodic_symbol(
    *,
    slot_id: str,
    user_symbol: str,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    cache: TimeframeCache,
    now: datetime | None = None,
    source_run_id: str | None = None,
) -> PeriodicSymbolResult:
    """Run one NORMAL periodic symbol cycle using the shared TC5-18 last-successful cache.

    Scheduled TFs are LIVE. Non-scheduled D1/H4 are resolved from CACHE. Any
    retry_pending TF is attempted once at the next slot. A failed Native call is
    recorded and is never immediately retried inside the same slot.
    """
    resolved = resolve_symbol(user_symbol)
    resolver = MarketInputResolver(cache)
    run_id = source_run_id or f"tcperiodic-{slot_id.replace(':', '')}-{resolved.canonical_symbol}-{uuid4().hex[:10]}"
    decisions = resolver.resolve_periodic(slot_id=slot_id, resolved_symbol=resolved, now=now)

    raw_records: list[Mapping[str, Any]] = []
    normalized_records: list[NormalizedTCState] = []
    provenance: list[TFProvenance] = []
    errors: list[PeriodicError] = []
    results: dict[str, TimeframeResult] = {}
    execution_order = 0

    for decision in decisions:
        execution_order += 1
        if decision.source_mode == "UNAVAILABLE":
            provenance.append(
                TFProvenance(
                    timeframe=decision.timeframe,
                    source_mode="UNAVAILABLE",
                    fetched_at=None,
                    cache_age_seconds=None,
                    reason=decision.reason,
                )
            )
            errors.append(
                PeriodicError(
                    decision.timeframe,
                    "REUSE_UNAVAILABLE",
                    "no last successful CURRENT exists for this provider/symbol/timeframe",
                )
            )
            continue
        if decision.source_mode == "CACHE":
            if decision.cache_lookup is None:
                errors.append(PeriodicError(decision.timeframe, "CACHE_RESOLUTION_INVALID", "CACHE selected without evidence"))
                continue
            raw = decision.cache_lookup.item.raw
            normalized = decision.cache_lookup.item.normalized
            tf_provenance = _cache_provenance(decision.timeframe, decision.cache_lookup, decision.reason)
        else:
            try:
                raw, normalized, tf_provenance = _live_one(
                    slot_id=slot_id,
                    run_id=run_id,
                    resolved=resolved,
                    timeframe=decision.timeframe,
                    execution_order=execution_order,
                    reason=decision.reason,
                    client=client,
                    raw_sink=raw_sink,
                    cache=cache,
                    now=now,
                )
            except OrchestratorError as exc:
                errors.append(PeriodicError(decision.timeframe, exc.code, str(exc)))
                continue

        raw_records.append(raw)
        normalized_records.append(normalized)
        provenance.append(tf_provenance)
        results[decision.timeframe] = _tf_result(normalized)

    aggregate: TCRoleAggregate | None = None
    if all(tf in results for tf in ("D1", "H4", "H1")):
        aggregate = aggregate_role_profile(
            batch_id=run_id,
            canonical_symbol=resolved.canonical_symbol,
            provider=resolved.provider,
            profile="NORMAL",
            results=results,
        )

        if aggregate.runtime_status == "NEEDS_DRILLDOWN":
            execution_order += 1
            try:
                raw, normalized, tf_provenance = _live_one(
                    slot_id=slot_id,
                    run_id=run_id,
                    resolved=resolved,
                    timeframe="M15",
                    execution_order=execution_order,
                    reason="LOWER_TF_CONFIRMATION_REQUIRED",
                    client=client,
                    raw_sink=raw_sink,
                    cache=cache,
                    now=now,
                )
                raw_records.append(raw)
                normalized_records.append(normalized)
                provenance.append(tf_provenance)
                results["M15"] = _tf_result(normalized)
                aggregate = aggregate_role_profile(
                    batch_id=run_id,
                    canonical_symbol=resolved.canonical_symbol,
                    provider=resolved.provider,
                    profile="NORMAL",
                    results=results,
                )
            except OrchestratorError as exc:
                errors.append(PeriodicError("M15", exc.code, str(exc)))

    return PeriodicSymbolResult(
        slot_id=slot_id,
        source_run_id=run_id,
        resolved_symbol=resolved,
        raw_records=tuple(raw_records),
        normalized_records=tuple(normalized_records),
        timeframe_provenance=tuple(provenance),
        aggregate=aggregate,
        errors=tuple(errors),
    )


def run_periodic_slot(
    *,
    slot_id: str,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    cache: TimeframeCache,
    now: datetime | None = None,
) -> PeriodicSlotResult:
    """Run the fixed TC5-15 three-symbol slot in GOLD/USDJPY/US100 order."""
    results = tuple(
        run_periodic_symbol(
            slot_id=slot_id,
            user_symbol=symbol,
            client=client,
            raw_sink=raw_sink,
            cache=cache,
            now=now,
        )
        for symbol in SCHEDULED_SYMBOLS
    )
    return PeriodicSlotResult(slot_id=slot_id, symbol_results=results)
