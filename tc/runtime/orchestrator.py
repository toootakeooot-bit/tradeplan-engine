from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Tuple
from uuid import uuid4

from tc.adapter.adapter import AdapterRequest, adapt_native_response
from tc.adapter.native_client import TradingCursorNativeClient
from tc.normalizer.normalizer import NormalizedTCState, normalize_tc_raw
from tc.runtime.acquisition import AcquisitionDecision, MarketInputResolver
from tc.runtime.aggregate import TCRoleAggregate, TimeframeResult, aggregate_role_profile
from tc.runtime.command import TCSpotRuntimeRequest
from tc.runtime.planner import NativeRequestPlan, build_drilldown_plan, build_entry_pre_plan
from tc.runtime.symbol import ResolvedSymbol
from tc.runtime.tf_cache import TimeframeCache


class RawSink(Protocol):
    def preserve(
        self,
        *,
        source_run_id: str,
        execution_order: int,
        native_response: Mapping[str, Any],
    ) -> str:
        """Persist the unmodified Native response and return a stable artifact reference."""
        ...


@dataclass(frozen=True)
class TFProvenance:
    timeframe: str
    source_mode: str
    fetched_at: str | None
    cache_age_seconds: int | None
    reason: str


@dataclass(frozen=True)
class SpotRunResult:
    source_run_id: str
    profile: str
    canonical_symbol: str
    provider: str
    provider_symbol: str
    raw_records: Tuple[Mapping[str, Any], ...]
    normalized_records: Tuple[NormalizedTCState, ...]
    aggregate: TCRoleAggregate
    timeframe_provenance: Tuple[TFProvenance, ...] = ()


class OrchestratorError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _utc_iso(now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).isoformat()


def _execute_one(
    *,
    source_run_id: str,
    plan: NativeRequestPlan,
    profile: str,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
) -> tuple[Mapping[str, Any], NormalizedTCState]:
    request_id = f"{source_run_id}:{plan.execution_order}:{uuid4().hex[:12]}"
    try:
        native_response = client.request_analysis(
            exchange=plan.exchange,
            symbol=plan.symbol,
            interval=plan.interval,
        )
    except Exception as exc:
        raise OrchestratorError(
            "NATIVE_CALL_FAILED",
            f"{plan.timeframe}/{plan.role} native call failed: {exc}",
        ) from exc

    if not isinstance(native_response, Mapping) or not native_response:
        raise OrchestratorError("NATIVE_RESPONSE_INVALID", f"empty/invalid response for {plan.timeframe}")

    try:
        artifact_ref = raw_sink.preserve(
            source_run_id=source_run_id,
            execution_order=plan.execution_order,
            native_response=native_response,
        )
    except Exception as exc:
        raise OrchestratorError(
            "RAW_PRESERVATION_FAILED",
            f"raw preservation failed for {plan.timeframe}: {exc}",
        ) from exc

    raw = adapt_native_response(
        request=AdapterRequest(
            request_id=request_id,
            source_run_id=source_run_id,
            execution_order=plan.execution_order,
            analysis_source=plan.exchange,
            analysis_symbol=plan.symbol,
            timeframe=plan.timeframe,
            profile=profile,
            role=plan.role,
        ),
        native_response=native_response,
        source_raw_artifact=artifact_ref,
    )
    normalized = normalize_tc_raw(raw)
    return raw, normalized


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


def _mark_failure(cache: TimeframeCache | None, resolved_symbol: ResolvedSymbol, timeframe: str, exc: OrchestratorError, now: datetime | None) -> None:
    if cache is None:
        return
    cache.mark_failure(
        canonical_symbol=resolved_symbol.canonical_symbol,
        provider=resolved_symbol.provider,
        provider_symbol=resolved_symbol.provider_symbol,
        timeframe=timeframe,
        failure_code=exc.code,
        now=now,
    )


def _live_and_cache(
    *,
    run_id: str,
    plan: NativeRequestPlan,
    profile: str,
    resolved_symbol: ResolvedSymbol,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    cache: TimeframeCache | None,
    now: datetime | None,
    reason: str,
) -> tuple[Mapping[str, Any], NormalizedTCState, TFProvenance]:
    try:
        raw, normalized = _execute_one(
            source_run_id=run_id,
            plan=plan,
            profile=profile,
            client=client,
            raw_sink=raw_sink,
        )
    except OrchestratorError as exc:
        _mark_failure(cache, resolved_symbol, plan.timeframe, exc, now)
        raise

    fetched_at = _utc_iso(now)
    if cache is not None:
        item = cache.put(
            canonical_symbol=resolved_symbol.canonical_symbol,
            provider=resolved_symbol.provider,
            provider_symbol=resolved_symbol.provider_symbol,
            profile=profile,
            timeframe=plan.timeframe,
            raw=raw,
            normalized=normalized,
            now=now,
        )
        fetched_at = item.fetched_at
    return raw, normalized, TFProvenance(plan.timeframe, "LIVE", fetched_at, 0, reason)


