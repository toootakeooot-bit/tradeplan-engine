import unittest

from tc.runtime.symbol import resolve_symbol


class SymbolRegistryTests(unittest.TestCase):
    def test_gold_family(self):
        expected = ("GOLD", "OANDA", "XAUUSD")
        for symbol in ("GOLD", "GOLD#", "XAUUSD", "XAU/USD"):
            resolved = resolve_symbol(symbol)
            self.assertEqual((resolved.canonical_symbol, resolved.provider, resolved.provider_symbol), expected)

    def test_usdjpy_family(self):
        expected = ("USDJPY", "OANDA", "USDJPY")
        for symbol in ("USDJPY", "USDJPY#"):
            resolved = resolve_symbol(symbol)
            self.assertEqual((resolved.canonical_symbol, resolved.provider, resolved.provider_symbol), expected)

    def test_us100_family(self):
        expected = ("US100", "PEPPERSTONE", "NAS100")
        for symbol in ("US100", "US100Cash", "US100Cash#", "NAS100"):
            resolved = resolve_symbol(symbol)
            self.assertEqual((resolved.canonical_symbol, resolved.provider, resolved.provider_symbol), expected)
            self.assertEqual(resolved.alias_rule, "US100_ALIAS_V2")

    def test_jp225_family(self):
        expected = ("JP225", "PEPPERSTONE", "JPN225")
        for symbol in ("JP225Cash", "JP225Cash#", "JPN225"):
            resolved = resolve_symbol(symbol)
            self.assertEqual((resolved.canonical_symbol, resolved.provider, resolved.provider_symbol), expected)


if __name__ == "__main__":
    unittest.main()
