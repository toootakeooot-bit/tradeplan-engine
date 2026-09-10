# TC4-5 — provisional TradePlanState Mapping

Status: **TC4-5 baseline / provisional mapping contract**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `c94ea9439739a2858f5b37762686468ad004faca`

## 1. Purpose

TC4-5 defines how information preserved in `TCTradePlanRaw` v1.0.0 may be projected into a **provisional** common `TradePlanState` surface.

```text
TradingCursor Native
        ↓
TCTradePlanRaw
        ↓
TC4-5 Mapping Contract
        ↓
provisional TradePlanState
```

This work does not finalize the Common TradePlanState around TC. NODA② requirements are not yet defined.

## 2. Governing rules

```text
EXTRACT = YES
LIGHT_NORMALIZATION = YES
INFERENCE = NO
```

TC4-5 is **DATA MAPPING**, not state semantics.

It does not define:
- WAIT / INVALID final decision rules;
- state transitions;
- trade readiness;
- 4TF synthesis;
- NODA logic;
- Position Sizing / Lot / account risk;
- execution;
- production Normalizer or Adapter.

## 3. Inputs and evidence

Primary input contract:
- `TCTradePlanRaw` schema version `1.0.0`;
- `tc/schema/tc_tradeplan_raw.schema.json`;
- `tc/spec/TC4_4_TCTRADEPLANRAW_SPEC.md`;
- `fixtures/tc4_4/TCTradePlanRaw_1h_example.json`.

Semantic boundaries:
- `spec/QUESTION_CONTRACT.md`;
- `spec/TRADEPLAN_STATE.md`;
- TC4-3 observable mapping documents.

`spec/TRADEPLAN_STATE.md` remains unchanged and provisional.

## 4. Provisional mapping model

The TC4-5 target is an illustrative provisional surface, not a final JSON Schema.

Conceptual shape:

```text
provisional TradePlanState
├─ Environment
├─ Setup
├─ Trigger
├─ Entry
├─ SL
├─ TP
└─ Q7 evidence
   ├─ Wait
   ├─ Invalidation
   └─ Alternative Scenario
```

Every mapped value must remain traceable to `TCTradePlanRaw` through:

```text
record_id + RFC 6901 JSON Pointer
```

For text extraction, the pointer may target `/parsed_analysis/observations`; exact sentence/span offsets remain TBD.

## 5. Mapping types

### DIRECT
Native value is carried without semantic change.

Examples:
- `futureAssumption.trend -> environment.direction`
- `entryPrice -> entry.price`
- `stopLoss -> sl.price`
- `takeProfits[] -> tp.targets[]`

### LIGHT_NORMALIZATION
Representation is normalized without changing strategic meaning.

Confirmed TC example:

```text
potentialPosition.positionType = "long"
→ entry.direction = "LONG"
```

Native and normalized values must both remain traceable.

### TEXT_EXTRACT
Only explicit text contained in `observations` is extracted for concepts not represented by a dedicated structured field.

Used for:
- Setup candidate description;
- explicit Trigger condition;
- Wait evidence;
- Invalidation evidence;
- Alternative Scenario evidence;
- rationale when explicitly present.

### NOT_MAPPED
Raw content is preserved in `TCTradePlanRaw` but is not projected into the provisional common state.

### TBD
Common adoption cannot yet be decided safely, usually because NODA② requirements or semantic evidence are insufficient.

## 6. Availability status

TC4-5 retains the Question Contract statuses:

- `OBSERVED`
- `NOT_PROVIDED`
- `AMBIGUOUS`
- `NOT_APPLICABLE`

These describe **availability/mappability of evidence**, not trade state.

They are not equivalent to future state semantics such as WAIT, INVALID or TRADE_READY.

## 7. Q1 Environment

Primary direct source:

`/parsed_analysis/futureAssumption/trend`

Provisional target:

`environment.direction`

No conversion from `bullish` to `LONG` is allowed. Environment bias and Entry direction remain separate concepts.

The following are retained in Raw and are not forced into the common target in TC4-5:
- `priceMetrics.supportLevels` — `TBD_COMMON_ADOPTION`;
- `priceMetrics.current_price` — `TBD_COMMON_ADOPTION`;
- `priceMetrics.resistanceLevels` — `TBD_COMMON_ADOPTION`;
- `futureAssumption.patternDetected` — `TBD_COMMON_ADOPTION`;
- `indicatorReadings` — `NOT_MAPPED` for common state in TC4-5.

TC-native support/resistance must not be renamed as NODA lines/fields/際.

## 8. Q2 Setup

No dedicated structured Setup field was observed.

Source: explicit setup/candidate language in `/parsed_analysis/observations`.

Mapping type: `TEXT_EXTRACT`.

A trend label alone does not create Setup.

```text
futureAssumption.trend = bullish
≠ automatic bullish setup
```

If explicit setup/candidate text is absent, use `NOT_PROVIDED` rather than inference.

## 9. Q3 Trigger

No dedicated structured Trigger field was observed.

Source: explicit pre-entry activation/confirmation language in `/parsed_analysis/observations`.

Mapping type: `TEXT_EXTRACT`.

Trigger requires explicit TradingCursor wording tying the condition to entry activation/confirmation. Indicator values, pattern labels, MACD crossovers or support commentary are not promoted automatically.

A missing Trigger does not block creation of a provisional mapping record.

## 10. Q4 Entry

Direct sources:
- `/parsed_analysis/potentialPosition/positionType`;
- `/parsed_analysis/potentialPosition/entryPrice`.

Provisional targets:
- `entry.direction`;
- `entry.price`.

