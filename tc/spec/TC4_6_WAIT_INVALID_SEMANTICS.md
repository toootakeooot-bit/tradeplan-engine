# TC4-6 — WAIT / INVALID State Semantics

Status: **TC4-6 baseline / provisional state semantics contract**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `d34c5d2019f28a70c9bd2dcbca4515e5de4b9245`

## 1. Purpose

TC4-6 defines how explicit TradingCursor-native evidence already mapped in TC4-5 may support a **provisional trade state**. It does not add market logic, infer missing conditions, evaluate live price conditions, or authorize execution.

```text
TCTradePlanRaw
      ↓
TC4-5 provisional mapping
      ↓
Q1-Q7 evidence
      ↓
TC4-6 state semantics
      ↓
provisional trade state
```

TC4-5 = DATA MAPPING.  
TC4-6 = STATE SEMANTICS.

## 2. Governing rule

```text
EXTRACT = YES
LIGHT_NORMALIZATION = YES
INFERENCE = NO
```

State may be concluded only from explicit Native current-state wording or from the absence of enough evidence to conclude a state. Strategy values do not become state authority merely because they exist.

## 3. Question status is not trade state

Question availability status remains:

- `OBSERVED`
- `NOT_PROVIDED`
- `AMBIGUOUS`
- `NOT_APPLICABLE`

These describe whether Q1-Q7 evidence is available. They are not trade states.

Examples:

- `Trigger.status = NOT_PROVIDED` does not mean WAIT or INVALID.
- `Entry.status = OBSERVED` does not mean ACTIONABLE.
- `Invalidation rule = OBSERVED` does not mean current INVALID.

## 4. Provisional state model

TC4-6 adopts the following **TC-side provisional semantics**, subject to later NODA/common review:

- `WAIT`
- `ACTIONABLE`
- `INVALID`
- `UNDETERMINED`

These are not a final Common TradePlanState enum.

### WAIT

Definition: explicit Native wording indicates that the current recommendation is to wait, that the trade is not yet confirmed, that entry should be avoided for now, or that confirmation is still pending.

WAIT may coexist with a complete candidate plan containing direction, Entry, SL and TP.

```text
candidate direction = LONG
trade_state = WAIT
```

is valid.

WAIT must not be created solely from:

- Trigger being `NOT_PROVIDED`;
- a future trigger condition existing;
- Entry/SL/TP values existing;
- trend or setup labels.

### ACTIONABLE

Definition: explicit Native wording recommends entering now/current price, and no explicit current WAIT or current INVALID evidence is present in the same observed semantic context.

Example basis: `A long position is recommended with entry at current price`.

`ACTIONABLE` is **not execution authorization**. Risk validation, sizing, Lot and broker execution remain downstream/out of scope.

ACTIONABLE is provisional because NODA② common-state requirements are not yet defined.

### INVALID

Definition: explicit Native wording states that the setup/scenario is currently invalid, has been invalidated, or is no longer valid.

A future invalidation rule such as `break below X could invalidate the setup` is not current INVALID.

No formal TC4-2 sample contains a sufficiently explicit current INVALID statement. Therefore INVALID semantics are defined, but the current-INVALID recognition path remains evidence-limited and unvalidated by a positive fixture.

### UNDETERMINED

Definition: evidence is insufficient to conclude WAIT, ACTIONABLE or INVALID without inference, or genuinely incompatible current-state evidence is present and no evidence-based conflict rule exists.

`UNDETERMINED` is a trade-state result. It is distinct from `NOT_PROVIDED`, which is a per-question availability status.

## 5. State selection constraints

The following rules are provisional semantic constraints, not runtime code.

1. Explicit current WAIT evidence can support `WAIT`.
2. Explicit current-entry recommendation can support `ACTIONABLE` when there is no explicit current WAIT/current INVALID evidence and no unresolved same-axis conflict.
3. Explicit current-invalid wording can support `INVALID`.
4. If none of those is supported without inference, use `UNDETERMINED`.
5. If mutually exclusive **current-state** evidence is simultaneously present and no observed conflict rule resolves it, do not choose a winner; use `UNDETERMINED` and preserve the conflict for later work.

