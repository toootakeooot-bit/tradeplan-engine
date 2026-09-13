# TC5-0 — TC Spot Runtime Boundary Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Starting branch HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Specification Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

Status: **PASS WITH DEFERRED IMPLEMENTATION / TC5-0 RESPONSIBILITY FIXED**

## 1. Purpose

TC5-0 audits and fixes the responsibility boundary for a future production TC Spot Runtime capable of receiving a short command such as:

```text
tc スポット GOLD# エントリー前
```

and coordinating a TC-only, four-timeframe pre-entry analysis without changing the frozen TC Engine v1 specification.

TC5-0 is documentation/boundary work only. No production runtime code is implemented.

## 2. Artifacts added

TC5-0 adds:

```text
tc/runtime/TC_SPOT_RESPONSIBILITY.md
tc/runtime/SYMBOL_NORMALIZATION_POLICY.md
audit/TC5_0_SPOT_BOUNDARY_AUDIT.md
```

No TC4 historical artifact is intentionally modified.

## 3. Baseline/change-control review

TC Engine v1 remains frozen at Specification Freeze Point:

```text
91a146625e45c913efd9cebf63a3d25217c8bafe
```

The branch started TC5-0 at the TC4-9 attestation HEAD:

```text
023c8247a1a09900a7f8dccbc8434858ab2697db
```

TC5-0 is additive upper-runtime documentation. It does not alter the FIXED TC v1 artifacts governed by `tc/spec/TC_V1_CHANGE_POLICY.md`.

Impact classification:

| Area | TC5-0 impact |
|---|---|
| TC responsibility semantics | NO CHANGE |
| Native Interface | NO CHANGE |
| TCTradePlanRaw v1.0.0 | NO CHANGE |
| Raw preservation | NO CHANGE |
| Question Contract | NO CHANGE |
| Mapping semantics | NO CHANGE |
| State semantics | NO CHANGE |
| Adapter responsibility | NO CHANGE |
| TCREG expected behavior | NO CHANGE |
| Common TradePlanState | NO CHANGE |
| NODA | NO CHANGE |
| production implementation | DEFERRED |
| new upper-runtime boundary docs | ADDED |

## 4. Runtime responsibility fixed

TC5-0 fixes the following upper-layer responsibility chain:

```text
User / ChatGPT
  -> TC Spot Command Parser
  -> TC Spot Runtime Controller
  -> Broker Symbol Normalizer
  -> Canonical Symbol Resolver
  -> Provider Symbol Mapper
  -> 4TF Orchestrator
       -> D1  per-timeframe TC path
       -> H4  per-timeframe TC path
       -> H1  per-timeframe TC path
       -> M15 per-timeframe TC path
  -> Entry-Pre Runtime Evaluation
  -> Response Formatter
  -> User / ChatGPT
```

The 4TF Orchestrator is explicitly **outside and above** the Adapter/TC Engine. This preserves TC4-8's one-timeframe Adapter contract and the TC v1 anti-regression rule against TC-side 4TF synthesis.

## 5. Broker Suffix Normalization audit

TC5-0 separates broker suffix handling from canonical aliasing.

Registered current suffix rule:

```text
BROKER_SUFFIX_HASH_V1
terminal # -> registered broker suffix removal
```

Examples:

```text
GOLD#      -> GOLD
USDJPY#    -> USDJPY
US100Cash# -> US100Cash
JP225Cash# -> JP225Cash
```

Audit result: **PASS**.

Important boundary:

```text
Broker Suffix Normalization != Canonical Alias Resolution
```

`GOLD# -> GOLD` and `USDJPY# -> USDJPY` are not stored as individual alias rules.

The original broker/user symbol remains traceable.

## 6. Canonical Symbol Alias audit

TC5-0 fixes:

```text
GOLD
GOLD#
XAU/USD
    -> canonical GOLD
```

and:

