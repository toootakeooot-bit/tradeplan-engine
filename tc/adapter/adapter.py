from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Protocol
from urllib.parse import parse_qs, urlparse

from tc.native.client import (
    InvalidNativeRequestError,
    NativeClient,
    NativeClientError,
    NativeRequest,
)

SCHEMA_VERSION = "1.0.0"
ADAPTER_CONTRACT_VERSION = "TC4-8"
_ALLOWED_PARSE_STATES = {"PARSED", "NOT_PARSED", "PARSE_ERROR"}


class AdapterStage(str, Enum):
    INPUT_VALIDATION = "INPUT_VALIDATION"
    NATIVE_TRANSPORT = "NATIVE_TRANSPORT"
    RAW_PRESERVATION = "RAW_PRESERVATION"
    RAW_OUTPUT_VALIDATION = "RAW_OUTPUT_VALIDATION"


class TCAdapterError(Exception):
    """Operational Adapter failure. Never a Trade State."""

    def __init__(
        self,
        stage: AdapterStage,
        request_id: str,
        message: str,
        *,
        source_raw_artifact: str | None = None,
    ) -> None:
        super().__init__(f"{stage.value}: {message}; request_id={request_id}")
        self.stage = stage
        self.request_id = request_id
        self.source_raw_artifact = source_raw_artifact


class RawPreserver(Protocol):
    """Narrow preservation port implemented concretely in TC-P3."""

    def preserve(
        self,
        *,
        request: NativeRequest,
        original_response: Mapping[str, Any],
    ) -> str:
        """Persist one untouched Native response and return a stable reference."""
        ...


@dataclass(frozen=True, slots=True)
class AdapterResult:
    raw_record: dict[str, Any]


def build_record_id(source_run_id: str, execution_order: int) -> str:
    return f"{source_run_id}:{execution_order:02d}"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_nonempty_string(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path} must be a non-empty string")


def _validate_number_list(value: Any, path: str) -> None:
    if not isinstance(value, list) or not all(_is_number(item) for item in value):
        raise ValueError(f"{path} must be an array of numbers")


