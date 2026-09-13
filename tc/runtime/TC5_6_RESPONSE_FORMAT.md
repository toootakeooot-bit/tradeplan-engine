# TC5-6 — TC Spot Response Format

Status: **REVISED / COMMON OUTPUT PRESERVED**

TC Spot user output follows the common TradePlanState direction rather than exposing a mandatory four-timeframe table as the primary result.

When the profile gate is finalized, the outward strategy payload is conceptually:

```text
TradePlanState

symbol
timestamp

status:
  TRADE / WAIT / INVALID

direction:
  LONG / SHORT / NONE

environment
setup
entry
stop_loss
take_profit
invalidation
evidence
source_engine:
  TC
```

The schema remains provisional until NODA/Common review; TC5 does not finalize the Common JSON Schema.

## Evidence/provenance

`evidence` must retain at least:

- profile: NORMAL or SHORT;
- environment source timeframe;
- setup source timeframe;
- decision source timeframe;
- confirmation source timeframe when used;
- used timeframes and record/raw references;
- provider source/symbol.

Entry/SL/TP come from the profile decision plan only. Values from D1/H4/H1/M15 are not mixed to manufacture a better-looking plan.

## Runtime presentation outside TradePlanState

If no valid common TradePlanState can be finalized, the UI may display runtime states such as:

```text
判定保留
下位足確認待ち
取得失敗
```

These are not TradePlanState `WAIT` or `INVALID`.

Examples:

```text
UNDETERMINED -> 判定保留
NORMAL H1 explicitly requests lower-TF confirmation before M15 is obtained -> 下位足確認待ち
Native/transport failure -> 取得失敗
```

Execution permission remains outside TC Spot and is always `NO` here. External web prices/news/analysis must not be inserted into the TC result.
