# TC4-2P Observation Method

Status: **PASS WITH LIMITATION**

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `c66a679a4a852f961fc438a11b1523f794bf55b7`

## 1. Purpose

TC4-2P fixes how TradingCursor can actually be observed before resuming TC4-2. It does not evaluate trade quality and does not change TC4-0 responsibility or TC4-1 input rules.

## 2. TradingCursor callable input capability

The currently exposed TradingCursor analysis interface accepts exactly these request dimensions:

- `exchange`
- `symbol`
- `interval`

The exposed interval contract includes single-timeframe requests such as `15m`, `1h`, `4h`, and `1D`.

Pilot execution confirmed `OANDA / XAUUSD` succeeds individually for:

- D1 -> `1D`
- H4 -> `4h`
- H1 -> `1h`
- M15 -> `15m`

The current callable interface does not expose request parameters for:

- arbitrary uploaded chart images;
- a fixed `artifact_ref`;
- four timeframe artifacts in one request;
- a free-form analysis prompt;
- a frozen historical snapshot identifier supplied by the caller.

These statements describe the currently exposed callable interface only; they do not claim that no other TradingCursor UI/product path can ever support them.

## 3. TradingCursor output capability

Pilot execution confirmed the response can contain:

- completion status;
- exchange;
- symbol;
- interval;
- an `analysis` field containing the native JSON text;
- model identifier;
- analysis completion timestamp.

The returned native JSON also contained an `action_url` with a TradingCursor `chartId` value in all four pilot calls.

The pilot therefore proves Raw Response capture and run-time provenance are technically possible for the callable path.

## 4. Arbitrary image / fixed artifact input

### Current callable path

`NOT_SUPPORTED`

No image, file, artifact reference, or binary-input parameter is exposed.

Therefore a TC4-1 artifact cannot currently be proven to be directly consumed by TC② through this path.

## 5. Free prompt input

### Current callable path

`NOT_SUPPORTED`

No prompt parameter is exposed.

Therefore:

- Phase A can be represented by the connector's native/default analysis;
- Phase B cannot be implemented as a distinct Minimal Trade Plan Request through the currently exposed call.

Phase B must remain `NOT_SUPPORTED / HOLD` unless another verified TradingCursor path is introduced.

## 6. Four-timeframe input

### Simultaneous 4TF input

`NOT_SUPPORTED`

### Individual 4TF requests

`SUPPORTED`

D1/H4/H1/M15 can be requested separately. Their Raw Responses must remain separate. TC4-2P does not authorize ChatGPT to synthesize those four responses into a new "TradingCursor multi-timeframe decision".

## 7. Raw response capture

`SUPPORTED`

For every native call, preserve at minimum:

- corresponding observation/pilot identifier;
- execution order;
- exchange/source;
- symbol;
- interval;
- full unmodified `analysis` string;
- model;
- TradingCursor timestamp;
- action URL / chartId if returned.

Classification may only be created after Raw preservation.

## 8. Same-input replay capability

`PARTIAL`

The same request signature (`exchange`, `symbol`, `interval`) can be issued again, but the exposed call does not provide a caller-controlled frozen market snapshot or artifact identifier.

Therefore repeated calls cannot currently be certified as consuming the exact same Market Input.

Exact replay is not proven.

## 9. Comparison modes

### Mode A — STRICT_SAME_ARTIFACT

Definition: NODA② and TC② consume the exact same fixed D1/H4/H1/M15 artifacts.

Current callable TradingCursor path: **UNAVAILABLE**.

Reason: caller-supplied artifact input is not exposed.

### Mode B — SAME_MARKET_OBSERVATION

Definition: NODA② and TC② observe the same source, symbol, observation state, and timeframe set even if they do not consume identical files.

Current callable TradingCursor path: **NOT YET PROVEN**.

The pilot used the same source/symbol and sequential D1/H4/H1/M15 calls, but each call had its own completion timestamp and no frozen cross-timeframe snapshot identifier. TC4-2P does not label that sequence as a certified same-observation set.

## 10. Broker symbol / canonical symbol / analysis symbol

