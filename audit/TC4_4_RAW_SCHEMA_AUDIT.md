# TC4-4 Raw Schema Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `053f8955bdffcd1aa9eda5b5d02ee535aee1f005`

## Result

**PASS WITH NOTES**

TC4-4 establishes `TCTradePlanRaw` schema version `1.0.0` as a TC-specific Raw-retention wrapper. The schema preserves the recorded TradingCursor response and original `analysis` string, separates lossless parsed content from derived metadata, keeps unknown Native fields, and does not perform Question Contract or TradePlanState normalization.

## 1. Evidence

Primary evidence:

`fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/`

Reviewed formal Raw, with `raw_1h.json` selected for the example because it includes Environment/Setup/Trigger/Entry/SL/TP/Wait-related text and out-of-scope Position Sizing text.

TC4-3 handoff was applied, including:
- Original Raw first;
- Native / Parsed / Derived separation;
- `chartId` not standalone Native;
- unknown Native fields retained;
- Position Size remains outside ②;
- no internal reasoning inference.

## 2. Schema artifacts

Created:

- `tc/spec/TC4_4_TCTRADEPLANRAW_SPEC.md`
- `tc/schema/tc_tradeplan_raw.schema.json`
- `fixtures/tc4_4/TCTradePlanRaw_1h_example.json`
- `audit/TC4_4_RAW_SCHEMA_AUDIT.md`

No TC4-2 fixture was modified.

## 3. Formal schema

Name: `TCTradePlanRaw`

Version: `1.0.0`

JSON Schema dialect: Draft 2020-12.

Required top-level fields:
- `schema_version`
- `record_identity`
- `original_response`
- `parse_status`

Conditional requirement:
- `parse_status.state = PARSED` requires both `parsed_analysis` and string-valued `original_response.analysis`.

Strategy-specific Native fields are optional.

## 4. Original Raw audit

| Gate | Result | Note |
|---|---|---|
| `original_response` required | PASS | entirely missing Original Raw is invalid |
| original `analysis` string retained | PASS | stored at `/original_response/analysis` |
| Original and Parsed separated | PASS | separate top-level areas |
| unknown outer Native fields retained | PASS | `additionalProperties: true` |
| Parse failure may preserve Raw | PASS | PARSE_ERROR/NOT_PARSED do not require `parsed_analysis` |
| HTTP wire-byte identity claimed | NO | TC4-2 did not capture an HTTP wire-byte stream; source fixture remains serialization authority |

The preservation guarantee is therefore semantic JSON-value-level for the response TC4-2 actually recorded, with exact retention of the recorded `analysis` string value.

## 5. Parsed Native audit

`parsed_analysis` is defined as lossless structural parsing only.

Observed fields can be retained:
- `potentialPosition`
- `indicatorReadings`
- `priceMetrics`
- `futureAssumption`
- `observations`
- `action_url`

Unknown inner fields are accepted and retained via open Native objects.

No Entry/SL/TP correction, Trigger generation, key renaming, NODA mapping, Question status or strategy inference is performed.

## 6. Derived metadata audit

`chartId` is not represented as a Native field.

The example stores it only as:

`derived_metadata.chart_id`

with:
- source pointer `/parsed_analysis/action_url`;
- method `url_query_parameter:chartId`.

Result: **PASS**.

## 7. Record identity / raw reference

Required identity:
- `record_id`
- `source_run_id`
- `execution_order`
- `source_raw_artifact`

Selected identity convention:

`source_run_id + ':' + execution-order token`

Selected raw-reference convention for downstream records:

`record_id + RFC 6901 JSON Pointer`

Examples:
- `/original_response/analysis`
- `/parsed_analysis/potentialPosition/entryPrice`
- `/parsed_analysis/observations`

Text-span offsets within observations remain TBD.

## 8. Validation performed

Local Draft 2020-12 validation was executed against the exact designed schema/example structure before repository commit.

Results:

| Test | Result |
|---|---|
| Schema self-check | PASS |
| TCTradePlanRaw 1h example | PASS |
| missing `original_response` | INVALID as required |
| missing Native Strategy fields with Original Raw present | VALID |
| PARSE_ERROR with Original Raw but no `parsed_analysis` | VALID |

These are structural preservation tests only; they do not evaluate TradingCursor trade quality.

## 9. Required / optional audit

### Required
- schema version;
- record identity;
- Original Raw response;
- parse status.

