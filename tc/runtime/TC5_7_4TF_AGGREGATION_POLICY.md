# TC5-7 — 4TF Aggregation Policy

Status: **FIXED AS NON-STRATEGY AGGREGATION / COMBINED TRADE DECISION NOT DEFINED**

## 1. Purpose

TC5-7 defines how a complete D1/H4/H1/M15 TC Spot batch is collected into one runtime aggregate without creating strategy meaning that TradingCursor or TC4 did not provide.

TC4-3 and TC4-5 explicitly keep timeframe outputs independent and forbid synthetic multi-timeframe TradePlan generation. TC5-7 therefore defines aggregation as packaging/provenance, not strategy synthesis.

## 2. Preconditions

Aggregation requires exactly one result for each standard ENTRY_PRE timeframe:

```text
D1
H4
H1
M15
```

All four results must belong to the same logical runtime batch and canonical instrument. Missing or duplicated timeframe results make the batch `INCOMPLETE` or `INVALID_BATCH`; they do not create a Trade State.

## 3. Aggregate shape

Conceptual output:

```text
TC4TFAggregate
  batch_id
  canonical_symbol
  provider
  completeness
  timeframe_results
    D1
    H4
    H1
    M15
  derived_observation
    entry_directions
    trade_states
    direction_alignment
    state_alignment
  combined_trade_state
  execution_permission
```

`timeframe_results` retain each TC result and provenance independently.

## 4. Derived observation only

TC5-7 may derive mechanical cross-timeframe metadata that does not itself authorize or recommend a trade.

Allowed examples:

- set/list of observed entry directions;
- set/list of observed per-timeframe Trade States;
- whether all observed entry directions are identical;
- whether all observed Trade States are identical;
- whether one or more timeframe outcomes are unavailable.

These are labelled **derived runtime observations**, not TradingCursor Native facts and not strategy decisions.

Different timeframe judgments are called `DIVERGENT`, not `CONFLICT`, because TC4-3 states that different timeframe judgments are not contradictions merely because they differ.

## 5. Direction alignment

Allowed descriptive values:

```text
ALIGNED
DIVERGENT
INSUFFICIENT
```

Rules:

- `ALIGNED`: every available timeframe supplies an entry direction and all are the same normalized value;
- `DIVERGENT`: every required timeframe supplies an entry direction and at least two direction values differ;
- `INSUFFICIENT`: one or more required timeframe directions are absent/unavailable.

No one timeframe is given priority in TC5-7.

`ALIGNED` does not mean ACTIONABLE or execution-ready.

## 6. State alignment

Allowed descriptive values:

```text
ALIGNED
DIVERGENT
INSUFFICIENT
```

The same mechanical comparison applies to per-timeframe TC4-6 states (`WAIT`, `ACTIONABLE`, `INVALID`, `UNDETERMINED`).

Examples:

```text
D1=ACTIONABLE, H4=ACTIONABLE, H1=ACTIONABLE, M15=ACTIONABLE
-> state_alignment = ALIGNED
```

```text
D1=ACTIONABLE, H4=WAIT, H1=ACTIONABLE, M15=ACTIONABLE
-> state_alignment = DIVERGENT
```

The second example does not automatically become WAIT, ACTIONABLE, INVALID or UNDETERMINED at the combined level.

## 7. Combined trade state

TC5-7 does **not** define a synthetic combined Trade State.

Fixed output:

```text
combined_trade_state = NOT_DEFINED
```

Reason: TC4 contains no approved rule for weighting/prioritizing D1/H4/H1/M15, and inventing one here would add new strategy logic.

Any later combined decision rule requires separately authorized strategy work and must be clearly labelled as TC5 upper-runtime semantics, not TradingCursor Native evidence.

## 8. Execution boundary

TC5-7 always preserves:

```text
execution_permission = false
```

Even four aligned `ACTIONABLE` timeframe states do not create execution permission.

## 9. Failure boundary

Infrastructure/runtime failures remain outside Trade State.

Examples:

- missing M15 Native result;
- timeout;
- provider mapping failure;
- Adapter failure;
- duplicate timeframe result;
- symbol/batch mismatch.

These produce an aggregate/batch failure or incompleteness status. They must not be translated to WAIT, INVALID or UNDETERMINED.

## 10. No NODA / no external fill

TC5-7 must not:

- use NODA rules to reconcile divergence;
- use web/current-price analysis to fill a missing timeframe;
- substitute another interval for M15;
- infer a missing direction/state;
- generate Entry/SL/TP across timeframes.

## 11. Completion criterion

TC5-7 is complete when a four-timeframe batch can be losslessly packaged and mechanically described as complete/aligned/divergent/insufficient while preserving each timeframe result independently and without creating a combined trade recommendation.