The following identities must remain distinct:

- `broker_symbol`: symbol used by the execution broker, e.g. XM `GOLD#`;
- `canonical_symbol`: strategy-neutral conceptual asset identity, e.g. gold/XAUUSD when mapping is validated;
- `analysis_symbol`: exact symbol requested from TradingCursor, pilot-confirmed as `XAUUSD`;
- `analysis_source`: exact source/exchange used by TradingCursor, pilot-confirmed as `OANDA`.

No rule may claim `XM GOLD# == OANDA XAUUSD` as strict identity.

If source/symbol differ, that difference must remain explicit in experiment metadata.

## 11. Observation timestamp

For the callable TradingCursor path, preserve the TradingCursor completion timestamp for every timeframe request.

A separate common `observation_timestamp` may only be assigned when the capture/observation procedure can justify that the related artifacts and TC requests belong to one defined observation state.

No arbitrary maximum-seconds threshold is introduced in TC4-2P.

## 12. Reproducibility levels

### LEVEL A — Exact artifact replay possible

Use for `STRICT_SAME_ARTIFACT` comparison.

Current status: **NOT AVAILABLE**.

### LEVEL B — Same market observation reproducible

Use for conditional NODA② / TC② comparison where source/symbol/observation state is demonstrably shared.

Current status: **NOT YET PROVEN**.

### LEVEL C — Live market request only

Use only for TradingCursor Raw behavior/schema observation, not strict engine-comparison claims.

Current status: **AVAILABLE AND PILOT-CONFIRMED**.

## 13. Phase A

Adopt, for the current callable path:

`Phase A = TradingCursor Native Default Analysis`

Formal procedure:

1. choose verified `analysis_source`, `analysis_symbol`, and one interval;
2. invoke the native TradingCursor analysis call without NODA information;
3. preserve the entire Raw Response before classification;
4. repeat separately for D1/H4/H1/M15 if 4TF coverage is required;
5. do not merge the four Raw Responses into a fabricated TC-native MTF decision.

This procedure is LEVEL C unless a frozen observation mechanism is later verified.

## 14. Phase B

`NOT_SUPPORTED / HOLD` through the current callable path.

Reason: no free prompt or trade-plan-request parameter exists in the exposed interface.

A future Phase B requires a separately verified path that can accept a Minimal Trade Plan Request while preserving comparable market input.

## 15. Pilot procedure and result

A Technical Feasibility Check was performed against:

- source/exchange: `OANDA`
- analysis symbol: `XAUUSD`
- timeframes: `1D`, `4h`, `1h`, `15m`

All four requests completed successfully.

The pilot is stored separately under `fixtures/tc4_2_pilot/` and is **not** a formal TC4-2 input set.

Because the requests were live and sequential, it is classified as **LEVEL C**.

## 16. TC4-1 consistency

TC4-1 is not modified by TC4-2P.

However, operational evidence shows that TC4-1's exact same-artifact concept cannot currently be satisfied by the exposed TradingCursor callable path.

A future clarification work should distinguish:

- strict artifact equality;
- same-market-observation equivalence;
- live native survey.

This is a proposed clarification only, not a TC4-1 modification.

## 17. Formal TC4-2 restart condition

Under the original TC4-2 Hard Gate, formal restart remains **HOLD** until at least one of these paths is verified:

A. TradingCursor can consume the exact fixed TC4-1 artifacts; or

B. a reproducible SAME_MARKET_OBSERVATION mechanism exists that can bind the exact observation state to both TC and NODA inputs and preserve Raw Responses.

LEVEL C may be used immediately for a separate Raw-output capability survey, but must not be presented as satisfying the original fixed-Market-Input comparison gate.

## 18. Prohibited shortcuts

Do not:

- equate XM `GOLD#` with OANDA `XAUUSD` as strict input identity;
- infer a frozen snapshot from sequential live requests;
- fabricate Phase B from the default analysis;
- synthesize four single-TF responses into a TradingCursor-native MTF response;
- alter TC4-0 responsibility;
- add NODA logic, sizing, execution, Adapter, or Normalizer behavior.
