from __future__ import annotations

import copy
import json
import unittest

from tc.adapter import AdapterStage, TCAdapter, TCAdapterError
from tc.native.client import NativeClient, NativeRequest


def request(order: int = 3, request_id: str = "req-03") -> NativeRequest:
    return NativeRequest(
        request_id=request_id,
        source_run_id="RUN-001",
        execution_order=order,
        analysis_source="OANDA",
        analysis_symbol="XAUUSD",
        timeframe="H1",
    )


def response(analysis: object = None, *, include_analysis: bool = True) -> dict:
    payload = {
        "status": "completed",
        "exchange": "OANDA",
        "symbol": "XAUUSD",
        "interval": "1h",
        "model": "native-model",
        "timestamp": "2026-09-10T10:14:36.173Z",
        "provider_extra": {"keep": True},
    }
    if include_analysis:
        if analysis is None:
            analysis = json.dumps(
                {
                    "potentialPosition": {
                        "positionType": "long",
                        "entryPrice": 4428.296,
                        "stopLoss": 4405.199,
                        "takeProfits": [4445, 4460, 4480],
                    },
                    "observations": "Wait for confirmation before entry.",
                    "action_url": "https://example.invalid/chart?foo=1&chartId=chart-123",
                    "nativeExtra": {"preserve": "yes"},
                },
                separators=(",", ":"),
            )
        payload["analysis"] = analysis
    return payload


class FakePreserver:
    def __init__(self, fail: bool = False, blank_ref: bool = False) -> None:
        self.fail = fail
        self.blank_ref = blank_ref
        self.calls = []

    def preserve(self, *, request, original_response):
        self.calls.append((request, copy.deepcopy(original_response)))
        if self.fail:
            raise OSError("disk unavailable")
        if self.blank_ref:
            return ""
        return f"memory://raw/{request.source_run_id}/{request.execution_order:02d}.json"


class RecordingExecutor:
    def __init__(self, payload: dict | None = None, fail: bool = False) -> None:
        self.payload = payload if payload is not None else response()
        self.fail = fail
        self.calls = []

    def __call__(self, *, exchange, symbol, interval):
        self.calls.append((exchange, symbol, interval))
        if self.fail:
            raise RuntimeError("provider down")
        return copy.deepcopy(self.payload)


