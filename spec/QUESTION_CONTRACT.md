# Common Question Contract

Status: **TC4-2R baseline**

## 1. Purpose

This contract defines **what each TradePlan Engine is asked to provide**, not **how each engine must reason**.

The common comparison surface is therefore the same Question / Output Contract. Internal decision logic remains engine-specific.

- NODA② may use NODA-specific rules internally.
- TC② uses TradingCursor Native analysis internally.
- NODA-specific rules must not be injected into TC②.
- A field not provided by the engine is not to be invented merely to complete the contract.

This contract is independent from the Market Input Contract.

> Input Contract != Question Contract

## 2. Common questions

### Q1 Environment

Target information may include, when the engine actually provides it:

- current market environment;
- directional bias;
- trend / range state;
- market structure;
- important price levels;
- other environment information explicitly recognized by the engine.

The engine is not required to provide every example sub-item.

### Q2 Setup

Target information may include:

- whether a tradable setup exists;
- long candidate;
- short candidate;
- conditional candidate;
- conditions or zones to monitor.

### Q3 Trigger

Target information may include an explicitly stated pre-entry trigger such as:

- confirmation;
- breakout;
- retest;
- close condition;
- reversal confirmation;
- another explicit entry-activation condition.

If the engine does not explicitly provide a trigger, Q3 is `NOT_PROVIDED`.

### Q4 Entry

Target information may include:

- LONG / SHORT / WAIT or equivalent native direction/state;
- entry price;
- entry zone;
- entry condition.

Only information actually provided by the engine may be extracted.

### Q5 SL

Target information may include:

- stop-loss price;
- stop-loss zone;
- explicit stop-loss rationale;
- explicit strategy invalidation basis tied to SL.

### Q6 TP

Target information may include:

- TP1;
- TP2;
- additional target(s);
- target zone;
- explicit TP rationale.

If only one target is provided, additional targets must not be generated.

### Q7 Wait / Invalidation

Target information may include:

- WAIT condition;
- No Trade / Avoid condition;
- scenario invalidation;
- alternative/opposite scenario condition;
- condition under which entry should be avoided.

## 3. Observation status

Every question mapping uses one of the following statuses:

### OBSERVED

The source Raw explicitly contains information that can be mapped to the question without adding new strategic meaning.

### NOT_PROVIDED

The source Raw does not provide the requested strategic information.

`NOT_PROVIDED` is a valid result and must not be auto-filled.

### AMBIGUOUS

Related wording is present, but the intended meaning cannot be mapped with sufficient certainty without inference.

### NOT_APPLICABLE

The question does not apply to the observed Raw/result context.

This status must not be used simply to hide missing information; ordinary absence is `NOT_PROVIDED`.

## 4. Mapping operations

### EXTRACT — ALLOWED

Copy or reference meaning explicitly contained in the Raw response.

Example:

`potentialPosition.stopLoss -> Q5 SL`

### LIGHT NORMALIZATION — ALLOWED

Normalize representation without adding strategic meaning.

Examples:

- `positionType: "long" -> LONG`
- normalize key naming or number representation while preserving the source value.

Every normalization must remain traceable to Raw.

### INFERENCE — FORBIDDEN

Do not create a strategic meaning that TradingCursor did not explicitly provide.

For example, observing an EMA crossover in Raw does not by itself authorize the mapper to label it `Trigger` unless TradingCursor explicitly presents it as the entry activation/confirmation condition.

Principle:

- EXTRACT = YES
- LIGHT NORMALIZATION = YES
- INFERENCE = NO

## 5. Required conceptual answer record

TC4-2R does not finalize a JSON Schema. The minimum conceptual record is:

```text
question_id
question_name
status
raw_reference
extracted_value
normalization_note
```

`raw_reference` must allow the mapped result to be traced back to the original engine output.

## 6. Same question does not mean same prompt

The engines do not need to receive an identical natural-language prompt.

Current TradingCursor Native Interface does not expose a free-prompt parameter. Therefore the common requirement is that outputs can be evaluated against the same Question Contract, not that identical prompt strings were sent.

Any report must disclose the actual acquisition method.

## 7. Same question does not mean same logic

NODA② and TC② may reach their outputs by completely different internal methods.

The contract must not inject NODA-specific concepts such as R01-R37, 大ダウ, 小ダウ, 際, 先行局面, 本格局面, 最終局面, BR, or other NODA-specific definitions into TC②.

## 8. Out-of-scope data

Position Size / Lot / account balance / monetary risk policy / execution instructions remain outside ② TradePlan Engine responsibility.

If TradingCursor Native Raw contains such advice, the Raw must be retained unmodified, but that content is not adopted as a Common Question answer.

## 9. Comparison levels

The common Question Contract can be used under multiple evidence levels, which must not be conflated:

- **LEVEL A — STRICT_SAME_ARTIFACT**: both engines consume the exact same market artifacts. Intended for the most rigorous future comparison.
- **LEVEL B — SAME_MARKET_OBSERVATION**: both engines observe materially aligned market/source/time conditions without exact artifact identity. Intended for conditional future comparison.
- **LEVEL C — SAME_QUESTION_NATIVE_SOURCE_SURVEY**: each engine uses its native available market source and outputs are mapped to the same Question Contract. Permitted for TC engine development and Raw-characteristic survey, not for claims of strict NODA-vs-TC performance fairness.

## 10. Core rule

**Do not force TC to answer all seven questions. Map only what TC actually provided.**
