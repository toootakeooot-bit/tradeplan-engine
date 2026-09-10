#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


wait_1h = load("fixtures/tc4_6/TCTradeState_1h_wait_example.json")
action_4h = load("fixtures/tc4_6/TCTradeState_4h_current_entry_example.json")
missing_trigger = load("fixtures/tc4_5/TCTradePlanState_missing_trigger_example.json")
mapping_1h = load("fixtures/tc4_5/TCTradePlanState_1h_provisional_example.json")
raw_1h = load("fixtures/tc4_4/TCTradePlanRaw_1h_example.json")

results = []


def check(case_id, name, condition, detail):
    results.append({
        "case_id": case_id,
        "name": name,
        "result": "PASS" if condition else "FAIL",
        "detail": detail,
    })


q = wait_1h["question_availability"]
ts = wait_1h["trade_state"]
pa = wait_1h["plan_axis"]
g = wait_1h["guardrails"]
a_ts = action_4h["trade_state"]
a_g = action_4h["guardrails"]
a_q = action_4h["question_availability"]

check("TCREG-01", "1h full plan + explicit wait -> WAIT",
      ts["value"] == "WAIT" and q["entry"] == q["sl"] == q["tp"] == q["trigger"] == q["wait"] == "OBSERVED",
      "1h fixed state fixture preserves full plan and explicit WAIT.")

check("TCREG-02", "LONG candidate + WAIT coexist",
      pa["entry_direction"] == "LONG" and ts["value"] == "WAIT" and g["direction_and_state_are_same_axis"] is False,
      "Direction and trade state remain separate axes.")

check("TCREG-03", "Trigger NOT_PROVIDED != WAIT",
      missing_trigger["question_mapping"]["trigger"]["status"] == "NOT_PROVIDED"
      and action_4h["trade_state"]["value"] != "WAIT"
      and a_g["missing_trigger_implies_wait"] is False,
      "4h missing Trigger remains non-WAIT under explicit current-entry evidence.")

check("TCREG-04", "4h explicit current entry -> ACTIONABLE",
      a_ts["value"] == "ACTIONABLE"
      and any("entry at current price" in e["extracted_text"] for e in a_ts["evidence"]),
      "ACTIONABLE is supported by explicit Native current-entry text.")

check("TCREG-05", "Entry presence != automatic ACTIONABLE",
      all(k in pa for k in ("entry_direction", "entry_price", "stop_loss", "take_profits"))
      and ts["value"] == "WAIT"
      and g["entry_sl_tp_implies_actionable"] is False,
      "1h has Entry/SL/TP yet remains WAIT.")

check("TCREG-06", "Invalidation Rule observed",
      a_q["invalidation_rule"] == "OBSERVED"
      and a_ts["invalidation_rule_evidence"]["status"] == "OBSERVED",
      "4h keeps the future invalidation rule as evidence.")

check("TCREG-07", "Invalidation Rule != Current INVALID",
      a_ts["invalidation_rule_evidence"]["status"] == "OBSERVED"
      and a_ts["current_invalid_evidence"]["status"] == "NOT_OBSERVED"
      and a_ts["value"] != "INVALID"
      and a_g["invalidation_rule_implies_current_invalid"] is False,
      "Rule presence does not produce current INVALID.")

check("TCREG-08", "No current_price-derived INVALID",
      a_g["current_price_compared_to_invalidation_rule"] is False,
      "Fixed semantics prohibit current-price comparison from synthesizing INVALID.")

check("TCREG-09", "SL / Invalidation separation",
      pa["stop_loss"] == 4405.199
      and ts["invalidation_rule_evidence"]["status"] == "NOT_PROVIDED"
      and a_ts["invalidation_rule_evidence"]["status"] == "OBSERVED",
      "SL and scenario invalidation are represented independently.")

check("TCREG-10", "Alternative / WAIT separation",
      ts["alternative_scenario_evidence"]["status"] == "OBSERVED"
      and ts["wait_release_condition_evidence"]["status"] == "OBSERVED"
      and "alternative_scenario_evidence" in ts
      and "wait_release_condition_evidence" in ts,
      "Alternative path and WAIT evidence occupy separate fields.")

check("TCREG-11", "Alternative / INVALID separation",
      a_ts["alternative_scenario_evidence"]["status"] == "OBSERVED"
      and a_ts["current_invalid_evidence"]["status"] == "NOT_OBSERVED"
      and a_g["alternative_scenario_implies_invalid"] is False,
      "Alternative scenario does not imply current INVALID.")

