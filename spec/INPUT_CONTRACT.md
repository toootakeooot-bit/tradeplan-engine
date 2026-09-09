# TradePlan Engine Input Contract

Status: **TC4-1 input contract baseline**

This document defines the prepared Market Input accepted by ② TradePlan Engine.

It does not define TradingCursor analysis logic, NODA logic, capture implementation, risk sizing, execution, or position management.

## 1. Objective

The input contract must allow the exact same observed market set to be supplied independently to:

- NODA② TradePlan Engine
- TC② TradePlan Engine

Shared input means **the same observed market information**, not shared strategy logic.

The contract therefore prioritizes:

- identity;
- four-timeframe completeness;
- traceability;
- reproducibility;
- strategy-neutrality;
- leakage prevention.

## 2. Minimum required input set

Every valid Market Input must contain:

- \`input_set_id\`
- \`symbol\`
- \`observation_timestamp\`
- D1 artifact
- H4 artifact
- H1 artifact
- M15 artifact

Each timeframe artifact must contain, at minimum:

- \`timeframe\`
- \`artifact_ref\`
- \`capture_timestamp\`
- \`source_id\`

The four timeframe labels are fixed for this contract:

- D1
- H4
- H1
- M15

TC4-1 does not define a final JSON transport schema.

## 3. Field classification

### REQUIRED

| Field | Meaning |
|---|---|
| \`input_set_id\` | Stable identifier that groups the exact four artifacts into one observation set. |
| \`symbol\` | Exact market symbol represented by all four artifacts. Broker-specific symbols such as \`GOLD#\`, \`USDJPY#\`, \`US100Cash#\`, and \`JP225Cash#\` are valid. |
| \`observation_timestamp\` | Reference timestamp for the observation set. Must be timezone-explicit so the observation can be reconstructed unambiguously. |
| \`D1\` | Required D1 artifact descriptor. |
| \`H4\` | Required H4 artifact descriptor. |
| \`H1\` | Required H1 artifact descriptor. |
| \`M15\` | Required M15 artifact descriptor. |
| \`timeframe\` | Explicit timeframe label inside each artifact descriptor. |
| \`artifact_ref\` | Stable reference that allows the exact artifact used for the decision to be located again. |
| \`capture_timestamp\` | Capture time for that specific artifact, timezone-explicit. |
| \`source_id\` | Identifier for the data/capture source sufficient to distinguish where the artifact came from. |

### OPTIONAL

| Field | Meaning |
|---|---|
| \`canonical_symbol\` | Broker-neutral symbol mapping, if a validated mapping exists. TC4-1 does not invent mappings. |
| \`broker\` / \`broker_id\` | Broker or venue metadata. |
| \`artifact_hash\` | Integrity fingerprint for stronger reproducibility and duplicate/change detection. |
| \`capture_session_id\` | Capture-cycle/session identifier if the capture system can provide it. |
| \`artifact_metadata\` | Non-strategy metadata such as file name, dimensions, MIME type, storage provider, or capture application version. |
| \`source_metadata\` | Additional non-strategy data-source metadata. |

Optional fields may strengthen traceability, but their absence does not invalidate TC4-1 minimum input if all REQUIRED fields and semantic conditions are satisfied.

### FORBIDDEN

The following must not be supplied as strategy input to either engine:

- LONG / SHORT recommendation;
- Entry decision, Entry label, or “correct entry”;
- SL decision, SL label, or “correct SL”;
- TP decision, TP label, or “correct TP”;
- NODA evaluation result;
- NODA rule-match result;
- TC analysis result from a prior run;
- future outcome / future price information;
- realized trade result, profit/loss, win/loss label;
- answer key, benchmark label, or post-hoc correctness label;
- account balance;
- risk amount;
- risk percentage policy;
- lot;
- position size;
- execution instruction;
- existing-position management instruction.

The input may not use hidden annotations, filenames, metadata, overlays, or adjacent text as a side channel to carry the same forbidden information.

## 4. Symbol identity

All four timeframe artifacts in one \`input_set_id\` must represent the same exact \`symbol\`.

The \`symbol\` field is the authoritative identity for the captured source symbol.

Broker-specific symbols are permitted and must not be silently rewritten.

If a \`canonical_symbol\` is supplied:

- it is supplemental;
- the mapping must be explicit and traceable;
- it must not replace or obscure the original \`symbol\`;
- a mapping that is uncertain must be omitted or marked TBD outside the required input.

TC4-1 defines no broker-symbol conversion table.

## 5. Observation and capture timestamps

\`observation_timestamp\` identifies the reference market observation represented by the set.

Each artifact's \`capture_timestamp\` records when that artifact was captured.

These timestamps serve different purposes and both are required.

They must be stored in an unambiguous timezone-explicit representation.

TC4-1 intentionally defines **no arbitrary maximum seconds/minutes difference** between the four capture timestamps.

A numeric freshness or capture-window threshold may be introduced only later with evidence and must be marked TBD until then.

## 6. Four-timeframe integrity

A valid Market Input must satisfy all of the following:

1. exactly one required artifact is available for each of D1, H4, H1, and M15;
2. every artifact descriptor's internal \`timeframe\` matches its assigned slot;
3. all four artifacts represent the same \`symbol\`;
4. all four belong to the same declared \`input_set_id\`;
5. every artifact has a traceable \`artifact_ref\`, \`capture_timestamp\`, and \`source_id\`;
6. the set can be supplied unchanged to both NODA② and TC②;
7. no artifact is substituted after one engine has run unless a new input set identity/version is created;
8. capture metadata must be sufficient to detect obvious old/new mixing or an unresolvable set mismatch.

If the system cannot establish that the four artifacts form one coherent observation set, the input is **invalid for engine comparison** rather than silently repaired.

## 7. Old/new image mixing

TC4-1 does not impose a numerical capture-window rule.

Instead, the contract requires traceability that makes mixing detectable.

Signals available for validation include:

- \`input_set_id\`;
- per-artifact \`capture_timestamp\`;
- \`source_id\`;
- optional \`capture_session_id\`;
- optional \`artifact_hash\`.

If metadata shows contradictory capture sessions, mismatched symbols/timeframes, replacement artifacts, or otherwise unresolved provenance, the set must not be treated as the same fixed Market Input.

The exact quantitative freshness threshold remains **TBD**.

## 8. Prepared image conditions

When the Market Input artifact is a chart image, it must already be analyzable when received by ②.

At minimum:

- symbol is identifiable;
- timeframe is identifiable;
- price axis is readable;
- candlesticks / bars are readable;
- the current-market vicinity is visible;
- the chart is not left in a historical/partial scroll state that hides the current vicinity;
- the image is not materially corrupted, blank, clipped, or obscured in a way that prevents market interpretation.

These are semantic acceptance conditions, not MT4 automation instructions.

TC4-1 does not implement:

- MT4 startup;
- Profile switching;
- movement to the current bar;
- screenshot capture;
- Drive storage;
- Scheduler;
- capture retry logic.

Those remain upstream Capture / preparation responsibilities.

## 9. Reproducibility

A completed input set must be referentially stable.

For comparison or replay:

- the same \`input_set_id\` must resolve to the same four artifacts;
- the four \`artifact_ref\` values must identify the artifacts actually used;
- an engine rerun must be able to consume the same fixed artifacts;
- if an artifact changes, is replaced, or is recaptured, the system must not pretend it is the unchanged prior input set.

An \`artifact_hash\` is recommended for stronger integrity checks but remains OPTIONAL in TC4-1 because storage/transport implementation is not yet fixed.

## 10. NODA② / TC② common-input rule

For a valid direct comparison:

- both engines receive the same \`input_set_id\`;
- both engines receive the same four artifact references;
- both engines receive the same symbol identity and timestamps;
- neither engine receives the other engine's output;
- neither engine receives strategy labels derived from the other;
- no engine-specific rule annotations are embedded into the common input.

Thus:

**same observation ≠ same logic**.

## 11. Responsibility boundary

Upstream Capture/preparation is responsible for producing a Market Input that satisfies this contract.

② TradePlan Engine is responsible for strategy analysis only after valid prepared input is supplied.

No Position Size, Lot, account balance, monetary risk, order execution, or open-position management data is required or permitted as strategy input under TC4-1.

## 12. TBD items

The following are intentionally not finalized in TC4-1:

- quantitative maximum time spread among four captures;
- quantitative maximum artifact age/freshness threshold;
- final storage/reference URI format;
- final \`source_id\` namespace;
- final canonical-symbol mapping table;
- whether \`artifact_hash\` becomes REQUIRED;
- final JSON Schema / transport schema;
- final invalid-input status enum and downstream handling.

These may be fixed only in later work with sufficient implementation or operational evidence.
