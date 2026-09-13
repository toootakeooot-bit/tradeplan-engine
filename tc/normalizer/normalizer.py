from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True)
class NormalizedTCState:
    record_id: str
    timeframe: str
    environment_direction: Optional[str]
    setup_evidence: Optional[str]
    trigger_evidence: Optional[str]
    entry_direction: Optional[str]
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profits: Tuple[float, ...]
    trade_state: str
    state_basis: str
    wait_evidence: Optional[str]
    invalidation_evidence: Optional[str]
    alternative_scenario_evidence: Optional[str]
    lower_tf_confirmation_required: bool


_WAIT_PATTERNS = (
    r"\bwait for confirmation\b",
    r"\bwait for (?:a |the )?breakout\b",
    r"\bshould wait\b",
    r"\bnot yet confirmed\b",
    r"\bavoid (?:entry|entering)\b",
    r"\bconfirmation is still pending\b",
)

_ACTIONABLE_PATTERNS = (
    r"\b(?:a |the )?(?:long|short) position (?:is )?recommended with entry at (?:the )?current price\b",
    r"\bentry at current price\b",
    r"\benter (?:long|short) now\b",
)

_INVALID_CURRENT_PATTERNS = (
    r"\bsetup is invalid\b",
    r"\bsetup has been invalidated\b",
    r"\bscenario is invalid\b",
    r"\btrade is no longer valid\b",
)

_LOWER_TF_PATTERNS = (
    r"\blower[- ]timeframe confirmation\b",
    r"\blower timeframe confirmation\b",
    r"\bconfirm on (?:the )?(?:15m|15-minute|lower timeframe)\b",
)

_TRIGGER_PATTERNS = (
    r"\bbreakout above [^.]+",
    r"\bbreakdown below [^.]+",
    r"\bclosing candle above/below [^.]+",
    r"\bclose above [^.]+",
    r"\bclose below [^.]+",
)


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _first_match(text: str, patterns: tuple[str, ...]) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _position(parsed: Mapping[str, Any]) -> Mapping[str, Any]:
    value = parsed.get("potentialPosition")
    return value if isinstance(value, Mapping) else {}


def _float_or_none(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _take_profits(value: Any) -> Tuple[float, ...]:
    if not isinstance(value, list):
        return ()
    result = []
    for item in value:
        numeric = _float_or_none(item)
        if numeric is not None:
            result.append(numeric)
    return tuple(result)


def _entry_direction(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized if normalized in {"LONG", "SHORT"} else None


def normalize_tc_raw(raw: Mapping[str, Any]) -> NormalizedTCState:
    """Project TCTradePlanRaw into a conservative provisional TC state.

    EXTRACT = YES, LIGHT_NORMALIZATION = YES, INFERENCE = NO.
    Unknown/unrecognized wording becomes UNDETERMINED rather than a guessed state.
    """
    record_identity = raw.get("record_identity")
    wrapper = raw.get("wrapper_metadata")
    parsed = raw.get("parsed_analysis")
    parse_status = raw.get("parse_status")

    if not isinstance(record_identity, Mapping) or not record_identity.get("record_id"):
        raise ValueError("record_identity.record_id is required")
    if not isinstance(wrapper, Mapping) or not wrapper.get("timeframe"):
        raise ValueError("wrapper_metadata.timeframe is required")
    if not isinstance(parse_status, Mapping) or parse_status.get("state") != "PARSED":
        raise ValueError("TCTradePlanRaw must be PARSED for normalization")
    if not isinstance(parsed, Mapping):
        raise ValueError("parsed_analysis is required for PARSED normalization")

    observations = _text(parsed.get("observations"))
    position = _position(parsed)
    future = parsed.get("futureAssumption")
    future = future if isinstance(future, Mapping) else {}

    wait_evidence = _first_match(observations, _WAIT_PATTERNS)
    actionable_evidence = _first_match(observations, _ACTIONABLE_PATTERNS)
    current_invalid_evidence = _first_match(observations, _INVALID_CURRENT_PATTERNS)
    lower_tf_required = _first_match(observations, _LOWER_TF_PATTERNS) is not None

    if current_invalid_evidence and not wait_evidence and not actionable_evidence:
        trade_state = "INVALID"
        state_basis = "EXPLICIT_NATIVE_TEXT"
    elif wait_evidence and not current_invalid_evidence:
        trade_state = "WAIT"
        state_basis = "EXPLICIT_NATIVE_TEXT"
    elif actionable_evidence and not current_invalid_evidence and not wait_evidence:
        trade_state = "ACTIONABLE"
        state_basis = "EXPLICIT_NATIVE_TEXT"
    else:
        trade_state = "UNDETERMINED"
        state_basis = "NOT_ENOUGH_EVIDENCE"

    trigger_evidence = _first_match(observations, _TRIGGER_PATTERNS)

    setup_evidence = None
    if re.search(r"\b(setup|reversal|breakout strategy|breakout is pending|range-bound strategy)\b", observations, re.IGNORECASE):
        setup_evidence = observations

    invalidation_evidence = None
    invalidation_match = re.search(
        r"(?:if|a) [^.]{0,120}(?:invalidate|invalidated|setup may fail|setup could fail)[^.]*",
        observations,
        flags=re.IGNORECASE,
    )
    if invalidation_match:
        invalidation_evidence = invalidation_match.group(0)

    alternative_evidence = None
    alternative_match = re.search(r"alternative scenario:[^.]+", observations, flags=re.IGNORECASE)
    if alternative_match:
        alternative_evidence = alternative_match.group(0)

    return NormalizedTCState(
        record_id=str(record_identity["record_id"]),
        timeframe=str(wrapper["timeframe"]),
        environment_direction=_text(future.get("trend")) or None,
        setup_evidence=setup_evidence,
        trigger_evidence=trigger_evidence,
        entry_direction=_entry_direction(position.get("positionType")),
        entry_price=_float_or_none(position.get("entryPrice")),
        stop_loss=_float_or_none(position.get("stopLoss")),
        take_profits=_take_profits(position.get("takeProfits")),
        trade_state=trade_state,
        state_basis=state_basis,
        wait_evidence=wait_evidence,
        invalidation_evidence=invalidation_evidence,
        alternative_scenario_evidence=alternative_evidence,
        lower_tf_confirmation_required=lower_tf_required,
    )
