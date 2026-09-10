# TC4-6 State Semantics Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `d34c5d2019f28a70c9bd2dcbca4515e5de4b9245`

## Result

**PASS WITH NOTES**

TC4-6 defines provisional WAIT / INVALID-centered state semantics from explicit TradingCursor evidence without introducing a runtime evaluator, price-trigger engine, NODA rules, 4TF synthesis or execution authority.

## 1. Evidence reviewed

Primary:
- `tc/spec/TC4_5_PROVISIONAL_STATE_MAPPING.md`
- `tc/spec/TC4_5_MAPPING_MATRIX.md`
- `fixtures/tc4_5/TCTradePlanState_1h_provisional_example.json`
- `fixtures/tc4_5/TCTradePlanState_missing_trigger_example.json`
- `audit/TC4_5_MAPPING_AUDIT.md`

Supporting:
- `tc/schema/tc_tradeplan_raw.schema.json`
- `tc/spec/TC4_4_TCTRADEPLANRAW_SPEC.md`
- `spec/QUESTION_CONTRACT.md`
- `spec/TRADEPLAN_STATE.md`
- formal TC4-2 Raw where needed.

## 2. Provisional state model

Adopted for TC-side provisional semantics:
- `WAIT`
- `ACTIONABLE`
- `INVALID`
- `UNDETERMINED`

This is not a final Common TradePlanState enum. NODA② requirements remain unknown.

## 3. WAIT audit

Definition fixed: explicit Native current waiting / not-yet-confirmed / avoid-now / pending-confirmation wording supports `WAIT`.

The 1h formal case demonstrates:
- Entry direction present;
- Entry price present;
- SL present;
- TP present;
- explicit current WAIT evidence present.

Expected conclusion:

```text
entry.direction = LONG
trade_state = WAIT
```

Result: **PASS**.

This fixes:

```text
Entry + SL + TP present != current Entry permission
```

## 4. Trigger NOT_PROVIDED audit

The formal 4h case has:
- `Trigger = NOT_PROVIDED`;
- explicit Native wording recommending a long position with entry at current price.

TC4-6 does not convert missing Trigger into WAIT.

Expected provisional conclusion:

```text
trade_state = ACTIONABLE
```

where ACTIONABLE means explicit current-action recommendation only, not execution permission.

Result: **PASS**.

## 5. INVALID audit

TC4-6 separates:

```text
Invalidation Rule
!=
Current INVALID
```

The 4h Raw explicitly contains a future condition that could invalidate the bullish setup. It does not explicitly say that the setup is currently invalid.

Result:
- Invalidation Rule: **OBSERVED**;
- Current INVALID evidence: **NOT_OBSERVED**;
- state is not changed to INVALID from the rule alone.

Result: **PASS**.

Positive Current INVALID evidence was not observed in the formal TC4-2 Raw set reviewed. Therefore positive INVALID fixture validation remains **TBD / EVIDENCE LIMITED**.

## 6. current_price audit

No rule of this form was introduced:

```text
current_price < invalidation level
→ INVALID
```

`priceMetrics.current_price` is not used to synthesize current state.

Result: **PASS**.

## 7. SL / Invalidation audit

`Stop Loss` and `Scenario Invalidation` remain separate concepts.

The 4h evidence demonstrates different values/conditions, which reinforces the separation. Equal values in a future case would still not merge the concepts automatically.

Result: **PASS**.

## 8. Alternative Scenario audit

Alternative Scenario is kept as an alternative path and is not auto-equated with WAIT or INVALID.

Alternative-transition policy remains `TBD` because no sufficient Native evidence establishes a universal transition rule.

Result: **PASS**.

## 9. Axis separation audit

| Axis pair | Result |
|---|---|
| Entry direction / Trade State | SEPARATE |
| Environment / Trade State | SEPARATE |
| Setup / Trade State | SEPARATE |
| Alternative Scenario / WAIT | SEPARATE |
| Alternative Scenario / INVALID | SEPARATE |
| SL / Invalidation | SEPARATE |

A LONG candidate with WAIT is explicitly valid.

## 10. WAIT release evidence

TC4-6 may preserve an explicitly stated wait-release condition, such as decisive break + confirmation.

No runtime condition evaluation or WAIT-release transition is implemented.

Result: **PASS**.

## 11. UNDETERMINED semantics

`UNDETERMINED` is adopted provisionally for cases where current state cannot be concluded without inference or where unresolved same-axis current-state evidence conflicts.

It is separate from `NOT_PROVIDED`:
- `NOT_PROVIDED` = one Question lacks information;
- `UNDETERMINED` = overall trade state lacks sufficient evidence.

Result: **PASS**.

## 12. Structured/text conflict

Different axes are not conflicts. Example: structured LONG candidate + explicit WAIT may coexist.

