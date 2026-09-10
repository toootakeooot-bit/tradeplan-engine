# TC4-7 Regression Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `b12de3f8fbab9ef0e4ca9ad88ea04b359a758182`

## Result

**PASS WITH NOTES**

TC4-7 establishes a fixed-fixture regression baseline for TCTradePlanRaw preservation, TC4-5 provisional Mapping semantics, and TC4-6 provisional Trade State semantics. No TradingCursor re-run, production Mapper/Normalizer, runtime state evaluator, Adapter, NODA logic, 4TF synthesis or execution logic was introduced.

## 1. Evidence baseline

Reviewed and used:
- `fixtures/tc4_4/TCTradePlanRaw_1h_example.json`
- `fixtures/tc4_5/TCTradePlanState_1h_provisional_example.json`
- `fixtures/tc4_5/TCTradePlanState_missing_trigger_example.json`
- `fixtures/tc4_6/TCTradeState_1h_wait_example.json`
- `fixtures/tc4_6/TCTradeState_4h_current_entry_example.json`
- TC4-4 Raw schema/spec
- TC4-5 Mapping Contract
- TC4-6 WAIT / INVALID State Semantics

Existing source fixtures were not modified.

## 2. Test method

Harness:

`tests/tc4_7/test_fixed_fixture_regression.py`

Method:
- Python standard library only;
- load saved fixed fixtures;
- assert fixed Mapping / State invariants;
- emit deterministic canonical JSON;
- exit nonzero on any TESTABLE regression failure.

Repository-root command:

```text
python tests/tc4_7/test_fixed_fixture_regression.py
```

TradingCursor API call: **NO**.

The harness is regression-only test code, not a production Mapper, Normalizer, state evaluator or Adapter.

## 3. Test ID namespace

`TCREG-01` through `TCREG-20` are used to avoid collision with NODA R01-R37.

## 4. Testable results

```text
TESTABLE       20
PASS           20
FAIL            0
NOT_TESTABLE    5
```

All TESTABLE regression cases passed in the static harness dry-run.

| Case | Result |
|---|---|
| TCREG-01 1h full plan + explicit WAIT | PASS |
| TCREG-02 LONG + WAIT coexist | PASS |
| TCREG-03 Trigger NOT_PROVIDED != WAIT | PASS |
| TCREG-04 4h explicit current entry -> ACTIONABLE | PASS |
| TCREG-05 Entry presence != automatic ACTIONABLE | PASS |
| TCREG-06 Invalidation Rule observed | PASS |
| TCREG-07 Rule != Current INVALID | PASS |
| TCREG-08 no current_price-derived INVALID | PASS |
| TCREG-09 SL / Invalidation separate | PASS |
| TCREG-10 Alternative / WAIT separate | PASS |
| TCREG-11 Alternative / INVALID separate | PASS |
| TCREG-12 Environment / State separate | PASS |
| TCREG-13 Setup / State separate | PASS |
| TCREG-14 Position Size excluded from mapping/state | PASS |
| TCREG-15 indicator inference prohibited | PASS |
| TCREG-16 pattern inference prohibited | PASS |
| TCREG-17 Missing Trigger mapping remains valid | PASS |
| TCREG-18 Question Status / Trade State separate | PASS |
| TCREG-19 no 4TF synthesis | PASS |
| TCREG-20 ACTIONABLE != Execution Permission | PASS |

## 5. NOT_TESTABLE results

These remain deliberately unproven rather than fabricated:

- `NT01` Current INVALID positive recognition — real Native positive evidence unavailable.
- `NT02` true same-axis Structured/Text conflict resolution — real Native conflict evidence unavailable / policy TBD.
- `NT03` Alternative Scenario automatic transition — transition evidence unavailable.
- `NT04` WAIT-release runtime evaluation — outside TC4-7 scope.
- `NT05` Invalidation runtime evaluation — outside TC4-7 scope.

NOT_TESTABLE cases are not counted as PASS and do not independently cause FAIL.

## 6. Determinism

The same harness assertion logic was run twice against the same mirrored fixed fixture fields required by the harness.

Both canonical JSON outputs produced:

```text
e7d9cdeb3bc44796b15033af58daa419e256ea9b359b7b7b8fe7d111afdec802
```

Result: **DETERMINISM PASS**.

Scope note: this verifies deterministic behavior of the saved-fixture regression logic. It is not evidence that TradingCursor Native itself is deterministic. No live TradingCursor call was made.

Execution summary is preserved in:

`audit/TC4_7_TEST_OUTPUT.txt`

## 7. Core regression invariants confirmed

