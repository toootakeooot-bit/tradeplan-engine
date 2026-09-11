from __future__ import annotations

import json
import unittest

from tc.normalizer import MapperUnavailableError, TCMapper


OBS_1H = (
    "The XAUUSD 1-hour chart shows a consolidation phase within the Bollinger Bands, with price currently trading near the middle band at 4407.329 and slightly below the EMA 20 at 4405.199. "
    "The RSI reading of 46.51 indicates a neutral momentum, neither overbought nor oversold, suggesting a potential continuation or reversal is pending. "
    "Volume has been relatively low and consistent, with no significant spikes to confirm breakout momentum. "
    "The MACD histogram is positive at 3.475 but the MACD line (-2.123) remains below the signal line (1.352), signaling weak bullish momentum. "
    "Key support is at the lower Bollinger Band (4386.362) and a psychological level around 4360.0, while resistance lies at the EMA 20 (4405.199) and upper Bollinger Band (4428.296). "
    "Given the lack of strong directional signals and the consolidation pattern, a breakout trade is not yet confirmed. "
    "A conservative approach would be to wait for a decisive break above 4428.296 with volume confirmation for a long, or below 4386.362 for a short. "
    "Risk management should include tight stop losses if entering on a breakout, and position sizing should account for potential false breakouts in low-volume consolidation zones."
)

OBS_4H = (
    "The XAUUSD 4-hour chart on OANDA shows a potential bullish reversal setup. "
    "Price is currently trading at 4396.385, just above the lower Bollinger Band (4364.748) and near the EMA 20 (4402.955), suggesting a bounce from key support. "
    "The RSI is at 47.09, indicating neutral conditions with room to rise before overbought territory. "
    "Volume has been relatively stable with no significant spikes, suggesting accumulation rather than distribution. "
    "The MACD histogram is turning positive (1.973) while the MACD line (-9.019) is crossing above the signal line (-7.046), signaling a potential bullish momentum shift. "
    "A long position is recommended with entry at current price, stop loss below the lower Bollinger Band at 4370.0, and take profit targets at 4420.0 (near EMA 20), 4450.0 (mid-range resistance), and 4480.0 (upper Bollinger Band). "
    "Risk management is crucial as the market remains in a consolidation phase, and a break below 4364.748 could invalidate the bullish setup. "
    "Alternative scenario: if price fails to hold above 4380.0, consider shorting with stop above 4405.0."
)


def raw_record(*, record_id: str = "RUN-001:03", timeframe: str = "1h", parsed=None, parse_state="PARSED"):
    if parsed is None:
        parsed = {
            "indicatorReadings": [
                {"id": "RSI", "values": {"value": 46.51}},
                {"id": "MACD", "values": {"macd": -2.123}},
            ],
            "priceMetrics": {
                "supportLevels": [4386.362, 4360],
                "current_price": 4396.655,
                "resistanceLevels": [4405.199, 4428.296],
            },
            "futureAssumption": {
                "trend": "neutral",
                "confidenceScore": 0.65,
                "patternDetected": "Consolidation within Bollinger Bands",
            },
            "observations": OBS_1H,
            "potentialPosition": {
                "entryPrice": 4428.296,
                "positionType": "long",
                "takeProfits": [4445, 4460, 4480],
                "stopLoss": 4405.199,
            },
        }
    order = int(record_id.rsplit(":", 1)[1]) if ":" in record_id else 1
    base = {
        "schema_version": "1.0.0",
        "record_identity": {
            "record_id": record_id,
            "source_run_id": record_id.rsplit(":", 1)[0] if ":" in record_id else "RUN-001",
            "execution_order": order,
            "source_raw_artifact": f"tcraw://v1/RUN-001/{order:02d}.json",
        },
        "original_response": {"interval": timeframe, "analysis": json.dumps(parsed)},
        "parse_status": {"state": parse_state},
    }
    if parse_state == "PARSED":
        base["parsed_analysis"] = parsed
    return base


