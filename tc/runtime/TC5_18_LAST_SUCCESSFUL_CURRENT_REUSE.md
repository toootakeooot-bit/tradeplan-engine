# TC5-18 — Last-Successful CURRENT Reuse Resolver

Status: **IMPLEMENTED / REGRESSION PENDING**

Base: `feature/tc5-17-fixed-tf-report`

Implementation branch: `feature/tc5-18-last-successful-reuse`

## Purpose

Prevent an unscheduled timeframe from becoming `NONE` or disappearing merely because the current periodic cycle did not acquire that timeframe LIVE.

Periodic reuse is resolved from the latest successfully persisted CURRENT for the exact provider/symbol/timeframe identity across prior cycle boundaries.

## Canonical identity

Reuse key:

```text
canonical_symbol
provider
provider_symbol
timeframe
```

The reusable record does **not** need to have the current `cycle_key`, `source_run_id`, or manifest owner.

## Fixed daily periodic schedule (JST)

Same every calendar day:

| Slot | LIVE per symbol | Reuse |
|---|---|---|
| 06:03 | D1 / H4 / H1 | — |
| 11:03 | H1 | D1 / H4 |
| 15:03 | H1 | D1 / H4 |
| 19:03 | H4 / H1 | D1 |
| 23:03 | H1 | D1 / H4 |

For GOLD / USDJPY / US100 the standing successful-call base is **24 Native calls/day** before M15, retry, recovery, or Spot.

## Resolver contract

### Scheduled timeframe

A scheduled TF is LIVE.

On success:

1. preserve Original Raw;
2. normalize;
3. persist the new CURRENT;
4. clear matching retry state;
5. use the new evidence as LIVE.

### Unscheduled timeframe

Resolve `last_successful_CURRENT` for the exact identity.

When found:

- source_mode = CACHE;
- reason = `LAST_SUCCESSFUL_CURRENT_REUSE`;
- preserve original `fetched_at`, raw reference, normalized result and source run/cycle;
- do not apply a fixed Periodic D1/H4 TTL that invalidates the intended scheduled-refresh chain.

When absent:

- source_mode = `UNAVAILABLE`;
- reason = `LAST_SUCCESSFUL_CURRENT_MISSING`;
- periodic result is insufficient / 判定保留;
- do not synthesize `NONE`;
- do not silently issue an unscheduled LIVE call solely to fill the missing row.

Spot retains its separate cache-freshness rules.

## Failure-state separation

A failed LIVE attempt and a successful CURRENT are independent state dimensions.

`mark_failure()` records retry state but MUST NOT overwrite or delete the last successful CURRENT.

Therefore a failed later request cannot erase the prior reusable evidence.

The failed canonical slot must still not mislabel that older CURRENT as newly successful LIVE.

## NONE semantics

`NONE` is reserved for an actually available TC result whose normalized direction is genuinely absent.

These are not NONE:

- cache lookup failed;
- no prior CURRENT exists;
- registry lookup failed;
- host/tool unavailable;
- provider acquisition failed;
- cache write failed.

Those states remain operational/data-availability states and must be surfaced separately.

## Provenance

CACHE reuse retains the original:

- fetched_at
- source_run_id
- record_id
- raw_artifact_ref
- normalized values
- provider identity

No backdating and no CACHE→LIVE relabeling.

## Regression expectations

1. 06:03 success → 11:03 D1/H4 reuse + H1 LIVE.
2. 06:03 success → 15:03 D1/H4 reuse even when H4 age exceeds the old fixed 8h concept.
3. 19:03 success → 23:03 H4 reuse.
4. A failed later LIVE attempt does not remove the earlier last-successful CURRENT.
5. Missing unscheduled D1/H4 produces UNAVAILABLE / 判定保留, not NONE and not an implicit LIVE fetch.
6. Spot cache-first behavior remains unchanged.
7. Execution Permission remains NO.