1. Full Entry/SL/TP candidate data may coexist with current `WAIT`.
2. `LONG` direction + `WAIT` state is valid and not a conflict.
3. Trigger `NOT_PROVIDED` does not imply WAIT.
4. Explicit current-price recommendation supports provisional `ACTIONABLE` under TC4-6 semantics.
5. Entry presence alone does not create ACTIONABLE.
6. Invalidation Rule is distinct from Current INVALID.
7. No current-price comparison creates INVALID.
8. SL and Scenario Invalidation remain separate.
9. Alternative Scenario remains separate from WAIT and INVALID.
10. Environment and Setup remain different axes from Trade State.
11. Position Sizing remains Raw-retained but excluded from mapping/state authority.
12. RSI/MACD/EMA/BB/VOL and `patternDetected` do not create new state semantics.
13. Missing Trigger does not invalidate the mapping record.
14. Question availability statuses remain separate from Trade State values.
15. No synthetic 4TF Trade State is created.
16. ACTIONABLE does not authorize execution.

## 8. Regression detected

**NO**.

No TESTABLE fixed semantic invariant diverged from the TC4-5 / TC4-6 baseline.

## 9. Specification change required

**NO**.

No mismatch requiring TC4-4, TC4-5 or TC4-6 correction was found.

## 10. Hard Gate audit

| Gate | Result |
|---|---|
| Correct repository | PASS |
| Correct branch | PASS |
| Started from TC4-6 HEAD | PASS |
| TradingCursor re-executed | NO |
| fixed saved fixtures only | PASS |
| TC4-4 Raw retention represented | PASS |
| TC4-5 Mapping represented | PASS |
| TC4-6 State Semantics represented | PASS |
| 1h WAIT regression | PASS |
| LONG + WAIT coexist | PASS |
| Missing Trigger regression | PASS |
| Trigger NOT_PROVIDED auto-WAIT | NO |
| 4h current-entry regression | PASS |
| ACTIONABLE grants execution | NO |
| Entry presence auto-ACTIONABLE | NO |
| Invalidation Rule regression | PASS |
| Rule-only Current INVALID | NO |
| current_price-derived INVALID | NO |
| SL / Invalidation merged | NO |
| Alternative / WAIT merged | NO |
| Alternative / INVALID merged | NO |
| Direction / State merged | NO |
| Environment / State merged | NO |
| Setup / State merged | NO |
| Position Size used for state | NO |
| indicator-derived state | NO |
| pattern-derived state | NO |
| Question Status / State merged | NO |
| 4TF synthesis | NO |
| artificial Current INVALID formal PASS | NO |
| artificial conflict resolution | NO |
| unobserved transition invented | NO |
| TESTABLE / NOT_TESTABLE separated | PASS |
| deterministic fixed-fixture output | PASS |
| existing source fixtures modified | NO |
| production Mapper implemented | NO |
| production Normalizer implemented | NO |
| runtime evaluator implemented | NO |
| Adapter implemented | NO |
| NODA rules added | NO |
| NODA② implemented | NO |
| final Common TradePlanState schema fixed | NO |
| Position Sizing implemented | NO |
| Execution implemented | NO |
| `trade-plan-a` changed | NO |
| main merged | NO |

## 11. Notes / limitations

- The executable harness has been dry-run locally against the connector-verified fixture fields consumed by the harness; no GitHub Actions or repository checkout runtime was available in this session. This is why the overall result is `PASS WITH NOTES` rather than overstating an external CI pass.
- Positive Current INVALID remains untestable until genuine Native evidence exists.
- True same-axis Structured/Text conflict resolution remains TBD.
- Alternative Scenario automatic transition remains TBD.
- Runtime WAIT-release and invalidation-condition evaluation remain out of scope.
- No claim is made about TradingCursor Native determinism or future trade correctness.

## 12. TC4-8 handoff

TC4-8 may rely on the following fixed regression baseline:
- TCTradePlanRaw v1.0.0 retention boundaries;
- TC4-5 provisional Mapping Contract;
- TC4-6 provisional State Semantics;
- 20 `TCREG-*` invariants;
- fixed WAIT and ACTIONABLE fixtures;
- known NOT_TESTABLE cases;
- no 4TF synthesis;
- no execution authority in ACTIONABLE.

Adapter design must not cause regressions such as:

```text
WAIT -> ACTIONABLE without evidence
NOT_PROVIDED -> WAIT
Invalidation Rule -> Current INVALID
ACTIONABLE -> execution authorization
```

## 13. Verdict

**TC4-7 = PASS WITH NOTES**

All 20 TESTABLE fixed-fixture regressions pass; 5 evidence/runtime-dependent cases remain explicitly NOT_TESTABLE; no specification change is required.

**TC4-8 readiness = GO**

No TC4-8 work is started by this audit.
