from __future__ import annotations

from typing import Any, Mapping, Sequence

from tc.normalizer.normalizer import NormalizedTCState
from tc.runtime.aggregate import TCRoleAggregate
from tc.runtime.symbol import ResolvedSymbol


def _by_timeframe(records: Sequence[NormalizedTCState]) -> Mapping[str, NormalizedTCState]:
    return {record.timeframe: record for record in records}


def build_tradeplan_state(
    *,
    aggregate: TCRoleAggregate,
    normalized_records: Sequence[NormalizedTCState],
    resolved_symbol: ResolvedSymbol,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build the provisional common output surface for TC Spot.

    This does not finalize the Common schema for NODA. It only emits fields
    already authorized by the provisional TradePlanState direction.
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
        },
        "source_engine": "TC",
        "execution_permission": False,
    }
