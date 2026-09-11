# TC-P4 Mapper Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-prod-v1`  
Start HEAD: `3a70e1dae96709012a210602adf7113abcf08bde`  
Base specification completion HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## Result

**PASS WITH NOTES**

**TC-P5 readiness: GO**

TC-P4 implements only the TC4-5 provisional Mapping contract. It maps one `TCTradePlanRaw v1.0.0` record into one provisional mapping result using DIRECT, LIGHT_NORMALIZATION and conservative deterministic TEXT_EXTRACT operations. It does not evaluate WAIT/ACTIONABLE/INVALID/UNDETERMINED and does not aggregate timeframes.

## 1. Implemented scope

Production code added:

- `tc/normalizer/mapper.py`
- `tc/normalizer/__init__.py`

Tests added:

- `tests/tc_prod/test_mapper.py`

Mapping pipeline:

```text
TCTradePlanRaw v1.0.0
  -> validate parsed evidence availability
  -> DIRECT / LIGHT_NORMALIZATION
  -> conservative deterministic TEXT_EXTRACT
  -> provisional question mapping
```

No generative completion, indicator-derived strategy logic, price arithmetic, state evaluation, sizing, execution, NODA logic or 4TF synthesis is present.

## 2. Direct/light-normalization mappings

Implemented exactly from TC4-5:

```text
futureAssumption.trend -> environment.direction
potentialPosition.positionType -> entry.direction
potentialPosition.entryPrice -> entry.price
potentialPosition.stopLoss -> sl.price
potentialPosition.takeProfits -> tp.targets[]
```

Confirmed representation normalization is limited to:

```text
long  -> LONG
short -> SHORT
```

An unrecognized position direction is not guessed or uppercased into authority; Entry status becomes `AMBIGUOUS` for that representation while any independently valid Entry price remains traceable.

Environment trend is not converted to Entry direction.

## 3. Text evidence policy

`observations` handling is deterministic and conservative. The mapper uses fixed explicit cue extraction only.

Frozen evidence reproduced:

### 1h

- Setup: `a breakout trade is not yet confirmed`
- Trigger: explicit `wait for a decisive break ... for a long, or below ... for a short`
- Wait evidence: explicit conservative `wait for ...` clause
- Invalidation: `NOT_PROVIDED`
- Alternative Scenario: explicit `below ... for a short`

### 4h

- Setup: explicit sentence containing `setup`
- Trigger: `NOT_PROVIDED`
- MACD crossover / support / pattern labels do not create Trigger
- Invalidation evidence: explicit `could invalidate ... setup`
- Alternative Scenario: explicit `Alternative scenario:` text

Unmatched text becomes `NOT_PROVIDED`. Explicitly conflict/ambiguity-marked wording in the limited supported cue surface can become `AMBIGUOUS`. The mapper does not call a model or perform semantic completion.

## 4. Provenance

Every direct/light-normalized mapped value carries:

```text
record_id
RFC 6901 JSON Pointer
```

Every text-derived evidence item carries:

```text
record_id
/parsed_analysis/observations
character_span.start
character_span.end
```

The span is verified against the exact source observation string in tests.

## 5. Deferred/excluded Native fields

Frozen dispositions are emitted explicitly:

```text
indicatorReadings = NOT_MAPPED
priceMetrics = TBD_COMMON_ADOPTION
futureAssumption.confidenceScore = TC_NATIVE_ONLY_OR_TBD
futureAssumption.patternDetected = TBD_COMMON_ADOPTION
position_sizing_text = EXCLUDED_OUT_OF_SCOPE
risk_reward = TBD
structured_text_conflict_resolution = TBD
```

The mapper does not create strategy authority from any of them.

## 6. Parse/infrastructure separation

`TC-P4` maps only a `PARSED` TCTradePlanRaw record. If `parse_status != PARSED`, mapping raises `MapperUnavailableError` rather than converting parse/storage/provider conditions into `NOT_PROVIDED`, `WAIT`, `INVALID` or `UNDETERMINED`.

Within a valid PARSED record, absent strategic fields map to `NOT_PROVIDED` as specified.

## 7. One-record / one-timeframe boundary

One call to `map_record()` accepts exactly one Raw record and returns one mapping result whose source timeframe is the Native interval from that record.

