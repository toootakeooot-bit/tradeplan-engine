# TC5-4 — ChatGPT Native Bridge

Status: **DESIGN FIXED / LIVE EXECUTION BLOCKED AT M15**

The ChatGPT runtime may invoke TradingCursor only with the exact provider source/symbol and one timeframe per call. For ENTRY_PRE the mandatory set is D1/H4/H1/M15. Every response must retain timeframe/source/symbol/timestamp and must remain separate; no missing timeframe may be inferred or substituted.

Current observed path on 2026-09-13 for OANDA/XAUUSD: D1, H4 and H1 completed. M15 was blocked by the ChatGPT connector safety layer before a Native result was returned. Therefore no valid 4TF batch and no combined Entry-Pre result may be emitted from this run.

When M15 access is available, the next valid run must make four fresh calls as one new batch. Historical M15 must not be mixed with current D1/H4/H1. Adapter retry remains NONE; any upper retry is a new request and prior evidence is retained.
