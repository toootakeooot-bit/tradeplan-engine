# TC5-16 Host Scheduler Integration Audit

Status: **IMPLEMENTED AT HOST CONTRACT / ACTIVE CONFIG UPDATED**

## Fixed outcomes

- Active TC periodic controller: `TC Native 定期`.
- Separate quota-recovery controller: retired/disabled.
- Canonical acquisition times: 05:03 / 09:03 / 12:03 / 17:03 / 21:03 subject to weekly market guard.
- 09:03 D1/H4/H1; 12:03 H1; 17:03 H4/H1; 21:03 H4/H1; 05:03 H1.
- Base full-day scheduled Native usage: 27 successful calls.
- M15: only on explicit `lower_tf_confirmation_required=true`.
- 05:03 H4: conditional refresh only when H1 ACTIONABLE and H4 age >4h.
- retry_pending: next accepted slot only; no same-slot loop.
- H1 Spot cache freshness: <=90m.

## Shared state authority

Operational authority is `toootakeooot-bit/trade-plan-tc` Issue #1.

`runtime/tc5-shared-cache` is retained as schema/reference/mirror only. This avoids dual operational authorities while preserving the repository TimeframeCache design as implementation reference.

The Issue #1 body has been revised to TC5-16 provider/schedule/cache policy. Historical comments remain audit history.

## Provider normalization

Current operational tuples:

- GOLD -> OANDA/XAUUSD
- USDJPY -> OANDA/USDJPY
- US100 -> PEPPERSTONE/NAS100

Historical FOREXCOM US100 evidence is not reusable under the current provider identity.

## Quota recovery

Quota recovery is integrated into periodic preflight. Confirmed quota exhaustion causes fail-closed zero-provider behavior until the 09:00 JST reset. Historical missed work is marked missed; current data is not backfilled as historical LIVE evidence. 09:03 is the normal fresh baseline after reset.

## Periodic / Spot parity

Both modes are required to read/write the same operational cache registry and use frozen TC4/TC5 NORMAL aggregation. Spot is cache-first, with D1/H4 reuse and H1 <=90m reuse.

## Boundaries

This step changes host orchestration/runtime policy, not TC4/TC5 strategy semantics. It does not create autonomous order execution. Gmail remains notification-only.

`Execution Permission: NO`.
