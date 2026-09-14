# TC5-13 Device / Session Independent Native-first Guard — Audit

Status: **PASS**

## Scope

Target repository:

```text
toootakeooot-bit/tradeplan-engine
```

Target branch:

```text
feature/tc-v1
```

Validated implementation head before this audit record:

```text
dc069a8cfcfd661f85cb8e75488a16294cef8388
```

## Implemented controls

1. Added `tc/runtime/host_guard.py`.
2. Added `tests/tc5_runtime/test_host_native_first_guard.py`.
3. Added `tc/runtime/TC5_13_DEVICE_SESSION_NATIVE_FIRST_GUARD.md`.
4. Updated `tc/runtime/TC5_10_CHATGPT_HOST_BINDING.md` with device/session independence.

## Fixed invariant

An accepted TC Spot command must produce and attempt its TradingCursor Native plan before any Market Input availability failure is reported.

The following are explicitly non-authoritative:

- mobile vs desktop;
- screen size / full-chart visibility;
- new vs existing chat session;
- visible session history;
- uploaded chart presence;
- pre-supplied Market Input presence.

A zero-attempt STOP tied to those conditions is classified as:

```text
NATIVE_FIRST_VIOLATION
```

Any other zero-attempt failure is classified as:

```text
NATIVE_ATTEMPT_NOT_OBSERVED
```

## Regression coverage

The runtime regression includes:

- GOLD# NORMAL -> OANDA/XAUUSD -> 1D/4h/1h;
- repeated session/device-equivalent preparation -> identical Native plan;
- GOLD# SHORT -> 4h/1h/15m;
- no-chart pre-Native STOP -> rejected;
- mobile/full-screen pre-Native STOP -> rejected;
- provider failure after an actual Native attempt -> allowed;
- unexplained zero-attempt Host STOP -> rejected.

## CI evidence

GitHub Actions workflow:

```text
TC5 Runtime Regression
run #38
run id: 34838491313
head: dc069a8cfcfd661f85cb8e75488a16294cef8388
```

Result:

```text
PASS
```

All workflow stages completed successfully, including:

- TC4 regression;
- TC5 profile aggregation regression;
- TC5 static pipeline regression;
- TC5 runtime core regression;
- TC5 notification regression.

## Audit conclusion

TC5-13 successfully converts the observed mobile/session pre-Native STOP pattern into an explicit regression violation and makes the initial Native request plan independent of device/session/chart presentation context.

Residual boundary: the repository cannot control the ChatGPT client UI itself. The enforceable contract is that an accepted TC Spot command must not use client/session presentation as a reason to skip the Native-first sequence.
