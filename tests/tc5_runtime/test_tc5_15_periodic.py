import json
import unittest
from datetime import datetime, timezone

from tc.runtime.command import parse_spot_command
from tc.runtime.orchestrator import run_spot_entry_pre
from tc.runtime.periodic import run_periodic_symbol
from tc.runtime.symbol import resolve_symbol
from tc.runtime.tf_cache import TimeframeCache


UTC = timezone.utc


def native_response(interval, observations, *, exchange="OANDA", symbol="XAUUSD", trend="neutral"):
    return {
        "status": "completed",
        "exchange": exchange,
        "symbol": symbol,
        "interval": interval,
        "analysis": json.dumps(
            {
                "futureAssumption": {"trend": trend},
                "observations": observations,
                "action_url": "https://www.tradingcursor.com/view?chartId=tc5-15-periodic",
            }
        ),
        "model": "test-model",
        "timestamp": "2026-09-15T03:03:00Z",
    }


class FakeSink:
    def __init__(self):
        self.saved = []

    def preserve(self, *, source_run_id, execution_order, native_response):
        self.saved.append((source_run_id, execution_order, dict(native_response)))
        return f"memory://{source_run_id}/{execution_order}.json"


class FakeClient:
    def __init__(self, responses):
        self.responses = {key: list(values) for key, values in responses.items()}
        self.calls = []

    def request_analysis(self, *, exchange, symbol, interval):
        self.calls.append((exchange, symbol, interval))
        value = self.responses[interval].pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class PeriodicSharedCacheTests(unittest.TestCase):
    def test_1103_uses_cached_d1_h4_and_live_h1_then_spot_reuses_same_evidence(self):
        cache = TimeframeCache()
        sink = FakeSink()
        at_0603 = datetime(2026, 9, 14, 21, 3, tzinfo=UTC)
        at_1103 = datetime(2026, 9, 15, 2, 3, tzinfo=UTC)

        first = FakeClient(
            {
                "1D": [native_response("1D", "Daily environment remains neutral.")],
                "4h": [native_response("4h", "A bearish reversal setup is forming.", trend="bearish")],
                "1h": [native_response("1h", "Traders should wait for confirmation before entering.")],
            }
        )
        r0603 = run_periodic_symbol(
            slot_id="06:03",
            user_symbol="GOLD",
            client=first,
            raw_sink=sink,
            cache=cache,
            now=at_0603,
            source_run_id="periodic-0603",
        )
        self.assertEqual([c[2] for c in first.calls], ["1D", "4h", "1h"])
        self.assertEqual(r0603.aggregate.common_status, "WAIT")

        second = FakeClient(
            {
                "1h": [native_response("1h", "Traders should wait for confirmation before entering.")],
            }
        )
        r1103 = run_periodic_symbol(
            slot_id="11:03",
            user_symbol="GOLD#",
            client=second,
            raw_sink=sink,
            cache=cache,
            now=at_1103,
            source_run_id="periodic-1103",
        )
        self.assertEqual([c[2] for c in second.calls], ["1h"])
        self.assertEqual(
            [(p.timeframe, p.source_mode) for p in r1103.timeframe_provenance],
            [("D1", "CACHE"), ("H4", "CACHE"), ("H1", "LIVE")],
        )
        self.assertEqual(r1103.aggregate.common_status, "WAIT")

        # Spot at the same time reuses the just-established D1/H4/H1 evidence
        # and reaches the same common aggregation with zero Native calls.
        spot_client = FakeClient({})
        command = parse_spot_command("tc スポット GOLD# エントリー前")
        spot = run_spot_entry_pre(
            command_request=command,
            resolved_symbol=resolve_symbol(command.user_symbol),
            client=spot_client,
            raw_sink=sink,
            source_run_id="spot-after-1103",
            cache=cache,
            now=at_1103,
        )
        self.assertEqual(spot_client.calls, [])
        self.assertEqual(spot.aggregate.common_status, r1103.aggregate.common_status)
        self.assertEqual(spot.aggregate.direction, r1103.aggregate.direction)

    def test_periodic_failure_sets_retry_and_next_slot_retries_once_then_clears(self):
        cache = TimeframeCache()
        sink = FakeSink()
        at_0603 = datetime(2026, 9, 15, 0, 3, tzinfo=UTC)
        at_1103 = datetime(2026, 9, 15, 3, 3, tzinfo=UTC)
        resolved = resolve_symbol("GOLD")

        failing = FakeClient(
            {
                "1D": [native_response("1D", "Daily environment remains neutral.")],
                "4h": [RuntimeError("provider failure")],
                "1h": [native_response("1h", "Traders should wait for confirmation before entering.")],
            }
        )
        result = run_periodic_symbol(
            slot_id="06:03",
            user_symbol="GOLD",
            client=failing,
            raw_sink=sink,
            cache=cache,
            now=at_0603,
            source_run_id="periodic-fail-0603",
        )
        self.assertEqual([c[2] for c in failing.calls], ["1D", "4h", "1h"])
        self.assertIsNone(result.aggregate)
        self.assertEqual([e.timeframe for e in result.errors], ["H4"])
        self.assertIsNotNone(
            cache.retry_pending(
                canonical_symbol=resolved.canonical_symbol,
                provider=resolved.provider,
                provider_symbol=resolved.provider_symbol,
                timeframe="H4",
            )
        )

        recovery = FakeClient(
            {
                "4h": [native_response("4h", "A bearish reversal setup is forming.", trend="bearish")],
                "1h": [native_response("1h", "Traders should wait for confirmation before entering.")],
            }
        )
        recovered = run_periodic_symbol(
            slot_id="11:03",
            user_symbol="GOLD",
            client=recovery,
            raw_sink=sink,
            cache=cache,
            now=at_1103,
            source_run_id="periodic-retry-1103",
        )
        self.assertEqual([c[2] for c in recovery.calls], ["4h", "1h"])
        self.assertEqual(recovered.aggregate.common_status, "WAIT")
        self.assertIsNone(
            cache.retry_pending(
                canonical_symbol=resolved.canonical_symbol,
                provider=resolved.provider,
                provider_symbol=resolved.provider_symbol,
                timeframe="H4",
            )
        )


if __name__ == "__main__":
    unittest.main()
