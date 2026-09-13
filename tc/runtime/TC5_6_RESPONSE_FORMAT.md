# TC5-6 — TC Spot Response Format

Status: **DESIGN FIXED FOR SAFE PARTIAL/COMPLETE REPORTING**

The user-facing response must first distinguish Runtime status from Trade State.

Minimum fields:
- requested user symbol;
- canonical symbol;
- provider source/symbol;
- batch status: COMPLETE or INCOMPLETE;
- D1/H4/H1/M15 per-timeframe status;
- per-timeframe TC direction/state/Entry/SL/TP/Wait/Invalidation only when actually observed/mapped;
- runtime failure code and failed timeframe when applicable;
- combined 4TF trade state: `NOT_DEFINED` until a separate TC5 aggregation policy is approved;
- execution permission: always `NO` in TC Spot.

If any mandatory timeframe is missing, the response must say the batch is incomplete and must not silently provide a 3TF combined decision. External web prices/news/analysis must not be inserted into the TC section.
