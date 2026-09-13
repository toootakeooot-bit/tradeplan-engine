# TC5-1 — Spot Command / Runtime Request Specification

Status: **REVISED / PROFILE-BASED TC SPOT V2**

Accepted commands:

```text
tc スポット <symbol> エントリー前
tc スポット <symbol> 通常 エントリー前
tc スポット <symbol> 短期 エントリー前
```

The four-token form is the backward-compatible default for `NORMAL`.

## Profile mapping

```text
NORMAL
  Environment = D1
  Setup       = H4
  Decision    = H1
  Optional confirmation = M15 only when H1 explicitly requires lower-timeframe confirmation

SHORT
  Environment = H4
  Setup       = H1
  Decision    = M15
```

Initial Native requests are therefore:

```text
NORMAL -> D1, H4, H1
SHORT  -> H4, H1, M15
```

`M15` is not a mandatory initial request for NORMAL.

The parser outputs intent/profile/role metadata only. It must not perform market analysis, symbol aliasing, provider mapping, NODA logic, external web lookup, or infer that M15 is needed.

Command failures are Runtime Failures, never Trade States.