These rules do not establish `structured wins` or `text wins`.

## 6. Entry / SL / TP do not define readiness

TC4-2 formal 1h contains a candidate direction, Entry, SL and TP, while explicit Native text says the breakout trade is not yet confirmed and recommends waiting for a decisive break with volume confirmation.

Therefore:

```text
Entry + SL + TP present
!= current Entry permission
```

This is a fixed TC4-6 semantic guardrail.

## 7. Trigger semantics

Trigger availability does not determine trade state by itself.

```text
Trigger = NOT_PROVIDED
!= WAIT
```

The formal 4h evidence contains no explicit pre-entry Trigger, yet Native text recommends a long position with entry at current price. TC4-6 therefore does not auto-WAIT a missing Trigger.

Likewise, the presence of a future trigger condition alone does not automatically mean current WAIT unless the Native text also expresses present waiting/not-yet-confirmed semantics.

## 8. WAIT release-condition evidence

When Native text says `wait until/for X`, X may be preserved as `wait_release_condition_evidence`.

This records the stated condition only. TC4-6 does not monitor the market, compare current price to X, or automatically transition WAIT to ACTIONABLE.

Example evidence in the 1h case includes a decisive break with volume confirmation.

## 9. Invalidation rule vs current INVALID

TC4-6 separates:

- `invalidation_rule`: a future condition that would/could invalidate a setup;
- `current_invalid_evidence`: explicit wording that the setup is already invalid now;
- `trade_state = INVALID`: a current state supported by explicit current-invalid evidence.

Example 4h evidence:

```text
a break below 4364.748 could invalidate the bullish setup
```

supports an Invalidation Rule, not current INVALID.

## 10. No current-price-derived INVALID

TC4-6 does not apply a newly invented evaluator such as:

```text
current_price < invalidation_level
→ INVALID
```

Even where `priceMetrics.current_price` exists, current INVALID is not generated unless TradingCursor itself explicitly states the current invalid state. Any future mechanical condition evaluator must be separately scoped.

## 11. SL and Invalidation remain separate

```text
Stop Loss != Scenario Invalidation
```

The 4h sample has `stopLoss = 4370` and a separate invalidation rule below `4364.748`. Both remain distinct.

The same numeric value in a future sample would not by itself merge the concepts.

## 12. Alternative Scenario remains separate

```text
Alternative Scenario != WAIT
Alternative Scenario != INVALID
```

An alternative/opposite scenario is an alternative path. Its condition becoming true does not automatically mark the original scenario INVALID unless Native evidence explicitly says so or a separately authorized transition policy is later defined.

Alternative transition policy: `TBD`.

## 13. Direction / Environment / Setup are different axes from State

The following combinations are valid:

```text
entry.direction = LONG
trade_state = WAIT
```

and:

```text
environment.direction = bullish
trade_state = UNDETERMINED
```

and:

```text
setup.status = OBSERVED
trade_state = WAIT
```

Environment, Setup, direction and state must not be collapsed.

## 14. Structured/text conflict

Different semantic axes are not conflicts. For example:

```text
potentialPosition.positionType = long
observations = wait
```

can mean `direction = LONG` and `state = WAIT`.

A true same-axis conflict such as structured LONG while text explicitly recommends SHORT now remains `TBD`. TC4-6 does not create a winner rule.

## 15. Semantic basis

State evidence should record one of these local basis categories where useful:

- `EXPLICIT_NATIVE_TEXT`
- `EXPLICIT_NATIVE_STRUCTURED_FIELD`
- `NOT_ENOUGH_EVIDENCE`

`INFERRED` is not an allowed semantic basis.

The current formal WAIT and ACTIONABLE examples rely primarily on explicit Native text.

## 16. State evidence record

Illustrative provisional shape:

