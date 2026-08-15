#!/usr/bin/env python3
"""Use-case risk-tier classifier for the ai-governance skill.

Reads a structured JSON description of an AI use case (data sensitivity,
autonomy, exposure, and decision impact), computes a governance risk tier
(low / medium / high) and the controls that tier requires, and reports the
result.

Behavior contract:

* ``--json`` emits a single JSON object to stdout containing the keys ``tier``
  (string) and ``controls`` (array).
* Exit code 0 on valid input; exit code 1 on missing, malformed, or
  semantically-invalid input (with an explanatory message on stderr).
* ``--dry-run`` is a true preview: the tool is read-only and never writes files,
  so a dry-run's ``--json`` output is byte-identical to the real run's.
* Output is deterministic: no timestamps, stable ordering, and sorted keys.

This is a defensible default classifier for intake triage; it does not replace a
full model risk assessment (see ``model-risk-assessment.md``). Expert judgment
should confirm the tier before it is recorded in the risk register.

Standard library only. No third-party runtime dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# Allowed values per dimension, mapped to their inherent-risk contribution.
# These follow the vocabulary used by the intake form and model-risk-assessment
# templates.
DATA_SENSITIVITY: dict[str, int] = {
    "public": 1,
    "internal": 2,
    "confidential": 3,
    "personal": 4,
    "sensitive_personal": 5,
    "regulated": 5,
}

AUTONOMY: dict[str, int] = {
    "human_in_the_loop": 1,
    "human_on_the_loop": 2,
    "fully_automated": 3,
}

EXPOSURE: dict[str, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

DECISION_IMPACT: dict[str, int] = {
    "informational": 1,
    "operational": 2,
    "financial": 3,
    "life_liberty": 4,
}

LEVEL_MAPS: dict[str, dict[str, int]] = {
    "data_sensitivity": DATA_SENSITIVITY,
    "autonomy": AUTONOMY,
    "exposure": EXPOSURE,
    "decision_impact": DECISION_IMPACT,
}

REQUIRED = ("data_sensitivity", "autonomy", "exposure", "decision_impact")
OPTIONAL = ("use_case", "notes")

# Data sensitivity and decision impact weigh twice as heavily as autonomy and
# exposure because they are the principal drivers of inherent risk.
WEIGHTED = ("data_sensitivity", "decision_impact")
SENSITIVITY_WEIGHT = 2
AUTONOMY_WEIGHT = 1

# Weighted-score thresholds for the tier (scores range 6..24).
HIGH_SCORE = 15
MEDIUM_SCORE = 10

# Values that force the high tier regardless of the weighted score.
FORCED_HIGH_SENSITIVITY = ("sensitive_personal", "regulated")
FORCED_HIGH_IMPACT = ("life_liberty",)

# Ordered control sets. Tier controls are cumulative; driver-specific controls
# are added when the matching dimension is present. Duplicates are collapsed.
CONTROL_BASE: tuple[str, ...] = (
    "register_in_inventory_and_risk_register",
    "document_in_model_or_data_card",
)
CONTROL_MEDIUM: tuple[str, ...] = (
    "bias_and_fairness_review",
    "monitoring_and_drift_detection",
    "privacy_and_minimization_review",
    "human_review_and_override_path",
)
CONTROL_HIGH: tuple[str, ...] = (
    "full_nist_rmf_aligned_risk_assessment",
    "independent_validation",
    "board_or_ai_council_approval",
    "audit_trail_and_logging",
    "security_review_and_red_teaming",
)
CONTROL_SENSITIVE_DATA: tuple[str, ...] = (
    "privacy_impact_assessment",
    "data_protection_and_access_controls",
)
CONTROL_HIGH_IMPACT: tuple[str, ...] = (
    "human_in_the_loop_final_decision",
    "appeal_and_redress_process",
)
CONTROL_AUTONOMY: tuple[str, ...] = ("automated_decision_oversight",)
CONTROL_EXPOSURE: tuple[str, ...] = ("scaled_monitoring_and_escalation",)


def validate_use_case(data: Any) -> dict[str, str]:
    """Validate the parsed JSON payload and return its dimension levels.

    Raises ``ValueError`` with a human-readable message when the payload is not
    the expected shape: a top-level object with exactly the four required
    dimensions (each an allowed string value), plus the optional ``use_case``
    and ``notes`` string fields.
    """
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    unknown = sorted(set(data) - set(REQUIRED) - set(OPTIONAL))
    if unknown:
        raise ValueError("unexpected key(s): " + ", ".join(unknown))
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError("missing required key(s): " + ", ".join(missing))
    levels: dict[str, str] = {}
    for key in REQUIRED:
        value = data[key]
        if not isinstance(value, str):
            raise ValueError(f"'{key}' must be a string, got {value!r}")
        allowed = sorted(LEVEL_MAPS[key])
        if value not in LEVEL_MAPS[key]:
            raise ValueError(f"'{key}' value {value!r} not in {allowed}")
        levels[key] = value
    for key in OPTIONAL:
        if key in data and not isinstance(data[key], str):
            raise ValueError(f"'{key}' must be a string, got {data[key]!r}")
    return levels


def _weighted_score(levels: dict[str, str]) -> int:
    total = 0
    for key, weight in (
        (k, SENSITIVITY_WEIGHT if k in WEIGHTED else AUTONOMY_WEIGHT) for k in REQUIRED
    ):
        total += weight * LEVEL_MAPS[key][levels[key]]
    return total


def _derive_tier(levels: dict[str, str], total: int) -> str:
    if (
        levels["data_sensitivity"] in FORCED_HIGH_SENSITIVITY
        or levels["decision_impact"] in FORCED_HIGH_IMPACT
    ):
        return "high"
    if total >= HIGH_SCORE:
        return "high"
    if total >= MEDIUM_SCORE:
        return "medium"
    return "low"


def _derive_controls(tier: str, levels: dict[str, str]) -> list[str]:
    controls: list[str] = list(CONTROL_BASE)
    if tier in ("medium", "high"):
        controls.extend(CONTROL_MEDIUM)
    if tier == "high":
        controls.extend(CONTROL_HIGH)
    if levels["data_sensitivity"] in ("personal", "sensitive_personal", "regulated"):
        controls.extend(CONTROL_SENSITIVE_DATA)
    if levels["decision_impact"] in ("financial", "life_liberty"):
        controls.extend(CONTROL_HIGH_IMPACT)
    if levels["autonomy"] == "fully_automated":
        controls.extend(CONTROL_AUTONOMY)
    if levels["exposure"] == "high":
        controls.extend(CONTROL_EXPOSURE)
    seen: set[str] = set()
    deduped: list[str] = []
    for control in controls:
        if control not in seen:
            seen.add(control)
            deduped.append(control)
    return deduped


def compute_risk(levels: dict[str, str]) -> dict[str, Any]:
    """Compute the risk tier and required controls for validated levels.

    Returns a dict with ``tier`` (string), ``total_score`` (int), the four
    dimension levels echoed back, and ``controls`` (a list of control names).
    """
    total = _weighted_score(levels)
    tier = _derive_tier(levels, total)
    return {
        "tier": tier,
        "total_score": total,
        "data_sensitivity": levels["data_sensitivity"],
        "autonomy": levels["autonomy"],
        "exposure": levels["exposure"],
        "decision_impact": levels["decision_impact"],
        "controls": _derive_controls(tier, levels),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Classify the governance risk tier and required controls for an AI "
            "use case from a JSON file of dimension levels."
        )
    )
    parser.add_argument(
        "use_case_file",
        help=(
            "path to a JSON file with data_sensitivity, autonomy, exposure, "
            "and decision_impact levels"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the result as a single JSON object on stdout",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview the result without writing anything (this tool is read-only)",
    )
    return parser.parse_args(argv)


def _fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        with open(args.use_case_file, encoding="utf-8") as handle:
            raw = handle.read()
    except OSError as exc:
        return _fail(f"cannot read use-case file '{args.use_case_file}': {exc}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"invalid JSON in '{args.use_case_file}': {exc}")

    try:
        levels = validate_use_case(data)
    except ValueError as exc:
        return _fail(str(exc))

    result = compute_risk(levels)

    if args.json:
        print(
            json.dumps(
                result,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
    else:
        _render_human(result)

    return 0


def _render_human(result: dict[str, Any]) -> None:
    header = (
        f"Risk tier: {result['tier']} "
        f"(score {result['total_score']}; "
        f"sensitivity={result['data_sensitivity']}, "
        f"autonomy={result['autonomy']}, "
        f"exposure={result['exposure']}, "
        f"impact={result['decision_impact']})"
    )
    print(header)
    print("Required controls:")
    for control in result["controls"]:
        print(f"  - {control}")


if __name__ == "__main__":
    raise SystemExit(main())
