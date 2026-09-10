# TC4-7 — Fixed-Fixture Mapping / State Regression Test Plan

Status: **TC4-7 regression baseline**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `b12de3f8fbab9ef0e4ca9ad88ea04b359a758182`

## 1. Purpose

TC4-7 regression-tests the fixed semantics established by TC4-4 through TC4-6 using only saved fixtures.

```text
Fixed Raw / Fixture
       ↓
Fixed Mapping Contract
       ↓
Fixed State Semantics
       ↓
Expected Result
       ↓
Regression Test
```

This is not a re-run of TradingCursor and does not test TradingCursor determinism or market-analysis quality.

## 2. Governing boundaries

- TradingCursor re-execution: **NO**
- Production Mapper: **NO**
- Production Normalizer: **NO**
- Runtime state evaluator: **NO**
- Adapter: **NO**
- 4TF aggregation: **NO**
- NODA rules / NODA②: **NO**
- Position Sizing / Lot / risk amount / execution: **NO**
- Final Common TradePlanState schema: **NO**

TC4-7 is a static fixed-fixture regression harness only.

## 3. Fixed evidence

Primary fixtures:
- `fixtures/tc4_4/TCTradePlanRaw_1h_example.json`
- `fixtures/tc4_5/TCTradePlanState_1h_provisional_example.json`
- `fixtures/tc4_5/TCTradePlanState_missing_trigger_example.json`
- `fixtures/tc4_6/TCTradeState_1h_wait_example.json`
- `fixtures/tc4_6/TCTradeState_4h_current_entry_example.json`

Specifications:
- `tc/spec/TC4_4_TCTRADEPLANRAW_SPEC.md`
- `tc/spec/TC4_5_PROVISIONAL_STATE_MAPPING.md`
- `tc/spec/TC4_6_WAIT_INVALID_SEMANTICS.md`

Existing fixtures under `fixtures/tc4_2/`, `fixtures/tc4_4/`, `fixtures/tc4_5/`, and `fixtures/tc4_6/` are treated as immutable source evidence.

## 4. Test IDs

Use `TCREG-01` through `TCREG-20` to avoid collision with NODA R01-R37.

## 5. Testable regression cases

1. `TCREG-01` — 1h full plan + explicit wait -> `WAIT`.
2. `TCREG-02` — LONG candidate + WAIT coexist.
3. `TCREG-03` — Trigger `NOT_PROVIDED` does not imply WAIT.
4. `TCREG-04` — 4h explicit current-entry recommendation -> provisional `ACTIONABLE`.
5. `TCREG-05` — Entry presence does not automatically produce ACTIONABLE.
6. `TCREG-06` — Invalidation Rule remains observed evidence.
7. `TCREG-07` — Invalidation Rule does not imply Current INVALID.
8. `TCREG-08` — no current-price-derived INVALID.
9. `TCREG-09` — SL and Scenario Invalidation remain separate.
10. `TCREG-10` — Alternative Scenario and WAIT remain separate.
11. `TCREG-11` — Alternative Scenario and INVALID remain separate.
12. `TCREG-12` — Environment and State remain separate.
13. `TCREG-13` — Setup and State remain separate.
14. `TCREG-14` — Position Size content is retained in Raw but excluded from mapping/state.
15. `TCREG-15` — indicators do not create state semantics.
16. `TCREG-16` — `patternDetected` does not create Trigger/State.
17. `TCREG-17` — Missing Trigger does not invalidate the provisional mapping record.
18. `TCREG-18` — Question availability status and Trade State remain distinct vocabularies.
19. `TCREG-19` — no 4TF synthesis.
20. `TCREG-20` — ACTIONABLE does not authorize execution.

## 6. NOT_TESTABLE cases

The following are deliberately not fabricated:
- `NT01` — Current INVALID positive recognition: real Native evidence unavailable.
- `NT02` — true same-axis Structured/Text conflict resolution: real Native evidence unavailable.
- `NT03` — Alternative Scenario automatic transition: evidence unavailable.
- `NT04` — WAIT-release runtime evaluation: out of TC4-7 scope.
- `NT05` — Invalidation runtime evaluation: out of TC4-7 scope.

`NOT_TESTABLE` is not counted as PASS and is not a failure by itself.

## 7. Harness

Harness:

`tests/tc4_7/test_fixed_fixture_regression.py`

It uses Python standard library only and performs static assertions against the saved fixtures. It does not call external APIs.

Expected repository-root command:

```text
python tests/tc4_7/test_fixed_fixture_regression.py
```

Exit code:
- `0`: all testable cases PASS;
- nonzero: at least one fixed regression failed.

## 8. Determinism

The harness output is canonical JSON (`sort_keys=True`). Running the same harness against unchanged fixtures must produce identical output.

This establishes determinism of:

```text
saved fixture + fixed semantics
```

It does **not** establish TradingCursor Native determinism.

## 9. Failure policy

A mismatch is reported as FAIL. TC4-7 must not edit TC4-4/5/6 specifications or source fixtures merely to make the test pass.

If a mismatch reveals a real specification problem, report `SPEC CHANGE REQUIRED` and identify the affected prior Work before any correction.

## 10. Core regression invariants

```text
LONG candidate + WAIT is valid.
Entry/SL/TP present != current-action permission.
Trigger NOT_PROVIDED != WAIT.
Invalidation Rule != Current INVALID.
Alternative Scenario != WAIT / INVALID.
SL != Scenario Invalidation.
ACTIONABLE != execution authorization.
No indicator/pattern inference.
No 4TF synthesis.
```
