"""OpenAI-compatible API adapter for paired skill evaluation.

Sends the case prompt to an OpenAI-compatible chat completions endpoint.
Every arm receives the same neutral system wrapper; its skill-context slot
contains the pinned skill and references or is empty for a no-skill diagnostic.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from .models import AdapterInput, AdapterOutput, ExitStatus, ToolEvent
from .reference_inputs import build_context

_SAFE_FINISH_REASON = re.compile(r"[A-Za-z0-9_.:-]{1,80}\Z")
_SAFE_HTTP_ERROR_FIELD_VALUE = re.compile(r"[A-Za-z0-9_.:-]{1,80}\Z")
_UNUSABLE_FINISH_REASONS = {"length", "content_filter", "tool_calls", "function_call"}
_RATE_LIMIT_MAX_RETRY_SECONDS = 60
_RATE_LIMIT_FALLBACK_RETRY_SECONDS = 1
_HARD_QUOTA_ERROR_CODES = {
    "credit_balance_exhausted",
    "insufficient_quota",
    "organization_spend_limit_exceeded",
    "organization_usage_limit_exceeded",
    "project_spend_limit_exceeded",
    "project_usage_limit_exceeded",
}
NEUTRAL_SYSTEM_WRAPPER = (
    "Answer the user's task directly. Use supplied skill context only as optional task guidance; "
    "the context may be empty."
)


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


@dataclass
class _RetryTelemetry:
    attempts: int = 0


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


def _safe_http_error_fields(exc: urllib.error.HTTPError) -> dict[str, str]:
    """Read and retain only allowlisted, provider-supplied error identifiers."""
    cached = getattr(exc, "_eval_runner_safe_error_fields", None)
    if isinstance(cached, dict):
        return cached

    fields: dict[str, str] = {}
    try:
        body = json.loads(exc.read())
        error = body.get("error", body) if isinstance(body, dict) else {}
        if isinstance(error, dict):
            for key in ("type", "code", "param"):
                value = error.get(key)
                if isinstance(value, str) and _SAFE_HTTP_ERROR_FIELD_VALUE.fullmatch(value):
                    fields[key] = value
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    finally:
        exc.close()

    # HTTPError has a normal instance dictionary. Cache only sanitized fields so
    # the retry decision and final diagnostic do not read or retain raw body text.
    exc._eval_runner_safe_error_fields = fields
    return fields


def _is_explicit_hard_quota_error(fields: dict[str, str]) -> bool:
    return any(fields.get(key) in _HARD_QUOTA_ERROR_CODES for key in ("type", "code"))


def _urlopen_with_rate_limit_retry(
    url: str,
    data: bytes,
    headers: dict[str, str],
    timeout: int,
    *,
    retry_telemetry: _RetryTelemetry | None = None,
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
        error_fields = _safe_http_error_fields(exc)
        if _is_explicit_hard_quota_error(error_fields):
            exc._eval_runner_retry_skipped_reason = "hard_quota"
            raise
        delay = _retry_after_seconds(exc.headers)
        if delay is None:
            delay = _RATE_LIMIT_FALLBACK_RETRY_SECONDS
        if delay > _RATE_LIMIT_MAX_RETRY_SECONDS:
            raise
        exc.close()
        time.sleep(delay)
        if retry_telemetry is not None:
            retry_telemetry.attempts += 1
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
        return "0.2.0"

    @property
    def max_skill_chars(self) -> int | None:
        """Maximum skill-context size used by the paired preflight."""
        return self._max_skill_chars

    def _build_input(self, input: AdapterInput) -> tuple[list[dict[str, str]], dict[str, Any]]:
        skill_content, provenance = build_context(
            input.skill_path, input.case.skill_references, self._max_skill_chars
        )
        expected_context_hash = input.harness_config.get("preflight_context_sha256")
        if expected_context_hash and provenance.get("context_sha256") != expected_context_hash:
            raise ValueError("staged skill context changed after paired preflight")
        system_message = (
            f"{NEUTRAL_SYSTEM_WRAPPER}\n\n<skill_context>\n{skill_content or ''}\n</skill_context>"
        )
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": input.case.prompt},
        ]
        harness_config = input.harness_config
        provenance["comparison"] = harness_config.get("comparison_mode", "skill_vs_no_skill")
        if harness_config.get("comparison_policy"):
            provenance["comparison_policy"] = harness_config["comparison_policy"]
        if harness_config.get("snapshot_revision"):
            provenance["snapshot_revision"] = harness_config["snapshot_revision"]
        if harness_config.get("arm"):
            provenance["arm"] = harness_config["arm"]
        if harness_config.get("pair_id"):
            provenance["pair_id"] = harness_config["pair_id"]
        if harness_config.get("evidence_contract_sha256"):
            provenance["evidence_contract_sha256"] = harness_config["evidence_contract_sha256"]
        if harness_config.get("oracle_type"):
            provenance["oracle_type"] = harness_config["oracle_type"]
        provenance["wrapper_sha256"] = hashlib.sha256(
            NEUTRAL_SYSTEM_WRAPPER.encode("utf-8")
        ).hexdigest()
        provenance["task_input_sha256"] = hashlib.sha256(
            input.case.prompt.encode("utf-8")
        ).hexdigest()
        settings = {
            "base_url": self._base_url,
            "model": self._model,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
            "timeout_seconds": self._timeout_seconds,
            "max_skill_chars": self._max_skill_chars,
        }
        if self._chat_template_kwargs:
            settings["chat_template_kwargs"] = self._chat_template_kwargs
        provenance["model_settings_sha256"] = _canonical_hash(settings)
        provenance["system_message_sha256"] = hashlib.sha256(
            system_message.encode("utf-8")
        ).hexdigest()
        provenance["messages_sha256"] = hashlib.sha256(
            json.dumps(messages, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        ).hexdigest()
        return messages, provenance

    def execute(self, input: AdapterInput) -> AdapterOutput:
        messages, provenance = self._build_input(input)
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
        retry_telemetry = _RetryTelemetry()
        try:
            with _urlopen_with_rate_limit_retry(
                url,
                data,
                headers,
                self._timeout_seconds,
                retry_telemetry=retry_telemetry,
            ) as resp:
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

            has_skill = provenance["condition"] == "skill"
            activation_evidence = (
                f"skill loaded from {input.skill_path.name}/SKILL.md" if has_skill else None
            )
            environment_state = {
                "model": self._model,
                "finish_reason": finish_reason or "unknown",
                "has_skill": has_skill,
                "rate_limit_retries": retry_telemetry.attempts,
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
                    rate_limit_retries=retry_telemetry.attempts,
                    input_provenance=provenance,
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
                rate_limit_retries=retry_telemetry.attempts,
                input_provenance=provenance,
                raw_trace_path=None,
                error=None,
                artifact_inventory_complete=False,
            )

        except urllib.error.HTTPError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            safe_context = []
            safe_context.extend(
                f"{key}={value}" for key, value in _safe_http_error_fields(exc).items()
            )
            if exc.code == 429:
                retry_skipped = getattr(exc, "_eval_runner_retry_skipped_reason", None)
                if retry_skipped:
                    safe_context.append(f"retry_skipped={retry_skipped}")
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
                rate_limit_retries=retry_telemetry.attempts,
                input_provenance=provenance,
            )
        except urllib.error.URLError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.ERROR,
                response=None,
                error=f"connection error: {exc.reason}",
                duration_ms=elapsed_ms,
                rate_limit_retries=retry_telemetry.attempts,
                input_provenance=provenance,
            )
        except TimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.TIMEOUT,
                response=None,
                error=f"request exceeded {self._timeout_seconds}s timeout",
                duration_ms=elapsed_ms,
                rate_limit_retries=retry_telemetry.attempts,
                input_provenance=provenance,
            )
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return AdapterOutput(
                exit_status=ExitStatus.ERROR,
                response=None,
                error=f"malformed response: {exc}",
                duration_ms=elapsed_ms,
                rate_limit_retries=retry_telemetry.attempts,
                input_provenance=provenance,
            )
