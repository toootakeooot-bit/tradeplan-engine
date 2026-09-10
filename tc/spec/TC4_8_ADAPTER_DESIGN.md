# TC4-8 — Adapter Design

Status: **TC4-8 baseline / design-only**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `1beaaaa4414b20c651dbb69eb205b364af195ff9`

## 1. Purpose

TC4-8 defines the boundary between the currently exposed TradingCursor Native Interface and the TC-side TradePlan Engine representation.

```text
Market Request
   ↓
TC Adapter
   ↓
TradingCursor Native Interface
   ↓
Native Response
   ↓
TC Adapter
   ↓
TCTradePlanRaw v1.0.0
   ↓
TC4-5 Mapping
   ↓
TC4-6 State Semantics
```

The Adapter is a transport/preservation boundary. It is not a strategy engine and does not improve, complete, reinterpret, or aggregate TradingCursor decisions.

## 2. Governing boundaries

The Adapter may:
- validate technical request completeness;
- translate TC common request names into the exact Native request arguments;
- invoke a Native Client boundary;
- receive a Native response;
- preserve that response before parsing;
- create wrapper/run identity metadata;
- losslessly parse `analysis` when it is JSON text;
- record parse/preservation/transport outcomes;
- derive technical metadata such as `chart_id` from `action_url` when explicitly marked derived;
- emit a schema-valid `TCTradePlanRaw v1.0.0` when a Native response has been preserved.

The Adapter must not:
- decide Environment / Setup / Trigger / Entry / SL / TP;
- map Native fields into provisional TradePlanState;
- determine WAIT / ACTIONABLE / INVALID / UNDETERMINED;
- synthesize 4TF strategy output;
- introduce NODA rules;
- size positions or calculate account/risk amounts/Lot;
- authorize or submit orders.

Core rule:

```text
Adapter != Mapper
Adapter != Normalizer
Adapter != State Evaluator
Adapter != 4TF Aggregator
Adapter != Execution Layer
```

## 3. Current Native Interface boundary

TC4-2P established the currently exposed callable request dimensions as:

- `exchange`
- `symbol`
- `interval`

TC4-8 does not assume image upload, fixed artifact input, simultaneous 4TF input, free prompt input, or caller-controlled frozen snapshot IDs.

Provider-specific names stay inside the Native Client / Adapter boundary.

## 4. Adapter request model

TC-side request semantics are defined in `TC4_8_ADAPTER_CONTRACT.md`.

Required request concepts:
- `request_id` — identity of one Adapter analysis request;
- `source_run_id` — run grouping used by TCTradePlanRaw identity;
- `execution_order` — order within the run; technical provenance only;
- `analysis_source` — exact TradingCursor analysis source/exchange to request;
- `analysis_symbol` — exact TradingCursor analysis symbol to request;
- `timeframe` — TC common timeframe among the currently supported v1 set.

Provider translation:

```text
analysis_source -> exchange
analysis_symbol -> symbol
D1  -> 1D
H4  -> 4h
H1  -> 1h
M15 -> 15m
```

This translation is technical representation only; it does not create strategy meaning.

## 5. Symbol policy

The Adapter does not perform strategy/broker symbol substitution.

```text
broker_symbol
canonical_symbol
analysis_symbol
```

remain distinct concepts.

In particular, no Adapter rule silently converts XM `GOLD#` to OANDA `XAUUSD`. Any future symbol mapping must be a separately specified layer or explicit caller decision.

## 6. Timeframe policy

One Native call remains one timeframe and produces at most one TCTradePlanRaw record.

```text
1 request
→ 1 Native call
→ 1 timeframe
→ 1 Native response
→ 1 TCTradePlanRaw record
```

An unsupported common timeframe must fail explicitly. The Adapter must not silently substitute a nearby interval.

## 7. Four-timeframe orchestration

TC4-8 permits a future upper orchestration layer to issue four independent requests for D1/H4/H1/M15. That orchestration is **DESIGN_ONLY / outside the core Adapter**.

If such orchestration exists, its output remains four independent records:

```text
D1 record
H4 record
H1 record
M15 record
```

No content-level 4TF synthesis, consensus, conflict resolution, or trading decision is performed by the Adapter.

Execution order such as D1 -> H4 -> H1 -> M15 is technical sequencing only and must never be described as TradingCursor internal reasoning order.

