# TC5-9 — Runtime Freeze Readiness Gate

Status: **NOT READY FOR PRODUCTION FREEZE / CHATGPT-SIDE RUNTIME CORE COMPLETE ENOUGH FOR HOST BINDING**

TC5-9 must not declare TC Spot Runtime production-ready merely because repository regression and ChatGPT-side Native calls pass.

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

Observed NORMAL H1 evidence explicitly supported WAIT semantics. Observed SHORT M15 evidence explicitly supported provisional ACTIONABLE semantics. ACTIONABLE remains distinct from execution permission.

These executions prove the ChatGPT-side Native request path and active profile interval availability. They do **not** yet prove that the repo-contained Orchestrator is directly bound to the external connector in one automatic live run.

### Repository runtime implementation

Implemented:

```text
tc/adapter/native_client.py       Native Client host interface
tc/adapter/adapter.py             Raw-preserving TCTradePlanRaw wrapper
tc/normalizer/normalizer.py       conservative mapping/state semantics
tc/runtime/orchestrator.py        NORMAL/SHORT + conditional drilldown flow
tc/runtime/raw_sink.py            immutable file Raw persistence sink
tc/runtime/response.py            provisional common TradePlanState builder
```

The Orchestrator requires a host-supplied Native Client implementation. `FileRawSink` is available for stable Raw persistence and refuses overwrite of existing artifacts.

### Regression

GitHub Actions workflow `TC5 Runtime Regression` covers:

- TC4 TCREG regression;
- TC5 profile aggregation regression;
- TC5 static pipeline regression;
- TC5 runtime core regression, including Raw persistence and symbol registry tests.

Verified successful runs include:

```text
run 2   head e510d3f0edbdb3757be2db0ad358ff154deecb62  PASS
run 12  head ebb76694c8766252299746743106c4bf14bc75df  PASS
```

## Current gates

```text
CHATGPT_NATIVE_NORMAL_SEQUENCE          = PASSED
CHATGPT_NATIVE_SHORT_SEQUENCE           = PASSED
CHATGPT_M15_ACCESS                      = PASSED
VALIDATED_SYMBOL_PROVIDER_REGISTRY      = PASSED (4 operational families)
REPO_NATIVE_CLIENT_INTERFACE            = IMPLEMENTED
REPO_ADAPTER                            = IMPLEMENTED
REPO_NORMALIZER                         = IMPLEMENTED
REPO_RUNTIME_ORCHESTRATOR               = IMPLEMENTED
REPO_RAW_PERSISTENCE_SINK               = IMPLEMENTED
REPO_COMMON_RESPONSE_BUILDER            = IMPLEMENTED
TC4_AND_TC5_REGRESSION_CI               = PASSED

LIVE_NORMAL_DRILLDOWN_TRIGGER_CASE      = NOT_OBSERVED
LIVE_CONNECTOR_TO_REPO_CLIENT_BINDING   = NOT_IMPLEMENTED
FULL_LIVE_RAW->ADAPTER->NORMALIZER_E2E  = NOT_PASSED
COMMON_TRADEPLANSTATE_FINAL_SCHEMA      = PROVISIONAL
```

## Clarification of E2E terminology

A ChatGPT-side sequence of successful Native calls is not labeled a full production E2E unless the same execution is automatically passed through:

```text
Command
-> Symbol Resolver
-> Runtime Orchestrator
-> concrete Native Client binding
-> Raw persistence
-> Adapter
-> Normalizer
-> Role Aggregation
-> TradePlanState response
```

## Allowed current claim

> TC Spot now has a CI-tested repository runtime core, stable Raw persistence implementation, four validated operational symbol/provider mappings, and separately proven ChatGPT-side TradingCursor Native sequences for NORMAL and SHORT. The main remaining production gap is the concrete external connector/client binding, followed by one full live Raw-to-TradePlanState E2E and one naturally/explicitly triggered NORMAL drilldown case.

## Prohibited claim

Do not state:

```text
TC Spot Runtime production ready
TC5 production frozen
fully automatic repo-hosted tc spot operational
full live Raw-to-TradePlanState E2E passed
```

until the remaining gates are actually passed.
