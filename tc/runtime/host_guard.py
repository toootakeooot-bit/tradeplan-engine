from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from tc.runtime.command import TCSpotRuntimeRequest, parse_spot_command
from tc.runtime.planner import NativeRequestPlan, build_entry_pre_plan
from tc.runtime.symbol import ResolvedSymbol, resolve_symbol


class HostExecutionGuardError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class NativeFirstPreparation:
    """Host-facing preparation for an accepted TC Spot command.

    Device type, screen visibility, chat session state, uploaded charts, and
    pre-supplied Market Input are intentionally not inputs. The live source is
    TradingCursor Native, so an accepted command must produce a Native request
    plan before any Market Input availability decision is made.
    """

    command_request: TCSpotRuntimeRequest
    resolved_symbol: ResolvedSymbol
    initial_plan: Tuple[NativeRequestPlan, ...]


_FORBIDDEN_PRE_NATIVE_STOP_MARKERS = (
    "chart",
    "uploaded chart",
    "pre-supplied market input",
    "market input missing",
    "screen",
    "display",
    "mobile",
    "smartphone",
    "session",
    "チャート",
    "market input不足",
    "market input未取得",
    "全体が見えない",
    "画面",
    "スマホ",
    "セッション",
)


def prepare_native_first_execution(command_text: str) -> NativeFirstPreparation:
    """Resolve an accepted TC Spot command into its mandatory initial Native plan."""
    command_request = parse_spot_command(command_text)
    resolved_symbol = resolve_symbol(command_request.user_symbol)
    initial_plan = build_entry_pre_plan(command_request, resolved_symbol)
    if not initial_plan:
        raise HostExecutionGuardError(
            "NATIVE_PLAN_EMPTY",
            "accepted TC Spot command produced no TradingCursor Native requests",
        )
    return NativeFirstPreparation(
        command_request=command_request,
        resolved_symbol=resolved_symbol,
        initial_plan=initial_plan,
    )


def assert_native_first_failure_boundary(
    *,
    attempted_calls: int,
    failure_reason: str | None = None,
    required_intervals: Iterable[str] | None = None,
) -> None:
    """Reject a Host failure that occurs before any required Native attempt.

    A runtime/provider failure is allowed after at least one actual Native call
    attempt. With zero attempts, reasons tied to charts, Market Input supplied by
    the user, screen/device visibility, or chat-session state are prohibited.
    """
    if attempted_calls < 0:
        raise ValueError("attempted_calls must be >= 0")
    if attempted_calls > 0:
        return

    reason = (failure_reason or "").casefold()
    matched = [marker for marker in _FORBIDDEN_PRE_NATIVE_STOP_MARKERS if marker in reason]
    if matched:
        intervals = tuple(required_intervals or ())
        suffix = f" required_intervals={intervals}" if intervals else ""
        raise HostExecutionGuardError(
            "NATIVE_FIRST_VIOLATION",
            "TC Spot stopped before any TradingCursor Native attempt for a "
            f"non-authoritative Host-context reason ({matched[0]}).{suffix}",
        )

    raise HostExecutionGuardError(
        "NATIVE_ATTEMPT_NOT_OBSERVED",
        "TC Spot failure was reported before any TradingCursor Native attempt was observed",
    )