No multi-record input, timeframe list, weighting, vote or synthetic 4TF state exists.

## 8. Status-definition compatibility check

`spec/STATUS_DEFINITION.md` was explicitly reviewed before implementation.

TC-P4 does not emit a Trade State. Question availability remains limited to:

```text
OBSERVED
NOT_PROVIDED
AMBIGUOUS
NOT_APPLICABLE
```

and remains separate from the provisional Trade State vocabulary reserved for P5.

No conflict was found between TC-P4 mapping behavior and the provisional status definition.

## 9. Test execution

Command:

```text
python -m unittest -v tests.tc_prod.test_mapper
```

Result:

```text
P4 Mapper: 10 PASS / 0 FAIL
```

This is local deterministic saved-input evidence. It is not live TradingCursor connectivity, Windows storage, Trade Plan A integration, or P5 State evaluation evidence.

P1-P3 production files are unchanged by P4. Their prior audited test baseline remains 31 PASS / 0 FAIL.

## 10. Applicable TCREG impact

TC4-7 expected results were not modified.

P4 specifically protects the mapping-applicable invariants, including:

- TCREG-03 mapping side: missing Trigger remains `NOT_PROVIDED`;
- TCREG-12: Environment remains separate from State;
- TCREG-13: Setup is mapping evidence, not State;
- TCREG-14: Position Size remains excluded;
- TCREG-15: indicators remain `NOT_MAPPED`;
- TCREG-16: `patternDetected` remains deferred;
- TCREG-17: missing Trigger does not invalidate mapping;
- TCREG-18: availability status vocabulary remains separate from Trade State vocabulary;
- TCREG-19: one record / one timeframe, no 4TF synthesis.

State-dependent TCREG assertions remain TC-P5 scope and were not redefined in P4.

## 11. Frozen-invariant audit

| Gate | Result |
|---|---|
| correct repository / production branch | PASS |
| started from TC-P3 HEAD | PASS |
| frozen `feature/tc-v1` changed | NO |
| TCTradePlanRaw schema changed | NO |
| Common TradePlanState finalized | NO |
| DIRECT mappings match TC4-5 | PASS |
| `long/short` light normalization only | PASS |
| Environment converted to Entry direction | NO |
| missing Trigger remains valid | PASS |
| MACD/pattern/support creates Trigger | NO |
| indicator values create strategy meaning | NO |
| priceMetrics promoted to Common authority | NO |
| Position Sizing mapped | NO |
| text extraction generative/model-based | NO |
| absent evidence filled by inference | NO |
| provenance retained | PASS |
| text character span retained | PASS |
| parse failure converted to Question status/Trade State | NO |
| Mapper emits Trade State | NO |
| 4TF synthesis added | NO |
| SL merged with Invalidation | NO |
| Alternative merged with Wait/Invalidation | NO |
| Position Sizing / Risk Amount / Lot / Execution added | NO |
| NODA logic added | NO |
| TC4-7 expected results changed | NO |
| Trade Plan A changed | NO |
| A connected to TC | NO |
| main merged | NO |
| P4 tests | 10 PASS / 0 FAIL |

## 12. Notes

### N-01 — deterministic text extractor is intentionally narrow

The production text extractor intentionally recognizes only explicit cue forms needed by the frozen TC evidence and a small conservative extension surface. New Native wording may therefore map to `NOT_PROVIDED` even when a human could interpret it. This is preferable to inference under TC v1. New cue coverage must be added through audited evidence/regression, not silently generalized.

### N-02 — structured/text true conflict remains TBD

P4 preserves the TC4-5 rule that true same-axis conflict resolution is not defined. P4 does not add `structured wins` or `text wins`. Genuine conflict handling remains a known TBD for later evidence/change control.

### N-03 — State semantics remain P5

P4 maps Wait/Invalidation/Alternative **evidence only**. It does not decide WAIT, ACTIONABLE, INVALID or UNDETERMINED. This is the required TC4-5 / TC4-6 boundary.

These notes do not block P5.

## 13. Verdict

**TC-P4 = PASS WITH NOTES**

**TC-P5 = GO, but NOT STARTED.**

STOP here under the P0 work-package discipline.
