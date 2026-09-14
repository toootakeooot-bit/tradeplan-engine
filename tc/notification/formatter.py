from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from tc.notification.model import (
    TRIGGER_PERIODIC,
    TRIGGER_SPOT,
    TCNotificationPayload,
    TCNotificationResult,
)
from tc.runtime.usage import format_usage_runtime_info


JST = timezone(timedelta(hours=9))


def _format_value(value: Any) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _timestamp_jst(timestamp: str) -> tuple[str, str]:
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        local = parsed.astimezone(JST)
        return local.strftime("%Y-%m-%d %H:%M"), local.strftime("%Y/%m/%d %H:%M JST")
    except Exception:
        return timestamp, timestamp


def _result_lines(result: TCNotificationResult) -> list[str]:
    if result.status == "ERROR":
        return [
            f"銘柄：{result.symbol}",
            "判定：ERROR",
            f"エラー：{_format_value(result.runtime_error)}",
            "Execution Permission：NO",
        ]

    permission = "YES" if result.execution_permission else "NO"
    return [
        f"銘柄：{result.symbol}",
        f"Profile：{_format_value(result.profile)}",
        f"判定：{result.status}",
        f"方向：{result.direction}",
        "",
        f"Environment：{_format_value(result.environment)}",
        f"Setup：{_format_value(result.setup)}",
        "",
        f"Entry：{_format_value(result.entry_price)}",
        f"SL：{_format_value(result.stop_loss)}",
        f"TP：{_format_value(result.take_profits)}",
        f"Invalidation：{_format_value(result.invalidation)}",
        "",
        f"使用TF：{_format_value(result.used_timeframes)}",
        f"Provider：{_format_value(result.provider)} / {_format_value(result.provider_symbol)}",
        f"Execution Permission：{permission}",
    ]


def format_gmail_subject(payload: TCNotificationPayload) -> str:
    compact_time, _ = _timestamp_jst(payload.timestamp)

    if payload.trigger_type == TRIGGER_SPOT:
        if payload.results:
            result = payload.results[0]
            profile = result.profile or "-"
            return f"[TC Spot][{result.symbol}][{result.status}][{profile}] {compact_time} JST"
        return f"[TC Spot][ERROR] {compact_time} JST"

    if payload.trigger_type == TRIGGER_PERIODIC:
        counts = Counter(result.status for result in payload.results)
        order = ("TRADE", "WAIT", "HOLD", "INVALID", "ERROR")
        summary = " ".join(f"{status}:{counts[status]}" for status in order if counts[status])
        summary = summary or "NO_RESULT"
        return f"[TC定期][{summary}] {compact_time} JST"

    raise ValueError(f"unsupported trigger_type: {payload.trigger_type}")


def format_gmail_body(payload: TCNotificationPayload) -> str:
    _, display_time = _timestamp_jst(payload.timestamp)
    lines: list[str] = []

    if payload.trigger_type == TRIGGER_SPOT:
        lines.extend(["TC Spot 判定", display_time, ""])
        if payload.results:
            lines.extend(_result_lines(payload.results[0]))
        elif payload.runtime_error:
            lines.extend(["判定：ERROR", f"エラー：{payload.runtime_error}"])
    elif payload.trigger_type == TRIGGER_PERIODIC:
        lines.extend(["TC定期判定", display_time, ""])
        for index, result in enumerate(payload.results):
            if index:
                lines.extend(["", "--------------------", ""])
            lines.extend(_result_lines(result))
    else:
        raise ValueError(f"unsupported trigger_type: {payload.trigger_type}")

    if payload.runtime_error:
        lines.extend(["", "Runtime Error", payload.runtime_error])

    if payload.runtime_usage is not None:
        lines.extend(["", "--------------------", format_usage_runtime_info(payload.runtime_usage)])

    lines.extend(
        [
            "",
            "--------------------",
            f"Run ID：{payload.run_id}",
            f"Notification ID：{payload.notification_id}",
            "※ TC判定通知です。自動注文・発注許可ではありません。",
        ]
    )
    return "\n".join(lines)


def format_gmail_message(payload: TCNotificationPayload) -> tuple[str, str]:
    return format_gmail_subject(payload), format_gmail_body(payload)
