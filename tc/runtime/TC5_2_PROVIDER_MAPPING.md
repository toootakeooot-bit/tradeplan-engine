# TC5-2 Provider Mapping

Status: **VALIDATED PROVIDER REGISTRY — PARTIAL**

Validated on 2026-09-13 through successful TradingCursor Native analysis calls.

## GOLD family

User/runtime aliases:

```text
GOLD
GOLD#
XAUUSD
XAU/USD
```

Canonical:

```text
GOLD
```

TradingCursor analysis target:

```text
provider/source = OANDA
provider_symbol = XAUUSD
```

The aliases are naming/input forms only. Original broker/user symbol remains traceable.

## USDJPY family

User/runtime aliases:

```text
USDJPY
USDJPY#
```

Canonical:

```text
USDJPY
```

TradingCursor analysis target:

```text
provider/source = OANDA
provider_symbol = USDJPY
```

## US100 family

User/runtime aliases:

```text
US100Cash
US100Cash#
NAS100
```

Canonical:

```text
US100
```

TradingCursor analysis target:

```text
provider/source = PEPPERSTONE
provider_symbol = NAS100
```

`PEPPERSTONE / NAS100 / 4h` completed successfully through TradingCursor on 2026-09-13.

## Broker suffix

Terminal `#` is handled by `BROKER_SUFFIX_HASH_V1` before canonical resolution.

Examples:

```text
GOLD#      -> GOLD
USDJPY#    -> USDJPY
US100Cash# -> US100Cash
```

This normalization is separate from canonical alias resolution and Provider Symbol Mapping.

## Boundary

Provider mapping remains explicit in TC5 Runtime and outside the frozen TC4 Adapter. TC4 Adapter receives exact `analysis_source` and `analysis_symbol`; it performs no silent broker-to-provider conversion.

## Not yet validated

```text
JP225Cash / JP225Cash#
```

No TradingCursor provider/symbol mapping is fixed for JP225 until a successful Native call is observed.
