# TC4-8 Adapter Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `1beaaaa4414b20c651dbb69eb205b364af195ff9`

## Result

**PASS WITH NOTES**

TC4-8 defines the Adapter responsibility, request/output contract, Native Client boundary, raw-preservation requirement, failure boundary, and downstream separation without implementing production Adapter/Normalizer/State logic or changing TC4-7 regression expectations.

## 1. Evidence reviewed

Primary:
- `tc/spec/TC4_4_TCTRADEPLANRAW_SPEC.md`
- `tc/schema/tc_tradeplan_raw.schema.json`
- `tc/spec/TC4_5_PROVISIONAL_STATE_MAPPING.md`
- `tc/spec/TC4_6_WAIT_INVALID_SEMANTICS.md`
- `audit/TC4_7_REGRESSION_AUDIT.md`
- `tests/tc4_7/test_fixed_fixture_regression.py`
- `fixtures/tc4_7/EXPECTED_REGRESSION_MATRIX.md`

Native-interface source:
- `tc/spec/TC4_2P_OBSERVATION_METHOD.md`

The current exposed TradingCursor request boundary remains `exchange`, `symbol`, `interval`.

## 2. Adapter design decision

The design separates responsibilities conceptually:

```text
Native Client
= provider transport call

TC Adapter
= request translation + response preservation + wrapper identity + lossless parse + TCTradePlanRaw output
```

No production implementation is added in TC4-8.

## 3. Adapter input contract

Required conceptual input:
- `request_id`
- `source_run_id`
- `execution_order`
- `analysis_source`
- `analysis_symbol`
- `timeframe`

Native translation:

```text
analysis_source -> exchange
analysis_symbol -> symbol
D1  -> 1D
H4  -> 4h
H1  -> 1h
M15 -> 15m
```

Unsupported timeframe substitution is forbidden. Symbol auto-conversion is forbidden.

## 4. One call / timeframe / Raw record

Fixed:

```text
1 request
= 1 Native call
= 1 timeframe
= at most 1 preserved TCTradePlanRaw record
```

Four-timeframe orchestration is design-only and belongs above the core Adapter. No 4TF strategy synthesis is authorized.

## 5. Native Response First / Raw preservation

TCTradePlanRaw v1.0.0 requires `record_identity.source_raw_artifact`.

Therefore TC4-8 fixes this sequence:

```text
Native Response
→ Raw Preservation
→ stable artifact reference
→ lossless parse
→ TCTradePlanRaw v1.0.0
```

If preservation fails, the Adapter must not fabricate `source_raw_artifact` or emit an apparently valid TCTradePlanRaw record.

This requirement fits the existing TCTradePlanRaw schema. **Schema Change Required = NO**.

Runtime raw-store backend and URI/path syntax remain TBD.

## 6. Parse boundary

`analysis` parse is lossless only.

Allowed parse states remain:
- `PARSED`
- `NOT_PARSED`
- `PARSE_ERROR`

A parse failure after successful response preservation can still retain TCTradePlanRaw with Original Raw and `PARSE_ERROR`.

Parse does not map Entry/SL/TP, extract Trigger/WAIT, interpret indicators, or generate State.

## 7. Failure separation

TC4-8 separates:
- request validation;
- Native transport;
- Raw preservation;
- analysis parse;
- Raw output validation;
- downstream Mapping/State processing.

Infrastructure failures are not Trade States.

Explicitly forbidden:

```text
transport failure -> UNDETERMINED
transport failure -> WAIT
parse error -> WAIT
parse error -> INVALID
preservation failure -> Trade State
```

## 8. Retry

Adapter-owned automatic retry: **NONE for TC v1 design**.

Rationale: TradingCursor is a live-source request path; an implicit retry can observe a different market state. A later explicit retry is a new request/record and must not overwrite prior Raw.

Retry count/backoff/orchestration policy outside the Adapter remains TBD.

## 9. Identity

`request_id` and `record_id` are distinct.

TC4-8 keeps the TC4-4 Raw identity model and does not change fixture identity semantics.

Runtime implementation of ID generation remains TBD, but must:
- be unique;
- preserve run/execution provenance;
- never overwrite repeat attempts;
- remain compatible with `record_id + RFC 6901 JSON Pointer` references.

## 10. Unknown fields and derived chartId

Unknown Native fields: **PRESERVE**.

`chartId`: **DERIVED**, never represented as a Native standalone field unless a future actual Native response explicitly supplies one and is separately versioned/audited.

Current derivation remains from `parsed_analysis.action_url` according to TCTradePlanRaw v1.0.0.

## 11. TC4-5 / TC4-6 boundary audit

Adapter does not implement:
- Native `positionType` -> common Entry direction Mapping;
- Setup/Trigger text extraction;
- WAIT/ACTIONABLE/INVALID/UNDETERMINED semantics;
- structured/text conflict resolution.

Those remain downstream responsibilities.

## 12. TC4-7 regression protection

TC4-8 changes none of:
- `tests/tc4_7/`
- `fixtures/tc4_7/`
- `audit/TC4_7_TEST_OUTPUT.txt`

