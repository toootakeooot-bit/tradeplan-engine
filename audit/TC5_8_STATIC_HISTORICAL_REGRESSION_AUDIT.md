# TC5-8 — Static / Historical Runtime Regression Audit

Status: **PASS STATIC + PASS HISTORICAL STRUCTURE / LIVE E2E NOT YET PASSED**

## 1. Static pipeline coverage

`tests/tc5_8/test_static_pipeline.py` fixes the following regression expectations:

- `tc スポット GOLD# エントリー前` parses to TC/SPOT/ENTRY_PRE;
- terminal `#` normalizes before canonical resolution;
- GOLD#, GOLD and XAU/USD resolve to canonical GOLD;
- validated OANDA provider symbol for canonical GOLD is XAUUSD;
- USDJPY# resolves to canonical USDJPY and OANDA/USDJPY;
- exact Native intervals remain D1=1D, H4=4h, H1=1h, M15=15m;
- UNKNOWN# stops at SYMBOL_UNRESOLVED before Native planning;
- a complete synthetic four-timeframe result batch can be aggregated without creating a combined Trade State.

## 2. Historical complete-4TF evidence

Reused frozen TC4-2 formal run:

`TC4-2-OANDA-XAUUSD-20260910-01`

The run contains independent completed Native observations for D1, H4, H1 and M15.

Observed Q4 Entry direction in the frozen observation matrix:

```text
D1  = long
H4  = long
H1  = long
M15 = long
```

Therefore TC5-7 may mechanically describe entry-direction alignment as:

```text
direction_alignment = ALIGNED
```

without creating a combined LONG recommendation.

The same historical evidence contains explicit H1 WAIT evidence while other timeframes do not provide the same WAIT state. TC4-6 state fixtures do not formally assign all four per-timeframe states. Therefore TC5-8 does not infer missing states and does not claim four-timeframe state alignment.

Safe classification:

```text
direction_alignment = ALIGNED
state_alignment = INSUFFICIENT (for fully formal per-TF state replay)
combined_trade_state = NOT_DEFINED
execution_permission = false
```

## 3. Current live capability observations — 2026-09-13

Observed successful TradingCursor Native calls include:

- OANDA/XAUUSD D1 — completed;
- OANDA/XAUUSD H4 — completed;
- OANDA/XAUUSD H1 — completed;
- OANDA/XAUUSD M15 — completed on a later call;
- OANDA/USDJPY H1 — completed.

This confirms each required XAUUSD interval is individually callable in the current ChatGPT-connected environment.

However, after the successful M15 observation, a new attempt to start a fresh coherent four-call XAUUSD batch was blocked by the connector safety layer before TradingCursor execution. Therefore TC5-8 does **not** claim a current coherent D1/H4/H1/M15 end-to-end batch.

No older D1/H4/H1 result is silently combined with the later M15 result as one live batch.

## 4. Hard gates

PASS:

- TC4-9 frozen artifacts unchanged;
- TCTradePlanRaw unchanged;
- TC4 Adapter responsibility unchanged;
- no NODA logic introduced;
- no web/current-price substitution;
- no timeframe substitution;
- symbol conversion remains explicit and traceable;
- runtime failure remains separate from Trade State;
- 4TF aggregation does not create strategy synthesis;
- execution permission remains false.

NOT YET PASSED:

- one current coherent live D1/H4/H1/M15 batch through the ChatGPT-connected TradingCursor path;
- production Native Client/Adapter persistence/logging implementation;
- any separately approved combined 4TF trade-decision semantics.

## 5. Verdict

TC5-8 static and historical regression baseline = **PASS**.

Current live end-to-end runtime qualification = **NOT YET PASSED**.

TC5-9 production/runtime freeze must not be declared until the live coherent-batch gate is passed and any desired combined trade-decision semantics are separately resolved.
