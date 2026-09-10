# TC4-2 — TradingCursor Raw Analysis Survey

Status: **PASS WITH NOTES**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Restart baseline: `be4835cabfa5d505d3c12d79c58c616f879ec0ac`

## 1. Survey mode

```text
survey_mode = TC_NATIVE_RAW_SURVEY
comparison_level = LEVEL_C
```

This survey observes TradingCursor Native output. It is not a LEVEL A/B NODA-vs-TC fair-performance comparison.

Historical note: the first TC4-2 attempt stopped as INSUFFICIENT OBSERVATION. TC4-2P established actual interface capability and TC4-2R authorized LEVEL C restart under the Common Question Contract.

## 2. Formal target and run

Formal run: `TC4-2-OANDA-XAUUSD-20260910-01`

- source/exchange: `OANDA`
- symbol: `XAUUSD`
- timeframes: `1D`, `4h`, `1h`, `15m`
- Phase A: TradingCursor Native Default Analysis — executed
- Phase B: `NOT_SUPPORTED` by the currently confirmed interface
- four timeframes were invoked and retained independently
- no ChatGPT-created four-timeframe synthesis was produced

A separate `1h` repeat call was also captured as a LIVE REPEATABILITY OBSERVATION.

## 3. Raw acquisition result

| TF | Status | Timestamp UTC | Model | chartId |
|---|---|---|---|---|
| D1 / 1D | completed | 2026-09-10T10:13:39.412Z | qwen.qwen3-vl-235b-a22b | b03658c0-d0f8-431b-b819-87f841d54e7f |
| H4 / 4h | completed | 2026-09-10T10:14:05.800Z | qwen.qwen3-vl-235b-a22b | 914e5b19-6c30-4e33-93bd-ff0a4fc1df57 |
| H1 / 1h | completed | 2026-09-10T10:14:36.173Z | qwen.qwen3-vl-235b-a22b | db4c53c3-20c1-43e6-a2e8-d1f823a5f64a |
| M15 / 15m | completed | 2026-09-10T10:15:01.090Z | qwen.qwen3-vl-235b-a22b | 37a6052b-8def-4837-8793-8006966c03af |
| H1 repeat / 1h | completed | 2026-09-10T10:15:30.706Z | qwen.qwen3-vl-235b-a22b | a53a8f2f-940b-4c51-826f-b1810303e45f |

Raw responses are retained under `fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/` before the Question mapping record.

## 4. Native Raw structure actually observed

The formal runs explicitly contained the following Raw structures/metadata:

- response status
- exchange/source
- symbol
- interval
- `analysis`
- model
- timestamp
- `potentialPosition`
- `indicatorReadings`
- `priceMetrics`
- `futureAssumption`
- `observations`
- `action_url`
- chartId embedded in the action URL

Observed recurring nested items include:

- `potentialPosition.entryPrice`
- `potentialPosition.positionType`
- `potentialPosition.takeProfits`
- `potentialPosition.stopLoss`
- RSI / EMA / Volume / Bollinger Bands / MACD readings
- support / current price / resistance metrics
- trend
- confidenceScore
- patternDetected
- natural-language observations / alternative scenario text

These are **TC_NATIVE_FIELD_CANDIDATE** observations only. TC4-2 does not finalize TCTradePlanRaw schema.

## 5. Common Question mapping

Mapping follows `spec/QUESTION_CONTRACT.md`:

- EXTRACT = YES
- LIGHT NORMALIZATION = YES
- INFERENCE = NO

### Per-timeframe result

| Question | 1D | 4h | 1h | 15m |
|---|---|---|---|---|
| Q1 Environment | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q2 Setup | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q3 Trigger | NOT_PROVIDED | NOT_PROVIDED | OBSERVED | NOT_PROVIDED |
| Q4 Entry | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q5 SL | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q6 TP | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q7 Wait / Invalidation | OBSERVED | OBSERVED | OBSERVED | OBSERVED |

Details are in the formal run `observation_matrix.md`.

### Important Q3 boundary