## 8. Native Client / Adapter separation

Decision: **SEPARATE RESPONSIBILITIES**.

Conceptual responsibilities:

```text
Native Client
= invoke the exposed TradingCursor transport/call contract

TC Adapter
= validate request translation, preserve Native response,
  wrap provenance, losslessly parse, and emit TCTradePlanRaw
```

This is a design separation, not a production implementation. No new runtime client or Adapter code is introduced in TC4-8.

Reason:
- provider interface changes remain localized;
- transport failure remains distinct from parsing/mapping/state semantics;
- TCTradePlanRaw preservation rules remain stable when provider transport evolves.

## 9. Native Response First

The Adapter must preserve the response before semantic processing.

```text
TradingCursor Native response
        ↓
Raw Preservation
        ↓
source_raw_artifact reference obtained
        ↓
lossless parse
        ↓
TCTradePlanRaw
```

It is forbidden to parse first and retain only selected fields.

## 10. `source_raw_artifact` integration requirement

TCTradePlanRaw v1.0.0 requires `record_identity.source_raw_artifact`.

Therefore a schema-valid TCTradePlanRaw record must not be emitted until the Native response has been persisted by a Raw Preservation collaborator and a stable artifact reference/path has been assigned.

This is an Adapter integration requirement, not a TCTradePlanRaw schema change.

The exact runtime storage backend and URI/path syntax remain TBD.

If Native response preservation fails, the Adapter must report a preservation failure and must not fabricate `source_raw_artifact` or emit an apparently valid TCTradePlanRaw record.

## 11. Original response preservation

When a Native response exists, `original_response` is primary evidence and is copied without semantic filtering.

Unknown Native outer fields are preserved.

When `analysis` is present as JSON text, the original string remains in:

`/original_response/analysis`

and is not replaced by its parsed form.

## 12. Lossless parser boundary

Allowed:
- JSON parse;
- key/value preservation;
- array/object preservation;
- unknown-field preservation.

Forbidden:
- renaming `positionType` to `direction`;
- extracting Trigger/WAIT;
- Entry/SL/TP correction;
- indicator interpretation;
- NODA tagging;
- Trade State generation.

```text
parse != normalize
```

## 13. Parse status

The Adapter uses TCTradePlanRaw v1.0.0 parse states:

- `PARSED`
- `NOT_PARSED`
- `PARSE_ERROR`

A Native response can be successfully preserved while parsing fails.

```text
transport success
raw preservation success
parse status = PARSE_ERROR
```

is valid.

Parse failure does not become WAIT, INVALID, ACTIONABLE, or UNDETERMINED.

## 14. Failure boundary

TC4-8 separates at least these stages:

1. input/request validation;
2. Native transport/call;
3. Native response preservation;
4. analysis parsing;
5. TCTradePlanRaw output validation;
6. downstream Mapping/State processing.

A pre-response transport failure cannot produce TCTradePlanRaw v1.0.0 because there is no `original_response` to preserve. It produces an Adapter failure result outside Trade State semantics.

A post-response parse failure can still produce TCTradePlanRaw when Original Raw is preserved and parse state is `PARSE_ERROR`.

## 15. Failure is not Trade State

Explicit prohibitions:

```text
Native transport failure != UNDETERMINED
Native transport failure != WAIT
Native transport failure != INVALID
PARSE_ERROR != Trade State
preservation failure != Trade State
```

The Adapter never creates a fake trading state to represent infrastructure failure.

## 16. Request and record identity

`request_id` and `record_id` are distinct:

- `request_id` identifies one Adapter request/attempt;
- `record_id` identifies one persisted TCTradePlanRaw record.

A repeat call, even with identical exchange/symbol/interval arguments, is a new attempt because the Native source is live.

Repeats must not overwrite an earlier record.

TC4-8 keeps the TC4-4 record identity convention and does not redefine fixture IDs. Exact runtime ID generation/padding policy remains compatible with TC4-4 and is finalized only when implementation is introduced.

## 17. Wrapper metadata

Wrapper-generated metadata may include:
- `request_id`;
- Adapter contract/version identifier;
- caller context;
- receipt/preservation timestamps where actually captured.

These values are never represented as TradingCursor Native authority.

Native provider fields remain inside `original_response`.

## 18. Derived metadata

`chartId` is not a Native standalone field in the observed response.

