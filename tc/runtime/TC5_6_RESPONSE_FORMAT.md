# TC5-6 — TC Spot / Periodic Response Format

Status: **REVISED BY TC5-17 / FIXED TF TABLE**

TC Spot and TC periodic user output must include the same fixed per-symbol timeframe table whenever at least one acquired normalized timeframe exists.

Required table:

```text
| TF | 判定 | Entry | SL | TP1 | TP2 | TP3 |
|---|---|---:|---:|---:|---:|---:|
| D1 | ... | ... | ... | ... | ... | ... |
| H4 | ... | ... | ... | ... | ... | ... |
| H1 | ... | ... | ... | ... | ... | ... |
| M15 | ... | ... | ... | ... | ... | ... |
```

## Fixed table rules

- row order is always `D1 -> H4 -> H1 -> M15`;
- M15 is omitted when M15 was not acquired;
- acquired normalized timeframes are shown for `ACTIONABLE`, `WAIT`, `INVALID`, and `UNDETERMINED`;
- no confidence / probability / score column is allowed;
- `ACTIONABLE + LONG` -> `🟢 LONG`;
- `ACTIONABLE + SHORT` -> `🔴 SHORT`;
- `WAIT + LONG` -> `🟡 LONG待ち`;
- `WAIT + SHORT` -> `🟡 SHORT待ち`;
- directionless explicit WAIT may be shown as `🟡 WAIT`;
- explicit current INVALID may be shown as `⚪ LONG無効`, `⚪ SHORT無効`, or `⚪ INVALID` when direction is absent;
- `UNDETERMINED + LONG` -> `⚪ LONG判定保留`;
- `UNDETERMINED + SHORT` -> `⚪ SHORT判定保留`;
- directionless `UNDETERMINED` -> `⚪ 判定保留`;
- Entry/SL/TP values come only from the same timeframe's normalized TC record, including UNDETERMINED rows when TC supplied those values;
- TP display is limited to TP1/TP2/TP3; missing values are absent markers and additional Native TP values remain retained in underlying state rather than being discarded;
- values must never be synthesized to fill the table.

The table is a presentation layer. It does not replace or alter the common TradePlanState decision fields. In particular, showing an `UNDETERMINED` row does not convert it into `WAIT`, `INVALID`, or `TRADE`.

The outward strategy payload remains conceptually:

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
- provider source/symbol;
- `report_format = TF_DECISION_TABLE_V1`;
- `timeframe_decisions`, containing the exact rows used by the fixed user-facing table.

Entry/SL/TP in the common plan come from the profile decision plan only. The presentation table may show each timeframe's own Native-derived Entry/SL/TP for comparison, but values from D1/H4/H1/M15 must never be mixed to manufacture a better-looking plan.

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
