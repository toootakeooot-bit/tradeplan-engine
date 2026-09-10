# TC4-3 Field Mapping Matrix

Status: **candidate mapping based on TC4-2 formal Raw**
Primary Run: `TC4-2-OANDA-XAUUSD-20260910-01`

The role labels below are TC4-3 local candidates, not final schema enums.

| Raw field / source | Observed TF | Native meaning | Question mapping | Mapping status | Role | Inference required? | TC4-4 retention candidate? | Notes |
|---|---|---|---|---|---|---|---|---|
| `status` | 1D/4h/1h/15m/repeat | execution status | none | observed | RUN_METADATA | NO | YES | not strategy output |
| `exchange` | all | analysis source/exchange | none | observed | RUN_METADATA | NO | YES | OANDA in formal run |
| `symbol` | all | analysis symbol | none | observed | RUN_METADATA | NO | YES | XAUUSD |
| `interval` | all | requested timeframe | none | observed | RUN_METADATA | NO | YES | independent per TF |
| `model` | all | model identifier | none | observed | RUN_METADATA | NO | YES | not Q1-Q7 |
| `timestamp` | all | analysis timestamp | none | observed | RUN_METADATA | NO | YES | UTC-formatted value observed |
| `analysis` | all | Raw analysis payload container encoded as JSON string | none directly | observed | RAW_CONTAINER | NO | YES | preserve original before any parse/mapping |
| `potentialPosition.positionType` | all | proposed position direction | Q4 Entry | DIRECT | COMMON_QUESTION_SOURCE | NO | YES | long in formal four TF |
| `potentialPosition.entryPrice` | all | proposed entry price | Q4 Entry | DIRECT | COMMON_QUESTION_SOURCE | NO | YES | structured source |
| `potentialPosition.stopLoss` | all | proposed stop-loss price | Q5 SL | DIRECT | COMMON_QUESTION_SOURCE | NO | YES | rationale may come from text |
| `potentialPosition.takeProfits` | all | proposed target list | Q6 TP | DIRECT | COMMON_QUESTION_SOURCE | NO | YES | preserve only observed count |
| `futureAssumption.trend` | all | native trend/bias label | Q1 Environment | DIRECT | COMMON_QUESTION_SOURCE | NO | YES | does not itself create Setup |
| `futureAssumption.confidenceScore` | all | native confidence value | none forced | NATIVE_ONLY | TC_NATIVE_ONLY_CANDIDATE | NO | YES | no forced Q1-Q7 home |
| `futureAssumption.patternDetected` | all | native pattern label | Q1/Q2 support only | SUPPORTING | SUPPORTING_NATIVE_FIELD | NO if retained as label; YES if promoted beyond explicit meaning | YES | not automatically Trigger |
| `priceMetrics.supportLevels` | all | support levels | Q1 Environment support | SUPPORTING | SUPPORTING_NATIVE_FIELD | NO | YES | explicit price context |
| `priceMetrics.current_price` | all | current price | Q1/Q4 context | SUPPORTING | SUPPORTING_NATIVE_FIELD | NO | YES | does not itself create Entry |
| `priceMetrics.resistanceLevels` | all | resistance levels | Q1 Environment support | SUPPORTING | SUPPORTING_NATIVE_FIELD | NO | YES | explicit price context |
| `indicatorReadings` | all | indicator names/values | Q1 support only when TC gives explicit interpretation | SUPPORTING | SUPPORTING_NATIVE_FIELD | YES if raw values are converted to strategy meaning by mapper | YES | values alone are not strategy meaning |
| `observations` — environment segments | all | explicit trend/range/momentum/level commentary | Q1 Environment | TEXTUAL_DIRECT / SUPPORTING | COMMON_QUESTION_SOURCE or SUPPORTING_NATIVE_FIELD by segment | NO | YES | segment-level reference required |
| `observations` — setup segments | all | explicit setup/candidate description | Q2 Setup | TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | trend alone is insufficient |
| `observations` — pre-entry activation segments | 1h formal | explicit wait/break/confirmation condition before entry | Q3 Trigger | TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | no dedicated structured Trigger field observed |
| `observations` — entry recommendation segments | all | explicit long/short/entry wording | Q4 Entry support | SUPPORTING/TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | structured `potentialPosition` remains direct source when aligned |
| `observations` — SL rationale | 4h/15m and others where explicit | reason/location for stop | Q5 SL | TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | do not infer absent rationale |
| `observations` — TP rationale | formal TFs where explicit | reason for targets | Q6 TP | TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | preserve explicit rationale only |
| `observations` — wait text | 1h formal | explicit wait state/condition | Q7 Wait | TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | absent on other formal TFs |
| `observations` — invalidation text | 4h/15m and others where explicit | setup/scenario invalidation condition | Q7 Invalidation | TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | not automatically identical to SL |
| `observations` — alternative scenario | formal TFs | opposite/alternative scenario condition | Q7 Alternative Scenario | TEXTUAL_DIRECT | COMMON_QUESTION_SOURCE | NO | YES | does not imply current WAIT |
| `observations` — position sizing advice | 1h formal | sizing/risk advice | none | OUT_OF_SCOPE | OUT_OF_SCOPE_NATIVE_CONTENT | NO | YES in Raw only | exclude from common ② answer |
| `observations` — generic risk management / risk-reward wording | observed | risk commentary | none fixed | AMBIGUOUS/TBD | OUT_OF_SCOPE or TC_NATIVE_FIELD_CANDIDATE | NO to retain; YES to assign strategy meaning | YES in Raw | boundary may depend on whether wording is strategy-side SL/TP rationale vs risk policy |
| `action_url` | all | link to TC chart/result | none | observed | RUN_METADATA | NO | YES | `chartId` is embedded in this URL |

## chartId handling

`chartId` was not observed as a standalone Raw field. It appears only inside the `action_url` query string. Therefore:

- Raw field inventory: `chartId` = **NO standalone field**;
- derivation from `action_url`: **LIGHT NORMALIZATION candidate**;
- TC4-3 does not make derived `chartId` required or canonical.

## Question-source summary

| Question | Main observable source |
|---|---|
| Q1 Environment | `futureAssumption.trend` + explicit environment text; price/indicator fields supporting |
| Q2 Setup | explicit setup/candidate text in `observations` |
| Q3 Trigger | explicit pre-entry activation/confirmation text in `observations`; no structured Trigger field observed |
| Q4 Entry | `potentialPosition.positionType`, `potentialPosition.entryPrice` |
| Q5 SL | `potentialPosition.stopLoss` + explicit rationale text where present |
| Q6 TP | `potentialPosition.takeProfits` + explicit rationale text where present |
| Q7 Wait / Invalidation | explicit `observations` segments; keep Wait, Invalidation, Alternative Scenario distinct |

## Priority and conflict status

Candidate source preference when no contradiction is present:

1. explicit Native structured field for the exact requested concept;
2. explicit Native text for semantic concepts not encoded structurally or for rationale/qualification;
3. supporting fields only as context.

This is **CANDIDATE**, not a fixed conflict-resolution rule.

`conflict resolution = TBD` because the formal sample is not sufficient to establish a safe generic rule for future structured/text disagreement.
