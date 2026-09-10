# TC4-2R — Common Question Policy and TC4-2 Restart Rule

Status: **fixed for TC Native Raw Survey**

## 1. Decision

TC4-2R separates two goals that were previously coupled:

1. **Track TC — TradingCursor Engine development / Raw survey**
2. **Track COMP — future NODA② vs TC② fair-comparison methodology**

For Track TC, exact same market artifacts are no longer a prerequisite to observe TradingCursor Native Raw.

The development comparison principle becomes:

**same Question / Output Contract, engine-native reasoning**

This change does not claim that LEVEL C is a fair performance comparison between NODA② and TC②.

## 2. Responsibility boundary preserved

TC4-0 remains unchanged. ② TradePlan Engine responsibility is still:

Environment → Setup → Trigger → Entry → SL → TP → Wait / Invalidation

Out of scope remains:

- account balance management;
- monetary risk amount selection;
- Lot;
- Position Size;
- order execution;
- open-position management.

## 3. Common Question Contract

The common questions are fixed as:

- Q1 Environment
- Q2 Setup
- Q3 Trigger
- Q4 Entry
- Q5 SL
- Q6 TP
- Q7 Wait / Invalidation

The canonical definitions are in `spec/QUESTION_CONTRACT.md`.

The same questions define the **comparison surface**. They do not define the engine's internal algorithm.

## 4. TC acquisition model

Current confirmed TradingCursor Native call accepts:

- exchange
- symbol
- interval

It does not expose, through the currently available interface:

- a fixed chart-artifact input parameter;
- a free prompt parameter;
- multi-timeframe input in one call.

Therefore TC Native Raw is acquired first and mapped afterward:

```text
TradingCursor Native Call
        ↓
Raw Response — preserve first
        ↓
Question Contract mapping
```

## 5. Mapping policy

Allowed:

- EXTRACT
- LIGHT NORMALIZATION

Forbidden:

- INFERENCE

A missing answer is not a defect in the mapper. It is recorded as `NOT_PROVIDED`.

Statuses:

- `OBSERVED`
- `NOT_PROVIDED`
- `AMBIGUOUS`
- `NOT_APPLICABLE`

### Example

If Raw explicitly contains:

- a proposed long entry;
- stop loss;
- take-profit targets;

but no explicit entry activation trigger, then:

- Q4 Entry = OBSERVED
- Q5 SL = OBSERVED
- Q6 TP = OBSERVED
- Q3 Trigger = NOT_PROVIDED

The mapper must not invent a breakout/retest trigger from surrounding indicator commentary.

## 6. Same prompt policy

Identical prompt text is **not required** for TC Native Survey.

Reason: the confirmed TradingCursor Native Interface does not expose a free-prompt input.

This limitation must remain visible in audit records. The system must not claim an identical-prompt experiment occurred.

## 7. Market-comparison levels

### LEVEL A — STRICT_SAME_ARTIFACT

Both engines consume the exact same frozen market artifacts.

Use: future strict NODA-vs-TC comparison.

Status for current TC Native Interface: not currently available.

### LEVEL B — SAME_MARKET_OBSERVATION

Both engines consume/observe materially aligned market, source and observation conditions, without proof of exact artifact identity.

Use: future conditional comparison.

Status: methodology not yet fully established.

### LEVEL C — SAME_QUESTION_NATIVE_SOURCE_SURVEY

TradingCursor uses its confirmed native source/interface. Raw output is retained and mapped against the same Common Question Contract used for future NODA② output.

Use:

- TC Raw-characteristic survey;
- TC output-structure discovery;
- TCTradePlanRaw design evidence;
- observable mapping design.

Not permitted use:

- claiming strict NODA-vs-TC fairness;
- claiming same-artifact comparison;
- claiming same-source comparison when source differs.

## 8. TC4-2 mode after TC4-2R

TC4-2 keeps the name:

**TradingCursor生分析調査**

but its formal mode for restart is:

```text
survey_mode = TC_NATIVE_RAW_SURVEY
comparison_level = LEVEL_C
```

## 9. New TC4-2 restart gate

TC4-2 Native Raw Survey may restart when all of the following are true:

- TradingCursor Native Analysis can be executed;
- source/exchange can be recorded;
- symbol can be recorded;
- timeframe can be recorded;
- Raw Response can be preserved before classification;
- model availability can be recorded;
- analysis timestamp availability can be recorded;
- chart/run identifier can be stored where exposed;
- D1 / H4 / H1 / M15 can be invoked individually;
- Raw and Question Contract result are separate records;
- missing Question Contract items can be represented as NOT_PROVIDED;
- ChatGPT strategic supplementation is prohibited;
- NODA rules are not injected into TC;
- Position Size advice is not promoted into the common ② output;
- the run is explicitly labelled LEVEL C and not strict same-artifact comparison.

TC4-2P Pilot evidence established these conditions sufficiently for a LEVEL C Native Raw Survey restart.

## 10. Raw retention

Raw Response is primary evidence.

When exposed, preserve alongside Raw:

- exchange/source;
- symbol;
- interval;
- model;
- analysis timestamp;
- action URL;
- chartId or other run identifier;
- execution order/run index.

Raw must not be edited to remove unwanted recommendations, including risk/sizing commentary.

## 11. Position Size content

If TradingCursor Raw contains language such as reducing/increasing position size:

- retain the original statement in Raw;
- do not map it to Q1-Q7 unless another explicit strategy statement independently qualifies;
- do not treat it as TradePlan Engine sizing authority.

This preserves evidence without violating TC4-0 responsibility.

## 12. NODA separation

NODA② is not implemented by TC4-2R.

Future NODA② will answer the same Q1-Q7 surface using NODA rules internally. Those rules remain private to NODA② and are not inserted into TradingCursor calls or mappings.

## 13. TC4-3 naming and scope

Recommended name:

**TC4-3 — TC出力判断構造定義 / TC Observable Decision Structure**

TC4-3 must define observable relationships between Raw and Q1-Q7. It must not claim to reverse-engineer TradingCursor's hidden reasoning sequence.

TC4-2R does not start TC4-3.

## 14. Track separation

### Track TC

Native Raw → retention → Common Question mapping → TC output structure.

LEVEL C is sufficient to continue this track.

### Track COMP

Establish LEVEL A/B conditions before performing comparative performance or decision-quality claims between NODA② and TC②.

Track COMP incompleteness must not block TC Raw engineering work.

## 15. Non-goals

TC4-2R does not implement:

- TC strategy logic;
- Adapter;
- Normalizer;
- TCTradePlanRaw final schema;
- TradePlanState final schema;
- Position Sizing;
- execution;
- NODA logic;
- fair-performance testing.
