from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from typing import Any, Mapping


AVAILABILITY = {"OBSERVED", "NOT_PROVIDED", "AMBIGUOUS", "NOT_APPLICABLE"}
MAPPING_VERSION = "TC-P4-v1"


class MapperError(Exception):
    """Base class for TC production Mapper failures."""


class MapperInputError(MapperError, ValueError):
    """Raised when the supplied Raw record is structurally unsuitable for mapping."""


class MapperUnavailableError(MapperError):
    """Raised when parsed Native evidence is unavailable due to an upstream condition."""


@dataclass(frozen=True, slots=True)
class TextEvidence:
    extracted_value: str
    start: int
    end: int


def _raw_ref(record_id: str, pointer: str, *, span: tuple[int, int] | None = None) -> dict[str, Any]:
    ref: dict[str, Any] = {"record_id": record_id, "pointer": pointer}
    if span is not None:
        ref["character_span"] = {"start": span[0], "end": span[1]}
    return ref


def _mapped_value(record_id: str, pointer: str, native: Any, normalized: Any, mapping_type: str) -> dict[str, Any]:
    return {
        "native_value": copy.deepcopy(native),
        "normalized_value": copy.deepcopy(normalized),
        "mapping_type": mapping_type,
        "raw_reference": _raw_ref(record_id, pointer),
    }


def _empty_question(question_id: str) -> dict[str, Any]:
    return {"question_id": question_id, "status": "NOT_PROVIDED"}


def _evidence_item(record_id: str, evidence: TextEvidence) -> dict[str, Any]:
    return {
        "extracted_value": evidence.extracted_value,
        "mapping_type": "TEXT_EXTRACT",
        "raw_reference": _raw_ref(
            record_id,
            "/parsed_analysis/observations",
            span=(evidence.start, evidence.end),
        ),
    }


def _sentence_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    start = 0
    for match in re.finditer(r"[.!?](?:\s+|$)", text):
        end = match.start() + 1
        segment = text[start:end].strip()
        if segment:
            seg_start = text.find(segment, start, end + 1)
            spans.append((seg_start, seg_start + len(segment), segment))
        start = match.end()
    tail = text[start:].strip()
    if tail:
        seg_start = text.find(tail, start)
        spans.append((seg_start, seg_start + len(tail), tail))
    return spans


def _find_first_regex(text: str, patterns: tuple[str, ...], flags: int = re.IGNORECASE) -> TextEvidence | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            value = match.group("value") if "value" in match.groupdict() else match.group(0)
            start, end = match.span("value") if "value" in match.groupdict() else match.span(0)
            return TextEvidence(value.strip(), start, end)
    return None


def _find_sentence_with_keywords(text: str, *, required: tuple[str, ...], any_of: tuple[str, ...] = ()) -> TextEvidence | None:
    for start, end, sentence in _sentence_spans(text):
        lowered = sentence.lower()
        if not all(token in lowered for token in required):
            continue
        if any_of and not any(token in lowered for token in any_of):
            continue
        return TextEvidence(sentence, start, end)
    return None


def _extract_setup(text: str) -> tuple[str, list[TextEvidence]]:
    exact = _find_first_regex(
        text,
        (
            r"(?P<value>\b(?:a|an|the)\s+[A-Za-z0-9_-]+(?:\s+[A-Za-z0-9_-]+){0,4}\s+trade\s+is\s+not\s+yet\s+confirmed\b)",
        ),
    )
    if exact:
        return "OBSERVED", [exact]
    sentence = _find_sentence_with_keywords(text, required=("setup",))
    if sentence:
        return "OBSERVED", [sentence]
    if re.search(r"\b(?:setup|trade candidate)\b", text, re.IGNORECASE) and re.search(
        r"\b(?:unclear|ambiguous|conflicting)\b", text, re.IGNORECASE
    ):
        return "AMBIGUOUS", []
    return "NOT_PROVIDED", []


def _extract_trigger(text: str) -> tuple[str, list[TextEvidence]]:
    trigger = _find_first_regex(
        text,
        (
            r"(?P<value>\bwait\s+for\s+a\s+decisive\s+break\s+above\s+[-+]?\d+(?:\.\d+)?\s+with\s+volume\s+confirmation\s+for\s+a\s+long,\s+or\s+below\s+[-+]?\d+(?:\.\d+)?\s+for\s+a\s+short\b)",
            r"(?P<value>\b(?:entry|enter)\s+only\s+(?:if|when|after)\b[^.!?]+)",
            r"(?P<value>\bonly\s+enter\s+(?:if|when|after)\b[^.!?]+)",
        ),
    )
    if trigger:
        return "OBSERVED", [trigger]
    if re.search(r"\b(?:trigger|entry condition|activation)\b", text, re.IGNORECASE) and re.search(
        r"\b(?:unclear|ambiguous|conflicting)\b", text, re.IGNORECASE
    ):
        return "AMBIGUOUS", []
    return "NOT_PROVIDED", []


