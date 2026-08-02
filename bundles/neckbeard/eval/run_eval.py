#!/usr/bin/env python3
"""neckbeard evaluation runner.

Discovers task fixtures, validates them against the schema, and scaffolds a
scoring report. Standard library only.

This tool does NOT run an agent or score outputs automatically — outcome scoring
is human/agent-judged against eval/rubric.md. The runner's jobs are:
  1. validate that every fixture is well-formed (schema check),
  2. report suite composition (classes, public vs. holdout, adversarial coverage),
  3. scaffold a report from templates/eval-report.md with the fixtures listed.

Supports two fixture kinds:
  - single-task: flat key-value fixtures (the original format)
  - trajectory: multi-phase journey fixtures (kind: trajectory)

Usage:
  python3 run_eval.py --suite fixtures --report out/report.md
  python3 run_eval.py --suite fixtures --validate-only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --- single-task fixture schema ---

REQUIRED_FIELDS = ["id", "class", "prompt", "ground_truth", "expected_boundary", "visibility"]
VALID_CLASSES = {
    "bug-diagnosis", "feature-change", "refactor", "spec-ambiguity",
    "regression-prevention", "review-finding", "release-verification",
    "no-change-needed", "adversarial",
}
VALID_BOUNDARIES = {"unit", "integration", "end-to-end", "production"}
VALID_VISIBILITY = {"public", "holdout"}

# --- trajectory fixture schema ---

TRAJECTORY_REQUIRED_FIELDS = [
    "kind", "id", "path", "prompt", "phases", "gates", "terminal_state", "visibility",
]
VALID_PATHS = {"lightweight", "full", "refactor", "high-risk"}
VALID_TERMINAL_STATES = {"merged", "closed", "blocked", "released"}
VALID_GATE_IDS = {"gate-1", "gate-2", "gate-3", "gate-4", "gate-5"}
VALID_GATE_VERDICTS = {"pass", "conditional", "blocked"}

JOURNEY_PHASES = {
    "1": "Intake and provenance",
    "2": "Current-state discovery and reproduction",
    "3": "Architecture/design delta and risk assessment",
    "4": "Specification and work decomposition",
    "5": "Pre-implementation test and verification planning",
    "6": "Domain-specific implementation",
    "7": "Independent review and boundary verification",
    "8": "Readiness, CI/review feedback loops, and exact-final-head re-verification",
    "9": "Authorized post-merge release and closeout",
}


def parse_simple_yaml(text: str) -> dict:
    """Parse the flat key: value subset our fixtures use. No nesting, no lists.

    Deliberately minimal — fixtures are flat mappings of scalars. If a fixture
    needs structure, keep it in a sibling file and reference it from `context`.
    """
    data: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key] = value
    return data


def find_fixtures(suite: Path) -> list[Path]:
    return sorted(suite.glob("**/task.yaml"))


# --- single-task validation ---


def validate_fixture(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"{path}: cannot read: {exc}"]

    for field in REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f"{path}: missing required field '{field}'")

    cls = data.get("class")
    if cls and cls not in VALID_CLASSES:
        errors.append(
            f"{path}: invalid class '{cls}' (expected one of {sorted(VALID_CLASSES)})"
        )

    boundary = data.get("expected_boundary")
    if boundary and boundary not in VALID_BOUNDARIES:
        errors.append(f"{path}: invalid expected_boundary '{boundary}'")

    visibility = data.get("visibility")
    if visibility and visibility not in VALID_VISIBILITY:
        errors.append(f"{path}: invalid visibility '{visibility}'")

    fixture_id = data.get("id")
    if fixture_id and fixture_id != path.parent.name:
        errors.append(
            f"{path}: id '{fixture_id}' does not match directory name '{path.parent.name}'"
        )

    if cls == "adversarial" and not data.get("adversarial_intent"):
        errors.append(f"{path}: adversarial fixture must state 'adversarial_intent'")

    return errors


# --- trajectory validation helpers ---


def _parse_pipe_entries(value: str) -> list[str]:
    """Split a pipe-separated field value into stripped entries."""
    return [part.strip() for part in value.split("|") if part.strip()]


def _validate_phase_labels(path: Path, field: str, value: str, *, with_reason: bool) -> list[str]:
    """Validate phase entries like '1: Intake and provenance' (or with ': reason')."""
    errors: list[str] = []
    for entry in _parse_pipe_entries(value):
        m = re.match(r"^(\d+):\s*(.+)$", entry)
        if not m:
            errors.append(f"{path}: {field} entry is not 'N: Phase Name': '{entry}'")
            continue
        num, rest = m.group(1), m.group(2).strip()
        if num not in JOURNEY_PHASES:
            errors.append(f"{path}: {field} references unknown phase number {num}")
            continue
        expected = JOURNEY_PHASES[num]
        phase_name = rest
        if with_reason:
            # Format: "N: Phase Name: reason" — split on the LAST colon after the name
            idx = rest.find(": ")
            if idx == -1:
                errors.append(
                    f"{path}: {field} phase {num} entry lacks a skip reason: '{entry}'"
                )
                continue
            phase_name = rest[:idx].strip()
        if phase_name != expected:
            errors.append(
                f"{path}: {field} phase {num} label '{phase_name}' "
                f"does not match journey.md: '{expected}'"
            )
    return errors


def _validate_gate_labels(path: Path, field: str, value: str, *, with_verdict: bool) -> list[str]:
    """Validate gate entries like 'gate-1: description: pass' or 'gate-1: reason'."""
    errors: list[str] = []
    for entry in _parse_pipe_entries(value):
        m = re.match(r"^(gate-\d+):\s*(.+)$", entry)
        if not m:
            errors.append(f"{path}: {field} entry is not 'gate-N: ...': '{entry}'")
            continue
        gate_id, rest = m.group(1), m.group(2).strip()
        if gate_id not in VALID_GATE_IDS:
            errors.append(
                f"{path}: {field} references unknown gate '{gate_id}' "
                f"(expected one of {sorted(VALID_GATE_IDS)})"
            )
            continue
        if with_verdict:
            # Format: "gate-N: description: verdict"
            parts = rest.rsplit(":", 1)
            if len(parts) != 2:
                errors.append(
                    f"{path}: {field} entry for {gate_id} lacks a verdict: '{entry}'"
                )
                continue
            verdict = parts[1].strip()
            if verdict not in VALID_GATE_VERDICTS:
                errors.append(
                    f"{path}: {field} verdict '{verdict}' for {gate_id} "
                    f"is not one of {sorted(VALID_GATE_VERDICTS)}"
                )
    return errors


def validate_trajectory_fixture(path: Path) -> list[str]:
    """Validate a trajectory fixture against the trajectory sub-schema."""
    errors: list[str] = []
    try:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"{path}: cannot read: {exc}"]

    for field in TRAJECTORY_REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f"{path}: missing required field '{field}'")

    kind = data.get("kind")
    if kind and kind != "trajectory":
        errors.append(f"{path}: kind must be 'trajectory', got '{kind}'")

    fixture_id = data.get("id")
    if fixture_id and fixture_id != path.parent.name:
        errors.append(
            f"{path}: id '{fixture_id}' does not match directory name '{path.parent.name}'"
        )

    path_value = data.get("path")
    if path_value and path_value not in VALID_PATHS:
        errors.append(
            f"{path}: invalid path '{path_value}' (expected one of {sorted(VALID_PATHS)})"
        )

    terminal = data.get("terminal_state")
    if terminal and terminal not in VALID_TERMINAL_STATES:
        errors.append(
            f"{path}: invalid terminal_state '{terminal}' "
            f"(expected one of {sorted(VALID_TERMINAL_STATES)})"
        )

    visibility = data.get("visibility")
    if visibility and visibility not in VALID_VISIBILITY:
        errors.append(f"{path}: invalid visibility '{visibility}'")

    # Validate phase labels against journey.md canonical names
    phases = data.get("phases")
    if phases:
        errors.extend(_validate_phase_labels(path, "phases", phases, with_reason=False))

    skipped_phases = data.get("skipped_phases")
    if skipped_phases:
        errors.extend(
            _validate_phase_labels(path, "skipped_phases", skipped_phases, with_reason=True)
        )

    # Validate gate labels
    gates = data.get("gates")
    if gates:
        errors.extend(_validate_gate_labels(path, "gates", gates, with_verdict=True))

    skipped_gates = data.get("skipped_gates")
    if skipped_gates:
        errors.extend(
            _validate_gate_labels(path, "skipped_gates", skipped_gates, with_verdict=False)
        )

    # Full-path fixtures must traverse all nine phases and record all five gates
    if path_value == "full":
        if phases:
            phase_nums = set()
            for entry in _parse_pipe_entries(phases):
                m = re.match(r"^(\d+):", entry)
                if m:
                    phase_nums.add(m.group(1))
            missing = set(JOURNEY_PHASES) - phase_nums
            if missing:
                errors.append(
                    f"{path}: full-path fixture is missing phases: {sorted(missing)}"
                )
        if gates:
            gate_ids = set()
            for entry in _parse_pipe_entries(gates):
                m = re.match(r"^(gate-\d+):", entry)
                if m:
                    gate_ids.add(m.group(1))
            missing_gates = VALID_GATE_IDS - gate_ids
            if missing_gates:
                errors.append(
                    f"{path}: full-path fixture is missing gates: {sorted(missing_gates)}"
                )
        if not data.get("final_head_sha"):
            errors.append(f"{path}: full-path fixture must bind a final_head_sha")

    return errors


# --- summary and report ---


def summarize(task_fixtures: list[Path], trajectory_fixtures: list[Path]) -> dict:
    by_class: dict[str, int] = {}
    by_visibility: dict[str, int] = {}
    adversarial = 0
    for path in task_fixtures:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
        cls = data.get("class", "unknown")
        by_class[cls] = by_class.get(cls, 0) + 1
        vis = data.get("visibility", "unknown")
        by_visibility[vis] = by_visibility.get(vis, 0) + 1
        if cls == "adversarial":
            adversarial += 1
    trajectory_paths: dict[str, int] = {}
    for path in trajectory_fixtures:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
        p = data.get("path", "unknown")
        trajectory_paths[p] = trajectory_paths.get(p, 0) + 1
    return {
        "by_class": by_class,
        "by_visibility": by_visibility,
        "adversarial": adversarial,
        "trajectory_paths": trajectory_paths,
    }


def scaffold_report(
    suite: Path,
    task_fixtures: list[Path],
    trajectory_fixtures: list[Path],
    summary: dict,
) -> str:
    total = len(task_fixtures) + len(trajectory_fixtures)
    lines = [
        "# Evaluation Report (scaffold)",
        "",
        f"Suite: `{suite}` — {total} fixture(s) "
        f"({len(task_fixtures)} single-task, {len(trajectory_fixtures)} trajectory).",
        "",
        "## Suite composition",
        "",
        "| Class | Count |",
        "|---|---|",
    ]
    for cls in sorted(summary["by_class"]):
        lines.append(f"| {cls} | {summary['by_class'][cls]} |")
    lines += [
        "",
        f"Visibility: {summary['by_visibility']}. "
        f"Adversarial fixtures: {summary['adversarial']}.",
        "",
    ]
    if summary["trajectory_paths"]:
        lines += [
            "| Trajectory path | Count |",
            "|---|---|",
        ]
        for p in sorted(summary["trajectory_paths"]):
            lines.append(f"| {p} | {summary['trajectory_paths'][p]} |")
        lines.append("")
    lines += [
        "> Fill in run identity, arms, and per-dimension scores per eval/rubric.md and",
        "> templates/eval-report.md. Scope every claim to model/harness/repo/task/date.",
        "",
        "## Single-task fixtures",
        "",
    ]
    for path in task_fixtures:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
        lines.append(
            f"- `{data.get('id', path.parent.name)}` — "
            f"class={data.get('class', '?')}, "
            f"boundary={data.get('expected_boundary', '?')}, "
            f"visibility={data.get('visibility', '?')}"
        )
    if trajectory_fixtures:
        lines += ["", "## Trajectory fixtures", ""]
        for path in trajectory_fixtures:
            data = parse_simple_yaml(path.read_text(encoding="utf-8"))
            lines.append(
                f"- `{data.get('id', path.parent.name)}` — "
                f"path={data.get('path', '?')}, "
                f"terminal_state={data.get('terminal_state', '?')}, "
                f"visibility={data.get('visibility', '?')}"
            )
    lines.append("")
    return "\n".join(lines)


# --- main ---


def main() -> int:
    parser = argparse.ArgumentParser(description="neckbeard evaluation runner")
    parser.add_argument("--suite", required=True, help="path to the fixtures directory")
    parser.add_argument("--report", help="write a report scaffold to this path")
    parser.add_argument(
        "--validate-only", action="store_true", help="only validate fixtures, then exit"
    )
    args = parser.parse_args()

    suite = Path(args.suite)
    if not suite.is_dir():
        print(f"error: suite directory not found: {suite}", file=sys.stderr)
        return 2

    all_fixtures = find_fixtures(suite)
    if not all_fixtures:
        print(f"error: no task.yaml fixtures found under {suite}", file=sys.stderr)
        return 2

    # Classify fixtures by kind
    task_fixtures: list[Path] = []
    trajectory_fixtures: list[Path] = []
    for path in all_fixtures:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
        if data.get("kind") == "trajectory":
            trajectory_fixtures.append(path)
        else:
            task_fixtures.append(path)

    all_errors: list[str] = []
    for path in task_fixtures:
        all_errors.extend(validate_fixture(path))
    for path in trajectory_fixtures:
        all_errors.extend(validate_trajectory_fixture(path))

    if all_errors:
        print("Fixture validation FAILED:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK: {len(task_fixtures) + len(trajectory_fixtures)} fixture(s) valid.")
    print(f"  {len(task_fixtures)} single-task fixture(s) valid.")
    print(f"  {len(trajectory_fixtures)} trajectory fixture(s) valid.")

    if task_fixtures:
        summary = summarize(task_fixtures, trajectory_fixtures)
        print(f"  by class: {summary['by_class']}")
        print(f"  by visibility: {summary['by_visibility']}")
        print(f"  adversarial: {summary['adversarial']}")
    else:
        summary = summarize([], trajectory_fixtures)

    if trajectory_fixtures:
        print(f"  trajectory paths: {summary['trajectory_paths']}")

    if args.validate_only:
        return 0

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            scaffold_report(suite, task_fixtures, trajectory_fixtures, summary),
            encoding="utf-8",
        )
        print(f"Report scaffold written to {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
