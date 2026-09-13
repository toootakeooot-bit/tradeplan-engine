# TC5-7 Profile Architecture Revision Audit

Status: **PASS / PROFILE REVISION APPLIED / LIVE E2E STILL OPEN**

Revision start HEAD: `127bf007e7c42101afb894ba16c8efb9811ec965`.

## Purpose

Replace the earlier TC5 assumption that every TC Spot ENTRY_PRE run requires D1/H4/H1/M15 with a role-based profile architecture consistent with the intended user workflow and common TradePlanState output.

## Active architecture

```text
NORMAL
  D1 = Environment
  H4 = Setup
  H1 = Decision
  M15 = optional Confirmation only when explicit H1 Native evidence requires lower-timeframe confirmation

SHORT
  H4  = Environment
  H1  = Setup
  M15 = Decision
```

Default four-token command remains backward compatible and selects NORMAL.

## Files revised

- `tc/runtime/command.py`
- `tc/runtime/planner.py`
- `tc/runtime/aggregate.py`
- `tc/runtime/TC5_1_COMMAND_REQUEST_SPEC.md`
- `tc/runtime/TC5_3_4TF_REQUEST_PLAN.md` (path retained; content revised to profile planning)
- `tc/runtime/TC5_5_ENTRY_PRE_EVALUATION_GATE.md`
- `tc/runtime/TC5_6_RESPONSE_FORMAT.md`
- `tc/runtime/TC5_7_4TF_AGGREGATION_POLICY.md` (path retained; title/semantics revised to MTF role aggregation)
- `tc/runtime/TC5_9_FREEZE_READINESS_GATE.md`
- `tests/tc5_7/test_aggregation.py`
- `tests/tc5_8/test_static_pipeline.py`

Added:
- `tc/runtime/TC5_PROFILE_AMENDMENT.md`
- `audit/TC5_7_PROFILE_REVISION_AUDIT.md`

## Key semantic changes

1. NORMAL initial request set changed from D1/H4/H1/M15 to D1/H4/H1.
2. SHORT is explicitly H4/H1/M15.
3. M15 NORMAL drilldown requires explicit H1 lower-timeframe confirmation evidence; generic WAIT is insufficient.
4. Cross-timeframe majority voting/alignment is removed as the primary trade-decision mechanism.
5. Entry/SL/TP come from the Decision-role plan only and are not merged across timeframes.
6. Final common output direction is restored to provisional TradePlanState:
   - ACTIONABLE -> TRADE
   - WAIT -> WAIT
   - INVALID -> INVALID
   - UNDETERMINED -> Runtime HOLD / 判定保留
7. NORMAL eligible M15 confirmation can release a lower-TF confirmation gate only when M15 is ACTIONABLE in the same H1 candidate direction.
8. Opposite M15 direction or insufficient/UNDETERMINED confirmation produces Runtime HOLD rather than a fabricated Trade State.
9. MT4 screenshots/charts are not required TC Spot inputs.
10. Execution permission remains outside TC Spot.

## TC4 impact

**NONE.**

This revision does not modify TC4-0 through TC4-9, TCTradePlanRaw v1.0.0, Adapter contract, one-call/one-timeframe rule, Raw preservation, Question Contract, TCREG semantics, or NODA separation.

The new role aggregation is explicitly TC5 upper-runtime semantics, not a claim about TradingCursor hidden reasoning.

## Static validation

A local mirror validation of the revised runtime core passed checks covering:

- default command -> NORMAL;
- explicit SHORT command;
- NORMAL plan = D1/H4/H1 roles;
- NORMAL drilldown = M15 confirmation;
- SHORT plan = H4/H1/M15 roles;
- NORMAL H1 ACTIONABLE -> common TRADE without mandatory M15;
- explicit lower-TF requirement -> NEEDS_DRILLDOWN;
- same-direction M15 ACTIONABLE -> TRADE gate release;
- opposite-direction M15 ACTIONABLE -> Runtime HOLD;
- SHORT M15 WAIT -> common WAIT;
- execution permission remains false.

Result: **PASS**.

## Remaining gates

- current live NORMAL profile E2E;
- current live SHORT profile E2E;
- current live NORMAL explicit-drilldown E2E;
- production Native Client/Adapter/persistence/logging integration;
- final Common TradePlanState schema after NODA/Common review.

## Historical note

Earlier TC5-7/TC5-8 audit artifacts describing mandatory four-timeframe aggregation remain historical evidence of the pre-revision design. This audit and `TC5_PROFILE_AMENDMENT.md` define the active TC5 runtime architecture after this revision.
