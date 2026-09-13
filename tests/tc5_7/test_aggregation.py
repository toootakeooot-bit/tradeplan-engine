import unittest

from tc.runtime.aggregate import (
    AggregateError,
    TimeframeResult,
    aggregate_4tf,
)


class TC57AggregationTests(unittest.TestCase):
    def test_all_aligned_does_not_create_combined_trade_state(self):
        results = {
            tf: TimeframeResult(tf, "LONG", "ACTIONABLE", f"r-{tf}")
            for tf in ("D1", "H4", "H1", "M15")
        }
        agg = aggregate_4tf(
            batch_id="b1",
            canonical_symbol="GOLD",
            provider="OANDA",
            results=results,
        )
        self.assertEqual(agg.completeness, "COMPLETE")
        self.assertEqual(agg.direction_alignment, "ALIGNED")
        self.assertEqual(agg.state_alignment, "ALIGNED")
        self.assertEqual(agg.combined_trade_state, "NOT_DEFINED")
        self.assertFalse(agg.execution_permission)

    def test_state_divergence_is_descriptive_only(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "WAIT"),
            "H1": TimeframeResult("H1", "LONG", "ACTIONABLE"),
            "M15": TimeframeResult("M15", "LONG", "ACTIONABLE"),
        }
        agg = aggregate_4tf(
            batch_id="b2",
            canonical_symbol="GOLD",
            provider="OANDA",
            results=results,
        )
        self.assertEqual(agg.direction_alignment, "ALIGNED")
        self.assertEqual(agg.state_alignment, "DIVERGENT")
        self.assertEqual(agg.combined_trade_state, "NOT_DEFINED")

    def test_missing_m15_is_runtime_batch_failure_not_trade_state(self):
        results = {
            tf: TimeframeResult(tf, "LONG", "ACTIONABLE")
            for tf in ("D1", "H4", "H1")
        }
        with self.assertRaises(AggregateError) as ctx:
            aggregate_4tf(
                batch_id="b3",
                canonical_symbol="GOLD",
                provider="OANDA",
                results=results,
            )
        self.assertEqual(ctx.exception.code, "BATCH_INCOMPLETE")

    def test_missing_direction_is_insufficient_not_inferred(self):
        results = {
            "D1": TimeframeResult("D1", "LONG", "ACTIONABLE"),
            "H4": TimeframeResult("H4", "LONG", "ACTIONABLE"),
            "H1": TimeframeResult("H1", None, "UNDETERMINED"),
            "M15": TimeframeResult("M15", "LONG", "ACTIONABLE"),
        }
        agg = aggregate_4tf(
            batch_id="b4",
            canonical_symbol="GOLD",
            provider="OANDA",
            results=results,
        )
        self.assertEqual(agg.direction_alignment, "INSUFFICIENT")
        self.assertEqual(agg.combined_trade_state, "NOT_DEFINED")


if __name__ == "__main__":
    unittest.main()
