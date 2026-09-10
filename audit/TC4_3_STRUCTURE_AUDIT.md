# TC4-3 Structure Audit

Repository: `toootakeooot-bit/tradeplan-engine`
Branch: `feature/tc-v1`
Start HEAD: `8575beef1181e06a4a4ab89d3935bb576a92049a`

## Result

**PASS WITH NOTES**

TC4-3 defines an observable output-to-question structure from TC4-2 formal Raw without claiming hidden internal reasoning order.

## 1. Evidence audit

Primary evidence:

`fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/`

Reviewed formal files:
- `raw_1D.json`
- `raw_4h.json`
- `raw_1h.json`
- `raw_15m.json`
- `raw_1h_repeat_01.json`
- `observation_matrix.md`

Pilot-only evidence was not used as the sole basis.

## 2. Q1-Q7 mapping audit

| Question | Result | Main evidence |
|---|---|---|
| Q1 Environment | PASS | `futureAssumption.trend`, explicit environment text, supporting `priceMetrics` / `indicatorReadings` |
| Q2 Setup | PASS | explicit setup/candidate wording in `observations` |
| Q3 Trigger | PASS | explicit pre-entry activation text only; structured Trigger field not observed |
| Q4 Entry | PASS | `potentialPosition.positionType`, `potentialPosition.entryPrice` |
| Q5 SL | PASS | `potentialPosition.stopLoss`, explicit rationale text where present |
| Q6 TP | PASS | `potentialPosition.takeProfits`, explicit rationale text where present |
| Q7 Wait / Invalidation | PASS | explicit `observations` segments; Wait/Invalidation/Alternative kept distinct |

## 3. Mapping safety audit

| Gate | Result |
|---|---|
| Field existence separated from semantic mapping | PASS |
| Structured fields separated from free text | PASS |
| Raw references required | PASS |
| Indicator values not converted into strategy meaning by mapper | PASS |
| Trigger not inferred from pattern/indicator commentary | PASS |
| `observations` not assigned wholesale to one Question | PASS |
| Missing semantic information not filled | PASS |
| EXTRACT only | PASS |
| LIGHT NORMALIZATION only | PASS |
| INFERENCE | NO |

## 4. Native field-role audit

Local candidate roles are defined without turning them into final common enums:
- `COMMON_QUESTION_SOURCE`
- `SUPPORTING_NATIVE_FIELD`
- `TC_NATIVE_ONLY_CANDIDATE`
- `RUN_METADATA`
- `OUT_OF_SCOPE_NATIVE_CONTENT`

These are organizational labels for TC4-3/TC4-4 handoff only.

## 5. Metadata audit

Observed run metadata:
- `status`
- `exchange`
- `symbol`
- `interval`
- `model`
- `timestamp`
- `action_url`

Important correction:

`chartId` is not a standalone observed Raw field. It is embedded in the query parameter of `action_url`. Any separate `chartId` value would be a derived LIGHT NORMALIZATION candidate, not original Raw.

## 6. Priority / conflict audit

A candidate non-conflict source preference is documented:
1. exact Native structured field;
2. explicit Native text;
3. supporting context.

This is not a fixed conflict-resolution algorithm.

The formal samples contain prose/numeric descriptions that may deserve later consistency validation, but TC4-3 does not assess correctness and does not derive a generic resolution policy from them.

Therefore:
- field priority = **CANDIDATE**
- conflict resolution = **TBD**

## 7. Timeframe audit

| Gate | Result |
|---|---|
| 1D independent | PASS |
| 4h independent | PASS |
| 1h independent | PASS |
| 15m independent | PASS |
| Cross-TF difference treated automatically as contradiction | NO |
| ChatGPT 4TF synthesis created | NO |

## 8. Repeatability audit

The formal 1h/repeat pair demonstrates observable live-run variation in trend, price values, pattern and entry state. Since input was live and timestamps differ, no statement is made that identical frozen input is unstable.

Result: **PASS — limitation preserved**.

## 9. Responsibility audit

| Boundary | Result |
|---|---|
| TC4-0 responsibility changed | NO |
| Position Size promoted into ② | NO |
| Risk-policy logic implemented | NO |
| TC internal strategy logic implemented | NO |
| NODA rules injected | NO |
| TradePlanState finalized | NO |
| TCTradePlanRaw formal Schema created | NO |
| Adapter implemented | NO |
| Normalizer implemented | NO |
| Execution logic implemented | NO |

Position-sizing text remains retained in Raw and classified as out-of-scope native content.

Risk/reward wording remains unresolved where it cannot be cleanly distinguished between strategy-side SL/TP explanation and common risk-policy responsibility.

## 10. Hard Gate

| Hard Gate | Result |
|---|---|
| Correct repository | PASS |
| Correct branch | PASS |
| Started from TC4-2 completed HEAD | PASS |
| Formal TC4-2 Raw used as primary evidence | PASS |
| Observable output structure only | PASS |
| Hidden reasoning sequence not inferred | PASS |
| Q1-Q7 organized | PASS |
| Trigger inference prohibited | PASS |
| Raw field existence vs mapping separated | PASS |
| Run metadata separated | PASS |
| Structured vs free text separated | PASS |
| Native-only field retained | PASS |
| Out-of-scope native content separated | PASS |
| Position Size not adopted | PASS |
| Indicator-derived strategy inference prohibited | PASS |
| `observations` segmented conceptually | PASS |
| Raw-reference principle defined | PASS |
| TF independence preserved | PASS |
| No 4TF synthesis | PASS |
| Live repeat not misrepresented as frozen repeatability | PASS |
| Unobserved conflict resolution not invented | PASS |
| NODA logic absent | PASS |
| TCTradePlanRaw final Schema absent | PASS |
| Adapter / Normalizer absent | PASS |
| `trade-plan-a` modified | NO |
| main merged | NO |

## 11. Notes / unresolved items

The following remain for TC4-4 or later:
- final required/optional field list;
- exact serialization and types;
- final raw-reference representation;
- whether derived `chartId` should be stored separately;
- structured/text conflict policy after sufficient evidence;
- risk/reward responsibility classification where ambiguous;
- handling of future Raw field additions/omissions;
- no multi-timeframe synthesis rule has been designed.

## 12. Verdict

**TC4-3 = PASS WITH NOTES**

The structure is sufficiently grounded to hand off to TC4-4 `TCTradePlanRaw`, provided the TBD items remain explicit and TC4-4 does not treat candidate classifications as already-final schema decisions.

**TC4-4 readiness = GO**

TC4-4 is not started by this audit.
