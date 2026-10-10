#!/usr/bin/env python3
"""Validate curated case-review records and report distinct evidence lanes.

The checklist is an intentionally curated review register, not a row-per-case
mirror of every eval manifest. Missing rows are reported as absent coverage;
they are not errors and are never synthesized as reviewed records.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "lifecycle-evals/references/case-quality-checklist.json"
ADJUDICATION = ROOT / "docs/fair-skill-evaluation-adjudication-run-38021806973-v1.json"
EXCLUDED_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
TEST_SOURCE_SUFFIXES = {
    ".bats",
    ".bash",
    ".cjs",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".pl",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
}

sys.path.insert(0, str(ROOT))
from eval_runner.assertion_syntax import classify_assertion  # noqa: E402


def _manifest_paths(root: Path) -> list[Path]:
    paths = []
    for path in root.rglob("evals/evals.json"):
        relative = path.relative_to(root)
        if EXCLUDED_PARTS.intersection(relative.parts):
            continue
        if "agent-council/profiles/skills" in relative.as_posix():
            continue
        skill_root = path.parent.parent
        if (skill_root / "SKILL.md").is_file():
            paths.append(path)
    return sorted(paths)


def manifest_inventory(root: Path = ROOT) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Return canonical cases keyed by skill-root path and stable case ID."""
    cases: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in _manifest_paths(root):
        skill = path.parent.parent.relative_to(root).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(root)}: cannot read manifest: {exc}")
            continue
        evals = data.get("evals") if isinstance(data, dict) else None
        if not isinstance(evals, list):
            errors.append(f"{path.relative_to(root)}: evals must be a list")
            continue
        for case in evals:
            if not isinstance(case, dict) or not isinstance(case.get("id"), str):
                errors.append(f"{path.relative_to(root)}: case is missing a string id")
                continue
            case_id = case["id"]
            key = f"{skill}\0{case_id}"
            if key in cases:
                errors.append(f"duplicate canonical case: {skill}/{case_id}")
                continue
            assertions = case.get("assertions", [])
            if not isinstance(assertions, list):
                errors.append(f"{skill}/{case_id}: assertions must be a list")
                assertions = []
            syntax_counts: Counter[str] = Counter()
            for assertion in assertions:
                parsed = classify_assertion(assertion) if isinstance(assertion, str) else None
                syntax_counts[parsed.syntax.value if parsed else "malformed_value"] += 1
            cases[key] = {
                "skill": skill,
                "case_id": case_id,
                "assertion_count": len(assertions),
                "assertion_syntax": dict(sorted(syntax_counts.items())),
            }
    return cases, errors


def _load_checklist(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"cannot read checklist: {exc}"]
    rows = data.get("rows") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return [], ["checklist rows must be a list"]
    errors = []
    valid_rows = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"checklist row {index + 1} must be an object")
            continue
        if not all(
            isinstance(row.get(key), str) and row[key].strip() for key in ("skill", "case_id")
        ):
            errors.append(f"checklist row {index + 1} needs nonempty skill and case_id strings")
            continue
        valid_rows.append(row)
    return valid_rows, errors


def validate(path: Path = CHECKLIST, root: Path = ROOT) -> list[str]:
    """Reject malformed, duplicate, and orphan review records; omissions are valid."""
    cases, errors = manifest_inventory(root)
    rows, row_errors = _load_checklist(path)
    errors.extend(row_errors)
    keys = [(row["skill"], row["case_id"]) for row in rows]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    known = {(item["skill"], item["case_id"]) for item in cases.values()}
    actual = set(keys)
    if duplicates:
        errors.append(f"duplicate checklist rows: {duplicates}")
    if actual - known:
        errors.append(f"orphan checklist rows: {sorted(actual - known)}")
    adjudication_path = root / ADJUDICATION.relative_to(ROOT)
    if adjudication_path.is_file():
        try:
            record = json.loads(adjudication_path.read_text(encoding="utf-8"))
            canonical_record = copy.deepcopy(record)
            digest = canonical_record.get("integrity", {}).pop("sha256", None)
            calculated = hashlib.sha256(
                json.dumps(
                    canonical_record,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
            ).hexdigest()
            if digest != calculated:
                errors.append("independent adjudication companion integrity hash does not match")
        except (OSError, json.JSONDecodeError, AttributeError, TypeError):
            errors.append("independent adjudication companion is malformed")
    return errors


def _tracked_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        )
        return [path for path in result.stdout.decode().split("\0") if path]
    except (OSError, subprocess.CalledProcessError):
        return [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]


def _is_test_source(path: str) -> bool:
    name = Path(path).name
    if Path(name).suffix not in TEST_SOURCE_SUFFIXES:
        return False
    return name.startswith(("test_", "test-")) or name.endswith(
        ("_test.py", "_test.rb", "_test.sh", "-test.py", "-test.rb", "-test.sh", ".bats")
    )


