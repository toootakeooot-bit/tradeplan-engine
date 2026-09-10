# TC4-5 Mapping Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `c94ea9439739a2858f5b37762686468ad004faca`

## Result

**PASS WITH NOTES**

TC4-5 defines a safe provisional mapping contract from `TCTradePlanRaw` v1.0.0 into a provisional TradePlanState surface without finalizing the common schema or adding missing TradingCursor semantics.

## 1. Evidence reviewed

Primary:
- `tc/spec/TC4_4_TCTRADEPLANRAW_SPEC.md`
- `tc/schema/tc_tradeplan_raw.schema.json`
- `fixtures/tc4_4/TCTradePlanRaw_1h_example.json`
- `audit/TC4_4_RAW_SCHEMA_AUDIT.md`

Supporting semantic contracts:
- `spec/QUESTION_CONTRACT.md`
- `spec/TRADEPLAN_STATE.md`
- TC4-3 observable mapping documents.

The existing Common TradePlanState document was not modified and remains provisional.

## 2. Mapping policy

```text
EXTRACT = YES
LIGHT_NORMALIZATION = YES
INFERENCE = NO
```

Mapping types fixed for TC4-5:
- `DIRECT`
- `LIGHT_NORMALIZATION`
- `TEXT_EXTRACT`
- `NOT_MAPPED`
- `TBD`

These are TC4-5 mapping classifications, not a final Common schema enum.

## 3. Q1-Q7 audit

| Question | Mapping | Result |
|---|---|---|
| Q1 Environment | `futureAssumption.trend -> environment.direction`; other context deferred/supporting | PASS |
| Q2 Setup | explicit `observations` setup/candidate text only | PASS |
| Q3 Trigger | explicit pre-entry activation text only | PASS |
| Q4 Entry | `positionType`, `entryPrice` | PASS |
| Q5 SL | `stopLoss` | PASS |
| Q6 TP | `takeProfits[]` | PASS |
| Q7 Wait | explicit wait evidence only | PASS |
| Q7 Invalidation | explicit invalidation evidence only | PASS |
| Q7 Alternative Scenario | explicit alternative/opposite text only | PASS |

No trade-state consequence is assigned by this mapping audit.

## 4. 1h provisional example

Created:

`fixtures/tc4_5/TCTradePlanState_1h_provisional_example.json`

Source record:

`TC4-2-OANDA-XAUUSD-20260910-01:03`

Verified mappings:
- Environment: `neutral` from `futureAssumption.trend`;
- Setup: explicit breakout-trade candidate text;
- Trigger: explicit decisive-break + volume-confirmation text;
- Entry direction: Native `long` -> normalized `LONG`;
- Entry price: `4428.296`;
- SL: `4405.199`;
- TP: `[4445, 4460, 4480]`;
- Wait: explicit wait text;
- Invalidation: `NOT_PROVIDED` in this 1h example rather than inferred;
- Alternative Scenario: explicit short-side condition;
- Position Sizing text: excluded from provisional Common mapping.

Every mapped value/evidence is tied to the source `record_id` and a Raw JSON Pointer.

The fixture is explicitly marked `PROVISIONAL`; no final TradePlanState JSON Schema is implied.

## 5. Missing Trigger audit

Created:

`fixtures/tc4_5/TCTradePlanState_missing_trigger_example.json`

Evidence source:

`fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/raw_4h.json`

Result:

**PASS**

The 4h Raw includes MACD crossover/support commentary and a current-price Entry recommendation, but no explicit pre-entry activation requirement. Therefore:

```text
Q3 Trigger = NOT_PROVIDED
```

No Trigger is inferred from MACD, support, pattern or Entry existence. Missing Trigger does not prevent a provisional mapping record from existing.

This fixture is a static semantic mapping case and does not pretend that a separate persisted 4h TCTradePlanRaw wrapper fixture already exists.

## 6. Native / normalized traceability

The 1h example preserves both:
- Native `positionType = long`;
- normalized Entry direction `LONG`.

The Raw source remains traceable through:

```text
record_id + RFC 6901 JSON Pointer
```

Result: **PASS**.

## 7. Deferred/native-only content