```text
USDJPY
USDJPY#
    -> canonical USDJPY
```

For GOLD, `GOLD#` first passes through the common broker-suffix rule; `XAU/USD` is a canonical alias.

Audit result: **PASS**.

TC5-0 does not invent cross-name aliases for `US100Cash` or `JP225Cash`; only the common terminal-`#` normalization behavior is fixed for those examples. Additional canonical/provider mappings require explicit later validation.

## 7. Provider Symbol Mapping audit

Provider mapping is a separate explicit stage:

```text
canonical_symbol + provider/source
  -> validated provider mapping
  -> exact provider_symbol
  -> AdapterRequest.analysis_symbol
```

This is not an Adapter-owned conversion.

TC5-0 deliberately does not freeze `XAU/USD` as the Native token for every provider. Existing TC evidence can use provider-native tokens such as `XAUUSD`; therefore the exact provider token must be selected from validated provider/source mapping rather than inferred from the user alias.

Audit result: **PASS / implementation deferred**.

## 8. Prepared Market Input compatibility

TC4-1 permits exact broker/source symbols such as `GOLD#`, `USDJPY#`, `US100Cash#`, and `JP225Cash#` and forbids TC from silently overwriting broker-neutral identity.

TC5-0 remains compatible because:

- original broker/source symbol provenance is retained;
- normalized/canonical/provider symbols are separate traceable runtime identities;
- no historical chart/input identity is rewritten;
- the frozen Adapter still receives an already resolved exact `analysis_symbol` and does not perform automatic alias conversion.

Audit result: **PASS**.

## 9. Four-timeframe boundary audit

Standard `ENTRY_PRE` timeframe set:

```text
D1
H4
H1
M15
```

Required call model:

```text
D1   -> one Native call
H4   -> one Native call
H1   -> one Native call
M15  -> one Native call
```

The upper orchestrator may group/correlate results but may not cause the Adapter to create one synthetic 4TF TC response.

Audit result: **PASS**.

## 10. Entry-Pre responsibility audit

`ENTRY_PRE` is fixed as an analysis/evaluation mode, not execution permission.

Protected semantics remain:

```text
Entry presence != automatic ACTIONABLE
Trigger NOT_PROVIDED != WAIT
Invalidation Rule != Current INVALID
ACTIONABLE != Execution Permission
```

TC5-0 adds no new trading rule and does not finalize Common TradePlanState.

Audit result: **PASS**.

## 11. NODA separation audit

TC5 TC Spot Runtime is TC-only.

Forbidden:

```text
TC + NODA mixed judgment
NODA correction of TC output
NODA line/Formation injection
NODA completion of missing TC evidence
```

Any future comparison must exist in a separate upper comparison layer.

Audit result: **PASS**.

## 12. External-information boundary audit

TC Spot processing must not silently substitute independently obtained web/current-market information for the formal TC5 Market Input path.

Forbidden TC Spot injection includes:

- unrelated web current price;
- market news;
- third-party forecasts;
- independent ChatGPT technical analysis;
- external XAU/USD/USDJPY analysis.

Audit result: **PASS**.

## 13. Failure boundary audit

The following remain Runtime/Infrastructure failures rather than Trade States:

- command/input failure;
- symbol normalization failure;
- canonical symbol resolution failure;
- provider mapping failure;
- Market Input failure;
- Native transport failure;
- timeout;
- unsupported timeframe;
- Raw preservation failure;
- parse failure;
- Adapter failure;
- missing timeframe outcome.

Forbidden conversions:

```text
TradingCursor timeout -> WAIT
SYMBOL_UNRESOLVED -> INVALID
Adapter failure -> Trade UNDETERMINED
```

Audit result: **PASS**.

The final runtime failure enum/schema is deferred.

## 14. Execution boundary audit

TC5-0 responsibility ends at analysis/evaluation/presentation.

Out of scope:

