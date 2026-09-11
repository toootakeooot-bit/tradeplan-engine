# TC-P1 Native Client Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-prod-v1`  
Start HEAD: `212dbdd20ed2877e9b7b3e43b36e6f92c404f532`  
Base specification completion HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## Result

**PASS WITH NOTES**

**TC-P2 readiness: GO**

TC-P1 implements only the production Native Client boundary defined by TC-P0. It does not implement Adapter, Raw Storage, Mapper, State Evaluator, A integration, execution, or any NODA logic.

## 1. Implemented scope

Production code added:

- `tc/native/client.py`
- `tc/native/__init__.py`

Tests added:

- `tests/tc_prod/test_native_client.py`

The client implements:

```text
NativeRequest
  -> exact field translation
  -> injected ProviderExecutor(exchange, symbol, interval)
  -> NativeCallResult
```

The Native provider-facing surface is limited to the frozen TC v1 contract:

```text
exchange
symbol
interval
```

No URL, credentials, authentication scheme, SDK, image input, prompt input, snapshot input, or multi-timeframe provider contract is invented.

## 2. Request / identity model

`NativeRequest` carries:

```text
request_id
source_run_id
execution_order
analysis_source
analysis_symbol
timeframe
```

Structural identity validation requires non-empty string identifiers and `execution_order >= 1`.

The Native Client does not generate, deduplicate, or persist request identities. An explicit retry remains the caller's responsibility and must be represented as a new request / execution identity under the frozen contract.

## 3. Timeframe translation

Exact frozen mapping implemented:

```text
D1  -> 1D
H4  -> 4h
H1  -> 1h
M15 -> 15m
```

Unsupported timeframe fails before any provider call. No nearest-timeframe substitution exists.

## 4. Symbol/source handling

Mapping is exact:

```text
analysis_source -> exchange
analysis_symbol -> symbol
```

There is no canonical/broker symbol inference and no conversion such as `GOLD# -> XAUUSD`.

## 5. Provider executor boundary

`NativeClient` requires one injected callable implementing the exact provider request surface.

The client invokes it exactly once per `execute()` call.

Automatic retry:

```text
NONE
```

A provider exception is wrapped once as `NativeTransportError` with `request_id` provenance. It is not converted to any Trade State.

## 6. Response handling

The executor must return a mapping-like Native response.

- the response is not normalized;
- no strategy field is interpreted;
- unknown provider fields are retained;
- the returned Mapping object is passed through as `original_response` without selective reconstruction;
- a non-mapping response produces explicit `NativeResponseContractError`.

Original Raw preservation to durable storage is intentionally not implemented in P1. The Native Client only hands the untouched response to the next boundary; P2/P3 own wrapper/preservation integration according to TC-P0.

## 7. Test execution

Command used on an exact local mirror of the added P1 files:

```text
python -m unittest -v tests.tc_prod.test_native_client
```

Result:

```text
Ran 9 tests
OK
PASS 9
FAIL 0
```

Covered cases:

1. exact source/symbol/interval translation;
2. all four frozen timeframe mappings;
3. unsupported timeframe fails before provider invocation;
4. symbol is not auto-converted;
5. provider failure becomes transport failure with exactly one call / no retry;
6. repeated explicit requests remain distinct request identities;
7. unknown response fields pass through untouched;
8. non-mapping response is explicit provider-contract failure;
9. invalid request identity is rejected.

This is a local deterministic unit test, not a live TradingCursor connectivity test and not GitHub Actions evidence.

## 8. Frozen-invariant audit

| Gate | Result |
|---|---|
| correct repository / production branch | PASS |
| started from TC-P0 HEAD | PASS |
| frozen `feature/tc-v1` changed | NO |
| direct undocumented provider endpoint invented | NO |
| request surface limited to exchange/symbol/interval | PASS |
| timeframe mapping exact | PASS |
| unsupported timeframe substituted | NO |
| symbol auto-converted | NO |
| provider automatic retry | NONE |
| one `execute` call can call provider more than once | NO |
| provider error converted to Trade State | NO |
| unknown provider fields dropped | NO |
| strategy interpretation added | NO |
| Adapter implemented | NO |
| Raw Storage implemented | NO |
| Mapper implemented | NO |
| State Evaluator implemented | NO |
| 4TF synthesis added | NO |
| Position Sizing / Risk / Lot / Execution added | NO |
| NODA logic added | NO |
| TCTradePlanRaw schema changed | NO |
| TC4-7 expected results changed | NO |
| Trade Plan A changed | NO |
| A connected to TC | NO |
| main merged | NO |
| unit tests | 9 PASS / 0 FAIL |

## 9. TCREG / schema / Common impact

TCREG impact: **NONE EXPECTED / semantic baseline unchanged**. P1 ends before Mapping and State Semantics, so TCREG-01..20 expectations are untouched and are not rewritten.

TCTradePlanRaw schema impact: **NONE**.

Common/NODA impact: **NONE**.

Trade Plan A impact: **NONE**.

## 10. Notes

### N-01 — real provider host binding remains deferred

TC-P1 deliberately does not prove live TradingCursor connectivity because the frozen specification contains no approved direct network endpoint/credential/SDK contract. The production Native Client is host-bindable through injected `ProviderExecutor`; the concrete host binding is deferred to the later integration environment or separately evidenced provider runtime contract.

### N-02 — request identity uniqueness is caller-owned

The client validates request identity shape but does not maintain a global registry of previously used IDs. This avoids hidden state/deduplication inside the transport boundary. Later orchestration must create a new request identity for an explicit retry as required by TC v1.

These notes do not block P2.

## 11. Verdict

**TC-P1 = PASS WITH NOTES**

**TC-P2 = GO, but NOT STARTED.**

STOP here under the P0 work-package discipline.
