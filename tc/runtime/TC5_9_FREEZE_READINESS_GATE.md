# TC5-9 — Runtime Freeze Readiness Gate

Status: **NOT READY TO FREEZE / PROFILE GATES EXPLICIT**

TC5-9 must not declare TC Spot Runtime production-ready merely because static/historical work passes.

## Freeze prerequisites

All of the following are required before a TC5 runtime freeze:

1. one coherent current NORMAL run completes through D1/H4/H1 using the intended runtime path;
2. one coherent current SHORT run completes through H4/H1/M15 using the intended runtime path;
3. one NORMAL drilldown case is verified where explicit H1 lower-timeframe confirmation evidence causes an M15 request and the result is handled by TC5-7 policy;
4. each Native call remains traceable to run/profile/role/timeframe identity;
5. no interval substitution occurs;
6. Raw/Adapter handling is production-connected or the freeze is explicitly labelled non-production;
7. runtime/infrastructure failures remain separate from TradePlanState;
8. symbol normalization/provider mapping provenance is retained;
9. TC4 regression guardrails remain intact;
10. NODA remains separated;
11. execution permission remains outside TC Spot;
12. common output remains compatible with the provisional TradePlanState direction without finalizing Common solely around TC.

## Current blocking items

```text
LIVE_NORMAL_PROFILE_E2E = NOT_PASSED
LIVE_SHORT_PROFILE_E2E = NOT_PASSED
LIVE_NORMAL_DRILLDOWN_E2E = NOT_PASSED
PRODUCTION_NATIVE_CLIENT_PATH = NOT_IMPLEMENTED
PRODUCTION_PERSISTENCE_LOGGING = NOT_IMPLEMENTED
COMMON_TRADEPLANSTATE_FINAL_SCHEMA = PROVISIONAL
```

The prior `LIVE_COHERENT_4TF_BATCH` requirement is superseded by the active profile architecture amendment.

## Allowed current claim

> TC Spot Runtime now has profile-based command parsing, symbol/provider resolution, NORMAL/SHORT request planning, role-based aggregation semantics and common-output boundaries; production/live end-to-end qualification remains open.

## Prohibited claim

Do not state:

```text
TC Spot Runtime production ready
TC5 frozen
fully automatic tc spot operational
NORMAL/SHORT live E2E qualified
```

until the corresponding gates are actually passed.
