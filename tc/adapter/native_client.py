from __future__ import annotations

from typing import Any, Mapping, Protocol


class NativeClientError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class TradingCursorNativeClient(Protocol):
    """Host-supplied TradingCursor transport.

    The repository owns this interface, not the external connector binding.
    Implementations must issue exactly one TradingCursor request per call and
    return the full provider-native response mapping without strategy edits.
    """

    def request_analysis(
        self,
        *,
        exchange: str,
        symbol: str,
        interval: str,
    ) -> Mapping[str, Any]:
        ...
