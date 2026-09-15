#!/usr/bin/env python3
"""Validate a community guide plan without reading from the network."""

from __future__ import annotations

import datetime as _datetime
import json
import ntpath
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

_MISSING = object()
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MAINTENANCE_STATUSES = {"proposed", "confirmed"}
_SOURCE_STATUSES = {"verified", "supplied", "unresolved"}
_HELP_TEXT = """Usage: python3 scripts/validate_guide.py PATH_TO_PLAN_JSON
Validate a community guide plan and its local file references.
Exit codes: 0 valid, 1 invalid plan, 2 input failure.
"""


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains a key more than once."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r} is not allowed")


def _path_label(path: str, key: str | int | None = None) -> str:
    if key is None:
        return path
    if isinstance(key, int):
        return f"{path}[{key}]"
    return f"{path}.{key}"


def _get(mapping: dict[str, Any], key: str, path: str, errors: list[str]) -> Any:
    if key not in mapping:
        errors.append(f"{_path_label(path, key)}: required field is missing")
        return _MISSING
    return mapping[key]


def _is_nonblank_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _check_nonblank_string(value: Any, path: str, errors: list[str]) -> bool:
    if not _is_nonblank_string(value):
        errors.append(f"{path}: must be a nonblank string")
        return False
    return True


def _check_positive_int(value: Any, path: str, errors: list[str]) -> bool:
    if not _positive_int(value):
        errors.append(f"{path}: must be a positive integer")
        return False
    return True


def _check_list(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, list):
        errors.append(f"{path}: must be an array")
        return False
    return True


