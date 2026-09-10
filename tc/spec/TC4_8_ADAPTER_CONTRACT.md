# TC4-8 — Adapter Contract

Status: **TC4-8 design contract / non-production**

## 1. Contract purpose

This document defines the TC-side request/output contract around the TradingCursor Native call boundary without implementing strategy logic.

```text
AdapterRequest
   ↓
TC Adapter / Native Client boundary
   ↓
TradingCursor Native Response
   ↓
Raw Preservation + lossless parse
   ↓
TCTradePlanRaw v1.0.0
```

A transport/preservation failure may return an Adapter failure result instead of TCTradePlanRaw. Adapter failures are not Trade States.

## 2. AdapterRequest

Required conceptual fields:

```text
request_id
source_run_id
execution_order
analysis_source
analysis_symbol
timeframe
```

Optional wrapper-only context may include:

```text
requested_at
caller_context
batch_request_id
```

No optional field is forwarded to TradingCursor unless the Native Interface explicitly supports it.

## 3. Field meanings

### request_id
Identifies one Adapter request/attempt. A repeat attempt receives a new request_id.

### source_run_id
Groups related Raw records under the TCTradePlanRaw identity model. It is wrapper provenance, not TradingCursor Native data.

### execution_order
Technical order within the run. It does not express strategy or internal reasoning order.

### analysis_source
Exact source/exchange requested from TradingCursor.

Native mapping:

```text
analysis_source -> exchange
```

No broker-source equivalence is inferred.

### analysis_symbol
Exact TradingCursor symbol requested.

Native mapping:

```text
analysis_symbol -> symbol
```

No automatic `GOLD# -> XAUUSD` or other broker/canonical mapping is allowed.

### timeframe
TC v1 common request timeframe. Current mapping:

| Common timeframe | Native interval |
|---|---|
| D1 | 1D |
| H4 | 4h |
| H1 | 1h |
| M15 | 15m |

Unsupported values fail explicitly; nearest-interval substitution is forbidden.

## 4. Native request contract

The current Native request is exactly:

```text
exchange = analysis_source
symbol   = analysis_symbol
interval = timeframe_map[timeframe]
```

No free prompt, image, artifact_ref, fixed snapshot ID, or simultaneous 4TF input is assumed.

## 5. One-call contract

```text
1 AdapterRequest
→ 1 Native call
→ 1 timeframe
→ 0 or 1 Native Response
→ 0 or 1 TCTradePlanRaw record
```

If no Native response exists because transport fails, no fake TCTradePlanRaw is produced.

If a Native response exists and is preserved successfully, the Adapter may complete TCTradePlanRaw even when `analysis` parsing fails.

## 6. Output contract

The Adapter has two conceptual outcome families.

### A. Raw outcome

Condition:
- a Native response was obtained;
- the response was preserved successfully;
- a stable `source_raw_artifact` reference exists;
- TCTradePlanRaw v1.0.0 structural requirements can be met.

Output:

```text
TCTradePlanRaw v1.0.0
```

### B. Adapter failure outcome

Condition examples:
- invalid AdapterRequest;
- unsupported timeframe;
- Native transport/call failure before a response exists;
- Native response preservation failure;
- TCTradePlanRaw wrapper/output contract failure.

Output concept:

```text
TCAdapterFailure
```

TC4-8 does not formalize TCAdapterFailure as a JSON Schema. It must remain separate from Trade State and from provider-native response status.

## 7. TCTradePlanRaw construction contract

The Adapter must use TCTradePlanRaw schema version `1.0.0` without modifying that schema in TC4-8.

Required top-level TCTradePlanRaw fields remain:

```text
schema_version
record_identity
original_response
parse_status
```

Required record identity remains:

```text
record_id
source_run_id
execution_order
source_raw_artifact
```

Adapter consequence: Raw Preservation must occur before final TCTradePlanRaw emission because `source_raw_artifact` cannot be fabricated.

## 8. Record identity

The Adapter respects the TC4-4 identity model:

```text
record_id = identity derived from source_run_id + execution order convention
```

TC4-8 does not change fixture IDs or establish a new incompatible format.

Runtime ID implementation details remain TBD until production implementation. Requirements are:
- uniqueness within the relevant storage domain;
- no overwrite on repeat attempts;
- traceability back to request/run/execution order;
- compatibility with TC4-4 raw references.

## 9. Original Response First

`original_response` is the source-native evidence envelope.

The Adapter must preserve all returned Native JSON values, including unknown fields, before any parse or derived extraction.

The Adapter must not rebuild `original_response` from a whitelist of known fields.

## 10. Analysis parsing

If `original_response.analysis` is JSON text, it may be parsed into `parsed_analysis`.