check("TCREG-12", "Environment / State separation",
      mapping_1h["question_mapping"]["environment"]["status"] == "OBSERVED"
      and ts["value"] == "WAIT"
      and "trade_state" not in mapping_1h["question_mapping"]["environment"],
      "Environment evidence remains distinct from trade state.")

check("TCREG-13", "Setup / State separation",
      mapping_1h["question_mapping"]["setup"]["status"] == "OBSERVED"
      and ts["value"] == "WAIT",
      "Observed Setup can coexist with WAIT.")

check("TCREG-14", "Position Size exclusion",
      "position sizing" in raw_1h["parsed_analysis"]["observations"].lower()
      and mapping_1h["excluded_or_deferred"]["position_sizing_text"] == "EXCLUDED_OUT_OF_SCOPE"
      and "position_size" not in ts,
      "Native sizing text is retained in Raw but excluded from provisional state.")

indicator_ids = {x.get("id") for x in raw_1h["parsed_analysis"]["indicatorReadings"]}
check("TCREG-15", "Indicator inference prohibited",
      {"RSI", "EMA", "VOL", "BB", "MACD"}.issubset(indicator_ids)
      and mapping_1h["excluded_or_deferred"]["indicatorReadings"] == "NOT_MAPPED"
      and g["inference"] == "NO",
      "Indicators exist in Raw but are not mapped into state logic.")

check("TCREG-16", "patternDetected inference prohibited",
      bool(raw_1h["parsed_analysis"]["futureAssumption"]["patternDetected"])
      and mapping_1h["excluded_or_deferred"]["futureAssumption.patternDetected"] == "TBD_COMMON_ADOPTION"
      and g["inference"] == "NO",
      "Pattern label exists but does not create Trigger/State.")

check("TCREG-17", "Missing Trigger mapping valid",
      missing_trigger["question_mapping"]["trigger"]["status"] == "NOT_PROVIDED"
      and missing_trigger["guardrails"]["missing_trigger_blocks_provisional_mapping"] is False,
      "Missing Trigger does not invalidate the mapping record.")

availability_values = set(q.values()) | set(a_q.values())
trade_state_values = {ts["value"], a_ts["value"]}
check("TCREG-18", "Question Status / Trade State separation",
      availability_values.issubset({"OBSERVED", "NOT_PROVIDED", "AMBIGUOUS", "NOT_APPLICABLE"})
      and trade_state_values.issubset({"WAIT", "ACTIONABLE", "INVALID", "UNDETERMINED"})
      and availability_values.isdisjoint(trade_state_values),
      "Availability status and trade-state vocabularies are disjoint.")

check("TCREG-19", "No 4TF synthesis",
      wait_1h["source"]["timeframe"] == "1h"
      and action_4h["source"]["timeframe"] == "4h"
      and mapping_1h["mapping_policy"]["timeframe_synthesis"] == "NO",
      "Each fixture remains one-record/one-timeframe; synthesis is disabled.")

forbidden_execution_keys = {"order", "lot", "position_size", "risk_amount", "execution_instruction", "buy_now", "sell_now"}
serialized_action = json.dumps(action_4h).lower()
check("TCREG-20", "ACTIONABLE != Execution Permission",
      a_ts["value"] == "ACTIONABLE"
      and a_g["actionable_authorizes_execution"] is False
      and not any(f'"{k}"' in serialized_action for k in forbidden_execution_keys),
      "ACTIONABLE does not authorize or encode order execution.")

not_testable = [
    ("NT01", "Current INVALID positive recognition", "EVIDENCE_NOT_AVAILABLE"),
    ("NT02", "True same-axis Structured/Text conflict resolution", "EVIDENCE_NOT_AVAILABLE"),
    ("NT03", "Alternative Scenario automatic transition", "EVIDENCE_NOT_AVAILABLE"),
    ("NT04", "WAIT release runtime evaluation", "OUT_OF_SCOPE"),
    ("NT05", "Invalidation runtime evaluation", "OUT_OF_SCOPE"),
]

failed = [r for r in results if r["result"] == "FAIL"]
payload = {
    "testable_cases": len(results),
    "pass": len(results) - len(failed),
    "fail": len(failed),
    "not_testable": len(not_testable),
    "results": results,
    "not_testable_cases": [
        {"case_id": c, "name": n, "result": "NOT_TESTABLE", "reason": reason}
        for c, n, reason in not_testable
    ],
}
print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
raise SystemExit(1 if failed else 0)
