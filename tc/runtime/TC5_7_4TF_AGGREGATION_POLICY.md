# TC5-7 — Multi-Timeframe Role Aggregation Policy

Status: **REVISED / ROLE-BASED AGGREGATION FIXED**

This revision supersedes the earlier TC5-7 assumption that every TC Spot run must aggregate D1/H4/H1/M15. The file path is retained for history/traceability.

## 1. Purpose

TC5-7 combines independent TradingCursor timeframe outputs by assigned role. It does not use majority voting, equal-weight alignment, or arbitrary timeframe priority.

TC4 remains unchanged: each timeframe is independently observed/mapped, one Native call handles one timeframe, and TC4 itself performs no multi-timeframe synthesis.

TC5-7 is an explicitly separate upper-runtime policy.

## 2. Profiles

### NORMAL

```text
D1 -> Environment
H4 -> Setup
H1 -> Decision
M15 -> Optional Confirmation only when H1 explicitly requires lower-timeframe confirmation
```

Initial required set: `D1/H4/H1`.

### SHORT

```text
H4  -> Environment
H1  -> Setup
M15 -> Decision
```

Initial required set: `H4/H1/M15`.

## 3. No voting

Forbidden examples:

```text
3 of 4 LONG -> LONG
D1 has higher priority because it is D1
M15 wins because it is closest to entry
all four ACTIONABLE -> automatic execution permission
```

Each profile assigns semantic responsibility before analysis starts.

## 4. Decision-plan integrity

The decision timeframe owns:

- direction;
- Entry;
- SL;
- TP;
- current WAIT/INVALID/ACTIONABLE evidence;
- Trigger/invalidation evidence used for the decision layer.

Higher-timeframe Entry/SL/TP values must not be averaged, selected, or merged into the final candidate plan.

NORMAL decision plan = H1.
SHORT decision plan = M15.

## 5. NORMAL optional drilldown

M15 is not requested merely because H1 is WAIT, Trigger is missing, or the runtime is uncertain.

M15 is requested only when explicit H1 Native evidence states that lower-timeframe/15-minute confirmation is required for the candidate decision.

Until M15 is obtained:

```text
runtime_status = NEEDS_DRILLDOWN
TradePlanState = not finalized
```

When M15 is obtained, it acts only as confirmation of the H1 candidate.

Eligible release rule:

```text
H1 candidate direction exists
AND H1 lower-TF confirmation requirement is explicit
AND M15 trade_state = ACTIONABLE
AND M15 direction = H1 candidate direction
-> common status = TRADE
```

If M15 explicitly says WAIT:

```text
-> common status = WAIT
```

If M15 is opposite-direction ACTIONABLE, INVALID, UNDETERMINED, or insufficient:

```text
-> runtime_status = HOLD
-> user display = 判定保留
-> no fabricated common TradePlanState status
```

M15 may not release an H1 WAIT that was caused by some other explicit condition unrelated to lower-timeframe confirmation.

## 6. Direct decision-state mapping

For NORMAL without drilldown, use H1.
For SHORT, use M15.

At the TC5 common-output boundary:

```text
ACTIONABLE   -> TRADE
WAIT         -> WAIT
INVALID      -> INVALID
UNDETERMINED -> Runtime HOLD / 判定保留
```

This mapping is TC5 upper-runtime/common-output semantics. It does not rewrite TC4-6 Native-state evidence.

## 7. Common TradePlanState construction direction

When finalized:

```text
symbol/timestamp -> runtime identity
status           -> TC5 common-output mapping above
direction        -> decision timeframe
environment      -> Environment-role timeframe
setup            -> Setup-role timeframe
entry/sl/tp      -> Decision-role timeframe
invalidation     -> Decision-role evidence
evidence         -> all used timeframe provenance + role mapping
source_engine    -> TC
```

The Common schema remains provisional pending NODA review.

## 8. Failure boundary

Runtime/infrastructure failures remain outside Trade State, including timeout, Native failure, provider mapping failure, missing required profile timeframe, or failed drilldown acquisition.

They must not be converted to WAIT or INVALID.

## 9. Prohibitions

TC5-7 must not:

- use MT4 screenshots or MT4 chart state as required TC input;
- inject NODA rules;
- use web/current-price analysis to fill a missing timeframe;
- substitute another interval for a required role;
- infer lower-timeframe need from generic WAIT alone;
- merge Entry/SL/TP across timeframes;
- authorize execution.

## 10. Completion criterion

TC5-7 is fixed when NORMAL and SHORT runs can be routed by role, optional M15 drilldown is triggered only by explicit H1 evidence, finalized output remains compatible with the provisional common TradePlanState direction, and every source/result remains traceable without TC4 semantic changes.
