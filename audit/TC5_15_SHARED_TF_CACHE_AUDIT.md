# TC5-15 Shared TF Cache Audit

Status: **PASS / IMPLEMENTED**

Starting HEAD: `3b9b545b162448998fdef81576cb7f4bf6406710`

Verified implementation HEAD before this audit-only commit: `96ad523c9eb7f2b54ac0b12c2a367505b35e9e33`

GitHub Actions run: `34930438243` — **SUCCESS**

## 1. Scope audited

TC5-15 was audited against the requested contract:

- fixed three-symbol periodic acquisition;
- five fixed JST slots;
- Shared TF Cache;
- persistent cache metadata and Raw provenance;
- common Market Input Resolver;
- retry_pending carry to the next slot;
- Spot Cache-First;
- H1 90-minute Spot freshness;
- conditional 05:03 H4 refresh;
- M15 only when lower-TF confirmation is explicitly required;
- Periodic / Spot common aggregation semantics;
- LIVE / CACHE provenance exposure;
- existing TC4/TC5 regression preservation.

## 2. Implemented files

### Runtime

- `tc/runtime/tf_cache.py`
  - shared cache identity = canonical/provider/provider_symbol/timeframe;
  - optional JSON persistence;
  - original `fetched_at` preservation;
  - record/raw artifact provenance;
  - dynamic cache age;
  - retry_pending state and successful-clear behavior.

- `tc/runtime/acquisition.py`
  - fixed periodic schedule;
  - fixed target symbols;
  - base call count = 27/day;
  - common Periodic / Spot acquisition policy;
  - H1 <= 90 minute Spot cache rule;
  - one-H4-interval 05:03 freshness gate.

- `tc/runtime/orchestrator.py`
  - NORMAL Spot cache-first path;
  - D1/H4 cache reuse;
  - H1 selective refresh;
  - M15 LIVE only after common aggregation requests confirmation;
  - LIVE acquisition writes back to shared cache;
  - retry_pending clears after successful Spot acquisition;
  - TF provenance is returned with the run result.

- `tc/runtime/periodic.py`
  - executable per-symbol and three-symbol slot runners;
  - scheduled LIVE vs CACHE resolution through the same Resolver;
  - next-slot retry behavior;
  - no same-slot retry loop;
  - 05:03 conditional H4 refresh;
  - failed required H4 refresh prevents silent finalization on stale setup evidence;
  - same `aggregate_role_profile()` semantics as Spot.

- `tc/runtime/response.py`
  - user-facing evidence may expose per-TF LIVE/CACHE provenance, original cache fetch time, age and resolution reason.

- `tc/runtime/service.py`
  - optional shared cache binding for Spot;
  - current Native call usage excludes cache hits;
  - when TC5-15 cache mode is active, local scheduled reserve defaults to the fixed 27-call base.

### Specification

- `tc/runtime/TC5_15_SHARED_TF_CACHE.md`

### Tests

- `tests/tc5_runtime/test_tc5_15_shared_cache.py`
- `tests/tc5_runtime/test_tc5_15_periodic.py`

### CI

- `.github/workflows/tc5-runtime-tests.yml`
  - TC5-15 feature branch included so branch changes are continuously regression-tested.

## 3. Fixed schedule

| JST slot | LIVE TF per symbol | 3-symbol base calls |
|---|---|---:|
| 05:03 | H1 | 3 |
| 09:03 | D1 / H4 / H1 | 9 |
| 12:03 | H1 | 3 |
| 17:03 | H4 / H1 | 6 |
| 21:03 | H4 / H1 | 6 |

Base scheduled total: **27 successful Native calls/day**.

M15 is not standing schedule consumption.

The theoretical case where all three symbols require M15 at all five slots adds 15 calls, giving **42 calls/day before Spot/retry/conditional H4 refresh**.

## 4. Periodic cache reuse audit

Expected resolver behavior is implemented:

