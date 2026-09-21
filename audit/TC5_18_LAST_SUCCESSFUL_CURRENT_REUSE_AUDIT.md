# TC5-18 Last-Successful CURRENT Reuse Audit

Repository: `toootakeooot-bit/tradeplan-engine`

Implementation branch: `feature/tc5-18-last-successful-reuse`

Operational authority: `toootakeooot-bit/trade-plan-tc` Issue #1

## Result

**IMPLEMENTED — operational verification pending the next canonical cycles**

## Defect addressed

A later H1-only periodic cycle could fail to resolve D1/H4 when it searched too narrowly around the current cycle/run. The resulting data-unavailable condition could then appear as `NONE` / 判定保留 even though an earlier successful D1/H4 CURRENT existed.

This is a reuse-resolution defect, not a market-direction change.

## Changes

### 1. Explicit last-successful CURRENT resolver

`TimeframeCache.get_last_successful_current()` resolves by exact:

```text
canonical_symbol + provider + provider_symbol + timeframe
```

It is intentionally independent of the current cycle key.

`get_latest()` remains as a compatibility alias.

### 2. Failure state no longer replaces successful CURRENT

Retry/failure state remains separate from the last successfully persisted CURRENT.

Regression coverage verifies that `mark_failure()` leaves the earlier CURRENT intact.

### 3. Missing unscheduled evidence is UNAVAILABLE, not NONE

For Periodic:

- scheduled TF -> LIVE;
- unscheduled TF + last successful CURRENT -> CACHE / `LAST_SUCCESSFUL_CURRENT_REUSE`;
- unscheduled TF + no successful CURRENT -> `UNAVAILABLE` / `LAST_SUCCESSFUL_CURRENT_MISSING`.

The runtime records `REUSE_UNAVAILABLE` and cannot aggregate a complete D1/H4/H1 profile until required evidence exists.

No synthetic TC direction is created.

### 4. Current daily schedule aligned in code

Same every day:

- 06:03 D1/H4/H1 LIVE
- 11:03 H1 LIVE
- 15:03 H1 LIVE
- 19:03 H4/H1 LIVE
- 23:03 H1 LIVE

Base standing consumption: **24 successful Native calls/day** for GOLD/USDJPY/US100 before conditional work.

### 5. Scheduled-refresh reuse, not fixed H4 TTL

Periodic D1/H4 are reused until their next scheduled LIVE refresh. In particular, the 06:03 H4 remains the intended reusable evidence at 15:03 even though nine hours have elapsed.

Spot keeps its independent freshness policy.

### 6. Output-state separation

The per-symbol presentation was hardened to:

```text
TF | TC方向 | ENTRY判定 | Entry | SL | TP
```

D1/H4/H1 rows are retained. Missing evidence is `判定保留` with no fabricated prices/direction. M15 is shown only when acquired.

`NONE` is reserved for an available TC record whose direction is actually absent; it is not used as a synonym for data-unavailable/reuse-failed.

## Regression coverage added/updated

- fixed daily schedule = 24 base calls;
- 11:03 D1/H4 reuse + H1 LIVE;
- 15:03 reuse of older H4 without old fixed-TTL invalidation;
- missing unscheduled D1/H4 -> UNAVAILABLE, not implicit LIVE;
- failed LIVE state preserves prior last-successful CURRENT;
- 06:03 -> 11:03 Periodic/Spot parity;
- retry_pending remains next-slot-only;
- six-column table contract;
- missing required TF -> 判定保留 rather than NONE;
- M15 shown only when actually present;
- Gmail table rendering updated to the same six-column contract.

## Operational authority update

Issue #1 now explicitly defines the TC5-18 resolver contract and the same 06:03 / 11:03 / 15:03 / 19:03 / 23:03 schedule.

The automation already treats the current Issue #1 body as authoritative, so this fixes the operational reuse rule without adding another scheduler task.

## Remaining verification

The branch workflow was extended to include `feature/tc5-18-last-successful-reuse`. Connector-visible commit status has not yet exposed a completed run, so CI PASS is not claimed here.

Operational acceptance should confirm:

1. 15:03 uses the earlier 06:03 D1/H4 when those are the latest successful CURRENT values.
2. 19:03 updates H4/H1 and reuses D1.
3. 23:03 reuses 19:03 H4 and the latest successful D1.
4. A reuse lookup failure is surfaced as REUSE_UNAVAILABLE / 判定保留, never NONE.
5. Original fetched_at/provenance remains unchanged on CACHE reuse.

Execution Permission remains **NO**.
