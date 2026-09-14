from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from tc.adapter.native_client import NativeClientError, TradingCursorNativeClient


NativeCall = Callable[..., Mapping[str, Any]]


@dataclass(frozen=True)
class CallableNativeClient:
    """Bind any host-provided TradingCursor call into the repo NativeClient contract.

    The host callable must accept keyword arguments `exchange`, `symbol`, and
    `interval`, and must return the complete Native response mapping unchanged.
    This adapter performs no retry, symbol conversion, interval substitution,
    strategy inference, or response rewriting.
    """

    call: NativeCall

    def request_analysis(
        self,
        *,
        exchange: str,
        symbol: str,
        interval: str,
    ) -> Mapping[str, Any]:
        try:
            response = self.call(exchange=exchange, symbol=symbol, interval=interval)
        except Exception as exc:
            raise NativeClientError("HOST_NATIVE_CALL_FAILED", str(exc)) from exc

        if not isinstance(response, Mapping) or not response:
            raise NativeClientError(
                "HOST_NATIVE_RESPONSE_INVALID",
                "host TradingCursor call returned an empty or non-mapping response",
            )
        return response


@dataclass
class UsageTrackingNativeClient:
    """Count successful Native responses without changing Native semantics.

    A call is counted only after the wrapped client returns a non-empty mapping.
    This boundary is intentionally before Raw preservation, Adapter mapping and
    normalization so a consumed provider call is not lost if a later stage fails.
    """

    client: TradingCursorNativeClient
    successful_calls: int = 0

    def request_analysis(
        self,
        *,
        exchange: str,
        symbol: str,
        interval: str,
    ) -> Mapping[str, Any]:
        response = self.client.request_analysis(
            exchange=exchange,
            symbol=symbol,
            interval=interval,
        )
        if isinstance(response, Mapping) and response:
            self.successful_calls += 1
        return response
