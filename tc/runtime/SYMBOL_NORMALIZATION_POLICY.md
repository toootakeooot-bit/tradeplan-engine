# TC5-0 — Symbol Normalization Policy

Status: **TC5-0 runtime policy baseline — non-production**

TC Engine v1 Freeze Point: `91a146625e45c913efd9cebf63a3d25217c8bafe`

## 1. Purpose

This policy defines the TC Spot Runtime symbol boundary before the frozen TC4 Adapter/Native boundary.

It separates three distinct operations:

```text
1. Broker Suffix Normalization
2. Canonical Symbol Resolution
3. Provider Symbol Mapping
```

These stages must remain explicit and traceable. They must not be collapsed into an unexplained direct symbol replacement.

## 2. Non-change to TC4

TC4 remains unchanged.

In particular:

- TC4-1 continues to accept and preserve exact broker/source symbols such as `GOLD#` and `USDJPY#` in prepared Market Input provenance;
- TC4-8 Adapter continues to require an exact `analysis_symbol` and performs no automatic broker/canonical mapping;
- no silent symbol conversion is added to the Adapter or TC Engine;
- this TC5 policy is an upper-runtime preprocessing and provenance policy only.

The original user/broker symbol is never discarded merely because a normalized/canonical/provider representation exists.

## 3. Required trace chain

Where applicable, runtime symbol provenance must be capable of representing:

```text
user_symbol
broker_symbol
normalized_symbol
broker_suffix
normalization_rule
canonical_symbol
alias_rule
provider
provider_symbol
provider_map_rule
```

Not every field must be serialized in one object in TC5-0, but the production design must preserve the conceptual trace chain.

## 4. Stage 1 — Broker Suffix Normalization

### 4.1 Meaning of `#`

For the current TC Spot runtime policy, a terminal `#` is a registered broker-specific suffix.

Rule identifier:

```text
BROKER_SUFFIX_HASH_V1
```

Conceptual rule:

```text
<base># -> <base>
```

Examples:

```text
GOLD#      -> GOLD
USDJPY#    -> USDJPY
US100Cash# -> US100Cash
JP225Cash# -> JP225Cash
```

This is **normalization**, not canonical aliasing.

### 4.2 Scope

Only a terminal `#` recognized by the runtime Broker Suffix Registry is removed under `BROKER_SUFFIX_HASH_V1`.

The policy must not perform arbitrary character deletion, embedded-`#` deletion, fuzzy symbol repair, or symbol guessing.

Examples that are not automatically covered:

```text
#GOLD
G#OLD
GOLD##
```

Their future handling belongs to command/input validation, not to this rule.

### 4.3 Normalization does not prove symbol validity

Suffix normalization is syntactic and traceable. It does not by itself prove that the resulting base symbol has a valid canonical or provider mapping.

Example:

```text
UNKNOWN#
  -> normalized_symbol = UNKNOWN
  -> canonical resolution fails
  -> SYMBOL_UNRESOLVED runtime failure
```

The runtime must not convert this failure into WAIT, INVALID, or another Trade State.

### 4.4 Provenance example

```text
user_symbol        = USDJPY#
broker_symbol      = USDJPY#
normalized_symbol  = USDJPY
broker_suffix      = #
normalization_rule = BROKER_SUFFIX_HASH_V1
```

For GOLD:

```text
user_symbol        = GOLD#
broker_symbol      = GOLD#
normalized_symbol  = GOLD
broker_suffix      = #
normalization_rule = BROKER_SUFFIX_HASH_V1
```

## 5. Stage 2 — Canonical Symbol Resolution

Canonical resolution determines the logical instrument identity used by TC5 orchestration. It is separate from broker suffix handling.

### 5.1 GOLD canonical family

The following user/runtime forms are defined as the same logical instrument:

```text
GOLD
GOLD#
XAU/USD
```

Canonical symbol:

```text
GOLD
```

Resolution paths:

```text
GOLD
  -> normalized_symbol = GOLD
  -> canonical_symbol = GOLD
```

```text
GOLD#
  -> BROKER_SUFFIX_HASH_V1
  -> normalized_symbol = GOLD
  -> canonical_symbol = GOLD
```

```text
XAU/USD
  -> no hash-suffix normalization required
  -> canonical alias resolution
  -> canonical_symbol = GOLD
```

Canonical alias rule:

```text
GOLD_ALIAS_V1
```

Minimum entries:

```text
GOLD    -> GOLD
XAU/USD -> GOLD
```

`GOLD# -> GOLD` is deliberately **not** an alias-table entry; it is the result of Broker Suffix Normalization followed by the `GOLD -> GOLD` canonical identity mapping.

### 5.2 USDJPY canonical family

The following forms represent the same logical instrument:

```text
USDJPY
USDJPY#
```

Canonical symbol:

```text
USDJPY
```

Paths:

```text
USDJPY
  -> canonical_symbol = USDJPY
```

