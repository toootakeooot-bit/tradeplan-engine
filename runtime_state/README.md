# TC5 Runtime State

This branch is the operational state store for the ChatGPT Host TC5-16 runtime. It is intentionally separate from implementation branches and must not be merged into feature history merely to move runtime state.

Authoritative runtime files:

- `runtime_state/tc5_host_cache.json` — shared Periodic/Spot timeframe cache.
- `runtime_state/tc_usage_ledger.json` — locally observed successful TradingCursor Native calls for the current 00:00 UTC / 09:00 JST quota window.
- `runtime_state/raw/` — immutable per-run Native response bundles created by the Host before cache normalization/update.

## Host invariants

1. Periodic and Spot must read the same cache file before deciding LIVE vs CACHE.
2. A successful LIVE result must be preserved in an immutable raw bundle before the cache record is updated.
3. Cache reads must preserve original `fetched_at`; CACHE is never represented as LIVE.
4. Failed LIVE acquisition sets `retry_pending`; there is no same-slot retry loop.
5. Successful Periodic or Spot acquisition clears matching `retry_pending`.
6. M15 is LIVE only when NORMAL H1 explicitly requires lower-timeframe confirmation.
7. The usage ledger counts only observed successful Native responses. It is not provider-authoritative if calls occur outside this Host.
8. Execution permission remains NO.

## Fixed JST schedule

- 05:03 — H1
- 09:03 — D1/H4/H1
- 12:03 — H1
- 17:03 — H4/H1
- 21:03 — H4/H1

Targets: GOLD, USDJPY, US100. Base scheduled budget: 27 successful Native calls/day before M15, retry, conditional H4 refresh, or Spot calls.
