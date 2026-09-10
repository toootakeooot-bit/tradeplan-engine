# TC4-2R Addendum to Market Input Contract

Status: **addendum — original TC4-1 contract retained**

This document records the relationship between the TC4-1 Market Input Contract and the TC4-2R Common Question policy without rewriting or deleting the TC4-1 baseline.

## 1. History

### TC4-1 original rule

TC4-1 established a prepared Market Input model centered on a traceable D1/H4/H1/M15 set and future direct reuse of the same input set by NODA② and TC②.

### TC4-2 / TC4-2P observed limitation

The currently confirmed TradingCursor Native Interface accepts exchange, symbol and interval. It does not expose a fixed-artifact input parameter, free prompt parameter, or multi-timeframe input in one call.

Therefore the strict TC4-1 same-artifact condition cannot currently be satisfied by the available TC Native execution path.

### TC4-2R revised use

TC4-1 is not deleted or declared incorrect. Instead its strict input requirements are repositioned for future controlled comparison work.

For **TC Native Raw Survey / Track TC**, fixed same-artifact reuse is no longer a Hard Gate.

For **Track COMP**, TC4-1-style traceability remains relevant and comparison evidence must explicitly identify the comparison level.

## 2. Contract separation

Two different contracts now exist:

### Market Input Contract

Defines market-input identity, provenance, timeframe and traceability requirements.

### Common Question Contract

Defines which strategy-output questions are inspected across engines:

- Environment
- Setup
- Trigger
- Entry
- SL
- TP
- Wait / Invalidation

These must not be conflated.

```text
Input Contract != Question Contract
```

## 3. Evidence levels

### LEVEL A — STRICT_SAME_ARTIFACT

TC4-1 strict target: both engines consume the exact same artifacts.

This remains the strongest future comparison condition.

### LEVEL B — SAME_MARKET_OBSERVATION

Market/source/time conditions are aligned but exact artifact consumption is not proven.

This is a weaker conditional comparison level.

### LEVEL C — SAME_QUESTION_NATIVE_SOURCE_SURVEY

TradingCursor is observed through its native available interface and its Raw is mapped against the Common Question Contract.

LEVEL C is sufficient for:

- TradingCursor Raw survey;
- output-field discovery;
- mapping design;
- TCTradePlanRaw evidence gathering.

LEVEL C is not sufficient for a claim that NODA② and TC② received identical market input.

## 4. No silent downgrade

An experiment planned as LEVEL A must not silently become LEVEL B or LEVEL C.

Every observation record must identify its comparison/evidence level.

Differences such as XM `GOLD#` versus OANDA `XAUUSD` must remain explicit and must not be described as exact input identity without evidence.

## 5. Native TC survey input

For LEVEL C TC Native Raw Survey, record the actual TradingCursor request identity available through the interface, including:

- exchange/source;
- analysis symbol;
- timeframe/interval;
- analysis timestamp where returned;
- model where returned;
- chart/run identifier where returned.

Do not fabricate `artifact_ref` fields for artifacts TradingCursor did not actually consume.

## 6. Future finalization

This addendum does not finalize the future fair-comparison Market Input schema.

LEVEL A/B methodology may be refined later in Track COMP without blocking Track TC development.
