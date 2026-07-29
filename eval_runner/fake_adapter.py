"""Deterministic fake adapter for unit and CI testing without model credentials."""

from __future__ import annotations

import time

from .models import AdapterInput, AdapterOutput, ExitStatus, ToolEvent


class FakeAdapter:
    """Returns canned responses derived from the case prompt.

    Behavior is fully deterministic: the response echoes the case ID, tool
    events are synthesized from the assertion count, and timing is fixed.
    Useful for validating the runner pipeline, manifest serialization, and
    grader bindings without any external dependencies.
    """

    @property
    def name(self) -> str:
        return "fake"

    @property
    def version(self) -> str:
        return "0.1.0"

    def execute(self, input: AdapterInput) -> AdapterOutput:
        start = time.monotonic()

        case = input.case
        response = f"[fake] Processed case '{case.id}': {case.prompt[:80]}"
        activation_evidence = f"skill loaded from {input.skill_path.name}/SKILL.md"

        tool_events = [
            ToolEvent(
                name="read_file",
                arguments={"path": f"{input.skill_path.name}/SKILL.md"},
                result_summary="skill content loaded",
                timestamp="2025-01-01T00:00:00Z",
            ),
        ]
        for i, assertion in enumerate(case.assertions):
            tool_events.append(
                ToolEvent(
                    name="assert_check",
                    arguments={"index": i, "assertion": assertion[:60]},
                    result_summary="pass",
                    timestamp="2025-01-01T00:00:00Z",
                )
            )

        elapsed_ms = (time.monotonic() - start) * 1000

        return AdapterOutput(
            exit_status=ExitStatus.COMPLETED,
            response=response,
            activation_evidence=activation_evidence,
            artifacts=[],
            environment_state={"work_dir": str(input.work_dir)},
            tool_events=tool_events,
            duration_ms=elapsed_ms,
            token_usage={"input_tokens": 100, "output_tokens": 50},
            raw_trace_path=None,
            error=None,
        )
