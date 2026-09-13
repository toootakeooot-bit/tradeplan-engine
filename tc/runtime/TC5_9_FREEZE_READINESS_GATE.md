# TC5-9 — Runtime Freeze Readiness Gate

Status: **NOT READY FOR PRODUCTION FREEZE / REPOSITORY RUNTIME + HOST BINDING CONTRACT + RECORDED LIVE REPLAY PASSED**

TC5-9 must not declare TC Spot Runtime production-ready merely because repository regression, ChatGPT-side Native calls, and recorded-live replay pass.

## Freeze prerequisites

All of the following are required before a production TC5 runtime freeze:

1. one coherent current NORMAL run completes through D1/H4/H1 using the intended runtime path;
2. one coherent current SHORT run completes through H4/H1/M15 using the intended runtime path;
3. one NORMAL drilldown case is verified where explicit H1 lower-timeframe confirmation evidence causes an M15 request and the result is handled by TC5-7 policy;
4. each Native call remains traceable to run/profile/role/timeframe identity;
5. no interval substitution occurs;
6. Raw/Adapter handling is connected to the actual live Native call path with stable persistence;
7. runtime/infrastructure failures remain separate from TradePlanState;
8. symbol normalization/provider mapping provenance is retained;
9. TC4 regression guardrails remain intact;
10. NODA remains separated;
11. execution permission remains outside TC Spot;
12. common output remains compatible with the provisional TradePlanState direction without finalizing Common solely around TC.

## Current verified progress

### ChatGPT Native capability

Verified on 2026-09-13 through the connected TradingCursor tool:

```text
GOLD family   -> OANDA / XAUUSD
USDJPY family -> OANDA / USDJPY
US100 family  -> PEPPERSTONE / NAS100
JP225 family  -> PEPPERSTONE / JPN225
```

Profile calls verified for GOLD:

```text
NORMAL: D1 -> H4 -> H1   = LIVE CALLS COMPLETED
SHORT : H4 -> H1 -> M15  = LIVE CALLS COMPLETED
```

A fresh NORMAL sequence captured at 2026-09-13 05:44-05:45Z was stored as:

```text
fixtures/tc5_live/TC5-LIVE-NORMAL-GOLD-20260913-0544Z.json
```

The H1 Native record in that run contained a LONG candidate plan but neither explicit current-entry wording nor explicit WAIT wording. Under frozen TC4 semantics this is correctly treated as:

```text
trade_state = UNDETERMINED
runtime_status = HOLD
common status = not emitted
execution_permission = false
```

### Repository runtime implementation

Implemented:

```text
tc/adapter/native_client.py       Native Client host interface
tc/adapter/adapter.py             Raw-preserving TCTradePlanRaw wrapper
tc/normalizer/normalizer.py       conservative mapping/state semantics
tc/runtime/orchestrator.py        NORMAL/SHORT + conditional drilldown flow
tc/runtime/raw_sink.py            immutable file Raw persistence sink
tc/runtime/response.py            provisional common TradePlanState builder
tc/runtime/host_binding.py        generic callable host binding
tc/runtime/service.py             one-line TC Spot service entrypoint
```

`run_spot_command()` now owns the repository-side path:

```text
command text
-> Command Parser
-> Symbol Resolver
-> Profile Planner
-> Runtime Orchestrator
-> host-supplied Native Client
-> immutable Raw persistence
-> TCTradePlanRaw Adapter
-> Normalizer
-> Role Aggregation
-> provisional TradePlanState
```

The external Host only needs to provide a Native call compatible with:

```text
request_analysis(exchange=..., symbol=..., interval=...)
```

No strategy logic is delegated to the Host binding.

### Recorded-live replay E2E

The fresh live GOLD NORMAL Native sequence was replayed through the actual repository service using the generic host binding and immutable FileRawSink.

Verified path:

