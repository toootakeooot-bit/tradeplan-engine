from __future__ import annotations

import copy
import re
from enum import Enum
from typing import Any, Mapping


STATE_VERSION = "TC-P5-v1"
_ALLOWED_AVAILABILITY = {"OBSERVED", "NOT_PROVIDED", "AMBIGUOUS", "NOT_APPLICABLE"}


class StateEvaluationError(Exception):
    """Base class for TC production state-evaluation failures."""


class StateInputError(StateEvaluationError, ValueError):
    """Raised when Raw/Mapping inputs do not represent the same valid record."""


class TradeState(str, Enum):
    WAIT = "WAIT"
    ACTIONABLE = "ACTIONABLE"
    INVALID = "INVALID"
    UNDETERMINED = "UNDETERMINED"


def _raw_ref(record_id: str, start: int, end: int) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "pointer": "/parsed_analysis/observations",
        "character_span": {"start": start, "end": end},
    }


def _match_items(text: str, record_id: str, patterns: tuple[str, ...]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if "value" in match.groupdict():
                start, end = match.span("value")
                value = match.group("value").strip()
            else:
                start, end = match.span(0)
                value = match.group(0).strip()
            if not value:
                continue
            if any(not (end <= a or start >= b) for a, b in occupied):
                continue
            occupied.append((start, end))
            items.append(
                {
                    "extracted_text": value,
                    "raw_reference": _raw_ref(record_id, start, end),
                }
            )
    items.sort(
        key=lambda x: (
            x["raw_reference"]["character_span"]["start"],
            x["raw_reference"]["character_span"]["end"],
        )
    )
    return items


_WAIT_PATTERNS = (
    r"(?P<value>\b(?:a|an|the)?\s*[A-Za-z0-9_-]+(?:\s+[A-Za-z0-9_-]+){0,5}\s+(?:trade|setup|entry)\s+is\s+not\s+yet\s+confirmed\b)",
    r"(?P<value>\bwait\s+(?:for|until)\b[^.!?]+)",
    r"(?P<value>\b(?:do\s+not\s+enter|avoid\s+entry|avoid\s+entering)\b[^.!?]*)",
)

_ACTIONABLE_PATTERNS = (
    r"(?P<value>\b(?:a|an|the)\s+(?:long|short)\s+position\s+is\s+recommended\s+with\s+entry\s+at\s+current\s+price\b)",
    r"(?P<value>\b(?:enter|buy|sell)\s+(?:now|at\s+current\s+price)\b[^.!?]*)",
)

_CURRENT_INVALID_PATTERNS = (
    r"(?P<value>\b(?:the\s+)?(?:setup|scenario|trade\s+plan)\s+(?:is|has\s+been)\s+(?:currently\s+)?invalid(?:ated)?\b[^.!?]*)",
    r"(?P<value>\b(?:the\s+)?(?:setup|scenario|trade\s+plan)\s+is\s+no\s+longer\s+valid\b[^.!?]*)",
)

_FUTURE_INVALIDATION_RE = re.compile(
    r"\b(?:could|would|may|might)\s+invalidate\b|\bif\b[^.!?]{0,160}\binvalidat(?:e|es)\b|\bunless\b[^.!?]{0,160}\binvalidat(?:e|es)\b",
    re.IGNORECASE,
)


def _question_mapping(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    qm = mapping.get("question_mapping")
    if not isinstance(qm, Mapping):
        raise StateInputError("mapping.question_mapping must be an object")
    return qm


def _question_status(qm: Mapping[str, Any], key: str) -> str:
    item = qm.get(key)
    status = item.get("status") if isinstance(item, Mapping) else None
    if status not in _ALLOWED_AVAILABILITY:
        raise StateInputError(f"question_mapping.{key}.status is invalid")
    return status


def _first_mapping_evidence(qm: Mapping[str, Any], key: str) -> dict[str, Any] | None:
    item = qm.get(key)
    evidence = item.get("evidence") if isinstance(item, Mapping) else None
    if not isinstance(evidence, list) or not evidence:
        return None
    first = evidence[0]
    if not isinstance(first, Mapping):
        return None
    text = first.get("extracted_value")
    raw_ref = first.get("raw_reference")
    if not isinstance(text, str) or not isinstance(raw_ref, Mapping):
        return None
    return {
        "extracted_text": text,
        "raw_reference": copy.deepcopy(dict(raw_ref)),
    }


def _normalized(qm: Mapping[str, Any], key: str, field: str) -> Any:
    item = qm.get(key)
    field_obj = item.get(field) if isinstance(item, Mapping) else None
    return field_obj.get("normalized_value") if isinstance(field_obj, Mapping) else None


def _validate_inputs(raw_record: Mapping[str, Any], mapping: Mapping[str, Any]) -> tuple[str, str]:
    if not isinstance(raw_record, Mapping):
        raise StateInputError("raw_record must be an object")
    if raw_record.get("schema_version") != "1.0.0":
        raise StateInputError("raw_record schema_version must be 1.0.0")
    parse_status = raw_record.get("parse_status")
    if not isinstance(parse_status, Mapping) or parse_status.get("state") != "PARSED":
        raise StateInputError("State evaluation requires PARSED TCTradePlanRaw")
    identity = raw_record.get("record_identity")
    if not isinstance(identity, Mapping):
        raise StateInputError("raw_record.record_identity missing")
    record_id = identity.get("record_id")
    if not isinstance(record_id, str) or not record_id:
        raise StateInputError("raw_record.record_identity.record_id missing")

    if not isinstance(mapping, Mapping):
        raise StateInputError("mapping must be an object")
    source = mapping.get("source_contract")
    if not isinstance(source, Mapping) or source.get("record_id") != record_id:
        raise StateInputError("Raw and Mapping record_id must match")
    policy = mapping.get("mapping_policy")
    if not isinstance(policy, Mapping):
        raise StateInputError("mapping.mapping_policy missing")
    if policy.get("inference") != "NO":
        raise StateInputError("mapping inference policy must remain NO")
    if policy.get("timeframe_synthesis") != "NO":
        raise StateInputError("mapping timeframe_synthesis must remain NO")

    parsed = raw_record.get("parsed_analysis")
    if not isinstance(parsed, Mapping):
        raise StateInputError("parsed_analysis missing")
    observations = parsed.get("observations")
    text = observations if isinstance(observations, str) else ""
    return record_id, text


class TCStateEvaluator:
    """TC4-6 provisional state evaluator.

    This evaluator selects only the current TC-side strategy state. It does not
    monitor price, evaluate future release/invalidation conditions, size positions,
    authorize execution, or synthesize multiple timeframes.
    """

    def evaluate(
        self,
        raw_record: Mapping[str, Any],
        mapping: Mapping[str, Any],
    ) -> dict[str, Any]:
        record_id, text = _validate_inputs(raw_record, mapping)
        qm = _question_mapping(mapping)

        question_availability = {
            key: _question_status(qm, key)
            for key in (
                "environment",
                "setup",
                "trigger",
                "entry",
                "sl",
                "tp",
                "wait",
                "invalidation",
                "alternative_scenario",
            )
        }

        wait_items = _match_items(text, record_id, _WAIT_PATTERNS)
        actionable_items = _match_items(text, record_id, _ACTIONABLE_PATTERNS)
        invalid_items = _match_items(text, record_id, _CURRENT_INVALID_PATTERNS)

        active_families = sum(
            bool(items) for items in (wait_items, actionable_items, invalid_items)
        )
        conflict = active_families > 1

        if conflict:
            state = TradeState.UNDETERMINED
            basis = "NOT_ENOUGH_EVIDENCE"
            state_evidence = wait_items + actionable_items + invalid_items
        elif invalid_items:
            state = TradeState.INVALID
            basis = "EXPLICIT_NATIVE_TEXT"
            state_evidence = invalid_items
        elif wait_items:
            state = TradeState.WAIT
            basis = "EXPLICIT_NATIVE_TEXT"
            state_evidence = wait_items
        elif actionable_items:
            state = TradeState.ACTIONABLE
            basis = "EXPLICIT_NATIVE_TEXT"
            state_evidence = actionable_items
        else:
            state = TradeState.UNDETERMINED
            basis = "NOT_ENOUGH_EVIDENCE"
            state_evidence = []

        invalidation_question = qm.get("invalidation")
        invalidation_evidence = (
            invalidation_question.get("evidence")
            if isinstance(invalidation_question, Mapping)
            else None
        )
        future_rule: dict[str, Any] | None = None
        if isinstance(invalidation_evidence, list):
            for item in invalidation_evidence:
                if not isinstance(item, Mapping):
                    continue
                extracted = item.get("extracted_value")
                raw_ref = item.get("raw_reference")
                if (
                    isinstance(extracted, str)
                    and isinstance(raw_ref, Mapping)
                    and _FUTURE_INVALIDATION_RE.search(extracted)
                ):
                    future_rule = {
                        "status": "OBSERVED",
                        "extracted_text": extracted,
                        "raw_reference": copy.deepcopy(dict(raw_ref)),
                    }
                    break

        if future_rule is None:
            invalidation_rule_out: dict[str, Any] = {
                "status": (
                    "NOT_PROVIDED"
                    if question_availability["invalidation"] == "NOT_PROVIDED"
                    else "NOT_OBSERVED"
                )
            }
        else:
            invalidation_rule_out = future_rule

        if invalid_items:
            current_invalid_out: dict[str, Any] = {
                "status": "OBSERVED",
                "evidence": copy.deepcopy(invalid_items),
            }
        else:
            current_invalid_out = {"status": "NOT_OBSERVED"}

        alt_first = _first_mapping_evidence(qm, "alternative_scenario")
        if alt_first is None:
            alt_out: dict[str, Any] = {
                "status": (
                    "NOT_PROVIDED"
                    if question_availability["alternative_scenario"] == "NOT_PROVIDED"
                    else question_availability["alternative_scenario"]
                )
            }
        else:
            alt_out = {"status": "OBSERVED", **alt_first}

        trigger_first = _first_mapping_evidence(qm, "trigger")
        if state is TradeState.WAIT and trigger_first is not None:
            release_text = trigger_first["extracted_text"]
            release_text = re.sub(r"^\s*wait\s+for\s+", "", release_text, flags=re.IGNORECASE)
            wait_release_out: dict[str, Any] = {
                "status": "OBSERVED",
                "extracted_text": release_text,
                "raw_reference": trigger_first["raw_reference"],
                "runtime_evaluation": "NOT_IMPLEMENTED",
            }
        elif state is TradeState.WAIT:
            wait_release_out = {
                "status": "NOT_PROVIDED",
                "runtime_evaluation": "NOT_IMPLEMENTED",
            }
        else:
            wait_release_out = {
                "status": "NOT_APPLICABLE",
                "runtime_evaluation": "NOT_IMPLEMENTED",
            }

        if wait_items:
            wait_out: dict[str, Any] = {
                "status": "OBSERVED",
                "evidence": copy.deepcopy(wait_items),
            }
        else:
            wait_out = {"status": "NOT_OBSERVED"}

        plan_axis = {
            "entry_direction": _normalized(qm, "entry", "direction"),
            "entry_price": _normalized(qm, "entry", "price"),
            "stop_loss": _normalized(qm, "sl", "price"),
            "take_profits": _normalized(qm, "tp", "targets"),
        }

        return {
            "state_version": STATE_VERSION,
            "source": {
                "record_id": record_id,
                "timeframe": mapping["source_contract"].get("timeframe"),
            },
            "question_availability": question_availability,
            "plan_axis": plan_axis,
            "trade_state": {
                "model_status": "PROVISIONAL_TC",
                "value": state.value,
                "semantic_basis": basis,
                "evidence": copy.deepcopy(state_evidence),
                "wait_evidence": wait_out,
                "wait_release_condition_evidence": wait_release_out,
                "invalidation_rule_evidence": invalidation_rule_out,
                "current_invalid_evidence": current_invalid_out,
                "alternative_scenario_evidence": alt_out,
                "conflict_preserved": conflict,
            },
            "guardrails": {
                "entry_sl_tp_implies_actionable": False,
                "missing_trigger_implies_wait": False,
                "invalidation_rule_implies_current_invalid": False,
                "current_price_compared_to_invalidation_rule": False,
                "actionable_authorizes_execution": False,
                "alternative_scenario_implies_wait": False,
                "alternative_scenario_implies_invalid": False,
                "direction_and_state_are_same_axis": False,
                "environment_determines_state": False,
                "setup_determines_state": False,
                "runtime_wait_release_evaluator": False,
                "runtime_invalidation_evaluator": False,
                "timeframe_synthesis": False,
                "inference": "NO",
            },
        }
