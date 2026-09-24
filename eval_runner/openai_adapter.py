"""OpenAI-compatible API adapter for paired skill evaluation.

Sends the case prompt to an OpenAI-compatible chat completions endpoint.
When a skill is present (SKILL.md exists in skill_path), its content is
injected as a system message. The baseline condition (empty skill_path)
sends only the user prompt.
"""

from __future__ import annotations

import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from .models import AdapterInput, AdapterOutput, ExitStatus, ToolEvent

_SAFE_FINISH_REASON = re.compile(r"[A-Za-z0-9_.:-]{1,80}\Z")
_UNUSABLE_FINISH_REASONS = {"length", "content_filter", "tool_calls", "function_call"}
_RATE_LIMIT_MAX_RETRY_SECONDS = 60
_RATE_LIMIT_FALLBACK_RETRY_SECONDS = 1


def _retry_after_seconds(headers: Any, *, now: datetime | None = None) -> float | None:
    """Parse the HTTP Retry-After delta or date form, returning a safe delay."""
    value = headers.get("Retry-After") if headers is not None else None
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    try:
        delay = float(value)
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        delay = (retry_at - current).total_seconds()
    if not math.isfinite(delay):
        return math.inf
    return max(0.0, delay)


def _urlopen_with_rate_limit_retry(
    url: str, data: bytes, headers: dict[str, str], timeout: int
) -> Any:
    """Retry one 429 once, respecting bounded Retry-After guidance."""

    def open_once() -> Any:
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        return urllib.request.urlopen(request, timeout=timeout)

    try:
        return open_once()
    except urllib.error.HTTPError as exc:
        if exc.code != 429:
            raise
        delay = _retry_after_seconds(exc.headers)
        if delay is None:
            delay = _RATE_LIMIT_FALLBACK_RETRY_SECONDS
        if delay > _RATE_LIMIT_MAX_RETRY_SECONDS:
            raise
        exc.close()
        time.sleep(delay)
        return open_once()


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
        self._api_key = api_key if api_key is not None else os.environ.get("EVAL_API_KEY")
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
        input.work_dir.mkdir(parents=True, exist_ok=True)
        input.output_dir.mkdir(parents=True, exist_ok=True)

        start = time.monotonic()
        try:
            with _urlopen_with_rate_limit_retry(url, data, headers, self._timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            elapsed_ms = (time.monotonic() - start) * 1000

            choice = body["choices"][0]
            message = choice["message"]
            content = message.get("content", "") or ""
            raw_finish_reason = choice.get("finish_reason")
            finish_reason = (
                raw_finish_reason.lower()
                if isinstance(raw_finish_reason, str)
                and _SAFE_FINISH_REASON.fullmatch(raw_finish_reason)
                else None
            )

            usage = body.get("usage", {})
            token_usage = {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            }

            skill_content = self._load_skill_content(input.skill_path)
            activation_evidence = (
                f"skill loaded from {input.skill_path.name}/SKILL.md" if skill_content else None
            )
            environment_state = {
                "model": self._model,
                "finish_reason": finish_reason or "unknown",
                "has_skill": skill_content is not None,
            }

            completion_error = None
            if not isinstance(content, str) or not content.strip():
                completion_error = "empty assistant content"
            elif finish_reason in _UNUSABLE_FINISH_REASONS:
                completion_error = "assistant completion did not end normally"

            if completion_error:
                reason_detail = f" (finish_reason={finish_reason})" if finish_reason else ""
                return AdapterOutput(
                    exit_status=ExitStatus.ERROR,
                    response=None,
                    finish_reason=finish_reason,
                    activation_evidence=activation_evidence,
                    environment_state=environment_state,
                    duration_ms=elapsed_ms,
                    token_usage=token_usage,
                    error=f"model completion unusable: {completion_error}{reason_detail}",
                )

            reasoning = message.get("reasoning_content", "") or ""
            tool_events = []
            if reasoning:
                tool_events.append(
                    ToolEvent(
                        name="reasoning",
                        arguments={"model": self._model},
                        result_summary=reasoning[:500],
                    )
                )

            return AdapterOutput(
                exit_status=ExitStatus.COMPLETED,
                response=content,
                finish_reason=finish_reason,
                activation_evidence=activation_evidence,
                artifacts=[],
                environment_state=environment_state,
                tool_events=tool_events,
                duration_ms=elapsed_ms,
                token_usage=token_usage,
                raw_trace_path=None,
                error=None,
            )

        except urllib.error.HTTPError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            safe_context = []
            try:
                body = json.loads(exc.read())
                error = body.get("error", body) if isinstance(body, dict) else {}
                if isinstance(error, dict):
                    for key in ("type", "code", "param"):
                        value = error.get(key)
                        if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,80}", value):
                            safe_context.append(f"{key}={value}")
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                pass
            if exc.code == 429:
                retry_after = _retry_after_seconds(exc.headers)
                if retry_after is not None:
                    if math.isfinite(retry_after):
                        safe_context.append(f"retry_after_seconds={math.ceil(retry_after)}")
                    else:
                        safe_context.append("retry_after_seconds=too_long")
                    if retry_after > _RATE_LIMIT_MAX_RETRY_SECONDS:
                        safe_context.append("retry_deferred=true")
            detail = f" ({', '.join(safe_context)})" if safe_context else ""
            return AdapterOutput(
                exit_status=ExitStatus.ERROR,
                response=None,
                error=f"HTTP {exc.code}: {exc.reason}{detail}",
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
