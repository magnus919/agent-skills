#!/usr/bin/env python3
"""Validate a life-coach deployment capability contract.

This checks declared structure and conservative activation rules. It does not
prove that a deployment implements its declarations.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MODES = {"disabled", "routine-adult-ephemeral", "full-service"}
PLACEHOLDERS = {"", "<replace>", "unknown", "tbd", "todo"}

SECTIONS: dict[str, tuple[str, ...]] = {
    "accountability": (
        "deployer",
        "accountable_operator",
        "human_contact",
        "complaints_contact",
        "incident_owner",
    ),
    "identity": (
        "ai_disclosed",
        "credential_claims_disabled",
        "human_presence_claims_disabled",
    ),
    "population": (
        "adult_only",
        "minor_pathway_verified",
        "vulnerable_adult_safeguarding_verified",
        "jurisdictions",
    ),
    "safety": (
        "narrow_fallback_verified",
        "crisis_protocol_verified",
        "medical_emergency_protocol_verified",
        "self_harm_protocol_verified",
        "harm_to_others_protocol_verified",
        "abuse_and_trafficking_protocol_verified",
        "domestic_violence_digital_safety_verified",
        "safeguarding_human_review_verified",
        "location_behavior_documented",
        "protocol_owner",
    ),
    "privacy": (
        "data_flow_documented",
        "subprocessors_documented",
        "telemetry_documented",
        "model_training_use_documented",
        "embeddings_documented",
        "backups_documented",
        "access_roles_documented",
        "retention_documented",
        "correction_export_documented",
        "deletion_propagation_verified",
        "breach_contact_documented",
    ),
    "records": (
        "durable_memory_enabled",
        "record_types_separated",
        "raw_transcripts_disabled_by_default",
        "sensitive_narratives_disabled_by_default",
    ),
    "sponsors": (
        "sponsored_coaching_enabled",
        "separate_agreements_required",
        "technical_separation_verified",
        "coercion_review_verified",
        "reidentification_review_verified",
        "prohibited_disclosures_enforced",
    ),
    "tools": (
        "sensitive_actions_enabled",
        "per_action_preview_verified",
        "per_action_confirmation_verified",
        "crisis_and_coercion_lockout_verified",
    ),
    "contact": (
        "proactive_contact_enabled",
        "notification_privacy_verified",
        "frequency_and_stop_controls_verified",
        "dependency_tapering_verified",
    ),
    "human_governance": (
        "independent_coaching_supervision_verified",
        "clinical_safeguarding_consultation_verified",
        "privacy_security_review_verified",
        "accessibility_review_verified",
        "cultural_language_review_verified",
        "review_sample_governance_verified",
    ),
    "operations": (
        "critical_eval_suite_passed",
        "model_change_regression_gate_verified",
        "rollback_verified",
        "disablement_verified",
        "incident_process_verified",
    ),
}

STRING_FIELDS = {
    "accountability": set(SECTIONS["accountability"]),
    "safety": {"protocol_owner"},
}
LIST_FIELDS = {"population": {"jurisdictions"}}


def _present(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() not in PLACEHOLDERS


def _require_true(data: dict[str, Any], paths: list[tuple[str, str]], errors: list[str]) -> None:
    for section, field in paths:
        if data[section][field] is not True:
            errors.append(f"{section}.{field} must be true")


def validate_contract(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return {"valid": False, "eligible": False, "mode": None, "errors": ["root must be an object"], "warnings": []}

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    mode = data.get("operating_mode")
    if mode not in MODES:
        errors.append(f"operating_mode must be one of: {', '.join(sorted(MODES))}")

    if not isinstance(data.get("last_verified"), str) or not data.get("last_verified", "").strip():
        errors.append("last_verified must be a non-empty string")

    for section, fields in SECTIONS.items():
        value = data.get(section)
        if not isinstance(value, dict):
            errors.append(f"{section} must be an object")
            continue
        for field in fields:
            if field not in value:
                errors.append(f"missing {section}.{field}")
                continue
            if field in STRING_FIELDS.get(section, set()):
                if not isinstance(value[field], str):
                    errors.append(f"{section}.{field} must be a string")
            elif field in LIST_FIELDS.get(section, set()):
                if not isinstance(value[field], list) or not all(isinstance(item, str) for item in value[field]):
                    errors.append(f"{section}.{field} must be an array of strings")
            elif not isinstance(value[field], bool):
                errors.append(f"{section}.{field} must be a boolean")

    if errors:
        return {"valid": False, "eligible": False, "mode": mode, "errors": errors, "warnings": warnings}

    if mode == "disabled":
        warnings.append("coaching is disabled; complete and verify the contract before activation")
        return {"valid": True, "eligible": False, "mode": mode, "errors": [], "warnings": warnings}

    for field in SECTIONS["accountability"]:
        if not _present(data["accountability"][field]):
            errors.append(f"accountability.{field} must be verified and must not be a placeholder")

    _require_true(
        data,
        [
            ("identity", "ai_disclosed"),
            ("identity", "credential_claims_disabled"),
            ("identity", "human_presence_claims_disabled"),
            ("population", "adult_only"),
            ("safety", "narrow_fallback_verified"),
            ("records", "raw_transcripts_disabled_by_default"),
            ("records", "sensitive_narratives_disabled_by_default"),
            ("sponsors", "separate_agreements_required"),
        ],
        errors,
    )

    if mode == "routine-adult-ephemeral":
        if data["records"]["durable_memory_enabled"]:
            errors.append("routine-adult-ephemeral mode cannot enable durable memory")
        if data["sponsors"]["sponsored_coaching_enabled"]:
            errors.append("routine-adult-ephemeral mode cannot enable sponsored coaching")
        if data["tools"]["sensitive_actions_enabled"]:
            errors.append("routine-adult-ephemeral mode cannot enable sensitive actions")
        if data["contact"]["proactive_contact_enabled"]:
            errors.append("routine-adult-ephemeral mode cannot enable proactive contact")
        if data["population"]["minor_pathway_verified"]:
            warnings.append("minor pathway is ignored; this public skill remains adult-only")
    elif mode == "full-service":
        full_true: list[tuple[str, str]] = []
        for section in ("safety", "privacy", "human_governance", "operations"):
            for field in SECTIONS[section]:
                if field not in STRING_FIELDS.get(section, set()):
                    full_true.append((section, field))
        full_true.append(("records", "record_types_separated"))
        _require_true(data, full_true, errors)
        if not _present(data["safety"]["protocol_owner"]):
            errors.append("safety.protocol_owner must be verified and must not be a placeholder")
        if not data["population"]["jurisdictions"]:
            errors.append("population.jurisdictions must name at least one reviewed jurisdiction")

        if data["records"]["durable_memory_enabled"]:
            _require_true(
                data,
                [
                    ("privacy", "correction_export_documented"),
                    ("privacy", "deletion_propagation_verified"),
                    ("records", "record_types_separated"),
                ],
                errors,
            )
        if data["sponsors"]["sponsored_coaching_enabled"]:
            _require_true(
                data,
                [
                    ("sponsors", "technical_separation_verified"),
                    ("sponsors", "coercion_review_verified"),
                    ("sponsors", "reidentification_review_verified"),
                    ("sponsors", "prohibited_disclosures_enforced"),
                ],
                errors,
            )
        if data["tools"]["sensitive_actions_enabled"]:
            _require_true(
                data,
                [
                    ("tools", "per_action_preview_verified"),
                    ("tools", "per_action_confirmation_verified"),
                    ("tools", "crisis_and_coercion_lockout_verified"),
                ],
                errors,
            )
        if data["contact"]["proactive_contact_enabled"]:
            _require_true(
                data,
                [
                    ("contact", "notification_privacy_verified"),
                    ("contact", "frequency_and_stop_controls_verified"),
                    ("contact", "dependency_tapering_verified"),
                ],
                errors,
            )

    return {
        "valid": not errors,
        "eligible": not errors,
        "mode": mode,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="path to capability-contract JSON")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 1

    result = validate_contract(data)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        label = "ELIGIBLE" if result["eligible"] else ("VALID BUT DISABLED" if result["valid"] else "INVALID")
        print(f"{label}: operating_mode={result['mode']}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
        for error in result["errors"]:
            print(f"error: {error}", file=sys.stderr)
        print("note: this validates declarations, not live implementation")

    if not result["valid"]:
        return 1
    if not result["eligible"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
