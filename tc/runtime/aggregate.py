from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Tuple

ALLOWED_STATES = {"WAIT", "ACTIONABLE", "INVALID", "UNDETERMINED"}

PROFILE_SPECS = {
    "NORMAL": {
        "required": ("D1", "H4", "H1"),
        "environment_tf": "D1",
        "setup_tf": "H4",
        "decision_tf": "H1",
        "confirmation_tf": "M15",
    },
    "SHORT": {
        "required": ("H4", "H1", "M15"),
        "environment_tf": "H4",
        "setup_tf": "H1",
        "decision_tf": "M15",
        "confirmation_tf": None,
    },
}


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
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profits: Tuple[float, ...] = ()
    lower_tf_confirmation_required: bool = False


@dataclass(frozen=True)
class TCRoleAggregate:
    batch_id: str
    canonical_symbol: str
    provider: str
    profile: str
    runtime_status: str
    common_status: Optional[str]
    direction: Optional[str]
    role_sources: Mapping[str, Optional[str]]
    timeframe_results: Mapping[str, TimeframeResult]
    used_timeframes: Tuple[str, ...]
    decision_timeframe: str
    confirmation_timeframe: Optional[str]
    execution_permission: bool = False


def _validate_results(results: Mapping[str, TimeframeResult]) -> None:
    for timeframe, result in results.items():
        if result.timeframe != timeframe:
            raise AggregateError(
                "TIMEFRAME_MISMATCH",
                f"slot {timeframe} contains result for {result.timeframe}",
            )
        if result.trade_state is not None and result.trade_state not in ALLOWED_STATES:
            raise AggregateError(
                "TRADE_STATE_INVALID",
                f"unsupported per-timeframe state: {result.trade_state}",
            )


def _role_sources(spec, confirmation: Optional[str]) -> Mapping[str, Optional[str]]:
    return {
        "environment": spec["environment_tf"],
        "setup": spec["setup_tf"],
        "decision": spec["decision_tf"],
        "confirmation": confirmation,
    }


def aggregate_role_profile(
    *,
    batch_id: str,
    canonical_symbol: str,
    provider: str,
    profile: str,
    results: Mapping[str, TimeframeResult],
) -> TCRoleAggregate:
    if not batch_id or not canonical_symbol or not provider:
        raise AggregateError(
            "AGGREGATE_IDENTITY_INVALID",
            "batch_id, canonical_symbol and provider are required",
        )
    if profile not in PROFILE_SPECS:
        raise AggregateError("PROFILE_UNSUPPORTED", f"unsupported profile: {profile}")

    spec = PROFILE_SPECS[profile]
    missing = [tf for tf in spec["required"] if tf not in results]
    if missing:
        raise AggregateError("BATCH_INCOMPLETE", f"missing required timeframes: {missing}")

    _validate_results(results)
    decision = results[spec["decision_tf"]]
    confirmation_tf = spec["confirmation_tf"]

    # NORMAL may drill down to M15 only when H1 explicitly requests lower-TF confirmation.
    if profile == "NORMAL" and decision.lower_tf_confirmation_required:
        if confirmation_tf not in results:
            return TCRoleAggregate(
                batch_id=batch_id,
                canonical_symbol=canonical_symbol,
                provider=provider,
                profile=profile,
                runtime_status="NEEDS_DRILLDOWN",
                common_status=None,
                direction=decision.entry_direction,
                role_sources=_role_sources(spec, confirmation_tf),
                timeframe_results=dict(results),
                used_timeframes=tuple(results.keys()),
                decision_timeframe=spec["decision_tf"],
                confirmation_timeframe=confirmation_tf,
            )

        confirmation = results[confirmation_tf]
        same_direction = (
            decision.entry_direction is not None
            and confirmation.entry_direction == decision.entry_direction
        )

        if confirmation.trade_state == "ACTIONABLE" and same_direction:
            runtime_status = "FINALIZED"
            common_status = "TRADE"
        elif confirmation.trade_state == "WAIT":
            runtime_status = "FINALIZED"
            common_status = "WAIT"
        else:
            runtime_status = "HOLD"
            common_status = None

        return TCRoleAggregate(
            batch_id=batch_id,
            canonical_symbol=canonical_symbol,
            provider=provider,
            profile=profile,
            runtime_status=runtime_status,
            common_status=common_status,
            direction=decision.entry_direction,
            role_sources=_role_sources(spec, confirmation_tf),
            timeframe_results=dict(results),
            used_timeframes=tuple(results.keys()),
            decision_timeframe=spec["decision_tf"],
            confirmation_timeframe=confirmation_tf,
        )

    common_map = {
        "ACTIONABLE": "TRADE",
        "WAIT": "WAIT",
        "INVALID": "INVALID",
    }
    common_status = common_map.get(decision.trade_state)
    runtime_status = "FINALIZED" if common_status is not None else "HOLD"

    return TCRoleAggregate(
        batch_id=batch_id,
        canonical_symbol=canonical_symbol,
        provider=provider,
        profile=profile,
        runtime_status=runtime_status,
        common_status=common_status,
        direction=decision.entry_direction,
        role_sources=_role_sources(spec, None),
        timeframe_results=dict(results),
        used_timeframes=tuple(results.keys()),
        decision_timeframe=spec["decision_tf"],
        confirmation_timeframe=None,
    )
