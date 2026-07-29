"""Run manifest construction and serialization."""

from __future__ import annotations

import json
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import AdapterInput, AdapterOutput
from .path_safety import contained_path, hash_contained_file, validate_case_id

MANIFEST_SCHEMA_VERSION = 1


def _git_tree_hash(skill_path: Path) -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%T", "--", str(skill_path)],
        capture_output=True,
        text=True,
        cwd=skill_path,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()[:16]
    return "unknown"


def _skill_name(skill_path: Path) -> str:
    skill_md = skill_path / "SKILL.md"
    if skill_md.is_file():
        return skill_path.name
    return skill_path.name


def build_manifest(
    *,
    adapter_name: str,
    adapter_version: str,
    harness_name: str,
    harness_version: str,
    model_provider: str,
    model_id: str,
    adapter_input: AdapterInput,
    adapter_output: AdapterOutput,
    started_at: datetime,
    finished_at: datetime,
) -> dict[str, Any]:
    case = adapter_input.case
    skill_path = adapter_input.skill_path

    artifact_digests: dict[str, str] = {}
    for artifact_rel in adapter_output.artifacts:
        artifact_digests[artifact_rel] = (
            hash_contained_file(adapter_input.output_dir, artifact_rel) or "missing"
        )

    failures: list[dict[str, str]] = []
    if adapter_output.error:
        failures.append({"type": "execution_error", "message": adapter_output.error})

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "trial_id": str(uuid.uuid4()),
        "candidate": {
            "skill_name": _skill_name(skill_path),
            "skill_path": skill_path.name,
            "tree_hash": _git_tree_hash(skill_path),
        },
        "case": {
            "case_id": case.id,
            "prompt_hash": case.prompt_hash,
            "fixture_hashes": case.fixture_hashes(skill_path),
        },
        "adapter": {
            "name": adapter_name,
            "version": adapter_version,
        },
        "harness": {
            "name": harness_name,
            "version": harness_version,
        },
        "model": {
            "provider": model_provider,
            "model_id": model_id,
        },
        "permissions": adapter_input.permissions,
        "network_policy": adapter_input.limits.get("network_policy", "unspecified"),
        "limits": adapter_input.limits,
        "cache_state": adapter_input.harness_config.get("cache_state", "unspecified"),
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "status": adapter_output.exit_status.value,
        "outputs": {
            "response": adapter_output.response,
            "activation_evidence": adapter_output.activation_evidence,
            "artifact_digests": artifact_digests,
            "tool_event_count": len(adapter_output.tool_events),
        },
        "duration_ms": adapter_output.duration_ms,
        "token_usage": adapter_output.token_usage,
        "failures": failures,
        "missing_evidence": adapter_output.missing_evidence(),
    }


def write_manifest(manifest: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    trial_id = manifest.get("trial_id", "unknown")
    case_id = manifest.get("case", {}).get("case_id", "unknown")
    validate_case_id(case_id)
    filename = f"{case_id}--{trial_id[:8]}.manifest.json"
    path = contained_path(output_dir, filename)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path
