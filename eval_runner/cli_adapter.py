"""Subprocess-based adapter for non-interactive CLI agent harnesses.

Executes a configurable command with the case prompt piped to stdin or passed
as an argument. Captures stdout as the response, stderr for diagnostics, and
records exit code, timing, and any artifacts produced in the output directory.

This is the first real harness adapter. It supports any agent CLI that can:
  - accept a prompt non-interactively (via stdin or --prompt flag)
  - write its response to stdout
  - operate within a working directory

Configuration via harness_config:
  command: list[str]  — the command to run (e.g. ["opencode", "--print"])
  prompt_mode: "stdin" | "arg"  — how to pass the prompt (default: "stdin")
  prompt_flag: str  — flag name if prompt_mode is "arg" (default: "--prompt")
  timeout_seconds: int  — max wall time (default: 120)
  extra_args: list[str]  — additional CLI arguments
"""

from __future__ import annotations

import os
import subprocess
import time

from .models import AdapterInput, AdapterOutput, ExitStatus, ToolEvent


class CliSubprocessAdapter:
    """Runs an agent CLI as a subprocess and normalizes the result."""

    def __init__(
        self,
        command: list[str],
        *,
        prompt_mode: str = "stdin",
        prompt_flag: str = "--prompt",
        timeout_seconds: int = 120,
        extra_args: list[str] | None = None,
    ):
        self._command = command
        self._prompt_mode = prompt_mode
        self._prompt_flag = prompt_flag
        self._timeout_seconds = timeout_seconds
        self._extra_args = extra_args or []

    @property
    def name(self) -> str:
        return "cli-subprocess"

    @property
    def version(self) -> str:
        return "0.1.0"

    def execute(self, input: AdapterInput) -> AdapterOutput:
        timeout = input.limits.get("timeout_seconds", self._timeout_seconds)
        cmd = list(self._command) + list(self._extra_args)

        stdin_data: str | None = None
        if self._prompt_mode == "stdin":
            stdin_data = input.case.prompt
        elif self._prompt_mode == "arg":
            cmd += [self._prompt_flag, input.case.prompt]

        env = dict(os.environ)
        env.update(input.env)

        input.work_dir.mkdir(parents=True, exist_ok=True)
        input.output_dir.mkdir(parents=True, exist_ok=True)

        start = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(input.work_dir),
                env=env,
            )
            elapsed_ms = (time.monotonic() - start) * 1000

            exit_status = ExitStatus.COMPLETED if proc.returncode == 0 else ExitStatus.ERROR

            artifacts = [f.name for f in input.output_dir.iterdir() if f.is_file()]

            tool_events = []
            if proc.stderr:
                tool_events.append(
                    ToolEvent(
                        name="subprocess_stderr",
                        arguments={"command": " ".join(cmd)},
                        result_summary=proc.stderr[:500],
                    )
                )

            return AdapterOutput(
                exit_status=exit_status,
                response=proc.stdout or None,
                activation_evidence=None,
                artifacts=artifacts,
                environment_state={"returncode": proc.returncode},
                tool_events=tool_events,
                duration_ms=elapsed_ms,
                token_usage=None,
                raw_trace_path=None,
                error=proc.stderr[:1000] if proc.returncode != 0 else None,
            )

        except subprocess.TimeoutExpired:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.TIMEOUT,
                response=None,
                error=f"process exceeded {timeout}s timeout",
                duration_ms=elapsed_ms,
            )
        except FileNotFoundError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.ERROR,
                response=None,
                error=f"command not found: {exc}",
                duration_ms=elapsed_ms,
            )
