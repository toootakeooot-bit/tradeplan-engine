# TC5-3 4TF Live Gate Audit

Status: **PARTIAL / BLOCKED AT M15**.

2026-09-13 live ChatGPT-orchestrated TradingCursor checks for `OANDA/XAUUSD`: D1 completed, H4 completed, H1 completed. M15 was blocked by the ChatGPT connector safety layer before a TradingCursor result was returned.

Hard gate: ENTRY_PRE requires exactly D1/H4/H1/M15. No nearest-timeframe substitution is allowed. Current live run is therefore rejected as incomplete; no combined Entry-Pre decision may be synthesized from only three TFs.

Historical TC4 evidence already contains a completed OANDA/XAUUSD 15m Native result, so the blocker is the current ChatGPT orchestration/access path, not evidence that TradingCursor lacks 15m capability.
