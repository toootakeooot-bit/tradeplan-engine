# TC5-11 — TC Usage Runtime Display

Status: **ACTIVE TC5 HOST RUNTIME EXTENSION**

## 1. Purpose

Every TC Spot response must expose usage/budget information without contaminating TradePlanState.

Required user-facing block:

```text
TC利用状況
今回消費：N回
予定を抜いた残り：R回
スポット換算：約S回分
次回リセット：M/D 09:00（日本時間）
```

## 2. Separation from TradePlanState

Usage information is Host Runtime telemetry only.

It must not be inserted into:

- `status`;
- `direction`;
- `environment`;
- `setup`;
- `entry`;
- `stop_loss`;
- `take_profit`;
- `invalidation`;
- Trade State mapping.

The repository service exposes it as `TCSpotServiceResult.runtime_usage`, beside `tradeplan_state`.

## 3. Consumption boundary

A call is counted only when the TradingCursor Native client returns a non-empty mapping.

The count occurs before:

```text
Raw Sink
-> Adapter
-> Normalizer
-> Aggregation
```

This prevents a consumed provider call from disappearing from accounting when a later repository stage fails.

Failed/exception Native calls are not counted as successful consumption.

## 4. Budget policy

Current local Host policy:

```text
daily_limit = 50
reset = 00:00 UTC = 09:00 JST
scheduled_reserve_default = 20
spot_call_budget = 3
```

The 20-call reserve represents future/pending scheduled workload. If the Host knows a more accurate pending scheduled-call total, that value replaces the default reserve.

Already executed scheduled calls are part of the daily used count and must not also remain in the pending reserve.

## 5. Calculation

```text
used_today_after
  = used_today_before_run + current_run_successful_calls

remaining_before_reserve
  = max(0, daily_limit - used_today_after)

remaining_after_reserve
  = max(0, remaining_before_reserve - scheduled_reserve_remaining)

spot_equivalent
  = floor(remaining_after_reserve / 3)
```

`spot_equivalent` is explicitly approximate. NORMAL may require a fourth call when H1 requests M15 drilldown.

## 6. Missing-ledger behavior

TradingCursor Native currently has no dedicated remaining-quota lookup contract in this integration.

Therefore the Host daily ledger is required for exact local remaining-budget arithmetic.

If `used_today_before_run` cannot be established:

```text
今回消費：<exact current run count>
予定を抜いた残り：不明
スポット換算：不明
次回リセット：<calculated next reset>
```

Fabricating an apparent remaining count is prohibited.

## 7. Profile reference

NORMAL:

```text
D1 + H4 + H1 = normally 3 successful Native calls
+ M15 only when H1 explicitly requires drilldown = 4
```

SHORT:

```text
H4 + H1 + M15 = 3 successful Native calls
```

The displayed `今回消費` always uses observed successful-call count rather than assuming these nominal values.

## 8. Implementation surface

```text
tc/runtime/usage.py
  TCUsagePolicy
  TCUsageRuntimeInfo
  build_usage_runtime_info
  format_usage_runtime_info

tc/runtime/host_binding.py
  UsageTrackingNativeClient

tc/runtime/service.py
  TCSpotServiceResult.runtime_usage
```

TC4 remains unchanged.
