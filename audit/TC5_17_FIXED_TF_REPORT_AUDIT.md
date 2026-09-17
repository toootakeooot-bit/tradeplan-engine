# TC5-17 Fixed TF Report Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Active branch: `feature/tc5-16-host-scheduler`

## Result

**PASS — amended: UNDETERMINED rows visible**

TC Spot and TC periodic reporting use the fixed per-symbol timeframe table contract:

```text
TF | 判定 | Entry | SL | TP1 | TP2 | TP3
```

Confidence/probability/score is not part of the report contract.

## Fixed behavior

- row order is `D1 -> H4 -> H1 -> M15`;
- M15 is omitted when it was not acquired;
- acquired normalized timeframes are shown for ACTIONABLE / WAIT / INVALID / UNDETERMINED;
- `UNDETERMINED` creates a visible `判定保留` row rather than disappearing;
- Entry/SL/TP are copied only from the same timeframe's TC normalized record, including UNDETERMINED rows when TC supplied them;
- TP display is limited to TP1/TP2/TP3 without synthesizing missing values;
- no confidence field is created;
- the common TradePlanState decision semantics remain unchanged;
- presentation rows are retained under `evidence.timeframe_decisions` with `report_format = TF_DECISION_TABLE_V1`;
- Gmail Spot and periodic notifications render the same fixed table when rows exist.

## Decision labels

- ACTIONABLE + LONG -> `🟢 LONG`
- ACTIONABLE + SHORT -> `🔴 SHORT`
- WAIT + LONG -> `🟡 LONG待ち`
- WAIT + SHORT -> `🟡 SHORT待ち`
- directionless WAIT -> `🟡 WAIT`
- explicit INVALID -> `⚪ LONG無効` / `⚪ SHORT無効` / `⚪ INVALID`
- UNDETERMINED + LONG -> `⚪ LONG判定保留`
- UNDETERMINED + SHORT -> `⚪ SHORT判定保留`
- directionless UNDETERMINED -> `⚪ 判定保留`

Displaying UNDETERMINED does not upgrade it to ACTIONABLE, WAIT, INVALID, or TRADE. It remains a presentation-only hold state.

## Files changed

- `tc/runtime/response.py`
- `tc/notification/model.py`
- `tc/notification/formatter.py`
- `tc/runtime/TC5_6_RESPONSE_FORMAT.md`
- `tests/tc5_runtime/test_tc5_17_report.py`
- `tests/tc5_notification/test_notification.py`

## Boundary audit

| Gate | Result |
|---|---|
| Spot/Periodic common table contract | PASS |
| D1/H4/H1/M15 fixed order | PASS |
| M15 absent when not acquired | PASS |
| UNDETERMINED row visible | PASS |
| confidence removed | PASS |
| Entry/SL/TP same-TF source only | PASS |
| missing TP synthesized | NO |
| more than TP3 exposed in table | NO |
| TradePlanState decision logic changed | NO |
| TC Native semantics changed | NO |
| NODA rules introduced | NO |
| Gmail table rendering | PASS |
