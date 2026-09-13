from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple

STANDARD_TIMEFRAMES: Tuple[str, ...] = ("D1", "H4", "H1", "M15")
ALLOWED_STATES = {"WAIT", "ACTIONABLE", "INVALID", "UNDETERMINED"}


class AggregateError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class TimeframeResult:
    timeframe: str
    entry_direction: Optional[str]
    trade_state: Optional[str]
    record_id: Optional[str] = None


@dataclass(frozen=True)
class TC4TFAggregate:
    batch_id: str
    canonical_symbol: str
    provider: str
    completeness: str
    timeframe_results: Mapping[str, TimeframeResult]
    entry_directions: Tuple[str, ...]
    trade_states: Tuple[str, ...]
    direction_alignment: str
    state_alignment: str
    combined_trade_state: str = "NOT_DEFINED"
    execution_permission: bool = False


def _alignment(values: Tuple[Optional[str], ...]) -> str:
    if any(value is None for value in values):
        return "INSUFFICIENT"
    return "ALIGNED" if len(set(values)) == 1 else "DIVERGENT"


def aggregate_4tf(
    *,
    batch_id: str,
    canonical_symbol: str,
    provider: str,
    results: Mapping[str, TimeframeResult],
) -> TC4TFAggregate:
    if not batch_id or not canonical_symbol or not provider:
        raise AggregateError("AGGREGATE_IDENTITY_INVALID", "batch_id, canonical_symbol and provider are required")

    keys = tuple(results.keys())
    missing = [tf for tf in STANDARD_TIMEFRAMES if tf not in results]
    extra = [tf for tf in keys if tf not in STANDARD_TIMEFRAMES]
    if missing or extra:
        raise AggregateError(
            "BATCH_INCOMPLETE",
            f"required={STANDARD_TIMEFRAMES}; missing={missing}; extra={extra}",
        )

    ordered: Dict[str, TimeframeResult] = {}
    for tf in STANDARD_TIMEFRAMES:
        result = results[tf]
        if result.timeframe != tf:
            raise AggregateError("TIMEFRAME_MISMATCH", f"slot {tf} contains result for {result.timeframe}")
        if result.trade_state is not None and result.trade_state not in ALLOWED_STATES:
            raise AggregateError("TRADE_STATE_INVALID", f"unsupported per-timeframe state: {result.trade_state}")
        ordered[tf] = result

    directions_raw = tuple(ordered[tf].entry_direction for tf in STANDARD_TIMEFRAMES)
    states_raw = tuple(ordered[tf].trade_state for tf in STANDARD_TIMEFRAMES)

    return TC4TFAggregate(
        batch_id=batch_id,
        canonical_symbol=canonical_symbol,
        provider=provider,
        completeness="COMPLETE",
        timeframe_results=ordered,
        entry_directions=tuple(value for value in directions_raw if value is not None),
        trade_states=tuple(value for value in states_raw if value is not None),
        direction_alignment=_alignment(directions_raw),
        state_alignment=_alignment(states_raw),
    )
