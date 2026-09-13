# TC5-9 — Runtime Freeze Readiness Gate

Status: **NOT READY TO FREEZE / GATES EXPLICIT**

TC5-9 must not declare TC Spot Runtime production-ready merely because TC5-1 through TC5-8 static/historical work passes.

## Freeze prerequisites

All of the following are required before a TC5 runtime freeze:

1. one coherent current D1/H4/H1/M15 TradingCursor batch completes through the intended runtime path;
2. each call is traceable to one batch/run identity and exact timeframe;
3. no interval substitution occurs;
4. Raw/Adapter handling is production-connected or the freeze is explicitly labelled non-production;
5. runtime/infrastructure failures remain separate from Trade State;
6. symbol normalization/provider mapping provenance is retained;
7. TC4 regression guardrails remain intact;
8. NODA remains separated;
9. execution permission remains outside TC Spot;
10. if a single combined 4TF trade recommendation is desired, its semantics must be separately approved and tested. TC5-7 aggregation alone is not such a strategy rule.

## Current blocking items

```text
LIVE_COHERENT_4TF_BATCH = NOT_PASSED
PRODUCTION_NATIVE_CLIENT_PATH = NOT_IMPLEMENTED
PRODUCTION_PERSISTENCE_LOGGING = NOT_IMPLEMENTED
COMBINED_4TF_TRADE_DECISION = NOT_DEFINED (intentional unless separately authorized)
```

## Allowed current claim

The strongest allowed claim is:

> TC Spot Runtime command, symbol resolution, exact 4TF planning, non-strategy aggregation and response boundaries have a static/historical regression baseline; production/live end-to-end qualification remains open.

## Prohibited claim

Do not state:

```text
TC Spot Runtime production ready
TC5 frozen
fully automatic tc spot operational
combined 4TF LONG/SHORT/WAIT available
```

until the corresponding gates are actually passed.
