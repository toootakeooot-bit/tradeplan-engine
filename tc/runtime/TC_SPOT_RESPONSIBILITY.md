# TC5-0 — TC Spot Runtime Responsibility

Status: **TC5-0 responsibility / boundary baseline — non-production**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Starting branch HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Specification Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## 1. Purpose

TC Spot Runtime is the upper runtime/orchestration layer that turns a short user command such as:

```text
tc スポット GOLD# エントリー前
```

into an explicitly traced, four-timeframe TC analysis request without changing the frozen TC Engine v1 specification.

TC5-0 fixes responsibility and boundaries only. It does **not** implement production code, production Native calls, order execution, position sizing, or automatic trading.

## 2. Frozen lower-layer dependency

TC Spot Runtime depends on the TC Engine v1 specification frozen at:

```text
91a146625e45c913efd9cebf63a3d25217c8bafe
```

TC5-0 does not modify:

- TC4-0 through TC4-9 historical artifacts;
- `TCTradePlanRaw v1.0.0`;
- Original Response First / Raw preservation;
- Question Contract and `NOT_PROVIDED` semantics;
- `INFERENCE=NO`;
- TCREG-01 through TCREG-20;
- TC4 Adapter responsibility;
- TC mapping/state semantics;
- NODA boundary;
- `one Native call = one timeframe`.

TC Spot Runtime is additive and sits outside these frozen responsibilities.

## 3. Runtime topology

The TC5 runtime topology is an upper-layer orchestration model, not a new TC Engine internal pipeline.

```text
User / ChatGPT
      |
      v
TC Spot Command Parser
      |
      v
TC Spot Runtime Controller
      |
      v
Broker Symbol Normalizer
      |
      v
Canonical Symbol Resolver
      |
      v
Provider Symbol Mapper
      |
      v
4TF Orchestrator
      |
      +---- D1  ----> Market Input / Native Client / TC Adapter+Engine ----+
      +---- H4  ----> Market Input / Native Client / TC Adapter+Engine ----+
      +---- H1  ----> Market Input / Native Client / TC Adapter+Engine ----+
      +---- M15 ----> Market Input / Native Client / TC Adapter+Engine ----+
      |                                                                    |
      +<---------------- per-timeframe results / failures -----------------+
      |
      v
Entry-Pre Runtime Evaluation
      |
      v
Response Formatter
      |
      v
User / ChatGPT
```

This placement is required to preserve the TC4-8 contract: the Adapter/TC Engine processes one timeframe at a time; an upper caller may issue four separate requests, but the Adapter may not synthesize a four-timeframe strategy decision.

## 4. TC Spot Command responsibility

The command layer identifies runtime intent only. Minimum accepted conceptual commands include:

```text
tc スポット GOLD エントリー前
tc スポット GOLD# エントリー前
tc スポット XAU/USD エントリー前

tc スポット USDJPY エントリー前
tc スポット USDJPY# エントリー前
```

The command parser may extract:

```text
engine_mode = TC
run_mode = SPOT
user_symbol = <symbol token>
evaluation_mode = ENTRY_PRE
```

The command parser must not:

- infer market direction;
- generate Entry/SL/TP;
- repair missing TC evidence;
- apply NODA rules;
- call external web analysis as a substitute for the defined market-input path.

## 5. Symbol-processing ownership

TC Spot Runtime owns three explicit pre-Native symbol stages:

```text
User Symbol
  -> Broker Suffix Normalization
  -> Canonical Symbol Resolution
  -> Provider Symbol Mapping
  -> exact Adapter analysis_symbol / Native symbol
```

The detailed policy is defined by `tc/runtime/SYMBOL_NORMALIZATION_POLICY.md`.

This upper-layer preprocessing does not alter TC4-8's rule that the Adapter itself performs no automatic `GOLD# -> XAUUSD` or broker/canonical symbol conversion. The Adapter receives an already resolved exact provider symbol.

## 6. Standard four-timeframe set

For TC Spot `ENTRY_PRE`, the standard timeframe set is fixed as:

```text
D1
H4
H1
M15
```

The 4TF Orchestrator creates four independent Adapter/Native requests.

```text
D1   -> one Native call
H4   -> one Native call
H1   -> one Native call
M15  -> one Native call
```

No simultaneous 4TF Native request is assumed.

## 7. 4TF Orchestrator responsibility

The upper 4TF Orchestrator owns only runtime coordination and provenance, including:

- creation of a batch/run identity;
- creation of four per-timeframe requests;
- stable timeframe/request association;
- technical execution order;
- request/record correlation;
- collection of each per-timeframe result or runtime failure;
- detection of missing timeframe outcomes;
- handoff to Entry-Pre Runtime Evaluation.

It must not:

- rewrite TradingCursor Native output;
- fabricate missing timeframe evidence;
- infer a missing TC answer from another timeframe;
- modify TCTradePlanRaw;
- inject NODA concepts;
- cause the Adapter to synthesize a combined 4TF Trade State.

The implementation details of `request_id`, `source_run_id`, `batch_request_id`, concurrency, scheduling, and retry remain for later TC5 work.

## 8. Market Input / TradingCursor boundary

