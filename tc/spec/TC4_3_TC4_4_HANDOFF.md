# TC4-3 → TC4-4 Handoff

Status: **ready for TC4-4 design; no schema finalized here**

## A. Raw complete-retention target

Preserve the original TradingCursor run envelope and original `analysis` string before any parsing or normalization.

Observed Raw envelope candidates for retention:
- `status`
- `exchange`
- `symbol`
- `interval`
- `analysis`
- `model`
- `timestamp`

Observed inner analysis content candidates:
- `potentialPosition`
- `indicatorReadings`
- `priceMetrics`
- `futureAssumption`
- `observations`
- `action_url`

## B. Run Metadata

Observed metadata candidates:
- `status`
- `exchange`
- `symbol`
- `interval`
- `model`
- `timestamp`
- `action_url`

`chartId` is not a standalone observed Raw field. It may be derived from `action_url` only if TC4-4 explicitly chooses such LIGHT NORMALIZATION. Do not represent it as original Raw.

## C. COMMON_QUESTION_SOURCE candidates

### Q1 Environment
- `futureAssumption.trend`
- explicit Environment segments of `observations`

### Q2 Setup
- explicit Setup / candidate segments of `observations`

### Q3 Trigger
- explicit pre-entry activation/confirmation segments of `observations`
- no dedicated structured Trigger field observed

### Q4 Entry
- `potentialPosition.positionType`
- `potentialPosition.entryPrice`

### Q5 SL
- `potentialPosition.stopLoss`
- explicit SL rationale text where present

### Q6 TP
- `potentialPosition.takeProfits`
- explicit TP rationale text where present

### Q7 Wait / Invalidation
- explicit Wait text in `observations`
- explicit Invalidation text in `observations`
- explicit Alternative Scenario text in `observations`

Keep Wait, Invalidation and Alternative Scenario semantically distinct.

## D. SUPPORTING_NATIVE_FIELD candidates

- `priceMetrics.supportLevels`
- `priceMetrics.current_price`
- `priceMetrics.resistanceLevels`
- `indicatorReadings`
- `futureAssumption.patternDetected`
- contextual portions of `observations`

Supporting fields must not be converted into missing strategy meaning through inference.

## E. TC_NATIVE_ONLY_CANDIDATE

Observed:
- `futureAssumption.confidenceScore`

Additional observed metadata such as `model` and `action_url` has retention value but should remain Run Metadata rather than strategy-native Question content.

## F. OUT_OF_SCOPE_NATIVE_CONTENT

Observed examples:
- position sizing advice
- generic risk-management policy language

Disposition:

```text
Raw retention = KEEP
Common Q1-Q7 adoption = EXCLUDE_OUT_OF_SCOPE
```

Risk/reward wording remains `TBD` when its responsibility cannot be separated cleanly from strategy-side SL/TP rationale.

## G. raw_reference requirements

Every mapped/normalized output must remain traceable to:
1. the exact formal Raw file/run;
2. the exact field or `observations` source;
3. the original unmodified Raw value/text.

TC4-4 may choose a concrete pointer/path syntax. TC4-3 does not finalize JSON Pointer or another serialization.

## H. Unresolved / TBD for TC4-4

TC4-4 must decide or explicitly defer:
- final schema name/version;
- required vs optional fields;
- field types and null/absence semantics;
- whether original `analysis` stays string-only, is parsed into a parallel structure, or both;
- exact raw-reference representation;
- whether derived `chartId` is retained separately;
- handling of future unknown Native fields;
- structured/text conflict representation;
- risk/reward boundary where ambiguous;
- preservation of Question status (`OBSERVED`, `NOT_PROVIDED`, `AMBIGUOUS`, `NOT_APPLICABLE`) without manufacturing missing data.

## Non-negotiable constraints carried forward

- Raw first, mapping second.
- EXTRACT = allowed.
- LIGHT NORMALIZATION = allowed.
- INFERENCE = forbidden.
- NODA rule injection = forbidden.
- Position Size remains outside ②.
- TF outputs remain independent unless a future TradingCursor-native MTF result is actually observed.
- TC4-4 must not claim TradingCursor hidden internal reasoning order.
