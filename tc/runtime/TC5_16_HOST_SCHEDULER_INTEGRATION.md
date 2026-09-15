# TC5-16 — Host Scheduler / Shared Operational Cache Integration

Status: **FIXED / HOST-INTEGRATED**

Base: TC5-15 Shared TF Cache

## Purpose

Bind the ChatGPT Host periodic controller and on-demand Spot flow to one operational cache authority while keeping frozen TC4/TC5 decision semantics unchanged.

## Canonical JST market slots

- Monday: 09:03 / 12:03 / 17:03 / 21:03
- Tuesday-Friday: 05:03 / 09:03 / 12:03 / 17:03 / 21:03
- Saturday: 05:03 only
- Sunday: none

The recurring automation may wake at additional candidate times, but noncanonical wakes perform zero provider calls.

## Fixed acquisition policy

Per GOLD / USDJPY / US100:

- 09:03: D1 + H4 + H1 LIVE
- 12:03: H1 LIVE; D1/H4 from Shared TF Cache
- 17:03: H4 + H1 LIVE; D1 from cache
- 21:03: H4 + H1 LIVE; D1 from cache
- 05:03: H1 LIVE; D1/H4 from cache

Base full-day scheduled consumption is 27 successful Native calls before conditional M15, retry, conditional 05:03 H4 refresh, or Spot.

## Single operational authority

The authoritative Shared TF Cache and runtime state is:

`toootakeooot-bit/trade-plan-tc` Issue #1 — `[TC-CACHE] NORMAL-V1 Provider Cache Registry`

The branch `runtime/tc5-shared-cache` in this repository is schema/reference/mirror only. It is not a second operational authority.

Periodic and Spot MUST consult/update the same Issue #1 registry.

## Provider identity

- GOLD aliases -> OANDA / XAUUSD
- USDJPY aliases -> OANDA / USDJPY
- US100 aliases -> PEPPERSTONE / NAS100

Historical FOREXCOM / NAS100 entries are not reusable as current US100 evidence.

## Spot Cache-First

NORMAL Spot resolves in this order:

1. D1: latest valid shared cache first.
2. H4: latest valid shared cache first.
3. H1: shared cache only when age <= 90 minutes; otherwise refresh H1 only.
4. Missing/retry_pending required TF: fetch only that TF LIVE.
5. M15: LIVE only when frozen H1 normalized result explicitly has `lower_tf_confirmation_required=true`.

Successful Spot LIVE evidence writes back to the same operational registry and clears matching retry_pending.

## 05:03 conditional H4 refresh

05:03 normally reuses previous H4. If H1 is ACTIONABLE and H4 age is greater than 4 hours, refresh H4 once LIVE before finalization. If the refresh fails, finalization must not silently proceed on stale H4.

## Retry

Failed required TF sets retry_pending and is attempted at most once at the next accepted canonical slot. No same-slot retry loop.

## Quota recovery integration

The separate quota-recovery controller is retired. Every accepted periodic slot performs quota/reset preflight.

- Reset boundary: 09:00 JST.
- Once quota exhaustion is confirmed for the current reset window, later pre-reset slots fail closed with zero provider calls.
- At the first accepted slot after reset, historical unacquired evidence is marked `MISSED_DUE_TO_QUOTA`.
- Current data must never masquerade as historical LIVE evidence.
- 09:03 D1/H4/H1 is the normal fresh recovery baseline.
- If 09:03 is missed, the next accepted slot performs the same preflight and fetches only current missing required evidence.

## Original Raw First / provenance

Every successful Native response or stable complete response reference must be preserved before normalized/cache evidence is considered reusable.

CACHE reuse preserves original fetched_at and source provenance. CACHE is never relabeled LIVE.

## Common decision semantics

D1=Environment, H4=Setup, H1=Decision, M15=Optional Confirmation. Periodic and Spot both use frozen TC4/TC5 normalization and NORMAL ENTRY_PRE aggregation. Trigger/acquisition timing may differ; trade-state semantics do not.

No Web, NODA, MT4, screenshot, or other timeframe may substitute missing TradingCursor evidence.

`Execution Permission: NO`.
