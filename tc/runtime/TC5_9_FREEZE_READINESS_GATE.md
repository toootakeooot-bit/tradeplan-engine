# TC5-9 — Runtime Freeze Readiness Gate

Status: **FROZEN — TC SPOT v1 CHATGPT ON-DEMAND OPERATIONAL BASELINE**

Freeze date: 2026-09-13

This Freeze is intentionally limited to user-triggered TC Spot operation in ChatGPT.

It does **not** claim autonomous/background/repo-hosted connector operation.

## 1. Frozen operational scope

Supported host mode:

```text
User explicitly requests TC Spot in ChatGPT
-> ChatGPT Host invokes TradingCursor Native
-> TC4 frozen semantics + TC5 runtime policy are applied
-> user receives TC Spot result
```

Examples:

```text
tc スポット GOLD# エントリー前
tc スポット GOLD# 短期 エントリー前
```

Out of scope:

- scheduled/background execution;
- autonomous monitoring;
- operation without an explicit user request;
- direct order execution;
- autonomous repo-hosted TradingCursor connector.

## 2. Profile contract

NORMAL:

```text
D1 -> Environment
H4 -> Setup
H1 -> Decision
M15 -> only if H1 explicitly requires lower-timeframe confirmation
```

SHORT:

```text
H4 -> Environment
H1 -> Setup
M15 -> Decision
```

One Native call remains one timeframe. No interval substitution is allowed.

## 3. Validated symbol/provider registry

```text
GOLD / GOLD# / XAUUSD / XAU/USD -> OANDA / XAUUSD
USDJPY / USDJPY#                 -> OANDA / USDJPY
US100Cash / US100Cash# / NAS100 -> PEPPERSTONE / NAS100
JP225Cash / JP225Cash# / JPN225 -> PEPPERSTONE / JPN225
```

Original user/broker symbol remains traceable. Terminal `#` remains broker suffix normalization before canonical resolution.

## 4. Repository runtime baseline

Implemented and regression-covered:

```text
tc/adapter/native_client.py
tc/adapter/adapter.py
tc/normalizer/normalizer.py
tc/runtime/command.py
tc/runtime/symbol.py
tc/runtime/planner.py
tc/runtime/orchestrator.py
tc/runtime/raw_sink.py
tc/runtime/host_binding.py
tc/runtime/service.py
tc/runtime/response.py
tc/runtime/aggregate.py
```

Reference repository path:

```text
Command
-> Symbol Resolver
-> Planner
-> Orchestrator
-> Native Client
-> Raw persistence
-> Adapter
-> Normalizer
-> Role Aggregation
-> TradePlanState
```

## 5. Fresh Live qualification

TC5-10 audit passed using fresh GOLD runs on 2026-09-13.

NORMAL Live:

```text
D1  -> OANDA/XAUUSD -> completed
H4  -> OANDA/XAUUSD -> completed
H1  -> OANDA/XAUUSD -> completed
```

Captured:

```text
fixtures/tc5_live/TC5-LIVE-NORMAL-GOLD-20260913-0553Z.json
```

Recorded-live replay through the repository Runtime: **PASS**.

SHORT Live:

```text
H4  -> OANDA/XAUUSD -> completed
H1  -> OANDA/XAUUSD -> completed
M15 -> OANDA/XAUUSD -> completed
```

Captured:

```text
fixtures/tc5_live/TC5-LIVE-SHORT-GOLD-20260913-0554Z.json
```

Recorded-live replay through the repository Runtime: **PASS**.

## 6. State semantics retained

```text
ACTIONABLE   -> TRADE
WAIT         -> WAIT
INVALID      -> INVALID
UNDETERMINED -> HOLD / 判定保留
```

`TRADE` / `ACTIONABLE` never means execution permission.

Environment and Setup remain role evidence. TC5-9 does not add majority voting or an Environment/Setup alignment gate.

## 7. Regression qualification

GitHub Actions run 25 on head:

```text
a149c98f248d677cbc6efd0bd45a674f2b0e193a
```

completed successfully.

Verified regression scope includes:

- TC4 TCREG regression;
- TC5 Profile aggregation;
- TC5 static pipeline;
- TC5 runtime core;
- Host binding;
- immutable Raw persistence;
- validated symbol registry;
- one-line service entrypoint;
- fresh NORMAL recorded-live replay;
- fresh SHORT recorded-live replay.

## 8. Hard Gate result

```text
TC4-9 Freeze unchanged                         = PASS
NODA contamination                             = PASS / NONE
NORMAL Live sequence                           = PASS
SHORT Live sequence                            = PASS
M15 Native access                              = PASS
Fresh NORMAL Raw-to-TradePlanState replay      = PASS
Fresh SHORT Raw-to-TradePlanState replay       = PASS
TC4 + TC5 regression CI                        = PASS
Runtime failure != Trade State                 = PASS
Execution permission outside TC Spot           = PASS
User-triggered-only Host scope                  = PASS
```

## 9. Non-blocking follow-up observations

### NORMAL live drilldown case

A naturally occurring H1 Native response explicitly requesting lower-timeframe confirmation has not yet been observed live.

This is **not a Freeze blocker** for ChatGPT On-Demand v1 because:

- the branch is deterministic-regression tested;
- M15 Native access is proven;
- TC5-7 already fixes the exact trigger and release/HOLD behavior.

When such a case naturally appears during future spot use, record it as an operational regression fixture.

### Common TradePlanState

The TC-facing common output remains compatible with the provisional TradePlanState direction. Final cross-engine Common schema may later be fixed together with NODA without reopening TC Engine v1 semantics.

## 10. Explicit non-claims

This Freeze does **not** mean:

```text
background TC monitoring is enabled
autonomous scheduled TC Spot is enabled
repo Python directly imports a ChatGPT-internal TradingCursor SDK
automatic trade execution is permitted
Common schema is permanently frozen for every future engine
```

## 11. Freeze conclusion

> TC Spot v1 is operationally frozen for explicit user-triggered use in ChatGPT. NORMAL and SHORT Live Native sequences and fresh recorded-live repository replays have passed. The user may invoke TC Spot on demand without MT4 screenshots. Autonomous/background connector operation remains outside this baseline.
