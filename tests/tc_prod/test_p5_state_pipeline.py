from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tc.engine import TCEngine
from tc.native.client import NativeClient, NativeRequest
from tc.normalizer import MapperUnavailableError, TCMapper
from tc.state import TCStateEvaluator
from tc.storage import FileRawStorage

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "fixtures" / "tc4_2" / "TC4-2-OANDA-XAUUSD-20260910-01"


def load_raw(name: str) -> dict:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


class StaticExecutor:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls = []

    def __call__(self, *, exchange: str, symbol: str, interval: str):
        self.calls.append((exchange, symbol, interval))
        return copy.deepcopy(self.payload)


def run_engine(payload: dict, *, request_id: str, run_id: str, order: int, timeframe: str):
    td = tempfile.TemporaryDirectory()
    executor = StaticExecutor(payload)
    engine = TCEngine(NativeClient(executor), FileRawStorage(td.name))
    result = engine.analyze(
        NativeRequest(
            request_id=request_id,
            source_run_id=run_id,
            execution_order=order,
            analysis_source="OANDA",
            analysis_symbol="XAUUSD",
            timeframe=timeframe,
        )
    )
    return td, executor, result


class P5FrozenRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw1 = load_raw("raw_1h.json")
        cls.raw4 = load_raw("raw_4h.json")
        cls.td1, cls.ex1, cls.one = run_engine(
            cls.raw1, request_id="P5-1H", run_id="P5-FROZEN-1H", order=1, timeframe="H1"
        )
        cls.td4, cls.ex4, cls.four = run_engine(
            cls.raw4, request_id="P5-4H", run_id="P5-FROZEN-4H", order=1, timeframe="H4"
        )

    @classmethod
    def tearDownClass(cls):
        cls.td1.cleanup()
        cls.td4.cleanup()

    def test_tcreg_01_full_plan_explicit_wait_is_wait(self):
        q = self.one.state["question_availability"]
        self.assertEqual(self.one.state["trade_state"]["value"], "WAIT")
        for key in ("trigger", "entry", "sl", "tp", "wait"):
            self.assertEqual(q[key], "OBSERVED")

    def test_tcreg_02_long_candidate_and_wait_coexist(self):
        self.assertEqual(self.one.state["plan_axis"]["entry_direction"], "LONG")
        self.assertEqual(self.one.state["trade_state"]["value"], "WAIT")
        self.assertFalse(self.one.state["guardrails"]["direction_and_state_are_same_axis"])

    def test_tcreg_03_missing_trigger_does_not_force_wait(self):
        self.assertEqual(self.four.mapping["question_mapping"]["trigger"]["status"], "NOT_PROVIDED")
        self.assertNotEqual(self.four.state["trade_state"]["value"], "WAIT")
        self.assertFalse(self.four.state["guardrails"]["missing_trigger_implies_wait"])

    def test_tcreg_04_current_price_recommendation_is_actionable(self):
        ts = self.four.state["trade_state"]
        self.assertEqual(ts["value"], "ACTIONABLE")
        self.assertTrue(any("entry at current price" in x["extracted_text"].lower() for x in ts["evidence"]))

    def test_tcreg_05_plan_values_do_not_auto_actionable(self):
        axis = self.one.state["plan_axis"]
        self.assertTrue(all(axis[k] is not None for k in ("entry_direction", "entry_price", "stop_loss", "take_profits")))
        self.assertEqual(self.one.state["trade_state"]["value"], "WAIT")
        self.assertFalse(self.one.state["guardrails"]["entry_sl_tp_implies_actionable"])

    def test_tcreg_06_invalidation_rule_observed(self):
        self.assertEqual(self.four.state["trade_state"]["invalidation_rule_evidence"]["status"], "OBSERVED")

    def test_tcreg_07_rule_does_not_make_current_invalid(self):
        ts = self.four.state["trade_state"]
        self.assertEqual(ts["invalidation_rule_evidence"]["status"], "OBSERVED")
        self.assertEqual(ts["current_invalid_evidence"]["status"], "NOT_OBSERVED")
        self.assertNotEqual(ts["value"], "INVALID")
        self.assertFalse(self.four.state["guardrails"]["invalidation_rule_implies_current_invalid"])

    def test_tcreg_08_no_current_price_derived_invalid(self):
        self.assertFalse(self.four.state["guardrails"]["current_price_compared_to_invalidation_rule"])
        self.assertEqual(self.four.state["trade_state"]["value"], "ACTIONABLE")

    def test_tcreg_09_sl_and_invalidation_are_separate(self):
        self.assertEqual(self.four.state["plan_axis"]["stop_loss"], 4370)
        rule = self.four.state["trade_state"]["invalidation_rule_evidence"]
        self.assertEqual(rule["status"], "OBSERVED")
        self.assertIn("4364.748", rule["extracted_text"])
        self.assertNotEqual(str(self.four.state["plan_axis"]["stop_loss"]), "4364.748")

    def test_tcreg_10_alternative_and_wait_are_separate(self):
        ts = self.one.state["trade_state"]
        self.assertEqual(ts["alternative_scenario_evidence"]["status"], "OBSERVED")
        self.assertEqual(ts["wait_evidence"]["status"], "OBSERVED")
        self.assertFalse(self.one.state["guardrails"]["alternative_scenario_implies_wait"])

    def test_tcreg_11_alternative_and_invalid_are_separate(self):
        ts = self.four.state["trade_state"]
        self.assertEqual(ts["alternative_scenario_evidence"]["status"], "OBSERVED")
        self.assertEqual(ts["current_invalid_evidence"]["status"], "NOT_OBSERVED")
        self.assertFalse(self.four.state["guardrails"]["alternative_scenario_implies_invalid"])

    def test_tcreg_12_environment_state_separate(self):
        self.assertEqual(self.one.mapping["question_mapping"]["environment"]["status"], "OBSERVED")
        self.assertEqual(self.one.state["trade_state"]["value"], "WAIT")
        self.assertFalse(self.one.state["guardrails"]["environment_determines_state"])

    def test_tcreg_13_setup_state_separate(self):
        self.assertEqual(self.one.mapping["question_mapping"]["setup"]["status"], "OBSERVED")
        self.assertEqual(self.one.state["trade_state"]["value"], "WAIT")
        self.assertFalse(self.one.state["guardrails"]["setup_determines_state"])

    def test_tcreg_14_position_sizing_text_raw_only(self):
        observations = self.one.raw_record["parsed_analysis"]["observations"].lower()
        self.assertIn("position sizing", observations)
        self.assertEqual(
            self.one.mapping["excluded_or_deferred"]["position_sizing_text"],
            "EXCLUDED_OUT_OF_SCOPE",
        )
        serialized_state = json.dumps(self.one.state).lower()
        self.assertNotIn('"position_size"', serialized_state)
        self.assertNotIn('"lot"', serialized_state)

    def test_tcreg_15_indicators_not_mapped_to_state(self):
        ids = {x["id"] for x in self.one.raw_record["parsed_analysis"]["indicatorReadings"]}
        self.assertTrue({"RSI", "EMA", "VOL", "BB", "MACD"}.issubset(ids))
        self.assertEqual(self.one.mapping["excluded_or_deferred"]["indicatorReadings"], "NOT_MAPPED")
        self.assertEqual(self.one.state["guardrails"]["inference"], "NO")

    def test_tcreg_16_pattern_does_not_create_trigger_or_state(self):
        self.assertTrue(self.four.raw_record["parsed_analysis"]["futureAssumption"]["patternDetected"])
        self.assertEqual(
            self.four.mapping["excluded_or_deferred"]["futureAssumption.patternDetected"],
            "TBD_COMMON_ADOPTION",
        )
        self.assertEqual(self.four.mapping["question_mapping"]["trigger"]["status"], "NOT_PROVIDED")
        self.assertEqual(self.four.state["trade_state"]["value"], "ACTIONABLE")

    def test_tcreg_17_missing_trigger_mapping_remains_valid(self):
        self.assertEqual(self.four.mapping["question_mapping"]["trigger"]["status"], "NOT_PROVIDED")
        self.assertEqual(self.four.mapping["source_contract"]["record_id"], "P5-FROZEN-4H:01")

    def test_tcreg_18_question_status_vocab_separate_from_trade_state(self):
        avail = set(self.one.state["question_availability"].values()) | set(self.four.state["question_availability"].values())
        states = {self.one.state["trade_state"]["value"], self.four.state["trade_state"]["value"]}
        self.assertTrue(avail.issubset({"OBSERVED", "NOT_PROVIDED", "AMBIGUOUS", "NOT_APPLICABLE"}))
        self.assertTrue(states.issubset({"WAIT", "ACTIONABLE", "INVALID", "UNDETERMINED"}))
        self.assertTrue(avail.isdisjoint(states))

    def test_tcreg_19_one_record_one_timeframe_no_synthesis(self):
        self.assertEqual(self.one.state["source"]["timeframe"], "1h")
        self.assertEqual(self.four.state["source"]["timeframe"], "4h")
        self.assertFalse(self.one.state["guardrails"]["timeframe_synthesis"])
        self.assertEqual(self.one.mapping["mapping_policy"]["timeframe_synthesis"], "NO")

    def test_tcreg_20_actionable_not_execution_permission(self):
        self.assertEqual(self.four.state["trade_state"]["value"], "ACTIONABLE")
        self.assertFalse(self.four.state["guardrails"]["actionable_authorizes_execution"])
        serialized = json.dumps(self.four.state).lower()
        for forbidden in ('"order"', '"lot"', '"position_size"', '"risk_amount"', '"buy_now"', '"sell_now"'):
            self.assertNotIn(forbidden, serialized)

    def test_saved_response_pipeline_is_deterministic_after_raw_capture(self):
        mapper = TCMapper()
        evaluator = TCStateEvaluator()
        mapping_a = mapper.map_record(self.one.raw_record)
        state_a = evaluator.evaluate(self.one.raw_record, mapping_a)
        mapping_b = mapper.map_record(self.one.raw_record)
        state_b = evaluator.evaluate(self.one.raw_record, mapping_b)
        self.assertEqual(mapping_a, mapping_b)
        self.assertEqual(state_a, state_b)

    def test_end_to_end_pipeline_persists_original_response_before_mapping(self):
        self.assertEqual(self.ex1.calls, [("OANDA", "XAUUSD", "1h")])
        ref = self.one.raw_record["record_identity"]["source_raw_artifact"]
        self.assertTrue(ref.startswith("tcraw://v1/"))
        self.assertEqual(self.one.raw_record["original_response"], self.raw1)
        self.assertEqual(self.one.state["trade_state"]["value"], "WAIT")

    def test_entry_without_explicit_current_state_is_undetermined(self):
        payload = copy.deepcopy(self.raw4)
        parsed = json.loads(payload["analysis"])
        parsed["observations"] = "A potential bullish reversal setup is present. Entry price 4396.385 is listed for reference."
        payload["analysis"] = json.dumps(parsed)
        td, _, result = run_engine(payload, request_id="U1", run_id="P5-UND", order=1, timeframe="H4")
        try:
            self.assertEqual(result.mapping["question_mapping"]["entry"]["status"], "OBSERVED")
            self.assertEqual(result.state["trade_state"]["value"], "UNDETERMINED")
        finally:
            td.cleanup()

    def test_conflicting_current_wait_and_action_text_is_undetermined(self):
        payload = copy.deepcopy(self.raw4)
        parsed = json.loads(payload["analysis"])
        parsed["observations"] = (
            "A long position is recommended with entry at current price. "
            "However, wait for confirmation before entry."
        )
        payload["analysis"] = json.dumps(parsed)
        td, _, result = run_engine(payload, request_id="C1", run_id="P5-CONFLICT", order=1, timeframe="H4")
        try:
            self.assertEqual(result.state["trade_state"]["value"], "UNDETERMINED")
            self.assertTrue(result.state["trade_state"]["conflict_preserved"])
        finally:
            td.cleanup()

    def test_parse_failure_remains_upstream_failure_not_trade_state(self):
        payload = copy.deepcopy(self.raw1)
        payload["analysis"] = "{bad json"
        td = tempfile.TemporaryDirectory()
        engine = TCEngine(NativeClient(StaticExecutor(payload)), FileRawStorage(td.name))
        try:
            with self.assertRaises(MapperUnavailableError):
                engine.analyze(
                    NativeRequest("BAD1", "P5-BAD", 1, "OANDA", "XAUUSD", "H1")
                )
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
