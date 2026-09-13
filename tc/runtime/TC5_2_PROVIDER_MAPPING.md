# TC5-2 Provider Mapping

Status: **VALIDATED PROVIDER REGISTRY — ACTIVE**

Validated on 2026-09-13 through successful TradingCursor Native analysis calls.

## GOLD family

```text
GOLD / GOLD# / XAUUSD / XAU/USD
-> canonical GOLD
-> OANDA / XAUUSD
```

## USDJPY family

```text
USDJPY / USDJPY#
-> canonical USDJPY
-> OANDA / USDJPY
```

## US100 family

```text
US100Cash / US100Cash# / NAS100
-> canonical US100
-> PEPPERSTONE / NAS100
```

`PEPPERSTONE / NAS100 / 4h` completed successfully through TradingCursor on 2026-09-13.

## JP225 family

```text
JP225Cash / JP225Cash# / JPN225
-> canonical JP225
-> PEPPERSTONE / JPN225
```

`PEPPERSTONE / JPN225 / 4h` completed successfully through TradingCursor on 2026-09-13.

## Broker suffix

Terminal `#` is handled by `BROKER_SUFFIX_HASH_V1` before canonical resolution.

```text
GOLD#      -> GOLD
USDJPY#    -> USDJPY
US100Cash# -> US100Cash
JP225Cash# -> JP225Cash
```

Broker suffix normalization, canonical alias resolution and Provider Symbol Mapping remain separate and traceable operations.

## Boundary

Provider mapping remains explicit in TC5 Runtime and outside the frozen TC4 Adapter. TC4 Adapter receives exact `analysis_source` and `analysis_symbol`; it performs no silent broker-to-provider conversion.
