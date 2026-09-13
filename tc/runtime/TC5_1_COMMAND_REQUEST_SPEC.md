# TC5-1 — Spot Command / Runtime Request Specification

Status: **FIXED for TC5 Spot v1**

Accepted command: `tc スポット <symbol> エントリー前`.

Parser output is intent only: TC / SPOT / original user symbol / ENTRY_PRE / D1,H4,H1,M15. It must not perform market analysis, symbol aliasing, provider mapping, NODA logic, or external web lookup. Command failures are Runtime Failures, never Trade States.
