from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from tc.adapter.native_client import TradingCursorNativeClient
from tc.runtime.acquisition import BASE_PERIODIC_CALLS_PER_DAY
from tc.runtime.command import TCSpotRuntimeRequest, parse_spot_command
from tc.runtime.host_binding import UsageTrackingNativeClient
from tc.runtime.orchestrator import RawSink, SpotRunResult, run_spot_entry_pre
from tc.runtime.response import build_tradeplan_state
from tc.runtime.symbol import ResolvedSymbol, resolve_symbol
from tc.runtime.tf_cache import TimeframeCache
from tc.runtime.usage import TCUsageRuntimeInfo, build_usage_runtime_info


@dataclass(frozen=True)
class TCSpotServiceResult:
    command_request: TCSpotRuntimeRequest
    resolved_symbol: ResolvedSymbol
    run_result: SpotRunResult
    tradeplan_state: Mapping[str, Any]
    runtime_usage: TCUsageRuntimeInfo


def run_spot_command(
    command_text: str,
    *,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    timestamp: str | None = None,
    source_run_id: str | None = None,
    used_today_before_run: int | None = None,
    scheduled_reserve_calls: int | None = None,
    usage_as_of: datetime | str | None = None,
    cache: TimeframeCache | None = None,
    cache_as_of: datetime | None = None,
) -> TCSpotServiceResult:
    """Run one complete TC Spot command through the repository runtime core.

    When `cache` is supplied, NORMAL Spot is cache-first under TC5-15: D1/H4
    reuse shared scheduled evidence, H1 is reused for up to 90 minutes, and
    only missing/expired evidence is fetched LIVE. The same result is then sent
    through the existing common aggregation and TradePlanState construction.

    Usage information is kept outside TradePlanState. `current_run_calls` counts
    only successful Native responses in this run; cache hits consume zero calls.
    Daily remaining figures are calculated only when the Host supplies an
    authoritative pre-run local ledger value.
    """
    command_request = parse_spot_command(command_text)
    resolved_symbol = resolve_symbol(command_request.user_symbol)
    tracking_client = UsageTrackingNativeClient(client)
    run_result = run_spot_entry_pre(
        command_request=command_request,
        resolved_symbol=resolved_symbol,
        client=tracking_client,
        raw_sink=raw_sink,
        source_run_id=source_run_id,
        cache=cache,
        now=cache_as_of,
    )
    tradeplan_state = build_tradeplan_state(
        aggregate=run_result.aggregate,
        normalized_records=run_result.normalized_records,
        resolved_symbol=resolved_symbol,
        timestamp=timestamp,
        timeframe_provenance=run_result.timeframe_provenance,
    )
    reserve = scheduled_reserve_calls
    if reserve is None and cache is not None:
        reserve = BASE_PERIODIC_CALLS_PER_DAY
    runtime_usage = build_usage_runtime_info(
        current_run_calls=tracking_client.successful_calls,
        used_today_before_run=used_today_before_run,
        scheduled_reserve_calls=reserve,
        as_of=usage_as_of,
    )
    return TCSpotServiceResult(
        command_request=command_request,
        resolved_symbol=resolved_symbol,
        run_result=run_result,
        tradeplan_state=tradeplan_state,
        runtime_usage=runtime_usage,
    )
