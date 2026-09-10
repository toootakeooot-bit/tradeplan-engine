# TC4-2 Formal Run Manifest

survey_run_id: `TC4-2-OANDA-XAUUSD-20260910-01`

survey_mode: `TC_NATIVE_RAW_SURVEY`

comparison_level: `LEVEL_C`

restart_start_head: `be4835cabfa5d505d3c12d79c58c616f879ec0ac`

## Target

- exchange/source: `OANDA`
- analysis_symbol: `XAUUSD`
- common canonical/broker identity: not asserted by this LEVEL C run
- this run is not an XM `GOLD#` same-input claim

## Execution order

| Order | Role | Interval | Status | Timestamp UTC | chartId | Raw file |
|---:|---|---|---|---|---|---|
| 1 | D1 formal | 1D | completed | 2026-09-10T10:13:39.412Z | b03658c0-d0f8-431b-b819-87f841d54e7f | `raw_1D.json` |
| 2 | H4 formal | 4h | completed | 2026-09-10T10:14:05.800Z | 914e5b19-6c30-4e33-93bd-ff0a4fc1df57 | `raw_4h.json` |
| 3 | H1 formal | 1h | completed | 2026-09-10T10:14:36.173Z | db4c53c3-20c1-43e6-a2e8-d1f823a5f64a | `raw_1h.json` |
| 4 | M15 formal | 15m | completed | 2026-09-10T10:15:01.090Z | 37a6052b-8def-4837-8793-8006966c03af | `raw_15m.json` |
| 5 | H1 live repeat | 1h | completed | 2026-09-10T10:15:30.706Z | a53a8f2f-940b-4c51-826f-b1810303e45f | `raw_1h_repeat_01.json` |

Model returned on every call: `qwen.qwen3-vl-235b-a22b`.

## Acquisition boundary

- each TF is an independent TradingCursor Native call;
- no fixed artifact was directly supplied;
- no free prompt was supplied;
- no 4TF Native integration was available or claimed;
- Phase A = Native Default Analysis;
- Phase B = NOT_SUPPORTED;
- Raw response is retained separately from the Question Contract mapping.

## Repeatability note

Order 5 is a live repeat of the same request identity (`OANDA`, `XAUUSD`, `1h`). It is not exact-input replay. Any difference can reflect live market-data movement, model variation, or both; causation is not inferred.
