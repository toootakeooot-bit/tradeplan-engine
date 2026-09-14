# TC5 US100 Alias Completion Audit

Date: 2026-09-14
Branch: `feature/tc-v1`
Scope: TC5 Runtime only. TC4 frozen adapter/specification is unchanged.

## Finding

The operational design used `US100` as the canonical symbol, but the active TC5 Runtime alias registry accepted only:

```text
US100Cash / US100Cash# / NAS100
```

Therefore the user-facing canonical form `US100` could fail with `SYMBOL_UNRESOLVED` even though the same instrument was already mapped to `PEPPERSTONE / NAS100`.

The existing symbol-registry regression test reproduced the same coverage gap because it did not include `US100` as an input case.

## Fix

The TC5 Runtime registry is amended so that:

```text
US100 / US100Cash / US100Cash# / NAS100
-> canonical US100
-> PEPPERSTONE / NAS100
```

The US100 alias rule is versioned as `US100_ALIAS_V2` for the full family so provenance remains explicit after the registry change.

Updated surfaces:

- `tc/runtime/symbol.py`
- `tests/tc5_runtime/test_symbol_registry.py`
- `tc/runtime/SYMBOL_NORMALIZATION_AMENDMENT_V2.md`
- `tc/runtime/TC5_2_PROVIDER_MAPPING.md`
- `tc/runtime/TC5_10_CHATGPT_HOST_BINDING.md`

## Regression requirement

The runtime regression must prove that each of these resolves identically:

```text
US100
US100Cash
US100Cash#
NAS100
```

Expected result:

```text
canonical_symbol = US100
provider = PEPPERSTONE
provider_symbol = NAS100
alias_rule = US100_ALIAS_V2
```

The repository CI workflow `.github/workflows/tc5-runtime-tests.yml` runs the TC4 regression and all TC5 runtime tests on push to `feature/tc-v1`.

## Boundary audit

No TC4 adapter mapping, TC4 raw schema, TC4 state semantics, TradingCursor response interpretation, profile timeframe contract, or execution permission is changed by this amendment.

This is a TC5 upper-runtime symbol-registry correction only.
