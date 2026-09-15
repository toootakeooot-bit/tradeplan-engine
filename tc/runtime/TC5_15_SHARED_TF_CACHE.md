# TC5-15 — Scheduled Acquisition / Shared TF Cache / Spot Cache-First Resolver

Status: **IMPLEMENTED / CONTRACT FIXED**

Starting HEAD: `3b9b545b162448998fdef81576cb7f4bf6406710`

## 1. Purpose

TC5-15 reduces TradingCursor Native consumption without changing frozen TC4/TC5 decision semantics. Periodic and Spot share one cached evidence pool and one acquisition resolver. Already acquired evidence is reused as evidence; it is not sent back to TradingCursor as fabricated Native input.

The runtime topology is:

```text
TradingCursor Native
        |
        v
Original Raw preservation
        |
        v
Adapter / Normalizer
        |
        v
Shared TF Cache
        |
        v
Market Input Resolver
        |
        v
Resolved TF Evidence
        |
        v
aggregate_role_profile()
        |
        +---- Periodic
        +---- Spot
```

The cache never synthesizes a Native response and never changes the existing Original Raw First boundary.

## 2. Fixed instruments

Periodic targets are fixed in this order:

```text
GOLD
USDJPY
US100
```

Existing Symbol Normalization remains authoritative. Examples:

```text
GOLD = GOLD# = XAU/USD = XAUUSD
USDJPY = USDJPY#
US100 = US100Cash = US100Cash#
```

Cache identity is based on:

```text
canonical_symbol
provider
provider_symbol
timeframe
```

User alias and profile are not cache identity. Profile remains provenance only.

## 3. Fixed periodic schedule (JST)

| Slot | LIVE timeframes per symbol | Calls for 3 symbols |
|---|---|---:|
| 05:03 | H1 | 3 |
| 09:03 | D1 / H4 / H1 | 9 |
| 12:03 | H1 | 3 |
| 17:03 | H4 / H1 | 6 |
| 21:03 | H4 / H1 | 6 |

Base scheduled consumption is therefore **27 successful Native calls/day** before conditional M15, retry, conditional H4 refresh, or Spot calls.

M15 is never part of the standing schedule.

## 4. NORMAL role contract

Frozen role ownership remains:

```text
D1  = Environment
H4  = Setup
H1  = Decision
M15 = Optional Confirmation
```

M15 is LIVE only when H1 normalization explicitly sets:

```text
lower_tf_confirmation_required == true
```

ACTIONABLE or INVALID alone does not force M15.

## 5. Shared TF Cache contract

Each successful LIVE acquisition is persisted after Raw preservation and normalization.

Required metadata includes:

```text
canonical_symbol
provider
provider_symbol
timeframe
source_profile
candle_id
fetched_at
source_run_id
record_id
raw_artifact_ref
cache_status
raw
normalized
```

`candle_id` is provenance, not an automatic invalidation gate. Periodic policy intentionally reuses prior scheduled D1/H4 across candle-bucket boundaries, such as previous 21:03 H4 at 05:03.

`fetched_at` is the original cache acquisition time. Reading from CACHE must not rewrite it.

`TimeframeCache(storage_path=...)` provides JSON persistence so Periodic and Spot processes can share the same evidence when the Host binds the same storage path.

## 6. Retry state

A failed LIVE request records:

```text
retry_pending = true
last_failure_at
failure_code
```

No immediate loop retry is performed. An unscheduled timeframe with retry state is attempted exactly once at the next periodic slot.

Any later successful LIVE acquisition of that same cache identity clears retry state, including a successful Spot acquisition.

## 7. Market Input Resolver

`MarketInputResolver` is the only TC5-15 policy layer that decides CACHE versus LIVE.

The Normalizer and Aggregator do not perform acquisition decisions.

### Periodic

Scheduled TF -> LIVE.

Unscheduled required D1/H4 -> CACHE when available.

Unscheduled retry_pending TF -> LIVE once at the next slot.

Missing required cache -> LIVE fallback, because a required TC role may not be fabricated.

### Spot NORMAL

D1 -> latest shared CACHE when available.

H4 -> latest shared CACHE when available.

H1 -> shared CACHE only when age is <= 90 minutes; otherwise H1 alone is refreshed LIVE.

M15 -> LIVE only after common aggregation requests lower-TF confirmation.

A missing or retry_pending TF is fetched LIVE independently. Spot never performs a blanket D1/H4/H1 refetch merely because one TF is missing.

## 8. 05:03 conditional H4 refresh

05:03 normally uses:

```text
D1 = previous scheduled CACHE
H4 = previous 21:03 CACHE
H1 = 05:03 LIVE
```

If H1 is ACTIONABLE and H4 cache age is greater than one H4 interval (four hours), H4 is refreshed once LIVE before final aggregation. This makes the intended 21:03 -> 05:03 eight-hour gap refresh only when the Decision timeframe presents an entry candidate, while a more recent Spot-refreshed H4 can still be reused.

WAIT does not spend the additional H4 call.

## 9. Periodic examples

### 12:03

```text
D1  CACHE  from 09:03
H4  CACHE  from 09:03
H1  LIVE   at 12:03
M15 LIVE   only if required
```

### 17:03

```text
D1  CACHE  from 09:03
H4  LIVE   at 17:03
H1  LIVE   at 17:03
M15 LIVE   only if required
```

### 21:03

```text
D1  CACHE  from 09:03
H4  LIVE   at 21:03
H1  LIVE   at 21:03
M15 LIVE   only if required
```

## 10. Spot example

At 15:00, if latest evidence is:

```text
D1 09:03
H4 09:03
H1 12:03
```

then NORMAL Spot resolves:

```text
D1  CACHE
H4  CACHE
H1  LIVE   # >90 minutes old
M15 LIVE   # only if required after H1 aggregation
```

Normal Spot therefore consumes one Native call, or two when M15 confirmation is required.

## 11. Original Raw First

LIVE order remains fixed:

```text
Native
 -> Raw Sink
 -> Adapter
 -> Normalize
 -> Shared TF Cache
```

A CACHE hit reuses the already preserved `raw_artifact_ref`, Raw wrapper and normalized evidence. It does not create pseudo-Raw or present cached evidence as newly fetched LIVE evidence.

## 12. Common aggregation parity

Periodic and Spot both hand resolved evidence to:

```text
aggregate_role_profile()
```

There is no Periodic-specific or Spot-specific Trade State mapping. The only intended differences are trigger source, acquisition schedule, cache freshness policy, and delivery surface.

## 13. Provenance / output

Each used TF carries:

```text
timeframe
source_mode = LIVE | CACHE
fetched_at
cache_age_seconds
reason
```

Spot `TradePlanState.evidence.timeframe_provenance` exposes these rows. Periodic results expose the same `TFProvenance` structure.

Runtime Native usage counts only actual successful Native responses. Cache hits count as zero calls.

Provider quota remaining must remain unknown unless the Host owns an authoritative ledger. TC5-15's local fixed base is 27 scheduled successful calls/day.

## 14. Boundaries

The following remain prohibited:

- representing CACHE as LIVE;
- rewriting cached `fetched_at`;
- blanket Spot refetch of D1/H4/H1;
- Periodic-only or Spot-only decision semantics;
- inferring a missing timeframe from another timeframe;
- using ChatGPT/Web market data as a TC evidence substitute;
- NODA mixing;
- unconditional M15 acquisition;
- unlimited immediate Native retry;
- automatic order execution or lot sizing.

`Execution Permission: NO` remains fixed.
