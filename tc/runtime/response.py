from __future__ import annotations

from typing import Any, Mapping, Sequence

from tc.normalizer.normalizer import NormalizedTCState
from tc.runtime.aggregate import TCRoleAggregate
from tc.runtime.symbol import ResolvedSymbol


TIMEFRAME_REPORT_ORDER = ("D1", "H4", "H1", "M15")
REPORT_FORMAT_VERSION = "TF_DIRECTION_ENTRY_TABLE_V2"


def _by_timeframe(records: Sequence[NormalizedTCState]) -> Mapping[str, NormalizedTCState]:
    return {record.timeframe: record for record in records}


def _provenance_rows(values: Sequence[Any] | None) -> list[dict[str, Any]]:
    rows = []
    for value in values or ():
        rows.append(
            {
                "timeframe": getattr(value, "timeframe", None),
                "source_mode": getattr(value, "source_mode", None),
                "fetched_at": getattr(value, "fetched_at", None),
                "cache_age_seconds": getattr(value, "cache_age_seconds", None),
                "reason": getattr(value, "reason", None),
            }
        )
    return rows


def _tc_direction(record: NormalizedTCState) -> str:
    if record.entry_direction in {"LONG", "SHORT"}:
        return record.entry_direction
    env = (record.environment_direction or "").lower()
    if env == "bullish":
        return "LONG"
    if env == "bearish":
        return "SHORT"
    if env == "neutral":
        return "NEUTRAL"
    return "NONE"


def _entry_decision_label(record: NormalizedTCState) -> str:
    direction = record.entry_direction if record.entry_direction in {"LONG", "SHORT"} else None
    if record.trade_state == "ACTIONABLE":
        return direction or "判定保留"
    if record.trade_state == "WAIT":
        if direction == "LONG":
            return "LONG候補"
        if direction == "SHORT":
            return "SHORT候補"
        return "待機"
    if record.trade_state == "INVALID":
        return "無効"
    return "判定保留"


def build_timeframe_decision_rows(
    normalized_records: Sequence[NormalizedTCState],
) -> list[dict[str, Any]]:
    """Build the fixed user-facing per-symbol table rows.

    D1/H4/H1 are always represented. Missing evidence is explicitly shown as
    判定保留 and is never converted into a TC direction of NONE.
    M15 is shown only when it was actually acquired.
    """
    records = _by_timeframe(normalized_records)
    rows: list[dict[str, Any]] = []

    for timeframe in TIMEFRAME_REPORT_ORDER:
        record = records.get(timeframe)
        if record is None:
            if timeframe == "M15":
                continue
            rows.append(
                {
                    "timeframe": timeframe,
                    "tc_direction": "—",
                    "entry_decision": "判定保留",
                    "entry": None,
                    "sl": None,
                    "tp": (),
                }
            )
            continue

        rows.append(
            {
                "timeframe": timeframe,
                "tc_direction": _tc_direction(record),
                "entry_decision": _entry_decision_label(record),
                "entry": record.entry_price,
                "sl": record.stop_loss,
                "tp": tuple(record.take_profits),
            }
        )

    return rows


def _display_value(value: Any) -> str:
    if value is None or value == "":
        return "なし"
    return str(value)


def _display_tp(values: Any) -> str:
    if not values:
        return "なし"
    return " / ".join(str(value) for value in values)


def format_timeframe_decision_table(rows: Sequence[Mapping[str, Any]]) -> str:
    """Render the fixed six-column TC per-symbol table as Markdown."""
    if not rows:
        return ""

    lines = [
        "| TF | TC方向 | ENTRY判定 | Entry | SL | TP |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {timeframe} | {tc_direction} | {entry_decision} | {entry} | {sl} | {tp} |".format(
                timeframe=_display_value(row.get("timeframe")),
                tc_direction=_display_value(row.get("tc_direction")),
                entry_decision=_display_value(row.get("entry_decision")),
                entry=_display_value(row.get("entry")),
                sl=_display_value(row.get("sl")),
                tp=_display_tp(row.get("tp")),
            )
        )
    return "\n".join(lines)


def build_tradeplan_state(
    *,
    aggregate: TCRoleAggregate,
    normalized_records: Sequence[NormalizedTCState],
    resolved_symbol: ResolvedSymbol,
    timestamp: str | None = None,
    timeframe_provenance: Sequence[Any] | None = None,
) -> dict[str, Any]:
    """Build the provisional common output surface for TC Spot/Periodic.

    TC5-15 adds acquisition provenance only. TC5-17 adds a presentation-only
    per-timeframe decision row set under evidence. Decision semantics remain
    sourced from the frozen normalized records and common role aggregation.
    """
    records = _by_timeframe(normalized_records)
    environment_tf = aggregate.role_sources.get("environment")
    setup_tf = aggregate.role_sources.get("setup")
    decision_tf = aggregate.decision_timeframe
    confirmation_tf = aggregate.confirmation_timeframe

    environment = records.get(environment_tf) if environment_tf else None
    setup = records.get(setup_tf) if setup_tf else None
    decision = records.get(decision_tf)
    confirmation = records.get(confirmation_tf) if confirmation_tf else None

    if decision is None:
        raise ValueError(f"decision record missing: {decision_tf}")

    status = aggregate.common_status
    direction = aggregate.direction if aggregate.direction in {"LONG", "SHORT"} else "NONE"
    timeframe_decisions = build_timeframe_decision_rows(normalized_records)

    return {
        "symbol": resolved_symbol.canonical_symbol,
        "timestamp": timestamp,
        "status": status,
        "direction": direction,
        "environment": {
            "direction": environment.environment_direction if environment else None,
            "source_timeframe": environment_tf,
        },
        "setup": {
            "evidence": setup.setup_evidence if setup else None,
            "source_timeframe": setup_tf,
        },
        "entry": {
            "price": decision.entry_price,
            "source_timeframe": decision_tf,
        },
        "stop_loss": {
            "price": decision.stop_loss,
            "source_timeframe": decision_tf,
        },
        "take_profit": {
            "prices": list(decision.take_profits),
            "source_timeframe": decision_tf,
        },
        "invalidation": {
            "evidence": decision.invalidation_evidence,
            "source_timeframe": decision_tf,
        },
        "evidence": {
            "profile": aggregate.profile,
            "runtime_status": aggregate.runtime_status,
            "used_timeframes": list(aggregate.used_timeframes),
            "role_sources": dict(aggregate.role_sources),
            "decision_trade_state": decision.trade_state,
            "decision_state_basis": decision.state_basis,
            "wait_evidence": decision.wait_evidence,
            "trigger_evidence": decision.trigger_evidence,
            "confirmation_trade_state": confirmation.trade_state if confirmation else None,
            "confirmation_record_id": confirmation.record_id if confirmation else None,
            "provider": resolved_symbol.provider,
            "provider_symbol": resolved_symbol.provider_symbol,
            "user_symbol": resolved_symbol.user_symbol,
            "normalized_symbol": resolved_symbol.normalized_symbol,
            "canonical_symbol": resolved_symbol.canonical_symbol,
            "provider_map_rule": resolved_symbol.provider_map_rule,
            "timeframe_provenance": _provenance_rows(timeframe_provenance),
            "report_format": REPORT_FORMAT_VERSION,
            "timeframe_decisions": timeframe_decisions,
        },
        "source_engine": "TC",
        "execution_permission": False,
    }