```text
trade_state:
  value: WAIT | ACTIONABLE | INVALID | UNDETERMINED
  provisional: true
  semantic_basis: EXPLICIT_NATIVE_TEXT | EXPLICIT_NATIVE_STRUCTURED_FIELD | NOT_ENOUGH_EVIDENCE
  evidence:
    source_record
    raw_reference
    extracted_text
  wait_release_condition_evidence
  invalidation_rule_evidence
  current_invalid_evidence
  alternative_scenario_evidence
```

This is a TC4-6 semantics fixture shape, not a final Common JSON Schema.

## 17. 1h WAIT case

Primary source:

`fixtures/tc4_5/TCTradePlanState_1h_provisional_example.json`

Expected TC4-6 semantics:

- Entry direction: LONG candidate;
- Entry/SL/TP: present;
- explicit current wait/not-yet-confirmed evidence: present;
- state: `WAIT`;
- wait release-condition evidence: present;
- current INVALID: not evidenced;
- alternative scenario: separate.

This fixes the core rule that a full plan may coexist with WAIT.

## 18. 4h current-entry / missing-trigger case

Primary sources:

- `fixtures/tc4_5/TCTradePlanState_missing_trigger_example.json`;
- `fixtures/tc4_2/TC4-2-OANDA-XAUUSD-20260910-01/raw_4h.json`.

Expected TC4-6 semantics:

- Trigger: `NOT_PROVIDED`;
- explicit Native current-price long recommendation: present;
- explicit current WAIT: not observed;
- explicit current INVALID: not observed;
- state: `ACTIONABLE` (provisional TC state);
- invalidation rule: present separately;
- alternative scenario: present separately.

This fixes the rule that missing Trigger is not an automatic WAIT.

## 19. Current INVALID evidence status

Across the formal TC4-2 samples reviewed for TC4-6, explicit statements that the setup is already invalid now were not observed.

Therefore:

```text
Current INVALID evidence = NOT_OBSERVED
INVALID positive-fixture validation = TBD
```

This is not a failure of the semantic definition.

## 20. State transition policy

State transitions are **PARTIAL / non-runtime** in TC4-6.

Supported conceptually:

- WAIT may carry an explicit release-condition evidence;
- a setup may carry a future invalidation rule;
- ACTIONABLE is distinct from execution;
- current INVALID requires explicit current-invalid evidence.

Not fixed:

- automatic WAIT → ACTIONABLE evaluation;
- automatic WAIT/ACTIONABLE → INVALID evaluation;
- Alternative Scenario activation transitions;
- conflict resolution transitions;
- cross-timeframe transitions.

## 21. Timeframe independence

Each timeframe remains independent.

```text
1D state candidate
4h state candidate
1h state candidate
15m state candidate
```

TC4-6 creates no synthetic multi-timeframe state.

## 22. Risk and execution boundary

State semantics do not consume Position Sizing, account balance, monetary risk, Lot or generic Risk Management advice.

`ACTIONABLE` means only that Native TC text currently recommends action under this provisional semantics. It does not authorize order submission.

## 23. TC4-7 handoff

TC4-7 should use fixed fixtures to regression-test at least:

1. 1h full plan + explicit wait → `WAIT`;
2. 4h Trigger NOT_PROVIDED + explicit current-price recommendation → `ACTIONABLE`;
3. 4h Invalidation Rule present → rule retained, current state not changed to INVALID solely from the rule;
4. missing/current-state insufficient evidence → `UNDETERMINED` where applicable;
5. direction/state independence;
6. no current-price-derived INVALID;
7. no 4TF synthesis.

Current INVALID positive fixture remains unavailable and must not be fabricated.

## 24. Non-goals

TC4-6 does not implement:

- production state evaluator;
- runtime price monitoring;
- Normalizer;
- Adapter;
- final Common TradePlanState schema;
- NODA②;
- NODA rules;
- Position Sizing / Lot / risk amount;
- broker execution;
- 4TF synthesis.

## 25. Core rules

```text
LONG candidate + WAIT is valid.
LONG candidate != execute LONG now.
Invalidation Rule exists != Current INVALID.
Trigger NOT_PROVIDED != WAIT.
ACTIONABLE != execution authorization.
```
