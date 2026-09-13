import unittest

from tc.runtime.aggregate import TimeframeResult, aggregate_4tf
from tc.runtime.command import parse_spot_command
from tc.runtime.planner import build_4tf_plan
from tc.runtime.symbol import SymbolResolutionError, resolve_symbol


class TC58StaticPipelineTests(unittest.TestCase):
    def test_gold_hash_command_to_exact_oanda_4tf_plan(self):
        command = parse_spot_command("tc スポット GOLD# エントリー前")
        symbol = resolve_symbol(command.user_symbol)
        plan = build_4tf_plan(command, symbol)

        self.assertEqual(symbol.normalized_symbol, "GOLD")
        self.assertEqual(symbol.canonical_symbol, "GOLD")
        self.assertEqual(symbol.provider_symbol, "XAUUSD")
        self.assertEqual(
            [(p.timeframe, p.exchange, p.symbol, p.interval) for p in plan],
            [
                ("D1", "OANDA", "XAUUSD", "1D"),
                ("H4", "OANDA", "XAUUSD", "4h"),
                ("H1", "OANDA", "XAUUSD", "1h"),
                ("M15", "OANDA", "XAUUSD", "15m"),
            ],
        )

    def test_xau_slash_and_gold_hash_resolve_same_canonical(self):
        a = resolve_symbol("GOLD#")
        b = resolve_symbol("XAU/USD")
        self.assertEqual(a.canonical_symbol, b.canonical_symbol)
        self.assertEqual(a.provider_symbol, b.provider_symbol)

    def test_usdjpy_hash(self):
        command = parse_spot_command("tc スポット USDJPY# エントリー前")
        symbol = resolve_symbol(command.user_symbol)
        plan = build_4tf_plan(command, symbol)
        self.assertEqual(symbol.canonical_symbol, "USDJPY")
        self.assertEqual(symbol.provider_symbol, "USDJPY")
        self.assertEqual(plan[-1].interval, "15m")

    def test_unknown_symbol_stops_before_native_plan(self):
        command = parse_spot_command("tc スポット UNKNOWN# エントリー前")
        with self.assertRaises(SymbolResolutionError) as ctx:
            resolve_symbol(command.user_symbol)
        self.assertEqual(ctx.exception.code, "SYMBOL_UNRESOLVED")

    def test_complete_batch_can_aggregate_without_trade_synthesis(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult("H1", "LONG", "WAIT"),
            "M15": TimeframeResult("M15", "LONG", "ACTIONABLE"),
        }
        aggregate = aggregate_4tf(
            batch_id="TC5-8-STATIC-01",
            canonical_symbol="GOLD",
            provider="OANDA",
            results=results,
        )
        self.assertEqual(aggregate.direction_alignment, "ALIGNED")
        self.assertEqual(aggregate.state_alignment, "DIVERGENT")
        self.assertEqual(aggregate.combined_trade_state, "NOT_DEFINED")
        self.assertFalse(aggregate.execution_permission)


if __name__ == "__main__":
    unittest.main()