def test_routing_inventory(root: Path = ROOT) -> dict[str, Any]:
    """Classify repository test sources by the selectors CI actually declares."""
    files = sorted(path for path in _tracked_files(root) if _is_test_source(path))
    core_file = root / "scripts/core-test-files.txt"
    core_paths = (
        [
            line.strip()
            for line in core_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if core_file.exists()
        else []
    )
    core_selected: set[str] = set()
    for selected in core_paths:
        target = root / selected
        if target.is_file():
            core_selected.add(selected)
        elif target.is_dir():
            core_selected.update(
                path
                for path in files
                if path == selected or path.startswith(selected.rstrip("/") + "/")
            )

    workflow_text = (
        "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in (root / ".github/workflows").glob("*.y*ml")
        )
        if (root / ".github/workflows").exists()
        else ""
    )
    shell_run: set[str] = set()
    shell_manual: set[str] = set()
    registry = root / "scripts/check-skill-tests.py"
    if registry.is_file():
        tree = ast.parse(registry.read_text(encoding="utf-8"))
        for node in tree.body:
            value: ast.expr | None
            if isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names = [node.target.id]
                value = node.value
            else:
                continue
            if value is None:
                continue
            if "RUN_TESTS" in names:
                shell_run = {item[0] for item in ast.literal_eval(value)}
            elif "MANUAL_TESTS" in names:
                shell_manual = set(ast.literal_eval(value))
    skill_auto = {
        path
        for path in files
        if "/scripts/test_" in f"/{path}"
        and path.endswith(".py")
        and any(
            (root / parent / "SKILL.md").is_file()
            for parent in Path(path).parents
            if parent != Path(".")
        )
    }
    integration = {path for path in files if path.startswith("tests/integration/")}
    workflow_explicit = {path for path in files if path in workflow_text}
    routes: dict[str, list[str]] = {
        "core_manifest": sorted(core_selected),
        "skill_local_python_autodiscovery": sorted(skill_auto - core_selected),
        "registered_skill_shell_run": sorted(shell_run - core_selected - skill_auto),
        "registered_skill_shell_manual": sorted(
            shell_manual - core_selected - skill_auto - shell_run
        ),
        "integration_suite": sorted(
            integration - core_selected - skill_auto - shell_run - shell_manual
        ),
        "workflow_explicit_path": sorted(
            workflow_explicit - core_selected - skill_auto - shell_run - shell_manual - integration
        ),
    }
    routed = set().union(*(set(items) for items in routes.values()))
    unclassified = sorted(set(files) - routed)
    return {
        "test_source_count": len(files),
        "core_manifest_entries": core_paths,
        "routed_counts": {key: len(value) for key, value in routes.items()},
        "unclassified_count": len(unclassified),
        "unclassified_paths": unclassified,
        "interpretation": "Unclassified means no route was identified by these declared selectors; it is a follow-up queue, not proof a test is never run.",
    }


def _run_artifact_inventory(root: Path, known_cases: set[tuple[str, str]]) -> dict[str, Any]:
    artifact_root = root / "lifecycle-evals/run-artifacts/manifests"
    adapters: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    matched_cases: set[tuple[str, str]] = set()
    malformed = 0
    count = 0
    if artifact_root.exists():
        for path in sorted(artifact_root.glob("*.manifest.json")):
            count += 1
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                malformed += 1
                continue
            if not isinstance(record, dict):
                malformed += 1
                continue
            status = record.get("status")
            statuses[str(status or "unknown")] += 1
            candidate = record.get("candidate") or {}
            case = record.get("case") or {}
            adapter = record.get("adapter") or record.get("harness") or {}
            if not all(isinstance(item, dict) for item in (candidate, case, adapter)):
                malformed += 1
                continue
            adapters[str(adapter.get("name", "unknown"))] += 1
            key = (str(candidate.get("skill_path", "")), str(case.get("case_id", "")))
            if key in known_cases:
                matched_cases.add(key)
            else:
                malformed += 1
    return {
        "artifact_count": count,
        "status_counts": dict(sorted(statuses.items())),
        "adapter_counts": dict(sorted(adapters.items())),
        "unique_cases_linked_to_current_manifests": len(matched_cases),
        "malformed_or_unmatched_count": malformed,
        "scope": "Stored lifecycle corpus run artifacts only. Completed fake-adapter runs evidence execution/serialization, not model behavior or semantic verification.",
    }