- MT4/MT5 orders;
- automatic execution;
- Lot/position sizing;
- risk amount/account management;
- position modification/closure;
- SL/TP order modification.

Audit result: **PASS**.

## 15. Hard Gate

| Gate | Result |
|---|---|
| correct repository | PASS |
| correct branch | PASS |
| started from TC4-9 completed HEAD | PASS |
| TC4-9 Freeze changed | NO |
| TCTradePlanRaw changed | NO |
| TC4 Adapter responsibility changed | NO |
| TC strategy semantics changed | NO |
| NODA mixed into TC Spot | NO |
| TC Spot Runtime responsibility explicit | PASS |
| Command boundary explicit | PASS |
| Market Input boundary explicit | PASS |
| Native Client boundary explicit | PASS |
| 4TF Orchestrator boundary explicit | PASS |
| Orchestrator outside Adapter/TC Engine | PASS |
| Entry-Pre Runtime boundary explicit | PASS |
| Response boundary explicit | PASS |
| Execution boundary explicit | PASS |
| Failure boundary explicit | PASS |
| Broker Suffix vs Canonical Alias separated | PASS |
| terminal `#` explicitly registered as broker suffix | PASS |
| `GOLD# -> GOLD` via common suffix rule | PASS |
| `USDJPY# -> USDJPY` via common suffix rule | PASS |
| `US100Cash# -> US100Cash` via common suffix rule | PASS |
| `JP225Cash# -> JP225Cash` via common suffix rule | PASS |
| `GOLD / GOLD# / XAU/USD -> canonical GOLD` | PASS |
| `USDJPY / USDJPY# -> canonical USDJPY` | PASS |
| symbol transformations explicit/traceable | PASS |
| silent symbol conversion added to Adapter | NO |
| unknown symbol guessed | NO |
| D1/H4/H1/M15 fixed for ENTRY_PRE | PASS |
| one Native call = one timeframe retained | PASS |
| infrastructure failure -> Trade WAIT | NO |
| infrastructure failure -> Trade INVALID | NO |
| Entry candidate -> Execution Permission | NO |
| production code added | NO |

## 16. Regression / schema assessment

TC5-0 changes only additive responsibility/policy/audit documentation outside the frozen TC4 files.

TCREG expected outcomes: **NO CHANGE**.  
TCTradePlanRaw schema impact: **NONE**.  
Adapter contract impact: **NONE**.  
Common/NODA semantic impact: **NONE**.

Because TC5-0 contains no production implementation and does not alter TC4 regression artifacts or behavior, the TC4-7 regression suite is not re-baselined by this work. A later production implementation must execute applicable regression/runtime tests before being declared operational.

## 17. Deferred items

The following are explicitly not solved by TC5-0:

- production Command Parser;
- production Runtime Controller;
- Market Input Provider;
- TradingCursor Native Client;
- production Adapter/Mapper/State Evaluator;
- physical Symbol Registry/config format;
- complete provider/source symbol map;
- provider-selection logic;
- request/run/batch ID concrete format;
- persistent Raw/runtime log storage;
- orchestration concurrency/order;
- upper-layer retry count/backoff;
- runtime failure JSON schema;
- exact user-facing response schema;
- operational monitoring;
- production deployment technology.

These must be handled by later TC5 work without silently changing TC4.

## 18. Completion verdict

**TC5-0 = PASS WITH DEFERRED IMPLEMENTATION**

The responsibility and boundary model is sufficiently fixed to explain both:

```text
tc スポット GOLD# エントリー前
```

and:

```text
tc スポット USDJPY# エントリー前
```

through command intake, common `#` normalization, canonical resolution, provider mapping, four independent timeframe calls, TC-only evaluation, failure separation, response formatting, and execution exclusion.

No production implementation is authorized or claimed by TC5-0.

The exact final TC5-0 completion HEAD cannot be embedded into this file's own creating commit. It is reported externally after commit creation and final diff verification.
