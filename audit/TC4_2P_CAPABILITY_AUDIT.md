# TC4-2P Capability Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Start HEAD: `c66a679a4a852f961fc438a11b1523f794bf55b7`

## Capability classification

| Capability | Result | Evidence |
|---|---|---|
| exchange input | SUPPORTED | Current callable interface exposes `exchange`; pilot `OANDA` completed. |
| symbol input | SUPPORTED | Current callable interface exposes `symbol`; pilot `XAUUSD` completed. |
| single timeframe input | SUPPORTED | Interface exposes one `interval` per call. |
| D1 | SUPPORTED | Pilot `1D` completed. |
| H4 | SUPPORTED | Pilot `4h` completed. |
| H1 | SUPPORTED | Pilot `1h` completed. |
| M15 | SUPPORTED | Pilot `15m` completed. |
| arbitrary image input | NOT_SUPPORTED | No image/file parameter in current callable interface. |
| fixed artifact input | NOT_SUPPORTED | No `artifact_ref` or frozen artifact parameter. |
| simultaneous 4TF input | NOT_SUPPORTED | Exactly one interval is passed per call. |
| free prompt input | NOT_SUPPORTED | No prompt parameter in current callable interface. |
| Raw Response capture | SUPPORTED | Full native analysis returned as JSON text in `analysis`. |
| model metadata | SUPPORTED | Pilot returned model identifier. |
| analysis timestamp | SUPPORTED | Pilot returned top-level completion timestamp. |
| chart identifier | SUPPORTED WITH LOCATION NOTE | Pilot Raw contained `action_url` with `chartId`; no separate caller-controlled snapshot id was available. |
| exact same-input replay | NOT PROVEN | Request can be repeated, but market state cannot be frozen/replayed through exposed parameters. |
| same request signature rerun | SUPPORTED | Same exchange/symbol/interval signature can be issued again. |

## Pilot execution evidence

Technical Feasibility Check only; not formal TC4-2 observation data.

### Call 1

- exchange: OANDA
- symbol: XAUUSD
- interval: 1D
- status: completed
- model: `qwen.qwen3-vl-235b-a22b`
- timestamp: `2026-09-10T09:42:35.375Z`
- chartId: `8c8412bd-61cf-4c7d-b807-1ea33436ae94`

### Call 2

- exchange: OANDA
- symbol: XAUUSD
- interval: 4h
- status: completed
- model: `qwen.qwen3-vl-235b-a22b`
- timestamp: `2026-09-10T09:43:02.538Z`
- chartId: `fb1174f0-4b25-46eb-9725-1969cf54a014`

### Call 3

- exchange: OANDA
- symbol: XAUUSD
- interval: 1h
- status: completed
- model: `qwen.qwen3-vl-235b-a22b`
- timestamp: `2026-09-10T09:43:29.817Z`
- chartId: `7a182ea3-7fcd-4650-9579-c0ef0a57f785`

### Call 4

- exchange: OANDA
- symbol: XAUUSD
- interval: 15m
- status: completed
- model: `qwen.qwen3-vl-235b-a22b`
- timestamp: `2026-09-10T09:43:54.302Z`
- chartId: `f1f38098-4ddf-4733-943a-66e6c615957f`

The sequential pilot spans multiple completion timestamps. No unsupported claim is made that all four calls consumed one frozen observation state.

## Phase feasibility

### Phase A — TradingCursor Native Default Analysis

SUPPORTED at LEVEL C.

### Phase B — Minimal Trade Plan Request

NOT_SUPPORTED through current callable interface because no free-prompt parameter is exposed.

## Comparison-mode audit

### STRICT_SAME_ARTIFACT

Current status: **UNAVAILABLE**.

Reason: fixed caller-supplied artifacts cannot be passed through the exposed TradingCursor request.

### SAME_MARKET_OBSERVATION

Current status: **NOT YET PROVEN**.

Using the same exchange/symbol with sequential calls does not prove a frozen shared observation state.

## Reproducibility audit

- LEVEL A: unavailable
- LEVEL B: not yet proven
- LEVEL C: available and pilot-confirmed

## TC4-1 impact

No TC4-1 file is changed in TC4-2P.

Audit conclusion: a later clarification is advisable to distinguish strict artifact equality, same-market-observation equivalence, and live-native survey. That recommendation does not change the existing TC4-1 contract.

## Scope audit

- TC4-0 responsibility changed: NO
- TC decision logic added: NO
- NODA logic added: NO
- Position Sizing added: NO
- Adapter added: NO
- Normalizer added: NO
- `trade-plan-a` changed: NO
- main merged: NO

## Hard Gate result

TC4-2P itself: **PASS WITH LIMITATION**.

Original TC4-2 fixed-input Hard Gate: **NOT YET UNBLOCKED**.