def build_inventory(root: Path = ROOT, checklist: Path | None = None) -> dict[str, Any]:
    checklist = checklist or root / "lifecycle-evals/references/case-quality-checklist.json"
    cases, manifest_errors = manifest_inventory(root)
    rows, row_errors = _load_checklist(checklist)
    known_case_rows = {(item["skill"], item["case_id"]) for item in cases.values()}
    row_keys = {(row["skill"], row["case_id"]) for row in rows}
    syntax_counts: Counter[str] = Counter()
    cases_with_manual = 0
    for case in cases.values():
        manual = False
        for syntax, count in case["assertion_syntax"].items():
            syntax_counts[syntax] += count
            manual = manual or syntax != "exact"
        cases_with_manual += int(manual)
    top_level = sum("/" not in item["skill"] for item in cases.values())
    nested = len(cases) - top_level
    manifest_paths = _manifest_paths(root)
    top_manifests = sum(
        len(path.parent.parent.relative_to(root).parts) == 1 for path in manifest_paths
    )
    nested_manifests = len(manifest_paths) - top_manifests
    verdicts = Counter(str(row.get("verdict", "unspecified")) for row in rows)
    reviewers = Counter(str(row.get("reviewer", "unspecified")) for row in rows)

    independent = {"record_count": 0, "case_count": 0, "reviewer_kind": "not_assessed"}
    adjudication_path = root / ADJUDICATION.relative_to(ROOT)
    if adjudication_path.is_file():
        try:
            record = json.loads(adjudication_path.read_text(encoding="utf-8"))
            digest = record.get("integrity", {}).get("sha256")
            canonical_record = copy.deepcopy(record)
            canonical_record.get("integrity", {}).pop("sha256", None)
            calculated = hashlib.sha256(
                json.dumps(
                    canonical_record,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
            ).hexdigest()
            independent = {
                "record_count": 1,
                "case_count": len(record.get("cases", [])),
                "reviewer_kind": record.get("reviewer", {}).get("kind", "unknown"),
                "artifact": adjudication_path.relative_to(root).as_posix(),
                "integrity_hash_valid": digest == calculated,
            }
        except (OSError, json.JSONDecodeError, AttributeError, TypeError):
            independent["reviewer_kind"] = "invalid_record"

    return {
        "schema_version": 1,
        "manifest_inventory": {
            "manifests": len(manifest_paths),
            "top_level_manifests": top_manifests,
            "nested_manifests": nested_manifests,
            "cases": len(cases),
            "top_level_cases": top_level,
            "nested_cases": nested,
            "parse_or_shape_errors": len(manifest_errors),
        },
        "oracle_inventory": {
            "assertions_by_syntax": dict(sorted(syntax_counts.items())),
            "cases_with_any_unresolved_or_prose_assertion": cases_with_manual,
        },
        "case_review_records": {
            "rows_present": len(rows),
            "unique_known_cases_with_row": len(row_keys & known_case_rows),
            "cases_without_row": len(known_case_rows - row_keys),
            "recorded_verdict_values": dict(sorted(verdicts.items())),
            "recorded_reviewer_values": dict(sorted(reviewers.items())),
            "independent_review_provenance": "not inferable from legacy reviewer/verdict fields; see separate adjudication companion where available",
            "parse_errors": len(row_errors),
        },
        "execution_evidence": _run_artifact_inventory(root, known_case_rows),
        "independent_adjudication": independent,
        "eval_selection": {
            "nested_manifest_count": nested_manifests,
            "nested_case_count": nested,
            "selector": "eval_runner.selection.manifests_for_paths",
            "policy": "Attribute changed paths to the deepest real skill root; fail closed above the five-skill cap rather than silently truncating.",
            "regression_test": "eval_runner/tests/test_selection.py",
        },
        "verified_behavioral_coverage": {
            "assessment": "not_assessed_repository_wide",
            "reason": "No repository-wide contract maps every case to independently verified behavioral evidence. Structural validation, fake execution, and case-review rows are reported separately.",
        },
        "test_routing": test_routing_inventory(root),
        "validation_errors": validate(checklist, root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the evidence inventory as JSON")
    args = parser.parse_args()
    report = build_inventory()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        manifest = report["manifest_inventory"]
        reviews = report["case_review_records"]
        runs = report["execution_evidence"]
        routes = report["test_routing"]
        print(
            f"Manifests: {manifest['manifests']} ({manifest['top_level_manifests']} top-level, "
            f"{manifest['nested_manifests']} nested); cases: {manifest['cases']} "
            f"({manifest['top_level_cases']} top-level, {manifest['nested_cases']} nested)."
        )
        print(
            f"Case-review rows present: {reviews['rows_present']}; cases without rows: "
            f"{reviews['cases_without_row']} (curated omissions are allowed)."
        )
        print(
            f"Stored run artifacts: {runs['artifact_count']}; test-like sources: "
            f"{routes['test_source_count']}; unclassified by declared selectors: "
            f"{routes['unclassified_count']}."
        )
        print("Verified behavioral coverage: not assessed repository-wide.")
        if report["validation_errors"]:
            print("\n".join(report["validation_errors"]), file=sys.stderr)
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
