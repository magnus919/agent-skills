#!/usr/bin/env python3
"""neckbeard evaluation runner.

Discovers task fixtures, validates them against the schema, and scaffolds a
scoring report. Standard library only.

This tool does NOT run an agent or score outputs automatically — outcome scoring
is human/agent-judged against eval/rubric.md. The runner's jobs are:
  1. validate that every fixture is well-formed (schema check),
  2. report suite composition (classes, public vs. holdout, adversarial coverage),
  3. scaffold a report from templates/eval-report.md with the fixtures listed.

Usage:
  python3 run_eval.py --suite fixtures --report out/report.md
  python3 run_eval.py --suite fixtures --validate-only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = ["id", "class", "prompt", "ground_truth", "expected_boundary", "visibility"]
VALID_CLASSES = {
    "bug-diagnosis", "feature-change", "refactor", "spec-ambiguity",
    "regression-prevention", "review-finding", "release-verification",
    "no-change-needed", "adversarial",
}
VALID_BOUNDARIES = {"unit", "integration", "end-to-end", "production"}
VALID_VISIBILITY = {"public", "holdout"}


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
        errors.append(f"{path}: invalid class '{cls}' (expected one of {sorted(VALID_CLASSES)})")

    boundary = data.get("expected_boundary")
    if boundary and boundary not in VALID_BOUNDARIES:
        errors.append(f"{path}: invalid expected_boundary '{boundary}'")

    visibility = data.get("visibility")
    if visibility and visibility not in VALID_VISIBILITY:
        errors.append(f"{path}: invalid visibility '{visibility}'")

    fixture_id = data.get("id")
    if fixture_id and fixture_id != path.parent.name:
        errors.append(f"{path}: id '{fixture_id}' does not match directory name '{path.parent.name}'")

    if cls == "adversarial" and not data.get("adversarial_intent"):
        errors.append(f"{path}: adversarial fixture must state 'adversarial_intent'")

    return errors


def summarize(fixtures: list[Path]) -> dict:
    by_class: dict[str, int] = {}
    by_visibility: dict[str, int] = {}
    adversarial = 0
    for path in fixtures:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
        by_class[data.get("class", "unknown")] = by_class.get(data.get("class", "unknown"), 0) + 1
        by_visibility[data.get("visibility", "unknown")] = by_visibility.get(data.get("visibility", "unknown"), 0) + 1
        if data.get("class") == "adversarial":
            adversarial += 1
    return {"by_class": by_class, "by_visibility": by_visibility, "adversarial": adversarial}


def scaffold_report(suite: Path, fixtures: list[Path], summary: dict) -> str:
    lines = [
        "# Evaluation Report (scaffold)",
        "",
        f"Suite: `{suite}` — {len(fixtures)} fixture(s).",
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
        f"Visibility: {summary['by_visibility']}. Adversarial fixtures: {summary['adversarial']}.",
        "",
        "> Fill in run identity, arms, and per-dimension scores per eval/rubric.md and",
        "> templates/eval-report.md. Scope every claim to model/harness/repo/task/date.",
        "",
        "## Fixtures",
        "",
    ]
    for path in fixtures:
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
        lines.append(
            f"- `{data.get('id', path.parent.name)}` — class={data.get('class', '?')}, "
            f"boundary={data.get('expected_boundary', '?')}, visibility={data.get('visibility', '?')}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="neckbeard evaluation runner")
    parser.add_argument("--suite", required=True, help="path to the fixtures directory")
    parser.add_argument("--report", help="write a report scaffold to this path")
    parser.add_argument("--validate-only", action="store_true", help="only validate fixtures, then exit")
    args = parser.parse_args()

    suite = Path(args.suite)
    if not suite.is_dir():
        print(f"error: suite directory not found: {suite}", file=sys.stderr)
        return 2

    fixtures = find_fixtures(suite)
    if not fixtures:
        print(f"error: no task.yaml fixtures found under {suite}", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for path in fixtures:
        all_errors.extend(validate_fixture(path))

    if all_errors:
        print("Fixture validation FAILED:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    summary = summarize(fixtures)
    print(f"OK: {len(fixtures)} fixture(s) valid.")
    print(f"  by class: {summary['by_class']}")
    print(f"  by visibility: {summary['by_visibility']}")
    print(f"  adversarial: {summary['adversarial']}")

    if args.validate_only:
        return 0

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(scaffold_report(suite, fixtures, summary), encoding="utf-8")
        print(f"Report scaffold written to {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
