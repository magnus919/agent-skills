"""Opt-in, bounded reference context for skill-versus-no-skill API trials."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

from .path_safety import validate_case_id, validate_relative_path

MAX_FILE_BYTES = 60_000
MAX_REFERENCE_BYTES = 80_000
MAX_REFERENCES = 3


def read_source(root: Path, relative: str, limit: int = MAX_FILE_BYTES) -> bytes:
    """Read a bounded regular UTF-8 source without following any symlink."""
    validate_relative_path(relative)
    if root.is_symlink():
        raise ValueError("reference root must not be a symlink")
    descriptors: list[int] = []
    try:
        current = os.open(root.resolve(strict=True), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(current)
        parts = relative.split("/")
        for part in parts[:-1]:
            current = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            descriptors.append(current)
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=current)
        descriptors.append(fd)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("input source must be a regular file")
        data = bytearray()
        while chunk := os.read(fd, min(8192, limit + 1 - len(data))):
            data.extend(chunk)
            if len(data) > limit:
                raise ValueError("input source exceeds byte limit")
        result = bytes(data)
        result.decode("utf-8")
        return result
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def validate_references(references: dict[str, str]) -> None:
    if not isinstance(references, dict) or len(references) > MAX_REFERENCES:
        raise ValueError("reference inputs require a mapping of at most three files")
    for path, digest in references.items():
        validate_relative_path(path)
        parts = path.split("/")
        if (
            len(parts) != 2
            or parts[0] != "references"
            or parts[1].startswith(".")
            or not parts[1].endswith(".md")
        ):
            raise ValueError("only direct references/*.md sources may be injected")
        if not isinstance(digest, str) or re.fullmatch(r"[a-f0-9]{64}", digest) is None:
            raise ValueError("reference source requires a full SHA-256")


def load_reference_inputs(skill_root: Path, case_ids: set[str]) -> dict[str, dict[str, str]]:
    """Load a separate adapter contract; leave portable evals-v1 assertions unchanged."""
    config = skill_root / "evals/openai-reference-inputs.json"
    if not config.exists() and not config.is_symlink():
        return {}
    data = json.loads(read_source(skill_root, "evals/openai-reference-inputs.json"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "cases"}:
        raise ValueError("invalid reference-input contract fields")
    if (
        type(data["schema_version"]) is not int
        or data["schema_version"] != 1
        or not isinstance(data["cases"], dict)
    ):
        raise ValueError("invalid reference-input contract version or cases")
    for case_id, references in data["cases"].items():
        validate_case_id(case_id)
        if case_id not in case_ids:
            raise ValueError("reference-input contract names an unknown case")
        validate_references(references)
    return dict(data["cases"])


def build_context(
    skill_root: Path, references: dict[str, str], max_skill_chars: int | None
) -> tuple[str | None, dict[str, Any]]:
    """Return exactly the transmitted context and deterministic source metadata."""
    validate_references(references)
    metadata: dict[str, Any] = {
        "contract": "openai-reference-inputs-v1",
        "comparison": "skill_vs_no_skill",
        "sources": [],
    }
    if not (skill_root / "SKILL.md").exists() and not (skill_root / "SKILL.md").is_symlink():
        metadata["condition"] = "no_skill"
        return None, metadata
    raw = read_source(skill_root, "SKILL.md")
    content = raw.decode("utf-8")
    truncated = bool(max_skill_chars and len(content) > max_skill_chars)
    if truncated:
        content = content[:max_skill_chars] + "\n[truncated]"
    metadata["condition"] = "skill"
    metadata["sources"].append(
        {
            "path": "SKILL.md",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "truncated": truncated,
        }
    )
    total = 0
    for path, expected in sorted(references.items()):
        raw = read_source(skill_root, path)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected:
            raise ValueError(f"reference source hash mismatch: {path}")
        total += len(raw)
        if total > MAX_REFERENCE_BYTES:
            raise ValueError("reference context exceeds aggregate byte limit")
        content += f"\n\n<reference path={json.dumps(path)}>\n{raw.decode('utf-8')}\n</reference>"
        metadata["sources"].append(
            {"path": path, "sha256": digest, "bytes": len(raw), "truncated": False}
        )
    return content, metadata
