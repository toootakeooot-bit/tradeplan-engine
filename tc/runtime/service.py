from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tc.adapter.native_client import TradingCursorNativeClient
from tc.runtime.command import TCSpotRuntimeRequest, parse_spot_command
from tc.runtime.orchestrator import RawSink, SpotRunResult, run_spot_entry_pre
from tc.runtime.response import build_tradeplan_state
from tc.runtime.symbol import ResolvedSymbol, resolve_symbol


@dataclass(frozen=True)
class TCSpotServiceResult:
    command_request: TCSpotRuntimeRequest
    resolved_symbol: ResolvedSymbol
    run_result: SpotRunResult
    tradeplan_state: Mapping[str, Any]


def run_spot_command(
    command_text: str,
    *,
    client: TradingCursorNativeClient,
    raw_sink: RawSink,
    timestamp: str | None = None,
    source_run_id: str | None = None,
) -> TCSpotServiceResult:
    """Run one complete TC Spot command through the repository runtime core.

    Host responsibility is intentionally narrow: supply a Native Client binding
    and a Raw sink. The repository owns command parsing, symbol/provider
    resolution, profile planning, orchestration, Raw wrapping, normalization,
    role aggregation, and provisional TradePlanState construction.
    """
    command_request = parse_spot_command(command_text)
    resolved_symbol = resolve_symbol(command_request.user_symbol)
    run_result = run_spot_entry_pre(
        command_request=command_request,
        resolved_symbol=resolved_symbol,
        client=client,
        raw_sink=raw_sink,
        source_run_id=source_run_id,
    )
    tradeplan_state = build_tradeplan_state(
        aggregate=run_result.aggregate,
        normalized_records=run_result.normalized_records,
        resolved_symbol=resolved_symbol,
        timestamp=timestamp,
    )
    return TCSpotServiceResult(
        command_request=command_request,
        resolved_symbol=resolved_symbol,
        run_result=run_result,
        tradeplan_state=tradeplan_state,
    )
