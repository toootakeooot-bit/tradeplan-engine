from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from tc.runtime.usage import TCUsageRuntimeInfo


TRIGGER_SPOT = "SPOT"
TRIGGER_PERIODIC = "PERIODIC"
DELIVERY_PENDING = "PENDING"
DELIVERY_SENT = "SENT"
DELIVERY_FAILED = "FAILED"


@dataclass(frozen=True)
class TCNotificationResult:
    symbol: str
    status: str
    direction: str
    profile: str | None = None
    environment: Any = None
    setup: Any = None
    entry_price: Any = None
    stop_loss: Any = None
    take_profits: tuple[Any, ...] = ()
    invalidation: Any = None
    used_timeframes: tuple[str, ...] = ()
    provider: str | None = None
    provider_symbol: str | None = None
    timeframe_rows: tuple[Mapping[str, Any], ...] = ()
    execution_permission: bool = False
    runtime_error: str | None = None


@dataclass(frozen=True)
class TCNotificationPayload:
    notification_id: str
    trigger_type: str
    run_id: str
    timestamp: str
    results: tuple[TCNotificationResult, ...]
    runtime_usage: TCUsageRuntimeInfo | None = None
    runtime_error: str | None = None


@dataclass(frozen=True)
class NotificationEnvelope:
    payload: TCNotificationPayload
    delivery_status: str = DELIVERY_PENDING
    attempts: int = 0
    last_error: str | None = None
    provider_message_id: str | None = None


def make_spot_notification_id(run_id: str) -> str:
    return f"tc:spot:{run_id}"


def make_periodic_notification_id(cycle_id: str) -> str:
    return f"tc:periodic:{cycle_id}"


def _tuple(value: Sequence[Any] | None) -> tuple[Any, ...]:
    if value is None:
        return ()
    return tuple(value)


def result_from_tradeplan_state(state: Mapping[str, Any]) -> TCNotificationResult:
    evidence = state.get("evidence") or {}
    environment = state.get("environment") or {}
    setup = state.get("setup") or {}
    entry = state.get("entry") or {}
    stop_loss = state.get("stop_loss") or {}
    take_profit = state.get("take_profit") or {}
    invalidation = state.get("invalidation") or {}

    return TCNotificationResult(
        symbol=str(state.get("symbol") or "UNKNOWN"),
        status=str(state.get("status") or "HOLD"),
        direction=str(state.get("direction") or "NONE"),
        profile=evidence.get("profile"),
        environment=environment.get("direction"),
        setup=setup.get("evidence"),
        entry_price=entry.get("price"),
        stop_loss=stop_loss.get("price"),
        take_profits=_tuple(take_profit.get("prices")),
        invalidation=invalidation.get("evidence"),
        used_timeframes=tuple(evidence.get("used_timeframes") or ()),
        provider=evidence.get("provider"),
        provider_symbol=evidence.get("provider_symbol"),
        timeframe_rows=tuple(evidence.get("timeframe_decisions") or ()),
        execution_permission=bool(state.get("execution_permission", False)),
    )


def error_result(symbol: str, error: str, *, profile: str | None = None) -> TCNotificationResult:
    return TCNotificationResult(
        symbol=symbol,
        status="ERROR",
        direction="NONE",
        profile=profile,
        runtime_error=error,
        execution_permission=False,
    )


def build_spot_payload(
    *,
    run_id: str,
    timestamp: str,
    tradeplan_state: Mapping[str, Any] | None,
    runtime_usage: TCUsageRuntimeInfo | None,
    runtime_error: str | None = None,
    fallback_symbol: str = "UNKNOWN",
    profile: str | None = None,
) -> TCNotificationPayload:
    if tradeplan_state is not None:
        results = (result_from_tradeplan_state(tradeplan_state),)
    else:
        results = (error_result(fallback_symbol, runtime_error or "TC Spot failed", profile=profile),)

    return TCNotificationPayload(
        notification_id=make_spot_notification_id(run_id),
        trigger_type=TRIGGER_SPOT,
        run_id=run_id,
        timestamp=timestamp,
        results=results,
        runtime_usage=runtime_usage,
        runtime_error=runtime_error,
    )


def build_periodic_payload(
    *,
    cycle_id: str,
    timestamp: str,
    tradeplan_states: Sequence[Mapping[str, Any]],
    runtime_usage: TCUsageRuntimeInfo | None,
    runtime_errors: Mapping[str, str] | None = None,
) -> TCNotificationPayload:
    results = [result_from_tradeplan_state(state) for state in tradeplan_states]
    for symbol, error in (runtime_errors or {}).items():
        results.append(error_result(symbol, error))

    payload_error = None
    if results and all(result.status == "ERROR" for result in results):
        payload_error = "all periodic TC results failed"

    return TCNotificationPayload(
        notification_id=make_periodic_notification_id(cycle_id),
        trigger_type=TRIGGER_PERIODIC,
        run_id=cycle_id,
        timestamp=timestamp,
        results=tuple(results),
        runtime_usage=runtime_usage,
        runtime_error=payload_error,
    )


def payload_to_dict(payload: TCNotificationPayload) -> dict[str, Any]:
    return asdict(payload)


def _result_from_dict(data: Mapping[str, Any]) -> TCNotificationResult:
    return TCNotificationResult(
        symbol=str(data["symbol"]),
        status=str(data["status"]),
        direction=str(data["direction"]),
        profile=data.get("profile"),
        environment=data.get("environment"),
        setup=data.get("setup"),
        entry_price=data.get("entry_price"),
        stop_loss=data.get("stop_loss"),
        take_profits=tuple(data.get("take_profits") or ()),
        invalidation=data.get("invalidation"),
        used_timeframes=tuple(data.get("used_timeframes") or ()),
        provider=data.get("provider"),
        provider_symbol=data.get("provider_symbol"),
        timeframe_rows=tuple(data.get("timeframe_rows") or ()),
        execution_permission=bool(data.get("execution_permission", False)),
        runtime_error=data.get("runtime_error"),
    )


def payload_from_dict(data: Mapping[str, Any]) -> TCNotificationPayload:
    usage_data = data.get("runtime_usage")
    usage = TCUsageRuntimeInfo(**usage_data) if usage_data else None
    results = tuple(_result_from_dict(result) for result in data.get("results", ()))
    return TCNotificationPayload(
        notification_id=str(data["notification_id"]),
        trigger_type=str(data["trigger_type"]),
        run_id=str(data["run_id"]),
        timestamp=str(data["timestamp"]),
        results=results,
        runtime_usage=usage,
        runtime_error=data.get("runtime_error"),
    )


def envelope_to_dict(envelope: NotificationEnvelope) -> dict[str, Any]:
    return {
        "payload": payload_to_dict(envelope.payload),
        "delivery_status": envelope.delivery_status,
        "attempts": envelope.attempts,
        "last_error": envelope.last_error,
        "provider_message_id": envelope.provider_message_id,
    }


def envelope_from_dict(data: Mapping[str, Any]) -> NotificationEnvelope:
    return NotificationEnvelope(
        payload=payload_from_dict(data["payload"]),
        delivery_status=str(data.get("delivery_status") or DELIVERY_PENDING),
        attempts=int(data.get("attempts") or 0),
        last_error=data.get("last_error"),
        provider_message_id=data.get("provider_message_id"),
    )
