# TC5-13 — Device / Session Independent Native-first Regression Guard

Status: **IMPLEMENTED — REGRESSION GUARD ADDED**

## 1. Purpose

Prevent recurrence of the TC Spot failure pattern where an accepted command is stopped before TradingCursor Native is called because the Host believes that the chart, Market Input, full screen, mobile display, or chat session context is insufficient.

Observed failure pattern:

```text
tc スポット GOLD# エントリー前
-> no uploaded chart / no prepared Market Input / screen not fully visible
-> STOP
```

This pattern is invalid for TC Spot Host mode.

## 2. Fixed invariant

For every accepted command:

```text
tc スポット <symbol> [通常|短期] エントリー前
```

execution order is fixed as:

```text
Command parse
-> Symbol resolve
-> Native request plan
-> actual TradingCursor Native attempt
-> only then provider/runtime failure may be reported
```

The following are non-authoritative Host context and MUST NOT decide whether Native acquisition is attempted:

- mobile vs desktop;
- screen size or whether the full chart is visible;
- new chat vs existing chat;
- session history length;
- presence or absence of an uploaded chart;
- presence or absence of pre-supplied Market Input.

TradingCursor Native is the live Market Input source for TC Spot.

## 3. GOLD NORMAL regression case

Input:

```text
tc スポット GOLD# エントリー前
```

Mandatory initial plan:

```text
GOLD#
-> canonical GOLD
-> OANDA / XAUUSD
-> 1D
-> 4h
-> 1h
```

`15m` remains conditional under the existing NORMAL drilldown rule.

The initial plan must be identical whether the command is submitted from a mobile or desktop client and whether the chat is a new or existing session.

## 4. SHORT regression case

Input:

```text
tc スポット GOLD# 短期 エントリー前
```

Mandatory initial plan:

```text
OANDA / XAUUSD
-> 4h
-> 1h
-> 15m
```

## 5. Prohibited pre-Native stop reasons

With zero observed Native attempts, the Host must not stop for reasons such as:

```text
チャート入力がない
Market Input がない / 未取得
スマホでは全体が見えない
画面が小さい
セッション情報が足りない
uploaded chart missing
pre-supplied Market Input missing
```

Such a stop is classified as:

```text
NATIVE_FIRST_VIOLATION
```

A zero-attempt Host stop with another reason is still invalid and is classified as:

```text
NATIVE_ATTEMPT_NOT_OBSERVED
```

## 6. Allowed failure boundary

A provider/runtime failure may be reported only after at least one actual Native call attempt has occurred.

When the first required call fails, the result must identify the actual failed provider/symbol/interval and remain outside Trade State.

Example:

```text
attempted Native: OANDA / XAUUSD / 1D
provider response: unavailable/error
-> Runtime/Provider failure
```

No web-price substitute, chart-image substitute, NODA substitute, or interval substitution is allowed.

## 7. Implementation

Runtime guard:

```text
tc/runtime/host_guard.py
```

The guard provides:

- `prepare_native_first_execution(...)`
  - parses the accepted TC Spot command;
  - resolves the canonical/provider symbol;
  - produces the mandatory initial Native plan without using device/session/chart context.

- `assert_native_first_failure_boundary(...)`
  - rejects any reported failure when no Native attempt has been observed;
  - gives a specific `NATIVE_FIRST_VIOLATION` classification to device/session/chart/Market Input shortcut stops.

Regression tests:

```text
tests/tc5_runtime/test_host_native_first_guard.py
```

Covered cases:

1. GOLD NORMAL -> OANDA/XAUUSD -> 1D/4h/1h;
2. repeated mobile/desktop session-equivalent preparation is identical;
3. GOLD SHORT -> 4h/1h/15m;
4. no-chart pre-Native STOP is rejected;
5. mobile/full-screen pre-Native STOP is rejected;
6. actual provider failure after a Native attempt is allowed;
7. any unexplained zero-attempt Host stop is rejected.

The existing TC5 runtime GitHub Actions discovery includes this test file automatically.

## 8. Scope boundary

This guard strengthens the repository and ChatGPT Host contract. It does not claim control over the ChatGPT client UI itself and does not infer that mobile and desktop clients expose identical UI surfaces.

The required operational invariant is narrower and testable:

> Client/device/session presentation must never be used as a reason to skip the TradingCursor Native-first sequence for an accepted TC Spot command.

## 9. Completion criteria

TC5-13 is complete when:

- the guard module exists;
- the regression tests exist;
- TC5-10 references the device/session-independent invariant;
- the TC5 runtime regression suite passes on `feature/tc-v1`.
