from __future__ import annotations

from dataclasses import dataclass


class SymbolResolutionError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ResolvedSymbol:
    user_symbol: str
    normalized_symbol: str
    canonical_symbol: str
    provider: str
    provider_symbol: str
    broker_suffix: str | None
    normalization_rule: str | None
    alias_rule: str
    provider_map_rule: str


# GOLD user-facing aliases are normalized to one logical instrument.
# TradingCursor analysis for this family is intentionally centralized on
# the validated provider mapping OANDA / XAUUSD.
_CANONICAL = {
    "GOLD": ("GOLD", "GOLD_ALIAS_V2"),
    "XAUUSD": ("GOLD", "GOLD_ALIAS_V2"),
    "XAU/USD": ("GOLD", "GOLD_ALIAS_V2"),
    "USDJPY": ("USDJPY", "USDJPY_IDENTITY_V1"),
}

_OANDA = {
    "GOLD": "XAUUSD",
    "USDJPY": "USDJPY",
}


def resolve_symbol(user_symbol: str, provider: str = "OANDA") -> ResolvedSymbol:
    if not isinstance(user_symbol, str) or not user_symbol:
        raise SymbolResolutionError("SYMBOL_FORMAT_INVALID", "symbol must be a non-empty string")

    broker_suffix = None
    normalization_rule = None
    normalized = user_symbol
    if user_symbol.endswith("#") and not user_symbol.endswith("##"):
        broker_suffix = "#"
        normalization_rule = "BROKER_SUFFIX_HASH_V1"
        normalized = user_symbol[:-1]
    elif "#" in user_symbol:
        raise SymbolResolutionError("SYMBOL_FORMAT_INVALID", "only one terminal # suffix is supported")

    canonical_entry = _CANONICAL.get(normalized)
    if canonical_entry is None:
        raise SymbolResolutionError("SYMBOL_UNRESOLVED", f"no canonical mapping for {normalized}")
    canonical_symbol, alias_rule = canonical_entry

    if provider != "OANDA":
        raise SymbolResolutionError("PROVIDER_UNSUPPORTED", f"unsupported provider: {provider}")
    provider_symbol = _OANDA.get(canonical_symbol)
    if provider_symbol is None:
        raise SymbolResolutionError(
            "PROVIDER_MAPPING_UNRESOLVED",
            f"no validated OANDA mapping for {canonical_symbol}",
        )

    return ResolvedSymbol(
        user_symbol=user_symbol,
        normalized_symbol=normalized,
        canonical_symbol=canonical_symbol,
        provider=provider,
        provider_symbol=provider_symbol,
        broker_suffix=broker_suffix,
        normalization_rule=normalization_rule,
        alias_rule=alias_rule,
        provider_map_rule="TC5_OANDA_PROVIDER_MAP_V1",
    )