| Content | TC4-5 disposition |
|---|---|
| `indicatorReadings` | NOT_MAPPED to provisional Common state |
| `priceMetrics` | TBD_COMMON_ADOPTION |
| `confidenceScore` | TC_NATIVE_ONLY_OR_TBD |
| `patternDetected` | TBD_COMMON_ADOPTION |
| Position Sizing | EXCLUDED_OUT_OF_SCOPE |
| Risk Amount / Lot | EXCLUDED_OUT_OF_SCOPE |
| Risk/Reward | TBD; not Common-mapped |

No TC-only field was promoted to a Common required field merely because TradingCursor provides it.

## 8. Semantic separation audit

| Boundary | Result |
|---|---|
| Environment bullish/neutral auto-converted to Entry direction | NO |
| Trend auto-creates Setup | NO |
| Indicator values auto-create strategy meaning | NO |
| Pattern label auto-creates Trigger | NO |
| SL auto-equals Invalidation | NO |
| Alternative Scenario auto-equals WAIT | NO |
| Missing Trigger treated as mapper failure | NO |
| Question availability status treated as trade state | NO |

## 9. Structured/text conflict

`conflict resolution = TBD`.

TC4-5 does not establish `structured wins` or `text wins`. No strategic conflict-resolution algorithm is implemented.

## 10. Timeframe audit

TC4-5 retains one-record/one-timeframe mapping independence.

- 1D: independent
- 4h: independent
- 1h: independent
- 15m: independent
- 4TF synthetic TradePlanState: **NO**

## 11. TC4-6 boundary

TC4-5 maps evidence only. It does not define:
- final WAIT condition;
- final INVALID condition;
- WAIT release;
- Entry-ready state;
- Setup-without-Trigger state consequence;
- SL-hit vs scenario invalidation semantics;
- Alternative Scenario transition.

These remain for TC4-6.

## 12. Hard Gate audit

| Gate | Result |
|---|---|
| Correct repository | PASS |
| Correct branch | PASS |
| Started from TC4-4 HEAD | PASS |
| TCTradePlanRaw v1.0.0 used as input baseline | PASS |
| TradePlanState remains provisional | PASS |
| Final Common State not fixed | PASS |
| Q1 mapping defined | PASS |
| Q2 mapping defined | PASS |
| Q3 mapping defined | PASS |
| Q4 mapping defined | PASS |
| Q5 mapping defined | PASS |
| Q6 mapping defined | PASS |
| Q7 Wait/Invalidation mapping defined | PASS |
| Trigger inference added | NO |
| Setup generated from trend | NO |
| SL auto-equaled to Invalidation | NO |
| Alternative Scenario conflated with WAIT | NO |
| Raw references retained | PASS |
| record_id retained | PASS |
| Native/normalized traceability | PASS |
| NOT_PROVIDED accepted | PASS |
| AMBIGUOUS remains supported by contract | PASS |
| indicator-derived strategy logic | NO |
| TC-native-only field forced Common | NO |
| Position Size Common mapping | NO |
| Risk Amount added | NO |
| Lot added | NO |
| Risk/Reward forced Common | NO |
| structured/text conflict auto-resolved | NO |
| 4TF synthesis | NO |
| TCTradePlanRaw modified | NO |
| TC4-2 Raw modified | NO |
| NODA rules added | NO |
| NODA② implemented | NO |
| WAIT/INVALID final logic implemented | NO |
| production Normalizer implemented | NO |
| Adapter implemented | NO |
| Position Sizing implemented | NO |
| Execution implemented | NO |
| `trade-plan-a` changed | NO |
| main merged | NO |

## 13. Notes / TBD

Remaining items:
- NODA② requirements before final Common TradePlanState;
- whether `priceMetrics` belongs in the final Common state;
- whether `confidenceScore` remains TC extension only;
- whether/how `patternDetected` is represented commonly;
- exact free-text span/offset reference if later required;
- structured/text conflict representation/resolution;
- Risk/Reward semantic boundary;
- production Mapper/Normalizer implementation;
- final WAIT/INVALID state semantics.

## 14. Verdict

**TC4-5 = PASS WITH NOTES**

The data-mapping contract is sufficiently defined to proceed to TC4-6 without inventing missing TradingCursor meaning or finalizing the Common schema around TC.

**TC4-6 readiness = GO**

No TC4-6 work is started by this audit.
