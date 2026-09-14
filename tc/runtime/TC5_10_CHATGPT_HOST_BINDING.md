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
6. account for successful Native-call consumption under TC5-11;
7. return the TC Spot result and Runtime usage block to the user.

ChatGPT must not inject web analysis, NODA rules, independent technical judgment, or a substitute interval into TC Spot.

### 2.1 Mandatory Native-first execution guard

For every accepted `tc スポット ... エントリー前` command, the Host **MUST attempt the TradingCursor Native call sequence before declaring Market Input unavailable**.

The following shortcut is prohibited:

```text
no uploaded chart / no pre-supplied Market Input
-> MARKET_INPUT_MISSING
-> NO DECISION
```

Absence of a user-uploaded chart or pre-supplied Market Input is **not** an input failure. TradingCursor Native is the live Market Input source for TC Spot Host mode.

A Market Input / provider failure may be reported only after an actual required Native call has been attempted and that call has returned an error, invalid response, or unavailable result.

When a required Native call fails:

- classify it as a runtime/provider failure, outside Trade State;
- do not fabricate `WAIT`, `INVALID`, or `UNDETERMINED` from missing data;
- do not substitute web prices, web technical analysis, NODA analysis, uploaded charts, or another interval;
- report the failed provider/symbol/interval and stop the affected TC Spot run.

This guard is fail-closed: **Native call first; provider/runtime error only after observed failure; no substitute analysis.**

### 2.2 Device / session independence

The Native-first decision is independent of client presentation and chat-session state.

The following MUST NOT be used as a reason to skip or stop before the Native sequence:

- mobile vs desktop client;
- screen size or whether the full chart is visible;
- new chat vs existing chat;
- session length or visible history;
- absence of an uploaded chart;
- absence of pre-supplied Market Input.

For an accepted TC Spot command, device/session/chart context is non-authoritative. The Host must produce the provider/timeframe plan and attempt TradingCursor Native first.

A zero-attempt stop for `チャート入力がない`, `Market Input未取得`, `スマホでは全体が見えない`, or equivalent reasons is a **Native-first regression violation** under TC5-13.

See:

```text
tc/runtime/TC5_13_DEVICE_SESSION_NATIVE_FIRST_GUARD.md
tc/runtime/host_guard.py
tests/tc5_runtime/test_host_native_first_guard.py
```

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

For NORMAL, M15 is conditional and its absence is not Market Input missing unless H1 explicitly requires lower-timeframe confirmation and the required M15 Native call then fails.

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

### 4.1 Usage accounting boundary

TC usage accounting is Host Runtime telemetry, not TradePlanState.

The Host must count a Native call as consumed only after the TradingCursor Native client returns a non-empty response mapping. The count boundary is before Raw preservation, Adapter mapping and Normalizer execution so a provider call already consumed is not lost if a downstream stage fails.

The current local budget policy is:

```text
daily limit: 50 Native calls
reset: 00:00 UTC = 09:00 JST
scheduled reserve: 20 calls by default
spot conversion: 3 Native calls = approximately 1 spot
```

For each completed run:

```text
used_today_after = used_today_before + current_run_successful_calls
remaining_raw = max(0, 50 - used_today_after)
remaining_after_schedule = max(0, remaining_raw - scheduled_reserve_remaining)
spot_equivalent = floor(remaining_after_schedule / 3)
```

The Host may replace the default 20-call scheduled reserve with a known remaining scheduled workload. Scheduled calls actually consumed belong in the daily used count; only future/pending scheduled calls remain in the reserve.

If the Host cannot establish `used_today_before`, it must not invent a remaining quota. It still displays exact current-run consumption and marks remaining/spot-equivalent as `不明`.

This is a local operational budget model because TradingCursor Native does not provide a dedicated remaining-quota lookup contract in the current integration.

## 5. Operational symbol registry

```text
GOLD / GOLD# / XAUUSD / XAU/USD     -> OANDA / XAUUSD
USDJPY / USDJPY#                    -> OANDA / USDJPY
US100 / US100Cash / US100Cash# / NAS100 -> PEPPERSTONE / NAS100
JP225Cash / JP225Cash# / JPN225    -> PEPPERSTONE / JPN225
```

`US100`, `US100Cash`, and `US100Cash#` are operationally equivalent user inputs for the same canonical `US100` instrument. `NAS100` remains the provider-facing alias family member and routes to the same provider symbol.

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

Runtime/provider failure is not a Trade State and must not be converted into WAIT/HOLD/INVALID merely because Market Input is absent.

Usage exhaustion or usage-accounting uncertainty also remains Runtime state and must never be mapped into a Trade State.

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

## 8. Host regression invariant

The following command is a mandatory regression case:

```text
tc スポット GOLD# エントリー前
```

Expected Host behavior:

```text
GOLD#
-> OANDA / XAUUSD
-> Native 1D
-> Native 4h
-> Native 1h
-> Native 15m only if H1 explicitly requires drilldown
-> TC4/TC5 mapping and TradePlanState
-> Runtime usage block
```

The run must never stop merely because the user supplied no chart or no separate prepared Market Input.

The same invariant applies regardless of mobile/desktop client or new/existing chat session. Those presentation/session differences must not alter the initial Native request plan or authorize a pre-Native STOP.

Equivalent aliases (`GOLD`, `GOLD#`, `XAUUSD`, `XAU/USD`) must enter the same provider route. `USDJPY` and `USDJPY#` must likewise enter the same provider route.

For US100, all of the following commands must resolve identically before Native calls:

```text
tc スポット US100 エントリー前
tc スポット US100Cash エントリー前
tc スポット US100Cash# エントリー前
```

All three must resolve to:

```text
canonical US100
-> PEPPERSTONE / NAS100
```

## 9. Explicit limitation

This Freeze does **not** claim an autonomous repo-hosted TradingCursor connector. It qualifies only the user-triggered ChatGPT Host workflow.
