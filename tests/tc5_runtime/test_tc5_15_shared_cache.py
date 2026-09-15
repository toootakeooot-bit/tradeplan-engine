import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tc.normalizer.normalizer import NormalizedTCState
from tc.runtime.acquisition import (
    BASE_PERIODIC_CALLS_PER_DAY,
    MarketInputResolver,
    PERIODIC_SLOTS,
    SCHEDULED_SYMBOLS,
)
from tc.runtime.command import parse_spot_command
from tc.runtime.orchestrator import run_spot_entry_pre
from tc.runtime.symbol import resolve_symbol
from tc.runtime.tf_cache import TimeframeCache


UTC = timezone.utc


def normalized(timeframe, *, state="WAIT", direction=None, lower=False, record_id=None):
    return NormalizedTCState(
        record_id=record_id or f"cached-{timeframe}",
        timeframe=timeframe,
        environment_direction="neutral",
        setup_evidence=None,
        trigger_evidence=None,
        entry_direction=direction,
        entry_price=100.0 if direction else None,
        stop_loss=95.0 if direction else None,
        take_profits=(105.0,) if direction else (),
        trade_state=state,
        state_basis="TEST",
        wait_evidence="wait for confirmation" if state == "WAIT" else None,
        invalidation_evidence=None,
        alternative_scenario_evidence=None,
        lower_tf_confirmation_required=lower,
    )


def raw(timeframe, *, run_id="seed", order=1, timestamp="2026-09-15T00:03:00Z"):
    return {
        "record_identity": {
            "record_id": f"{run_id}:{order}",
            "source_run_id": run_id,
            "execution_order": order,
            "source_raw_artifact": f"memory://{run_id}/{order}.json",
        },
        "wrapper_metadata": {"timeframe": timeframe, "profile": "NORMAL"},
        "original_response": {"timestamp": timestamp},
    }


def native_response(interval, observations, position=None, trend="neutral", exchange="OANDA", symbol="XAUUSD"):
    analysis = {
        "futureAssumption": {"trend": trend},
        "observations": observations,
        "action_url": "https://www.tradingcursor.com/view?chartId=tc5-15-test",
    }
    if position is not None:
        analysis["potentialPosition"] = position
    return {
        "status": "completed",
        "exchange": exchange,
        "symbol": symbol,
        "interval": interval,
        "analysis": json.dumps(analysis),
        "model": "test-model",
        "timestamp": "2026-09-15T06:00:00Z",
    }


class FakeSink:
    def __init__(self):
        self.saved = []

    def preserve(self, *, source_run_id, execution_order, native_response):
        self.saved.append((source_run_id, execution_order, dict(native_response)))
        return f"memory://{source_run_id}/{execution_order}.json"


class FakeClient:
    def __init__(self, responses=None):
        self.responses = {k: list(v) for k, v in (responses or {}).items()}
        self.calls = []

    def request_analysis(self, *, exchange, symbol, interval):
        self.calls.append((exchange, symbol, interval))
        return self.responses[interval].pop(0)


def put_cache(cache, resolved, timeframe, at, state="WAIT", direction=None, lower=False, order=1):
    cache.put(
        canonical_symbol=resolved.canonical_symbol,
        provider=resolved.provider,
        provider_symbol=resolved.provider_symbol,
        profile="NORMAL",
        timeframe=timeframe,
        raw=raw(timeframe, order=order),
        normalized=normalized(timeframe, state=state, direction=direction, lower=lower),
        now=at,
    )


class ScheduleTests(unittest.TestCase):
    def test_fixed_schedule_is_27_base_calls_for_three_symbols(self):
        self.assertEqual(SCHEDULED_SYMBOLS, ("GOLD", "USDJPY", "US100"))
        self.assertEqual(
            [(s.slot_id, s.live_timeframes) for s in PERIODIC_SLOTS],
            [
                ("05:03", ("H1",)),
                ("09:03", ("D1", "H4", "H1")),
                ("12:03", ("H1",)),
                ("17:03", ("H4", "H1")),
                ("21:03", ("H4", "H1")),
            ],
        )
        self.assertEqual(BASE_PERIODIC_CALLS_PER_DAY, 27)


