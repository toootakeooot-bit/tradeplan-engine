from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from tc.runtime.command import TCSpotRuntimeRequest
from tc.runtime.symbol import ResolvedSymbol


_INTERVALS = {
    "D1": "1D",
    "H4": "4h",
    "H1": "1h",
    "M15": "15m",
}


@dataclass(frozen=True)
class NativeRequestPlan:
    timeframe: str
    exchange: str
    symbol: str
    interval: str
    execution_order: int


def build_4tf_plan(
    command_request: TCSpotRuntimeRequest,
    resolved_symbol: ResolvedSymbol,
) -> Tuple[NativeRequestPlan, ...]:
    if command_request.engine_mode != "TC" or command_request.run_mode != "SPOT":
        raise ValueError("unsupported runtime request")
    if command_request.evaluation_mode != "ENTRY_PRE":
        raise ValueError("unsupported evaluation mode")
    if tuple(command_request.timeframes) != ("D1", "H4", "H1", "M15"):
        raise ValueError("ENTRY_PRE requires exact D1/H4/H1/M15 timeframes")

    return tuple(
        NativeRequestPlan(
            timeframe=tf,
            exchange=resolved_symbol.provider,
            symbol=resolved_symbol.provider_symbol,
            interval=_INTERVALS[tf],
            execution_order=index,
        )
        for index, tf in enumerate(command_request.timeframes, start=1)
    )
