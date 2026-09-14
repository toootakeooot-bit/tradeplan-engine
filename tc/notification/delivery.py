from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from tc.notification.formatter import format_gmail_message
from tc.notification.model import DELIVERY_SENT, NotificationEnvelope, TCNotificationPayload
from tc.notification.outbox import FileNotificationOutbox


class EmailSender(Protocol):
    def send_email(self, *, to: str, subject: str, body: str) -> str | None:
        ...


@dataclass(frozen=True)
class CallableEmailSender:
    """Bind a host-provided Gmail/send-email action to the notification contract.

    The callable is expected to accept `to`, `subject`, and `body`. The return
    value may be a string message id, a mapping containing an id/message_id, or
    any other host-specific object. Only an available message id is persisted.
    """

    call: Callable[..., Any]

    def send_email(self, *, to: str, subject: str, body: str) -> str | None:
        response = self.call(to=to, subject=subject, body=body)
        if isinstance(response, str):
            return response
        if isinstance(response, Mapping):
            value = response.get("message_id") or response.get("id")
            return str(value) if value else None
        return None


def deliver_notification(
    *,
    payload: TCNotificationPayload,
    recipient: str,
    sender: EmailSender,
    outbox: FileNotificationOutbox,
) -> NotificationEnvelope:
    """Deliver one saved notification without re-running any TC analysis.

    Delivery failure is converted into FAILED outbox state and intentionally
    does not raise into the TC decision path.
    """
    current = outbox.enqueue(payload)
    if current.delivery_status == DELIVERY_SENT:
        return current

    outbox.mark_attempt(payload.notification_id)
    subject, body = format_gmail_message(payload)
    try:
        provider_message_id = sender.send_email(
            to=recipient,
            subject=subject,
            body=body,
        )
    except Exception as exc:
        return outbox.mark_failed(payload.notification_id, str(exc))

    return outbox.mark_sent(payload.notification_id, provider_message_id)


def retry_saved_notification(
    *,
    notification_id: str,
    recipient: str,
    sender: EmailSender,
    outbox: FileNotificationOutbox,
) -> NotificationEnvelope:
    """Retry Gmail delivery from the persisted payload only.

    This function has no TradingCursor client, planner, or TC service argument by
    design. A retry therefore cannot consume another Native analysis call.
    """
    current = outbox.get(notification_id)
    if current is None:
        raise KeyError(f"notification not found: {notification_id}")
    return deliver_notification(
        payload=current.payload,
        recipient=recipient,
        sender=sender,
        outbox=outbox,
    )