def _check_iso_date(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not _DATE_RE.fullmatch(value):
        errors.append(f"{path}: must be an ISO date in YYYY-MM-DD format")
        return False
    try:
        _datetime.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{path}: must be a valid calendar date in YYYY-MM-DD format")
        return False
    return True


def _is_absolute_path(value: str) -> bool:
    # ntpath catches drive-letter and UNC paths even when this checker runs on
    # POSIX, where those strings would otherwise look like ordinary filenames.
    return os.path.isabs(value) or ntpath.isabs(value) or bool(ntpath.splitdrive(value)[0])


def _check_relative_file(
    value: Any,
    path: str,
    plan_dir: Path,
    errors: list[str],
) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: must be a nonblank relative file path")
        return False
    if "\x00" in value:
        errors.append(f"{path}: must not contain a NUL character")
        return False
    if "\\" in value:
        errors.append(f"{path}: backslashes are not allowed; use '/' path separators")
        return False
    if ".." in value.split("/"):
        errors.append(f"{path}: '..' path components are not allowed")
        return False
    if _is_absolute_path(value):
        errors.append(f"{path}: must be relative to the plan directory")
        return False

    relative = Path(value)
    if relative == Path("."):
        errors.append(f"{path}: must name a file, not the plan directory")
        return False

    try:
        base = plan_dir.resolve()
        candidate = (base / relative).resolve(strict=False)
        candidate.relative_to(base)
    except (OSError, RuntimeError, ValueError):
        errors.append(f"{path}: resolves outside the plan directory")
        return False

    if not candidate.is_file():
        errors.append(f"{path}: referenced file does not exist: {value!r}")
        return False
    return True


def _validate_module(
    module: Any,
    index: int,
    worksheet_ids: set[str],
    errors: list[str],
) -> None:
    path = f"$.modules[{index}]"
    if not isinstance(module, dict):
        errors.append(f"{path}: must be an object")
        return

    module_id = _get(module, "id", path, errors)
    _check_nonblank_string(module_id, f"{path}.id", errors)
    title = _get(module, "title", path, errors)
    _check_nonblank_string(title, f"{path}.title", errors)
    duration = _get(module, "duration_minutes", path, errors)
    duration_valid = _check_positive_int(duration, f"{path}.duration_minutes", errors)

    activities = _get(module, "activities", path, errors)
    activities_valid = _check_list(activities, f"{path}.activities", errors)
    activity_minutes: list[int] = []
    if activities_valid:
        if not activities:
            errors.append(f"{path}.activities: must contain at least one activity")
            activities_valid = False
        for activity_index, activity in enumerate(activities):
            activity_path = f"{path}.activities[{activity_index}]"
            if not isinstance(activity, dict):
                errors.append(f"{activity_path}: must be an object")
                activities_valid = False
                continue
            activity_title = _get(activity, "title", activity_path, errors)
            title_valid = _check_nonblank_string(
                activity_title, f"{activity_path}.title", errors
            )
            minutes = _get(activity, "minutes", activity_path, errors)
            minutes_valid = _check_positive_int(
                minutes, f"{activity_path}.minutes", errors
            )
            if title_valid and minutes_valid:
                activity_minutes.append(minutes)
            else:
                activities_valid = False

    if duration_valid and activities_valid and sum(activity_minutes) > duration:
        errors.append(
            f"{path}: activity minutes total {sum(activity_minutes)} "
            f"exceeds duration_minutes {duration}"
        )

    worksheet_refs = _get(module, "worksheet_ids", path, errors)
    if _check_list(worksheet_refs, f"{path}.worksheet_ids", errors):
        for ref_index, worksheet_id in enumerate(worksheet_refs):
            ref_path = f"{path}.worksheet_ids[{ref_index}]"
            if not isinstance(worksheet_id, str):
                errors.append(f"{ref_path}: must be a string")
            elif worksheet_id not in worksheet_ids:
                errors.append(f"{ref_path}: worksheet id {worksheet_id!r} does not resolve")


def _validate_worksheet(
    worksheet: Any,
    index: int,
    plan_dir: Path,
    worksheet_ids: set[str],
    errors: list[str],
) -> None:
    path = f"$.worksheets[{index}]"
    if not isinstance(worksheet, dict):
        errors.append(f"{path}: must be an object")
        return
    worksheet_id = _get(worksheet, "id", path, errors)
    if _check_nonblank_string(worksheet_id, f"{path}.id", errors):
        if worksheet_id in worksheet_ids:
            errors.append(f"{path}.id: duplicate worksheet id {worksheet_id!r}")
        else:
            worksheet_ids.add(worksheet_id)
    worksheet_path = _get(worksheet, "path", path, errors)
    _check_relative_file(worksheet_path, f"{path}.path", plan_dir, errors)


def _validate_source(source: Any, index: int, errors: list[str], warnings: list[str]) -> None:
    path = f"$.sources[{index}]"
    if not isinstance(source, dict):
        errors.append(f"{path}: must be an object")
        return
    source_id = _get(source, "id", path, errors)
    _check_nonblank_string(source_id, f"{path}.id", errors)
    locator = _get(source, "locator", path, errors)
    _check_nonblank_string(locator, f"{path}.locator", errors)
    checked_on = _get(source, "checked_on", path, errors)
    _check_iso_date(checked_on, f"{path}.checked_on", errors)
    status = _get(source, "status", path, errors)
    if not isinstance(status, str) or status not in _SOURCE_STATUSES:
        errors.append(
            f"{path}.status: must be one of {', '.join(sorted(_SOURCE_STATUSES))}"
        )
    elif status == "unresolved":
        warnings.append(f"{path}.status: source is unresolved; readiness is not established")


def validate_plan(plan: Any, plan_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Return the checker result for an already parsed guide plan."""

    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, dict):
        return {
            "valid": False,
            "errors": ["$: root must be an object"],
            "warnings": [],
        }

    schema_version = _get(plan, "schema_version", "$", errors)
    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version != 1
    ):
        errors.append("$.schema_version: must be the integer 1")

    title = _get(plan, "title", "$", errors)
    _check_nonblank_string(title, "$.title", errors)

    modules = _get(plan, "modules", "$", errors)
    module_ids: set[str] = set()
    modules_valid = _check_list(modules, "$.modules", errors)
    if modules_valid:
        if not modules:
            errors.append("$.modules: must contain at least one module")
        for index, module in enumerate(modules):
            if isinstance(module, dict):
                module_id = module.get("id", _MISSING)
                if _is_nonblank_string(module_id):
                    if module_id in module_ids:
                        errors.append(
                            f"$.modules[{index}].id: duplicate module id {module_id!r}"
                        )
                    else:
                        module_ids.add(module_id)

    worksheets = _get(plan, "worksheets", "$", errors)
    worksheet_ids: set[str] = set()
    worksheets_valid = _check_list(worksheets, "$.worksheets", errors)
    if worksheets_valid:
        for index, worksheet in enumerate(worksheets):
            _validate_worksheet(worksheet, index, Path(plan_path).resolve().parent, worksheet_ids, errors)

    # Resolve module references after collecting all worksheet IDs, including
    # references in modules that appeared before their worksheet declarations.
    if modules_valid:
        for index, module in enumerate(modules):
            _validate_module(module, index, worksheet_ids, errors)

    materials = _get(plan, "materials", "$", errors)
    if not isinstance(materials, dict):
        if materials is not _MISSING:
            errors.append("$.materials: must be an object")
    else:
        participant = _get(materials, "participant", "$.materials", errors)
        facilitator = _get(materials, "facilitator", "$.materials", errors)
        plan_dir = Path(plan_path).resolve().parent
        _check_relative_file(participant, "$.materials.participant", plan_dir, errors)
        _check_relative_file(facilitator, "$.materials.facilitator", plan_dir, errors)

    maintenance = _get(plan, "maintenance", "$", errors)
    if not isinstance(maintenance, dict):
        if maintenance is not _MISSING:
            errors.append("$.maintenance: must be an object")
    else:
        owner = _get(maintenance, "owner", "$.maintenance", errors)
        _check_nonblank_string(owner, "$.maintenance.owner", errors)
        maintenance_status = _get(maintenance, "status", "$.maintenance", errors)
        if (
            not isinstance(maintenance_status, str)
            or maintenance_status not in _MAINTENANCE_STATUSES
        ):
            errors.append(
                "$.maintenance.status: must be one of confirmed, proposed"
            )
        elif maintenance_status == "proposed":
            warnings.append(
                "$.maintenance.status: owner is unconfirmed while maintenance is proposed"
            )
        review_date = _get(maintenance, "review_date", "$.maintenance", errors)
        _check_iso_date(review_date, "$.maintenance.review_date", errors)

    sources = _get(plan, "sources", "$", errors)
    source_ids: set[str] = set()
    sources_valid = _check_list(sources, "$.sources", errors)
    if sources_valid:
        for index, source in enumerate(sources):
            if isinstance(source, dict):
                source_id = source.get("id", _MISSING)
                if _is_nonblank_string(source_id):
                    if source_id in source_ids:
                        errors.append(
                            f"$.sources[{index}].id: duplicate source id {source_id!r}"
                        )
                    else:
                        source_ids.add(source_id)
            _validate_source(source, index, errors, warnings)

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def _parse_json(text: str) -> Any:
    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonstandard_constant,
    )


def validate_file(plan_path: str | os.PathLike[str]) -> tuple[dict[str, Any], int]:
    """Read and validate a plan, returning (JSON result, process exit code)."""

    path = Path(plan_path)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return (
            {"valid": False, "errors": [f"input failure: cannot read plan: {exc}"], "warnings": []},
            2,
        )
    try:
        plan = _parse_json(text)
    except (DuplicateKeyError, json.JSONDecodeError, ValueError) as exc:
        return (
            {"valid": False, "errors": [f"input failure: invalid JSON: {exc}"], "warnings": []},
            2,
        )

    result = validate_plan(plan, path)
    return result, 0 if result["valid"] else 1


def _emit(result: dict[str, Any]) -> None:
    json.dump(result, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")


def main(argv: Iterable[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args in (["--help"], ["-h"]):
        sys.stdout.write(_HELP_TEXT)
        return 0
    if len(args) != 1:
        _emit(
            {
                "valid": False,
                "errors": ["input failure: expected exactly one plan JSON path"],
                "warnings": [],
            }
        )
        return 2
    try:
        result, exit_code = validate_file(args[0])
    except Exception as exc:  # Keep the noninteractive CLI traceback-free.
        result, exit_code = (
            {"valid": False, "errors": [f"input failure: unable to validate plan: {exc}"], "warnings": []},
            2,
        )
    _emit(result)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
