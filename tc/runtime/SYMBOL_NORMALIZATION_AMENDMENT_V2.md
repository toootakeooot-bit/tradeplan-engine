# Symbol Normalization Amendment v2

Status: **ACTIVE TC5 RUNTIME AMENDMENT**

This amendment extends the TC5-0 baseline without changing TC4.

## GOLD

```text
GOLD / GOLD# / XAUUSD / XAU/USD
-> canonical GOLD
-> OANDA / XAUUSD
```

## USDJPY

```text
USDJPY / USDJPY#
-> canonical USDJPY
-> OANDA / USDJPY
```

## US100

```text
US100Cash / US100Cash# / NAS100
-> canonical US100
-> PEPPERSTONE / NAS100
```

## JP225

```text
JP225Cash / JP225Cash# / JPN225
-> canonical JP225
-> PEPPERSTONE / JPN225
```

`PEPPERSTONE / JPN225 / 4h` completed successfully through TradingCursor on 2026-09-13.

## Suffix rule

Terminal `#` remains a broker suffix handled before alias/canonical resolution.

## Boundary

These mappings belong to TC5 Runtime. The frozen TC4 Adapter still receives exact provider/source and provider symbol and performs no silent symbol conversion.
