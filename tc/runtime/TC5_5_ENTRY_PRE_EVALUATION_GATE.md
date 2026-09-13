# TC5-5 — ENTRY_PRE Evaluation Gate

Status: **REVISED / PROFILE ROLE GATE FIXED**

ENTRY_PRE is evaluated by profile role, not by four-timeframe voting.

## NORMAL

```text
Environment = D1
Setup       = H4
Decision    = H1
```

H1 owns the candidate direction and Entry/SL/TP/Wait/Invalidation decision evidence. D1/H4 do not outvote H1 and their Entry/SL/TP values are not merged into the final plan.

If H1 explicitly states that lower-timeframe confirmation is required, the runtime enters `NEEDS_DRILLDOWN` and requests M15. M15 is confirmation evidence only; it does not replace the H1 candidate plan.

The lower-timeframe requirement must be explicit Native evidence. Generic WAIT, missing Trigger, setup ambiguity, or runtime uncertainty does not automatically request M15.

For an eligible NORMAL drilldown:

- M15 `ACTIONABLE` in the same candidate direction may release the gate to common `TRADE`;
- M15 explicit `WAIT` produces common `WAIT`;
- opposite direction, `INVALID`, `UNDETERMINED`, or insufficient M15 evidence produces Runtime `HOLD` / user-facing 判定保留, not a fabricated Trade State.

M15 confirmation cannot release unrelated H1 WAIT reasons. Drilldown release is allowed only when the H1 wait/confirmation evidence is explicitly tied to lower-timeframe confirmation.

## SHORT

```text
Environment = H4
Setup       = H1
Decision    = M15
```

M15 is the decision timeframe. Its TC4-6 state maps at the TC5 common-output boundary as:

```text
ACTIONABLE   -> TRADE
WAIT         -> WAIT
INVALID      -> INVALID
UNDETERMINED -> Runtime HOLD / 判定保留
```

The same mapping applies to NORMAL H1 when no drilldown is explicitly required.

## Guardrails

Per-timeframe TC4-6 semantics remain unchanged: Entry presence does not imply ACTIONABLE; missing Trigger does not imply WAIT; future invalidation does not imply current INVALID; ACTIONABLE is not execution permission.

Runtime/infrastructure failure is never WAIT/INVALID. NODA and external web analysis are not used to release the gate.
