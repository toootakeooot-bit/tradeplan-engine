import tempfile
import unittest

from tc.notification.delivery import deliver_notification, retry_saved_notification
from tc.notification.formatter import format_gmail_message
from tc.notification.model import (
    DELIVERY_FAILED,
    DELIVERY_SENT,
    build_periodic_payload,
    build_spot_payload,
)
from tc.notification.outbox import FileNotificationOutbox
from tc.runtime.usage import build_usage_runtime_info


def state(symbol, status, direction, *, profile="NORMAL", entry=None, sl=None, tp=None):
    return {
        "symbol": symbol,
        "status": status,
        "direction": direction,
        "environment": {"direction": direction if direction != "NONE" else "NEUTRAL"},
        "setup": {"evidence": f"{symbol} setup"},
        "entry": {"price": entry},
        "stop_loss": {"price": sl},
        "take_profit": {"prices": tp or []},
        "invalidation": {"evidence": "test invalidation"},
        "evidence": {
            "profile": profile,
            "used_timeframes": ["D1", "H4", "H1"] if profile == "NORMAL" else ["H4", "H1", "M15"],
            "provider": "OANDA" if symbol in {"GOLD", "USDJPY"} else "PEPPERSTONE",
            "provider_symbol": {"GOLD": "XAUUSD", "USDJPY": "USDJPY", "US100": "NAS100", "JP225": "JPN225"}.get(symbol),
        },
        "source_engine": "TC",
        "execution_permission": False,
    }


class FakeSender:
    def __init__(self, *, fail=False):
        self.fail = fail
        self.calls = []

    def send_email(self, *, to, subject, body):
        self.calls.append((to, subject, body))
        if self.fail:
            raise RuntimeError("gmail unavailable")
        return "gmail-message-1"


class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.usage = build_usage_runtime_info(
            current_run_calls=3,
            used_today_before_run=10,
            as_of="2026-09-14T11:15:00Z",
        )

    def test_spot_message_contains_decision_and_runtime_usage(self):
        payload = build_spot_payload(
            run_id="spot-1",
            timestamp="2026-09-14T11:15:00Z",
            tradeplan_state=state("US100", "WAIT", "NONE"),
            runtime_usage=self.usage,
        )
        subject, body = format_gmail_message(payload)
        self.assertIn("[TC Spot][US100][WAIT][NORMAL]", subject)
        self.assertIn("銘柄：US100", body)
        self.assertIn("Execution Permission：NO", body)
        self.assertIn("今回消費：3回", body)
        self.assertIn("予定を抜いた残り：17回", body)
        self.assertIn("Notification ID：tc:spot:spot-1", body)

    def test_periodic_cycle_is_one_grouped_message(self):
        payload = build_periodic_payload(
            cycle_id="periodic-0600-1",
            timestamp="2026-09-14T21:00:00Z",
            tradeplan_states=[
                state("GOLD", "TRADE", "SHORT", entry=3600, sl=3620, tp=[3570]),
                state("USDJPY", "WAIT", "NONE"),
                state("US100", "WAIT", "NONE"),
            ],
            runtime_errors={"JP225": "provider timeout"},
            runtime_usage=build_usage_runtime_info(
                current_run_calls=9,
                used_today_before_run=2,
                scheduled_reserve_calls=8,
                as_of="2026-09-14T21:00:00Z",
            ),
        )
        subject, body = format_gmail_message(payload)
        self.assertIn("[TC定期]", subject)
        self.assertIn("TRADE:1", subject)
        self.assertIn("WAIT:2", subject)
        self.assertIn("ERROR:1", subject)
        for symbol in ("GOLD", "USDJPY", "US100", "JP225"):
            self.assertIn(f"銘柄：{symbol}", body)
        self.assertIn("エラー：provider timeout", body)

    def test_sent_notification_is_idempotent(self):
        payload = build_spot_payload(
            run_id="spot-idempotent",
            timestamp="2026-09-14T11:15:00Z",
            tradeplan_state=state("GOLD", "WAIT", "NONE"),
            runtime_usage=self.usage,
        )
        with tempfile.TemporaryDirectory() as tmp:
            outbox = FileNotificationOutbox(tmp)
            sender = FakeSender()
            first = deliver_notification(
                payload=payload,
                recipient="recipient@example.com",
                sender=sender,
                outbox=outbox,
            )
            second = deliver_notification(
                payload=payload,
                recipient="recipient@example.com",
                sender=sender,
                outbox=outbox,
            )
            self.assertEqual(first.delivery_status, DELIVERY_SENT)
            self.assertEqual(second.delivery_status, DELIVERY_SENT)
            self.assertEqual(first.provider_message_id, "gmail-message-1")
            self.assertEqual(len(sender.calls), 1)

    def test_failed_delivery_retries_saved_payload_only(self):
        payload = build_spot_payload(
            run_id="spot-retry",
            timestamp="2026-09-14T11:15:00Z",
            tradeplan_state=state("USDJPY", "TRADE", "LONG", entry=150, sl=149, tp=[151]),
            runtime_usage=self.usage,
        )
        with tempfile.TemporaryDirectory() as tmp:
            outbox = FileNotificationOutbox(tmp)
            failed_sender = FakeSender(fail=True)
            failed = deliver_notification(
                payload=payload,
                recipient="recipient@example.com",
                sender=failed_sender,
                outbox=outbox,
            )
            self.assertEqual(failed.delivery_status, DELIVERY_FAILED)
            self.assertEqual(failed.attempts, 1)
            self.assertIn("gmail unavailable", failed.last_error)

            success_sender = FakeSender()
            sent = retry_saved_notification(
                notification_id=payload.notification_id,
                recipient="recipient@example.com",
                sender=success_sender,
                outbox=outbox,
            )
            self.assertEqual(sent.delivery_status, DELIVERY_SENT)
            self.assertEqual(sent.attempts, 2)
            self.assertEqual(len(success_sender.calls), 1)
            self.assertEqual(outbox.get(payload.notification_id).payload, payload)

    def test_spot_runtime_error_still_builds_email(self):
        payload = build_spot_payload(
            run_id="spot-error",
            timestamp="2026-09-14T11:15:00Z",
            tradeplan_state=None,
            runtime_usage=None,
            runtime_error="Native 1h failed",
            fallback_symbol="GOLD",
            profile="NORMAL",
        )
        subject, body = format_gmail_message(payload)
        self.assertIn("[GOLD][ERROR][NORMAL]", subject)
        self.assertIn("エラー：Native 1h failed", body)
        self.assertIn("自動注文・発注許可ではありません", body)


if __name__ == "__main__":
    unittest.main()
