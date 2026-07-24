#!/usr/bin/env python3
"""Validation for this repository's eval manifest v1 contract."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_VERSION = 1
STATE_NAMES = (
    "manifest_present",
    "schema_valid",
    "executable_grader_bindings_present",
    "recent_run_evidence_present",
    "release_gated_evidence_present",
)
NOT_ASSESSED = "not_assessed"
NOT_APPLICABLE = "not_applicable"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "evals-v1.schema.json"
CASE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class ValidationResult:
    manifest_path: Path
    case_count: int = 0
    errors: list[str] = field(default_factory=list)
    states: dict[str, bool | str] = field(
        default_factory=lambda: {
            "manifest_present": False,
            "schema_valid": NOT_APPLICABLE,
            "executable_grader_bindings_present": NOT_ASSESSED,
            "recent_run_evidence_present": NOT_ASSESSED,
            "release_gated_evidence_present": NOT_ASSESSED,
        }
    )

    def error(self, location: str, message: str) -> None:
        suffix = f" {location}" if location else ""
        self.errors.append(f"{self.manifest_path}:{suffix}: {message}")


class DuplicateKeyError(ValueError):
    def __init__(self, key: str):
        super().__init__(f"duplicate key {key!r}")
        self.key = key


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise DuplicateKeyError(key)
        out[key] = value
    return out


def _json_pointer(path: Any) -> str:
    if not path:
        return "$"
    location = "$"
    for part in path:
        location += f"[{part}]" if isinstance(part, int) else f".{part}"
    return location


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _contains_control_characters(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, check=False)


def _tracked_files(repo_root: Path) -> set[str]:
    result = _git(repo_root, "ls-files", "-z")
    if result.returncode != 0:
        return set()
    return {
        path
        for path in result.stdout.decode("utf-8", errors="replace").split("\0")
        if path
    }


def _tracked_mode(repo_root: Path, relative_path: str) -> str | None:
    result = _git(repo_root, "ls-files", "-s", "--", relative_path)
    if result.returncode != 0 or not result.stdout:
        return None
    return result.stdout.decode("utf-8", errors="replace").split(None, 1)[0]


def _case_mismatch(tracked: set[str], relative_path: str) -> bool:
    lower = relative_path.lower()
    return any(path.lower() == lower and path != relative_path for path in tracked)


def _load_json_strict(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parsed = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(parsed, dict):
        raise TypeError("top-level JSON value must be an object")
    return parsed


@lru_cache(maxsize=1)
def _schema_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _validate_schema(data: dict[str, Any], result: ValidationResult) -> None:
    validator = _schema_validator()
    for issue in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        result.error(_json_pointer(issue.absolute_path), issue.message)


def _targeted_schema_version_errors(data: dict[str, Any], result: ValidationResult) -> None:
    if "schema_version" not in data:
        result.error(
            "$.schema_version",
            "missing required schema_version; add \"schema_version\": 1",
        )
        return
    version = data["schema_version"]
    if isinstance(version, str):
        result.error(
            "$.schema_version",
            "schema_version must be integer 1, not a string",
        )
        return
    if isinstance(version, bool) or not isinstance(version, int):
        result.error("$.schema_version", "schema_version must be integer 1")
        return
    if version != SCHEMA_VERSION:
        result.error(
            "$.schema_version",
            f"unsupported schema_version {version!r}; supported version is 1",
        )


def _validate_case_aliases(case: dict[str, Any], index: int, result: ValidationResult) -> None:
    has_assertions = "assertions" in case
    has_expectations = "expectations" in case
    if has_assertions and has_expectations:
        result.error(
            f"$.evals[{index}].expectations",
            "assertions and expectations cannot both be present; keep assertions only",
        )
    elif has_expectations:
        result.error(
            f"$.evals[{index}].expectations",
            "expectations is not supported by repository schema v1; rename it to assertions",
        )


def _validate_fixture_path(
    value: Any,
    *,
    skill_root: Path,
    repo_root: Path,
    tracked: set[str],
    location: str,
    result: ValidationResult,
) -> None:
    if not _nonempty_string(value):
        result.error(location, "must be a nonempty relative path string")
        return

    path_text = value
    if _contains_control_characters(path_text):
        result.error(location, "must not contain control characters")
        return
    if "\\" in path_text:
        result.error(location, "must not contain backslashes")
        return

    lexical_parts = path_text.split("/")
    if any(part in {"", ".", ".."} for part in lexical_parts):
        result.error(location, "must not contain '.', '..', or empty path components")
        return

    pure = PurePosixPath(path_text)
    if pure.is_absolute() or not pure.parts:
        result.error(location, "must be a relative path")
        return

    candidate = skill_root.joinpath(*lexical_parts)
    relative = candidate.relative_to(repo_root).as_posix()

    if _case_mismatch(tracked, relative):
        result.error(location, f"path is case-mismatched with tracked Git path: {path_text}")
        return

    probe = skill_root
    for part in lexical_parts:
        probe = probe / part
        if probe.is_symlink():
            result.error(location, f"symlinks are not allowed in path components: {path_text}")
            return

    if not candidate.exists():
        mode = _tracked_mode(repo_root, relative)
        if mode is None:
            result.error(location, f"file does not exist: {path_text}")
        else:
            result.error(
                location,
                f"file does not exist in working tree (tracked in Git index): {path_text}",
            )
        return

    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(skill_root.resolve())
    except ValueError:
        result.error(location, f"path escapes skill root: {path_text}")
        return
    except OSError:
        result.error(location, f"file does not exist: {path_text}")
        return

    if not resolved.is_file():
        result.error(location, f"must resolve to a regular file: {path_text}")
        return

    if relative not in tracked:
        result.error(location, f"file is not tracked by Git: {path_text}")
        return

    mode = _tracked_mode(repo_root, relative)
    if mode is not None and mode == "120000":
        result.error(location, f"tracked symlink is not allowed: {path_text}")


def _semantic_checks(data: dict[str, Any], result: ValidationResult, repo_root: Path) -> None:
    manifest_path = result.manifest_path
    skill_root = manifest_path.parent.parent.resolve()
    tracked = _tracked_files(repo_root)

    _targeted_schema_version_errors(data, result)

    skill_name = data.get("skill_name")
    if skill_name != skill_root.name:
        result.error(
            "$.skill_name",
            f"must equal containing skill directory name {skill_root.name!r}",
        )

    evals = data.get("evals")
    if isinstance(evals, list):
        result.case_count = len(evals)
    else:
        result.case_count = 0
        return

    seen_ids: dict[str, int] = {}
    for index, case in enumerate(evals):
        if not isinstance(case, dict):
            continue
        _validate_case_aliases(case, index, result)

        case_id = case.get("id")
        if isinstance(case_id, str):
            if len(case_id) > 64:
                result.error(f"$.evals[{index}].id", "must be 1-64 characters")
            if not CASE_ID_RE.fullmatch(case_id):
                result.error(
                    f"$.evals[{index}].id",
                    "must match ^[a-z0-9]+(?:-[a-z0-9]+)*$",
                )
            prior = seen_ids.get(case_id)
            if prior is not None:
                result.error(
                    f"$.evals[{index}].id",
                    f"duplicate case ID {case_id!r}; first seen at $.evals[{prior}].id",
                )
            else:
                seen_ids[case_id] = index

        assertions = case.get("assertions")
        if isinstance(assertions, list):
            seen_assertions: set[str] = set()
            for assertion_index, assertion in enumerate(assertions):
                if not _nonempty_string(assertion):
                    result.error(
                        f"$.evals[{index}].assertions[{assertion_index}]",
                        "must be a nonempty non-whitespace string",
                    )
                    continue
                if assertion in seen_assertions:
                    result.error(
                        f"$.evals[{index}].assertions[{assertion_index}]",
                        "duplicate assertion values are not allowed",
                    )
                    continue
                seen_assertions.add(assertion)

        files = case.get("files")
        if isinstance(files, list):
            for file_index, file_value in enumerate(files):
                _validate_fixture_path(
                    file_value,
                    skill_root=skill_root,
                    repo_root=repo_root,
                    tracked=tracked,
                    location=f"$.evals[{index}].files[{file_index}]",
                    result=result,
                )


def validate_manifest(manifest_path: Path, repo_root: Path) -> ValidationResult:
    """Validate one manifest against schema and repository semantics."""
    manifest_path = Path(manifest_path)
    repo_root = Path(repo_root).resolve()
    result = ValidationResult(manifest_path)
    if not manifest_path.is_file():
        return result

    result.states["manifest_present"] = True
    result.states["schema_valid"] = False
    try:
        data = _load_json_strict(manifest_path)
    except DuplicateKeyError as exc:
        result.error("$", f"duplicate JSON object key: {exc.key!r}")
        return result
    except json.JSONDecodeError as exc:
        result.error("$", f"invalid JSON: {exc}")
        return result
    except OSError as exc:
        result.error("$", f"unable to read manifest: {exc}")
        return result
    except TypeError as exc:
        result.error("$", str(exc))
        return result

    _validate_schema(data, result)
    _semantic_checks(data, result, repo_root)

    result.states["schema_valid"] = not result.errors
    return result


def find_skill_manifests(repo_root: Path) -> list[Path]:
    manifests = []
    for skill_file in Path(repo_root).glob("**/SKILL.md"):
        if "agent-council/profiles/skills" in skill_file.as_posix():
            continue
        manifest = skill_file.parent / "evals" / "evals.json"
        if manifest.is_file():
            manifests.append(manifest)
    return sorted(manifests)
