# TC Production Implementation Plan — TC-P0

Status: **TC-P0 implementation plan / production branch baseline**

Repository: `toootakeooot-bit/tradeplan-engine`  
Production branch: `feature/tc-prod-v1`  
Base specification branch: `feature/tc-v1`  
Base specification completion HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 specification Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## 1. Purpose

TC-P0 converts the frozen TC Engine v1 specification into an implementation work plan without changing frozen semantics and without connecting to Trade Plan A.

The production sequence is:

```text
TC-P0  Production implementation plan
  ↓ STOP / audit
TC-P1  Native Client
  ↓ STOP / audit
TC-P2  Adapter
  ↓ STOP / audit
TC-P3  Raw Storage
  ↓ STOP / audit
TC-P4  Mapper
  ↓ STOP / audit
TC-P5  State Evaluator + pipeline regression
  ↓ STOP / final TC-engine implementation audit
```

Every work package is an independent gate. A later package must not start until the previous package is reported and explicitly continued.

## 2. Branch and write boundary

Production implementation is isolated from the frozen specification branch.

```text
feature/tc-v1
= frozen specification / READ ONLY

feature/tc-prod-v1
= production implementation / WRITE
```

`feature/tc-prod-v1` starts exactly from TC4-9 completion HEAD:

`023c8247a1a09900a7f8dccbc8434858ab2697db`

During TC-P0 through TC-P5:

- `tradeplan-engine/feature/tc-prod-v1` is the only production write target;
- `tradeplan-engine/feature/tc-v1` is reference-only;
- `toootakeooot-bit/trade-plan-a` is reference-only;
- no main merge;
- no Trade Plan A W10/Scheduler/MT4/runtime change;
- no TC-to-A integration.

A integration remains blocked until the A-side minimum 72-hour W12-5 baseline is explicitly finalized by the user.

## 3. Frozen invariants that implementation must preserve

The implementation must preserve all TC Engine v1 fixed rules, including:

```text
Environment → Setup → Trigger → Entry → SL → TP → Wait / Invalidation
EXTRACT = YES
LIGHT_NORMALIZATION = YES
INFERENCE = NO
TCTradePlanRaw = v1.0.0
Original Raw First
Unknown Native fields = PRESERVE
chartId = DERIVED
1 Native call = 1 timeframe = at most 1 Raw record
repeat request = new record
Trigger NOT_PROVIDED != WAIT
Entry presence != automatic ACTIONABLE
Invalidation Rule != Current INVALID
ACTIONABLE != Execution Permission
SL != Scenario Invalidation
Alternative Scenario != WAIT / INVALID
Direction / Environment / Setup != Trade State
Adapter automatic retry = NONE
infrastructure failure != Trade State
no silent symbol conversion
no unsupported-timeframe substitution
no TC-side 4TF strategy synthesis
no Position Sizing / Lot / Risk Amount / execution
no NODA logic
```

If production implementation cannot satisfy a frozen invariant, the package must stop with `SPEC CHANGE REQUIRED`; the frozen specification must not be silently edited to fit code.

## 4. Implementation technology rule

Implementation is **Python standard-library-first**.

The production branch may add a third-party dependency only when a concrete requirement cannot be met safely with the standard library and the dependency is explicitly audited in that work package.

TC-P0 does not lock a direct TradingCursor HTTP/API endpoint because TC Engine v1 does not define one. Production code must not invent provider URLs, credentials, authentication, or undocumented request fields.

Therefore TC-P1 implements a real production **Native Client boundary** with an injected provider executor/callable. A concrete host binding may be supplied later by the Trade Plan TC integration layer once the execution host is fixed. This preserves the verified Native call contract `exchange / symbol / interval` without fabricating an unavailable transport contract.

## 5. Planned package layout

The implementation should use the existing repository structure and add only what each package needs.

```text
tc/
  native/          # TC-P1: provider request/response client boundary
  adapter/         # TC-P2: request translation, Raw wrapper creation
  storage/         # TC-P3: durable original-response preservation
  normalizer/      # TC-P4: provisional mapping / light normalization
  state/           # TC-P5: provisional state evaluator
  engine/          # TC-P5: composition facade only
  schema/          # existing frozen TCTradePlanRaw schema
  spec/            # design/frozen specs

tests/
  tc_prod/         # production implementation unit/integration tests
```

