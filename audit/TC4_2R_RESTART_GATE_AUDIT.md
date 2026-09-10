# TC4-2R Restart Gate Audit

Repository: `toootakeooot-bit/tradeplan-engine`

Branch: `feature/tc-v1`

TC4-2R start HEAD: `72cb2828fe54e88f84cba9953af3716650aaaaaf`

## 1. Change purpose

TC4-2R changes the development comparison principle for the TC Native Raw Survey from a strict same-artifact prerequisite to a Common Question / Output Contract, while preserving strict market-input comparison as a separate future Track COMP objective.

## 2. Common Question Contract audit

| Gate | Result |
|---|---|
| Q1 Environment defined | PASS |
| Q2 Setup defined | PASS |
| Q3 Trigger defined | PASS |
| Q4 Entry defined | PASS |
| Q5 SL defined | PASS |
| Q6 TP defined | PASS |
| Q7 Wait / Invalidation defined | PASS |
| NOT_PROVIDED explicitly allowed | PASS |
| AMBIGUOUS explicitly allowed | PASS |
| NOT_APPLICABLE explicitly allowed | PASS |
| OBSERVED explicitly defined | PASS |

## 3. Mapping-safety audit

| Rule | Result |
|---|---|
| EXTRACT allowed | PASS |
| LIGHT NORMALIZATION allowed | PASS |
| INFERENCE prohibited | PASS |
| Missing TC fields may remain NOT_PROVIDED | PASS |
| Raw must be preserved before mapping | PASS |
| Mapped output cannot be used to reconstruct/overwrite Raw | PASS |

## 4. Input / prompt policy audit

| Gate | Result |
|---|---|
| Identical natural-language prompt is not a TC Native Survey Hard Gate | PASS |
| Same fixed artifact is not a TC Native Survey Hard Gate | PASS |
| Actual TC source/symbol/timeframe must be disclosed | PASS |
| Same-artifact claims remain prohibited at LEVEL C | PASS |
| TC4-1 baseline is retained | PASS |
| TC4-2R addendum records the revised use | PASS |

## 5. Comparison-level audit

### LEVEL A — STRICT_SAME_ARTIFACT

Purpose: future strict NODA②-vs-TC② comparison.

TC Native Survey restart prerequisite: **NO**.

### LEVEL B — SAME_MARKET_OBSERVATION

Purpose: future conditional NODA②-vs-TC② comparison.

TC Native Survey restart prerequisite: **NO**.

### LEVEL C — SAME_QUESTION_NATIVE_SOURCE_SURVEY

Purpose: TC Native Raw survey, output discovery, mapping evidence, TCTradePlanRaw design evidence.

TC Native Survey restart prerequisite: **YES / selected mode**.

Formal TC4-2 restart mode:

```text
survey_mode = TC_NATIVE_RAW_SURVEY
comparison_level = LEVEL_C
```

## 6. TC4-2 new restart gate audit

TC4-2P Pilot already demonstrated that the current TradingCursor Native Interface can:

- execute Native Analysis;
- identify source/exchange;
- identify symbol;
- identify interval/timeframe;
- return Raw `analysis`;
- return model metadata;
- return analysis timestamp;
- expose action URL / chartId in Raw;
- execute D1 / H4 / H1 / M15 as separate calls.

TC4-2R additionally defines that:

- Raw and Question Contract records remain separate;
- absent answers are `NOT_PROVIDED`;
- ChatGPT strategic supplementation is prohibited;
- NODA rules are not injected into TC;
- Position Size advice may remain in Raw but is excluded from common ② answers;
- every survey run must be identified as LEVEL C rather than strict same-artifact comparison.

Result: **TC4-2 Native Raw Survey restart gate = SATISFIED**.

## 7. Responsibility audit

TC4-0 responsibility remains unchanged:

Environment → Setup → Trigger → Entry → SL → TP → Wait / Invalidation

No Position Sizing authority is added to ②.

No TC strategy logic is implemented.

No NODA strategy logic is implemented.

No Adapter or Normalizer is implemented.

No TCTradePlanRaw final schema is defined.

No TradePlanState final schema is defined.

## 8. Track separation

### Track TC

May proceed at LEVEL C.

### Track COMP

Remains separate and requires future LEVEL A/B methodology before fair comparative-performance claims.

Track COMP does not block TC4-2 Native Raw Survey.

## 9. TC4-3 audit position

Recommended rename:

**TC4-3 — TC出力判断構造定義 / TC Observable Decision Structure**

Reason: available evidence supports mapping observable Raw output to Q1-Q7, not reconstruction of TradingCursor hidden internal reasoning sequence.

TC4-2R itself does not start TC4-3.

## 10. Hard Gate final audit

| Hard Gate | Result |
|---|---|
| Repository is tradeplan-engine | PASS |
| Branch is feature/tc-v1 | PASS |
| Started from TC4-2P HEAD | PASS |
| Common Question Contract defined | PASS |
| Q1-Q7 defined | PASS |
| NOT_PROVIDED allowed | PASS |
| AMBIGUOUS allowed | PASS |
| EXTRACT vs INFERENCE separated | PASS |
| INFERENCE prohibited | PASS |
| Identical prompt not required | PASS |
| Same artifact removed from TC Native Survey Hard Gate | PASS |
| LEVEL A/B/C separated | PASS |
| LEVEL C restart conditions defined | PASS |
| Fair comparison separated from TC development | PASS |
| Position Sizing still out of scope | PASS |
| TC4-0 responsibility unchanged | PASS |
| NODA rules not injected | PASS |
| No new TC strategy logic | PASS |
| trade-plan-a changed | NO |
| main merged/changed by TC4-2R | NO |

## 11. Verdict

**TC4-2R = PASS**

**TC4-2 Native Raw Survey = GO**

**TC4-3 = HOLD until TC4-2 Native Raw Survey produces the required observation material.**
