# TC4-5 Mapping Matrix

Status: **provisional mapping contract**

Input: `TCTradePlanRaw` v1.0.0

Rules:

```text
EXTRACT = YES
LIGHT_NORMALIZATION = YES
INFERENCE = NO
```

| TCTradePlanRaw source | Raw meaning | Question | Provisional target | Mapping type | Status handling | Raw reference | Inference required? | Scope | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `/parsed_analysis/futureAssumption/trend` | Native trend/bias label | Q1 Environment | `environment.direction` | DIRECT | absent -> NOT_PROVIDED | record + pointer | NO | provisional common | `bullish` is not auto-converted to LONG Entry |
| `/parsed_analysis/priceMetrics/supportLevels` | Native support levels | Q1 support | TBD | TBD | preserve in Raw | record + pointer | NO to retain; YES if reinterpreted | TBD | never rename as NODA line/際 |
| `/parsed_analysis/priceMetrics/current_price` | Native current price | Q1/Q4 context | TBD | TBD | preserve in Raw | record + pointer | NO | TBD | does not create Entry |
| `/parsed_analysis/priceMetrics/resistanceLevels` | Native resistance levels | Q1 support | TBD | TBD | preserve in Raw | record + pointer | NO to retain; YES if reinterpreted | TBD | never rename as NODA field |
| `/parsed_analysis/indicatorReadings` | Native indicator readings | Q1 support candidate | none | NOT_MAPPED | preserve in Raw | record + pointer | YES if converted into strategy meaning | TC-native Raw only | no RSI/EMA/BB/MACD strategy logic added |
| `/parsed_analysis/futureAssumption/patternDetected` | Native pattern label | Q1/Q2 support candidate | TBD | TBD | preserve in Raw | record + pointer | YES if promoted beyond explicit label | TBD | not automatically Trigger |
| `/parsed_analysis/futureAssumption/confidenceScore` | Native confidence value | none forced | none/TBD | NOT_MAPPED/TBD | preserve in Raw | record + pointer | NO | TC_NATIVE_ONLY_OR_TBD | do not make Common-required based on TC only |
| `/parsed_analysis/observations` explicit environment segment | Native explicit environment text | Q1 | environment evidence candidate | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common evidence | segment/span offset remains TBD |
| `/parsed_analysis/observations` explicit setup/candidate segment | Native explicit setup/candidate text | Q2 Setup | `setup.evidence` | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common | trend alone cannot create Setup |
| `/parsed_analysis/observations` explicit pre-entry activation segment | Native explicit Trigger condition | Q3 Trigger | `trigger.evidence` | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common | dedicated Trigger structured field not observed |
| `/parsed_analysis/potentialPosition/positionType` | Native proposed position direction | Q4 Entry | `entry.direction` | LIGHT_NORMALIZATION | absent -> NOT_PROVIDED | record + pointer | NO | provisional common | `long -> LONG`, `short -> SHORT` only representation normalization |
| `/parsed_analysis/potentialPosition/entryPrice` | Native proposed Entry price | Q4 Entry | `entry.price` | DIRECT | absent -> NOT_PROVIDED | record + pointer | NO | provisional common | Entry does not imply TRADE_READY |
| `/parsed_analysis/potentialPosition/stopLoss` | Native Stop Loss price | Q5 SL | `sl.price` | DIRECT | absent -> NOT_PROVIDED | record + pointer | NO | provisional common | not auto-equal to Invalidation |
| `/parsed_analysis/observations` explicit SL rationale | Native SL rationale | Q5 SL | `sl.evidence` candidate | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common evidence | explicit rationale only |
| `/parsed_analysis/potentialPosition/takeProfits` | Native TP target array | Q6 TP | `tp.targets[]` | DIRECT | absent -> NOT_PROVIDED | record + pointer | NO | provisional common | preserve observed count/order; no synthetic TP |
| `/parsed_analysis/observations` explicit TP rationale | Native TP rationale | Q6 TP | `tp.evidence` candidate | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common evidence | explicit rationale only |
| `/parsed_analysis/observations` explicit wait segment | Native wait wording | Q7 Wait | `wait.evidence` | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common evidence | not final WAIT state |
| `/parsed_analysis/observations` explicit invalidation segment | Native invalidation wording | Q7 Invalidation | `invalidation.evidence` | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common evidence | not automatically SL |
| `/parsed_analysis/observations` explicit opposite/alternative condition | Native opposite scenario wording | Q7 Alternative Scenario | `alternative_scenario.evidence` | TEXT_EXTRACT | absent -> NOT_PROVIDED | record + observations pointer | NO | provisional common evidence | does not imply current WAIT |
| `/parsed_analysis/observations` position-sizing wording | Native sizing advice | none | none | NOT_MAPPED | keep Raw; exclude mapping | record + observations pointer | NO | OUT_OF_SCOPE | no Position Size authority in ② |
| `/parsed_analysis/observations` generic risk policy | Native risk wording | none | none | NOT_MAPPED | keep Raw; exclude mapping | record + observations pointer | NO | OUT_OF_SCOPE | risk policy outside ② |
| `/parsed_analysis/observations` risk/reward wording | Native RR wording | none fixed | none/TBD | TBD | keep Raw | record + observations pointer | NO to retain | TBD | responsibility boundary unresolved |

## Question summary

| Question | Primary mapping source | TC4-5 result |
|---|---|---|
| Q1 Environment | `futureAssumption.trend`; explicit text optional evidence | MAPPABLE / PROVISIONAL |
| Q2 Setup | explicit `observations` segment | MAPPABLE WHEN EXPLICIT |
| Q3 Trigger | explicit pre-entry `observations` segment | MAPPABLE WHEN EXPLICIT; missing allowed |
| Q4 Entry | `potentialPosition.positionType`, `entryPrice` | MAPPABLE |
| Q5 SL | `potentialPosition.stopLoss` | MAPPABLE |
| Q6 TP | `potentialPosition.takeProfits` | MAPPABLE |
| Q7 Wait | explicit wait text | EVIDENCE MAPPABLE; state semantics deferred |
| Q7 Invalidation | explicit invalidation text | EVIDENCE MAPPABLE; state semantics deferred |
| Q7 Alternative Scenario | explicit opposite/alternative text | EVIDENCE MAPPABLE; transition semantics deferred |

## Conflict status

`structured/text conflict resolution = TBD`.

TC4-5 does not introduce `structured wins` or `text wins`.

## Common-state adoption status

- Direct Entry / SL / TP targets and Native Environment trend have provisional common targets.
- Setup / Trigger / Q7 concepts are represented through explicit evidence only.
- `indicatorReadings` is not mapped to common state in TC4-5.
- `priceMetrics`, `patternDetected`, `confidenceScore` remain deferred/TBD where NODA/common symmetry is unknown.
- Position Size / Lot / monetary risk / execution remain excluded.
