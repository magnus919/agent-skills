"""Comparison report generation for paired evaluation trials."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .grader import GradeResult

COMPARISON_SCHEMA_VERSION = 1


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

    if candidate_passed and not baseline_passed:
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
        "paired_delta": delta,
    }


def write_comparison_report(report: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    case_id = report.get("case_id", "unknown")
    report_id = report.get("report_id", "unknown")[:8]
    path = output_dir / f"{case_id}--{report_id}.comparison.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def format_comparison_summary(report: dict[str, Any]) -> str:
    lines = [
        f"Skill: {report['skill_name']}  Case: {report['case_id']}",
        f"Delta: {report['paired_delta']}",
        "",
        f"  Candidate: {'PASS' if report['candidate']['passed'] else 'FAIL'}"
        f" ({report['candidate']['pass_count']} pass, {report['candidate']['fail_count']} fail,"
        f" {report['candidate']['manual_count']} manual)",
        f"  Baseline:  {'PASS' if report['baseline']['passed'] else 'FAIL'}"
        f" ({report['baseline']['pass_count']} pass, {report['baseline']['fail_count']} fail,"
        f" {report['baseline']['manual_count']} manual)",
    ]
    if report["candidate"]["infra_error"]:
        lines.append("  [!] Candidate had infrastructure error")
    if report["baseline"]["infra_error"]:
        lines.append("  [!] Baseline had infrastructure error")
    return "\n".join(lines)
