# TC4-7 Expected Regression Matrix

Status: **Golden regression baseline**

`GOLDEN FIXTURE` here means approved semantic regression evidence, not correct future trade outcome.

| Case | Source | Expected | Forbidden regression | Testability | Result |
|---|---|---|---|---|---|
| TCREG-01 | `TCTradeState_1h_wait_example.json` | full plan + explicit wait -> `WAIT` | Entry values force ACTIONABLE | TESTABLE | PASS |
| TCREG-02 | same | `LONG` + `WAIT` coexist | LONG and WAIT treated as conflict | TESTABLE | PASS |
| TCREG-03 | missing-trigger + 4h state | Trigger `NOT_PROVIDED` remains non-WAIT under explicit current-entry evidence | missing Trigger -> WAIT | TESTABLE | PASS |
| TCREG-04 | `TCTradeState_4h_current_entry_example.json` | explicit current-price recommendation -> `ACTIONABLE` | state lost or converted to WAIT | TESTABLE | PASS |
| TCREG-05 | 1h WAIT | Entry/SL/TP presence does not auto-ACTIONABLE | structured plan overrides WAIT | TESTABLE | PASS |
| TCREG-06 | 4h state | Invalidation Rule = `OBSERVED` | rule dropped | TESTABLE | PASS |
| TCREG-07 | 4h state | Rule observed + Current INVALID not observed | rule -> INVALID | TESTABLE | PASS |
| TCREG-08 | 4h state guardrail | no `current_price`-derived INVALID | price comparison synthesizes INVALID | TESTABLE | PASS |
| TCREG-09 | 1h/4h state | SL and Scenario Invalidation remain separate | concepts merged | TESTABLE | PASS |
| TCREG-10 | 1h state | Alternative Scenario and WAIT separate | Alternative = WAIT | TESTABLE | PASS |
| TCREG-11 | 4h state | Alternative Scenario and INVALID separate | Alternative = INVALID | TESTABLE | PASS |
| TCREG-12 | 1h mapping + state | Environment and Trade State separate | Environment determines State | TESTABLE | PASS |
| TCREG-13 | 1h mapping + state | Setup and Trade State separate | Setup determines ACTIONABLE | TESTABLE | PASS |
| TCREG-14 | 1h Raw + mapping | sizing text kept Raw, excluded from mapping/state | sizing influences State | TESTABLE | PASS |
| TCREG-15 | 1h Raw + mapping | indicators remain `NOT_MAPPED` | indicator values create State | TESTABLE | PASS |
| TCREG-16 | 1h Raw + mapping | `patternDetected` remains deferred | pattern creates Trigger/State | TESTABLE | PASS |
| TCREG-17 | missing-trigger fixture | missing Trigger mapping remains valid | missing Trigger blocks record | TESTABLE | PASS |
| TCREG-18 | state fixtures | availability status vocabulary separate from Trade State vocabulary | status auto-converted to State | TESTABLE | PASS |
| TCREG-19 | state/mapping fixtures | one record / one timeframe; synthesis=`NO` | 4TF synthetic State | TESTABLE | PASS |
| TCREG-20 | 4h state | `ACTIONABLE` is not execution permission | order/lot/risk/execution authority created | TESTABLE | PASS |

## NOT_TESTABLE baseline

| Case | Subject | Status | Reason |
|---|---|---|---|
| NT01 | Current INVALID positive recognition | NOT_TESTABLE | no real Native positive Current INVALID fixture |
| NT02 | true same-axis Structured/Text conflict resolution | NOT_TESTABLE | no real Native conflict fixture / resolution remains TBD |
| NT03 | Alternative Scenario automatic transition | NOT_TESTABLE | transition evidence unavailable |
| NT04 | WAIT release runtime evaluation | NOT_TESTABLE | runtime evaluation outside TC4-7 scope |
| NT05 | Invalidation runtime evaluation | NOT_TESTABLE | runtime evaluation outside TC4-7 scope |

## Summary

```text
TESTABLE       20
PASS           20
FAIL            0
NOT_TESTABLE    5
```

The matrix must not be interpreted as future-market performance validation or TradingCursor output determinism.
