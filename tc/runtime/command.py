from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

COMMAND_CONTRACT_VERSION = "TC_SPOT_COMMAND_V1"
STANDARD_ENTRY_PRE_TIMEFRAMES: Tuple[str, ...] = ("D1", "H4", "H1", "M15")


class CommandParseError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class TCSpotRuntimeRequest:
    raw_command: str
    engine_mode: str
    run_mode: str
    user_symbol: str
    evaluation_mode: str
    timeframes: Tuple[str, ...]
    command_contract_version: str = COMMAND_CONTRACT_VERSION


def parse_spot_command(command: str) -> TCSpotRuntimeRequest:
    if not isinstance(command, str) or not command.strip():
        raise CommandParseError("COMMAND_EMPTY", "command must be a non-empty string")
    tokens = command.strip().split()
    if len(tokens) != 4:
        raise CommandParseError("COMMAND_SHAPE_INVALID", "expected: tc スポット <symbol> エントリー前")
    engine, run_mode, user_symbol, evaluation = tokens
    if engine.casefold() != "tc":
        raise CommandParseError("ENGINE_UNSUPPORTED", "engine token must be TC")
    if run_mode != "スポット":
        raise CommandParseError("RUN_MODE_UNSUPPORTED", "run mode must be スポット")
    if evaluation != "エントリー前":
        raise CommandParseError("EVALUATION_MODE_UNSUPPORTED", "evaluation mode must be エントリー前")
    return TCSpotRuntimeRequest(
        raw_command=command,
        engine_mode="TC",
        run_mode="SPOT",
        user_symbol=user_symbol,
        evaluation_mode="ENTRY_PRE",
        timeframes=STANDARD_ENTRY_PRE_TIMEFRAMES,
    )
