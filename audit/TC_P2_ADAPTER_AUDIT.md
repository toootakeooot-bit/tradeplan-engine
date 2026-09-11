# TC-P2 Adapter Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-prod-v1`  
Start HEAD: `dd93817033a9a4b969dc55064b664c430b4bc55f`  
Base specification completion HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## Result

**PASS WITH NOTES**

**TC-P3 readiness: GO**

TC-P2 implements only the production Adapter boundary defined by TC4-8 / TC-P0. It composes the TC-P1 Native Client with an injected `RawPreserver` protocol and emits TCTradePlanRaw v1.0.0 only after successful Native-response preservation. Concrete durable Raw Storage remains TC-P3 scope.

## 1. Implemented scope

Production code added:

- `tc/adapter/adapter.py`
- `tc/adapter/__init__.py`

Tests added:

- `tests/tc_prod/test_adapter.py`

The Adapter pipeline is:

```text
NativeRequest
  -> TC-P1 NativeClient
  -> Native response
  -> RawPreserver.preserve(...)
  -> stable source_raw_artifact
  -> lossless analysis JSON parse
  -> derived chartId extraction (if present)
  -> TCTradePlanRaw v1.0.0 output guard
  -> AdapterResult
```

No Question mapping or Trade State evaluation is implemented.

## 2. RawPreserver dependency boundary

P2 intentionally defines only a narrow injected preservation port:

```text
preserve(request, original_response) -> source_raw_artifact
```

P2 tests use an in-memory fake preserver. TC-P3 must provide the concrete durable implementation and rerun Adapter/storage integration tests.

The Adapter rejects preservation exceptions and missing/blank artifact references. No fabricated `source_raw_artifact` is emitted.

## 3. Original Raw First

The provider response is copied as a semantic JSON-value snapshot without whitelisting provider fields. The complete snapshot is handed to `RawPreserver` before `analysis` parsing occurs.

Only after preservation returns a stable artifact reference does the Adapter construct TCTradePlanRaw.

Unknown outer and inner Native fields are retained. The original `analysis` string is retained exactly as received at the Python string-value level.

## 4. Parse behavior

Implemented states remain exactly:

```text
PARSED
NOT_PARSED
PARSE_ERROR
```

Rules implemented:

- string `analysis` containing a JSON object -> `PARSED` + lossless `parsed_analysis`;
- missing or non-string `analysis` -> `NOT_PARSED`;
- invalid JSON string -> `PARSE_ERROR`;
- valid JSON whose root is not an object -> `PARSE_ERROR` because frozen `parsed_analysis` is an object.

A parse error does not delete the preserved Original Raw and does not become a Trade State.

## 5. chartId derivation

When `parsed_analysis.action_url` contains a non-empty `chartId` query parameter, P2 emits only:

```text
derived_metadata.chart_id.value
derived_metadata.chart_id.derived_from_pointer = /parsed_analysis/action_url
derived_metadata.chart_id.method = url_query_parameter:chartId
```

No standalone Native `chartId` field is invented.

## 6. Record identity

P2 implements the TC4-4-compatible runtime convention:

```text
record_id = source_run_id + ":" + two-digit execution_order
```

Example: `RUN-001:03`.

This is within the TC4-4 allowed zero/non-zero-padded execution-order token convention. Repeat attempts must arrive with a new execution identity; the Adapter itself does not deduplicate or overwrite.

## 7. Output validation

P2 adds a Python-standard-library schema-aligned output guard covering the frozen TCTradePlanRaw v1.0.0 constraints used by Adapter output, including:

- required top-level fields;
- closed wrapper top-level field set;
- record identity requirements;
- Native envelope known-field type checks while allowing unknown provider fields;
- known parsed Native field type checks while allowing unknown provider fields;
- derived chartId shape/constants;
- parse-status rules;
- PARSED conditional requirements;
- JSON compatibility / no NaN emission.

Authority remains `tc/schema/tc_tradeplan_raw.schema.json`; the Python guard does not replace or modify the schema.

If a preserved Native response parses successfully but violates a frozen known-field schema constraint, the Adapter raises `RAW_OUTPUT_VALIDATION` and includes the already-created `source_raw_artifact` in the error provenance. It does not silently coerce the Native value.

