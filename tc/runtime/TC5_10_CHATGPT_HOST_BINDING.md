# TC5-10 — ChatGPT Host Binding / On-Demand Live E2E

Status: **FIXED — CHATGPT ON-DEMAND HOST MODE**

## 1. Scope

TC Spot is started only by an explicit user command in ChatGPT.

Supported examples:

```text
tc スポット GOLD# エントリー前
tc スポット GOLD# 短期 エントリー前
```

Out of scope:

- scheduled execution;
- background monitoring;
- autonomous wake-up;
- operation while ChatGPT is not being used;
- automatic order execution.

## 2. Host responsibility

ChatGPT is the operational Host. On an explicit TC Spot command it must:

1. parse the command under TC5-1;
2. resolve the symbol under the validated TC5 symbol registry;
3. issue the required TradingCursor Native calls exactly by profile;
4. preserve Native responses as the source of truth;
5. apply the frozen TC4 mapping/state semantics and TC5 role policy;
6. return the TC Spot result to the user.

ChatGPT must not inject web analysis, NODA rules, independent technical judgment, or a substitute interval into TC Spot.

## 3. Profile call contract

NORMAL:

```text
D1 -> Environment
H4 -> Setup
H1 -> Decision
M15 -> only when H1 explicitly requires lower-timeframe confirmation
```

SHORT:

```text
H4 -> Environment
H1 -> Setup
M15 -> Decision
```

One Native call remains one timeframe.

## 4. Repository runtime equivalence

The repository service path remains the reference implementation:

```text
Command
-> Symbol Resolver
-> Planner
-> Orchestrator
-> Native Client
-> Raw Sink
-> Adapter
-> Normalizer
-> Role Aggregation
-> TradePlanState
```

The ChatGPT Host must preserve the same semantics even though the external TradingCursor connector is invoked by the ChatGPT host rather than imported by repository Python code.

## 5. Operational symbol registry

```text
GOLD / GOLD# / XAUUSD / XAU/USD -> OANDA / XAUUSD
USDJPY / USDJPY#                 -> OANDA / USDJPY
US100Cash / US100Cash# / NAS100 -> PEPPERSTONE / NAS100
JP225Cash / JP225Cash# / JPN225 -> PEPPERSTONE / JPN225
```

Terminal `#` remains broker suffix normalization before canonical resolution.

## 6. State boundary

Decision state mapping remains:

```text
ACTIONABLE   -> TRADE
WAIT         -> WAIT
INVALID      -> INVALID
UNDETERMINED -> HOLD / 判定保留
```

ACTIONABLE / TRADE never grants execution permission.

Environment and Setup are retained as role evidence. TC5-10 does not add a new alignment/voting gate.

## 7. Freeze qualification for this host mode

ChatGPT On-Demand Host mode may be frozen when all are true:

- NORMAL Live Native sequence observed;
- SHORT Live Native sequence observed;
- NORMAL recorded-live Raw-to-TradePlanState replay PASS;
- SHORT recorded-live Raw-to-TradePlanState replay PASS;
- TC4 + TC5 CI regression PASS;
- no NODA contamination;
- no interval substitution;
- runtime failures remain outside Trade State;
- execution remains outside TC Spot.

A naturally occurring NORMAL drilldown Live example is an operational follow-up test, not a blocker for initial on-demand Freeze, because the branch path is already covered by deterministic regression.

## 8. Explicit limitation

This Freeze does **not** claim an autonomous repo-hosted TradingCursor connector. It qualifies only the user-triggered ChatGPT Host workflow.
