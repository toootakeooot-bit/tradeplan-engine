# TC5-9 — Runtime Freeze Readiness Gate

Status: **NOT READY FOR PRODUCTION FREEZE / CHATGPT-SIDE RUNTIME SUBSTANTIALLY ADVANCED**

TC5-9 must not declare TC Spot Runtime production-ready merely because static regression and ChatGPT-side Native calls pass.

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
GOLD family -> OANDA / XAUUSD
NORMAL: D1 -> H4 -> H1   = LIVE CALLS COMPLETED
SHORT : H4 -> H1 -> M15  = LIVE CALLS COMPLETED
```

Observed NORMAL decision evidence on H1 contained explicit waiting-for-confirmation wording, supporting the existing TC4 WAIT semantics.

Observed SHORT decision evidence on M15 contained an explicit current-price LONG recommendation, supporting the existing TC4 ACTIONABLE semantics.

These executions prove the ChatGPT-side Native request path and active profile interval availability. They do **not** yet prove the repo-contained orchestrator is directly bound to the same connector or that the live Native responses were automatically persisted through the production Raw sink.

### Repository runtime implementation

Implemented:

```text
tc/adapter/native_client.py       Native Client host interface
tc/adapter/adapter.py             Raw-preserving TCTradePlanRaw wrapper
tc/normalizer/normalizer.py       conservative mapping/state semantics
tc/runtime/orchestrator.py        NORMAL/SHORT + conditional drilldown flow
tc/runtime/response.py            provisional common TradePlanState builder
```

The Orchestrator requires a host-supplied Native Client implementation and RawSink. This preserves the boundary between repository logic and the external ChatGPT connector binding.

### Regression

GitHub Actions workflow `TC5 Runtime Regression` runs:

- TC4 TCREG regression;
- TC5 profile aggregation regression;
- TC5 static pipeline regression;
- TC5 runtime core regression.

Run 2 on commit `e510d3f0edbdb3757be2db0ad358ff154deecb62` completed successfully across all four steps.

## Current gates

```text
CHATGPT_NATIVE_NORMAL_SEQUENCE          = PASSED
CHATGPT_NATIVE_SHORT_SEQUENCE           = PASSED
CHATGPT_M15_ACCESS                      = PASSED
REPO_NATIVE_CLIENT_INTERFACE            = IMPLEMENTED
REPO_ADAPTER                            = IMPLEMENTED
REPO_NORMALIZER                         = IMPLEMENTED
REPO_RUNTIME_ORCHESTRATOR               = IMPLEMENTED
REPO_COMMON_RESPONSE_BUILDER            = IMPLEMENTED
TC4_AND_TC5_REGRESSION_CI               = PASSED

LIVE_NORMAL_DRILLDOWN_TRIGGER_CASE      = NOT_OBSERVED
LIVE_CONNECTOR_TO_REPO_CLIENT_BINDING   = NOT_IMPLEMENTED
LIVE_RAW_PERSISTENCE_SINK               = NOT_IMPLEMENTED
FULL_LIVE_RAW->ADAPTER->NORMALIZER_E2E  = NOT_PASSED
COMMON_TRADEPLANSTATE_FINAL_SCHEMA      = PROVISIONAL
```

## Clarification of E2E terminology

A manual/ChatGPT-side sequence of successful Native calls is not labeled a full production E2E unless the same execution is automatically passed through:

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

This distinction prevents a successful connector experiment from being mislabeled as a production runtime qualification.

## Allowed current claim

> TC Spot now has a tested repository runtime core and a separately proven ChatGPT-side TradingCursor Native path for NORMAL and SHORT profiles. The remaining production gap is the concrete connector/client binding plus live Raw persistence and one naturally/explicitly triggered NORMAL drilldown E2E case.

## Prohibited claim

Do not state:

```text
TC Spot Runtime production ready
TC5 production frozen
fully automatic repo-hosted tc spot operational
full live Raw-to-TradePlanState E2E passed
```

until the remaining gates are actually passed.
