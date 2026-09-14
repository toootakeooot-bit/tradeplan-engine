# TC5-11 Usage Runtime Display Audit

Date: 2026-09-14
Branch: `feature/tc-v1`
Scope: TC5 Runtime / ChatGPT Host usage telemetry only.

## Finding

TC5-6 already allowed Runtime presentation outside TradePlanState, but the repository had no fixed contract for:

- current-run TradingCursor consumption;
- remaining daily local budget after scheduled reserve;
- spot-equivalent display;
- next reset display.

Using `len(raw_records)` alone would be insufficient because a Native call can already be consumed before a later Raw preservation, Adapter or Normalizer failure.

## Implementation

Added `tc/runtime/usage.py` with:

- `TCUsagePolicy`;
- `TCUsageRuntimeInfo`;
- daily budget calculation;
- scheduled-reserve subtraction;
- 3-call spot approximation;
- 00:00 UTC / 09:00 JST next-reset calculation;
- user-facing formatter.

Added `UsageTrackingNativeClient` at the Host/Native boundary. It increments only after a non-empty Native response mapping is returned, before downstream repository processing.

Extended `TCSpotServiceResult` with `runtime_usage`, which remains beside and outside `tradeplan_state`.

## Fixed local policy

```text
daily limit: 50 calls
reset: 00:00 UTC = 09:00 JST
default pending scheduled reserve: 20 calls
spot planning conversion: 3 calls ~= 1 spot
```

The pending scheduled reserve is overrideable when the Host knows the actual future scheduled workload.

## Fail-safe behavior

If the Host cannot establish `used_today_before_run`, the runtime still reports exact current-run successful-call consumption but returns remaining and spot-equivalent as unknown.

No false remaining-quota number is manufactured.

## Boundary audit

No change was made to:

- TC4 Adapter;
- TC4 schema;
- TC4 state semantics;
- TC Native analysis content;
- profile role assignment;
- Entry/SL/TP mapping;
- execution permission.

TC usage information is Runtime telemetry only and cannot alter Trade State.

## Regression requirements

Tests must cover:

- 3-call successful run accounting;
- 50/day budget arithmetic;
- 20-call scheduled reserve arithmetic;
- 3-call spot conversion;
- 09:00 JST reset rendering;
- missing-ledger non-fabrication;
- successful Native response increments usage;
- failed Native call does not increment usage;
- existing TC4 + TC5 runtime regressions remain green.
