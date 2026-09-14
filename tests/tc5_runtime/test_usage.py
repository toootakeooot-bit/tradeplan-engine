import unittest

from tc.runtime.host_binding import UsageTrackingNativeClient
from tc.runtime.usage import build_usage_runtime_info, format_usage_runtime_info


class FakeClient:
    def __init__(self):
        self.calls = 0

    def request_analysis(self, *, exchange, symbol, interval):
        self.calls += 1
        return {"status": "completed", "interval": interval}


class FailingClient:
    def request_analysis(self, *, exchange, symbol, interval):
        raise RuntimeError("provider failure")


class UsageRuntimeTests(unittest.TestCase):
    def test_budget_math_and_reset_display(self):
        info = build_usage_runtime_info(
            current_run_calls=3,
            used_today_before_run=10,
            as_of="2026-09-14T10:34:00Z",
        )
        self.assertEqual(info.used_today, 13)
        self.assertEqual(info.remaining_before_reserve, 37)
        self.assertEqual(info.scheduled_reserve_calls, 20)
        self.assertEqual(info.remaining_after_reserve, 17)
        self.assertEqual(info.spot_equivalent, 5)
        self.assertEqual(info.next_reset_utc, "2026-09-15T00:00:00Z")
        self.assertTrue(info.next_reset_jst.startswith("2026-09-15T09:00:00"))
        self.assertEqual(
            format_usage_runtime_info(info),
            "\n".join(
                [
                    "TC利用状況",
                    "今回消費：3回",
                    "予定を抜いた残り：17回",
                    "スポット換算：約5回分",
                    "次回リセット：9/15 09:00（日本時間）",
                ]
            ),
        )

    def test_unknown_daily_ledger_never_fabricates_remaining(self):
        info = build_usage_runtime_info(
            current_run_calls=3,
            used_today_before_run=None,
            as_of="2026-09-14T10:34:00Z",
        )
        self.assertIsNone(info.used_today)
        self.assertIsNone(info.remaining_after_reserve)
        self.assertIsNone(info.spot_equivalent)
        rendered = format_usage_runtime_info(info)
        self.assertIn("今回消費：3回", rendered)
        self.assertIn("予定を抜いた残り：不明", rendered)
        self.assertIn("スポット換算：不明", rendered)

    def test_successful_native_response_is_counted_at_host_boundary(self):
        wrapped = UsageTrackingNativeClient(FakeClient())
        response = wrapped.request_analysis(
            exchange="OANDA",
            symbol="XAUUSD",
            interval="1D",
        )
        self.assertEqual(response["status"], "completed")
        self.assertEqual(wrapped.successful_calls, 1)

    def test_failed_native_call_is_not_counted(self):
        wrapped = UsageTrackingNativeClient(FailingClient())
        with self.assertRaises(RuntimeError):
            wrapped.request_analysis(
                exchange="OANDA",
                symbol="XAUUSD",
                interval="1D",
            )
        self.assertEqual(wrapped.successful_calls, 0)


if __name__ == "__main__":
    unittest.main()
