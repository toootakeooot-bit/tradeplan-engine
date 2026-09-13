from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

COMMAND_CONTRACT_VERSION = "TC_SPOT_COMMAND_V2"

PROFILE_SPECS = {
    "NORMAL": {
        "initial_timeframes": ("D1", "H4", "H1"),
        "environment_tf": "D1",
        "setup_tf": "H4",
        "decision_tf": "H1",
        "optional_drilldown_tf": "M15",
    },
    "SHORT": {
        "initial_timeframes": ("H4", "H1", "M15"),
        "environment_tf": "H4",
        "setup_tf": "H1",
        "decision_tf": "M15",
        "optional_drilldown_tf": None,
    },
}

PROFILE_TOKENS = {
    "通常": "NORMAL",
    "短期": "SHORT",
}


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
    profile: str
    initial_timeframes: Tuple[str, ...]
    environment_tf: str
    setup_tf: str
    decision_tf: str
    optional_drilldown_tf: Optional[str]
    command_contract_version: str = COMMAND_CONTRACT_VERSION


def parse_spot_command(command: str) -> TCSpotRuntimeRequest:
    if not isinstance(command, str) or not command.strip():
        raise CommandParseError("COMMAND_EMPTY", "command must be a non-empty string")

    tokens = command.strip().split()
    if len(tokens) == 4:
        engine, run_mode, user_symbol, evaluation = tokens
        profile = "NORMAL"
    elif len(tokens) == 5:
        engine, run_mode, user_symbol, profile_token, evaluation = tokens
        try:
            profile = PROFILE_TOKENS[profile_token]
        except KeyError as exc:
            raise CommandParseError(
                "PROFILE_UNSUPPORTED",
                "profile token must be 通常 or 短期",
            ) from exc
    else:
        raise CommandParseError(
            "COMMAND_SHAPE_INVALID",
            "expected: tc スポット <symbol> [通常|短期] エントリー前",
        )

    if engine.casefold() != "tc":
        raise CommandParseError("ENGINE_UNSUPPORTED", "engine token must be TC")
    if run_mode != "スポット":
        raise CommandParseError("RUN_MODE_UNSUPPORTED", "run mode must be スポット")
    if evaluation != "エントリー前":
        raise CommandParseError("EVALUATION_MODE_UNSUPPORTED", "evaluation mode must be エントリー前")

    spec = PROFILE_SPECS[profile]
    return TCSpotRuntimeRequest(
        raw_command=command,
        engine_mode="TC",
        run_mode="SPOT",
        user_symbol=user_symbol,
        evaluation_mode="ENTRY_PRE",
        profile=profile,
        initial_timeframes=spec["initial_timeframes"],
        environment_tf=spec["environment_tf"],
        setup_tf=spec["setup_tf"],
        decision_tf=spec["decision_tf"],
        optional_drilldown_tf=spec["optional_drilldown_tf"],
    )
