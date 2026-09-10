# TC4-8 — Adapter Failure Matrix

Status: **TC4-8 design-only failure boundary**

This matrix defines what the Adapter may do when technical conditions fail. It does not create trading states.

| Event / Input | Native operation | Adapter responsibility | Output | Failure handling | Raw preservation | Downstream owner | Inference? | Notes |
|---|---|---|---|---|---|---|---|---|
| `analysis_source` missing | none | reject incomplete request | Adapter failure | INPUT_VALIDATION | N/A | caller | NO | No default exchange is invented |
| `analysis_symbol` missing | none | reject incomplete request | Adapter failure | INPUT_VALIDATION | N/A | caller | NO | No symbol is guessed |
| unsupported common timeframe | none | reject unsupported mapping | Adapter failure | INPUT_VALIDATION | N/A | caller | NO | No nearest timeframe substitution |
| valid D1 | `interval=1D` | technical translation only | Native request | proceed | N/A | Native Client | NO | Strategy meaning unchanged |
| valid H4 | `interval=4h` | technical translation only | Native request | proceed | N/A | Native Client | NO | Strategy meaning unchanged |
| valid H1 | `interval=1h` | technical translation only | Native request | proceed | N/A | Native Client | NO | Strategy meaning unchanged |
| valid M15 | `interval=15m` | technical translation only | Native request | proceed | N/A | Native Client | NO | Strategy meaning unchanged |
| Native call succeeds and response exists | call provider | pass untouched response to preservation | preserved response reference | proceed | REQUIRED | Adapter | NO | Native Response First |
| Native call fails before response | call provider | preserve failure provenance only | Adapter failure | NATIVE_TRANSPORT | no Native Raw exists | caller/orchestrator | NO | Do not create WAIT/INVALID/UNDETERMINED |
| Native response exists but preservation fails | no further semantic processing | report preservation failure | Adapter failure | RAW_PRESERVATION | FAILED | storage/operator | NO | Do not fabricate `source_raw_artifact` |
| Native response preserved; `analysis` valid JSON text | parse | lossless structural parse | TCTradePlanRaw candidate | `PARSED` | KEEP original | Mapping later | NO | Parse is not normalization |
| Native response preserved; `analysis` cannot parse | parse | retain Original Raw | TCTradePlanRaw candidate | `PARSE_ERROR` | KEEP original | downstream may stop/handle separately | NO | Parse Error is not Trade State |
| Native response preserved; parse intentionally not attempted | none | retain Original Raw | TCTradePlanRaw candidate | `NOT_PARSED` | KEEP original | downstream policy | NO | Allowed by TCTradePlanRaw v1.0.0 |
| unknown outer Native field | none | preserve field | TCTradePlanRaw | none | KEEP | future observation/mapping | NO | No whitelist drop |
| unknown parsed Native field | parse | preserve field/key/value | TCTradePlanRaw | none | KEEP | future observation/mapping | NO | No speculative mapping |
| `action_url` with `chartId` | optional derive | preserve URL, optionally derive chart id | derived metadata | none | KEEP Native URL | audit/technical metadata | NO | chartId remains derived |
| `action_url` without `chartId` | optional derive | retain URL; omit derived chart id | TCTradePlanRaw | no error required | KEEP | downstream | NO | Do not invent chart id |
| repeated same exchange/symbol/interval call | call provider only if caller explicitly requests | create new attempt identity | new record if response preserved | no automatic dedupe-overwrite | KEEP both | caller/orchestrator | NO | Live market may differ |
| Adapter automatic retry request | none | do not auto-retry in TC v1 | original failure | retry = NONE | as available | caller/orchestrator | NO | Any later retry is explicit new attempt |
| symbol looks equivalent to broker/canonical symbol | none | preserve explicit analysis symbol | unchanged request | no auto conversion | N/A | caller/symbol layer | NO | `GOLD# -> XAUUSD` forbidden |
| 4TF batch requested by upper layer | four independent calls only if separately orchestrated | process each request independently | four independent Raw records | per-call failure isolation | KEEP each response | upper orchestrator | NO | No 4TF strategy synthesis |
| `potentialPosition` present | none | preserve Native content | TCTradePlanRaw | none | KEEP | TC4-5 | NO | Adapter does not map Entry |
| explicit wait text present | none | preserve text | TCTradePlanRaw | none | KEEP | TC4-5/TC4-6 | NO | Adapter does not emit WAIT |
| invalidation rule text present | none | preserve text | TCTradePlanRaw | none | KEEP | TC4-5/TC4-6 | NO | Adapter does not emit INVALID |
| Position Sizing / risk text present | none | preserve text | TCTradePlanRaw | none | KEEP | outside TradePlan authority | NO | Adapter neither drops nor acts on it |
| TCTradePlanRaw wrapper cannot satisfy required identity/output fields | none | report wrapper/output contract failure | Adapter failure | RAW_OUTPUT_VALIDATION | preserved Native Raw remains authoritative | implementation/operator | NO | Do not silently change schema |
| downstream Mapping fails | none | no Adapter reinterpretation | downstream failure | outside Adapter | Raw already preserved | TC4-5 implementation | NO | Do not relabel as transport/parse failure |
| downstream State evaluation fails | none | no Adapter reinterpretation | downstream failure | outside Adapter | Raw already preserved | TC4-6 implementation | NO | Do not create fake state |

## Failure classes

TC4-8 uses the following **processing-stage labels** only for traceability; these are not TradingCursor provider statuses and are not Trade States:

- `INPUT_VALIDATION`
- `NATIVE_TRANSPORT`
- `RAW_PRESERVATION`
- `ANALYSIS_PARSE`
- `RAW_OUTPUT_VALIDATION`

`DOWNSTREAM_MAPPING` and later state processing are outside the Adapter.

## Retry rule

```text
Adapter automatic retry = NONE
```

No fixed retry count or backoff is introduced. An explicit upper-layer retry, if later authorized, is a new request/attempt and may yield a new market observation.

## Failure-to-state prohibition

None of the following conversions are permitted:

```text
NATIVE_TRANSPORT failure -> WAIT
NATIVE_TRANSPORT failure -> UNDETERMINED
RAW_PRESERVATION failure -> INVALID
PARSE_ERROR -> WAIT
PARSE_ERROR -> UNDETERMINED
RAW_OUTPUT_VALIDATION failure -> ACTIONABLE
```

Infrastructure/process status and Trade State remain orthogonal.

## Schema-change trigger

If a real preserved Native response cannot be represented by TCTradePlanRaw v1.0.0 without data loss, the result is:

```text
SCHEMA CHANGE REQUIRED
```

TC4-8 must not silently change `tc/schema/tc_tradeplan_raw.schema.json`.