TC5 runtime may coordinate the components that obtain the exact market/provider input needed by the TradingCursor Native interface, but TC5-0 does not implement those components.

The following remain later implementation work:

- production Market Input Provider;
- production TradingCursor Native Client;
- authentication/connection details;
- timeout values;
- rate-limit handling;
- persistence backend;
- operational logging.

A provider input must not be replaced by independently searched current prices, news, external technical analysis, or ChatGPT-generated market facts.

## 9. Entry-Pre Runtime Evaluation responsibility

`ENTRY_PRE` means:

> evaluate whether the collected TC outputs contain a usable pre-entry condition and present the TC evidence/state without granting execution permission.

The runtime may organize and present distinct TC concepts such as:

- Environment;
- Setup;
- Trigger;
- Direction;
- Entry;
- SL;
- TP;
- Wait;
- Invalidation;
- insufficient/unavailable information.

It must preserve all existing TC semantic guardrails, including:

```text
Entry presence != automatic ACTIONABLE
Trigger NOT_PROVIDED != WAIT
Invalidation Rule != Current INVALID
ACTIONABLE != Execution Permission
```

TC5-0 does not finalize a new Common TradePlanState or redefine TC4-5/TC4-6 semantics.

## 10. Response Formatter responsibility

The formatter may convert runtime results into a concise ChatGPT/user-facing response, but it must preserve provenance and failure distinctions.

It must not:

- add independent web-derived market analysis;
- silently fill absent TC fields;
- relabel infrastructure failure as a Trade State;
- convert ACTIONABLE into an order command.

## 11. NODA boundary

TC Spot Runtime is TC-only.

Forbidden within TC5 TC Spot processing:

```text
TC + NODA mixed judgment
NODA correction of TC output
NODA line/Formation injection
NODA completion of missing TC evidence
```

Any later TC-vs-NODA comparison must exist in a separate upper comparison layer and must keep each engine output independently traceable.

## 12. Failure boundary

Runtime/infrastructure failures remain separate from Trade State.

Examples include:

- command parse failure;
- symbol normalization failure;
- canonical symbol resolution failure;
- provider symbol mapping failure;
- market input failure;
- Native connection/transport failure;
- timeout;
- unsupported timeframe;
- Raw preservation failure;
- parser failure;
- Adapter failure;
- missing timeframe result.

Forbidden conversions include:

```text
TradingCursor timeout -> WAIT
SYMBOL_UNRESOLVED -> INVALID
Adapter failure -> UNDETERMINED Trade State
```

The runtime must expose a Runtime/Infrastructure Failure family separately from TC trading semantics.

TC5-0 does not freeze the final machine-readable runtime failure enum; naming/schema is deferred to later TC5 implementation work.

## 13. Retry boundary

TC4-8 Adapter-owned automatic retry remains `NONE`.

A later TC5 upper-layer retry policy may be designed, but every retry must remain an explicit new attempt with a new request identity and must never overwrite prior Raw evidence.

TC5-0 defines no retry count, backoff, or retry trigger.

## 14. Execution boundary

TC Spot Runtime responsibility ends at analysis/evaluation/presentation.

Out of scope:

- MT4/MT5 order submission;
- automatic trade execution;
- lot sizing;
- position sizing;
- risk amount calculation;
- account balance/margin management;
- modification/closure of open positions;
- SL/TP order modification.

Any future execution capability must be a separately authorized Execution Layer.

## 15. External-information boundary

During TC Spot processing, ChatGPT or any runtime component must not independently obtain and inject:

- current price from unrelated web search;
- market news;
- external forecasts;
- third-party technical analysis;
- independent XAU/USD or USDJPY analysis.

TC Spot evidence is restricted to the formally defined TC5 input path and frozen TC Engine behavior. If external information is requested, it is a different mode and must be identified separately.

## 16. Fixed vs deferred by TC5-0

### FIXED by TC5-0

- TC Spot is an upper Runtime/Orchestration layer outside frozen TC Engine v1.
- standard `ENTRY_PRE` timeframe set is D1/H4/H1/M15;
- one Native call per timeframe remains mandatory;
- symbol preprocessing occurs before the Adapter and is explicit/traceable;
- the 4TF Orchestrator is outside the Adapter/TC Engine;
- TC and NODA remain separated;
- Runtime Failure is not Trade WAIT/INVALID/other Trade State;
- ENTRY_PRE does not grant execution permission;
- external web analysis is not TC Spot market input.

### DEFERRED

- production implementation language/framework;
- command-parser implementation details;
- provider configuration storage;
- exact request/run ID format;
- persistence/logging backend;
- orchestration concurrency/order policy;
- upper-layer retry policy;
- runtime failure schema;
- exact Entry-Pre user response schema;
- production Native Client/Adapter/Mapper/State Evaluator implementation.

## 17. Completion criterion

TC5-0 responsibility work is complete when the following command can be explained unambiguously without invoking implementation details:

```text
tc スポット GOLD# エントリー前
```

Specifically, responsibility must be identifiable for command parsing, `#` handling, canonical symbol resolution, provider mapping, four independent timeframe requests, TC Engine entry, collection/evaluation, failure stopping, formatting, and execution separation.
