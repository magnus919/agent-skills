#!/usr/bin/env python3
"""Validate a life-coach v2 activation manifest.

The validator checks declarations and conservative activation rules. It does
not prove that a deployment implements the referenced controls or evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

MODES = {
    "disabled",
    "routine-adult-no-coaching-memory",
    "capability-enabled",
}
CAPABILITIES = (
    "coaching_memory",
    "sponsored_coaching",
    "proactive_contact",
    "sensitive_actions",
    "human_review",
)
PLACEHOLDERS = {
    "",
    "unknown",
    "tbd",
    "todo",
    "yyyy-mm-dd",
}

OBJECT_FIELDS: dict[str, dict[str, type | tuple[type, ...]]] = {
    "deployment": {"id": str, "environment": str},
    "verification": {
        "verified_on": str,
        "review_due_on": str,
        "attested_by": str,
        "basis_ref": str,
    },
    "accountability": {"operator": str, "support_route": str},
    "scope": {"adult_only": bool, "jurisdictions": list},
    "evidence": {
        "ai_scope_disclosure_ref": str,
        "safety_fallback_ref": str,
        "data_notice_ref": str,
    },
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "mode",
    *OBJECT_FIELDS,
    "governance_profile_ref",
    "capabilities",
}
CAPABILITY_FIELDS = {"enabled", "control_profile_ref"}
JURISDICTION_PATTERN = re.compile(r"[A-Z]{2}(?:-[A-Z0-9]{1,3})?")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def _result(
    mode: Any,
    structural_errors: list[str],
    declaration_errors: list[str],
    warnings: list[str],
    enabled_capabilities: list[str] | None = None,
) -> dict[str, Any]:
    structurally_valid = not structural_errors
    declarations_valid = structurally_valid and not declaration_errors
    active_declarations_valid = declarations_valid and mode != "disabled"
    if not declarations_valid:
        status = "INVALID"
    elif mode == "disabled":
        status = "VALID BUT DISABLED"
    else:
        status = "DECLARATIONS VALID"
    return {
        "status": status,
        "mode": mode,
        "structurally_valid": structurally_valid,
        "declarations_valid": declarations_valid,
        "active_declarations_valid": active_declarations_valid,
        "enabled_capabilities": enabled_capabilities or [],
        "errors": structural_errors + declaration_errors,
        "warnings": warnings,
    }


def _is_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return True
    normalized = value.strip().lower()
    return normalized in PLACEHOLDERS or (
        normalized.startswith("<") and normalized.endswith(">")
    )


class DuplicateKeyError(ValueError):
    """Raised when JSON contains an ambiguous object declaration."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate object key: {key}")
        result[key] = value
    return result


def _check_object(
    data: dict[str, Any],
    name: str,
    fields: dict[str, type | tuple[type, ...]],
    errors: list[str],
) -> None:
    value = data.get(name)
    if not isinstance(value, dict):
        errors.append(f"{name} must be an object")
        return
    for extra in sorted(set(value) - set(fields)):
        errors.append(f"unknown property {name}.{extra}")
    for field, expected_type in fields.items():
        path = f"{name}.{field}"
        if field not in value:
            errors.append(f"missing {path}")
        elif not isinstance(value[field], expected_type):
            errors.append(f"{path} must be {_type_name(expected_type)}")


def _type_name(expected_type: type | tuple[type, ...]) -> str:
    names = {
        str: "a string",
        bool: "a boolean",
        list: "an array",
    }
    if isinstance(expected_type, tuple):
        return " or ".join(names.get(item, item.__name__) for item in expected_type)
    return names.get(expected_type, expected_type.__name__)


def _check_structure(data: dict[str, Any], errors: list[str]) -> None:
    for extra in sorted(set(data) - TOP_LEVEL_FIELDS):
        errors.append(f"unknown property {extra}")
    for field in sorted(TOP_LEVEL_FIELDS - set(data)):
        errors.append(f"missing {field}")

    if "schema_version" in data and not isinstance(data["schema_version"], int):
        errors.append("schema_version must be an integer")
    if "mode" in data and not isinstance(data["mode"], str):
        errors.append("mode must be a string")
    if "governance_profile_ref" in data and not isinstance(
        data["governance_profile_ref"], (str, type(None))
    ):
        errors.append("governance_profile_ref must be a string or null")

    for name, fields in OBJECT_FIELDS.items():
        _check_object(data, name, fields, errors)

    scope = data.get("scope")
    if isinstance(scope, dict) and isinstance(scope.get("jurisdictions"), list):
        if not all(isinstance(item, str) for item in scope["jurisdictions"]):
            errors.append("scope.jurisdictions must contain only strings")

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, dict):
        errors.append("capabilities must be an object")
        return
    for extra in sorted(set(capabilities) - set(CAPABILITIES)):
        errors.append(f"unknown property capabilities.{extra}")
    for name in CAPABILITIES:
        path = f"capabilities.{name}"
        capability = capabilities.get(name)
        if not isinstance(capability, dict):
            errors.append(f"{path} must be an object")
            continue
        for extra in sorted(set(capability) - CAPABILITY_FIELDS):
            errors.append(f"unknown property {path}.{extra}")
        for field in sorted(CAPABILITY_FIELDS - set(capability)):
            errors.append(f"missing {path}.{field}")
        if "enabled" in capability and not isinstance(capability["enabled"], bool):
            errors.append(f"{path}.enabled must be a boolean")
        if "control_profile_ref" in capability and not isinstance(
            capability["control_profile_ref"], (str, type(None))
        ):
            errors.append(f"{path}.control_profile_ref must be a string or null")


