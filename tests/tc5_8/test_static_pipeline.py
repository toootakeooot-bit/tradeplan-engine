import unittest

from tc.runtime.aggregate import TimeframeResult, aggregate_role_profile
from tc.runtime.command import parse_spot_command
from tc.runtime.planner import build_drilldown_plan, build_entry_pre_plan
from tc.runtime.symbol import SymbolResolutionError, resolve_symbol


class TC58StaticPipelineTests(unittest.TestCase):
    def test_gold_hash_default_command_builds_normal_three_tf_plan(self):
        command = parse_spot_command("tc スポット GOLD# エントリー前")
        symbol = resolve_symbol(command.user_symbol)
        plan = build_entry_pre_plan(command, symbol)

        self.assertEqual(command.profile, "NORMAL")
        self.assertEqual(symbol.normalized_symbol, "GOLD")
        self.assertEqual(symbol.canonical_symbol, "GOLD")
        self.assertEqual(symbol.provider_symbol, "XAUUSD")
        self.assertEqual(
            [(p.timeframe, p.role, p.interval) for p in plan],
            [
                ("D1", "ENVIRONMENT", "1D"),
                ("H4", "SETUP", "4h"),
                ("H1", "DECISION", "1h"),
            ],
        )

    def test_normal_drilldown_plan_is_m15_confirmation(self):
        command = parse_spot_command("tc スポット GOLD# エントリー前")
        symbol = resolve_symbol(command.user_symbol)
        plan = build_drilldown_plan(command, symbol)
        self.assertEqual((plan.timeframe, plan.role, plan.interval), ("M15", "CONFIRMATION", "15m"))

    def test_short_command_builds_h4_h1_m15_plan(self):
        command = parse_spot_command("tc スポット GOLD# 短期 エントリー前")
        symbol = resolve_symbol(command.user_symbol)
        plan = build_entry_pre_plan(command, symbol)
        self.assertEqual(command.profile, "SHORT")
        self.assertEqual(
            [(p.timeframe, p.role, p.interval) for p in plan],
            [
                ("H4", "ENVIRONMENT", "4h"),
                ("H1", "SETUP", "1h"),
                ("M15", "DECISION", "15m"),
            ],
        )

    def test_xau_slash_and_gold_hash_resolve_same_canonical(self):
        a = resolve_symbol("GOLD#")
        b = resolve_symbol("XAU/USD")
        self.assertEqual(a.canonical_symbol, b.canonical_symbol)
        self.assertEqual(a.provider_symbol, b.provider_symbol)

    def test_usdjpy_hash_uses_same_profile_logic(self):
        command = parse_spot_command("tc スポット USDJPY# 短期 エントリー前")
        symbol = resolve_symbol(command.user_symbol)
        plan = build_entry_pre_plan(command, symbol)
        self.assertEqual(symbol.canonical_symbol, "USDJPY")
        self.assertEqual(symbol.provider_symbol, "USDJPY")
        self.assertEqual(plan[-1].interval, "15m")

    def test_unknown_symbol_stops_before_native_plan(self):
        command = parse_spot_command("tc スポット UNKNOWN# エントリー前")
        with self.assertRaises(SymbolResolutionError) as ctx:
            resolve_symbol(command.user_symbol)
        self.assertEqual(ctx.exception.code, "SYMBOL_UNRESOLVED")

    def test_normal_role_aggregation_can_finalize_trade_without_m15(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult("H1", "LONG", "ACTIONABLE"),
        }
        aggregate = aggregate_role_profile(
            batch_id="TC5-8-STATIC-01",
            canonical_symbol="GOLD",
            provider="OANDA",
            profile="NORMAL",
            results=results,
        )
        self.assertEqual(aggregate.common_status, "TRADE")
        self.assertEqual(aggregate.decision_timeframe, "H1")
        self.assertFalse(aggregate.execution_permission)


if __name__ == "__main__":
    unittest.main()
