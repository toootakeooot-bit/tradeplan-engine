# TC5 Profile Architecture Amendment

Status: **ACTIVE TC5 RUNTIME AMENDMENT**

Starting revision point: `127bf007e7c42101afb894ba16c8efb9811ec965`.

This amendment changes TC5 runtime orchestration only. TC4-0 through TC4-9, TCTradePlanRaw v1.0.0, Adapter responsibilities, TCREG semantics, NODA separation, and one Native call = one timeframe remain unchanged.

## Superseded TC5 assumptions

The following earlier TC5 runtime assumptions are superseded:

- every ENTRY_PRE run requires D1/H4/H1/M15;
- NORMAL cannot evaluate until all four are present;
- cross-timeframe alignment/voting is the primary aggregation model.

## Active profile model

```text
NORMAL
  D1 = Environment
  H4 = Setup
  H1 = Decision
  M15 = optional confirmation only when H1 explicitly requests lower-timeframe confirmation

SHORT
  H4  = Environment
  H1  = Setup
  M15 = Decision
```

The default command without a profile token means NORMAL.

## Input boundary

TC Spot does not require MT4 screenshots or four MT4 chart captures. Market evidence is obtained through the TradingCursor Native path defined by TC5 provider mapping/request planning.

## Common output direction

When finalized, TC Spot returns the same provisional common TradePlanState direction intended for NODA/TC interoperability:

```text
status: TRADE / WAIT / INVALID
direction: LONG / SHORT / NONE
environment
setup
entry
stop_loss
take_profit
invalidation
evidence
source_engine: TC
```

Runtime HOLD/判定保留, NEEDS_DRILLDOWN/下位足確認待ち, and infrastructure failures remain outside TradePlanState.