def _check_active_baseline(data: dict[str, Any], errors: list[str]) -> None:
    required_refs = (
        ("deployment", "id"),
        ("deployment", "environment"),
        ("verification", "attested_by"),
        ("verification", "basis_ref"),
        ("accountability", "operator"),
        ("accountability", "support_route"),
        ("evidence", "ai_scope_disclosure_ref"),
        ("evidence", "safety_fallback_ref"),
        ("evidence", "data_notice_ref"),
    )
    for section, field in required_refs:
        if _is_placeholder(data[section][field]):
            errors.append(f"{section}.{field} must be a verified non-placeholder value")

    parsed_dates: dict[str, date] = {}
    for field in ("verified_on", "review_due_on"):
        value = data["verification"][field]
        if not DATE_PATTERN.fullmatch(value):
            errors.append(f"verification.{field} is malformed; use YYYY-MM-DD")
            continue
        try:
            parsed_dates[field] = date.fromisoformat(value)
        except ValueError:
            errors.append(f"verification.{field} is malformed; use YYYY-MM-DD")

    verified_date = parsed_dates.get("verified_on")
    review_due_date = parsed_dates.get("review_due_on")
    if verified_date is not None and verified_date > date.today():
        errors.append("verification.verified_on is in the future")
    if verified_date is not None and review_due_date is not None:
        if review_due_date < verified_date:
            errors.append(
                "verification.review_due_on must be on or after verification.verified_on"
            )
        elif review_due_date < date.today():
            errors.append("verification.review_due_on is stale")

    jurisdictions = data["scope"]["jurisdictions"]
    if not jurisdictions:
        errors.append("scope.jurisdictions must contain at least one jurisdiction")
    elif any(not item.strip() for item in jurisdictions):
        errors.append("scope.jurisdictions contains a blank value")
    elif len(jurisdictions) != len(set(jurisdictions)):
        errors.append("scope.jurisdictions contains a duplicate value")
    elif any(not JURISDICTION_PATTERN.fullmatch(item) for item in jurisdictions):
        errors.append(
            "scope.jurisdictions contains a value that is not code-shaped; use uppercase country or subdivision code syntax"
        )


def validate_contract(data: Any) -> dict[str, Any]:
    structural_errors: list[str] = []
    declaration_errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return _result(None, ["root must be an object"], [], warnings)
    mode = data.get("mode")
    if data.get("schema_version") == 1:
        return _result(
            mode,
            [
                "schema v1 is no longer supported; migrate to the v2 activation manifest using capability-contract.example.json"
            ],
            [],
            warnings,
        )

    _check_structure(data, structural_errors)
    if data.get("schema_version") != 2 and not any(
        error.startswith("schema_version must") for error in structural_errors
    ):
        structural_errors.append("schema_version must be 2")
    if isinstance(mode, str) and mode not in MODES:
        structural_errors.append(f"mode must be one of: {', '.join(sorted(MODES))}")

    if structural_errors:
        return _result(mode, structural_errors, declaration_errors, warnings)

    enabled = [
        name for name in CAPABILITIES if data["capabilities"][name]["enabled"]
    ]
    for name in CAPABILITIES:
        capability = data["capabilities"][name]
        profile_ref = capability["control_profile_ref"]
        if capability["enabled"] and _is_placeholder(profile_ref):
            declaration_errors.append(
                f"capabilities.{name}.control_profile_ref must be verified when enabled"
            )
        elif not capability["enabled"] and profile_ref is not None:
            declaration_errors.append(
                f"capabilities.{name}.control_profile_ref must be null while the capability is disabled"
            )

    if data["scope"]["adult_only"] is not True:
        declaration_errors.append("scope.adult_only must be true")
    if mode != "capability-enabled" and data["governance_profile_ref"] is not None:
        declaration_errors.append(
            "governance_profile_ref must be null outside capability-enabled mode"
        )

    if mode == "disabled":
        if enabled:
            declaration_errors.append(
                "disabled mode cannot enable capabilities: " + ", ".join(enabled)
            )
        if not declaration_errors:
            warnings.append("coaching activation is disabled")
    else:
        _check_active_baseline(data, declaration_errors)
        if mode == "routine-adult-no-coaching-memory" and enabled:
            declaration_errors.append(
                "routine-adult-no-coaching-memory mode cannot enable optional capabilities: "
                + ", ".join(enabled)
            )
        if mode == "capability-enabled":
            if not enabled:
                declaration_errors.append(
                    "capability-enabled mode requires at least one enabled capability"
                )
            if _is_placeholder(data["governance_profile_ref"]):
                declaration_errors.append(
                    "governance_profile_ref must be verified in capability-enabled mode"
                )

    return _result(
        mode,
        structural_errors,
        declaration_errors,
        warnings,
        enabled,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="path to a host-owned v2 manifest")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = json.loads(
            args.contract.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 1

    result = validate_contract(data)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['status']}: mode={result['mode']}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
        for error in result["errors"]:
            print(f"error: {error}", file=sys.stderr)
        print("note: this validates declarations, not live implementation")

    if not result["declarations_valid"]:
        return 1
    if not result["active_declarations_valid"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
