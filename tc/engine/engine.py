from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tc.adapter import RawPreserver, TCAdapter
from tc.native.client import NativeClient, NativeRequest
from tc.normalizer import TCMapper
from tc.state import TCStateEvaluator


ENGINE_VERSION = "TC-P5-v1"


@dataclass(frozen=True, slots=True)
class TCEngineResult:
    raw_record: dict[str, Any]
    mapping: dict[str, Any]
    state: dict[str, Any]


class TCEngine:
    """Thin production composition facade for one TC timeframe.

    No 4TF synthesis, sizing, execution, A/W8/W9 logic, or NODA logic exists here.
    """

    def __init__(
        self,
        native_client: NativeClient,
        preserver: RawPreserver,
        *,
        mapper: TCMapper | None = None,
        evaluator: TCStateEvaluator | None = None,
    ) -> None:
        if not isinstance(native_client, NativeClient):
            raise TypeError("native_client must be NativeClient")
        self._adapter = TCAdapter(native_client, preserver)
        self._mapper = mapper or TCMapper()
        self._evaluator = evaluator or TCStateEvaluator()

    def analyze(self, request: NativeRequest) -> TCEngineResult:
        raw_record = self._adapter.analyze(request).raw_record
        mapping = self._mapper.map_record(raw_record)
        state = self._evaluator.evaluate(raw_record, mapping)
        return TCEngineResult(
            raw_record=raw_record,
            mapping=mapping,
            state=state,
        )