def _extract_wait(text: str) -> tuple[str, list[TextEvidence]]:
    wait = _find_first_regex(
        text,
        (
            r"(?P<value>\bA\s+conservative\s+approach\s+would\s+be\s+to\s+wait\s+for\s+a\s+decisive\s+break\s+above\s+[-+]?\d+(?:\.\d+)?\s+with\s+volume\s+confirmation\b)",
            r"(?P<value>\bwait\s+(?:for|until)\b[^.!?]+)",
            r"(?P<value>\b(?:do\s+not\s+enter|avoid\s+entry|avoid\s+entering)\b[^.!?]*)",
        ),
    )
    if wait:
        return "OBSERVED", [wait]
    if re.search(r"\bwait\b", text, re.IGNORECASE) and re.search(
        r"\b(?:unclear|ambiguous|conflicting)\b", text, re.IGNORECASE
    ):
        return "AMBIGUOUS", []
    return "NOT_PROVIDED", []


def _extract_invalidation(text: str) -> tuple[str, list[TextEvidence]]:
    invalidation = _find_first_regex(
        text,
        (
            r"(?P<value>\b(?:a\s+)?break\s+below\s+[-+]?\d+(?:\.\d+)?\s+could\s+invalidate\s+the\s+[^.!?]+?setup\b)",
            r"(?P<value>\b[^.!?]*\binvalidat(?:e|es|ed|ion)\b[^.!?]*)",
            r"(?P<value>\b[^.!?]*\bno\s+longer\s+valid\b[^.!?]*)",
        ),
    )
    if invalidation:
        return "OBSERVED", [invalidation]
    return "NOT_PROVIDED", []


def _extract_alternative(text: str) -> tuple[str, list[TextEvidence]]:
    alt = _find_first_regex(
        text,
        (
            r"(?P<value>\bbelow\s+[-+]?\d+(?:\.\d+)?\s+for\s+a\s+short\b)",
            r"(?P<value>\bAlternative\s+scenario:\s*[^.!?]+)",
            r"(?P<value>\balternative\s+scenario\b[^.!?]*)",
        ),
    )
    if alt:
        return "OBSERVED", [alt]
    return "NOT_PROVIDED", []


def _extract_sl_rationale(text: str) -> tuple[str, list[TextEvidence]]:
    evidence = _find_sentence_with_keywords(text, required=("stop loss",), any_of=("at ", "below", "above"))
    return ("OBSERVED", [evidence]) if evidence else ("NOT_PROVIDED", [])


def _extract_tp_rationale(text: str) -> tuple[str, list[TextEvidence]]:
    evidence = _find_sentence_with_keywords(text, required=("take profit",))
    return ("OBSERVED", [evidence]) if evidence else ("NOT_PROVIDED", [])


def _text_question(record_id: str, question_id: str, status: str, evidence: list[TextEvidence]) -> dict[str, Any]:
    if status not in AVAILABILITY:
        raise AssertionError(f"invalid availability status: {status}")
    return {
        "question_id": question_id,
        "status": status,
        "evidence": [_evidence_item(record_id, item) for item in evidence],
    }


def _ensure_raw_input(raw_record: Mapping[str, Any]) -> tuple[str, Mapping[str, Any], str]:
    if not isinstance(raw_record, Mapping):
        raise MapperInputError("raw_record must be a mapping")
    if raw_record.get("schema_version") != "1.0.0":
        raise MapperInputError("TCTradePlanRaw schema_version must be 1.0.0")
    identity = raw_record.get("record_identity")
    if not isinstance(identity, Mapping):
        raise MapperInputError("record_identity must be present")
    record_id = identity.get("record_id")
    if not isinstance(record_id, str) or not record_id:
        raise MapperInputError("record_identity.record_id must be non-empty")
    parse_status = raw_record.get("parse_status")
    state = parse_status.get("state") if isinstance(parse_status, Mapping) else None
    if state != "PARSED":
        raise MapperUnavailableError(
            f"parsed_analysis unavailable for mapping; parse_status={state!r}"
        )
    parsed = raw_record.get("parsed_analysis")
    if not isinstance(parsed, Mapping):
        raise MapperInputError("PARSED raw_record requires parsed_analysis object")
    original = raw_record.get("original_response")
    timeframe = original.get("interval") if isinstance(original, Mapping) else None
    if not isinstance(timeframe, str) or not timeframe:
        timeframe = "UNKNOWN"
    return record_id, parsed, timeframe


