import json
import tempfile
import unittest
from pathlib import Path

from tc.runtime.host_binding import CallableNativeClient
from tc.runtime.raw_sink import FileRawSink
from tc.runtime.service import run_spot_command


def response(interval, observations, *, position=None, trend="neutral"):
    analysis = {
        "futureAssumption": {"trend": trend},
        "observations": observations,
        "action_url": "https://www.tradingcursor.com/view?chartId=service-test",
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
    }


class ServiceEntrypointTests(unittest.TestCase):
    def test_one_line_normal_command_runs_end_to_end_with_injected_host(self):
        responses = {
            "1D": response("1D", "Daily environment remains neutral."),
            "4h": response("4h", "A bearish reversal setup is forming.", trend="bearish"),
            "1h": response("1h", "Traders should wait for confirmation before entering."),
        }
        calls = []

        def host_call(*, exchange, symbol, interval):
            calls.append((exchange, symbol, interval))
            return responses[interval]

        with tempfile.TemporaryDirectory() as tmp:
            result = run_spot_command(
                "tc スポット GOLD# エントリー前",
                client=CallableNativeClient(host_call),
                raw_sink=FileRawSink(tmp),
                timestamp="2026-09-13T00:00:00Z",
                source_run_id="service-normal-1",
                used_today_before_run=10,
                usage_as_of="2026-09-14T10:34:00Z",
            )

            self.assertEqual(
                calls,
                [
                    ("OANDA", "XAUUSD", "1D"),
                    ("OANDA", "XAUUSD", "4h"),
                    ("OANDA", "XAUUSD", "1h"),
                ],
            )
            self.assertEqual(result.tradeplan_state["status"], "WAIT")
            self.assertEqual(result.tradeplan_state["symbol"], "GOLD")
            self.assertEqual(result.tradeplan_state["source_engine"], "TC")
            self.assertFalse(result.tradeplan_state["execution_permission"])
            self.assertEqual(result.runtime_usage.current_run_calls, 3)
            self.assertEqual(result.runtime_usage.used_today, 13)
            self.assertEqual(result.runtime_usage.remaining_after_reserve, 17)
            self.assertEqual(result.runtime_usage.spot_equivalent, 5)
            self.assertEqual(result.runtime_usage.next_reset_utc, "2026-09-15T00:00:00Z")
            self.assertEqual(len(list(Path(tmp).rglob("*_native.json"))), 3)


if __name__ == "__main__":
    unittest.main()
