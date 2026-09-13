# TC5-7 — 4TF Aggregation Audit

Status: **PASS — NON-STRATEGY AGGREGATION FIXED**

Starting HEAD: `9a50b9fce9cc2869a1b95e85fd459659d2a984d3`

## Scope

TC5-7 adds an upper-runtime four-timeframe aggregate without changing TC4 timeframe independence, TC4 state semantics, TCTradePlanRaw, Adapter responsibility, NODA separation or execution boundary.

## Fixed behavior

- exact timeframe set: D1/H4/H1/M15;
- incomplete/extra timeframe set -> runtime batch failure;
- each timeframe result retained independently;
- direction comparison -> ALIGNED/DIVERGENT/INSUFFICIENT;
- state comparison -> ALIGNED/DIVERGENT/INSUFFICIENT;
- different timeframe judgments are described as DIVERGENT, not semantic contradiction;
- `combined_trade_state = NOT_DEFINED`;
- `execution_permission = false`.

## Regression cases

Defined in `tests/tc5_7/test_aggregation.py`:

1. all four LONG/ACTIONABLE -> direction ALIGNED, state ALIGNED, combined state still NOT_DEFINED;
2. all LONG but one WAIT -> direction ALIGNED, state DIVERGENT, combined state NOT_DEFINED;
3. missing M15 -> BATCH_INCOMPLETE runtime error, not Trade State;
4. missing direction -> direction_alignment INSUFFICIENT, no inferred direction.

Representative logic was also checked in an isolated interpreter with the expected outcomes above.

## TC4 compatibility

PASS:

- no synthetic TradingCursor 4TF decision;
- no timeframe priority introduced;
- no Entry/SL/TP cross-timeframe manufacture;
- no missing evidence inference;
- no NODA rule injection;
- no infrastructure failure -> WAIT/INVALID conversion;
- ACTIONABLE remains non-execution authority.

## Verdict

TC5-7 = **PASS** for aggregation/provenance responsibility.

A separate combined strategy-decision rule remains intentionally undefined. Defining one would be new TC5 strategy semantics and requires separate authorization/evidence; it is not silently introduced by aggregation.
