# TC4-2 — TradingCursor Raw Analysis Survey

Status: **INSUFFICIENT OBSERVATION**

Repository: \`toootakeooot-bit/tradeplan-engine\`  
Branch: \`feature/tc-v1\`  
Start HEAD: \`fbf8a5a1df98bca6b3f57de0bf6d5f857d16f364\`

## 1. Survey objective

TC4-2 is intended to observe what TradingCursor itself returns from one fixed, strategy-neutral prepared Market Input, without NODA rule injection, ChatGPT supplementation, answer labels, position sizing, or post-hoc outcome information.

The required observation flow remains:

Market Input
→ TradingCursor native analysis
→ Raw Response
→ Observation classification

No TradingCursor strategy logic is implemented in this work.

## 2. Required input condition inherited from TC4-1

A valid TC4-2 observation requires one fixed \`input_set_id\` containing the exact same four prepared artifacts:

- D1
- H4
- H1
- M15

with the TC4-1 required identity and provenance fields:

- \`input_set_id\`
- \`symbol\`
- \`observation_timestamp\`
- per artifact: \`timeframe\`, \`artifact_ref\`, \`capture_timestamp\`, \`source_id\`

The same fixed set must be reusable later by both NODA② and TC②.

## 3. Available input-set survey

At TC4-2 start, the repository contains no TC4-1-compliant fixed Market Input fixture under \`fixtures/\`.

Observed repository state:

- \`fixtures/.gitkeep\` exists;
- no D1/H4/H1/M15 artifact set is present;
- no \`input_set_id\` fixture is present;
- no artifact references, capture timestamps, or source identifiers for a fixed 4TF set are present.

Therefore no repository input set is currently eligible for the TC4-2 experiment.

### Surveyed input_set list

**NONE — no valid fixed input set available.**

## 4. TradingCursor execution-interface capability observed

The currently callable TradingCursor analysis interface accepts:

- exchange
- symbol
- interval

and returns a TradingCursor-generated analysis for that requested asset/timeframe.

The callable interface does **not** expose parameters for:

- \`input_set_id\`;
- user-supplied D1/H4/H1/M15 \`artifact_ref\` values;
- fixed uploaded chart images;
- a custom natural-language analysis prompt;
- a separate Phase A prompt and Phase B prompt over the exact same supplied artifact set.

Consequently, using that interface against live/current charts would not prove that the exact TC4-1 fixed four-artifact Market Input was consumed.

It also would not allow the required Phase A / Phase B prompt distinction to be controlled.

TC4-2 does not substitute live requests for the required fixed Market Input because doing so would make the observation non-compliant with the TC4-1 contract.

## 5. Phase A — Natural Raw Analysis

Status: **NOT EXECUTED**

Reason:

1. no valid fixed TC4-1 Market Input fixture is available;
2. the available TradingCursor callable interface cannot receive the exact prepared 4TF artifact set;
3. the available callable interface does not expose a custom prompt channel needed to preserve the intended minimal Phase A instruction.

No Raw Response is fabricated or inferred.

## 6. Phase B — Minimal Trade Plan Request

Status: **NOT EXECUTED**

Reason:

1. no valid fixed TC4-1 Market Input fixture is available;
2. the available TradingCursor callable interface cannot replay that exact fixed artifact set;
3. the callable interface does not expose a distinct custom prompt channel for a minimal trade-plan request.

No Phase B output is fabricated from Phase A or from unrelated TradingCursor requests.

## 7. Output item observations

Because no valid TC4-2 run occurred, the following classifications remain unobserved rather than guessed.

| TradePlan component | TC4-2 observation |
|---|---|
| Environment | NOT_OBSERVED |
| Setup | NOT_OBSERVED |
| Trigger | NOT_OBSERVED |
| Entry | NOT_OBSERVED |
| SL | NOT_OBSERVED |
| TP | NOT_OBSERVED |
| Wait / Invalidation | NOT_OBSERVED |

These statuses mean **no compliant observation was available**. They do not mean TradingCursor is incapable of producing the fields.

## 8. TradingCursor-native fields

No TC-native field candidate is promoted from speculation.

The following examples remain survey targets only and are **not confirmed observations** in this TC4-2 run:

- confidence / score / probability;
- indicator state;
- volatility characterization;
- pattern name;
- liquidity information;
- risk/reward;
- reasoning text;
- warnings;
- alternative scenario.

TC4-4 must not treat these as confirmed fields based on this document.

## 9. Output variability

Status: **NOT OBSERVED**

A compliant repeatability experiment requires multiple TradingCursor runs against the same fixed Market Input.

Because the current interface cannot demonstrate replay of the exact four prepared artifacts, no repeat count is invented and no live rerun is used as a proxy.

Repeat count remains:

**TBD / available compliant runs**

## 10. Missing / ambiguous observations

### Missing

All strategy-output categories remain missing from a compliant TC4-2 experiment:

- Environment
- Setup
- Trigger
- Entry
- SL
- TP
- Wait / Invalidation
- TC-native field inventory
- same-input output variability

### Ambiguous

None are classified AMBIGUOUS because no valid Raw Response exists to interpret.

## 11. Raw-response preservation

No TradingCursor Raw Response has been committed as a TC4-2 fixture because no compliant fixed-input run was executed.

This preserves the core rule:

> do not present a non-compliant live analysis as if it were the Raw Response to the fixed TC4-1 Market Input.

## 12. What is required to unblock TC4-2

TC4-2 can resume when both conditions below are satisfied.

### A. Fixed Market Input fixture

At least one TC4-1-compliant set must be available and referenceable, containing:

- one \`input_set_id\`;
- one symbol;
- one observation timestamp;
- exact D1/H4/H1/M15 artifacts;
- timeframe identity;
- artifact references;
- capture timestamps;
- source identifiers.

### B. TradingCursor execution path compatible with the experiment

The experiment needs a path that can:

1. consume or visibly operate on the exact fixed chart artifacts;
2. preserve the same artifacts between runs;
3. execute a minimal natural analysis request (Phase A);
4. execute a distinct minimal trade-plan request (Phase B);
5. return/preserve the original Raw Response for each run.

If the TradingCursor UI or another integration can satisfy these conditions, the resulting Raw Responses may be captured as TC4-2 fixtures and then classified without modification.

## 13. TC4-3 handoff

**HOLD**

TC4-3 is intended to define the TC internal decision process from observed TradingCursor behavior.

Proceeding now would risk inventing that process without evidence.

TC4-3 should begin only after TC4-2 has at least enough compliant Raw Response material to support the proposed internal steps.

## 14. TC4-4 Raw-retention candidates

No field list is formally promoted from observation yet.

The only retention requirements already justified independently of TradingCursor output are:

- preserve the full original Raw Response;
- preserve the related \`input_set_id\`;
- preserve run identity / timestamp when available;
- preserve the request mode (Phase A or Phase B);
- preserve engine/source metadata when available.

All semantic TC-native field candidates remain pending actual observation.

## 15. Scope compliance

TC4-2 does not modify:

- TC4-0 responsibility boundaries;
- TC4-1 input contract;
- NODA logic;
- TC decision logic;
- TCTradePlanRaw formal schema;
- TradePlanState formal schema;
- WAIT / INVALID formal rules;
- Adapter;
- Normalizer;
- Position Sizing;
- execution;
- \`trade-plan-a\`.

No TradingCursor answer correctness or trading performance is evaluated.

## 16. Interim verdict

**TC4-2: INSUFFICIENT OBSERVATION**

This is a controlled stop, not a fabricated PASS or FAIL of TradingCursor capability.
