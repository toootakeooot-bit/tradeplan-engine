# TC-P3 Raw Storage Audit

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-prod-v1`  
Start HEAD: `46ace92db06ca1157139dc93ba46e9e3652d2ccc`  
Base specification completion HEAD: `023c8247a1a09900a7f8dccbc8434858ab2697db`  
TC Engine v1 Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## Result

**PASS WITH NOTES**

**TC-P4 readiness: GO**

TC-P3 implements only the durable filesystem Raw Storage required by TC-P0/P2. It does not implement Mapping, State evaluation, A integration, execution, or NODA logic.

## 1. Implemented scope

Production code added:

- `tc/storage/raw_store.py`
- `tc/storage/__init__.py`

Tests added:

- `tests/tc_prod/test_raw_storage.py`

Storage implements the TC-P2 `RawPreserver` contract:

```text
preserve(request, original_response)
  -> durable no-overwrite artifact
  -> stable source_raw_artifact
```

The TC-P2 Adapter can now use the concrete storage directly.

## 2. Logical artifact convention

TC-P3 fixes the logical reference convention as:

```text
tcraw://v1/<source_run_id>/<execution_order>.json
```

Execution order is rendered with a minimum width of two digits, e.g.:

```text
tcraw://v1/RUN-001/03.json
```

The logical reference is intentionally independent of the machine-specific absolute storage root. The configured root resolves it to:

```text
<root>/v1/<source_run_id>/<execution_order>.json
```

This does not require any TCTradePlanRaw schema change because `source_raw_artifact` remains a non-empty string.

## 3. Original Raw preservation

Storage serializes the complete Native response as UTF-8 JSON without a known-field whitelist.

Before publication it verifies:

- JSON serialization is lossless at the semantic JSON-value level;
- NaN/non-JSON values are rejected;
- the original `analysis` string round-trips exactly as a Python string value;
- unknown outer/inner Native content is retained.

TC-P3 does not claim HTTP wire-byte preservation that was never available in the TC v1 source evidence.

## 4. Atomic/no-overwrite publication

Publication uses a fully written same-directory temporary file.

Common steps:

```text
serialize
-> write same-directory temp
-> flush + fsync file
-> verify temp read-back
-> atomically publish final name without overwrite
-> fsync directory where supported
-> verify final read-back
```

Platform strategy:

- POSIX: `os.link(temp, final)` provides atomic final-name creation and fails if final exists;
- Windows: same-directory `os.rename(temp, final)` is used; the destination is not intentionally replaced.

The implementation never calls `os.replace()` and never deliberately overwrites an existing logical Raw artifact.

## 5. Duplicate/repeat behavior

Same `source_run_id + execution_order`:

```text
existing artifact
-> DuplicateRawArtifactError
-> prior artifact preserved unchanged
```

A repeat request must use a new execution identity as fixed in TC v1/P1. Distinct execution orders produce distinct durable artifacts.

## 6. Path/reference safety

Filesystem-facing `source_run_id` is restricted to:

```text
[A-Za-z0-9][A-Za-z0-9._-]{0,127}
```

This rejects slash/backslash/traversal-style identifiers before path construction.

Read references must match the fixed `tcraw://v1/.../<digits>.json` form. Wrong scheme, authority, path shape, query/fragment, or filename is rejected.

Resolved artifact parents are checked to remain under the configured root.

## 7. Read-back verification

Both temporary and published files are decoded as UTF-8 JSON and compared to the requested semantic Native snapshot. `analysis` is checked explicitly for exact string equality.

`FileRawStorage.read()` provides deterministic retrieval by logical `source_raw_artifact` for later integration/testing.

## 8. Failure semantics

Storage-specific failures remain infrastructure outcomes:

- `InvalidRawStorageInputError`
- `DuplicateRawArtifactError`
- `RawStoragePublicationError`
- `RawStorageVerificationError`

