# TC4-4 — TCTradePlanRaw Specification

Status: **TC4-4 baseline / formal raw-retention schema**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `053f8955bdffcd1aa9eda5b5d02ee535aee1f005`

## 1. Purpose

`TCTradePlanRaw` is the TC-specific, audit-oriented record used to preserve one TradingCursor Native response before any Question Contract mapping or TradePlanState normalization.

```text
TradingCursor Native Response
          ↓
     TCTradePlanRaw
          ↓
 future Mapper / Normalizer
          ↓
    TradePlanState
```

TCTradePlanRaw is **not** TradePlanState, is **not** the Q1-Q7 answer object, and is **not** a NODA representation.

Primary rule:

> Preserve first. Parse second. Normalize later.

## 2. Evidence basis

Primary formal evidence:

`fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/`

including formal 1D / 4h / 1h / 15m Raw and the 1h repeat.

TC4-3 handoff is also authoritative for this design:

- preserve the original TradingCursor run envelope and original `analysis` string;
- keep Run Metadata separate from strategy meaning;
- keep TC-native fields even when they do not map to Q1-Q7;
- keep out-of-scope native text in Raw;
- do not infer hidden reasoning or missing strategy meaning;
- `chartId` is not a standalone Native Raw field.

## 3. Schema identity

Formal schema name:

`TCTradePlanRaw`

Initial schema version:

`1.0.0`

Schema file:

`tc/schema/tc_tradeplan_raw.schema.json`

Versioning policy:

- breaking wrapper/schema contract change → major version;
- backward-compatible optional wrapper/derived field addition → minor version;
- documentation/constraint clarification with no data-shape incompatibility → patch version.

Native provider field additions do not by themselves require a schema bump because unknown Native fields are preserved under open Native objects.

## 4. Top-level structure

```text
TCTradePlanRaw
├─ schema_version
├─ record_identity
├─ wrapper_metadata           optional
├─ original_response          REQUIRED / primary evidence
├─ parsed_analysis            optional; required when parse_status=PARSED
├─ derived_metadata           optional
└─ parse_status               REQUIRED
```

### Provenance classes

- `original_response` = `source_native`
- `parsed_analysis` = mechanical parse of Native `analysis`; no semantic normalization
- `wrapper_metadata` = `wrapper_generated`
- `derived_metadata` = `derived`

`Native != Parsed != Derived`.

## 5. Original Raw preservation

`original_response` is mandatory and is the primary evidence area. It preserves the TradingCursor response at the semantic JSON-value level and permits unknown outer Native fields through `additionalProperties: true`.

The formal TC4-2 fixture identified by `record_identity.source_raw_artifact` remains the serialization-level source artifact. TC4-4 does not claim capture of HTTP wire bytes that were never retained by TC4-2.

`original_response.analysis` is the authoritative **original_analysis** value when present. Its original string is retained; it is not replaced by the parsed form.

Unknown Native fields must not be dropped merely to satisfy the wrapper schema.

## 6. Original vs Parsed

When `original_response.analysis` is a JSON-formatted string, TCTradePlanRaw may also hold `parsed_analysis`.

`parsed_analysis` is allowed only as a **lossless structural parse**:

Allowed:
- JSON parse;
- preserve key names;
- preserve values;
- preserve arrays and object nesting;
- preserve unknown Native fields.

Forbidden:
- key renaming for common-schema convenience;
- value correction;
- field deletion;
- field merge;
- unit correction;
- Entry / SL / TP recalculation;
- Trigger creation;
- NODA concepts;
- Q1-Q7 status injection.

## 7. Parse status

TC4-4 defines a TCTradePlanRaw-local parse status:

- `PARSED`
- `NOT_PARSED`
- `PARSE_ERROR`

This is not the Common Question status set (`OBSERVED`, `NOT_PROVIDED`, `AMBIGUOUS`, `NOT_APPLICABLE`).

Rules:

