# TC5-14 — Periodic / Spot Parity Audit

Audit date: 2026-09-15 JST
Branch: `feature/tc-v1`
Result: **PASS WITH NOTE**

## Observed baseline

The Spot runtime currently fixes NORMAL as D1/H4/H1 with optional M15 drilldown. `aggregate_role_profile()` permits NORMAL M15 drilldown only when the H1 normalized decision explicitly sets `lower_tf_confirmation_required=true`.

The prior standalone periodic automation had a materially different confirmation condition: it instructed M15 when H1 was exactly ACTIONABLE or INVALID and also forced H4 LIVE. That was not equivalent to the current frozen Spot decision path.

## Change applied

The active standalone `TC Native 定期` Host automation was revised so that:

- periodic acquisition keeps the existing slot-specific LIVE/CACHE policy;
- after D1/H4/H1 evidence is available, decision semantics follow the TC Spot NORMAL `ENTRY_PRE` path;
- the old `H1 ACTIONABLE or INVALID => M15` shortcut is explicitly retired;
- M15 is fetched only when H1 carries `lower_tf_confirmation_required=true`;
- H4 is not force-refreshed merely because H1 is ACTIONABLE or INVALID;
- the user-facing periodic result is expanded from a compact monitoring line to a Spot-equivalent detailed per-symbol answer;
- Entry / SL / TP / invalidation remain sourced from the same Spot role/timeframe contract;
- exact LIVE/CACHE provenance remains visible;
- Gmail carries the same core established result and remains notification-only;
- `Execution Permission: NO` remains fixed.

The Host automation update was applied at 2026-09-15 06:53 JST.

## Repository guard

`tc/runtime/TC5_14_PERIODIC_SPOT_PARITY.md` was added to freeze the intended parity boundary and acceptance criteria.

## PASS WITH NOTE rationale

Decision and output parity is now fixed at the Host contract level. Acquisition is intentionally not byte-for-byte identical to Spot because periodic monitoring reuses valid D1/H4 cache to control Native consumption. This is an accepted operational difference only; it must not change the normalized state semantics, aggregation, direction, Entry, SL, TP, invalidation, or execution permission.

No claim is made that a post-change scheduled production cycle has already been observed. The configuration and contract change itself is complete; runtime evidence from subsequent accepted cycles can be checked against the TC5-14 acceptance criteria without changing the contract.
