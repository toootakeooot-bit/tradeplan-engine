# TC4-3 — TC Observable Decision Structure

Status: **TC4-3 baseline**

Repository: `toootakeooot-bit/tradeplan-engine`
Branch: `feature/tc-v1`
Start HEAD: `8575beef1181e06a4a4ab89d3935bb576a92049a`

## 1. Purpose

TC4-3 defines the **observable output structure** of TradingCursor from the TC4-2 formal Raw survey. It does not reconstruct or claim a hidden internal reasoning sequence.

```text
TradingCursor Native Raw
        ↓
Observable field / explicit text
        ↓
Traceable mapping
        ↓
Q1 Environment
Q2 Setup
Q3 Trigger
Q4 Entry
Q5 SL
Q6 TP
Q7 Wait / Invalidation
```

`Observable Mapping != TradingCursor internal reasoning`.

## 2. Primary evidence

Primary evidence is the TC4-2 formal run:

`fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/`

Files used:
- `raw_1D.json`
- `raw_4h.json`
- `raw_1h.json`
- `raw_15m.json`
- `raw_1h_repeat_01.json`
- `observation_matrix.md`

TC4-2P Pilot is not used as the primary basis.

## 3. Observed Raw layers

### 3.1 Outer run envelope

Observed outer fields:
- `status`
- `exchange`
- `symbol`
- `interval`
- `analysis`
- `model`
- `timestamp`

`analysis` is the original TradingCursor analysis payload preserved as a JSON string. TC4-3 treats this as the Raw payload container, not as a Common Question answer by itself.

### 3.2 Native structured content inside `analysis`

Observed:
- `potentialPosition`
  - `entryPrice`
  - `positionType`
  - `takeProfits`
  - `stopLoss`
- `indicatorReadings`
- `priceMetrics`
  - `supportLevels`
  - `current_price`
  - `resistanceLevels`
- `futureAssumption`
  - `trend`
  - `confidenceScore`
  - `patternDetected`
- `observations`
- `action_url`

`chartId` is **not an independent Raw field** in the formal fixtures. It is embedded as a query parameter in `action_url`. Extracting it may later be a LIGHT NORMALIZATION candidate, but TC4-3 does not promote it to an observed Raw field.

## 4. Q1 Environment

Primary direct source:
- `futureAssumption.trend`

Supporting native sources:
- `priceMetrics.supportLevels`
- `priceMetrics.current_price`
- `priceMetrics.resistanceLevels`
- `futureAssumption.patternDetected`
- explicit environment statements in `observations`
- `indicatorReadings` only as raw indicator data; indicator values are not independently converted into strategy meaning.

Rule:

`indicator value != strategy meaning`.

## 5. Q2 Setup

Primary source is explicit setup/candidate language in `observations`, such as observed phrases describing a potential bullish reversal setup or breakout trade candidate.

`futureAssumption.trend` alone is not sufficient to create a Setup.

`potentialPosition` may support the fact that a position candidate exists, but it does not by itself establish the semantic Setup classification.

## 6. Q3 Trigger

No dedicated structured Trigger field was observed.

Trigger is mapped only from explicit pre-entry activation/confirmation language in `observations`.

TC4-2 evidence:
- 1D: `NOT_PROVIDED`
- 4h: `NOT_PROVIDED`
- 1h: `OBSERVED`
- 15m: `NOT_PROVIDED`

The 1h Raw explicitly states waiting for a decisive break with confirmation before entry. By contrast, `patternDetected`, a breakout description, or a MACD crossover is not promoted to Trigger unless TradingCursor explicitly uses it as an entry-activation condition.

```text
Market observation != Setup != Trigger
```

## 7. Q4 Entry

Direct structured sources:
- `potentialPosition.positionType`
- `potentialPosition.entryPrice`

Explicit entry wording in `observations` may support or qualify the structured field.

The current mapping relationship is observational only; it does not finalize future `TradePlanState` or `TCTradePlanRaw` field names.

## 8. Q5 SL

Direct structured source:
- `potentialPosition.stopLoss`

Supporting source:
- explicit stop-loss rationale in `observations`
- explicit invalidation wording only when the text itself ties the statement to SL or strategy invalidation.

SL and scenario invalidation are related but are not assumed identical.

## 9. Q6 TP

Direct structured source:
- `potentialPosition.takeProfits`

Supporting source:
- explicit target rationale in `observations`

