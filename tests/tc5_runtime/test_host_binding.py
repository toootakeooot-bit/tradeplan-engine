import unittest

from tc.runtime.host_binding import CallableNativeClient
from tc.runtime.symbol import resolve_symbol


class HostBindingTests(unittest.TestCase):
    def test_callable_binding_passes_exact_native_arguments_and_response(self):
        calls = []
        native = {
            "status": "completed",
            "exchange": "OANDA",
            "symbol": "XAUUSD",
            "interval": "1h",
            "analysis": "{}",
            "model": "test-model",
            "timestamp": "2026-09-13T00:00:00Z",
        }

        def host_call(*, exchange, symbol, interval):
            calls.append((exchange, symbol, interval))
            return native

        client = CallableNativeClient(host_call)
        result = client.request_analysis(exchange="OANDA", symbol="XAUUSD", interval="1h")

        self.assertEqual(calls, [("OANDA", "XAUUSD", "1h")])
        self.assertIs(result, native)

    def test_validated_symbol_registry_covers_four_target_families(self):
        expected = {
            "GOLD#": ("GOLD", "OANDA", "XAUUSD"),
            "USDJPY#": ("USDJPY", "OANDA", "USDJPY"),
            "US100Cash#": ("US100", "PEPPERSTONE", "NAS100"),
            "JP225Cash#": ("JP225", "PEPPERSTONE", "JPN225"),
        }
        for user_symbol, target in expected.items():
            resolved = resolve_symbol(user_symbol)
            self.assertEqual(
                (resolved.canonical_symbol, resolved.provider, resolved.provider_symbol),
                target,
            )


if __name__ == "__main__":
    unittest.main()
