import unittest

from tc.runtime.aggregate import TimeframeResult, aggregate_role_profile


class TC57AggregationTests(unittest.TestCase):
    def test_normal_uses_h1_as_decision_without_m15_by_default(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult("H1", "LONG", "ACTIONABLE"),
        }
        agg = aggregate_role_profile(
            batch_id="b1",
            canonical_symbol="GOLD",
            provider="OANDA",
            profile="NORMAL",
            results=results,
        )
        self.assertEqual(agg.runtime_status, "FINALIZED")
        self.assertEqual(agg.common_status, "TRADE")
        self.assertEqual(agg.decision_timeframe, "H1")
        self.assertIsNone(agg.confirmation_timeframe)
        self.assertEqual(agg.used_timeframes, ("D1", "H4", "H1"))
        self.assertFalse(agg.execution_permission)

    def test_normal_explicit_lower_tf_requirement_requests_m15(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult(
                "H1", "LONG", "WAIT", lower_tf_confirmation_required=True
            ),
        }
        agg = aggregate_role_profile(
            batch_id="b2",
            canonical_symbol="GOLD",
            provider="OANDA",
            profile="NORMAL",
            results=results,
        )
        self.assertEqual(agg.runtime_status, "NEEDS_DRILLDOWN")
        self.assertIsNone(agg.common_status)
        self.assertEqual(agg.confirmation_timeframe, "M15")

    def test_normal_m15_same_direction_actionable_releases_trade_gate(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult(
                "H1", "LONG", "WAIT", lower_tf_confirmation_required=True
            ),
            "M15": TimeframeResult("M15", "LONG", "ACTIONABLE"),
        }
        agg = aggregate_role_profile(
            batch_id="b3",
            canonical_symbol="GOLD",
            provider="OANDA",
            profile="NORMAL",
            results=results,
        )
        self.assertEqual(agg.runtime_status, "FINALIZED")
        self.assertEqual(agg.common_status, "TRADE")
        self.assertEqual(agg.direction, "LONG")

    def test_normal_opposite_m15_holds_without_fabricated_trade_state(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult(
                "H1", "LONG", "WAIT", lower_tf_confirmation_required=True
            ),
            "M15": TimeframeResult("M15", "SHORT", "ACTIONABLE"),
        }
        agg = aggregate_role_profile(
            batch_id="b4",
            canonical_symbol="GOLD",
            provider="OANDA",
            profile="NORMAL",
            results=results,
        )
        self.assertEqual(agg.runtime_status, "HOLD")
        self.assertIsNone(agg.common_status)

    def test_short_uses_m15_as_decision(self):
        results = {
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult("H1", "LONG", "ACTIONABLE"),
            "M15": TimeframeResult("M15", "LONG", "WAIT"),
        }
        agg = aggregate_role_profile(
            batch_id="b5",
            canonical_symbol="GOLD",
            provider="OANDA",
            profile="SHORT",
            results=results,
        )
        self.assertEqual(agg.common_status, "WAIT")
        self.assertEqual(agg.decision_timeframe, "M15")


if __name__ == "__main__":
    unittest.main()
