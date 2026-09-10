# TC4-2P Pilot Manifest

Pilot type: Technical Feasibility Check only  
Formal TC4-2 input set: **NO**  
Reproducibility level: **LEVEL C — live market request only**

## Identity

- pilot_id: `TC4-2P-OANDA-XAUUSD-20260910-01`
- analysis_source: `OANDA`
- analysis_symbol: `XAUUSD`
- broker_symbol: not assigned
- canonical_symbol: not formally fixed by this pilot
- comparison_mode: none certified
- artifact_consumed_by_tc: `NO`

## Calls

| order | intended TF | TradingCursor interval | completion timestamp | chartId |
|---:|---|---|---|---|
| 1 | D1 | 1D | 2026-09-10T09:42:35.375Z | 8c8412bd-61cf-4c7d-b807-1ea33436ae94 |
| 2 | H4 | 4h | 2026-09-10T09:43:02.538Z | fb1174f0-4b25-46eb-9725-1969cf54a014 |
| 3 | H1 | 1h | 2026-09-10T09:43:29.817Z | 7a182ea3-7fcd-4650-9579-c0ef0a57f785 |
| 4 | M15 | 15m | 2026-09-10T09:43:54.302Z | f1f38098-4ddf-4733-943a-66e6c615957f |

## Important limitation

These calls were sequential live analyses. They are not certified as one frozen `observation_timestamp` and are not a TC4-1-compliant fixed four-artifact `input_set_id`.

The pilot proves interface feasibility only:

- single-TF analysis works;
- all four required TF labels can be requested separately;
- raw JSON is returned;
- timestamps/model/action URL are traceable.

It does not prove STRICT_SAME_ARTIFACT or SAME_MARKET_OBSERVATION comparability.

## Raw files

- `raw_1D.json`
- `raw_4h.json`
- `raw_1h.json`
- `raw_15m.json`

The Raw files are preserved for interface evidence only and must not be used as formal TC4-2 comparison fixtures.
