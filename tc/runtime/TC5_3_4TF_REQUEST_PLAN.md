# TC5-3 — 4TF Request Planning / ChatGPT Runtime Gate

Status: **OFFLINE PLAN FIXED / LIVE GATE PARTIAL**

ENTRY_PRE request order remains exactly D1->1D, H4->4h, H1->1h, M15->15m, with one Native call per timeframe. The upper runtime owns batch/request correlation only and must not synthesize missing timeframe evidence, substitute another interval, alter Native output, or authorize execution.

Live TradingCursor validation on 2026-09-13: OANDA/XAUUSD D1 completed; H4 completed; H1 completed. The M15 call was blocked by the ChatGPT connector safety layer before a TradingCursor result was returned. Therefore current ChatGPT-orchestrated 4TF live execution is NOT fully cleared. M15 must not be replaced with 30m/1h.

Historical TC4 evidence still contains an observed OANDA/XAUUSD 15m Native result, so this is an orchestration/access gate, not evidence that TradingCursor lacks 15m capability.