def _cache_evidence(decision: AcquisitionDecision) -> tuple[Mapping[str, Any], NormalizedTCState, TFProvenance]:
    if decision.cache_lookup is None:
        raise OrchestratorError("CACHE_RESOLUTION_INVALID", f"CACHE selected without evidence for {decision.timeframe}")
    item = decision.cache_lookup.item
    return (
        item.raw,
        item.normalized,
        TFProvenance(
            timeframe=decision.timeframe,
            source_mode="CACHE",
            fetched_at=item.fetched_at,
            cache_age_seconds=decision.cache_lookup.cache_age_seconds,
            reason=decision.reason,
        ),
    )


def run_spot_entry_pre(
    *,
    command_request: TCSpotRuntimeRequest,
    resolved_symbol: ResolvedSymbol,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    source_run_id: str | None = None,
    cache: TimeframeCache | None = None,
    now: datetime | None = None,
) -> SpotRunResult:
    """Execute one NORMAL or SHORT TC Spot ENTRY_PRE run.

    NORMAL is cache-first when a shared TimeframeCache is supplied. D1/H4 use
    the latest scheduled evidence, H1 cache is accepted for at most 90 minutes,
    and only missing/expired TFs call Native. M15 remains LIVE and is requested
    only when the common aggregation explicitly requires confirmation.

    Without a cache this preserves the pre-TC5-15 all-LIVE behavior so existing
    hosts remain compatible until they bind shared persistence.
    """
    run_id = source_run_id or f"tcspot-{uuid4().hex}"
    raw_records: list[Mapping[str, Any]] = []
    normalized_records: list[NormalizedTCState] = []
    provenance: list[TFProvenance] = []
    results: dict[str, TimeframeResult] = {}
    plans = build_entry_pre_plan(command_request, resolved_symbol)

    decisions: dict[str, AcquisitionDecision] = {}
    if cache is not None and command_request.profile == "NORMAL":
        resolver = MarketInputResolver(cache)
        decisions = {
            decision.timeframe: decision
            for decision in resolver.resolve_spot(
                resolved_symbol=resolved_symbol,
                timeframes=(plan.timeframe for plan in plans),
                now=now,
            )
        }

    for plan in plans:
        decision = decisions.get(plan.timeframe)
        if decision is not None and decision.source_mode == "CACHE":
            raw, normalized, tf_provenance = _cache_evidence(decision)
        else:
            reason = decision.reason if decision is not None else "SPOT_LIVE_DEFAULT"
            raw, normalized, tf_provenance = _live_and_cache(
                run_id=run_id,
                plan=plan,
                profile=command_request.profile,
                resolved_symbol=resolved_symbol,
                client=client,
                raw_sink=raw_sink,
                cache=cache,
                now=now,
                reason=reason,
            )
        raw_records.append(raw)
        normalized_records.append(normalized)
        provenance.append(tf_provenance)
        results[plan.timeframe] = _tf_result(normalized)

    aggregate = aggregate_role_profile(
        batch_id=run_id,
        canonical_symbol=resolved_symbol.canonical_symbol,
        provider=resolved_symbol.provider,
        profile=command_request.profile,
        results=results,
    )

    if aggregate.runtime_status == "NEEDS_DRILLDOWN":
        drilldown = build_drilldown_plan(command_request, resolved_symbol)
        raw, normalized, tf_provenance = _live_and_cache(
            run_id=run_id,
            plan=drilldown,
            profile=command_request.profile,
            resolved_symbol=resolved_symbol,
            client=client,
            raw_sink=raw_sink,
            cache=cache,
            now=now,
            reason="LOWER_TF_CONFIRMATION_REQUIRED",
        )
        raw_records.append(raw)
        normalized_records.append(normalized)
        provenance.append(tf_provenance)
        results[drilldown.timeframe] = _tf_result(normalized)
        aggregate = aggregate_role_profile(
            batch_id=run_id,
            canonical_symbol=resolved_symbol.canonical_symbol,
            provider=resolved_symbol.provider,
            profile=command_request.profile,
            results=results,
        )

    return SpotRunResult(
        source_run_id=run_id,
        profile=command_request.profile,
        canonical_symbol=resolved_symbol.canonical_symbol,
        provider=resolved_symbol.provider,
        provider_symbol=resolved_symbol.provider_symbol,
        raw_records=tuple(raw_records),
        normalized_records=tuple(normalized_records),
        aggregate=aggregate,
        timeframe_provenance=tuple(provenance),
    )
