# TC-P5 State Evaluator + Pipeline Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-prod-v1`  
Start HEAD: `a7139bf14e148532de453a69c909bb4459c24c9e`  
Base specification completion HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## Result

**PASS WITH NOTES**

**TC Engine production implementation (P0-P5): COMPLETE WITH NOTES**

**TC-side integration readiness: GO WITH NOTES**

**A integration: BLOCKED until the user explicitly finalizes the A-side minimum 72-hour W12-5 baseline.**

TC-P5 implements the TC4-6 provisional State Evaluator and a thin one-timeframe composition facade across the existing production layers. It does not create `trade-plan-tc`, does not modify Trade Plan A, and does not authorize execution.

## 1. Implemented scope

Production code added:

- `tc/state/evaluator.py`
- `tc/state/__init__.py`
- `tc/engine/engine.py`
- `tc/engine/__init__.py`

Tests added:

- `tests/tc_prod/test_p5_state_pipeline.py`

Pipeline:

```text
NativeClient
  -> TCAdapter
  -> RawPreserver / FileRawStorage
  -> TCTradePlanRaw v1.0.0
  -> TCMapper
  -> TCStateEvaluator
  -> provisional TC State
```

One call remains one timeframe. No 4TF synthetic decision is produced.

## 2. Provisional state outputs

P5 implements only the TC4-6 provisional vocabulary:

```text
WAIT
ACTIONABLE
INVALID
UNDETERMINED
```

The output is explicitly marked `PROVISIONAL_TC`; it is not a finalized Common/NODA enum.

Question availability remains separately limited to:

```text
OBSERVED
NOT_PROVIDED
AMBIGUOUS
NOT_APPLICABLE
```

Question status is never auto-converted into Trade State.

## 3. State selection behavior

### WAIT

Explicit current Native text such as current waiting / not-yet-confirmed / avoid-entry wording can support WAIT.

The fixed 1h formal Native Raw produces:

```text
entry.direction = LONG
Entry/SL/TP = present
trade_state = WAIT
```

Therefore full candidate plan values do not force ACTIONABLE.

### ACTIONABLE

Explicit current-action wording such as:

```text
A long position is recommended with entry at current price
```

can support ACTIONABLE only when explicit current WAIT/current INVALID evidence is absent.

The fixed 4h formal Native Raw produces ACTIONABLE even though Trigger is `NOT_PROVIDED`.

ACTIONABLE is not execution authorization.

### INVALID

The semantic recognition path is implemented only for explicit current-invalid wording, consistent with TC4-6.

No positive real Native Current INVALID fixture exists. The P5 test suite does **not** fabricate one. NT01 remains NOT_TESTABLE.

### UNDETERMINED

UNDETERMINED is returned when no explicit current WAIT/ACTIONABLE/INVALID evidence exists, or when mutually exclusive explicit current-state evidence is present and no evidence-based winner rule exists.

A candidate Entry alone remains insufficient.

## 4. Wait release evidence

When WAIT is supported and an explicit Trigger condition exists, P5 preserves the stated release condition as evidence and marks:

```text
runtime_evaluation = NOT_IMPLEMENTED
```

P5 does not monitor market price or automatically transition WAIT -> ACTIONABLE.

## 5. Invalidation separation

P5 preserves all fixed separations:

```text
SL != Scenario Invalidation
Invalidation Rule != Current INVALID
Alternative Scenario != WAIT
Alternative Scenario != INVALID
```

The fixed 4h phrase:

```text
a break below 4364.748 could invalidate the bullish setup
```

is retained as future `invalidation_rule_evidence` and does not produce INVALID.

P5 never compares `priceMetrics.current_price` with an invalidation level to synthesize current INVALID.

## 6. Conflict behavior

If explicit mutually exclusive **current-state** text supports more than one of WAIT/ACTIONABLE/INVALID in the same record, P5 returns:

```text
UNDETERMINED
conflict_preserved = true
```

This does not establish `structured wins` or `text wins`.

The true structured-vs-text same-axis conflict remains NT02 / TBD because no genuine Native fixture/policy exists.

## 7. Provenance

State evidence retains:

```text
record_id
/parsed_analysis/observations
character_span.start
character_span.end
```

Mapped plan values continue to retain P4 record + RFC6901 provenance.

No evidence is generated from RSI/EMA/BB/MACD, `patternDetected`, current-price arithmetic, or generic risk/sizing text.

## 8. Composition facade

`TCEngine` is deliberately thin. It composes:

```text
NativeClient + RawPreserver
-> TCAdapter
-> TCMapper
-> TCStateEvaluator
```

and returns:

- `raw_record`
- `mapping`
- `state`

It adds no strategy rule beyond the frozen P1-P5 contracts.