class AdapterTests(unittest.TestCase):
    def build(self, payload: dict | None = None, *, fail_provider=False, preserver=None):
        executor = RecordingExecutor(payload, fail=fail_provider)
        preserver = preserver or FakePreserver()
        return TCAdapter(NativeClient(executor), preserver), executor, preserver

    def test_parsed_raw_preserves_original_unknown_fields_and_analysis_string(self):
        payload = response()
        adapter, executor, preserver = self.build(payload)
        result = adapter.analyze(request()).raw_record
        self.assertEqual(executor.calls, [("OANDA", "XAUUSD", "1h")])
        self.assertEqual(len(preserver.calls), 1)
        self.assertEqual(preserver.calls[0][1], payload)
        self.assertEqual(result["original_response"], payload)
        self.assertEqual(result["original_response"]["analysis"], payload["analysis"])
        self.assertEqual(result["original_response"]["provider_extra"], {"keep": True})
        self.assertEqual(result["parsed_analysis"]["nativeExtra"], {"preserve": "yes"})
        self.assertEqual(result["parse_status"], {"state": "PARSED"})
        self.assertNotIn("trade_state", result)
        self.assertNotIn("question_mapping", result)

    def test_chart_id_is_derived_only(self):
        adapter, _, _ = self.build(response())
        result = adapter.analyze(request()).raw_record
        self.assertNotIn("chartId", result["original_response"])
        self.assertNotIn("chartId", result["parsed_analysis"])
        self.assertEqual(
            result["derived_metadata"]["chart_id"],
            {
                "value": "chart-123",
                "derived_from_pointer": "/parsed_analysis/action_url",
                "method": "url_query_parameter:chartId",
            },
        )

    def test_parse_error_still_preserves_raw_and_emits_parse_error(self):
        payload = response("{bad json")
        adapter, _, preserver = self.build(payload)
        result = adapter.analyze(request()).raw_record
        self.assertEqual(len(preserver.calls), 1)
        self.assertEqual(preserver.calls[0][1], payload)
        self.assertEqual(result["parse_status"]["state"], "PARSE_ERROR")
        self.assertNotIn("parsed_analysis", result)
        self.assertEqual(result["original_response"]["analysis"], "{bad json")

    def test_non_object_json_root_is_parse_error_not_normalized(self):
        payload = response('[1,2,3]')
        adapter, _, _ = self.build(payload)
        result = adapter.analyze(request()).raw_record
        self.assertEqual(result["parse_status"]["state"], "PARSE_ERROR")
        self.assertIn("root must be an object", result["parse_status"]["error_message"])
        self.assertNotIn("parsed_analysis", result)

    def test_missing_or_nonstring_analysis_is_not_parsed(self):
        for payload in (response(include_analysis=False), response({"already": "object"})):
            adapter, _, _ = self.build(payload)
            result = adapter.analyze(request()).raw_record
            self.assertEqual(result["parse_status"], {"state": "NOT_PARSED"})
            self.assertNotIn("parsed_analysis", result)

    def test_preservation_failure_stops_before_raw_output(self):
        adapter, _, preserver = self.build(response(), preserver=FakePreserver(fail=True))
        with self.assertRaises(TCAdapterError) as caught:
            adapter.analyze(request())
        self.assertEqual(caught.exception.stage, AdapterStage.RAW_PRESERVATION)
        self.assertEqual(len(preserver.calls), 1)
        self.assertIsNone(caught.exception.source_raw_artifact)

    def test_blank_artifact_reference_is_preservation_failure(self):
        adapter, _, _ = self.build(response(), preserver=FakePreserver(blank_ref=True))
        with self.assertRaises(TCAdapterError) as caught:
            adapter.analyze(request())
        self.assertEqual(caught.exception.stage, AdapterStage.RAW_PRESERVATION)

    def test_provider_failure_is_native_transport_and_never_preserves(self):
        preserver = FakePreserver()
        adapter, executor, _ = self.build(response(), fail_provider=True, preserver=preserver)
        with self.assertRaises(TCAdapterError) as caught:
            adapter.analyze(request())
        self.assertEqual(caught.exception.stage, AdapterStage.NATIVE_TRANSPORT)
        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(preserver.calls, [])

    def test_schema_known_type_mismatch_becomes_output_validation_after_preservation(self):
        bad_analysis = json.dumps(
            {"potentialPosition": {"entryPrice": "4428.296", "positionType": "long"}}
        )
        preserver = FakePreserver()
        adapter, _, _ = self.build(response(bad_analysis), preserver=preserver)
        with self.assertRaises(TCAdapterError) as caught:
            adapter.analyze(request())
        self.assertEqual(caught.exception.stage, AdapterStage.RAW_OUTPUT_VALIDATION)
        self.assertEqual(len(preserver.calls), 1)
        self.assertEqual(caught.exception.source_raw_artifact, "memory://raw/RUN-001/03.json")

    def test_record_identity_and_repeat_are_distinct(self):
        adapter, _, _ = self.build(response())
        first = adapter.analyze(request(order=3, request_id="req-03")).raw_record
        second = adapter.analyze(request(order=4, request_id="req-04")).raw_record
        self.assertEqual(first["record_identity"]["record_id"], "RUN-001:03")
        self.assertEqual(second["record_identity"]["record_id"], "RUN-001:04")
        self.assertNotEqual(first["record_identity"]["source_raw_artifact"], second["record_identity"]["source_raw_artifact"])
        self.assertEqual(first["wrapper_metadata"]["request_id"], "req-03")
        self.assertEqual(second["wrapper_metadata"]["request_id"], "req-04")

    def test_adapter_does_not_retry_provider(self):
        preserver = FakePreserver()
        adapter, executor, _ = self.build(response(), fail_provider=True, preserver=preserver)
        with self.assertRaises(TCAdapterError):
            adapter.analyze(request())
        self.assertEqual(len(executor.calls), 1)

    def test_output_contains_only_frozen_wrapper_top_level_fields(self):
        adapter, _, _ = self.build(response())
        result = adapter.analyze(request()).raw_record
        self.assertEqual(
            set(result),
            {
                "schema_version",
                "record_identity",
                "wrapper_metadata",
                "original_response",
                "parsed_analysis",
                "derived_metadata",
                "parse_status",
            },
        )


if __name__ == "__main__":
    unittest.main()
