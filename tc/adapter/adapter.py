from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse


_TIMEFRAME_INTERVAL = {
    "D1": "1D",
    "H4": "4h",
    "H1": "1h",
    "M15": "15m",
}


class AdapterError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class AdapterRequest:
    request_id: str
    source_run_id: str
    execution_order: int
    analysis_source: str
    analysis_symbol: str
    timeframe: str
    profile: str
    role: str


def native_interval(timeframe: str) -> str:
    try:
        return _TIMEFRAME_INTERVAL[timeframe]
    except KeyError as exc:
        raise AdapterError("TIMEFRAME_UNSUPPORTED", f"unsupported timeframe: {timeframe}") from exc


def _parse_analysis(value: Any) -> tuple[str, Mapping[str, Any] | None, str | None]:
    if not isinstance(value, str):
        return "NOT_PARSED", None, None
    try:
        parsed = json.loads(value)
    except Exception as exc:  # preserve Raw even when parsing fails
        return "PARSE_ERROR", None, str(exc)
    if not isinstance(parsed, dict):
        return "PARSE_ERROR", None, "analysis JSON must decode to an object"
    return "PARSED", parsed, None


def _derive_chart_id(parsed: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
    if not parsed:
        return None
    action_url = parsed.get("action_url")
    if not isinstance(action_url, str):
        return None
    values = parse_qs(urlparse(action_url).query).get("chartId")
    if not values or not values[0]:
        return None
    return {
        "value": values[0],
        "derived_from_pointer": "/parsed_analysis/action_url",
        "method": "url_query_parameter:chartId",
    }


def adapt_native_response(
    *,
    request: AdapterRequest,
    native_response: Mapping[str, Any],
    source_raw_artifact: str,
) -> dict[str, Any]:
    """Wrap one native response as TCTradePlanRaw v1.0.0.

    This function performs transport-envelope validation, Raw preservation and
    lossless JSON parsing only. It does not map strategy fields or Trade State.
    """
    if not request.request_id or not request.source_run_id:
        raise AdapterError("REQUEST_IDENTITY_INVALID", "request_id and source_run_id are required")
    if request.execution_order < 1:
        raise AdapterError("EXECUTION_ORDER_INVALID", "execution_order must be >= 1")
    expected_interval = native_interval(request.timeframe)
    if not source_raw_artifact:
        raise AdapterError("RAW_ARTIFACT_REQUIRED", "source_raw_artifact is required")
    if not isinstance(native_response, Mapping) or not native_response:
        raise AdapterError("NATIVE_RESPONSE_INVALID", "native_response must be a non-empty mapping")

    actual_exchange = native_response.get("exchange")
    actual_symbol = native_response.get("symbol")
    actual_interval = native_response.get("interval")
    if actual_exchange is not None and actual_exchange != request.analysis_source:
        raise AdapterError("NATIVE_SOURCE_MISMATCH", f"expected {request.analysis_source}, got {actual_exchange}")
    if actual_symbol is not None and actual_symbol != request.analysis_symbol:
        raise AdapterError("NATIVE_SYMBOL_MISMATCH", f"expected {request.analysis_symbol}, got {actual_symbol}")
    if actual_interval is not None and actual_interval != expected_interval:
        raise AdapterError("NATIVE_INTERVAL_MISMATCH", f"expected {expected_interval}, got {actual_interval}")

    original = copy.deepcopy(dict(native_response))
    parse_state, parsed_analysis, parse_error = _parse_analysis(original.get("analysis"))

    raw: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_identity": {
            "record_id": f"{request.source_run_id}:{request.execution_order}",
            "source_run_id": request.source_run_id,
            "execution_order": request.execution_order,
            "source_raw_artifact": source_raw_artifact,
        },
        "wrapper_metadata": {
            "request_id": request.request_id,
            "adapter_contract_version": "TC4_8_IMPL_V1",
            "profile": request.profile,
            "role": request.role,
            "timeframe": request.timeframe,
        },
        "original_response": original,
        "parse_status": {"state": parse_state},
    }

    if parsed_analysis is not None:
        raw["parsed_analysis"] = copy.deepcopy(dict(parsed_analysis))
        chart_id = _derive_chart_id(parsed_analysis)
        if chart_id is not None:
            raw["derived_metadata"] = {"chart_id": chart_id}
    if parse_error:
        raw["parse_status"]["error_message"] = parse_error

    return raw
