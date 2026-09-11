#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tc.native.client import (  # noqa: E402
    InvalidNativeRequestError,
    NativeClient,
    NativeRequest,
    NativeResponseContractError,
    NativeTransportError,
    UnsupportedTimeframeError,
)


def make_request(
    *,
    request_id: str = "REQ-001",
    source_run_id: str = "RUN-001",
    execution_order: int = 1,
    analysis_source: str = "OANDA",
    analysis_symbol: str = "XAUUSD",
    timeframe: str = "H1",
) -> NativeRequest:
    return NativeRequest(
        request_id=request_id,
        source_run_id=source_run_id,
        execution_order=execution_order,
        analysis_source=analysis_source,
        analysis_symbol=analysis_symbol,
        timeframe=timeframe,
    )


class RecordingExecutor:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def __call__(self, *, exchange, symbol, interval):
        self.calls.append(
            {"exchange": exchange, "symbol": symbol, "interval": interval}
        )
        return self.response


class FailingExecutor:
    def __init__(self):
        self.calls = 0

    def __call__(self, *, exchange, symbol, interval):
        self.calls += 1
        raise RuntimeError("provider unavailable")


class NativeClientTests(unittest.TestCase):
    def test_exact_source_symbol_interval_translation(self):
        response = {"status": "completed"}
        executor = RecordingExecutor(response)
        result = NativeClient(executor).execute(
            make_request(
                analysis_source="OANDA",
                analysis_symbol="XAUUSD",
                timeframe="H1",
            )
        )

        self.assertEqual(
            executor.calls,
            [{"exchange": "OANDA", "symbol": "XAUUSD", "interval": "1h"}],
        )
        self.assertEqual(result.invocation.exchange, "OANDA")
        self.assertEqual(result.invocation.symbol, "XAUUSD")
        self.assertEqual(result.invocation.interval, "1h")
        self.assertIs(result.original_response, response)

    def test_all_frozen_timeframe_mappings(self):
        expected = {"D1": "1D", "H4": "4h", "H1": "1h", "M15": "15m"}
        for order, (timeframe, interval) in enumerate(expected.items(), start=1):
            with self.subTest(timeframe=timeframe):
                executor = RecordingExecutor({"status": "completed"})
                result = NativeClient(executor).execute(
                    make_request(
                        request_id=f"REQ-{order}",
                        execution_order=order,
                        timeframe=timeframe,
                    )
                )
                self.assertEqual(result.invocation.interval, interval)
                self.assertEqual(executor.calls[0]["interval"], interval)

    def test_unsupported_timeframe_fails_before_provider_call(self):
        executor = RecordingExecutor({"status": "completed"})
        with self.assertRaises(UnsupportedTimeframeError):
            NativeClient(executor).execute(make_request(timeframe="M5"))
        self.assertEqual(executor.calls, [])

    def test_symbol_is_not_auto_converted(self):
        executor = RecordingExecutor({"status": "completed"})
        result = NativeClient(executor).execute(
            make_request(analysis_symbol="GOLD#", timeframe="M15")
        )
        self.assertEqual(result.invocation.symbol, "GOLD#")
        self.assertEqual(executor.calls[0]["symbol"], "GOLD#")

    def test_provider_error_is_transport_failure_and_not_retried(self):
        executor = FailingExecutor()
        with self.assertRaises(NativeTransportError) as ctx:
            NativeClient(executor).execute(make_request())
        self.assertEqual(executor.calls, 1)
        self.assertEqual(ctx.exception.request_id, "REQ-001")
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)

    def test_repeated_explicit_calls_remain_distinct_requests(self):
        executor = RecordingExecutor({"status": "completed"})
        client = NativeClient(executor)
        first = client.execute(
            make_request(request_id="REQ-001", execution_order=1)
        )
        second = client.execute(
            make_request(request_id="REQ-002", execution_order=2)
        )

        self.assertEqual(len(executor.calls), 2)
        self.assertEqual(first.request.request_id, "REQ-001")
        self.assertEqual(second.request.request_id, "REQ-002")
        self.assertEqual(first.request.execution_order, 1)
        self.assertEqual(second.request.execution_order, 2)

    def test_unknown_response_fields_pass_through_untouched(self):
        response = {
            "status": "completed",
            "exchange": "OANDA",
            "symbol": "XAUUSD",
            "interval": "1h",
            "future_provider_field": {
                "nested": [1, {"raw": True}],
            },
        }
        executor = RecordingExecutor(response)
        result = NativeClient(executor).execute(make_request())

        self.assertIs(result.original_response, response)
        self.assertEqual(
            result.original_response["future_provider_field"],
            {"nested": [1, {"raw": True}]},
        )

    def test_non_mapping_response_is_explicit_contract_failure(self):
        executor = RecordingExecutor("not-a-mapping")
        with self.assertRaises(NativeResponseContractError) as ctx:
            NativeClient(executor).execute(make_request())
        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(ctx.exception.request_id, "REQ-001")

    def test_invalid_request_identity_is_rejected(self):
        with self.assertRaises(InvalidNativeRequestError):
            make_request(request_id="")
        with self.assertRaises(InvalidNativeRequestError):
            make_request(execution_order=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
