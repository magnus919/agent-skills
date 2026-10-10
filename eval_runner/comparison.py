"""Comparison report generation for paired evaluation trials."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .grader import GradeResult
from .path_safety import contained_path, validate_case_id

COMPARISON_SCHEMA_VERSION = 3


def build_comparison_report(
    *,
    skill_name: str,
    case_id: str,
    candidate_grade: GradeResult,
    baseline_grade: GradeResult,
    candidate_manifest: dict[str, Any],
    baseline_manifest: dict[str, Any],
) -> dict[str, Any]:
    candidate_passed = candidate_grade.passed
    baseline_passed = baseline_grade.passed

    if candidate_grade.infra_error or baseline_grade.infra_error:
        delta = "insufficient_data"
    elif (
        candidate_grade.semantic_verdict == "not_assessed"
        or baseline_grade.semantic_verdict == "not_assessed"
        or not candidate_grade.evidence_complete
        or not baseline_grade.evidence_complete
    ):
        delta = "insufficient_evidence"
    elif candidate_passed and not baseline_passed:
        delta = "candidate_improvement"
    elif not candidate_passed and baseline_passed:
        delta = "candidate_regression"
    elif candidate_passed and baseline_passed:
        delta = "both_pass"
    else:
        delta = "both_fail"

    return {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "report_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_name": skill_name,
        "case_id": case_id,
        "candidate": {
            "trial_id": candidate_manifest.get("trial_id", ""),
            "execution_status": candidate_grade.execution_status,
            "execution_success": candidate_grade.execution_success,
            "semantic_verdict": candidate_grade.semantic_verdict,
            "evidence_complete": candidate_grade.evidence_complete,
            "assertion_count": candidate_grade.assertion_count,
            "resolved_count": candidate_grade.resolved_count,
            "passed": candidate_passed,
            "infra_error": candidate_grade.infra_error,
            "pass_count": candidate_grade.pass_count,
            "fail_count": candidate_grade.fail_count,
            "manual_count": candidate_grade.manual_count,
            "assertions": [
                {"assertion": r.assertion, "verdict": r.verdict.value, "detail": r.detail}
                for r in candidate_grade.results
            ],
            "manifest": candidate_manifest,
        },
        "baseline": {
            "trial_id": baseline_manifest.get("trial_id", ""),
            "execution_status": baseline_grade.execution_status,
            "execution_success": baseline_grade.execution_success,
            "semantic_verdict": baseline_grade.semantic_verdict,
            "evidence_complete": baseline_grade.evidence_complete,
            "assertion_count": baseline_grade.assertion_count,
            "resolved_count": baseline_grade.resolved_count,
            "passed": baseline_passed,
            "infra_error": baseline_grade.infra_error,
            "pass_count": baseline_grade.pass_count,
            "fail_count": baseline_grade.fail_count,
            "manual_count": baseline_grade.manual_count,
            "assertions": [
                {"assertion": r.assertion, "verdict": r.verdict.value, "detail": r.detail}
                for r in baseline_grade.results
            ],
            "manifest": baseline_manifest,
        },
        "aggregate_outcome": {
            "candidate_semantic_verdict": candidate_grade.semantic_verdict,
            "baseline_semantic_verdict": baseline_grade.semantic_verdict,
            "comparison_status": (
                "comparable"
                if delta
                in {
                    "candidate_improvement",
                    "candidate_regression",
                    "both_pass",
                    "both_fail",
                }
                else delta
            ),
        },
        "paired_delta": delta,
    }


def write_comparison_report(report: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    case_id = report.get("case_id", "unknown")
    validate_case_id(case_id)
    report_id = report.get("report_id", "unknown")[:8]
    path = contained_path(output_dir, f"{case_id}--{report_id}.comparison.json")
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def format_comparison_summary(report: dict[str, Any]) -> str:
    def trial_summary(side: str) -> str:
        trial = report[side]
        semantic = trial.get("semantic_verdict")
        if semantic is None:
            # Archived v2 reports used ``passed`` for both completed triage
            # and semantic outcomes, so unresolved evidence must stay unknown.
            if trial.get("fail_count", 0):
                semantic_label = "FAIL (legacy report)"
            elif trial.get("manual_count", 0):
                semantic_label = "NOT ASSESSED (legacy report)"
            elif trial.get("passed") and trial.get("pass_count", 0) > 0:
                semantic_label = "PASS (legacy report)"
            elif not trial.get("passed") and trial.get("fail_count", 0) > 0:
                semantic_label = "FAIL (legacy report)"
            else:
                semantic_label = "NOT ASSESSED (legacy report)"
        else:
            semantic_label = {
                "pass": "PASS",
                "fail": "FAIL",
                "not_assessed": "NOT ASSESSED",
            }.get(semantic, "UNKNOWN")
        execution = trial.get("execution_status", "legacy")
        return (
            f"  {side.title()}: {semantic_label}"
            f" ({trial['pass_count']} pass, {trial['fail_count']} fail,"
            f" {trial['manual_count']} unresolved;"
            f" evidence {trial.get('resolved_count', trial['pass_count'] + trial['fail_count'])}"
            f"/{trial.get('assertion_count', trial['pass_count'] + trial['fail_count'] + trial['manual_count'])};"
            f" execution {execution})"
        )

    paired_delta = report["paired_delta"]
    if "aggregate_outcome" not in report and any(
        report.get(side, {}).get("manual_count", 0) > 0 for side in ("candidate", "baseline")
    ):
        paired_delta = "not assessed (legacy report)"
    lines = [
        f"Skill: {report['skill_name']}  Case: {report['case_id']}",
        f"Delta: {paired_delta}",
        "",
        trial_summary("candidate"),
        trial_summary("baseline"),
    ]
    if report["candidate"]["infra_error"]:
        lines.append("  [!] Candidate had infrastructure error")
    if report["baseline"]["infra_error"]:
        lines.append("  [!] Baseline had infrastructure error")
    if report["candidate"]["infra_error"] or report["baseline"]["infra_error"]:
        lines.append(
            "  [!] Paired comparison not assessed because a trial had an infrastructure error"
        )
    elif report["paired_delta"] == "insufficient_evidence":
        lines.append(
            "  [!] Semantic comparison not assessed because required assertion evidence is unresolved"
        )
    return "\n".join(lines)