class CachePersistenceTests(unittest.TestCase):
    def test_persistent_cache_keeps_original_fetched_at_and_raw_provenance(self):
        resolved = resolve_symbol("GOLD#")
        at = datetime(2026, 9, 15, 0, 3, tzinfo=UTC)
        later = at + timedelta(hours=3)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tc-cache.json"
            cache = TimeframeCache(path)
            put_cache(cache, resolved, "D1", at)
            first = cache.get_latest(
                canonical_symbol=resolved.canonical_symbol,
                provider=resolved.provider,
                provider_symbol=resolved.provider_symbol,
                timeframe="D1",
                now=later,
            )
            self.assertEqual(first.item.fetched_at, at.isoformat())
            self.assertEqual(first.cache_age_seconds, 3 * 3600)
            self.assertTrue(first.item.raw_artifact_ref.startswith("memory://"))

            reloaded = TimeframeCache(path)
            second = reloaded.get_latest(
                canonical_symbol=resolved.canonical_symbol,
                provider=resolved.provider,
                provider_symbol=resolved.provider_symbol,
                timeframe="D1",
                now=later,
            )
            self.assertEqual(second.item.fetched_at, first.item.fetched_at)
            self.assertEqual(second.item.record_id, first.item.record_id)
            self.assertEqual(second.item.normalized.timeframe, "D1")


class ResolverTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 15, 6, 0, tzinfo=UTC)
        self.resolved = resolve_symbol("USDJPY#")
        self.cache = TimeframeCache()

    def test_1203_reuses_d1_h4_and_fetches_h1(self):
        put_cache(self.cache, self.resolved, "D1", self.now - timedelta(hours=3))
        put_cache(self.cache, self.resolved, "H4", self.now - timedelta(hours=3))
        decisions = MarketInputResolver(self.cache).resolve_periodic(
            slot_id="12:03",
            resolved_symbol=self.resolved,
            now=self.now,
        )
        self.assertEqual(
            [(d.timeframe, d.source_mode) for d in decisions],
            [("D1", "CACHE"), ("H4", "CACHE"), ("H1", "LIVE")],
        )

    def test_retry_pending_is_attempted_at_next_slot(self):
        put_cache(self.cache, self.resolved, "H4", self.now - timedelta(hours=3))
        self.cache.mark_failure(
            canonical_symbol=self.resolved.canonical_symbol,
            provider=self.resolved.provider,
            provider_symbol=self.resolved.provider_symbol,
            timeframe="H4",
            failure_code="NATIVE_CALL_FAILED",
            now=self.now - timedelta(minutes=1),
        )
        decisions = MarketInputResolver(self.cache).resolve_periodic(
            slot_id="12:03",
            resolved_symbol=self.resolved,
            now=self.now,
        )
        h4 = next(d for d in decisions if d.timeframe == "H4")
        self.assertEqual(h4.source_mode, "LIVE")
        self.assertEqual(h4.reason, "RETRY_PENDING_NEXT_SLOT")

    def test_0503_h4_refresh_only_when_h1_actionable_and_h4_old(self):
        put_cache(self.cache, self.resolved, "H4", self.now - timedelta(hours=8))
        resolver = MarketInputResolver(self.cache)
        self.assertTrue(
            resolver.needs_0503_h4_refresh(
                resolved_symbol=self.resolved,
                h1=normalized("H1", state="ACTIONABLE", direction="LONG"),
                now=self.now,
            )
        )
        self.assertFalse(
            resolver.needs_0503_h4_refresh(
                resolved_symbol=self.resolved,
                h1=normalized("H1", state="WAIT"),
                now=self.now,
            )
        )


class SpotCacheFirstTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 15, 6, 0, tzinfo=UTC)
        self.command = parse_spot_command("tc スポット GOLD# エントリー前")
        self.resolved = resolve_symbol(self.command.user_symbol)

    def test_spot_all_cache_consumes_zero_native_calls(self):
        cache = TimeframeCache()
        put_cache(cache, self.resolved, "D1", self.now - timedelta(hours=6))
        put_cache(cache, self.resolved, "H4", self.now - timedelta(hours=2))
        put_cache(cache, self.resolved, "H1", self.now - timedelta(minutes=30))
        client = FakeClient()
        result = run_spot_entry_pre(
            command_request=self.command,
            resolved_symbol=self.resolved,
            client=client,
            raw_sink=FakeSink(),
            source_run_id="spot-all-cache",
            cache=cache,
            now=self.now,
        )
        self.assertEqual(client.calls, [])
        self.assertEqual(result.aggregate.common_status, "WAIT")
        self.assertEqual([p.source_mode for p in result.timeframe_provenance], ["CACHE", "CACHE", "CACHE"])

    def test_spot_refreshes_only_expired_h1(self):
        cache = TimeframeCache()
        put_cache(cache, self.resolved, "D1", self.now - timedelta(hours=6))
        put_cache(cache, self.resolved, "H4", self.now - timedelta(hours=2))
        put_cache(cache, self.resolved, "H1", self.now - timedelta(minutes=91))
        responses = {
            "1h": [native_response("1h", "Traders should wait for confirmation before entering.")],
        }
        client = FakeClient(responses)
        result = run_spot_entry_pre(
            command_request=self.command,
            resolved_symbol=self.resolved,
            client=client,
            raw_sink=FakeSink(),
            source_run_id="spot-h1-refresh",
            cache=cache,
            now=self.now,
        )
        self.assertEqual([call[2] for call in client.calls], ["1h"])
        modes = {p.timeframe: p.source_mode for p in result.timeframe_provenance}
        self.assertEqual(modes, {"D1": "CACHE", "H4": "CACHE", "H1": "LIVE"})

    def test_spot_missing_h4_fetches_only_h4_when_h1_is_fresh(self):
        cache = TimeframeCache()
        put_cache(cache, self.resolved, "D1", self.now - timedelta(hours=6))
        put_cache(cache, self.resolved, "H1", self.now - timedelta(minutes=30))
        responses = {
            "4h": [native_response("4h", "A bullish reversal setup is present.", trend="bullish")],
        }
        client = FakeClient(responses)
        run_spot_entry_pre(
            command_request=self.command,
            resolved_symbol=self.resolved,
            client=client,
            raw_sink=FakeSink(),
            source_run_id="spot-h4-missing",
            cache=cache,
            now=self.now,
        )
        self.assertEqual([call[2] for call in client.calls], ["4h"])

    def test_spot_confirmation_fetches_m15_live_only_after_cached_h1_requests_it(self):
        cache = TimeframeCache()
        put_cache(cache, self.resolved, "D1", self.now - timedelta(hours=6), state="UNDETERMINED")
        put_cache(cache, self.resolved, "H4", self.now - timedelta(hours=2), state="UNDETERMINED")
        put_cache(
            cache,
            self.resolved,
            "H1",
            self.now - timedelta(minutes=30),
            state="ACTIONABLE",
            direction="LONG",
            lower=True,
        )
        responses = {
            "15m": [native_response(
                "15m",
                "A long position is recommended with entry at current price.",
                {"positionType": "long", "entryPrice": 101, "stopLoss": 96, "takeProfits": [106]},
                "bullish",
            )],
        }
        client = FakeClient(responses)
        result = run_spot_entry_pre(
            command_request=self.command,
            resolved_symbol=self.resolved,
            client=client,
            raw_sink=FakeSink(),
            source_run_id="spot-m15",
            cache=cache,
            now=self.now,
        )
        self.assertEqual([call[2] for call in client.calls], ["15m"])
        self.assertEqual(result.aggregate.common_status, "TRADE")
        self.assertEqual(result.timeframe_provenance[-1].timeframe, "M15")
        self.assertEqual(result.timeframe_provenance[-1].source_mode, "LIVE")

    def test_spot_success_clears_retry_pending(self):
        cache = TimeframeCache()
        put_cache(cache, self.resolved, "D1", self.now - timedelta(hours=6))
        put_cache(cache, self.resolved, "H4", self.now - timedelta(hours=2))
        put_cache(cache, self.resolved, "H1", self.now - timedelta(minutes=30))
        cache.mark_failure(
            canonical_symbol=self.resolved.canonical_symbol,
            provider=self.resolved.provider,
            provider_symbol=self.resolved.provider_symbol,
            timeframe="H4",
            failure_code="NATIVE_CALL_FAILED",
            now=self.now - timedelta(minutes=5),
        )
        responses = {
            "4h": [native_response("4h", "A bullish reversal setup is present.", trend="bullish")],
        }
        run_spot_entry_pre(
            command_request=self.command,
            resolved_symbol=self.resolved,
            client=FakeClient(responses),
            raw_sink=FakeSink(),
            source_run_id="spot-clear-retry",
            cache=cache,
            now=self.now,
        )
        self.assertIsNone(
            cache.retry_pending(
                canonical_symbol=self.resolved.canonical_symbol,
                provider=self.resolved.provider,
                provider_symbol=self.resolved.provider_symbol,
                timeframe="H4",
            )
        )


if __name__ == "__main__":
    unittest.main()
