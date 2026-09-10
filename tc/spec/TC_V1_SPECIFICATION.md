# TC Engine v1 Specification

Status: **TC v1 specification baseline / design-frozen, production-not-implemented**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`

## 1. Purpose

This document integrates the TC-side design produced by TC4-0 through TC4-8 into one versioned specification baseline named **TC Engine v1**.

TC Engine v1 is a specification baseline, not a claim of production readiness, TradingCursor determinism, trading profitability, NODA equivalence, or a final Common TradePlanState.

Conceptual flow:

```text
Market Request
     ↓
TC Adapter
     ↓
TradingCursor Native Interface
     ↓
Native Response
     ↓
Raw Preservation
     ↓
TCTradePlanRaw v1.0.0
     ↓
provisional Mapping
     ↓
provisional State Semantics
     ↓
TC output
```

Position sizing, risk-amount policy and execution remain downstream/outside TC Engine v1.

## 2. Responsibility boundary — FIXED

TC Engine v1 owns the strategy-decision surface:

```text
Environment
→ Setup
→ Trigger
→ Entry
→ SL
→ TP
→ Wait / Invalidation
```

It does not own:
- account balance;
- monetary risk amount;
- risk-percent policy;
- Position Size / Lot;
- broker order execution;
- open-position or ticket management;
- W8 / W9 behavior.

TC logic and future NODA logic remain separate. NODA-specific rules such as R01-R37, 大ダウ, 小ダウ, 際, 先行局面, 本格局面, 最終局面 and BR are not part of TC v1.

## 3. Current TradingCursor Native boundary — FIXED for TC v1

The currently verified callable boundary accepts:

```text
exchange
symbol
interval
```

Current TC v1 does not assume support for:
- image upload;
- caller-supplied artifact_ref;
- free prompt;
- simultaneous 4TF input;
- caller-controlled frozen snapshot ID.

This is a versioned current boundary, not a permanent claim about the TradingCursor product.

## 4. Question Contract relation — FIXED

The common output questions are:

```text
Q1 Environment
Q2 Setup
Q3 Trigger
Q4 Entry
Q5 SL
Q6 TP
Q7 Wait / Invalidation
```

Same Question Contract does not imply same reasoning logic or identical prompt text.

Availability statuses remain:

```text
OBSERVED
NOT_PROVIDED
AMBIGUOUS
NOT_APPLICABLE
```

`NOT_PROVIDED` is a valid result. Missing TC information is not invented to complete the contract.

## 5. Mapping operations — FIXED

```text
EXTRACT = YES
LIGHT_NORMALIZATION = YES
INFERENCE = NO
```

Examples of prohibited inference include:
- RSI value -> Setup;
- MACD crossover -> Trigger;
- patternDetected -> WAIT;
- support-break arithmetic -> Current INVALID;
- adding missing Entry/SL/TP/Trigger fields.

## 6. Observation / comparison level — FIXED disclosure rule

TC Native Raw development survey is LEVEL C:

```text
SAME_QUESTION_NATIVE_SOURCE_SURVEY
```

LEVEL C is not a strict NODA-vs-TC fairness claim. LEVEL A `STRICT_SAME_ARTIFACT` and LEVEL B `SAME_MARKET_OBSERVATION` remain separate future comparison modes.

## 7. Observable decision structure — FIXED boundary

TC v1 defines only observable output mapping. It does not claim to know TradingCursor's hidden internal reasoning sequence.

Native structured fields and explicit Native text may be mapped only where their meaning is explicit. Structured field existence and Question meaning remain separate judgments.

## 8. TCTradePlanRaw v1.0.0 — FIXED

Formal raw contract:

`tc/schema/tc_tradeplan_raw.schema.json`

Version:

```text
TCTradePlanRaw = 1.0.0
```

Core rules:
- Original Raw First;
- `original_response` is primary evidence;
- original `analysis` string is retained;
- `parsed_analysis` is lossless structural parse only;
- Native, wrapper-generated and derived metadata remain separate;
- unknown Native fields are preserved;
- `observations` is retained in full;
- out-of-scope Native text such as Position Sizing remains in Raw;
- one Native call corresponds to one Raw record;
- repeat calls produce new records and never overwrite earlier records;
- raw references use `record_id + RFC 6901 JSON Pointer`.

Parse states remain:

```text
PARSED
NOT_PARSED
PARSE_ERROR
```

Parse state is not Trade State.

## 9. chartId — FIXED

`chartId` is not treated as a standalone Native field in the observed v1 response shape. When retained separately, it is derived from `parsed_analysis.action_url` and stored as derived metadata.

```text
Native action_url
→ query parameter extraction
→ derived_metadata.chart_id
```

## 10. Provisional Common Mapping — PROVISIONAL

TC4-5 mapping targets remain provisional pending NODA/Common review.

Confirmed mappings:

```text
futureAssumption.trend
→ environment.direction