The 1D/4h/15m Raw contains indicator, breakout, crossover or pullback language, but the mapper did not automatically reinterpret that text as a pre-entry Trigger where TradingCursor simultaneously recommended current-price entry. Those Q3 records remain `NOT_PROVIDED`.

The initial 1h Raw explicitly says to wait for a decisive break above a stated level with volume confirmation for a long, or a break below another level for a short. That qualifies as Q3 `OBSERVED` without inference.

## 6. Q7 split behavior

Q7 may contain independent sub-aspects.

Observed patterns include:

- explicit WAIT in the initial 1h run;
- explicit invalidation or alternative/opposite scenario conditions in other formal Raw responses.

An alternative scenario is not treated as proof that the current state is WAIT.

## 7. Out-of-scope content

The initial 1h Raw explicitly contains position-sizing advice in its natural-language analysis. This content is preserved in Raw but excluded from Q1-Q7 as `EXCLUDE_OUT_OF_SCOPE`.

Generic risk-management and risk/reward commentary was also observed in other Raw responses. TC4-0 still prohibits Position Sizing authority inside ②.

## 8. Four-timeframe integration

**NONE.**

TradingCursor was called once per timeframe. TC4-2 did not combine the four analyses into a new TradingCursor 'overall' decision and does not claim TradingCursor itself performed multi-timeframe integration.

## 9. Live repeatability observation

The 1h request was repeated once using the same request identity (`OANDA`, `XAUUSD`, `1h`). This is not exact-input replay because the native market source is live.

Observed between the two 1h responses:

- `positionType`: long -> long
- `futureAssumption.trend`: neutral -> bullish
- `entryPrice`: 4428.296 -> 4395.445
- `stopLoss`: 4405.199 -> 4375
- take-profit values changed
- `patternDetected`: consolidation -> bullish reversal near support with MACD crossover
- confidenceScore: 0.65 -> 0.65
- first run explicitly recommended waiting for breakout confirmation; repeat suggested current-price long entry

Classification: **VALUE_VARIATION**.

A LONG/SHORT `DECISION_VARIATION` was not observed in this pair. Because the source is live, the survey does not attribute the differences specifically to model randomness versus market-data change.

## 10. Quality/performance evaluation

Not performed.

No claim is made about whether any long/short direction, entry, SL, TP, indicator statement, numerical relation or future assumption is correct.

## 11. TC4-3 handoff evidence

The formal Raw is sufficient to support an observable output-structure work package. Examples of directly observed mappings:

- `futureAssumption.trend` -> Q1 Environment
- explicit bullish/bearish setup wording and/or proposed trade candidate -> Q2 Setup
- explicit wait-for-break/confirmation wording -> Q3 Trigger where present
- `potentialPosition.positionType` / `entryPrice` -> Q4 Entry
- `potentialPosition.stopLoss` -> Q5 SL
- `potentialPosition.takeProfits` -> Q6 TP
- explicit wait, invalidation, or alternative/opposite scenario condition -> Q7

This evidence does **not** prove TradingCursor hidden reasoning order.

Recommended next scope remains:

**TC4-3 — TC出力判断構造定義 / TC Observable Decision Structure**

TC4-3 GO is justified on observable-output evidence, but TC4-2 itself does not start it.

## 12. TC4-4 Raw-retention candidates

Candidate evidence from actual Raw:

- outer status / exchange / symbol / interval
- full unmodified `analysis`
- model
- timestamp
- action_url / chartId
- `potentialPosition`
- `indicatorReadings`
- `priceMetrics`
- `futureAssumption`
- `observations`
- run identity and execution order

No formal schema is created here.

## 13. Final result

**TC4-2 = PASS WITH NOTES**

Notes:

1. LEVEL C only; not a fair NODA-vs-TC performance comparison.
2. Phase B remains NOT_SUPPORTED.
3. Q3 is not consistently provided and is intentionally not backfilled.
4. Live repeatability showed value/state differences that cannot be isolated from market movement.
5. Four independent timeframe outputs were not synthesized.