Only the targets actually present in Raw may be retained. Missing TP levels are not generated.

## 10. Q7 Wait / Invalidation

No dedicated structured Wait/Invalidation field was observed.

Primary source:
- explicit text in `observations`

Keep separate where evidence allows:
- Wait
- Invalidation
- Alternative Scenario

Rules:

```text
Alternative Scenario != current WAIT
SL != always identical to Scenario Invalidation
```

## 11. Candidate field-role classes

These are TC4-3 local classifications, not formal common enums.

### COMMON_QUESTION_SOURCE
Directly supplies a Common Question answer without strategic inference.

Observed candidates:
- `potentialPosition.positionType`
- `potentialPosition.entryPrice`
- `potentialPosition.stopLoss`
- `potentialPosition.takeProfits`
- `futureAssumption.trend`
- explicit qualifying segments of `observations`

### SUPPORTING_NATIVE_FIELD
Supports context or rationale but must not be promoted through inference.

Observed candidates:
- `priceMetrics.supportLevels`
- `priceMetrics.current_price`
- `priceMetrics.resistanceLevels`
- `indicatorReadings`
- `futureAssumption.patternDetected`
- non-direct contextual portions of `observations`

### TC_NATIVE_ONLY_CANDIDATE
Observed native information with retention value but no forced Q1-Q7 mapping.

Observed candidate:
- `futureAssumption.confidenceScore`

### RUN_METADATA
Observed execution/provenance information rather than strategy output.

- `status`
- `exchange`
- `symbol`
- `interval`
- `model`
- `timestamp`
- `action_url`

### OUT_OF_SCOPE_NATIVE_CONTENT
Native text that may remain in Raw but is outside ② authority.

Observed examples:
- position sizing advice
- monetary/risk-policy style guidance

Risk/reward wording remains `TBD` where it cannot be cleanly separated between strategy-side SL/TP explanation and common risk-policy responsibility.

## 12. Structured field vs free text

Structured fields are preferred as the direct source when they explicitly answer the Common Question. Explicit free text is required when the meaning is not represented structurally, especially Setup, Trigger, Wait and Invalidation.

This is a **candidate source preference**, not a conflict-resolution rule.

No unconditional priority is fixed because the TC4-2 sample is insufficient to define a safe resolution rule for future structured/text disagreement.

## 13. Raw reference principle

Every mapped answer must remain traceable to the exact Raw source.

Examples:

```text
Q4 Entry.direction
source = potentialPosition.positionType
raw_reference = raw_1h.json / analysis / potentialPosition / positionType
```

```text
Q3 Trigger
source = observations
raw_reference = raw_1h.json / analysis / observations
```

Exact JSON Pointer syntax is not finalized in TC4-3. Traceability is mandatory; serialization syntax is deferred to TC4-4.

## 14. Conflict handling

No general conflict-resolution algorithm is created in TC4-3.

The formal Raw contains places where prose and numeric indicator descriptions may merit later consistency validation, but TC4-3 does not score correctness and does not use those cases to invent a strategy-conflict resolution rule.

Therefore:

`conflict resolution = TBD`

## 15. Timeframe independence

1D, 4h, 1h and 15m are independent TradingCursor Native outputs.

Different timeframe judgments are not treated as contradictions merely because they differ.

TC4-3 does not generate:
- a combined TC direction;
- a combined TC Entry;
- a synthetic multi-timeframe TradePlan.

`timeframe synthesis = NO`.

## 16. Repeatability observation

The 1h repeat changed trend, entry, SL, TP, pattern and entry state while keeping LONG direction. Since both observations used live market data at different timestamps, TC4-3 records only:

`observable output may vary between live runs`.

It does not conclude that identical frozen input is unstable.

## 17. Mapping safety

- EXTRACT = YES
- LIGHT NORMALIZATION = YES
- INFERENCE = NO
- NODA rule injection = NO
- 4TF synthetic integration = NO

## 18. Scope boundary

TC4-3 does not define or implement:
- TradingCursor hidden reasoning sequence;
- NODA logic;
- TC strategy logic;
- TCTradePlanRaw formal JSON Schema;
- TradePlanState formal Schema;
- Adapter;
- Normalizer;
- Position Sizing;
- execution.

## 19. TC4-4 readiness

The observed output structure is sufficiently defined to begin TC4-4 Raw-retention/schema design, provided all unresolved items remain visible and no semantic gap is filled by inference.
