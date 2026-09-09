# TC4-1 — TC② Input Specification

Status: **TC4-1 fixed input requirements**

This document applies the common \`spec/INPUT_CONTRACT.md\` to TC② without adding TradingCursor strategy logic.

## 1. TC② accepted input

TC② accepts one prepared Market Input set representing a single symbol observation across:

- D1
- H4
- H1
- M15

Required top-level identity:

- \`input_set_id\`
- \`symbol\`
- \`observation_timestamp\`

Required per-timeframe identity:

- \`timeframe\`
- \`artifact_ref\`
- \`capture_timestamp\`
- \`source_id\`

The exact serialization remains unspecified in TC4-1.

## 2. Broker-specific symbols

TC② must accept the exact broker/source symbols used in current operation, including examples such as:

- \`GOLD#\`
- \`USDJPY#\`
- \`US100Cash#\`
- \`JP225Cash#\`

TC② must not infer or overwrite a broker-neutral mapping.

\`canonical_symbol\` may be supplied only as optional traceable metadata when a validated mapping exists.

## 3. Image acceptance conditions

Before TC② analysis begins, each supplied chart artifact must make it possible to identify and read:

- symbol;
- timeframe;
- price axis;
- candlesticks/bars;
- current-market vicinity.

An artifact that is materially blank, clipped, corrupted, obscured, or scrolled away from the current vicinity is not valid prepared input.

TC② does not operate MT4 to repair these conditions in TC4-1.

## 4. Four-timeframe set validation

The set is suitable for TC② only if:

- all four required timeframes exist;
- timeframe labels match their slots;
- all four symbols match;
- all four artifacts are bound to the same \`input_set_id\`;
- all four capture timestamps are traceable;
- all four sources are traceable;
- no unresolved evidence indicates stale/new artifact mixing.

No arbitrary capture-time difference threshold is introduced in TC4-1.

If set coherence cannot be established, the input must be rejected or held as invalid by a future Validator rather than silently guessed.

## 5. Input leakage prohibition

TC② common Market Input must not contain:

- NODA rules or NODA evaluation output;
- R01-R37 results;
- 大ダウ / 小ダウ / 際 / 先行局面 / 本格局面 / 最終局面 / BR annotations;
- prior TC recommendation or analysis output;
- Entry / SL / TP answer labels;
- future price outcome;
- realized trade outcome;
- lot / position size / monetary risk / account balance;
- execution or position-management instructions.

TradingCursor must be evaluated from its own analysis capability on the neutral observed market input.

## 6. Replay and comparison

A replay or NODA②-vs-TC② comparison must reference the same fixed \`input_set_id\` and exact same four artifacts.

If any of the four artifacts is replaced, regenerated, or recaptured, that comparison must use a new input-set identity/version rather than representing the changed set as unchanged.

## 7. Out of scope

TC4-1 does not:

- evaluate TradingCursor analysis quality;
- define Entry, SL, TP logic;
- define TCTradePlanRaw;
- finalize TradePlanState;
- implement Adapter or Normalizer;
- implement capture;
- implement sizing;
- implement execution;
- modify \`trade-plan-a\`.
