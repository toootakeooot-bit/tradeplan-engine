import unittest

from tc.normalizer.normalizer import NormalizedTCState
from tc.runtime.response import build_timeframe_decision_rows, format_timeframe_decision_table


def record(
    timeframe,
    *,
    direction="LONG",
    state="ACTIONABLE",
    entry=100.0,
    sl=99.0,
    tp=(101.0, 102.0, 103.0),
):
    return NormalizedTCState(
        record_id=f"rec-{timeframe}",
        timeframe=timeframe,
        environment_direction="bullish",
        setup_evidence="setup",
        trigger_evidence=None,
        entry_direction=direction,
        entry_price=entry,
        stop_loss=sl,
        take_profits=tuple(tp),
        trade_state=state,
        state_basis="EXPLICIT_NATIVE_TEXT" if state != "UNDETERMINED" else "NOT_ENOUGH_EVIDENCE",
        wait_evidence="wait" if state == "WAIT" else None,
        invalidation_evidence=None,
        alternative_scenario_evidence=None,
        lower_tf_confirmation_required=False,
    )


class TC517ReportTests(unittest.TestCase):
    def test_fixed_order_and_missing_m15(self):
        rows = build_timeframe_decision_rows(
            [
                record("H1", direction="LONG", state="WAIT", entry=155.662),
                record("D1", direction="SHORT", state="ACTIONABLE", entry=155.650),
                record("H4", direction="LONG", state="ACTIONABLE", entry=155.655),
            ]
        )
        self.assertEqual([row["timeframe"] for row in rows], ["D1", "H4", "H1"])
        self.assertEqual(rows[0]["decision"], "🔴 SHORT")
        self.assertEqual(rows[1]["decision"], "🟢 LONG")
        self.assertEqual(rows[2]["decision"], "🟡 LONG待ち")
        self.assertNotIn("confidence", rows[0])

        table = format_timeframe_decision_table(rows)
        self.assertIn("| TF | 判定 | Entry | SL | TP1 | TP2 | TP3 |", table)
        self.assertNotIn("| M15 |", table)
        self.assertNotIn("確度", table)

    def test_m15_is_shown_only_when_acquired_and_undetermined_is_visible(self):
        rows = build_timeframe_decision_rows(
            [
                record("D1"),
                record("H4"),
                record("H1"),
                record("M15", direction="LONG", state="WAIT", entry=155.700),
            ]
        )
        self.assertEqual(rows[-1]["timeframe"], "M15")
        self.assertEqual(rows[-1]["decision"], "🟡 LONG待ち")

        undetermined = build_timeframe_decision_rows(
            [
                record("D1"),
                record("H4"),
                record("H1"),
                record("M15", direction="LONG", state="UNDETERMINED", entry=155.700),
            ]
        )
        self.assertEqual(undetermined[-1]["timeframe"], "M15")
        self.assertEqual(undetermined[-1]["decision"], "⚪ LONG判定保留")
        self.assertEqual(undetermined[-1]["entry"], 155.700)

    def test_directionless_undetermined_is_shown_as_hold(self):
        rows = build_timeframe_decision_rows(
            [record("H1", direction=None, state="UNDETERMINED", entry=None, sl=None, tp=())]
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["decision"], "⚪ 判定保留")
        table = format_timeframe_decision_table(rows)
        self.assertIn("| H1 | ⚪ 判定保留 | — | — | — | — | — |", table)

    def test_tp_is_capped_at_three_for_display_without_synthesizing_values(self):
        rows = build_timeframe_decision_rows(
            [record("H4", tp=(101.0, 102.0, 103.0, 104.0))]
        )
        self.assertEqual(rows[0]["tp1"], 101.0)
        self.assertEqual(rows[0]["tp2"], 102.0)
        self.assertEqual(rows[0]["tp3"], 103.0)

        sparse = build_timeframe_decision_rows([record("H4", tp=(101.0,))])
        self.assertIsNone(sparse[0]["tp2"])
        self.assertIsNone(sparse[0]["tp3"])


if __name__ == "__main__":
    unittest.main()
