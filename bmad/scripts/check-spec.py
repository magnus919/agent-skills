#!/usr/bin/env python3
"""Validate BMad SPEC files: required five sections and status vocabulary.

Checks that a SPEC.md (or INTENT.md) contains the five core contract fields
(Why, Capabilities, Constraints, Non-goals, Success signal) and that the
frontmatter ``status`` field, when present, is one of the six vocabulary
values (draft, ready-for-dev, in-progress, in-review, done, blocked).

Exit codes: 0 = all files valid, 1 = at least one invalid or unreadable file.

Standard library only; usable in CI or by any harness that can run python3.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

STATUS_VOCABULARY = (
    "draft",
    "ready-for-dev",
    "in-progress",
    "in-review",
    "done",
    "blocked",
)

REQUIRED_SECTIONS = (
    "Why",
    "Capabilities",
    "Constraints",
    "Non-goals",
    "Success signal",
)

HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.DOTALL)


@dataclass
class SpecReport:
    """Validation result for one spec file."""

    path: str
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def extract_frontmatter(text: str) -> dict[str, str]:
    """Parse YAML frontmatter as a flat key/value map (no YAML dependency)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, raw = stripped.partition(":")
        raw = raw.strip()
        value = raw.strip("'\"") if raw[:1] in ("'", '"') else raw.split(" #", 1)[0].strip()
        fields[key.strip()] = value
    return fields


def collect_headings(text: str) -> list[str]:
    """Return the text of every markdown heading outside code blocks."""
    headings: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            fence = None if fence is not None else stripped[:3]
            continue
        if fence is not None:
            continue
        if line.startswith(("    ", "\t")):
            continue  # indented code block
        match = HEADING_RE.match(stripped)
        if match:
            headings.append(match.group(1).strip())
    return headings


def section_present(headings: list[str], required: str) -> bool:
    """True when a heading matches the required section name."""
    return any(heading.lower() == required.lower() for heading in headings)


def validate_spec(path: Path) -> SpecReport:
    """Validate a single spec file and return its report."""
    report = SpecReport(path=str(path))
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        report.valid = False
        report.errors.append(f"cannot read file: {exc}")
        return report

    frontmatter = extract_frontmatter(text)
    headings = collect_headings(text)

    status = frontmatter.get("status")
    if status is not None:
        if status not in STATUS_VOCABULARY:
            report.valid = False
            report.errors.append(
                f"invalid status {status!r}; expected one of " + ", ".join(STATUS_VOCABULARY)
            )
    else:
        report.warnings.append("no 'status' in frontmatter; add one when the work is resumable")

    missing = [name for name in REQUIRED_SECTIONS if not section_present(headings, name)]
    if missing:
        report.valid = False
        report.errors.append("missing required section(s): " + ", ".join(missing))

    return report


def render_text(reports: list[SpecReport]) -> str:
    """Human-readable summary of all reports."""
    lines: list[str] = []
    for report in reports:
        verdict = "PASS" if report.valid else "FAIL"
        lines.append(f"{verdict} {report.path}")
        for warning in report.warnings:
            lines.append(f"  warning: {warning}")
        for error in report.errors:
            lines.append(f"  error: {error}")
    valid = sum(1 for report in reports if report.valid)
    lines.append(f"{valid}/{len(reports)} spec(s) valid")
    return "\n".join(lines)


def render_json(reports: list[SpecReport]) -> str:
    """Machine-readable summary of all reports."""
    payload = {
        "valid": all(report.valid for report in reports),
        "files": [
            {
                "path": report.path,
                "valid": report.valid,
                "errors": report.errors,
                "warnings": report.warnings,
            }
            for report in reports
        ],
    }
    return json.dumps(payload, indent=2)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate BMad spec files: required sections and status vocabulary."
    )
    parser.add_argument(
        "files", nargs="+", type=Path, help="SPEC.md or INTENT.md files to validate"
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of text"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    reports = [validate_spec(path) for path in args.files]
    output = render_json(reports) if args.json else render_text(reports)
    print(output)
    return 0 if all(report.valid for report in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