A true same-axis conflict remains `TBD`; TC4-6 does not define `structured wins` or `text wins`.

Result: **PASS**.

## 13. State transition audit

State transitions are `PARTIAL`.

Defined:
- WAIT semantics;
- ACTIONABLE semantics;
- INVALID semantics;
- UNDETERMINED semantics;
- WAIT release-condition evidence concept;
- Invalidation Rule evidence concept.

Not defined as runtime transitions:
- WAIT -> ACTIONABLE automatic evaluation;
- any state -> INVALID automatic price evaluation;
- Alternative Scenario activation;
- conflict resolution;
- cross-timeframe transition/synthesis.

## 14. Semantic basis

Allowed local basis categories:
- `EXPLICIT_NATIVE_TEXT`
- `EXPLICIT_NATIVE_STRUCTURED_FIELD`
- `NOT_ENOUGH_EVIDENCE`

`INFERRED` is not allowed.

Result: **PASS**.

## 15. Timeframe audit

No 4TF state synthesis was introduced.

Each timeframe remains independent.

Result: **PASS**.

## 16. Risk / execution audit

Position Sizing, Lot, account risk, monetary risk amount and generic Risk Management advice are not used to derive WAIT / ACTIONABLE / INVALID.

`ACTIONABLE` does not authorize execution.

Result: **PASS**.

## 17. Fixtures created

- `fixtures/tc4_6/TCTradeState_1h_wait_example.json`
- `fixtures/tc4_6/TCTradeState_4h_current_entry_example.json`

The fixtures are semantics examples only and do not imply a final Common JSON Schema.

## 18. Hard Gate audit

| Gate | Result |
|---|---|
| Correct repository | PASS |
| Correct branch | PASS |
| Started from TC4-5 completed HEAD | PASS |
| TC4-5 provisional mapping used | PASS |
| Question Status / Trade State separated | PASS |
| WAIT defined | PASS |
| Current WAIT / future Trigger separated | PASS |
| Trigger NOT_PROVIDED auto-WAIT | NO |
| Entry existence auto-READY | NO |
| Entry/SL/TP + WAIT coexistence allowed | PASS |
| INVALID defined | PASS |
| Invalidation Rule / Current INVALID separated | PASS |
| rule-only auto-INVALID | NO |
| current_price-derived INVALID | NO |
| SL / Invalidation merged | NO |
| Alternative Scenario / WAIT merged | NO |
| Alternative Scenario / INVALID merged | NO |
| Direction / State merged | NO |
| Environment / State merged | NO |
| Setup / State merged | NO |
| WAIT release evidence organized | PASS |
| Invalidation rule evidence organized | PASS |
| missing Current INVALID evidence can remain TBD | PASS |
| structured/text conflict auto-resolved | NO |
| unobserved transition invented | NO |
| 4TF synthesis | NO |
| Position Size used for state | NO |
| Risk Amount added | NO |
| Lot added | NO |
| Execution added | NO |
| INFERENCE | NO |
| NODA rules added | NO |
| NODA② implemented | NO |
| final Common TradePlanState schema fixed | NO |
| production Normalizer implemented | NO |
| Adapter implemented | NO |
| runtime state evaluator implemented | NO |
| TCTradePlanRaw modified | NO |
| TC4-2 Raw modified | NO |
| `trade-plan-a` changed | NO |
| main merged | NO |

## 19. Notes / TBD

Remaining items:
- positive Current INVALID fixture/evidence;
- true same-axis structured/text conflict resolution;
- Alternative Scenario transition policy;
- runtime WAIT-release / invalidation-condition evaluator;
- final Common state names after NODA② review;
- whether ACTIONABLE survives as the final Common term;
- cross-timeframe state aggregation remains out of scope.

## 20. TC4-7 handoff

Fixed semantics suitable for regression:

1. 1h full plan + explicit wait -> `WAIT`.
2. LONG candidate and WAIT may coexist.
3. Trigger NOT_PROVIDED does not auto-WAIT.
4. 4h explicit current-price recommendation -> provisional `ACTIONABLE` when no current WAIT/INVALID conflict exists.
5. Invalidation Rule alone does not make current INVALID.
6. current_price is not compared by TC4-6 to synthesize INVALID.
7. Alternative Scenario remains separate.
8. SL and Invalidation remain separate.
9. ACTIONABLE is not execution authorization.
10. no 4TF synthesis.

TBD for TC4-7:
- positive INVALID recognition cannot be regression-proven until a real Native example exists;
- true same-axis conflict resolution;
- runtime transitions.

## 21. Verdict

**TC4-6 = PASS WITH NOTES**

The state-semantics contract is sufficient to proceed to fixed-fixture Mapping / State regression testing while keeping current-INVALID and conflict-resolution limitations explicit.

**TC4-7 readiness = GO**

No TC4-7 work is started by this audit.