```text
USDJPY#
  -> BROKER_SUFFIX_HASH_V1
  -> normalized_symbol = USDJPY
  -> canonical_symbol = USDJPY
```

No separate `USDJPY#` alias is created.

### 5.3 Other broker symbols

The suffix rule is reusable for symbols such as:

```text
US100Cash# -> US100Cash
JP225Cash# -> JP225Cash
```

TC5-0 fixes the common suffix behavior only. It does not assert an unvalidated provider mapping or additional cross-name alias for these instruments. Their canonical/provider registry entries may be fixed in later TC5 work using explicit evidence/configuration.

## 6. Stage 3 — Provider Symbol Mapping

Provider Symbol Mapping converts a validated canonical instrument into the **exact symbol token required by the selected provider/TradingCursor Native request**.

Conceptual direction:

```text
canonical_symbol + provider/source
  -> validated provider mapping
  -> provider_symbol
  -> AdapterRequest.analysis_symbol
```

This stage must be explicit and configuration/evidence-backed.

TC5-0 does not freeze one universal provider token for GOLD because exact Native symbols are provider/source-specific. Existing TC4 evidence includes provider-native forms such as `XAUUSD`; user-facing `XAU/USD` is a canonical alias form, not proof that every Native provider accepts the slash form.

Therefore this policy does **not** assume:

```text
canonical GOLD -> provider_symbol XAU/USD for every provider
```

Instead, the production mapper must use the exact validated provider/source mapping.

Example conceptual trace:

```text
user_symbol        = GOLD#
broker_symbol      = GOLD#
normalized_symbol  = GOLD
broker_suffix      = #
normalization_rule = BROKER_SUFFIX_HASH_V1
canonical_symbol   = GOLD
alias_rule         = GOLD_ALIAS_V1
provider           = <selected provider/source>
provider_symbol    = <validated exact provider token>
provider_map_rule  = <versioned provider mapping rule>
```

## 7. Explicit conversion vs silent conversion

Allowed:

```text
GOLD#
 -> record user/broker symbol
 -> BROKER_SUFFIX_HASH_V1
 -> GOLD
 -> GOLD_ALIAS_V1
 -> canonical GOLD
 -> explicit provider mapping rule
 -> exact provider symbol
```

Forbidden:

```text
GOLD#
 -> unexplained replacement
 -> Native request
```

The former is a TC5 upper-runtime traceable transformation. The latter is the silent symbol conversion prohibited by the TC4 baseline.

## 8. Prepared Market Input provenance

If prepared Market Input originated from a broker chart labeled `GOLD#`, the broker/source identity remains `GOLD#` in the source/input provenance even if TC5 also derives:

```text
normalized_symbol = GOLD
canonical_symbol  = GOLD
```

TC5 must not rewrite historical/chart provenance to pretend the broker emitted `GOLD` or `XAU/USD`.

The same rule applies to `USDJPY#` and other broker-suffixed source symbols.

## 9. Unknown / unresolved symbols

If any required stage cannot resolve safely, processing stops as Runtime/Infrastructure Failure.

Candidate conceptual failure labels include:

```text
SYMBOL_FORMAT_INVALID
SUFFIX_UNSUPPORTED
SYMBOL_UNRESOLVED
PROVIDER_MAPPING_UNRESOLVED
```

TC5-0 does not freeze the final runtime failure enum/schema.

Prohibited behavior:

- fuzzy-match to the nearest known symbol;
- infer a provider symbol from naming similarity;
- substitute another instrument;
- convert symbol failure to Trade WAIT;
- convert symbol failure to Trade INVALID.

## 10. Case, whitespace, and other formatting

TC5-0 intentionally does not freeze case-folding, whitespace trimming, alternate separators, or broad symbol spelling normalization.

Those are Command/Input validation concerns for later TC5 work. They must not be silently introduced as strategy or provider mappings.

The only broker-suffix rule frozen here is the registered terminal `#` behavior.

## 11. Runtime invariants

The following are fixed by TC5-0:

```text
Broker Suffix Normalization != Canonical Alias Resolution
Canonical Alias Resolution != Provider Symbol Mapping
Provider Symbol Mapping != TC Adapter-owned conversion

GOLD / GOLD# / XAU/USD -> canonical GOLD
USDJPY / USDJPY#       -> canonical USDJPY

terminal # = registered broker suffix under BROKER_SUFFIX_HASH_V1
original broker/user symbol remains traceable
unknown symbol is not guessed
unresolved symbol is Runtime Failure, not Trade State
```

## 12. Deferred implementation details

Deferred to later TC5 work:

- physical registry/configuration format;
- exact data model/schema for the trace chain;
- case/whitespace parser policy;
- provider/source selection algorithm;
- complete canonical symbol registry;
- complete provider mapping registry;
- production validation code;
- logging/storage format;
- configuration version deployment process.