Provider/Adapter/Storage/Parse/Mapper failures propagate as pipeline failures rather than becoming a fake Trade State.

## 9. Regression execution

Command:

```text
python -m unittest -v \
  tests.tc_prod.test_native_client \
  tests.tc_prod.test_adapter \
  tests.tc_prod.test_raw_storage \
  tests.tc_prod.test_mapper \
  tests.tc_prod.test_p5_state_pipeline
```

Result:

```text
P1 Native Client:  9 PASS / 0 FAIL
P2 Adapter:       12 PASS / 0 FAIL
P3 Raw Storage:   10 PASS / 0 FAIL
P4 Mapper:        10 PASS / 0 FAIL
P5 State/Pipeline:25 PASS / 0 FAIL
TOTAL:            66 PASS / 0 FAIL
```

P5 production TCREG-01 through TCREG-20: **20 PASS / 0 FAIL**.

The P5 tests use the frozen formal 1h and 4h TradingCursor Native Raw files already stored under `fixtures/tc4_2/...` for end-to-end regression.

## 10. TCREG status

TESTABLE baseline remains:

```text
TCREG-01 ... TCREG-20 = PASS
```

NOT_TESTABLE remains:

- NT01 Current INVALID positive recognition — no real positive Native fixture;
- NT02 true structured/text same-axis conflict resolution — evidence/policy unavailable;
- NT03 Alternative Scenario automatic transition — not fixed;
- NT04 WAIT release runtime evaluation — out of scope;
- NT05 invalidation runtime evaluation — out of scope.

No TCREG expected result was rewritten to fit Production code.

## 11. Frozen-invariant audit

| Gate | Result |
|---|---|
| correct repository / production branch | PASS |
| started from TC-P4 HEAD | PASS |
| frozen `feature/tc-v1` changed | NO |
| TCTradePlanRaw schema changed | NO |
| Common TradePlanState finalized | NO |
| WAIT explicit-evidence semantics | PASS |
| ACTIONABLE explicit-current-entry semantics | PASS |
| Trigger NOT_PROVIDED -> WAIT | NO |
| Entry/SL/TP -> automatic ACTIONABLE | NO |
| Invalidation Rule -> current INVALID | NO |
| current_price arithmetic -> INVALID | NO |
| Alternative Scenario -> WAIT/INVALID | NO |
| Environment/Setup/Direction -> State | NO |
| ACTIONABLE authorizes execution | NO |
| infrastructure/parse failure -> Trade State | NO |
| automatic WAIT release evaluator | NO |
| automatic invalidation evaluator | NO |
| 4TF synthesis | NO |
| Position Sizing / Risk Amount / Lot / Execution added | NO |
| NODA logic added | NO |
| Trade Plan A changed | NO |
| A connected to TC | NO |
| `trade-plan-tc` created | NO |
| main merged | NO |
| full P1-P5 local regression | 66 PASS / 0 FAIL |
| production TCREG-01..20 | 20 PASS / 0 FAIL |

## 12. Schema / Common / A impact

TCTradePlanRaw schema impact: **NONE**.

Frozen TC v1 specification impact: **NONE**.

Common/NODA impact: **NONE; Common state remains provisional**.

Trade Plan A impact: **NONE**.

## 13. Notes

### N-01 — real TradingCursor host binding remains deferred

P1-P5 use the frozen injected provider boundary. No direct endpoint/auth contract was invented. Live host binding belongs to the later Trade Plan TC integration phase.

### N-02 — Windows Raw Storage publication path remains unexecuted on this host

The current regression host is POSIX. The P3 Windows publication branch is still an integration item for the future Windows deployment environment.

### N-03 — Current INVALID positive fixture remains unavailable

INVALID semantics are implemented according to TC4-6, but positive validation remains NT01 until genuine Native evidence exists. No synthetic positive INVALID fixture was used to upgrade that status.

### N-04 — narrow text recognition is deliberate

P4/P5 remain conservative deterministic extractors. New TradingCursor wording can legitimately result in NOT_PROVIDED/UNDETERMINED rather than semantic guessing. Coverage extension requires audited evidence and regression.

### N-05 — A integration remains gated

TC-side implementation is ready to integrate, but A-side integration must not start until the user explicitly finalizes the minimum 72-hour W12-5 baseline. `trade-plan-a` remains READ ONLY.

## 14. Verdict

**TC-P5 = PASS WITH NOTES**

**TC-P0 through TC-P5 production-engine implementation = COMPLETE WITH NOTES.**

**TC-side integration = GO WITH NOTES.**

**Overall A + TC integration = HOLD pending A-side 72-hour W12-5 finalization.**

STOP here. Do not create `trade-plan-tc`, modify `trade-plan-a`, or begin integration without explicit user instruction after the A gate is satisfied.
