# TC5-17 Fixed TF Report Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Active branch: `feature/tc5-16-host-scheduler`  
Implementation branch: `feature/tc5-17-fixed-tf-report`  
Implementation head: `e3b68798891548c15d02160d8fe525fbe6494b4d`

## Result

**PASS**

TC Spot and TC periodic reporting now carry a fixed per-symbol timeframe table contract:

```text
TF | 判定 | Entry | SL | TP1 | TP2 | TP3
```

Confidence/probability/score is not part of the report contract.

## Fixed behavior

- row order is `D1 -> H4 -> H1 -> M15`;
- M15 is omitted when it was not acquired;
- a timeframe with no reportable judgement is omitted;
- `UNDETERMINED` does not create a table row;
- Entry/SL/TP are copied only from the same timeframe's TC normalized record;
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

No label is generated for `UNDETERMINED`.

## Files changed

- `tc/runtime/response.py`
- `tc/notification/model.py`
- `tc/notification/formatter.py`
- `tc/runtime/TC5_6_RESPONSE_FORMAT.md`
- `tests/tc5_runtime/test_tc5_17_report.py`
- `tests/tc5_notification/test_notification.py`

## Regression validation

GitHub Actions workflow: `TC5 Runtime Regression`  
Run ID: `35276899306`  
Result: **SUCCESS**

Passed steps:

- TC4 regression
- TC5 profile aggregation regression
- TC5 static pipeline regression
- TC5 runtime core regression
- TC5 notification regression

The added TC5-17 tests verify fixed row order, M15 omission, judgement omission, confidence-field absence, TP1/TP2/TP3 capping, and notification table rendering.

## Boundary audit

| Gate | Result |
|---|---|
| Spot/Periodic common table contract | PASS |
| D1/H4/H1/M15 fixed order | PASS |
| M15 absent when not acquired | PASS |
| no-judgement TF omitted | PASS |
| confidence removed | PASS |
| Entry/SL/TP same-TF source only | PASS |
| missing TP synthesized | NO |
| more than TP3 exposed in table | NO |
| TradePlanState decision logic changed | NO |
| TC Native semantics changed | NO |
| NODA rules introduced | NO |
| Gmail table rendering | PASS |
| TC4/TC5 regression | PASS |