The existing `tc/adapter/` and `tc/normalizer/` directories are reused rather than duplicated under a second runtime hierarchy.

## 6. Shared production principles

### 6.1 Deterministic local logic

Adapter, storage, mapping and state evaluation must be deterministic for the same saved input.

Live TradingCursor output itself is not assumed deterministic.

### 6.2 Provenance first

Every downstream mapped/state result must remain traceable to:

```text
record_id + RFC 6901 JSON Pointer
```

Text evidence should additionally carry an extract/span description when the implementation can determine it without inference.

### 6.3 Fail closed on missing evidence

Missing or ambiguous strategic evidence must not be completed from indicators, price arithmetic, patterns or model guesses.

Preferred outcome is `NOT_PROVIDED`, `AMBIGUOUS`, or `UNDETERMINED` according to the frozen layer semantics.

### 6.4 Infrastructure failures are separate

Provider failure, storage failure and parse failure are operational outcomes. They must never be converted to WAIT/ACTIONABLE/INVALID/UNDETERMINED.

### 6.5 No implicit retry

The Native Client and Adapter never auto-retry. A retry is an explicit new request and new record.

## 7. TC-P1 — Native Client

### Objective

Implement the production provider-call boundary while preserving the verified Native request surface.

### Minimum production objects

- request model containing `request_id`, `analysis_source`, `analysis_symbol`, `timeframe` plus run identity needed downstream;
- Native interval mapping D1→1D, H4→4h, H1→1h, M15→15m;
- provider executor protocol/callable accepting exact Native `exchange`, `symbol`, `interval`;
- Native response result model;
- transport/unsupported-input failure model;
- no automatic retry.

### Transport rule

Do not invent a direct TradingCursor network endpoint. The client must accept an injected provider executor. Tests use a deterministic fake executor. The real host binding is intentionally outside TC Engine until the Trade Plan TC integration environment is fixed.

### Required tests

- exact source/symbol/interval translation;
- unsupported timeframe fails explicitly;
- symbol is not auto-converted;
- provider error remains transport failure;
- no hidden retry;
- repeated explicit calls are distinct requests;
- unknown response fields pass through untouched.

### P1 exit gate

`PASS` only if the client boundary is production-usable with injection and does not assume undocumented provider behavior.

## 8. TC-P2 — Adapter

### Objective

Implement the TC4-8 Adapter contract from Native response to TCTradePlanRaw v1.0.0.

### Responsibilities

```text
request validation
Native request translation via P1
Original Native response handoff to preservation port
stable source_raw_artifact acceptance
lossless analysis JSON parse
TCTradePlanRaw identity/wrapper construction
derived chartId extraction from action_url
output structural validation
```

### Storage dependency handling

TC-P3 follows P2, therefore P2 must depend on a narrow `RawPreserver`/storage protocol, not a concrete filesystem store. P2 tests use an in-memory/fake preserver. TC-P3 later supplies the concrete implementation.

### Required tests

- Original Raw retained before parse-derived data is used;
- PARSED / NOT_PARSED / PARSE_ERROR separation;
- parse error retains preserved Original Raw;
- unknown Native fields survive;
- chartId only appears as derived metadata;
- missing strategy fields remain valid where schema allows;
- transport/preservation failure does not emit fake Trade State;
- one request yields at most one Raw record;
- repeat does not overwrite.

### P2 exit gate

TCTradePlanRaw output must remain compatible with frozen v1.0.0 and no Mapper/State behavior may be embedded in the Adapter.

## 9. TC-P3 — Raw Storage

### Objective

Implement a durable storage provider for the exact original Native response required by the Adapter.

### Requirements

- configurable storage root;
- atomic write or equivalent crash-safe publication;
- no overwrite of an existing logical Raw artifact;
- stable logical `source_raw_artifact` reference;
- exact UTF-8 JSON-value preservation and exact `analysis` string preservation;
- read-back verification;
- path traversal / invalid identifier protection;
- repeat requests stored independently;
- storage errors remain storage errors, never Trade State.

### URI/path convention

The concrete logical reference format is deliberately decided in P3 after implementation constraints are tested. P3 must document the chosen convention and compatibility implications. It must not require a TCTradePlanRaw schema change unless separately raised as `SCHEMA CHANGE REQUIRED`.

### Required tests

- write/read round trip;
- analysis string exactness;
- atomic publication behavior;
- duplicate artifact refusal;
- independent repeat records;
- failure injection / unwritable location;
- Adapter + concrete storage integration.

