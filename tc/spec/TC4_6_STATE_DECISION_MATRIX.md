# TC4-6 — State Decision Matrix

Status: **PROVISIONAL / semantics-only**

This matrix defines allowed state conclusions from explicit TC evidence. It is not runtime code and does not evaluate market prices.

| Case | Evidence pattern | Trigger status | Entry status | Wait evidence | Invalidation rule | Current invalid evidence | Alternative scenario | Allowed state conclusion | Forbidden conclusion | Reason / raw basis |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | Full candidate plan + explicit current wait/not-confirmed text | OBSERVED | OBSERVED | OBSERVED | NOT_PROVIDED in mapped 1h case | NOT_OBSERVED | OBSERVED | `WAIT` | ACTIONABLE merely because Entry/SL/TP exist | 1h explicit wait wording controls the current-state axis; direction remains LONG candidate |
| S2 | Trigger missing + explicit current-price entry recommendation | NOT_PROVIDED | OBSERVED | NOT_OBSERVED | OBSERVED | NOT_OBSERVED | OBSERVED | `ACTIONABLE` provisional | WAIT solely because Trigger is missing | 4h Native text explicitly recommends long entry at current price |
| S3 | Future invalidation condition only | any | any | any | OBSERVED | NOT_OBSERVED | any | preserve existing state; rule retained separately | INVALID | Future rule is not current invalid state |
| S4 | Explicit current-invalid wording | any | any | any | optional | OBSERVED | optional | `INVALID` | treating rule-only evidence as equivalent | Semantics defined, but no positive formal TC4-2 fixture observed |
| S5 | Alternative scenario only | any | any | NOT_OBSERVED | optional | NOT_OBSERVED | OBSERVED | state determined from separate current-state evidence; otherwise `UNDETERMINED` | automatic WAIT or INVALID | Alternative path is not current-state evidence |
| S6 | Entry values exist but no explicit current state/action wording | any | OBSERVED | NOT_OBSERVED | optional | NOT_OBSERVED | optional | `UNDETERMINED` | automatic ACTIONABLE | Entry field existence does not establish current action permission |
| S7 | Explicit trigger condition but no explicit wait/current-action wording | OBSERVED | optional | NOT_OBSERVED | optional | NOT_OBSERVED | optional | `UNDETERMINED` unless other explicit current-state evidence exists | automatic WAIT | A future activation condition alone is not equivalent to current WAIT under TC4-6 |
| S8 | Mutually exclusive same-axis current-state evidence with no evidence-based conflict rule | any | any | possible | optional | possible | optional | `UNDETERMINED` + preserve conflict | structured-wins/text-wins | Conflict policy is still TBD |

## Fixed semantic separations

```text
Question availability status != Trade State
Entry direction != Trade State
Environment direction != Trade State
Setup existence != Trade State
SL != Scenario Invalidation
Invalidation Rule != Current INVALID
Alternative Scenario != WAIT
Alternative Scenario != INVALID
ACTIONABLE != execution authorization
```

## 1h expected regression result

Source record: `TC4-2-OANDA-XAUUSD-20260910-01:03`

Expected:

```text
entry.direction = LONG
trade_state = WAIT
wait_release_condition_evidence = OBSERVED
current_invalid_evidence = NOT_OBSERVED
```

## 4h expected regression result

Source record convention: `TC4-2-OANDA-XAUUSD-20260910-01:02`

Expected:

```text
trigger.status = NOT_PROVIDED
entry = current-price recommendation
trade_state = ACTIONABLE (provisional)
invalidation_rule = OBSERVED
current_invalid_evidence = NOT_OBSERVED
```

## Current INVALID limitation

No formal positive Current INVALID sample is available. TC4-7 must not fabricate one. A negative/rule-only regression can be tested now; positive INVALID recognition remains TBD until real evidence exists.

## Transition status

`PARTIAL`

The model defines state meaning and evidence requirements, but no runtime transition evaluator, price monitor, alternative-path activation rule, cross-timeframe synthesis or conflict resolver exists.