class MapperTests(unittest.TestCase):
    def setUp(self):
        self.mapper = TCMapper()

    def test_frozen_1h_direct_and_light_mappings(self):
        result = self.mapper.map_record(raw_record())
        q = result["question_mapping"]
        self.assertEqual(q["environment"]["status"], "OBSERVED")
        self.assertEqual(q["environment"]["direction"]["normalized_value"], "neutral")
        self.assertEqual(q["entry"]["direction"]["native_value"], "long")
        self.assertEqual(q["entry"]["direction"]["normalized_value"], "LONG")
        self.assertEqual(q["entry"]["price"]["normalized_value"], 4428.296)
        self.assertEqual(q["sl"]["price"]["normalized_value"], 4405.199)
        self.assertEqual(q["tp"]["targets"]["normalized_value"], [4445, 4460, 4480])
        self.assertEqual(result["mapping_policy"]["inference"], "NO")
        self.assertEqual(result["mapping_policy"]["timeframe_synthesis"], "NO")

    def test_frozen_1h_text_evidence_matches_contract(self):
        result = self.mapper.map_record(raw_record())
        q = result["question_mapping"]
        self.assertEqual(q["setup"]["status"], "OBSERVED")
        self.assertEqual(q["setup"]["evidence"][0]["extracted_value"], "a breakout trade is not yet confirmed")
        self.assertEqual(q["trigger"]["status"], "OBSERVED")
        self.assertEqual(
            q["trigger"]["evidence"][0]["extracted_value"].lower(),
            "wait for a decisive break above 4428.296 with volume confirmation for a long, or below 4386.362 for a short",
        )
        self.assertEqual(q["wait"]["status"], "OBSERVED")
        self.assertEqual(
            q["wait"]["evidence"][0]["extracted_value"].lower(),
            "a conservative approach would be to wait for a decisive break above 4428.296 with volume confirmation",
        )
        self.assertEqual(q["invalidation"]["status"], "NOT_PROVIDED")
        self.assertEqual(q["alternative_scenario"]["status"], "OBSERVED")
        self.assertEqual(q["alternative_scenario"]["evidence"][0]["extracted_value"].lower(), "below 4386.362 for a short")

    def test_4h_missing_trigger_remains_valid_and_not_inferred_from_macd(self):
        parsed = {
            "potentialPosition": {
                "entryPrice": 4396.385,
                "positionType": "long",
                "takeProfits": [4420, 4450, 4480],
                "stopLoss": 4370,
            },
            "indicatorReadings": [{"id": "MACD", "values": {"macd": -9.019, "signal": -7.046}}],
            "priceMetrics": {"supportLevels": [4364.748, 4380], "current_price": 4396.385},
            "futureAssumption": {
                "trend": "bullish",
                "confidenceScore": 0.65,
                "patternDetected": "Bullish Reversal near Support with MACD Crossover",
            },
            "observations": OBS_4H,
        }
        result = self.mapper.map_record(raw_record(record_id="RUN-001:02", timeframe="4h", parsed=parsed))
        q = result["question_mapping"]
        self.assertEqual(q["setup"]["status"], "OBSERVED")
        self.assertEqual(q["trigger"], {"question_id": "Q3", "status": "NOT_PROVIDED", "evidence": []})
        self.assertEqual(q["entry"]["status"], "OBSERVED")
        self.assertEqual(q["invalidation"]["status"], "OBSERVED")
        self.assertIn("could invalidate the bullish setup", q["invalidation"]["evidence"][0]["extracted_value"].lower())
        self.assertEqual(q["alternative_scenario"]["status"], "OBSERVED")

    def test_indicators_pattern_price_metrics_and_sizing_are_not_promoted(self):
        result = self.mapper.map_record(raw_record())
        deferred = result["excluded_or_deferred"]
        self.assertEqual(deferred["indicatorReadings"], "NOT_MAPPED")
        self.assertEqual(deferred["futureAssumption.patternDetected"], "TBD_COMMON_ADOPTION")
        self.assertEqual(deferred["priceMetrics"], "TBD_COMMON_ADOPTION")
        self.assertEqual(deferred["position_sizing_text"], "EXCLUDED_OUT_OF_SCOPE")
        serialized = json.dumps(result).lower()
        self.assertNotIn('"position_size"', serialized)
        self.assertNotIn('"trade_state"', serialized)

    def test_all_mapped_values_retain_record_and_pointer_provenance(self):
        result = self.mapper.map_record(raw_record())
        q = result["question_mapping"]
        refs = [
            q["environment"]["direction"]["raw_reference"],
            q["entry"]["direction"]["raw_reference"],
            q["entry"]["price"]["raw_reference"],
            q["sl"]["price"]["raw_reference"],
            q["tp"]["targets"]["raw_reference"],
            q["setup"]["evidence"][0]["raw_reference"],
            q["trigger"]["evidence"][0]["raw_reference"],
            q["wait"]["evidence"][0]["raw_reference"],
        ]
        for ref in refs:
            self.assertEqual(ref["record_id"], "RUN-001:03")
            self.assertTrue(ref["pointer"].startswith("/parsed_analysis/"))
        for key in ("setup", "trigger", "wait", "alternative_scenario"):
            for evidence in q[key].get("evidence", []):
                span = evidence["raw_reference"].get("character_span")
                self.assertIsNotNone(span)
                extracted = OBS_1H[span["start"]:span["end"]]
                self.assertEqual(extracted, evidence["extracted_value"])

    def test_missing_fields_become_not_provided_not_inferred(self):
        parsed = {"observations": "Price is near support. MACD is crossing upward."}
        result = self.mapper.map_record(raw_record(parsed=parsed))
        q = result["question_mapping"]
        for key in ("environment", "setup", "trigger", "entry", "sl", "tp", "wait", "invalidation", "alternative_scenario"):
            self.assertEqual(q[key]["status"], "NOT_PROVIDED", key)

    def test_unknown_position_type_is_ambiguous_not_normalized(self):
        parsed = {
            "potentialPosition": {"positionType": "buy-ish", "entryPrice": 100.0},
            "observations": "A setup exists.",
        }
        result = self.mapper.map_record(raw_record(parsed=parsed))
        entry = result["question_mapping"]["entry"]
        self.assertEqual(entry["status"], "AMBIGUOUS")
        self.assertNotIn("direction", entry)
        self.assertEqual(entry["price"]["normalized_value"], 100.0)

    def test_parse_error_is_not_converted_to_question_status(self):
        with self.assertRaises(MapperUnavailableError):
            self.mapper.map_record(raw_record(parsed={}, parse_state="PARSE_ERROR"))

    def test_one_record_one_timeframe_no_aggregation_surface(self):
        result = self.mapper.map_record(raw_record(timeframe="1h"))
        self.assertEqual(result["source_contract"]["timeframe"], "1h")
        self.assertEqual(result["mapping_policy"]["timeframe_synthesis"], "NO")
        self.assertNotIn("timeframes", result)
        self.assertNotIn("aggregate", result)

    def test_mapper_is_deterministic_for_same_raw_record(self):
        raw = raw_record()
        first = self.mapper.map_record(raw)
        second = self.mapper.map_record(raw)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