When called through TC-P2, any preservation exception remains Adapter stage `RAW_PRESERVATION`; it does not produce WAIT, ACTIONABLE, INVALID, or UNDETERMINED.

## 9. Adapter integration

P3 includes an integration test:

```text
NativeClient
-> TCAdapter
-> FileRawStorage
-> source_raw_artifact
-> TCTradePlanRaw v1.0.0
```

The test verifies the durable file equals the Native payload, the original `analysis` string remains exact, and the Adapter emits the storage logical reference in `record_identity.source_raw_artifact`.

No Mapper or State Evaluator is involved.

## 10. Test execution

Command used on an exact local mirror of the P1/P2 production files plus the P3 files:

```text
python -m unittest -v \
  tests.tc_prod.test_native_client \
  tests.tc_prod.test_adapter \
  tests.tc_prod.test_raw_storage
```

Result:

```text
P1 Native Client:  9 PASS / 0 FAIL
P2 Adapter:       12 PASS / 0 FAIL
P3 Raw Storage:   10 PASS / 0 FAIL
Total:            31 PASS / 0 FAIL
```

This is local deterministic test evidence. It is not GitHub Actions, live TradingCursor connectivity, or Trade Plan A integration evidence.

## 11. Frozen-invariant audit

| Gate | Result |
|---|---|
| correct repository / production branch | PASS |
| started from TC-P2 HEAD | PASS |
| frozen `feature/tc-v1` changed | NO |
| TCTradePlanRaw schema changed | NO |
| configurable storage root | PASS |
| stable logical source_raw_artifact | PASS |
| Original Raw preserved without field whitelist | PASS |
| exact analysis string semantic round trip | PASS |
| unknown Native fields preserved | PASS |
| atomic/no-overwrite publication | PASS |
| duplicate artifact overwrites prior Raw | NO |
| repeat execution identities stored independently | PASS |
| read-back verification | PASS |
| path traversal protection | PASS |
| invalid references rejected | PASS |
| storage failure converted to Trade State | NO |
| Mapper implemented | NO |
| State Evaluator implemented | NO |
| 4TF synthesis added | NO |
| Position Sizing / Risk / Lot / Execution added | NO |
| NODA logic added | NO |
| TC4-7 expected results changed | NO |
| Trade Plan A changed | NO |
| A connected to TC | NO |
| main merged | NO |
| P1 regression tests | 9 PASS / 0 FAIL |
| P2 regression tests | 12 PASS / 0 FAIL |
| P3 tests | 10 PASS / 0 FAIL |

## 12. TCREG / schema / Common impact

TCREG impact: **NONE EXPECTED / semantic baseline unchanged**. P3 is evidence-preservation infrastructure and does not perform Mapping or State Semantics.

TCTradePlanRaw schema impact: **NONE**.

Common/NODA impact: **NONE**.

Trade Plan A impact: **NONE**.

## 13. Notes

### N-01 — Windows publication path not executed in current test host

The current local test host is POSIX, so the POSIX hard-link publication branch was executed. The Windows same-directory `os.rename()` branch is implemented but not executed in this environment. A Windows-host integration test remains appropriate before Trade Plan TC production deployment.

### N-02 — source_run_id filesystem-safe restriction

P3 intentionally narrows durable-storage identifiers to a filesystem-safe subset. Current formal run IDs satisfy it. Future orchestration must generate compatible run IDs or explicitly revise the storage identity contract; P3 does not silently escape unsafe identifiers.

### N-03 — logical reference requires configured storage root

`tcraw://v1/...` is a logical engine reference, not a globally dereferenceable network URI. The runtime must provide the same storage root/configuration to resolve it. This is intentional and avoids machine-specific absolute paths inside TCTradePlanRaw.

These notes do not block P4.

## 14. Verdict

**TC-P3 = PASS WITH NOTES**

**TC-P4 = GO, but NOT STARTED.**

STOP here under the P0 work-package discipline.