- `PARSED` requires `original_response.analysis` to be a string and requires `parsed_analysis`.
- `NOT_PARSED` and `PARSE_ERROR` may preserve the Original Raw without `parsed_analysis`.
- a parse failure does **not** invalidate Raw retention when `original_response` itself exists.

## 8. Observed Native analysis fields

The schema recognizes, but does not require, the following observed inner fields:

- `potentialPosition`
  - `entryPrice`
  - `positionType`
  - `takeProfits`
  - `stopLoss`
- `indicatorReadings`
- `priceMetrics`
  - `supportLevels`
  - `current_price`
  - `resistanceLevels`
- `futureAssumption`
  - `trend`
  - `confidenceScore`
  - `patternDetected`
- `observations`
- `action_url`

These are optional Native fields. Their absence does not make the Raw record invalid.

## 9. Unknown Native fields

Unknown Native outer and inner fields are preserved rather than rejected:

```text
Unknown Native field
→ retain as Native data
→ do not assign meaning speculatively
→ do not map automatically to Q1-Q7
```

Known wrapper-level top fields remain closed and versioned; provider-native objects remain open.

## 10. `potentialPosition`

`potentialPosition` is retained using Native names and Native values.

TC4-4 does not rename:

`positionType = "long"`

into:

`direction = "LONG"`.

That belongs to a later Normalizer.

## 11. `indicatorReadings`

The array is retained as Native structured data. TC4-4 does not turn indicator values into strategy meaning.

For example:

`RSI < 30 → oversold → Setup`

is not a TCTradePlanRaw operation.

The schema does not restrict indicator IDs to RSI / EMA / VOL / BB / MACD; future Native indicator entries can be retained.

## 12. `observations`

`observations` remains one Native free-text value. TC4-4 does not split it into Environment / Setup / Trigger / Entry / SL / TP / Wait / Invalidation fields.

Out-of-scope wording such as Position Sizing or generic Risk Management remains present in the original text.

## 13. Run Metadata

Observed TradingCursor fields remain inside `original_response` because they are source-native:

- `status`
- `exchange`
- `symbol`
- `interval`
- `model`
- `timestamp`

`timestamp` is treated only as the returned TradingCursor response / analysis timestamp. TC4-4 does not redefine it as candle close time, chart capture time, or market-observation time.

`action_url` is Native analysis content and remains unmodified.

## 14. Wrapper Metadata

`wrapper_metadata` is optional and explicitly wrapper-generated. Example wrapper metadata may include:

- `source_work`
- `survey_mode`
- `comparison_level`

It must never be presented as TradingCursor-native strategy authority.

## 15. `chartId`

`chartId` was not observed as a standalone Native Raw field. It occurs inside the `action_url` query string.

TC4-4 permits an optional derived representation:

```text
derived_metadata.chart_id.value
derived_metadata.chart_id.derived_from_pointer
derived_metadata.chart_id.method
```

with:

- source pointer fixed to `/parsed_analysis/action_url`;
- method fixed to `url_query_parameter:chartId`.

This keeps derived chart identity visibly separate from Native Raw.

## 16. Record identity

Every TCTradePlanRaw record requires:

- `record_id`
- `source_run_id`
- `execution_order`
- `source_raw_artifact`

The selected deterministic convention is:

```text
record_id = source_run_id + ":" + zero/non-zero-padded execution order token
```

Example:

`TC4-2-OANDA-XAUUSD-20260910-01:03`

The identity is tied to the source run and execution order, not to timestamp alone. Repeats are separate records and must not overwrite prior records.

## 17. Raw reference

TC4-4 fixes the external raw-reference convention as:

```text
record_id + RFC 6901 JSON Pointer
```

Examples:

- original analysis: `/original_response/analysis`
- parsed Entry price: `/parsed_analysis/potentialPosition/entryPrice`
- Native free text: `/parsed_analysis/observations`

