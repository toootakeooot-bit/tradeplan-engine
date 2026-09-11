from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

TIMEFRAME_TO_NATIVE_INTERVAL: dict[str, str] = {
    "D1": "1D",
    "H4": "4h",
    "H1": "1h",
    "M15": "15m",
}


class NativeClientError(Exception):
    """Base class for TC Native Client failures."""


class InvalidNativeRequestError(NativeClientError, ValueError):
    """Raised when a Native request is structurally invalid."""


class UnsupportedTimeframeError(InvalidNativeRequestError):
    """Raised when no frozen TC v1 interval mapping exists."""


class NativeTransportError(NativeClientError):
    """Raised when the injected provider executor fails."""

    def __init__(self, request_id: str, message: str = "provider executor failed") -> None:
        super().__init__(f"{message}; request_id={request_id}")
        self.request_id = request_id


class NativeResponseContractError(NativeClientError, TypeError):
    """Raised when the provider executor does not return a mapping-like response."""

    def __init__(self, request_id: str, response_type: type[Any]) -> None:
        super().__init__(
            f"provider executor returned unsupported response type "
            f"{response_type.__name__}; request_id={request_id}"
        )
        self.request_id = request_id
        self.response_type = response_type


@dataclass(frozen=True, slots=True)
class NativeRequest:
    """One explicit TC Native request.

    The client does not generate or deduplicate identities. A retry is represented
    by the caller as a new NativeRequest with a new request_id / execution identity.
    """

    request_id: str
    source_run_id: str
    execution_order: int
    analysis_source: str
    analysis_symbol: str
    timeframe: str

    def __post_init__(self) -> None:
        for field_name in (
            "request_id",
            "source_run_id",
            "analysis_source",
            "analysis_symbol",
            "timeframe",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise InvalidNativeRequestError(
                    f"{field_name} must be a non-empty string"
                )
        if isinstance(self.execution_order, bool) or not isinstance(
            self.execution_order, int
        ):
            raise InvalidNativeRequestError("execution_order must be an integer")
        if self.execution_order < 1:
            raise InvalidNativeRequestError("execution_order must be >= 1")


@dataclass(frozen=True, slots=True)
class NativeInvocation:
    """Exact provider-facing request surface verified for TC v1."""

    exchange: str
    symbol: str
    interval: str


@dataclass(frozen=True, slots=True)
class NativeCallResult:
    """Uninterpreted Native response plus request/invocation provenance."""

    request: NativeRequest
    invocation: NativeInvocation
    original_response: Mapping[str, Any]


class ProviderExecutor(Protocol):
    """Injected provider boundary.

    The concrete host integration must accept only the verified TC v1 Native
    request surface. TC-P1 intentionally defines no URL, credentials, SDK, retry,
    image input, prompt input or multi-timeframe provider contract.
    """

    def __call__(
        self, *, exchange: str, symbol: str, interval: str
    ) -> Mapping[str, Any]:
        ...


def translate_request(request: NativeRequest) -> NativeInvocation:
    """Translate only frozen field names and timeframe labels."""

    try:
        interval = TIMEFRAME_TO_NATIVE_INTERVAL[request.timeframe]
    except KeyError as exc:
        raise UnsupportedTimeframeError(
            f"unsupported timeframe: {request.timeframe!r}"
        ) from exc

    return NativeInvocation(
        exchange=request.analysis_source,
        symbol=request.analysis_symbol,
        interval=interval,
    )


class NativeClient:
    """Production TC Native Client boundary with explicit dependency injection."""

    def __init__(self, executor: ProviderExecutor) -> None:
        if not callable(executor):
            raise TypeError("executor must be callable")
        self._executor = executor

    def execute(self, request: NativeRequest) -> NativeCallResult:
        """Execute exactly one provider call, with no automatic retry."""

        if not isinstance(request, NativeRequest):
            raise InvalidNativeRequestError("request must be NativeRequest")

        invocation = translate_request(request)

        try:
            response = self._executor(
                exchange=invocation.exchange,
                symbol=invocation.symbol,
                interval=invocation.interval,
            )
        except Exception as exc:
            raise NativeTransportError(request.request_id) from exc

        if not isinstance(response, Mapping):
            raise NativeResponseContractError(request.request_id, type(response))

        return NativeCallResult(
            request=request,
            invocation=invocation,
            original_response=response,
        )
