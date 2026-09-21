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
    environment="bullish",
):
    return NormalizedTCState(
        record_id=f"rec-{timeframe}",
        timeframe=timeframe,
        environment_direction=environment,
        setup_evidence="setup",
        trigger_evidence=None,
        entry_direction=direction,
        entry_price=entry,
        stop_loss=sl,
        take_profits=tuple(tp),
        trade_state=state,
        state_basis="EXPLICIT_NATIVE_TEXT",
        wait_evidence="wait" if state == "WAIT" else None,
        invalidation_evidence=None,
        alternative_scenario_evidence=None,
        lower_tf_confirmation_required=False,
    )


class TC518ReportTests(unittest.TestCase):
    def test_fixed_six_column_table_uses_direction_and_entry_decision(self):
        rows = build_timeframe_decision_rows(
            [
                record("H1", direction=None, state="WAIT", entry=155.662, environment="neutral"),
                record("D1", direction="SHORT", state="ACTIONABLE", entry=155.650, environment="bearish"),
                record("H4", direction="LONG", state="ACTIONABLE", entry=155.655),
            ]
        )
        self.assertEqual([row["timeframe"] for row in rows], ["D1", "H4", "H1"])
        self.assertEqual(rows[0]["tc_direction"], "SHORT")
        self.assertEqual(rows[0]["entry_decision"], "SHORT")
        self.assertEqual(rows[1]["tc_direction"], "LONG")
        self.assertEqual(rows[1]["entry_decision"], "LONG")
        self.assertEqual(rows[2]["tc_direction"], "NEUTRAL")
        self.assertEqual(rows[2]["entry_decision"], "待機")

        table = format_timeframe_decision_table(rows)
        self.assertIn("| TF | TC方向 | ENTRY判定 | Entry | SL | TP |", table)
        self.assertIn("| H1 | NEUTRAL | 待機 |", table)
        self.assertNotIn("| M15 |", table)
        self.assertNotIn("確度", table)

    def test_missing_required_tf_is_shown_as_pending_not_none(self):
        rows = build_timeframe_decision_rows([record("H1", direction="LONG", state="WAIT")])
        by_tf = {row["timeframe"]: row for row in rows}
        self.assertEqual(by_tf["D1"]["tc_direction"], "—")
        self.assertEqual(by_tf["D1"]["entry_decision"], "判定保留")
        self.assertEqual(by_tf["H4"]["entry_decision"], "判定保留")
        self.assertEqual(by_tf["H1"]["entry_decision"], "LONG候補")

    def test_m15_is_shown_when_acquired_even_if_undetermined(self):
        rows = build_timeframe_decision_rows(
            [
                record("D1"),
                record("H4"),
                record("H1"),
                record("M15", direction=None, state="UNDETERMINED", entry=None, sl=None, tp=(), environment="neutral"),
            ]
        )
        self.assertEqual(rows[-1]["timeframe"], "M15")
        self.assertEqual(rows[-1]["tc_direction"], "NEUTRAL")
        self.assertEqual(rows[-1]["entry_decision"], "判定保留")

    def test_all_native_take_profits_are_preserved_in_single_tp_column(self):
        rows = build_timeframe_decision_rows([record("H4", tp=(101.0, 102.0, 103.0, 104.0))])
        h4 = next(row for row in rows if row["timeframe"] == "H4")
        self.assertEqual(h4["tp"], (101.0, 102.0, 103.0, 104.0))
        table = format_timeframe_decision_table(rows)
        self.assertIn("101.0 / 102.0 / 103.0 / 104.0", table)


if __name__ == "__main__":
    unittest.main()
