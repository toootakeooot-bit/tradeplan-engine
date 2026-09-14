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

### TC usage block

TC usage/budget information is also Runtime information and MUST remain outside TradePlanState.

For every completed TC Spot response, append:

```text
TC利用状況
今回消費：N回
予定を抜いた残り：R回
スポット換算：約S回分
次回リセット：M/D 09:00（日本時間）
```

Rules:

- `今回消費` is the number of successful TradingCursor Native responses actually consumed by the current run;
- a failed Native call is not counted as a successful consumption;
- counting occurs at the Host/Native response boundary, before Raw preservation, Adapter mapping and normalization;
- local daily budget policy is 50 calls/day;
- reset boundary is 00:00 UTC = 09:00 JST;
- scheduled workload reserve defaults to 20 calls and is subtracted before user-facing spot availability;
- `スポット換算` is an approximate planning figure using 3 Native calls per spot;
- NORMAL commonly consumes 3 calls and may consume 4 when H1 explicitly requires M15 drilldown;
- SHORT consumes 3 calls under the current profile contract;
- if the Host daily ledger is unavailable, `今回消費` remains exact but remaining and spot-equivalent MUST be displayed as `不明`; fabricated quota values are prohibited.

This usage block is operational telemetry only. It must not alter TRADE/WAIT/INVALID/HOLD state, direction, Entry/SL/TP, or execution permission.

Execution permission remains outside TC Spot and is always `NO` here. External web prices/news/analysis must not be inserted into the TC result.
