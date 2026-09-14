from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone


UTC = timezone.utc
JST = timezone(timedelta(hours=9))


@dataclass(frozen=True)
class TCUsagePolicy:
    """Budget policy for the TC Spot Host usage display.

    This is a local Host budget model, not provider-authoritative quota telemetry.
    """

    daily_limit: int = 50
    scheduled_reserve_calls: int = 20
    spot_call_budget: int = 3
    reset_hour_utc: int = 0


DEFAULT_TC_USAGE_POLICY = TCUsagePolicy()


@dataclass(frozen=True)
class TCUsageRuntimeInfo:
    current_run_calls: int
    used_today: int | None
    remaining_before_reserve: int | None
    scheduled_reserve_calls: int
    remaining_after_reserve: int | None
    spot_equivalent: int | None
    next_reset_utc: str
    next_reset_jst: str


def _coerce_as_of(as_of: datetime | str | None) -> datetime:
    if as_of is None:
        return datetime.now(UTC)
    if isinstance(as_of, str):
        parsed = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    elif isinstance(as_of, datetime):
        parsed = as_of
    else:
        raise TypeError("as_of must be datetime, ISO-8601 string, or None")
    if parsed.tzinfo is None:
        raise ValueError("as_of must be timezone-aware")
    return parsed.astimezone(UTC)


def _next_reset(as_of: datetime, reset_hour_utc: int) -> datetime:
    if not 0 <= reset_hour_utc <= 23:
        raise ValueError("reset_hour_utc must be between 0 and 23")
    candidate = datetime.combine(
        as_of.date(),
        time(hour=reset_hour_utc, tzinfo=UTC),
    )
    if candidate <= as_of:
        candidate += timedelta(days=1)
    return candidate


def build_usage_runtime_info(
    *,
    current_run_calls: int,
    used_today_before_run: int | None,
    scheduled_reserve_calls: int | None = None,
    as_of: datetime | str | None = None,
    policy: TCUsagePolicy = DEFAULT_TC_USAGE_POLICY,
) -> TCUsageRuntimeInfo:
    """Build Host-only usage information for one TC Spot run.

    `current_run_calls` counts successful Native responses in this run.
    `used_today_before_run` is supplied by the Host's daily ledger. When that
    value is unavailable, remaining figures are intentionally left unknown
    rather than fabricated.
    """
    if current_run_calls < 0:
        raise ValueError("current_run_calls must be non-negative")
    if used_today_before_run is not None and used_today_before_run < 0:
        raise ValueError("used_today_before_run must be non-negative")
    if policy.daily_limit <= 0:
        raise ValueError("daily_limit must be positive")
    if policy.spot_call_budget <= 0:
        raise ValueError("spot_call_budget must be positive")

    reserve = (
        policy.scheduled_reserve_calls
        if scheduled_reserve_calls is None
        else scheduled_reserve_calls
    )
    if reserve < 0:
        raise ValueError("scheduled_reserve_calls must be non-negative")

    now_utc = _coerce_as_of(as_of)
    reset_utc = _next_reset(now_utc, policy.reset_hour_utc)
    reset_jst = reset_utc.astimezone(JST)

    used_today = None
    remaining_before_reserve = None
    remaining_after_reserve = None
    spot_equivalent = None

    if used_today_before_run is not None:
        used_today = used_today_before_run + current_run_calls
        remaining_before_reserve = max(0, policy.daily_limit - used_today)
        remaining_after_reserve = max(0, remaining_before_reserve - reserve)
        spot_equivalent = remaining_after_reserve // policy.spot_call_budget

    return TCUsageRuntimeInfo(
        current_run_calls=current_run_calls,
        used_today=used_today,
        remaining_before_reserve=remaining_before_reserve,
        scheduled_reserve_calls=reserve,
        remaining_after_reserve=remaining_after_reserve,
        spot_equivalent=spot_equivalent,
        next_reset_utc=reset_utc.isoformat().replace("+00:00", "Z"),
        next_reset_jst=reset_jst.isoformat(),
    )


def format_usage_runtime_info(info: TCUsageRuntimeInfo) -> str:
    """Render the user-facing TC usage block outside TradePlanState."""
    remaining = (
        f"{info.remaining_after_reserve}回"
        if info.remaining_after_reserve is not None
        else "不明"
    )
    spot = (
        f"約{info.spot_equivalent}回分"
        if info.spot_equivalent is not None
        else "不明"
    )
    reset_jst = datetime.fromisoformat(info.next_reset_jst)
    reset_text = f"{reset_jst.month}/{reset_jst.day} {reset_jst:%H:%M}（日本時間）"

    return "\n".join(
        [
            "TC利用状況",
            f"今回消費：{info.current_run_calls}回",
            f"予定を抜いた残り：{remaining}",
            f"スポット換算：{spot}",
            f"次回リセット：{reset_text}",
        ]
    )
