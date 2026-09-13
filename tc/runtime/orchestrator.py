from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Tuple
from uuid import uuid4

from tc.adapter.adapter import AdapterRequest, adapt_native_response
from tc.adapter.native_client import TradingCursorNativeClient
from tc.normalizer.normalizer import NormalizedTCState, normalize_tc_raw
from tc.runtime.aggregate import TCRoleAggregate, TimeframeResult, aggregate_role_profile
from tc.runtime.command import TCSpotRuntimeRequest
from tc.runtime.planner import NativeRequestPlan, build_drilldown_plan, build_entry_pre_plan
from tc.runtime.symbol import ResolvedSymbol


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
class SpotRunResult:
    source_run_id: str
    profile: str
    canonical_symbol: str
    provider: str
    provider_symbol: str
    raw_records: Tuple[Mapping[str, Any], ...]
    normalized_records: Tuple[NormalizedTCState, ...]
    aggregate: TCRoleAggregate


class OrchestratorError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


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


def run_spot_entry_pre(
    *,
    command_request: TCSpotRuntimeRequest,
    resolved_symbol: ResolvedSymbol,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    source_run_id: str | None = None,
) -> SpotRunResult:
    """Execute one NORMAL or SHORT TC Spot ENTRY_PRE run.

    This is host-agnostic. A caller must supply both the external Native Client
    binding and a Raw sink that satisfies Original Raw First.
    """
    run_id = source_run_id or f"tcspot-{uuid4().hex}"
    raw_records: list[Mapping[str, Any]] = []
    normalized_records: list[NormalizedTCState] = []
    results: dict[str, TimeframeResult] = {}

    for plan in build_entry_pre_plan(command_request, resolved_symbol):
        raw, normalized = _execute_one(
            source_run_id=run_id,
            plan=plan,
            profile=command_request.profile,
            client=client,
            raw_sink=raw_sink,
        )
        raw_records.append(raw)
        normalized_records.append(normalized)
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
        raw, normalized = _execute_one(
            source_run_id=run_id,
            plan=drilldown,
            profile=command_request.profile,
            client=client,
            raw_sink=raw_sink,
        )
        raw_records.append(raw)
        normalized_records.append(normalized)
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
    )