Parser behavior:

```text
input  = original_response.analysis
output = same JSON structure/keys/values
```

Allowed result states:
- `PARSED`
- `NOT_PARSED`
- `PARSE_ERROR`

No mapping to Entry/SL/TP/Q1-Q7/Trade State occurs in this stage.

## 11. Parse failure contract

When Native response preservation succeeded but `analysis` parsing fails:

```text
original_response = preserved
parsed_analysis   = absent or unusable
parse_status      = PARSE_ERROR
```

This remains a Raw/pipeline condition, not a Trade State.

## 12. Unknown-field contract

Unknown provider fields are preserved at the Native envelope/parsed Native levels allowed by TCTradePlanRaw v1.0.0.

They are not automatically:
- rejected;
- renamed;
- mapped to Q1-Q7;
- promoted into TradePlanState.

## 13. Derived metadata contract

Derived metadata is optional and separated from Native values.

Current observed derivation candidate:

```text
parsed_analysis.action_url
  ↓ extract URL query parameter chartId
  ↓
derived_metadata.chart_id
```

The Adapter must preserve derivation provenance exactly as TCTradePlanRaw v1.0.0 requires.

No standalone Native `chartId` field is asserted.

## 14. Wrapper metadata contract

Wrapper metadata may carry operational provenance, for example:

```text
request_id
adapter_contract_version
caller_context
received_at
```

Such fields are wrapper-generated and must not be treated as TradingCursor Native strategy evidence.

TC4-8 does not require new wrapper fields in the TCTradePlanRaw schema because `wrapper_metadata` is already open.

## 15. Transport / preservation / parse / output separation

The Adapter contract distinguishes:

```text
INPUT_VALIDATION
NATIVE_TRANSPORT
RAW_PRESERVATION
ANALYSIS_PARSE
RAW_OUTPUT_VALIDATION
DOWNSTREAM_MAPPING
```

These are processing stages, not a new provider status enum.

A failure at one stage must not be relabeled as WAIT, ACTIONABLE, INVALID, or UNDETERMINED.

## 16. Retry contract

Automatic retry inside the Adapter: **NONE for TC v1**.

Reason: a retry against a live Native source may observe a new market state.

If an upper caller later retries explicitly:
- it is a new attempt;
- it receives a new request_id;
- if a response is preserved, it receives a new record identity;
- prior Raw is never overwritten.

Retry count/backoff policy remains outside TC4-8.

## 17. Four-timeframe contract

The Adapter core processes one timeframe at a time.

An upper orchestrator may later issue four requests, but it must not ask the Adapter to synthesize a combined strategy decision.

```text
batch_request_id (optional upper-layer concept)
├─ D1 request -> D1 record
├─ H4 request -> H4 record
├─ H1 request -> H1 record
└─ M15 request -> M15 record
```

This is design-only; no 4TF orchestrator is implemented here.

## 18. Downstream ownership

Once TCTradePlanRaw is emitted:
- TC4-5 Mapping owns Native-to-provisional-field mapping;
- TC4-6 State Semantics owns WAIT/ACTIONABLE/INVALID/UNDETERMINED semantics;
- TC4-7 regression protects those semantics.

The Adapter cannot absorb those responsibilities.

## 19. Pseudo-interface

Design-only pseudo-interface:

```text
TCAdapterResult analyze(AdapterRequest request)

TCAdapterResult =
  TCTradePlanRaw(v1.0.0)
  OR TCAdapterFailure
```

Conceptual internal steps:

```text
validate request
translate source/symbol/timeframe
invoke Native Client
if no Native response:
    return transport failure
preserve Native response
if preservation fails:
    return preservation failure
construct record identity using preserved artifact reference
attempt lossless analysis parse
build TCTradePlanRaw v1.0.0
validate wrapper/output contract
return TCTradePlanRaw
```

No strategy method is part of this pseudo-interface.

## 20. TC4-7 invariant compatibility

Adapter implementation must later preserve all TCREG-01 through TCREG-20 outcomes. TC4-8 does not modify those tests or expectations.

Particularly protected:

```text
LONG + WAIT is valid
Trigger NOT_PROVIDED != WAIT
Entry presence != automatic ACTIONABLE
Invalidation Rule != Current INVALID
ACTIONABLE != execution permission
no 4TF synthesis
```

## 21. Version / change policy

This is the TC4-8 Adapter design contract, not a production API version.

Future production contract changes must not silently change:
- TCTradePlanRaw v1.0.0 semantics;
- Mapping semantics;
- State semantics;
- regression expectations.

If implementation reveals a raw schema incompatibility, record `SCHEMA CHANGE REQUIRED` rather than silently changing TCTradePlanRaw.
