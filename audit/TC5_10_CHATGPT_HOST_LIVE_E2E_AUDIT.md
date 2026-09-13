# TC5-10 — ChatGPT Host Binding / Live E2E Audit

Date: 2026-09-13

Result: **PASS — CHATGPT ON-DEMAND HOST MODE**

## Scope

This audit qualifies only user-triggered TC Spot operation in ChatGPT.

```text
user command -> ChatGPT Host -> TradingCursor Native -> TC5 semantics -> user response
```

No scheduled, autonomous, background, or order-execution behavior is included.

## Fresh NORMAL Live

Command:

```text
tc スポット GOLD# エントリー前
```

Resolved target:

```text
canonical = GOLD
provider  = OANDA
symbol    = XAUUSD
```

Fresh Native sequence:

```text
D1  2026-09-13T05:53:12.774Z
H4  2026-09-13T05:53:40.479Z
H1  2026-09-13T05:54:25.889Z
```

Decision H1 contained explicit `entry at current price` wording and a LONG potentialPosition. Under frozen TC4 state semantics:

```text
trade_state = ACTIONABLE
TC5 common status = TRADE
direction = LONG
execution_permission = false
```

Captured fixture:

```text
fixtures/tc5_live/TC5-LIVE-NORMAL-GOLD-20260913-0553Z.json
```

Recorded-live Raw-to-TradePlanState replay: **PASS**.

## Fresh SHORT Live

Command:

```text
tc スポット GOLD# 短期 エントリー前
```

Fresh Native sequence:

```text
H4   2026-09-13T05:54:50.720Z
H1   2026-09-13T05:55:26.340Z
M15  2026-09-13T05:55:53.541Z
```

Decision M15 contained explicit `entry at current price` wording and a LONG potentialPosition. Under frozen TC4 state semantics:

```text
trade_state = ACTIONABLE
TC5 common status = TRADE
direction = LONG
execution_permission = false
```

Captured fixture:

```text
fixtures/tc5_live/TC5-LIVE-SHORT-GOLD-20260913-0554Z.json
```

Recorded-live Raw-to-TradePlanState replay: **PASS**.

## Regression

GitHub Actions run 25 on head `a149c98f248d677cbc6efd0bd45a674f2b0e193a` completed successfully.

Passed steps include:

- TC4 regression;
- TC5 profile aggregation regression;
- TC5 static pipeline regression;
- TC5 runtime core regression;
- recorded-live NORMAL replay;
- recorded-live SHORT replay;
- Raw persistence;
- Host binding;
- symbol/provider registry.

## Boundary checks

```text
NODA contamination                    = NONE
web/current-price substitution         = NONE
interval substitution                  = NONE
execution permission                   = FALSE
runtime failure -> Trade State         = PROHIBITED
one Native call -> one timeframe       = PRESERVED
TC4-9 Freeze                           = UNCHANGED
```

## Drilldown

A naturally occurring NORMAL H1 output that explicitly requests lower-timeframe confirmation was not observed in this audit.

This does not block ChatGPT On-Demand Freeze because:

- the branch is already deterministic-regression tested;
- M15 Native access is proven;
- TC5-7 explicitly defines the release/HOLD behavior;
- the feature will be live-audited when such a Native condition naturally occurs.

## Audit conclusion

TC5-10 satisfies the operational requirement for user-triggered ChatGPT TC Spot use.

The remaining autonomous/direct repo-hosted connector binding is outside this mode and is not required for this baseline.
