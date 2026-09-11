# TC-P0 Production Implementation Gate Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Production branch: `feature/tc-prod-v1`  
Base specification branch: `feature/tc-v1`  
Base specification completion HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## Result

**PASS WITH NOTES**

**TC-P1 readiness: GO**

TC-P0 creates the production implementation branch and fixes the P1-P5 work breakdown, implementation boundaries, regression gates and A-integration prohibition without changing frozen TC v1 semantics or implementing runtime code.

## 1. Branch audit

Verified before TC-P0 planning:

- `feature/tc-v1` HEAD = `023c8247a1a09900a7f8dccbc8434858ab2697db`;
- a separate `feature/tc-prod-v1` branch did not previously exist;
- `feature/tc-prod-v1` was created from exactly `023c8247a1a09900a7f8dccbc8434858ab2697db`.

This preserves the specification branch as a frozen reference and isolates production implementation.

## 2. Frozen baseline reviewed

TC-P0 reviewed at minimum:

- `tc/spec/TC_V1_SPECIFICATION.md`;
- `tc/spec/TC_V1_CHANGE_POLICY.md`;
- current repository production-placeholder structure under `tc/`;
- the Trade Plan A executable baseline only as READ ONLY context.

Key frozen invariants retained:

```text
INFERENCE = NO
TCTradePlanRaw v1.0.0
Original Raw First
unknown Native fields preserved
chartId derived
1 call = 1 timeframe
Adapter != Mapper != State Evaluator
Adapter retry = NONE
infrastructure failure != Trade State
no symbol auto-conversion
no 4TF synthesis
no sizing/risk/execution
no NODA logic
```

## 3. Production architecture decision

TC-P0 adopts a staged Python standard-library-first implementation using the existing repository layout.

Planned code areas:

```text
tc/native/
tc/adapter/
tc/storage/
tc/normalizer/
tc/state/
tc/engine/
tests/tc_prod/
```

No production code is added in TC-P0.

## 4. Native transport limitation / design decision

The frozen TC v1 specification defines the verified Native request boundary as:

```text
exchange
symbol
interval
```

but does not define a direct provider HTTP endpoint, credential contract or standalone runtime SDK.

TC-P0 therefore explicitly forbids inventing such a transport.

TC-P1 will implement:

- a production Native Client interface;
- exact Native request translation;
- an injected provider executor/callable boundary;
- deterministic fake-executor tests;
- no automatic retry.

The real host binding remains outside TC Engine until the eventual `trade-plan-tc` integration environment is fixed or an approved direct provider runtime contract is observed.

This is a deliberate boundary, not a silent missing implementation.

## 5. P2/P3 dependency audit

TC4-8 requires Raw Preservation before final TCTradePlanRaw emission, while the requested implementation order places Adapter before concrete Raw Storage.

TC-P0 resolves this without reordering the work packages:

```text
P2 Adapter
→ depends on narrow RawPreserver protocol
→ tests with in-memory fake

P3 Raw Storage
→ implements concrete durable RawPreserver
→ reruns Adapter + storage integration tests
```

This avoids a circular implementation dependency and preserves the frozen sequence.

## 6. Mapper risk control

Free-text observations cannot be safely converted by generative completion without violating `INFERENCE=NO`.

Therefore P4 is constrained to deterministic conservative extraction:

- explicit wording only;
- source reference retained;
- ambiguous wording -> `AMBIGUOUS`;
- absent wording -> `NOT_PROVIDED`;
- no indicator/pattern/price-derived promotion;
- no generative mapper inside the production engine.

This may prefer false negatives over invented strategic meaning. That is consistent with the frozen contract.

## 7. State evaluator boundary

P5 may implement only the frozen provisional TC semantics:

```text
WAIT
ACTIONABLE
INVALID
UNDETERMINED
```

It must not implement runtime price monitoring, automatic WAIT release, automatic invalidation transitions, 4TF synthesis or execution authorization.

The state names remain `PROVISIONAL_TC` pending future NODA/Common review.

## 8. Regression policy

- TC4-7 TCREG-01..20 remains the semantic baseline;
- implementation must conform to the baseline rather than rewriting expected results;
- P4 runs applicable mapping regressions;
- P5 runs all TESTABLE TCREG cases plus end-to-end saved-response pipeline tests;
- NOT_TESTABLE cases remain NOT_TESTABLE unless genuine new evidence/scope makes them testable.

## 9. A / Trade Plan A isolation

During TC-P0 through TC-P5:

```text
WRITE: tradeplan-engine / feature/tc-prod-v1
READ ONLY: trade-plan-a
```

Explicitly prohibited:

- Trade Plan A runtime/config changes;
- W10/Scheduler/MT4 changes;
- TC Engine connection to A;
- creation of `trade-plan-tc` before the integration phase.

A integration release requires both:

1. explicit finalization of the A-side minimum 72-hour W12-5 baseline;
2. TC-P5 production-engine audit with integration GO.

## 10. STOP discipline

Each package P0-P5 must stop after its audit.

No automatic P0->P1, P1->P2, P2->P3, P3->P4, or P4->P5 continuation is allowed.

## 11. Hard Gate

| Gate | Result |
|---|---|
| correct repository | PASS |
| frozen spec branch verified | PASS |
| production branch created from exact TC4-9 completion HEAD | PASS |
| frozen `feature/tc-v1` modified | NO |
| Trade Plan A modified | NO |
| main merged | NO |
| TC v1 fixed semantics changed | NO |
| TCTradePlanRaw schema changed | NO |
| P1-P5 responsibilities defined | PASS |
| P1 Native transport avoids invented provider API | PASS |
| P2 Adapter separated from concrete storage | PASS |
| P3 durable preservation requirements defined | PASS |
| P4 inference-free mapping rule defined | PASS |
| P5 state-only/runtime boundary defined | PASS |
| TCREG protection defined | PASS |
| A integration blocked | PASS |
| NODA logic introduced | NO |
| sizing/risk/execution introduced | NO |
| production code implemented in P0 | NO |
| current-state handoff created | PASS |
| automatic advance to P1 | NO |

## 12. Notes / implementation risks

### N-01 — real provider transport binding

The engine repository has no frozen direct provider network contract. P1 therefore implements an injected Native Client boundary. Real host binding is deferred to the integration environment unless a supported direct runtime interface is later evidenced.

### N-02 — final Common schema

Mapping and state outputs remain provisional pending NODA/Common review. Production TC implementation must not silently finalize the Common TradePlanState.

### N-03 — text extraction coverage

Conservative deterministic extraction may return `AMBIGUOUS`/`NOT_PROVIDED` more often than a generative interpreter. This is accepted to preserve `INFERENCE=NO` and must be evaluated against fixtures during P4/P5.

These notes do not block P1.

## 13. Verdict

**TC-P0 = PASS WITH NOTES**

**TC-P1 = GO, but NOT STARTED.**

TC-P0 stops here by explicit workflow rule.