Adapter design explicitly preserves TCREG-01 through TCREG-20 invariants, especially:
- LONG + WAIT coexistence;
- Trigger NOT_PROVIDED != WAIT;
- Entry presence != automatic ACTIONABLE;
- Invalidation Rule != Current INVALID;
- ACTIONABLE != execution permission;
- no 4TF synthesis.

## 13. Files created

- `tc/spec/TC4_8_ADAPTER_DESIGN.md`
- `tc/spec/TC4_8_ADAPTER_CONTRACT.md`
- `tc/spec/TC4_8_ADAPTER_FAILURE_MATRIX.md`
- `audit/TC4_8_ADAPTER_AUDIT.md`

No Adapter stub is created because TC4-8 is design-only and executable behavior would be premature.

## 14. Hard Gate audit

| Gate | Result |
|---|---|
| Correct repository | PASS |
| Correct branch | PASS |
| Started from TC4-7 completed HEAD | PASS |
| TC4-7 regression used as baseline | PASS |
| Adapter responsibility defined | PASS |
| Adapter non-responsibility defined | PASS |
| Adapter separated from strategy decisions | PASS |
| Adapter Input Contract defined | PASS |
| analysis_source defined | PASS |
| analysis_symbol defined | PASS |
| timeframe mapping defined | PASS |
| exchange/symbol/interval dependency contained at Native boundary | PASS |
| one call = one timeframe maintained | PASS |
| 4TF strategy synthesis | NO |
| technical sequencing treated as internal reasoning | NO |
| Native Response First | PASS |
| Original Response preserved before parse | PASS |
| TCTradePlanRaw v1.0.0 output contract retained | PASS |
| analysis parse lossless only | PASS |
| parse and normalization separated | PASS |
| PARSE_ERROR can preserve Original Raw | PASS |
| transport and parse failure separated | PASS |
| transport failure converted to Trade State | NO |
| parse failure converted to Trade State | NO |
| unknown Native field dropped | NO |
| chartId treated as Native standalone | NO |
| chartId derived only | PASS |
| request_id / record_id separated | PASS |
| repeat overwrites prior record | NO |
| unsupported timeframe silently substituted | NO |
| symbol silently converted | NO |
| TC4-5 Mapping moved into Adapter | NO |
| TC4-6 State Semantics moved into Adapter | NO |
| Trigger generated | NO |
| WAIT generated | NO |
| INVALID generated | NO |
| ACTIONABLE generated | NO |
| Position Size generated | NO |
| Risk Amount generated | NO |
| Lot generated | NO |
| Execution generated | NO |
| NODA rules added | NO |
| 4TF Aggregator implemented | NO |
| production Normalizer implemented | NO |
| runtime State Evaluator implemented | NO |
| production Adapter implemented | NO |
| TC4-7 regression expectations changed | NO |
| source fixtures changed | NO |
| TCTradePlanRaw schema changed | NO |
| Common TradePlanState finalized | NO |
| `trade-plan-a` changed | NO |
| main merged | NO |

## 15. Schema change assessment

**Schema Change Required: NO**.

The existing open Native objects and open `wrapper_metadata` are sufficient for the design. The required `source_raw_artifact` is handled by sequencing Raw Preservation before final wrapper emission.

If a future real Native response cannot be represented losslessly by TCTradePlanRaw v1.0.0, that future work must explicitly raise `SCHEMA CHANGE REQUIRED` rather than silently altering the schema.

## 16. Notes / TBD

Remaining implementation-level TBDs:
- Native Client runtime technology and actual provider invocation mechanism;
- durable Raw storage backend;
- `source_raw_artifact` URI/path convention;
- concrete runtime request_id/record_id generator implementation;
- upper-layer 4TF batch orchestration implementation;
- operational logging sink/retention;
- explicit upper-layer retry policy if one is later required;
- implementation tests for transport/preservation/parse failures.

These do not block TC v1 specification freezing because responsibility and failure semantics are defined and no hidden strategy behavior is required.

## 17. TC4-9 handoff

TC4-9 may treat the following as fixed TC v1 design inputs:
- current Native request boundary: exchange/symbol/interval;
- explicit TC Adapter request contract;
- Native Client / Adapter responsibility separation;
- timeframe mapping D1/1D, H4/4h, H1/1h, M15/15m;
- one call / one timeframe / one Raw record;
- Native Response First and mandatory preservation before final wrapper emission;
- TCTradePlanRaw v1.0.0 unchanged;
- unknown Native fields preserved;
- chartId derived only;
- automatic Adapter retry none;
- transport/preservation/parse failures never converted to Trade State;
- Mapper and State Semantics remain downstream;
- TC4-7 regression invariants remain immutable.

## 18. Verdict

**TC4-8 = PASS WITH NOTES**

The Adapter boundary is sufficiently defined to proceed to TC v1 specification freezing. Remaining items are production implementation details rather than unresolved strategy semantics.

**TC4-9 readiness = GO**

No TC4-9 work is started by this audit.