A downstream mapping record can therefore refer to the exact TCTradePlanRaw record plus a stable pointer without changing Raw content.

Text-span offsets inside `observations` remain TBD and are not required by TC4-4.

## 18. Required fields

Required top-level fields:

- `schema_version`
- `record_identity`
- `original_response`
- `parse_status`

Required `record_identity` fields:

- `record_id`
- `source_run_id`
- `execution_order`
- `source_raw_artifact`

Conditional rule:

- if `parse_status.state = PARSED`, then `parsed_analysis` and `original_response.analysis` are required.

## 19. Optional fields

Optional top-level fields:

- `wrapper_metadata`
- `parsed_analysis` when not PARSED
- `derived_metadata`

Observed strategy fields such as `potentialPosition`, `futureAssumption`, `confidenceScore`, and Trigger-related text remain optional Native content.

No TradePlan strategy field is required merely because it appeared in the five TC4-2 samples.

## 20. Failure / partial responses

TC4-2 formally observed only `status = completed`. TC4-4 does not invent an enum for unobserved provider statuses.

The schema therefore accepts a preserved non-empty `original_response` without requiring `potentialPosition`, model, timestamp, or even an analysis string when it is not represented as `PARSED`.

This keeps evidence-preservation possible for future provider failures/partials without pretending to know their exact response format.

An entirely missing `original_response` is invalid.

## 21. Out-of-scope Native content

Native text containing Position Sizing, generic Risk Management, or Risk/Reward is retained without deletion.

Disposition:

```text
Raw retention = KEEP
TradePlan Engine authority = NO
Question mapping = outside TC4-4
```

TC4-4 does not create a new `riskReward` authority field. Risk/Reward responsibility remains TBD where the text could be strategy-side SL/TP rationale or common risk policy.

## 22. Structured/text conflict

TC4-4 does not resolve a future conflict such as:

`potentialPosition.positionType = long`

versus text preferring short.

Both representations are retained. Conflict resolution remains **TBD** for later work with adequate evidence.

The TC4-3 candidate source preference is not converted into a correctness rule here.

## 23. Timeframe independence

One TradingCursor Native call corresponds to one TCTradePlanRaw record.

1D / 4h / 1h / 15m are not combined into one synthetic Raw record. Live repeat runs are separate records and are never overwritten.

## 24. Question Contract separation

TCTradePlanRaw does not embed Q1-Q7 answers or Common Question statuses.

```text
TCTradePlanRaw
potentialPosition.entryPrice
        ↓
future Mapper / Normalizer
        ↓
Q4 / TradePlanState
```

No Question Contract answer is generated by TC4-4.

## 25. Validation requirements

TC4-4 validation requires:

1. the schema itself is valid JSON Schema Draft 2020-12;
2. the formal 1h example validates;
3. absence of `original_response` fails validation;
4. absence of strategy fields alone does not fail validation;
5. `PARSE_ERROR` can retain Original Raw without parsed analysis.

These checks are structural preservation checks, not trading-quality tests.

## 26. Example source

Formal example source:

`fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/raw_1h.json`

Output example:

`fixtures/tc4_4/TCTradePlanRaw_1h_example.json`

The TC4-2 evidence file is not modified.

## 27. Explicit non-goals

TC4-4 does not implement or finalize:

- Q1-Q7 mapping output;
- Normalizer;
- Adapter;
- TradePlanState;
- NODA Raw;
- NODA rules;
- Position Sizing;
- account/risk amount policy;
- execution;
- 4TF synthesis;
- structured/text conflict resolution;
- trading-result evaluation.

## 28. Wire-byte limitation

TC4-4 can preserve the full TradingCursor response that TC4-2 recorded, including the exact `analysis` string value and all recorded Native JSON values. It cannot retroactively prove byte-for-byte HTTP wire serialization that TC4-2 never captured. The immutable TC4-2 source artifact remains the authoritative original recorded serialization.

This limitation does not permit any semantic alteration of Native values.
