# TC5-5 — ENTRY_PRE Evaluation Gate

Status: **BOUNDARY FIXED / COMBINED 4TF TRADE SEMANTICS TBD**

ENTRY_PRE evaluation may begin only from a complete, traceable D1/H4/H1/M15 batch. Runtime or infrastructure failure is not a Trade State.

Per-timeframe WAIT/ACTIONABLE/INVALID/UNDETERMINED must preserve TC4-6 semantics: explicit current Native evidence only; Entry presence does not imply ACTIONABLE; missing Trigger does not imply WAIT; future invalidation does not imply current INVALID; ACTIONABLE is not execution permission.

TC4 intentionally forbids Adapter/TC-side 4TF strategy synthesis. TC5 has not yet approved a separate upper-layer rule that converts four independent timeframe results into one combined LONG/SHORT/WAIT or execution decision. Therefore the runtime may report per-timeframe TC evidence and batch completeness, but must not invent a combined trade state.

A future combined 4TF policy must be separately specified, audited against TC4 guardrails, and labeled as TC5 upper-runtime semantics rather than TradingCursor Native fact.
