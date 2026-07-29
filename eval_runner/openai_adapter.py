"""OpenAI-compatible API adapter for paired skill evaluation.

Sends the case prompt to an OpenAI-compatible chat completions endpoint.
When a skill is present (SKILL.md exists in skill_path), its content is
injected as a system message. The baseline condition (empty skill_path)
sends only the user prompt.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .models import AdapterInput, AdapterOutput, ExitStatus, ToolEvent


class OpenAICompatAdapter:
    """Adapter for OpenAI-compatible API endpoints (vLLM, llama.cpp, etc.)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        timeout_seconds: int = 120,
        api_key: str | None = None,
        max_skill_chars: int | None = None,
        chat_template_kwargs: dict[str, Any] | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._timeout_seconds = timeout_seconds
        self._api_key = api_key
        self._max_skill_chars = max_skill_chars
        self._chat_template_kwargs = chat_template_kwargs or {}

    @property
    def name(self) -> str:
        return "openai-compat"

    @property
    def version(self) -> str:
        return "0.1.0"

    def _load_skill_content(self, skill_path: Path) -> str | None:
        skill_md = skill_path / "SKILL.md"
        if skill_md.is_file():
            content = skill_md.read_text(encoding="utf-8")
            if self._max_skill_chars and len(content) > self._max_skill_chars:
                content = content[: self._max_skill_chars] + "\n[truncated]"
            return content
        return None

    def _build_messages(self, input: AdapterInput) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        skill_content = self._load_skill_content(input.skill_path)
        if skill_content:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant with expertise from the following skill. "
                        "Use the knowledge, frameworks, and methodology described in the skill "
                        "to answer the user's question directly. Do NOT show commands or scripts "
                        "to run — instead, apply the framework yourself and provide the answer "
                        "with your reasoning.\n\n"
                        f"<skill>\n{skill_content}\n</skill>"
                    ),
                }
            )
        messages.append({"role": "user", "content": input.case.prompt})
        return messages

    def execute(self, input: AdapterInput) -> AdapterOutput:
        messages = self._build_messages(input)
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }
        if self._chat_template_kwargs:
            payload["chat_template_kwargs"] = self._chat_template_kwargs

        url = f"{self._base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        input.work_dir.mkdir(parents=True, exist_ok=True)
        input.output_dir.mkdir(parents=True, exist_ok=True)

        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self._timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            elapsed_ms = (time.monotonic() - start) * 1000

            choice = body["choices"][0]
            message = choice["message"]
            content = message.get("content", "") or ""
            reasoning = message.get("reasoning_content", "") or ""

            usage = body.get("usage", {})
            token_usage = {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            }

            tool_events = []
            if reasoning:
                tool_events.append(
                    ToolEvent(
                        name="reasoning",
                        arguments={"model": self._model},
                        result_summary=reasoning[:500],
                    )
                )

            skill_content = self._load_skill_content(input.skill_path)
            activation_evidence = (
                f"skill loaded from {input.skill_path.name}/SKILL.md" if skill_content else None
            )

            return AdapterOutput(
                exit_status=ExitStatus.COMPLETED,
                response=content if content else None,
                activation_evidence=activation_evidence,
                artifacts=[],
                environment_state={
                    "model": self._model,
                    "finish_reason": choice.get("finish_reason", ""),
                    "has_skill": skill_content is not None,
                },
                tool_events=tool_events,
                duration_ms=elapsed_ms,
                token_usage=token_usage,
                raw_trace_path=None,
                error=None,
            )

        except urllib.error.HTTPError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.ERROR,
                response=None,
                error=f"HTTP {exc.code}: {exc.reason}",
                duration_ms=elapsed_ms,
            )
        except urllib.error.URLError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.ERROR,
                response=None,
                error=f"connection error: {exc.reason}",
                duration_ms=elapsed_ms,
            )
        except TimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.TIMEOUT,
                response=None,
                error=f"request exceeded {self._timeout_seconds}s timeout",
                duration_ms=elapsed_ms,
            )
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.ERROR,
                response=None,
                error=f"malformed response: {exc}",
                duration_ms=elapsed_ms,
            )
