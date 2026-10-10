"""Bounded offline policy mutants against the shipped JSON CLI pipeline.

This is a contract-mechanics check for the fictional policy only. Its expected
rows were transcribed from clause text independently of the implementation;
they are not policy-owner approval or skill-quality evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "eval_runner" / "fair-pilot-policy-oracle-v1.json"
IMPLEMENTATION = ROOT / "spec-driven-development" / "scripts" / "business_policy.py"
SOURCE = ROOT / "spec-driven-development" / "references" / "executable-business-policy.md"

UNCOVERED_CHECKS = [
    "Human review of UX interaction quality and observed usability evidence.",
    "Human review of generated PydanticAI prose for app-owned permission and revision checks.",
    "Human review that discovery answers do not invent interviews or omit stakeholder conflicts.",
    "Human review of Raleigh answer honesty and live-data completeness beyond offline query-shape tests.",
    "Human review of System One conceptual evidence and qualification recommendations.",
    "Policy-owner validation that the fictional clauses and their interpretation match a real authority.",
]

MUTANTS: tuple[dict[str, str], ...] = (
    {
        "id": "include-v2-effective-start-in-v1",
        "class": "valid_defect",
        "anchor": "pickup < p.end",
        "replacement": "pickup <= p.end",
        "probe_case": "v2-effective-start-and-limit",
    },
    {
        "id": "reject-days-equal-to-v2-limit",
        "class": "valid_defect",
        "anchor": 'facts["days"] > policy.max_days',
        "replacement": 'facts["days"] >= policy.max_days',
        "probe_case": "v2-effective-start-and-limit",
    },
    {
        "id": "let-exception-suppress-unavailable-denial",
        "class": "valid_defect",
        "anchor": 'if not facts["available"]:',
        "replacement": 'if not facts["available"] and not facts["exception"]:',
        "probe_case": "unavailable-beats-exception",
    },
    {
        "id": "default-a-missing-pickup-date",
        "class": "valid_defect",
        "anchor": 'date.fromisoformat(facts["pickup_date"])',
        "replacement": 'date.fromisoformat(facts.get("pickup_date", "2026-07-01"))',
        "probe_case": "missing-pickup-date",
    },
    {
        "id": "commute-duration-comparison",
        "class": "equivalent",
        "anchor": 'facts["days"] > policy.max_days',
        "replacement": 'policy.max_days < facts["days"]',
        "probe_case": "v2-over-limit",
    },
    {
        "id": "unmatched-source-anchor",
        "class": "invalid",
        "anchor": "if facts.get('intentionally-absent-anchor'):",
        "replacement": "if True:",
        "probe_case": "v2-over-limit",
    },
    {
        "id": "controlled-runtime-error",
        "class": "infrastructure_error",
        "anchor": 'pickup = date.fromisoformat(facts["pickup_date"])',
        "replacement": 'raise RuntimeError("mutation infrastructure sentinel")',
        "probe_case": "v2-over-limit",
    },
)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _load_fixture() -> dict[str, Any]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("unsupported policy oracle fixture version")
    if _sha256(SOURCE.read_bytes()) != data["source"]["sha256"]:
        raise ValueError("policy clause source pin mismatch")
    if _sha256(IMPLEMENTATION.read_bytes()) != data["implementation"]["sha256"]:
        raise ValueError("policy implementation pin mismatch")
    return cast(dict[str, Any], data)


def _invoke(source: str, facts: dict[str, Any]) -> tuple[int, dict[str, Any] | None, str]:
    with tempfile.TemporaryDirectory(prefix="fair-pilot-policy-") as directory:
        root = Path(directory)
        script = root / "business_policy.py"
        input_path = root / "request.json"
        script.write_text(source, encoding="utf-8")
        input_path.write_text(json.dumps(facts), encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(script), "--input", str(input_path)],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return 125, None, type(exc).__name__
        try:
            output = json.loads(result.stdout) if result.stdout.strip() else None
        except json.JSONDecodeError:
            output = None
        return result.returncode, output, result.stderr


def _gap_overlap_controls() -> bool:
    spec = importlib.util.spec_from_file_location("fair_pilot_policy", IMPLEMENTATION)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned policy evaluator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from datetime import date

    facts = {"pickup_date": "2026-06-15", "days": 1, "available": True, "exception": False}
    gap = (
        module.Policy("before", date(2026, 1, 1), date(2026, 6, 1), 7),
        module.Policy("after", date(2026, 7, 1), None, 5),
    )
    overlap = (
        module.Policy("first", date(2026, 1, 1), date(2026, 8, 1), 7),
        module.Policy("second", date(2026, 6, 1), None, 5),
    )
    return bool(
        module.evaluate(facts, gap).reason == "policy_selection"
        and module.evaluate(facts, overlap).reason == "policy_selection"
    )


def run_mutation_suite() -> dict[str, Any]:
    """Run the pinned fixture through actual CLI invocations and bounded mutants."""
    fixture = _load_fixture()
    original = IMPLEMENTATION.read_text(encoding="utf-8")
    cases = {row["id"]: row for row in fixture["cases"]}
    baseline_failures = []
    for row in fixture["cases"]:
        status, output, stderr = _invoke(original, row["facts"])
        if status != 0 or output != row["expected"]:
            baseline_failures.append(
                {"case_id": row["id"], "returncode": status, "output": output, "stderr": stderr}
            )

    report: dict[str, Any] = {
        "status": "pass",
        "fixture_sha256": _sha256(FIXTURE.read_bytes()),
        "source_sha256": _sha256(SOURCE.read_bytes()),
        "implementation_sha256": _sha256(IMPLEMENTATION.read_bytes()),
        "baseline": {
            "case_count": len(fixture["cases"]),
            "failures": baseline_failures,
            "gap_and_overlap_controls_passed": _gap_overlap_controls(),
        },
        "valid_defects": {"killed": [], "survived": []},
        "equivalent_mutants": {"accepted": [], "changed_behavior": []},
        "invalid_mutants": [],
        "infrastructure_errors": [],
        "uncovered_checks": UNCOVERED_CHECKS,
    }
    for mutant in MUTANTS:
        anchor = mutant["anchor"]
        if original.count(anchor) != 1:
            report["invalid_mutants"].append(
                {"id": mutant["id"], "reason": "source anchor is absent or ambiguous"}
            )
            continue
        mutated = original.replace(anchor, mutant["replacement"], 1)
        probe = cases[mutant["probe_case"]]
        status, output, stderr = _invoke(mutated, probe["facts"])
        result = {"id": mutant["id"], "probe_case": probe["id"]}
        if mutant["class"] == "valid_defect":
            if status != 0:
                report["infrastructure_errors"].append(
                    {**result, "returncode": status, "expected_control": False, "stderr": stderr}
                )
            else:
                bucket = "killed" if output != probe["expected"] else "survived"
                report["valid_defects"][bucket].append({**result, "output": output})
        elif mutant["class"] == "equivalent":
            if status != 0:
                report["infrastructure_errors"].append(
                    {**result, "returncode": status, "expected_control": False, "stderr": stderr}
                )
            else:
                bucket = "accepted" if output == probe["expected"] else "changed_behavior"
                report["equivalent_mutants"][bucket].append({**result, "returncode": status})
        elif mutant["class"] == "invalid":
            # A declared invalid transformation is only accepted when it cannot
            # be applied to the pinned source. Valid mutations must be explicit.
            raise AssertionError("invalid-mutant anchor unexpectedly applied")
        elif mutant["class"] == "infrastructure_error":
            report["infrastructure_errors"].append(
                {
                    **result,
                    "returncode": status,
                    "expected_control": status != 0
                    and "mutation infrastructure sentinel" in stderr,
                }
            )
    from .fair_pilot_qualification import build_qualification_report

    qualification = build_qualification_report()
    report["semantic_mutation_controls"] = {
        "status": qualification["status"],
        "request_count": qualification["request_count"],
        "split_counts": qualification["split_counts"],
        "sample_kind_counts": qualification["sample_kind_counts"],
        "proposed_label_counts": qualification["proposed_label_counts"],
        "artifact_and_source_hash_preflight": "passed",
        "semantic_paraphrase_pairs": 1,
        "label_review_status": "pending_independent_agent_review",
        "dispatch_authorized": qualification["dispatch_authorized"],
    }
    if (
        baseline_failures
        or not report["baseline"]["gap_and_overlap_controls_passed"]
        or report["valid_defects"]["survived"]
        or report["equivalent_mutants"]["changed_behavior"]
        or not report["invalid_mutants"]
        or not report["infrastructure_errors"]
        or any(not row["expected_control"] for row in report["infrastructure_errors"])
        or qualification["status"] != "ready_for_independent_agent_review_not_dispatch"
    ):
        report["status"] = "fail"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the complete structured report")
    args = parser.parse_args()
    try:
        report = run_mutation_suite()
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        report = {"status": "infrastructure_error", "error": str(exc)}
    print(json.dumps(report, indent=2 if args.json else None, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