def validate_tc_tradeplan_raw(record: Mapping[str, Any]) -> None:
    """Validate the subset of Draft 2020-12 constraints frozen in v1.0.0.

    This is intentionally a schema-aligned output guard, not a replacement schema
    authority. `tc/schema/tc_tradeplan_raw.schema.json` remains authoritative.
    """

    allowed_top = {
        "schema_version",
        "record_identity",
        "wrapper_metadata",
        "original_response",
        "parsed_analysis",
        "derived_metadata",
        "parse_status",
    }
    if not isinstance(record, Mapping):
        raise ValueError("record must be an object")
    if set(record) - allowed_top:
        raise ValueError("unexpected top-level field")
    for key in ("schema_version", "record_identity", "original_response", "parse_status"):
        if key not in record:
            raise ValueError(f"missing required field: {key}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise ValueError("schema_version must be 1.0.0")

    identity = record["record_identity"]
    if not isinstance(identity, Mapping):
        raise ValueError("record_identity must be an object")
    required_identity = {"record_id", "source_run_id", "execution_order", "source_raw_artifact"}
    if set(identity) != required_identity:
        raise ValueError("record_identity fields do not match frozen schema")
    _require_nonempty_string(identity["record_id"], "record_identity.record_id")
    _require_nonempty_string(identity["source_run_id"], "record_identity.source_run_id")
    if isinstance(identity["execution_order"], bool) or not isinstance(identity["execution_order"], int) or identity["execution_order"] < 1:
        raise ValueError("record_identity.execution_order must be integer >= 1")
    _require_nonempty_string(identity["source_raw_artifact"], "record_identity.source_raw_artifact")

    if "wrapper_metadata" in record and not isinstance(record["wrapper_metadata"], Mapping):
        raise ValueError("wrapper_metadata must be an object")

    original = record["original_response"]
    if not isinstance(original, Mapping) or not original:
        raise ValueError("original_response must be a non-empty object")
    for field in ("status", "exchange", "symbol", "interval", "model", "timestamp"):
        if field in original and not isinstance(original[field], str):
            raise ValueError(f"original_response.{field} must be a string")

    parsed = record.get("parsed_analysis")
    if parsed is not None:
        if not isinstance(parsed, Mapping):
            raise ValueError("parsed_analysis must be an object")
        position = parsed.get("potentialPosition")
        if position is not None:
            if not isinstance(position, Mapping):
                raise ValueError("parsed_analysis.potentialPosition must be an object")
            for field in ("entryPrice", "stopLoss"):
                if field in position and not _is_number(position[field]):
                    raise ValueError(f"parsed_analysis.potentialPosition.{field} must be a number")
            if "positionType" in position and not isinstance(position["positionType"], str):
                raise ValueError("parsed_analysis.potentialPosition.positionType must be a string")
            if "takeProfits" in position:
                _validate_number_list(position["takeProfits"], "parsed_analysis.potentialPosition.takeProfits")

        indicators = parsed.get("indicatorReadings")
        if indicators is not None:
            if not isinstance(indicators, list) or not all(isinstance(item, Mapping) for item in indicators):
                raise ValueError("parsed_analysis.indicatorReadings must be an array of objects")
            for index, item in enumerate(indicators):
                for field in ("id", "label"):
                    if field in item and not isinstance(item[field], str):
                        raise ValueError(f"parsed_analysis.indicatorReadings[{index}].{field} must be a string")
                if "values" in item and not isinstance(item["values"], Mapping):
                    raise ValueError(f"parsed_analysis.indicatorReadings[{index}].values must be an object")

        metrics = parsed.get("priceMetrics")
        if metrics is not None:
            if not isinstance(metrics, Mapping):
                raise ValueError("parsed_analysis.priceMetrics must be an object")
            for field in ("supportLevels", "resistanceLevels"):
                if field in metrics:
                    _validate_number_list(metrics[field], f"parsed_analysis.priceMetrics.{field}")
            if "current_price" in metrics and not _is_number(metrics["current_price"]):
                raise ValueError("parsed_analysis.priceMetrics.current_price must be a number")

        assumption = parsed.get("futureAssumption")
        if assumption is not None:
            if not isinstance(assumption, Mapping):
                raise ValueError("parsed_analysis.futureAssumption must be an object")
            for field in ("trend", "patternDetected"):
                if field in assumption and not isinstance(assumption[field], str):
                    raise ValueError(f"parsed_analysis.futureAssumption.{field} must be a string")
            if "confidenceScore" in assumption and not _is_number(assumption["confidenceScore"]):
                raise ValueError("parsed_analysis.futureAssumption.confidenceScore must be a number")

        for field in ("observations", "action_url"):
            if field in parsed and not isinstance(parsed[field], str):
                raise ValueError(f"parsed_analysis.{field} must be a string")

    derived = record.get("derived_metadata")
    if derived is not None:
        if not isinstance(derived, Mapping) or set(derived) - {"chart_id"}:
            raise ValueError("derived_metadata has unsupported fields")
        if "chart_id" in derived:
            chart_id = derived["chart_id"]
            required_chart = {"value", "derived_from_pointer", "method"}
            if not isinstance(chart_id, Mapping) or set(chart_id) != required_chart:
                raise ValueError("derived_metadata.chart_id fields do not match frozen schema")
            _require_nonempty_string(chart_id["value"], "derived_metadata.chart_id.value")
            if chart_id["derived_from_pointer"] != "/parsed_analysis/action_url":
                raise ValueError("derived_metadata.chart_id.derived_from_pointer mismatch")
            if chart_id["method"] != "url_query_parameter:chartId":
                raise ValueError("derived_metadata.chart_id.method mismatch")

    parse_status = record["parse_status"]
    if not isinstance(parse_status, Mapping) or set(parse_status) - {"state", "error_message"}:
        raise ValueError("parse_status has unsupported fields")
    if "state" not in parse_status or parse_status["state"] not in _ALLOWED_PARSE_STATES:
        raise ValueError("parse_status.state is invalid")
    if "error_message" in parse_status and not isinstance(parse_status["error_message"], str):
        raise ValueError("parse_status.error_message must be a string")
    if parse_status["state"] == "PARSED":
        if "parsed_analysis" not in record:
            raise ValueError("PARSED requires parsed_analysis")
        if not isinstance(original.get("analysis"), str):
            raise ValueError("PARSED requires original_response.analysis string")

    try:
        json.dumps(record, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("record is not JSON-compatible") from exc


def _parse_analysis(original_response: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if "analysis" not in original_response or not isinstance(original_response["analysis"], str):
        return {"state": "NOT_PARSED"}, None

    try:
        decoded = json.loads(original_response["analysis"])
    except json.JSONDecodeError as exc:
        return {"state": "PARSE_ERROR", "error_message": f"JSONDecodeError: {exc.msg}"}, None

    if not isinstance(decoded, dict):
        return {"state": "PARSE_ERROR", "error_message": "analysis JSON root must be an object"}, None
    return {"state": "PARSED"}, decoded


def _derive_chart_id(parsed_analysis: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not parsed_analysis:
        return None
    action_url = parsed_analysis.get("action_url")
    if not isinstance(action_url, str) or not action_url:
        return None
    values = parse_qs(urlparse(action_url).query, keep_blank_values=True).get("chartId")
    if not values or not values[0]:
        return None
    return {
        "chart_id": {
            "value": values[0],
            "derived_from_pointer": "/parsed_analysis/action_url",
            "method": "url_query_parameter:chartId",
        }
    }


class TCAdapter:
    """TC Native response -> TCTradePlanRaw v1.0.0 boundary.

    No Question mapping, Trade State semantics, 4TF synthesis, sizing, risk, or
    execution logic belongs here.
    """

    def __init__(self, native_client: NativeClient, preserver: RawPreserver) -> None:
        if not isinstance(native_client, NativeClient):
            raise TypeError("native_client must be NativeClient")
        if not hasattr(preserver, "preserve") or not callable(preserver.preserve):
            raise TypeError("preserver must implement preserve()")
        self._native_client = native_client
        self._preserver = preserver

    def analyze(self, request: NativeRequest) -> AdapterResult:
        if not isinstance(request, NativeRequest):
            request_id = getattr(request, "request_id", "<unknown>")
            raise TCAdapterError(AdapterStage.INPUT_VALIDATION, request_id, "request must be NativeRequest")

        try:
            native_result = self._native_client.execute(request)
        except InvalidNativeRequestError as exc:
            raise TCAdapterError(AdapterStage.INPUT_VALIDATION, request.request_id, str(exc)) from exc
        except NativeClientError as exc:
            raise TCAdapterError(AdapterStage.NATIVE_TRANSPORT, request.request_id, str(exc)) from exc

        original_response = copy.deepcopy(dict(native_result.original_response))

        try:
            source_raw_artifact = self._preserver.preserve(
                request=request,
                original_response=original_response,
            )
        except Exception as exc:
            raise TCAdapterError(
                AdapterStage.RAW_PRESERVATION,
                request.request_id,
                "raw preservation failed",
            ) from exc
        if not isinstance(source_raw_artifact, str) or not source_raw_artifact.strip():
            raise TCAdapterError(
                AdapterStage.RAW_PRESERVATION,
                request.request_id,
                "preserver returned an invalid source_raw_artifact",
            )

        parse_status, parsed_analysis = _parse_analysis(original_response)
        record: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "record_identity": {
                "record_id": build_record_id(request.source_run_id, request.execution_order),
                "source_run_id": request.source_run_id,
                "execution_order": request.execution_order,
                "source_raw_artifact": source_raw_artifact,
            },
            "wrapper_metadata": {
                "request_id": request.request_id,
                "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
                "requested_timeframe": request.timeframe,
            },
            "original_response": original_response,
            "parse_status": parse_status,
        }
        if parsed_analysis is not None:
            record["parsed_analysis"] = parsed_analysis
            derived = _derive_chart_id(parsed_analysis)
            if derived is not None:
                record["derived_metadata"] = derived

        try:
            validate_tc_tradeplan_raw(record)
        except ValueError as exc:
            raise TCAdapterError(
                AdapterStage.RAW_OUTPUT_VALIDATION,
                request.request_id,
                str(exc),
                source_raw_artifact=source_raw_artifact,
            ) from exc

        return AdapterResult(raw_record=record)