class TCMapper:
    """Deterministic TCTradePlanRaw -> provisional TradePlanState mapper."""

    def map_record(self, raw_record: Mapping[str, Any]) -> dict[str, Any]:
        record_id, parsed, timeframe = _ensure_raw_input(raw_record)
        identity = raw_record["record_identity"]

        output: dict[str, Any] = {
            "mapping_version": MAPPING_VERSION,
            "source_contract": {
                "input_type": "TCTradePlanRaw",
                "schema_version": "1.0.0",
                "record_id": record_id,
                "source_artifact": identity.get("source_raw_artifact"),
                "timeframe": timeframe,
            },
            "mapping_policy": {
                "operations": ["DIRECT", "LIGHT_NORMALIZATION", "TEXT_EXTRACT"],
                "inference": "NO",
                "trade_state_semantics": "NOT_EVALUATED_TC_P4",
                "timeframe_synthesis": "NO",
            },
            "question_mapping": {},
            "excluded_or_deferred": {
                "indicatorReadings": "NOT_MAPPED",
                "priceMetrics": "TBD_COMMON_ADOPTION",
                "futureAssumption.confidenceScore": "TC_NATIVE_ONLY_OR_TBD",
                "futureAssumption.patternDetected": "TBD_COMMON_ADOPTION",
                "position_sizing_text": "EXCLUDED_OUT_OF_SCOPE",
                "risk_reward": "TBD",
                "structured_text_conflict_resolution": "TBD",
            },
        }
        qm: dict[str, Any] = output["question_mapping"]

        environment = _empty_question("Q1")
        assumption = parsed.get("futureAssumption")
        if isinstance(assumption, Mapping):
            trend = assumption.get("trend")
            if isinstance(trend, str) and trend:
                environment = {
                    "question_id": "Q1",
                    "status": "OBSERVED",
                    "direction": _mapped_value(
                        record_id,
                        "/parsed_analysis/futureAssumption/trend",
                        trend,
                        trend,
                        "DIRECT",
                    ),
                }
        qm["environment"] = environment

        observations = parsed.get("observations")
        observation_text = observations if isinstance(observations, str) else ""

        setup_status, setup_ev = _extract_setup(observation_text)
        qm["setup"] = _text_question(record_id, "Q2", setup_status, setup_ev)

        trigger_status, trigger_ev = _extract_trigger(observation_text)
        qm["trigger"] = _text_question(record_id, "Q3", trigger_status, trigger_ev)

        entry = _empty_question("Q4")
        position = parsed.get("potentialPosition")
        if isinstance(position, Mapping):
            entry_fields: dict[str, Any] = {"question_id": "Q4"}
            ambiguity = False
            mapped_any = False
            if "positionType" in position:
                native_direction = position.get("positionType")
                if isinstance(native_direction, str) and native_direction:
                    lowered = native_direction.lower()
                    if lowered in {"long", "short"}:
                        entry_fields["direction"] = _mapped_value(
                            record_id,
                            "/parsed_analysis/potentialPosition/positionType",
                            native_direction,
                            lowered.upper(),
                            "LIGHT_NORMALIZATION",
                        )
                        mapped_any = True
                    else:
                        ambiguity = True
            if "entryPrice" in position:
                price = position.get("entryPrice")
                if isinstance(price, (int, float)) and not isinstance(price, bool):
                    entry_fields["price"] = _mapped_value(
                        record_id,
                        "/parsed_analysis/potentialPosition/entryPrice",
                        price,
                        price,
                        "DIRECT",
                    )
                    mapped_any = True
                else:
                    ambiguity = True
            entry_fields["status"] = "AMBIGUOUS" if ambiguity else ("OBSERVED" if mapped_any else "NOT_PROVIDED")
            entry = entry_fields
        qm["entry"] = entry

        sl = _empty_question("Q5")
        if isinstance(position, Mapping) and "stopLoss" in position:
            stop = position.get("stopLoss")
            if isinstance(stop, (int, float)) and not isinstance(stop, bool):
                sl = {
                    "question_id": "Q5",
                    "status": "OBSERVED",
                    "price": _mapped_value(
                        record_id,
                        "/parsed_analysis/potentialPosition/stopLoss",
                        stop,
                        stop,
                        "DIRECT",
                    ),
                }
            else:
                sl = {"question_id": "Q5", "status": "AMBIGUOUS"}
        _, sl_ev = _extract_sl_rationale(observation_text)
        if sl_ev:
            sl["evidence"] = [_evidence_item(record_id, item) for item in sl_ev]
        qm["sl"] = sl

        tp = _empty_question("Q6")
        if isinstance(position, Mapping) and "takeProfits" in position:
            targets = position.get("takeProfits")
            if isinstance(targets, list) and all(
                isinstance(item, (int, float)) and not isinstance(item, bool) for item in targets
            ):
                tp = {
                    "question_id": "Q6",
                    "status": "OBSERVED",
                    "targets": _mapped_value(
                        record_id,
                        "/parsed_analysis/potentialPosition/takeProfits",
                        targets,
                        targets,
                        "DIRECT",
                    ),
                }
            else:
                tp = {"question_id": "Q6", "status": "AMBIGUOUS"}
        _, tp_ev = _extract_tp_rationale(observation_text)
        if tp_ev:
            tp["evidence"] = [_evidence_item(record_id, item) for item in tp_ev]
        qm["tp"] = tp

        wait_status, wait_ev = _extract_wait(observation_text)
        qm["wait"] = _text_question(record_id, "Q7", wait_status, wait_ev)

        invalid_status, invalid_ev = _extract_invalidation(observation_text)
        qm["invalidation"] = _text_question(record_id, "Q7", invalid_status, invalid_ev)

        alt_status, alt_ev = _extract_alternative(observation_text)
        qm["alternative_scenario"] = _text_question(record_id, "Q7", alt_status, alt_ev)

        return output
