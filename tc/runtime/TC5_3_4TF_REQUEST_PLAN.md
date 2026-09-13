# TC5-3 — Profile Request Planning / ChatGPT Runtime Gate

Status: **REVISED / ROLE-BASED REQUEST PLAN**

TC Spot no longer requires an unconditional D1/H4/H1/M15 batch.

## NORMAL

Initial request order:

```text
D1 -> 1D   (Environment)
H4 -> 4h   (Setup)
H1 -> 1h   (Decision)
```

M15 -> 15m is requested only when the H1 Native evidence explicitly requires lower-timeframe confirmation. A generic WAIT, missing Trigger, or Runtime uncertainty does not by itself trigger M15.

## SHORT

Initial request order:

```text
H4  -> 4h   (Environment)
H1  -> 1h   (Setup)
M15 -> 15m  (Decision)
```

Each timeframe remains one independent TradingCursor Native call. The upper runtime owns request order, roles, batch correlation, and optional drilldown only. It must not substitute intervals, fabricate missing evidence, alter Native output, inject NODA, or authorize execution.

Historical and live TC observations already establish that OANDA/XAUUSD is callable on 1D/4h/1h/15m. Runtime qualification must now be tested by profile, not by requiring all four timeframes in every NORMAL run.
