"""Typed data models for the eval runner adapter contract."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .path_safety import hash_contained_file, validate_case_id, validate_relative_path


class ExitStatus(str, Enum):
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"
    STOPPED = "stopped"


@dataclass(frozen=True)
class EvalCase:
    id: str
    prompt: str
    expected_output: str
    assertions: list[str]
    files: list[str] = field(default_factory=list)
    case_set: str = "dev"

    def __post_init__(self) -> None:
        validate_case_id(self.id)
        if len(self.files) != len(set(self.files)):
            raise ValueError("eval case fixture paths must be unique")
        for relative_path in self.files:
            validate_relative_path(relative_path)

    @property
    def prompt_hash(self) -> str:
        return hashlib.sha256(self.prompt.encode()).hexdigest()[:16]

    def fixture_hashes(self, skill_root: Path) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for rel in self.files:
            hashes[rel] = hash_contained_file(skill_root, rel) or "missing"
        return hashes


@dataclass
class AdapterInput:
    skill_path: Path
    case: EvalCase
    work_dir: Path
    output_dir: Path
    permissions: dict[str, Any] = field(default_factory=dict)
    limits: dict[str, Any] = field(default_factory=dict)
    env: dict[str, str] = field(default_factory=dict)
    model: str = ""
    harness_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolEvent:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    result_summary: str = ""
    timestamp: str = ""


@dataclass
class AdapterOutput:
    exit_status: ExitStatus
    response: str | None = None
    activation_evidence: str | None = None
    artifacts: list[str] = field(default_factory=list)
    environment_state: dict[str, Any] | None = None
    tool_events: list[ToolEvent] = field(default_factory=list)
    duration_ms: float = 0.0
    token_usage: dict[str, Any] | None = None
    raw_trace_path: str | None = None
    error: str | None = None

    def missing_evidence(self) -> list[str]:
        missing: list[str] = []
        if self.response is None:
            missing.append("response")
        if self.activation_evidence is None:
            missing.append("activation_evidence")
        if self.environment_state is None:
            missing.append("environment_state")
        if self.token_usage is None:
            missing.append("token_usage")
        if not self.tool_events:
            missing.append("tool_events")
        return missing
