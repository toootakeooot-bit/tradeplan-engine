# Symbol Normalization Amendment v2

Status: **ACTIVE TC5 RUNTIME AMENDMENT**

This amendment extends the TC5-0 baseline without changing TC4.

## GOLD

All of the following are accepted as the same logical TC Spot instrument:

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

Validated TradingCursor analysis target:

```text
OANDA / XAUUSD
```

## USDJPY

Accepted:

```text
USDJPY
USDJPY#
```

Canonical:

```text
USDJPY
```

Validated TradingCursor analysis target:

```text
OANDA / USDJPY
```

## US100

Accepted:

```text
US100Cash
US100Cash#
NAS100
```

Canonical:

```text
US100
```

Validated TradingCursor analysis target:

```text
PEPPERSTONE / NAS100
```

## Suffix rule

Terminal `#` remains a broker suffix handled before alias/canonical resolution.

## JP225

`JP225Cash` / `JP225Cash#` remains unresolved until an exact provider/symbol Native call succeeds.