## 10. TC-P4 — Mapper

### Objective

Implement the TC4-5 provisional mapping contract without adding strategy inference.

### Direct/light-normalization mappings

```text
futureAssumption.trend -> environment.direction
potentialPosition.positionType -> entry.direction
potentialPosition.entryPrice -> entry.price
potentialPosition.stopLoss -> sl.price
potentialPosition.takeProfits -> tp.targets[]
```

### Text evidence policy

Free-text `observations` mapping must be conservative and deterministic.

- explicit strategic wording may be extracted;
- ambiguous wording becomes `AMBIGUOUS` rather than inferred;
- absent meaning becomes `NOT_PROVIDED`;
- indicator/pattern/price values must not be promoted into Setup/Trigger/Wait/Invalidation authority;
- no generative completion step is permitted inside the production Mapper;
- source text/raw reference must be retained for every text-derived mapping.

### Required tests

- frozen 1h mapping fixture;
- frozen 4h missing-trigger fixture;
- Trigger missing remains valid;
- indicators stay NOT_MAPPED;
- Position Sizing text remains Raw-only;
- patternDetected does not create Trigger/State;
- no 4TF aggregation;
- all mapped fields retain provenance.

### P4 regression gate

Applicable TCREG invariants must remain PASS. Expected results are not rewritten to fit implementation.

## 11. TC-P5 — State Evaluator and composed TC pipeline

### Objective

Implement TC4-6 provisional state semantics and compose P1-P4 into a production TC Engine pipeline boundary.

### State outputs

```text
WAIT
ACTIONABLE
INVALID
UNDETERMINED
```

These remain **PROVISIONAL_TC**, not final Common enum values.

### Evaluator constraints

- explicit current WAIT evidence can support WAIT;
- explicit current-entry recommendation can support ACTIONABLE when no conflicting current-state evidence exists;
- explicit current-invalid wording can support INVALID;
- insufficient or unresolved same-axis evidence yields UNDETERMINED;
- Entry/SL/TP presence alone does not create ACTIONABLE;
- Trigger NOT_PROVIDED does not create WAIT;
- Invalidation Rule alone does not create INVALID;
- current_price arithmetic does not create INVALID;
- no runtime WAIT-release or invalidation transition monitoring;
- ACTIONABLE is never execution authorization.

### Composition facade

P5 may add a thin `tc/engine/` composition facade that wires:

```text
Native Client
→ Adapter
→ Raw Storage
→ Mapper
→ State Evaluator
```

It must not add 4TF strategy synthesis, Position Sizing, risk policy, broker execution, A/W8/W9 logic, or NODA logic.

### P5 required regression

- TCREG-01 through TCREG-20: all TESTABLE cases PASS;
- existing NOT_TESTABLE cases remain NOT_TESTABLE unless genuine new evidence/runtime scope explicitly makes one testable;
- fixed saved-fixture determinism PASS;
- end-to-end saved-response pipeline test PASS;
- no specification/schema regression.

## 12. STOP discipline

At the end of every TC-P work package, report:

```text
Work
Repository
Branch
Start HEAD
End HEAD
Files changed
Tests executed
PASS / PASS WITH NOTES / FAIL / BLOCKED / SPEC CHANGE REQUIRED
TCREG impact
Raw-schema impact
Common/NODA impact
A/trade-plan-a impact
Next package GO / HOLD
```

Then **STOP**. Do not begin the next package until explicit user continuation.

## 13. A / Trade Plan TC integration boundary

TC-P0 through P5 are TC Engine-only work.

They do not create `trade-plan-tc`, do not modify `trade-plan-a`, and do not connect the new engine to W10/MT4.

After:

1. A-side minimum 72-hour W12-5 baseline is explicitly finalized; and
2. TC-P5 production-engine audit passes;

then a separate integration phase may create `trade-plan-tc` from the finalized A baseline and integrate the frozen TC production engine.

## 14. P0 completion criteria

TC-P0 is complete when:

- production branch is created from exact TC4-9 completion HEAD;
- frozen spec branch remains untouched;
- P1-P5 responsibilities and gates are fixed;
- implementation boundaries above are documented;
- A integration is explicitly blocked during P1-P5;
- current-state handoff is written;
- no production code is implemented in P0;
- audit returns P1 GO or HOLD.
