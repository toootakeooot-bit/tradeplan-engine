# TC5-14 — Periodic / Spot Decision & Output Parity

Status: **IMPLEMENTED / HOST CONTRACT FIXED**

## 1. Purpose

The standalone TC Native periodic cycle must produce a user-facing result materially equivalent to a TC Spot `ENTRY_PRE` result while preserving the periodic acquisition/cache policy needed for call-budget efficiency.

The only intentional differences are:

- trigger source: scheduler vs. user command;
- acquisition freshness policy: periodic may reuse valid D1/H4 cache, while Spot is on-demand;
- delivery: periodic also emits one idempotent aggregate Gmail notification.

Decision semantics and outward strategy fields must not diverge.

## 2. Common NORMAL role contract

For periodic monitoring, use the same NORMAL role mapping as TC Spot:

- Environment: D1
- Setup: H4
- Decision: H1
- Optional confirmation: M15

After valid D1/H4/H1 evidence exists, normalize and aggregate using the frozen TC4/TC5 semantics. Do not create a periodic-only state map.

Common status mapping remains:

- H1 `ACTIONABLE` -> `TRADE`
- H1 `WAIT` -> `WAIT`
- H1 `INVALID` -> `INVALID`
- unsupported / `UNDETERMINED` finalization -> runtime HOLD / user-facing 判定保留

Direction, Entry, SL, TP and invalidation must come from the same role/timeframe sources as Spot.

## 3. M15 drilldown — frozen parity rule

The prior periodic shortcut is retired:

```text
H1 ACTIONABLE or INVALID => fetch M15
```

The only NORMAL drilldown trigger is the Spot rule:

```text
H1 normalized result has lower_tf_confirmation_required == true
```

When that flag is false, periodic must not fetch M15 merely because H1 is ACTIONABLE or INVALID.

When confirmation is required:

- fetch M15 LIVE;
- re-run the same NORMAL aggregation;
- same-direction M15 `ACTIONABLE` may finalize `TRADE`;
- M15 `WAIT` finalizes `WAIT`;
- other confirmation outcomes remain HOLD / no fabricated common status.

Do not force H4 LIVE solely because H1 is ACTIONABLE or INVALID.

## 4. Periodic acquisition policy remains distinct by design

To control Native consumption, periodic acquisition may use the slot-specific LIVE/CACHE plan. This is not a decision-logic difference.

Every reused item must preserve:

- `source_mode=CACHE`;
- original `fetched_at` / source time;
- age and TTL/provenance;
- provider/symbol/timeframe identity.

Cached evidence must never be represented as newly fetched LIVE evidence.

## 5. User-facing periodic answer

Each accepted periodic cycle must show, per symbol, the same core information expected from a Spot answer:

1. final status and direction;
2. D1/H4/H1 and M15 when used, with LIVE/CACHE provenance;
3. Environment / Setup / Decision summary;
4. Entry / Stop Loss / Take Profit(s) / Invalidation when present;
5. confirmation result when M15 was required;
6. provider, provider symbol, used timeframes and material runtime errors;
7. `Execution Permission: NO`.

Missing values must be shown as absent/unknown, never invented.

The overall periodic report also shows canonical slot, actual wake when different, cycle key, exact current-cycle Native consumption, cache use, M15 use, errors and reset information. Remaining quota must be `不明` when no authoritative ledger is available.

## 6. Gmail parity

Periodic sends exactly one aggregate Gmail after the TC result is established. The email carries the same core final status/direction and Entry/SL/TP/invalidation fields when available, plus acquisition provenance and runtime usage.

Gmail failure must never change TC state or trigger provider re-fetch.

## 7. Safety / boundary

- TradingCursor Native only for market analysis.
- No NODA mixing.
- No web-derived replacement technical analysis.
- No MT4/PC/screenshot dependency.
- No sizing or lot calculation.
- No automatic execution.
- `Execution Permission: NO` remains fixed.

## 8. Acceptance criteria

PASS requires all of the following:

- periodic D1/H4/H1 evidence is mapped into the same NORMAL role semantics as Spot;
- M15 is called only for explicit `lower_tf_confirmation_required=true`;
- no periodic-only Entry/SL/TP synthesis exists;
- per-symbol user output contains the Spot-equivalent core fields;
- cache provenance is explicit;
- provider/runtime failure is shown at the exact failed stage rather than silently omitted;
- Gmail reuses the established result and does not refetch;
- execution permission remains NO.