### Optional
- wrapper metadata;
- parsed analysis except when PARSED;
- derived metadata;
- provider Strategy fields including `potentialPosition`, indicators, price metrics, future assumption, observations and action URL.

Result: a No-Trade/failure-like Native response can still be preserved without fabricating missing strategy fields.

## 10. Failure response policy

Only `completed` was formally observed. TC4-4 does not invent provider status enums such as error/timeout/partial.

The schema preserves future non-empty Native response objects and does not require `status = completed`.

Exact future provider failure shapes remain unknown and are not speculated.

## 11. Out-of-scope content

| Content | Raw retention | Authority in ② |
|---|---|---|
| Position Sizing text | KEEP | NO |
| generic Risk Management text | KEEP | NO |
| Risk/Reward text | KEEP | TBD semantic boundary; no new authority field |

No Position Size field or risk-policy logic is introduced.

## 12. Conflict / priority

Structured/text conflict resolution remains **TBD**.

TC4-4 retains both Native forms and does not treat structured content as automatically strategically correct.

TC4-3 candidate source priority is not promoted into a conflict-resolution algorithm.

## 13. Timeframe / repeat audit

| Gate | Result |
|---|---|
| One Native call = one Raw record | PASS |
| 1D / 4h / 1h / 15m synthesis | NO |
| repeat overwrites prior record | NO |
| timestamp alone used as identity | NO |

## 14. Question Contract separation

Common statuses:
- OBSERVED
- NOT_PROVIDED
- AMBIGUOUS
- NOT_APPLICABLE

are **not** embedded into Native Raw.

TC4-4 performs no Q1-Q7 output conversion.

Result: **PASS**.

## 15. Hard Gate audit

| Hard Gate | Result |
|---|---|
| Correct repository | PASS |
| Correct branch | PASS |
| Started from TC4-3 completed HEAD | PASS |
| TC4-2 formal Raw used | PASS |
| TC4-3 handoff reflected | PASS |
| TCTradePlanRaw responsibility documented | PASS |
| Original Raw retained | PASS, semantic recorded-response level |
| Original and Parsed separated | PASS |
| Parse failure preserves Original | PASS |
| Native and Derived separated | PASS |
| original analysis string preserved | PASS |
| parsed analysis lossless-only | PASS |
| potentialPosition Native retention | PASS |
| indicatorReadings Native retention | PASS |
| priceMetrics Native retention | PASS |
| futureAssumption Native retention | PASS |
| observations whole-text retention | PASS |
| action_url retention | PASS |
| chartId falsely Native | NO |
| chartId derived provenance explicit | PASS |
| unknown Native fields preservable | PASS |
| Run Metadata separated from strategy interpretation | PASS |
| timestamp over-defined | NO |
| raw reference convention defined | PASS |
| Q1-Q7 early conversion | NO |
| Question statuses mixed into Raw | NO |
| out-of-scope Native text dropped | NO |
| Position Size authority created | NO |
| Risk/Reward new authority field created | NO |
| structured/text conflict invented | NO |
| TF independence retained | PASS |
| repeat overwrite | NO |
| record identity defined | PASS |
| required/optional defined | PASS |
| missing strategy field blocks Raw retention | NO |
| schema version defined | PASS |
| JSON Schema created | PASS |
| example created | PASS |
| example validation | PASS |
| Original Raw missing invalid | PASS |
| other schemas finalized | NO |
| NODA rules added | NO |
| TC decision logic added | NO |
| Normalizer implemented | NO |
| Adapter implemented | NO |
| TradePlanState finalized | NO |
| Position Sizing implemented | NO |
| `trade-plan-a` changed | NO |
| main merged | NO |

## 16. Notes / TBD

Remaining items for later work:
- provider wire-byte preservation cannot be retroactively proven from TC4-2;
- structured/text conflict policy;
- exact Risk/Reward responsibility boundary;
- whether text-span offsets are needed for free-text evidence;
- handling/version migration if a known Native field changes type rather than merely adding an unknown field;
- runtime implementation of wrapping/parsing is not part of TC4-4.

## 17. Verdict

**TC4-4 = PASS WITH NOTES**

The formal Raw schema is sufficient to proceed to the next design step, provided the next work preserves Raw immutability, does not infer missing TradingCursor semantics, and treats the listed TBD items explicitly.

**Next-work readiness = GO**

No next work is started by this audit.