## 8. Failure stages

P2 operational failures are kept separate from Trade State:

```text
INPUT_VALIDATION
NATIVE_TRANSPORT
RAW_PRESERVATION
RAW_OUTPUT_VALIDATION
```

Provider/Adapter failures never produce WAIT, ACTIONABLE, INVALID, or UNDETERMINED.

Analysis parse failure is represented inside a successfully preserved Raw record as `parse_status=PARSE_ERROR`, consistent with TC4-4/TC4-8.

## 9. Retry / timeframe / symbol guardrails

Inherited P1 behavior remains unchanged:

- Adapter-owned automatic retry: NONE;
- one Adapter call invokes at most one Native call;
- unsupported timeframe is not substituted;
- analysis symbol is not auto-converted;
- no 4TF synthesis.

## 10. Test execution

Command used on an exact local mirror of the P1/P2 production files:

```text
python -m unittest -v tests.tc_prod.test_native_client tests.tc_prod.test_adapter
```

Result:

```text
P1 regression: 9 PASS / 0 FAIL
P2 Adapter:     12 PASS / 0 FAIL
Total:          21 PASS / 0 FAIL
```

This is local deterministic unit-test evidence, not GitHub Actions, live TradingCursor connectivity, or durable-storage evidence.

## 11. Frozen-invariant audit

| Gate | Result |
|---|---|
| correct repository / production branch | PASS |
| started from TC-P1 HEAD | PASS |
| frozen `feature/tc-v1` changed | NO |
| TCTradePlanRaw schema changed | NO |
| Original Raw preserved before analysis parse | PASS |
| stable source_raw_artifact required | PASS |
| artifact reference fabricated on preservation failure | NO |
| unknown Native outer fields dropped | NO |
| unknown parsed Native fields dropped | NO |
| original analysis string replaced | NO |
| PARSED / NOT_PARSED / PARSE_ERROR separated | PASS |
| parse failure deletes Raw | NO |
| chartId represented as Derived only | PASS |
| Adapter performs Q1-Q7 mapping | NO |
| Adapter performs Trade State evaluation | NO |
| Adapter performs indicator/pattern strategy inference | NO |
| provider/Adapter failure converted to Trade State | NO |
| automatic retry added | NO |
| symbol auto-conversion added | NO |
| 4TF synthesis added | NO |
| Position Sizing / Risk / Lot / Execution added | NO |
| NODA logic added | NO |
| concrete durable Raw Storage implemented | NO |
| TC4-7 expected results changed | NO |
| Trade Plan A changed | NO |
| A connected to TC | NO |
| main merged | NO |
| P1 regression tests | 9 PASS / 0 FAIL |
| P2 tests | 12 PASS / 0 FAIL |

## 12. TCREG / schema / Common impact

TCREG impact: **NONE EXPECTED / semantic baseline unchanged**. P2 is upstream of Mapping and State Semantics and does not alter TC4-7 fixtures or expected results.

TCTradePlanRaw schema impact: **NONE**.

Common/NODA impact: **NONE**.

Trade Plan A impact: **NONE**.

## 13. Notes

### N-01 — concrete durable Raw Storage remains P3

The `RawPreserver` protocol is production code, but P2 uses only a fake/in-memory implementation for tests. Atomic durable storage, no-overwrite publication, path/reference convention, read-back verification, and failure-injection against a real filesystem remain P3 work.

### N-02 — schema validation implementation

The P2 Python output guard is intentionally standard-library-only and mirrors the frozen constraints needed for emitted records. The JSON Schema file remains authoritative. If later provider evidence exposes a mismatch that cannot be represented without changing the frozen schema, the correct action is `SCHEMA CHANGE REQUIRED`, not silent coercion.

### N-03 — live provider host binding remains deferred

As in P1, real TradingCursor host binding is not part of P2 because no approved direct runtime endpoint/credential contract is frozen. P2 tests use an injected deterministic executor.

These notes do not block P3.

## 14. Verdict

**TC-P2 = PASS WITH NOTES**

**TC-P3 = GO, but NOT STARTED.**

STOP here under the P0 work-package discipline.
