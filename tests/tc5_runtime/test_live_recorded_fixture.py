import json
import tempfile
import unittest
from pathlib import Path

from tc.runtime.host_binding import CallableNativeClient
from tc.runtime.raw_sink import FileRawSink
from tc.runtime.service import run_spot_command


NORMAL_FIXTURE = Path("fixtures/tc5_live/TC5-LIVE-NORMAL-GOLD-20260913-0544Z.json")
SHORT_FIXTURE = Path("fixtures/tc5_live/TC5-LIVE-SHORT-GOLD-20260913-0554Z.json")


class LiveRecordedFixtureTests(unittest.TestCase):
    def test_recorded_live_normal_gold_runs_raw_to_tradeplanstate(self):
        payload = json.loads(NORMAL_FIXTURE.read_text(encoding="utf-8"))
        responses = payload["responses"]
        calls = []

        def host_call(*, exchange, symbol, interval):
            calls.append((exchange, symbol, interval))
            return responses[interval]

        with tempfile.TemporaryDirectory() as tmp:
            result = run_spot_command(
                payload["command"],
                client=CallableNativeClient(host_call),
                raw_sink=FileRawSink(tmp),
                timestamp=responses["1h"]["timestamp"],
                source_run_id=payload["run_id"],
            )

            self.assertEqual(
                calls,
                [
                    ("OANDA", "XAUUSD", "1D"),
                    ("OANDA", "XAUUSD", "4h"),
                    ("OANDA", "XAUUSD", "1h"),
                ],
            )
            self.assertEqual(result.run_result.aggregate.runtime_status, "HOLD")
            self.assertIsNone(result.run_result.aggregate.common_status)
            self.assertEqual(result.run_result.aggregate.direction, "LONG")
            self.assertIsNone(result.tradeplan_state["status"])
            self.assertEqual(result.tradeplan_state["direction"], "LONG")
            self.assertEqual(result.tradeplan_state["evidence"]["decision_trade_state"], "UNDETERMINED")
            self.assertFalse(result.tradeplan_state["execution_permission"])
            self.assertEqual(len(list(Path(tmp).rglob("*_native.json"))), 3)

    def test_recorded_live_short_gold_runs_raw_to_tradeplanstate(self):
        payload = json.loads(SHORT_FIXTURE.read_text(encoding="utf-8"))
        responses = payload["responses"]
        calls = []

        def host_call(*, exchange, symbol, interval):
            calls.append((exchange, symbol, interval))
            return responses[interval]

        with tempfile.TemporaryDirectory() as tmp:
            result = run_spot_command(
                payload["command"],
                client=CallableNativeClient(host_call),
                raw_sink=FileRawSink(tmp),
                timestamp=responses["15m"]["timestamp"],
                source_run_id=payload["run_id"],
            )

            self.assertEqual(
                calls,
                [
                    ("OANDA", "XAUUSD", "4h"),
                    ("OANDA", "XAUUSD", "1h"),
                    ("OANDA", "XAUUSD", "15m"),
                ],
            )
            self.assertEqual(result.run_result.aggregate.runtime_status, "FINALIZED")
            self.assertEqual(result.run_result.aggregate.common_status, "TRADE")
            self.assertEqual(result.run_result.aggregate.direction, "LONG")
            self.assertEqual(result.tradeplan_state["status"], "TRADE")
            self.assertEqual(result.tradeplan_state["direction"], "LONG")
            self.assertEqual(result.tradeplan_state["evidence"]["decision_trade_state"], "ACTIONABLE")
            self.assertFalse(result.tradeplan_state["execution_permission"])
            self.assertEqual(len(list(Path(tmp).rglob("*_native.json"))), 3)


if __name__ == "__main__":
    unittest.main()
