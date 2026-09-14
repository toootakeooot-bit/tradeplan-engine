import unittest

from tc.runtime.host_guard import (
    HostExecutionGuardError,
    assert_native_first_failure_boundary,
    prepare_native_first_execution,
)


class HostNativeFirstGuardTests(unittest.TestCase):
    def test_gold_normal_prepares_native_plan_without_chart_or_device_context(self):
        prepared = prepare_native_first_execution("tc スポット GOLD# エントリー前")

        self.assertEqual(prepared.resolved_symbol.canonical_symbol, "GOLD")
        self.assertEqual(prepared.resolved_symbol.provider, "OANDA")
        self.assertEqual(prepared.resolved_symbol.provider_symbol, "XAUUSD")
        self.assertEqual(
            [(step.timeframe, step.interval) for step in prepared.initial_plan],
            [("D1", "1D"), ("H4", "4h"), ("H1", "1h")],
        )

    def test_mobile_and_desktop_session_labels_cannot_change_native_plan(self):
        # Device/session labels are intentionally outside the guard API. Repeated
        # preparation of the same accepted command must therefore be identical.
        mobile_new_session = prepare_native_first_execution("tc スポット GOLD# エントリー前")
        desktop_existing_session = prepare_native_first_execution("tc スポット GOLD# エントリー前")

        self.assertEqual(mobile_new_session, desktop_existing_session)

    def test_short_profile_prepares_required_three_native_calls(self):
        prepared = prepare_native_first_execution("tc スポット GOLD# 短期 エントリー前")
        self.assertEqual(
            [(step.timeframe, step.interval) for step in prepared.initial_plan],
            [("H4", "4h"), ("H1", "1h"), ("M15", "15m")],
        )

    def test_missing_chart_stop_before_native_is_rejected(self):
        with self.assertRaises(HostExecutionGuardError) as caught:
            assert_native_first_failure_boundary(
                attempted_calls=0,
                failure_reason="チャート入力がないため Market Input未取得。STOP",
                required_intervals=("1D", "4h", "1h"),
            )

        self.assertEqual(caught.exception.code, "NATIVE_FIRST_VIOLATION")

    def test_mobile_screen_visibility_stop_before_native_is_rejected(self):
        with self.assertRaises(HostExecutionGuardError) as caught:
            assert_native_first_failure_boundary(
                attempted_calls=0,
                failure_reason="スマホでは全体が見えないため実行できない",
                required_intervals=("1D", "4h", "1h"),
            )

        self.assertEqual(caught.exception.code, "NATIVE_FIRST_VIOLATION")

    def test_provider_failure_after_native_attempt_is_allowed(self):
        assert_native_first_failure_boundary(
            attempted_calls=1,
            failure_reason="OANDA/XAUUSD/1D provider unavailable",
            required_intervals=("1D", "4h", "1h"),
        )

    def test_unknown_zero_attempt_failure_is_still_rejected(self):
        with self.assertRaises(HostExecutionGuardError) as caught:
            assert_native_first_failure_boundary(
                attempted_calls=0,
                failure_reason="unexpected host stop",
            )

        self.assertEqual(caught.exception.code, "NATIVE_ATTEMPT_NOT_OBSERVED")


if __name__ == "__main__":
    unittest.main()
