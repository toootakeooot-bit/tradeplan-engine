from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

from tc.notification.model import (
    DELIVERY_FAILED,
    DELIVERY_PENDING,
    DELIVERY_SENT,
    NotificationEnvelope,
    TCNotificationPayload,
    envelope_from_dict,
    envelope_to_dict,
)


class FileNotificationOutbox:
    """Durable idempotent outbox for TC email notifications.

    The payload is persisted before delivery. A notification_id maps to one
    stable file, so repeated enqueue calls cannot create duplicate messages.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, notification_id: str) -> Path:
        digest = hashlib.sha256(notification_id.encode("utf-8")).hexdigest()
        return self.root / f"{digest}.json"

    def _write(self, envelope: NotificationEnvelope) -> NotificationEnvelope:
        path = self._path(envelope.payload.notification_id)
        temp = path.with_suffix(".tmp")
        temp.write_text(
            json.dumps(envelope_to_dict(envelope), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp.replace(path)
        return envelope

    def get(self, notification_id: str) -> NotificationEnvelope | None:
        path = self._path(notification_id)
        if not path.exists():
            return None
        return envelope_from_dict(json.loads(path.read_text(encoding="utf-8")))

    def enqueue(self, payload: TCNotificationPayload) -> NotificationEnvelope:
        existing = self.get(payload.notification_id)
        if existing is not None:
            return existing
        return self._write(NotificationEnvelope(payload=payload))

    def mark_attempt(self, notification_id: str) -> NotificationEnvelope:
        current = self._require(notification_id)
        if current.delivery_status == DELIVERY_SENT:
            return current
        return self._write(
            replace(
                current,
                delivery_status=DELIVERY_PENDING,
                attempts=current.attempts + 1,
                last_error=None,
            )
        )

    def mark_sent(self, notification_id: str, provider_message_id: str | None = None) -> NotificationEnvelope:
        current = self._require(notification_id)
        return self._write(
            replace(
                current,
                delivery_status=DELIVERY_SENT,
                last_error=None,
                provider_message_id=provider_message_id,
            )
        )

    def mark_failed(self, notification_id: str, error: str) -> NotificationEnvelope:
        current = self._require(notification_id)
        return self._write(
            replace(
                current,
                delivery_status=DELIVERY_FAILED,
                last_error=error,
            )
        )

    def _require(self, notification_id: str) -> NotificationEnvelope:
        current = self.get(notification_id)
        if current is None:
            raise KeyError(f"notification not found: {notification_id}")
        return current
