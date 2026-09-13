import json
import unittest

from tc.adapter.adapter import AdapterRequest, adapt_native_response
from tc.normalizer.normalizer import normalize_tc_raw
from tc.runtime.command import parse_spot_command
from tc.runtime.orchestrator import run_spot_entry_pre
from tc.runtime.symbol import resolve_symbol


def native_response(interval, observations, position=None, trend="neutral"):
    analysis = {
        "futureAssumption": {"trend": trend},
        "observations": observations,
        "action_url": "https://www.tradingcursor.com/view?chartId=test-chart",
    }
    if position is not None:
        analysis["potentialPosition"] = position
    return {
        "status": "completed",
        "exchange": "OANDA",
        "symbol": "XAUUSD",
        "interval": interval,
        "analysis": json.dumps(analysis),
        "model": "test-model",
        "timestamp": "2026-09-13T00:00:00Z",
        "unknown_native_field": {"keep": True},
    }


class FakeSink:
    def __init__(self):
        self.saved = []

    def preserve(self, *, source_run_id, execution_order, native_response):
        self.saved.append((source_run_id, execution_order, dict(native_response)))
        return f"memory://{source_run_id}/{execution_order}.json"


class FakeClient:
    def __init__(self, responses):
        self.responses = {k: list(v) for k, v in responses.items()}
        self.calls = []

    def request_analysis(self, *, exchange, symbol, interval):
        self.calls.append((exchange, symbol, interval))
        return self.responses[interval].pop(0)


class AdapterNormalizerTests(unittest.TestCase):
    def test_adapter_preserves_unknown_native_and_parses_analysis(self):
        response = native_response(
            "1h",
            "A long position is recommended with entry at current price.",
            {"positionType": "long", "entryPrice": 100, "stopLoss": 90, "takeProfits": [110]},
            "bullish",
        )
        raw = adapt_native_response(
            request=AdapterRequest(
                request_id="r1",
                source_run_id="run1",
                execution_order=1,
                analysis_source="OANDA",
                analysis_symbol="XAUUSD",
                timeframe="H1",
                profile="NORMAL",
                role="DECISION",
            ),
            native_response=response,
            source_raw_artifact="memory://run1/1.json",
        )
        self.assertTrue(raw["original_response"]["unknown_native_field"]["keep"])
        self.assertEqual(raw["parse_status"]["state"], "PARSED")
        self.assertEqual(raw["derived_metadata"]["chart_id"]["value"], "test-chart")

        normalized = normalize_tc_raw(raw)
        self.assertEqual(normalized.entry_direction, "LONG")
        self.assertEqual(normalized.trade_state, "ACTIONABLE")
        self.assertEqual(normalized.entry_price, 100.0)

    def test_explicit_wait_beats_candidate_plan(self):
        response = native_response(
            "1h",
            "Traders should wait for confirmation before entering.",
            {"positionType": "long", "entryPrice": 100, "stopLoss": 90, "takeProfits": [110]},
        )
        raw = adapt_native_response(
            request=AdapterRequest("r1", "run1", 1, "OANDA", "XAUUSD", "H1", "NORMAL", "DECISION"),
            native_response=response,
            source_raw_artifact="memory://run1/1.json",
        )
        normalized = normalize_tc_raw(raw)
        self.assertEqual(normalized.entry_direction, "LONG")
        self.assertEqual(normalized.trade_state, "WAIT")


class OrchestratorTests(unittest.TestCase):
    def test_normal_run_uses_three_timeframes_and_finalizes_wait(self):
        responses = {
            "1D": [native_response("1D", "Daily environment remains neutral.", trend="neutral")],
            "4h": [native_response("4h", "A bearish reversal setup is forming.", trend="bearish")],
            "1h": [native_response("1h", "Traders should wait for confirmation before entering.")],
        }
        client = FakeClient(responses)
        sink = FakeSink()
        command = parse_spot_command("tc スポット GOLD# エントリー前")
        result = run_spot_entry_pre(
            command_request=command,
            resolved_symbol=resolve_symbol(command.user_symbol),
            client=client,
            raw_sink=sink,
            source_run_id="normal-1",
        )
        self.assertEqual(result.aggregate.common_status, "WAIT")
        self.assertEqual(result.aggregate.decision_timeframe, "H1")
        self.assertEqual([call[2] for call in client.calls], ["1D", "4h", "1h"])
        self.assertEqual(len(sink.saved), 3)

    def test_short_run_uses_h4_h1_m15_and_m15_decides(self):
        responses = {
            "4h": [native_response("4h", "A bearish reversal setup is forming.", trend="bearish")],
            "1h": [native_response("1h", "Consolidation setup is present.", trend="neutral")],
            "15m": [native_response(
                "15m",
                "A long position is recommended with entry at current price.",
                {"positionType": "long", "entryPrice": 100, "stopLoss": 95, "takeProfits": [105]},
                "bullish",
            )],
        }
        client = FakeClient(responses)
        sink = FakeSink()
        command = parse_spot_command("tc スポット GOLD# 短期 エントリー前")
        result = run_spot_entry_pre(
            command_request=command,
            resolved_symbol=resolve_symbol(command.user_symbol),
            client=client,
            raw_sink=sink,
            source_run_id="short-1",
        )
        self.assertEqual(result.aggregate.common_status, "TRADE")
        self.assertEqual(result.aggregate.direction, "LONG")
        self.assertEqual(result.aggregate.decision_timeframe, "M15")
        self.assertEqual([call[2] for call in client.calls], ["4h", "1h", "15m"])

    def test_normal_explicit_lower_tf_confirmation_requests_m15(self):
        responses = {
            "1D": [native_response("1D", "Daily environment remains bullish.", trend="bullish")],
            "4h": [native_response("4h", "A bullish reversal setup is present.", trend="bullish")],
            "1h": [native_response(
                "1h",
                "A long position is recommended with entry at current price, but lower-timeframe confirmation is required.",
                {"positionType": "long", "entryPrice": 100, "stopLoss": 95, "takeProfits": [105]},
                "bullish",
            )],
            "15m": [native_response(
                "15m",
                "A long position is recommended with entry at current price.",
                {"positionType": "long", "entryPrice": 101, "stopLoss": 96, "takeProfits": [106]},
                "bullish",
            )],
        }
        client = FakeClient(responses)
        sink = FakeSink()
        command = parse_spot_command("tc スポット GOLD# エントリー前")
        result = run_spot_entry_pre(
            command_request=command,
            resolved_symbol=resolve_symbol(command.user_symbol),
            client=client,
            raw_sink=sink,
            source_run_id="normal-drilldown-1",
        )
        self.assertEqual([call[2] for call in client.calls], ["1D", "4h", "1h", "15m"])
        self.assertEqual(result.aggregate.common_status, "TRADE")
        self.assertEqual(result.aggregate.confirmation_timeframe, "M15")
        self.assertFalse(result.aggregate.execution_permission)


if __name__ == "__main__":
    unittest.main()
