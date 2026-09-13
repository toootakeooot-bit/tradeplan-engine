# TC5-2 Provider Mapping Audit

Status: **PASS for GOLD and USDJPY on OANDA**.

Observed 2026-09-13 through TradingCursor: `OANDA/XAUUSD/1h` completed and `OANDA/USDJPY/1h` completed. Therefore TC5 may explicitly map canonical GOLD to provider symbol XAUUSD and canonical USDJPY to provider symbol USDJPY for OANDA. This does not change the frozen TC4 Adapter and does not claim XM and OANDA quotes are identical.

Canonical policy remains: GOLD/GOLD#/XAU/USD = GOLD; USDJPY/USDJPY# = USDJPY; terminal `#` is broker suffix normalization, not aliasing. Unknown mappings fail as Runtime Failure, never Trade State.
