# TC Engine v1 Baseline Manifest

Status: **TC4-9 baseline manifest / pending freeze attestation**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`

## 1. Baseline identity

Baseline name: **TC Engine v1**  
Baseline kind: **SPECIFICATION**  
Production status: **NOT PRODUCTION READY**

Freeze Point SHA: `PENDING_ATTESTATION`  
Frozen date/time: `PENDING_ATTESTATION`

Git note: a commit cannot contain its own SHA as file content without circular self-reference. TC4-9 therefore uses a two-step freeze procedure:

1. create the immutable specification-baseline commit containing the authoritative TC v1 documents;
2. create a direct child attestation commit that records the exact baseline commit SHA and timestamp in this Manifest and the Freeze Audit.

The **Freeze Point** is the specification-baseline commit from step 1. The branch completion HEAD is the attestation commit from step 2. No specification semantics may change in step 2.

## 2. Status vocabulary

- `FIXED`: part of TC v1 and change-controlled after freeze.
- `PROVISIONAL`: used by TC v1 but subject to NODA/Common review.
- `TBD`: unresolved and not silently completed by the freeze.
- `NOT_TESTABLE`: evidence/runtime-dependent item not formally proven.

## 3. Authoritative baseline artifacts

| Artifact | Origin | Status | Role / version | Change requirement |
|---|---|---|---|---|
| `spec/RESPONSIBILITY.md` | TC4-0 | FIXED | TradePlan Engine responsibility boundary | explicit TC v1 change review |
| `tc/spec/TC4_0_RESPONSIBILITY.md` | TC4-0 | FIXED | TC responsibility detail | explicit TC v1 change review |
| `spec/INPUT_CONTRACT.md` | TC4-1 | FIXED | Market input contract; strict artifact comparison retained separately | explicit change review |
| `tc/spec/TC4_1_INPUT_SPEC.md` | TC4-1 | FIXED | TC input specification | explicit change review |
| `spec/QUESTION_CONTRACT.md` | TC4-2R | FIXED | Q1-Q7 common question surface | Common impact review required |
| `spec/INPUT_CONTRACT_TC4_2R_ADDENDUM.md` | TC4-2R | FIXED | LEVEL C survey clarification | explicit change review |
| `tc/spec/TC4_2P_OBSERVATION_METHOD.md` | TC4-2P | FIXED | verified Native observation/capability method | re-audit if provider interface changes |
| `tc/spec/TC4_2R_COMMON_QUESTION_POLICY.md` | TC4-2R | FIXED | same-question / native-source survey policy | explicit change review |
| `tc/spec/TC4_2_RAW_ANALYSIS_SURVEY.md` | TC4-2 | FIXED EVIDENCE | formal Native Raw survey record | immutable evidence policy |
| `fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/` | TC4-2 | FIXED EVIDENCE | formal Raw fixtures | do not rewrite; add new evidence separately |
| `tc/spec/TC4_3_OBSERVABLE_DECISION_STRUCTURE.md` | TC4-3 | FIXED | observable output structure | explicit change review |
| `tc/spec/TC4_3_FIELD_MAPPING_MATRIX.md` | TC4-3 | FIXED | Native-field role mapping | explicit change review |
| `tc/spec/TC4_4_TCTRADEPLANRAW_SPEC.md` | TC4-4 | FIXED | TCTradePlanRaw spec | schema/version review required |
| `tc/schema/tc_tradeplan_raw.schema.json` | TC4-4 | FIXED | `TCTradePlanRaw v1.0.0` | schema compatibility + version review |
| `fixtures/tc4_4/TCTradePlanRaw_1h_example.json` | TC4-4 | FIXED FIXTURE | Raw wrapper example | fixture change review |
| `tc/spec/TC4_5_PROVISIONAL_STATE_MAPPING.md` | TC4-5 | PROVISIONAL | TC -> Common mapping targets | NODA/Common review required |
| `tc/spec/TC4_5_MAPPING_MATRIX.md` | TC4-5 | PROVISIONAL | mapping matrix | NODA/Common review required |
| `tc/spec/TC4_6_WAIT_INVALID_SEMANTICS.md` | TC4-6 | PROVISIONAL | TC state semantics | NODA/Common review required |
| `tc/spec/TC4_6_STATE_DECISION_MATRIX.md` | TC4-6 | PROVISIONAL | state-decision matrix | NODA/Common review required |
| `fixtures/tc4_6/` | TC4-6 | FIXED FIXTURE | WAIT/ACTIONABLE examples | fixture change review |
| `tc/spec/TC4_7_REGRESSION_TEST_PLAN.md` | TC4-7 | FIXED | regression contract | explicit change + regression review |
| `fixtures/tc4_7/EXPECTED_REGRESSION_MATRIX.md` | TC4-7 | FIXED | TCREG-01..20 golden semantic baseline | must not be rewritten to fit implementation |
| `tests/tc4_7/test_fixed_fixture_regression.py` | TC4-7 | FIXED TEST BASELINE | fixed-fixture harness | regression impact review |
| `audit/TC4_7_REGRESSION_AUDIT.md` | TC4-7 | FIXED AUDIT | 20 PASS / 0 FAIL / 5 NOT_TESTABLE | append/new audit rather than rewrite history |
| `tc/spec/TC4_8_ADAPTER_DESIGN.md` | TC4-8 | FIXED DESIGN | Adapter boundary | explicit change review |
| `tc/spec/TC4_8_ADAPTER_CONTRACT.md` | TC4-8 | FIXED DESIGN | Adapter request/output contract | explicit change review |
| `tc/spec/TC4_8_ADAPTER_FAILURE_MATRIX.md` | TC4-8 | FIXED DESIGN | infrastructure-failure boundary | explicit change review |
| `audit/TC4_8_ADAPTER_AUDIT.md` | TC4-8 | FIXED AUDIT | Adapter design audit | historical audit preserved |
| `spec/TRADEPLAN_STATE.md` | Common | PROVISIONAL | common interface, not final | NODA/Common review before finalization |
| `tc/spec/TC_V1_SPECIFICATION.md` | TC4-9 | FIXED | integrated TC v1 specification | TC v1 change policy |
| `tc/spec/TC_V1_CHANGE_POLICY.md` | TC4-9 | FIXED | post-freeze change control | explicit governance change |
| `tc/spec/TC_V1_BASELINE_MANIFEST.md` | TC4-9 | FIXED | this baseline manifest | attestation metadata may be updated only by freeze procedure |
| `audit/TC4_9_V1_FREEZE_AUDIT.md` | TC4-9 | FIXED AUDIT | final freeze audit | historical audit preserved |

## 4. Selected pre-freeze Git provenance

These selected blobs were verified before TC4-9 and provide high-value provenance. The Freeze Point commit remains the authoritative full-tree identity.

| Path | Blob SHA |
|---|---|
| `spec/RESPONSIBILITY.md` | `7249573c24030aa9dcb078a3d97e5f48e939f8ba` |
| `spec/QUESTION_CONTRACT.md` | `7eadbe1ff5bee5166346805ef85b04cd88c2db10` |
| `spec/TRADEPLAN_STATE.md` | `6d874e32a76baf637af004e369a03ba6fd043baa` |
| `tc/schema/tc_tradeplan_raw.schema.json` | `7a780a628cbf7f8d29255fbc4ed6f8a875b24888` |
| `tc/spec/TC4_5_PROVISIONAL_STATE_MAPPING.md` | `55f9f780ae0ad1069e7f8607bc5afd3a073f4cfa` |
| `tc/spec/TC4_6_WAIT_INVALID_SEMANTICS.md` | `2ce359f0fc5de74fbb2689229fadfae41449ba55` |
| `fixtures/tc4_7/EXPECTED_REGRESSION_MATRIX.md` | `a2ea814337d26370949ed97d9deb773062f17682` |
| `audit/TC4_8_ADAPTER_AUDIT.md` | `dfda643a546d2287dd7d414213f6566bfbfef26a` |

## 5. FIXED TC v1 facts

- responsibility boundary: Environment -> Setup -> Trigger -> Entry -> SL -> TP -> Wait/Invalidation;
- current callable Native boundary: exchange/symbol/interval;
- Q1-Q7 Question Contract relation;
- `EXTRACT=YES`, `LIGHT_NORMALIZATION=YES`, `INFERENCE=NO`;
- TCTradePlanRaw v1.0.0 and Original Raw First;
- unknown Native fields preserved;
- chartId derived from action_url, not presented as Native standalone field;
- one Native call / one timeframe / one Raw record;
- repeat requests create new records;
- no silent symbol conversion;
- no unsupported-timeframe substitution;
- Adapter does not own Mapping/State/Execution;
- Adapter automatic retry = NONE;
- infrastructure failure is not Trade State;
- no TC-side 4TF strategy synthesis;
- TCREG-01..20 regression baseline fixed at 20 PASS / 0 FAIL.

## 6. PROVISIONAL TC v1 items

- TC -> Common TradePlanState mapping target names and common adoption;
- TC-side state names `WAIT`, `ACTIONABLE`, `INVALID`, `UNDETERMINED`;
- final Common representation of TC-native fields;
- `spec/TRADEPLAN_STATE.md` shape.

These require later NODA/Common review.

## 7. TBD items

- durable Raw storage backend;
- `source_raw_artifact` URI/path convention;
- runtime request_id/record_id generator implementation;
- upper-layer 4TF request orchestration;
- operational logging sink/retention;
- retry policy above Adapter;
- true same-axis Structured/Text conflict resolution;
- Risk/Reward responsibility boundary;
- Current INVALID positive behavior verification;
- Alternative Scenario state transition;
- WAIT-release runtime evaluation;
- Invalidation runtime evaluation;
- production implementation technology.

## 8. NOT_TESTABLE items

- NT01 Current INVALID positive recognition;
- NT02 true same-axis Structured/Text conflict resolution;
- NT03 Alternative Scenario automatic transition;
- NT04 WAIT-release runtime evaluation;
- NT05 Invalidation runtime evaluation.

These are not counted as PASS.

## 9. Regression baseline

```text
TCREG TESTABLE 20
PASS           20
FAIL            0
NOT_TESTABLE    5
```

The regression baseline validates fixed saved-fixture semantics only. It is not a market-performance benchmark or proof of live TradingCursor determinism.

## 10. Freeze interpretation

`TC Engine v1 FROZEN` means the TC-side **specification baseline** is frozen under change control.

It does not mean:
- final Common TradePlanState;
- production implementation complete;
- NODA implementation complete;
- NODA-vs-TC performance comparison complete;
- main branch merge complete.