```text
12:03  D1=CACHE H4=CACHE H1=LIVE
17:03  D1=CACHE H4=LIVE  H1=LIVE
21:03  D1=CACHE H4=LIVE  H1=LIVE
05:03  D1=CACHE H4=CACHE H1=LIVE
```

At 05:03, if H1 is ACTIONABLE and H4 is older than one H4 interval, H4 is refreshed once LIVE. WAIT does not trigger this extra call.

## 5. Spot Cache-First audit

NORMAL Spot now follows:

```text
Shared Cache
  -> D1 latest cache when present
  -> H4 latest cache when present
  -> H1 cache if <= 90 minutes
  -> otherwise only H1 LIVE
  -> common aggregation
  -> M15 LIVE only if lower_tf_confirmation_required=true
```

Missing or retry_pending evidence is acquired independently. The runtime no longer requires blanket D1/H4/H1 refetch when a shared cache is bound.

Spot LIVE success writes back to the same cache, allowing later Periodic or Spot reuse.

## 6. Retry audit

Failure behavior:

```text
LIVE failure
 -> retry_pending=true
 -> no immediate same-slot loop
 -> next periodic slot resolves pending TF as LIVE once
```

A later successful periodic or Spot LIVE acquisition clears the pending state.

The regression suite covers 09:03 H4 failure followed by 12:03 H4 retry and successful clear.

## 7. Original Raw First / provenance audit

PASS.

LIVE acquisition remains:

```text
Native
 -> Raw Sink
 -> Adapter
 -> Normalize
 -> Cache
```

CACHE reuse does not synthesize a fake Native response and does not rewrite the original `fetched_at`.

Cache records retain `source_run_id`, `record_id`, and `raw_artifact_ref`.

## 8. Periodic / Spot parity audit

PASS.

Both runtime paths ultimately use `aggregate_role_profile()` with the same NORMAL role semantics:

```text
D1  Environment
H4  Setup
H1  Decision
M15 Confirmation when required
```

The tests establish a 12:03 Periodic WAIT result and then execute Spot against the same cached evidence with zero Native calls; common status and direction remain equivalent.

## 9. Regression result

GitHub Actions run `34930438243` completed successfully on implementation HEAD `96ad523c9eb7f2b54ac0b12c2a367505b35e9e33`.

PASS steps:

- TC4 regression;
- TC5 profile aggregation regression;
- TC5 static pipeline regression;
- TC5 runtime core regression, including TC5-15 tests;
- TC5 notification regression.

No frozen TC4 artifacts were modified.

## 10. Consumption comparison

Before cache-first reuse, a NORMAL three-TF Spot commonly required D1/H4/H1 LIVE, with an additional M15 when required.

Under TC5-15, examples are:

```text
all required cache valid          -> 0 Native calls
D1/H4 cache + expired H1          -> 1 Native call
D1/H4 cache + expired H1 + M15    -> 2 Native calls
missing H4 + fresh H1             -> 1 Native call
```

The fixed periodic base is 27 calls/day, preserving headroom under a 50-call local planning ceiling for confirmation, Spot, retry and conditional refresh.

## 11. Boundary / remaining host work

Repository implementation is complete for TC5-15 runtime policy and execution entry points.

One operational boundary remains outside the repository runtime itself:

- the deployment Host/scheduler must invoke `run_periodic_slot()` at 05:03, 09:03, 12:03, 17:03 and 21:03 JST;
- Periodic and Spot Hosts must bind the same persistent `TimeframeCache(storage_path=...)` location if they run in separate processes;
- authoritative provider quota remaining is still unavailable unless supplied by an external Host ledger.

These are Host/deployment bindings, not missing TC5-15 decision/cache logic.

## 12. Audit conclusion

**PASS.**

TC5-15 now fixes and implements the requested architecture:

> Periodic and Spot share one persistent-capable TF cache and one Market Input Resolver, reuse already acquired TradingCursor evidence first, call Native only for required missing/expired evidence, and preserve common TC aggregation semantics and Original Raw First provenance.
