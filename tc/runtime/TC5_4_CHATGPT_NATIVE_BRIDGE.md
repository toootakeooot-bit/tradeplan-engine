# TC5-4 — ChatGPT Native Bridge

Status: **PROFILE-ALIGNED / CHATGPT LIVE PATH AVAILABLE / PRODUCTION CLIENT NOT YET BOUND**

## 1. Purpose

TC5-4 defines the boundary by which the ChatGPT runtime invokes TradingCursor Native without changing the frozen TC4 one-call/one-timeframe contract.

The ChatGPT runtime may invoke TradingCursor only with an exact provider/source, exact provider symbol, and one timeframe per call.

Native request contract:

```text
exchange
symbol
interval
```

No MT4 screenshot, uploaded chart image, free prompt, or simultaneous multi-timeframe request is assumed.

## 2. Active profile request sets

The earlier mandatory D1/H4/H1/M15 batch requirement is superseded for TC5 Spot by the active profile architecture.

### NORMAL

Initial calls:

```text
D1 -> Environment
H4 -> Setup
H1 -> Decision
```

Optional drilldown:

```text
M15 -> Confirmation
```

M15 is requested only when explicit H1 Native evidence states that lower-timeframe confirmation is required/pending. Generic WAIT, missing Trigger, or user preference alone does not authorize automatic drilldown.

### SHORT

```text
H4  -> Environment
H1  -> Setup
M15 -> Decision
```

## 3. One-call preservation

Each call remains independent:

```text
1 Native call
-> 1 exact timeframe
-> 1 Native response or explicit Runtime/Transport failure
```

Every obtained response must retain at minimum:

- run/request identity;
- profile;
- role;
- exact timeframe;
- provider/source;
- provider symbol;
- Native completion timestamp;
- full Native response before mapping.

No missing timeframe may be inferred or substituted.

## 4. Provider mapping boundary

TC5 Symbol Resolution occurs before this bridge.

Examples currently validated:

```text
GOLD / GOLD# / XAUUSD / XAU/USD
-> canonical GOLD
-> OANDA / XAUUSD

USDJPY / USDJPY#
-> canonical USDJPY
-> OANDA / USDJPY
```

The Native Bridge receives only the already-resolved exact provider/source and provider symbol. It does not perform silent broker/canonical conversion.

## 5. Current ChatGPT callable path

The connected TradingCursor Native tool supports the exact request dimensions required by this bridge and has successfully returned live responses for OANDA/XAUUSD on 1D, 4h, 1h and 15m, and OANDA/USDJPY on 4h.

Therefore M15 is no longer considered generally unavailable on the ChatGPT path.

This proves **ChatGPT-side Native call capability**, but not a repo-contained Production Native Client implementation.

## 6. Retry boundary

Adapter automatic retry remains NONE under TC4-8.

If the upper runtime explicitly retries a live Native request:

- it is a new request/attempt;
- it receives a new request identity;
- any prior Raw evidence remains preserved;
- the retry must not be represented as the same frozen market observation.

## 7. Failure boundary

The following remain Runtime/Infrastructure failures, never Trade States:

- connector/tool unavailable;
- Native call transport failure;
- unsupported provider symbol;
- unsupported interval;
- Raw preservation failure;
- malformed Native envelope.

Do not convert these failures to WAIT, INVALID or UNDETERMINED.

## 8. Production boundary

The ChatGPT connector is an external invocation surface. Repository code cannot assume that the same connector object is importable or callable from an arbitrary Python/runtime host.

Therefore TC5-4 distinguishes:

```text
CHATGPT_NATIVE_BRIDGE = AVAILABLE
PRODUCTION_NATIVE_CLIENT_BINDING = NOT_YET_IMPLEMENTED
```

A production host must later provide an implementation of the Native Client interface that satisfies the same exchange/symbol/interval and Raw-preservation contract.

## 9. TC4 preservation

TC5-4 does not change:

- TCTradePlanRaw v1.0.0;
- one Native call = one timeframe;
- Original Raw First;
- TC4 Mapping semantics;
- TC4 WAIT/ACTIONABLE/INVALID/UNDETERMINED semantics;
- NODA separation;
- execution boundary.