`positionType` may use `LIGHT_NORMALIZATION` for representation only (`long -> LONG`, `short -> SHORT`).

Entry existence does not by itself define TRADE_READY in TC4-5.

## 11. Q5 SL

Direct source:

`/parsed_analysis/potentialPosition/stopLoss`

Provisional target:

`sl.price`

Explicit rationale may be referenced by `TEXT_EXTRACT` from observations when present.

SL and scenario Invalidation remain distinct. TC4-5 does not make them equivalent.

## 12. Q6 TP

Direct source:

`/parsed_analysis/potentialPosition/takeProfits`

Provisional target:

`tp.targets[]`

The array preserves the observed count and order. TC4-5 does not manufacture TP1/TP2/TP3 to satisfy a fixed count.

## 13. Q7 Wait / Invalidation / Alternative Scenario

TC4-5 maps **evidence only**.

Sources: explicit segments of `/parsed_analysis/observations`.

Provisional concepts:
- `wait.evidence`;
- `invalidation.evidence`;
- `alternative_scenario.evidence`.

These remain separate:

```text
Alternative Scenario != WAIT
SL != Invalidation
```

TC4-5 does not define when the overall trade state becomes WAIT or INVALID. That is TC4-6.

## 14. Missing information

Absence is allowed.

Example:

```text
trigger.status = NOT_PROVIDED
```

A missing Trigger is not a mapper error and does not make the provisional state structurally impossible. Trade readiness consequences are deferred to TC4-6.

## 15. Native vs normalized values

When representation changes, the mapping evidence should preserve:
- native value;
- normalized value;
- mapping type;
- `record_id`;
- raw JSON Pointer.

TC4-5 does not alter TCTradePlanRaw.

## 16. TC-native-only and deferred fields

### `futureAssumption.confidenceScore`

Disposition: `TC_NATIVE_ONLY_OR_TBD`.

Reason: it is observed and useful TC-native information, but NODA② common semantics are unknown. It is not promoted to a required Common field.

### `futureAssumption.patternDetected`

Disposition: `TBD_COMMON_ADOPTION`.

It is not automatically Environment, Setup or Trigger.

### `indicatorReadings`

Disposition: `NOT_MAPPED` to common state in TC4-5.

Indicators remain available in TCTradePlanRaw. The mapper does not create strategy meaning from values.

### `priceMetrics`

Disposition: `TBD_COMMON_ADOPTION`.

They are explicit Native market context but Common/NODA symmetry is not yet known.

## 17. Out-of-scope content

Position Sizing, Lot, account balance, monetary risk amount and execution remain outside the common TradePlanState authority.

TradingCursor text containing such advice stays in TCTradePlanRaw but is not mapped.

Risk/Reward remains `TBD` in responsibility classification and is not promoted to a Common field in TC4-5.

## 18. Structured/text conflict

Conflict resolution remains `TBD`.

TC4-5 does not implement `structured wins` or `text wins`.

If a future mapping operation observes a contradiction, both Raw forms must remain available and downstream status/conflict handling must be designed separately.

## 19. Timeframe independence

Each `TCTradePlanRaw` record maps independently.

```text
1D Raw  -> 1D provisional mapping
4h Raw  -> 4h provisional mapping
1h Raw  -> 1h provisional mapping
15m Raw -> 15m provisional mapping
```

TC4-5 creates no synthetic multi-timeframe TradePlanState.

## 20. 1h example

Primary example:

`fixtures/tc4_5/TCTradePlanState_1h_provisional_example.json`

The example demonstrates:
- Environment direct mapping;
- explicit Setup text extraction;
- explicit Trigger text extraction;
- Entry direction/price;
- SL;
- TP list;
- Wait evidence;
- Invalidation kept `NOT_PROVIDED` where not explicitly labeled;
- opposite/alternative scenario kept separately;
- Position Sizing excluded from mapping;
- Raw provenance retained.

The example is a **provisional mapping fixture**, not a final TradePlanState schema instance.

## 21. Missing Trigger example

`fixtures/tc4_5/TCTradePlanState_missing_trigger_example.json`

uses the formal 4h TC4-2 evidence to confirm:
- MACD crossover/support commentary is not promoted to Trigger;
- current-price Entry may coexist with `Trigger = NOT_PROVIDED`;
- missing Trigger does not prevent the mapping record from existing.

This is a static semantic mapping case. A separate TCTradePlanRaw 4h wrapper fixture is not created merely to duplicate the immutable formal Raw.

## 22. Common schema status

`spec/TRADEPLAN_STATE.md` remains **PROVISIONAL** and unchanged.

TC4-5 does not create a final common JSON Schema. Any target names in TC4-5 documents/fixtures are provisional mapping targets subject to NODA② review.

## 23. TC4-6 boundary

TC4-5 hands off evidence, not trade-state decisions.

TC4-6 must address, without being pre-decided here:
- WAIT semantics;
- INVALID semantics;
- setup-present/trigger-missing consequences;
- WAIT release condition;
- SL vs Invalidation relation;
- Alternative Scenario transition meaning;
- readiness/state transition model.

Core boundary:

```text
TC4-5 = DATA MAPPING
TC4-6 = STATE SEMANTICS
```

## 24. Non-goals

TC4-5 does not implement:
- production Mapper / Normalizer;
- Adapter;
- NODA②;
- final TradePlanState schema;
- WAIT / INVALID logic;
- 4TF synthesis;
- Position Sizing;
- execution.

## 25. Core rule

> Carry what TradingCursor actually provided into a provisional common surface; do not create what TradingCursor did not provide merely to complete that surface.