potentialPosition.positionType
→ entry.direction
  light normalization only: long -> LONG, short -> SHORT

potentialPosition.entryPrice
→ entry.price

potentialPosition.stopLoss
→ sl.price

potentialPosition.takeProfits
→ tp.targets[]
```

Setup, Trigger, Wait, Invalidation and Alternative Scenario use only explicit Native `observations` text where the intended meaning is explicit.

The following are not forced into Common state:
- `confidenceScore`;
- `patternDetected`;
- `indicatorReadings`;
- `priceMetrics` final common adoption;
- Risk/Reward.

## 11. TC provisional State Semantics — PROVISIONAL

Current TC-side state names:

```text
WAIT
ACTIONABLE
INVALID
UNDETERMINED
```

These are TC v1 provisional semantics, not final Common enum values.

### WAIT
Explicit Native current-state wording says to wait / not yet confirmed / avoid entry for now / confirmation pending.

A full candidate plan may coexist with WAIT:

```text
direction = LONG
Entry/SL/TP = present
state = WAIT
```

### ACTIONABLE
Explicit Native wording recommends entry now/current price, with no explicit current WAIT/current INVALID in the same semantic context and no unresolved same-axis conflict.

`ACTIONABLE != Execution Permission`.

### INVALID
Requires explicit Native wording that the setup/scenario is currently invalid, already invalidated, or no longer valid.

An Invalidation Rule alone is not Current INVALID.

### UNDETERMINED
Evidence is insufficient to conclude WAIT/ACTIONABLE/INVALID without inference, or genuine unresolved current-state conflict exists.

`UNDETERMINED` is not a transport/parsing error substitute.

## 12. State guardrails — FIXED in TC v1

The following semantic invariants are fixed:

```text
Trigger NOT_PROVIDED != WAIT
Entry presence != automatic ACTIONABLE
Invalidation Rule != Current INVALID
ACTIONABLE != Execution Permission
SL != Scenario Invalidation
Alternative Scenario != WAIT
Alternative Scenario != INVALID
Direction != State
Environment != State
Setup != State
```

No current-price comparison is used to synthesize INVALID.

## 13. Timeframe independence — FIXED

Current mapping:

```text
D1  -> 1D
H4  -> 4h
H1  -> 1h
M15 -> 15m
```

Core rule:

```text
1 request
= 1 Native call
= 1 timeframe
= at most 1 TCTradePlanRaw record
```

TC v1 does not synthesize D1/H4/H1/M15 into one TradingCursor multi-timeframe strategy decision.

## 14. Symbol identity — FIXED

The following identities remain distinct where applicable:
- broker_symbol;
- canonical_symbol;
- analysis_symbol;
- analysis_source.

The Adapter must not silently convert symbols such as `GOLD# -> XAUUSD`.

## 15. Adapter boundary — FIXED design contract

Conceptual Adapter input:

```text
request_id
source_run_id
execution_order
analysis_source
analysis_symbol
timeframe
```

Native translation:

```text
analysis_source -> exchange
analysis_symbol -> symbol
D1 -> 1D
H4 -> 4h
H1 -> 1h
M15 -> 15m
```

Native Client and Adapter are responsibility-separated:

```text
Native Client = provider transport
TC Adapter = request translation + Raw preservation + wrapper identity + lossless parse + TCTradePlanRaw output
```