If extracted, the Adapter may preserve it only as:

```text
derived_metadata.chart_id
```

with derivation provenance from `/parsed_analysis/action_url` using the existing TCTradePlanRaw v1.0.0 convention.

No derived field may be presented as if it was supplied directly by TradingCursor.

## 19. Unknown Native fields

The Adapter must preserve unknown Native fields rather than reconstruct a whitelist-only response.

```text
unknown provider field
→ preserve
→ no speculative meaning
```

The Adapter must not map a newly observed provider field into Q1-Q7 or Trade State merely because its name appears suggestive.

## 20. Retry policy

Adapter-owned automatic retry for TC v1 design: **NONE**.

Reason: the source is live; an automatic retry can observe a different market state and must not masquerade as the same observation.

A caller may later issue an explicit retry/new attempt under a separately authorized orchestration policy. Such an attempt must receive a new `request_id` and, if a Native response is preserved, a new record identity.

Backoff counts/timers are not defined in TC4-8.

## 21. Regression guardrails

TC4-7 remains immutable and authoritative for Adapter downstream invariants.

Adapter integration must not produce regressions including:

```text
WAIT -> ACTIONABLE without explicit evidence
Trigger NOT_PROVIDED -> WAIT
Entry present -> ACTIONABLE automatically
Invalidation Rule -> Current INVALID
ACTIONABLE -> execution authorization
Position Size -> State authority
4TF records -> synthetic TC total state
```

TCREG-01 through TCREG-20 are not modified by TC4-8.

## 22. Sequence — normal path

```text
Caller
  ↓ AdapterRequest
TC Adapter
  ↓ request validation / technical translation
Native Client
  ↓ exchange / symbol / interval
TradingCursor
  ↓ Native Response
Native Client
  ↓ untouched response value
TC Adapter
  ↓ Raw Preservation
Raw Store
  ↓ stable source_raw_artifact reference
TC Adapter
  ↓ lossless analysis parse
TCTradePlanRaw v1.0.0
  ↓
TC4-5 Mapping
  ↓
TC4-6 State Semantics
```

## 23. Sequence — transport failure

```text
Caller
  ↓
TC Adapter
  ↓
Native Client
  ↓ failure / no Native Response
TC Adapter
  ↓
TCAdapterFailure
  ↓
NO TCTradePlanRaw
NO fake Trade State
```

## 24. Sequence — parse failure

```text
TradingCursor
  ↓ Native Response
Raw Preservation
  ↓ succeeds
original_response preserved
  ↓ parse fails
parse_status = PARSE_ERROR
  ↓
TCTradePlanRaw v1.0.0 retained
```

## 25. Current Interface containment

Provider-specific `exchange`, `symbol`, and `interval` are translated only at the Native boundary. TC4-5 Mapping and TC4-6 State Semantics remain provider-interface agnostic.

If the provider later adds snapshot/image/prompt/multi-timeframe capability, the Native Client/Adapter contract can evolve without silently changing Mapping/State semantics.

Unobserved future fields are not predeclared as v1 capabilities.

## 26. Production implementation status

TC4-8 is design-only.

Not implemented:
- Native Client runtime;
- production Adapter;
- production Mapper/Normalizer;
- runtime State Evaluator;
- 4TF Aggregator;
- risk/sizing/execution.

No stub is required at this stage because the interface can be fully specified without creating misleading executable behavior.

## 27. TC4-9 handoff

Fixed for TC4-9:
- Native request boundary = exchange/symbol/interval;
- TC request contract and timeframe translation;
- one call / one timeframe / one Raw record;
- Native Client and Adapter responsibilities are separated conceptually;
- Native Response First / Raw Preservation before parse;
- TCTradePlanRaw v1.0.0 remains the output contract;
- transport/preservation/parse failures remain distinct from Trade State;
- automatic Adapter retry = none;
- repeats are new identities;
- unknown Native fields are preserved;
- chartId is derived only;
- no symbol auto-conversion;
- no strategy/mapping/state logic in Adapter;
- TC4-7 regression baseline is immutable.

TBD for later implementation:
- concrete Native Client runtime technology;
- durable Raw storage backend and `source_raw_artifact` URI/path format;
- concrete runtime request/record ID generator implementation;
- caller-side batch orchestration implementation;
- operational logging sink and retention;
- explicit retry/orchestration policy if later required.