```text
recorded live Native responses
-> CallableNativeClient
-> run_spot_command
-> FileRawSink
-> Adapter
-> Normalizer
-> Role Aggregation
-> TradePlanState
```

Result:

```text
RECORDED_LIVE_NATIVE_RAW_TO_TRADEPLANSTATE_E2E = PASSED
```

This proves that actual Native response shapes observed from the connected TradingCursor tool traverse the repository runtime correctly. It is still not the same as an automatic direct connector-to-repository live call in one process.

### Regression

GitHub Actions workflow `TC5 Runtime Regression` covers:

- TC4 TCREG regression;
- TC5 profile aggregation regression;
- TC5 static pipeline regression;
- TC5 runtime core regression;
- host binding tests;
- immutable Raw persistence tests;
- four-family symbol/provider registry tests;
- one-line service entrypoint test;
- recorded-live Native replay test.

Verified successful runs include:

```text
run 2   head e510d3f0edbdb3757be2db0ad358ff154deecb62  PASS
run 12  head ebb76694c8766252299746743106c4bf14bc75df  PASS
run 19  head 5a582fe1a75f90391adf39119d43a3d62fa8ef7e  PASS
```

## Current gates

```text
CHATGPT_NATIVE_NORMAL_SEQUENCE                 = PASSED
CHATGPT_NATIVE_SHORT_SEQUENCE                  = PASSED
CHATGPT_M15_ACCESS                             = PASSED
VALIDATED_SYMBOL_PROVIDER_REGISTRY             = PASSED (4 operational families)
REPO_NATIVE_CLIENT_INTERFACE                   = IMPLEMENTED
REPO_CALLABLE_HOST_BINDING                     = IMPLEMENTED
REPO_ONE_LINE_SPOT_SERVICE                     = IMPLEMENTED
REPO_ADAPTER                                   = IMPLEMENTED
REPO_NORMALIZER                                = IMPLEMENTED
REPO_RUNTIME_ORCHESTRATOR                      = IMPLEMENTED
REPO_RAW_PERSISTENCE_SINK                      = IMPLEMENTED
REPO_COMMON_RESPONSE_BUILDER                   = IMPLEMENTED
RECORDED_LIVE_NATIVE_RAW_TO_TRADEPLANSTATE_E2E = PASSED
TC4_AND_TC5_REGRESSION_CI                      = PASSED

LIVE_NORMAL_DRILLDOWN_TRIGGER_CASE             = NOT_OBSERVED
AUTOMATIC_LIVE_CONNECTOR_TO_REPO_BINDING       = NOT_IMPLEMENTED
FULL_AUTOMATIC_LIVE_CONNECTOR_E2E              = NOT_PASSED
COMMON_TRADEPLANSTATE_FINAL_SCHEMA             = PROVISIONAL
```

## Connector boundary

The remaining connector gap is deployment/host integration, not strategy design.

The repository intentionally does not import or impersonate a ChatGPT-internal connector SDK. Production qualification requires a Host that can bind the real TradingCursor call to `CallableNativeClient` (or another `TradingCursorNativeClient` implementation) and invoke `run_spot_command()` in the same live execution.

Until that Host integration exists, distinguish:

```text
ChatGPT connected tool live call                    = available
repository runtime service                          = available
recorded live response through repository service   = passed
automatic live connector -> repository service       = not yet bound
```

## Allowed current claim

> TC Spot has a CI-tested repository runtime, immutable Raw persistence, validated mappings for four operational symbol families, a generic Host binding contract, a one-line service entrypoint, proven ChatGPT-side TradingCursor live access, and a recorded-live Native-to-TradePlanState replay E2E. The remaining production gap is the automatic live connector-to-repository Host binding plus one live NORMAL drilldown trigger case.

## Prohibited claim

Do not state:

```text
TC Spot Runtime production ready
TC5 production frozen
fully automatic repo-hosted tc spot operational
full automatic live connector E2E passed
```

until the remaining gates are actually passed.
