# TC4-2 Formal Observation Matrix

Run: `TC4-2-OANDA-XAUUSD-20260910-01`

Policy: `spec/QUESTION_CONTRACT.md`

Mapping safety:

```text
EXTRACT = YES
LIGHT NORMALIZATION = YES
INFERENCE = NO
```

## 1. Status matrix

| Question | 1D | 4h | 1h | 15m |
|---|---|---|---|---|
| Q1 Environment | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q2 Setup | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q3 Trigger | NOT_PROVIDED | NOT_PROVIDED | OBSERVED | NOT_PROVIDED |
| Q4 Entry | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q5 SL | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q6 TP | OBSERVED | OBSERVED | OBSERVED | OBSERVED |
| Q7 Wait / Invalidation | OBSERVED | OBSERVED | OBSERVED | OBSERVED |

## 2. 1D mapping

- Q1 Environment = OBSERVED
  - Raw reference: `futureAssumption.trend = bullish`; `priceMetrics.supportLevels`; `priceMetrics.resistanceLevels`; explicit momentum commentary.
- Q2 Setup = OBSERVED
  - Raw reference: explicit recommended long position / `potentialPosition.positionType = long` and bullish continuation description.
- Q3 Trigger = NOT_PROVIDED
  - Raw contains breakout/indicator commentary, but the trade is recommended at current price; no explicit pre-entry activation condition is stated. No Trigger is inferred.
- Q4 Entry = OBSERVED
  - Raw reference: `potentialPosition.positionType = long`, `entryPrice = 4395.73`.
- Q5 SL = OBSERVED
  - Raw reference: `stopLoss = 4350`.
- Q6 TP = OBSERVED
  - Raw reference: `takeProfits = [4445.512, 4497.389, 4550]`.
- Q7 = OBSERVED
  - Wait = NOT_PROVIDED.
  - Alternative/opposite scenario = OBSERVED: explicit condition if price fails to hold above EMA 20.

## 3. 4h mapping

- Q1 Environment = OBSERVED
  - Raw reference: bullish trend, support/resistance, consolidation and momentum commentary.
- Q2 Setup = OBSERVED
  - Raw explicitly says `potential bullish reversal setup`.
- Q3 Trigger = NOT_PROVIDED
  - Raw recommends current-price entry. MACD crossover/support commentary is not promoted to a pre-entry Trigger.
- Q4 Entry = OBSERVED
  - `positionType = long`, `entryPrice = 4396.385`.
- Q5 SL = OBSERVED
  - `stopLoss = 4370`; Raw explicitly ties it to below the lower Bollinger Band.
- Q6 TP = OBSERVED
  - `[4420, 4450, 4480]`.
- Q7 = OBSERVED
  - Wait = NOT_PROVIDED.
  - Invalidation/alternative = OBSERVED: Raw explicitly states a break below 4364.748 could invalidate the bullish setup and provides an alternative short condition.

## 4. 1h mapping

- Q1 Environment = OBSERVED
  - Raw explicitly describes consolidation, neutral momentum, support/resistance and `futureAssumption.trend = neutral`.
- Q2 Setup = OBSERVED
  - Raw explicitly discusses a breakout trade candidate but says it is not yet confirmed.
- Q3 Trigger = OBSERVED
  - Raw explicitly says to wait for a decisive break above 4428.296 with volume confirmation for a long, or below 4386.362 for a short.
- Q4 Entry = OBSERVED
  - `potentialPosition.positionType = long`, `entryPrice = 4428.296`.
- Q5 SL = OBSERVED
  - `stopLoss = 4405.199`.
- Q6 TP = OBSERVED
  - `[4445, 4460, 4480]`.
- Q7 = OBSERVED
  - Wait = OBSERVED: explicit conservative approach to wait for breakout confirmation.
  - Opposite scenario condition = OBSERVED: break below 4386.362 for a short.

## 5. 15m mapping

- Q1 Environment = OBSERVED
  - Raw explicitly describes bullish reversal context, support, resistance, RSI/MACD/EMA state and `futureAssumption.trend = bullish`.
- Q2 Setup = OBSERVED
  - Raw explicitly says `potential bullish reversal setup`.
- Q3 Trigger = NOT_PROVIDED
  - A possible pullback/retest is mentioned, but Raw suggests current-price long entry and does not require that retest as entry activation. No Trigger is inferred.
- Q4 Entry = OBSERVED
  - `positionType = long`, `entryPrice = 4395.965`.
- Q5 SL = OBSERVED
  - `stopLoss = 4383.895`; Raw explicitly describes it as below the lower Bollinger Band.
- Q6 TP = OBSERVED
  - `[4409.223, 4434.551, 4460]`.
- Q7 = OBSERVED
  - Wait = NOT_PROVIDED.
  - Invalidation/alternative = OBSERVED: break below 4383.895 could invalidate the setup; alternative short scenario explicitly provided.

## 6. Out-of-scope information

The initial 1h Raw explicitly says that position sizing should account for potential false breakouts.

Disposition:

```text
Raw = KEEP
Question mapping = EXCLUDE_OUT_OF_SCOPE
```

No lot, Position Size or monetary-risk decision is created by the mapper.

## 7. Live repeatability observation — 1h

Comparison: formal `raw_1h.json` vs `raw_1h_repeat_01.json`.

| Field/aspect | Formal 1h | Repeat 1h |
|---|---|---|
| positionType | long | long |
| trend | neutral | bullish |
| confidenceScore | 0.65 | 0.65 |
| entryPrice | 4428.296 | 4395.445 |
| stopLoss | 4405.199 | 4375 |
| takeProfits | 4445 / 4460 / 4480 | 4410 / 4425 / 4450 |
| patternDetected | Consolidation within Bollinger Bands | Bullish Reversal near Support with MACD Crossover |
| entry state/text | wait for decisive breakout confirmation | current-price long suggested |

Classification: `VALUE_VARIATION`.

No LONG/SHORT direction change occurred in this pair. Since both calls use live native data and have different timestamps, the observed differences are not attributed solely to model randomness.

## 8. No 4TF synthesis

The four formal TF responses are independent observations only. This matrix does not create a new multi-timeframe TradingCursor decision.