Production implementation technology is not fixed by TC v1.

## 16. Raw preservation sequence — FIXED

Because TCTradePlanRaw v1.0.0 requires `source_raw_artifact`, the Adapter design sequence is:

```text
Native Response
→ Raw Preservation
→ stable source_raw_artifact reference
→ lossless parse
→ TCTradePlanRaw v1.0.0
```

If preservation fails, the Adapter must not fabricate an artifact reference or emit a deceptively valid Raw record.

## 17. Failure semantics — FIXED

These failure domains remain separate:
- Adapter input validation;
- unsupported timeframe;
- Native transport failure;
- Raw preservation failure;
- analysis parse failure;
- TCTradePlanRaw output validation failure;
- downstream mapping/state processing.

Infrastructure failure is not Trade State:

```text
transport failure != WAIT/INVALID/UNDETERMINED
PARSE_ERROR != WAIT/INVALID/UNDETERMINED
preservation failure != Trade State
```

Unsupported timeframe must fail explicitly; nearest-timeframe substitution is forbidden.

## 18. Retry — FIXED at Adapter boundary

Adapter-owned automatic retry in TC v1:

```text
NONE
```

An explicit later retry is a new request and new record. Upper-layer retry policy remains TBD.

## 19. Regression baseline — FIXED

TC4-7 baseline:

```text
TCREG TESTABLE 20
PASS           20
FAIL            0
NOT_TESTABLE    5
```

TCREG-01 through TCREG-20 are specification invariants, not profitability tests and not evidence that live TradingCursor output is deterministic.

The baseline must not be rewritten merely to make later implementation pass.

## 20. NOT_TESTABLE baseline — NOT_TESTABLE

- NT01 Current INVALID positive recognition;
- NT02 true same-axis Structured/Text conflict resolution;
- NT03 Alternative Scenario automatic transition;
- NT04 WAIT-release runtime evaluation;
- NT05 Invalidation runtime evaluation.

These remain unproven rather than fabricated.

## 21. Known TBD — TBD

Implementation / evidence items not fixed by TC v1:
- durable Raw storage backend;
- `source_raw_artifact` URI/path convention;
- concrete runtime request_id generator;
- concrete runtime record_id generator;
- upper-layer 4TF request orchestration;
- operational logging sink/retention;
- retry policy above Adapter;
- true same-axis Structured/Text conflict resolution;
- Risk/Reward boundary;
- Current INVALID positive behavior verification;
- Alternative Scenario state transition;
- WAIT-release runtime evaluation;
- Invalidation runtime evaluation;
- production implementation technology.

## 22. Common TradePlanState remains PROVISIONAL

`spec/TRADEPLAN_STATE.md` remains provisional because NODA② requirements are not yet defined.

```text
TC Engine v1 specification frozen
!= Common TradePlanState final
```

TC-specific mapping/state semantics may be reviewed after NODA v1 without forcing TC to adopt NODA-specific logic.

## 23. Non-goals / not production-ready

TC v1 does not mean production implementation is complete. The following are not implemented/finalized by the freeze:
- production Native Client;
- production Adapter;
- production Mapper;
- production Normalizer;
- runtime State Evaluator;
- 4TF Aggregator / 4TF strategy logic;
- Position Sizing / Risk Engine;
- broker execution;
- NODA②.

Correct description:

```text
TC v1 specification baseline frozen
```

Incorrect description:

```text
TC v1 production ready
```

## 24. Change control

FIXED content is change-controlled after this baseline. Changes require explicit impact review against Raw schema, TCREG baseline, Common/NODA boundary and versioning. See `tc/spec/TC_V1_CHANGE_POLICY.md`.

## 25. Core freeze statement

TC Engine v1 freezes the currently supported TC-side architecture and semantic guardrails without pretending unresolved Common/NODA/runtime questions are complete.

```text
Raw in TC stays Raw.
Missing meaning is not invented.
Infrastructure failure is not Trade State.
TC-specific behavior is not rewritten into NODA behavior.
Common state remains provisional until NODA review.
```
