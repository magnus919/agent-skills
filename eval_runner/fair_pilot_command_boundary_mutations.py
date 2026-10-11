"""Finite source-code mutation sensitivity check for the command-boundary reference.

The five gate mutants and equivalent control run existing regression tests
against temporary, mutated copies of the pinned command-boundary source module.
Results describe test sensitivity only; they are not production coverage evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "eval_runner" / "fair_pilot_command_boundary.py"
REGRESSION_TESTS = ROOT / "eval_runner" / "tests" / "test_fair_pilot_command_boundary.py"

# These pins freeze the source and regression test file used for this finite run.
EXPECTED_IMPLEMENTATION_SHA256 = "b5777c9d7f69e370e3aa96c5b19918d525ba2557514a97b8ed0534485878a7fc"
EXPECTED_TESTS_SHA256 = "a963f2e8184b5c423f4f56d2a3c1e3317737a16dfd652d92f179d6aec98ee8d2"

_FOCUSED_TEST = "eval_runner/tests/test_fair_pilot_command_boundary.py"
_POST_APPROVAL_MUTATIONS = (
    f"{_FOCUSED_TEST}::test_post_approval_mutations_return_to_review_without_writes"
)

SOURCE_MUTANTS: tuple[dict[str, Any], ...] = (
    {
        "id": "bypass-current-permission-gate",
        "replacements": (("if self.current_permission is not True:", "if False:"),),
        "tests": (_POST_APPROVAL_MUTATIONS,),
    },
    {
        "id": "bypass-record-revision-gates",
        "replacements": (
            (
                "if command.expected_record_revision != self.approval.record_revision:",
                "if False:",
            ),
            (
                "if self.current_record_revision != self.approval.record_revision:",
                "if False:",
            ),
        ),
        "tests": (_POST_APPROVAL_MUTATIONS,),
    },
    {
        "id": "bypass-policy-version-gates",
        "replacements": (
            ("if command.policy_version != self.approval.policy_version:", "if False:"),
            ("if self.current_policy_version != self.approval.policy_version:", "if False:"),
        ),
        "tests": (_POST_APPROVAL_MUTATIONS,),
    },
    {
        "id": "bypass-exact-approved-action-gate",
        "replacements": (("if command.action != self.approval.action:", "if False:"),),
        "tests": (_POST_APPROVAL_MUTATIONS,),
    },
    {
        "id": "bypass-identical-replay-response-deduplication",
        "scope": "response-only; the executed-state gate still prevents a second write",
        "replacements": (("if completed == command:", "if False:"),),
        "tests": (
            f"{_FOCUSED_TEST}::test_identical_new_command_replay_deduplicates_after_revocation",
        ),
    },
)

EQUIVALENT_CONTROL = {
    "id": "permission-bool-equivalent-spelling",
    "replacements": (
        ("if self.current_permission is not True:", "if self.current_permission is False:"),
    ),
    "tests": (_FOCUSED_TEST,),
}


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _mutate(original: str, replacements: tuple[tuple[str, str], ...]) -> str:
    mutated = original
    for anchor, replacement in replacements:
        if mutated.count(anchor) != 1:
            raise ValueError(f"source anchor is absent or ambiguous: {anchor!r}")
        mutated = mutated.replace(anchor, replacement, 1)
    if mutated == original:
        raise ValueError("mutation produced no source change")
    compile(mutated, str(IMPLEMENTATION), "exec")
    return mutated


def _run_tests(
    mutated_source: str, test_nodes: tuple[str, ...], regression_test_bytes: bytes
) -> dict[str, Any]:
    """Run exact existing regression tests with a temporary module overlay."""
    with tempfile.TemporaryDirectory(prefix="fair-command-boundary-mutation-") as directory:
        overlay = Path(directory)
        package = overlay / "eval_runner"
        tests_dir = package / "tests"
        tests_dir.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "fair_pilot_command_boundary.py").write_text(mutated_source, encoding="utf-8")
        (tests_dir / "test_fair_pilot_command_boundary.py").write_bytes(regression_test_bytes)
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(overlay) + (
            os.pathsep + existing_pythonpath if existing_pythonpath else ""
        )
        command = [sys.executable, "-m", "pytest", "-q", "--no-cov", *test_nodes]
        try:
            result = subprocess.run(
                command,
                cwd=overlay,
                env=env,
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"kind": "infrastructure_error", "error": f"{type(exc).__name__}: {exc}"}

        output = f"{result.stdout}\n{result.stderr}"
        summary = [
            line.strip() for line in output.splitlines() if " passed" in line or " failed" in line
        ]
        if result.returncode == 0:
            return {"kind": "passed", "returncode": 0, "summary": summary[-1:]}
        if "AssertionError" in output and " failed" in output and "ERROR collecting" not in output:
            return {
                "kind": "test_failure",
                "returncode": result.returncode,
                "summary": summary[-1:],
            }
        return {
            "kind": "infrastructure_error",
            "returncode": result.returncode,
            "summary": summary[-2:],
            "detail": output[-4000:],
        }


def run_mutation_suite() -> dict[str, Any]:
    """Run five source mutants and one equivalent control against pinned tests."""
    source_bytes = IMPLEMENTATION.read_bytes()
    test_bytes = REGRESSION_TESTS.read_bytes()
    source_hash = _sha256(source_bytes)
    test_hash = _sha256(test_bytes)
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "pass",
        "evidence_classification": "finite mutation sensitivity only",
        "source": {"path": str(IMPLEMENTATION.relative_to(ROOT)), "sha256": source_hash},
        "regression_tests": {
            "path": _FOCUSED_TEST,
            "sha256": test_hash,
        },
        "baseline": None,
        "source_mutants": {"killed": [], "survived": []},
        "equivalent_control": {"passed": [], "changed_behavior": []},
        "invalid_mutants": [],
        "infrastructure_errors": [],
        "limitations": [
            "These results measure sensitivity of the pinned in-memory reference tests only.",
            "They do not establish production runtime behavior, deployed authority, or P0 closure.",
            "The mutation set is deliberately limited to five source mutants and one equivalent control.",
        ],
    }

    if source_hash != EXPECTED_IMPLEMENTATION_SHA256 or test_hash != EXPECTED_TESTS_SHA256:
        report["status"] = "fail"
        report["invalid_mutants"].append(
            {
                "id": "pinned-input-integrity",
                "reason": "source or regression-test hash differs from the frozen mutation input",
            }
        )
        return report

    original = source_bytes.decode("utf-8")
    baseline = _run_tests(original, (_FOCUSED_TEST,), test_bytes)
    report["baseline"] = baseline
    if baseline["kind"] != "passed":
        report["status"] = "fail"
        report["infrastructure_errors"].append({"id": "baseline", **baseline})
        return report

    for mutant in SOURCE_MUTANTS:
        mutant_id = cast(str, mutant["id"])
        try:
            mutated = _mutate(original, cast(tuple[tuple[str, str], ...], mutant["replacements"]))
        except (SyntaxError, ValueError) as exc:
            report["invalid_mutants"].append({"id": mutant_id, "reason": str(exc)})
            continue
        result = _run_tests(mutated, cast(tuple[str, ...], mutant["tests"]), test_bytes)
        row = {"id": mutant_id, "test_outcome": result}
        if "scope" in mutant:
            row["scope"] = mutant["scope"]
        if result["kind"] == "test_failure":
            report["source_mutants"]["killed"].append(row)
        elif result["kind"] == "passed":
            report["source_mutants"]["survived"].append(row)
        else:
            report["infrastructure_errors"].append(row)

    try:
        equivalent_source = _mutate(
            original, cast(tuple[tuple[str, str], ...], EQUIVALENT_CONTROL["replacements"])
        )
    except (SyntaxError, ValueError) as exc:
        report["invalid_mutants"].append({"id": EQUIVALENT_CONTROL["id"], "reason": str(exc)})
    else:
        equivalent_result = _run_tests(
            equivalent_source, cast(tuple[str, ...], EQUIVALENT_CONTROL["tests"]), test_bytes
        )
        equivalent_row = {"id": EQUIVALENT_CONTROL["id"], "test_outcome": equivalent_result}
        if equivalent_result["kind"] == "passed":
            report["equivalent_control"]["passed"].append(equivalent_row)
        elif equivalent_result["kind"] == "test_failure":
            report["equivalent_control"]["changed_behavior"].append(equivalent_row)
        else:
            report["infrastructure_errors"].append(equivalent_row)

    if (
        len(report["source_mutants"]["killed"]) != 5
        or report["source_mutants"]["survived"]
        or len(report["equivalent_control"]["passed"]) != 1
        or report["equivalent_control"]["changed_behavior"]
        or report["invalid_mutants"]
        or report["infrastructure_errors"]
    ):
        report["status"] = "fail"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the complete structured report")
    args = parser.parse_args()
    try:
        report = run_mutation_suite()
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        report = {"status": "infrastructure_error", "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(report, indent=2 if args.json else None, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
