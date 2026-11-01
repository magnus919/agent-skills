#!/usr/bin/env python3
"""Check that a review record is complete and internally consistent.

A review record is the durable artifact a reviewer writes when the verdict
matters: what was in scope, what evidence was gathered, what was found, what
the reviewer decided, and what they knowingly did not look at. This checker
holds the record to that contract.

It cannot tell whether the findings are *true* — that requires the evidence
the record cites. It catches the failure modes that make a review record
untrustworthy instead: a verdict that contradicts its own blocking findings,
findings with no evidence, an approval that never states residual risk, and
sections left as placeholders.

Usage:
    review_record_check.py review.md
    review_record_check.py review.md --json
    review_record_check.py review.md --strict

Exit codes:
    0  record satisfies the contract (warnings allowed unless --strict)
    1  record violates the contract
    2  usage error (missing or unreadable file)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_SECTIONS = (
    "scope",
    "evidence",
    "findings",
    "verdict",
    "residual risk",
    "not reviewed",
)

SEVERITIES = ("blocking", "should-fix", "nit", "question", "praise")
EVIDENCE_REQUIRED = ("blocking", "should-fix")

VERDICTS = {
    "approve": "APPROVE",
    "approve with comments": "APPROVE WITH COMMENTS",
    "request changes": "REQUEST CHANGES",
    "needs more evidence": "NEEDS MORE EVIDENCE",
}

PLACEHOLDERS = re.compile(r"^(?:todo|tbd|tba|n/?a|none|\.\.\.|-\s*)$", re.IGNORECASE)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
SEVERITY_LABEL = re.compile(r"^[-*+]\s+\[([^\]]+)\]\s*(.*)$")
COVERAGE_LINE = re.compile(r"coverage\s*[:=]\s*(full|partial)\b(.*)$", re.IGNORECASE)


@dataclass
class Finding:
    severity: str
    text: str
    line: int


@dataclass
class Record:
    sections: dict[str, list[str]] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    verdict: str | None = None
    verdict_line: int = 0


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    verdict: str | None = None
    coverage: str | None = None
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "valid": self.valid,
            "verdict": self.verdict,
            "coverage": self.coverage,
            "counts": self.counts,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def normalise_heading(text: str) -> str:
    text = re.sub(r"[`*_]", "", text).strip().lower()
    text = re.sub(r"^(?:section|part)\s+\d+\s*[:.\-]\s*", "", text)
    text = re.sub(r"^\d+\s*[:.\-]\s*", "", text)
    return re.sub(r"\s+", " ", text)


def split_sections(text: str) -> dict[str, list[str]]:
    """Group body lines under their top-most matched section heading."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    current_level = 0
    for line in text.splitlines():
        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            name = normalise_heading(heading.group(2))
            matched = next((s for s in REQUIRED_SECTIONS if name.startswith(s)), None)
            if matched:
                current = matched
                current_level = level
                sections.setdefault(current, [])
                continue
            # A sibling or parent heading ends the section; a deeper
            # sub-heading inside it (for example "### Blocking") does not.
            if level <= current_level:
                current = None
                current_level = 0
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def substantive(lines: list[str]) -> list[str]:
    entries = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # A bullet or heading marker is structure, not content: "- TBD" is a
        # placeholder, not a stated risk.
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        if PLACEHOLDERS.match(stripped):
            continue
        if stripped.startswith("<!--"):
            continue
        entries.append(stripped)
    return entries


def parse_findings(lines: list[str], offset: int = 0) -> list[Finding]:
    findings: list[Finding] = []
    for line in lines:
        match = SEVERITY_LABEL.match(line.strip())
        if not match:
            continue
        findings.append(
            Finding(
                severity=match.group(1).strip().lower(),
                text=match.group(2).strip(),
                line=offset,
            )
        )
    return findings


def parse_verdict(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip().strip("*_` ")
        if not stripped or stripped.startswith("<!--"):
            continue
        key = re.sub(r"[^a-z ]", "", stripped.lower())
        key = re.sub(r"\s+", " ", key).strip()
        for candidate in sorted(VERDICTS, key=len, reverse=True):
            if key.startswith(candidate):
                return VERDICTS[candidate]
        return stripped.upper()
    return None


def has_field(text: str, field_name: str) -> bool:
    return re.search(rf"\b{field_name}\s*:", text, re.IGNORECASE) is not None


def check(text: str) -> Result:
    result = Result()
    # Guidance comments are authoring scaffolding. A finding documented inside
    # a comment is not a finding in this review.
    sections = split_sections(re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL))

    for section in REQUIRED_SECTIONS:
        if section not in sections:
            result.errors.append(f"missing required section: {section.title()}")
    if result.errors:
        return result

    scope = substantive(sections["scope"])
    if not scope:
        result.errors.append("Scope is empty; record the base and head revisions reviewed")

    coverage_detail = ""
    for line in sections["scope"]:
        match = COVERAGE_LINE.search(line)
        if match:
            result.coverage = match.group(1).lower()
            coverage_detail = match.group(2).strip(" .-:\t")
            break
    if result.coverage is None:
        result.errors.append(
            "Scope must record `Coverage: full` or `Coverage: partial (<units read>)`"
        )
    elif result.coverage == "partial" and not coverage_detail:
        result.errors.append(
            "Coverage is partial but does not say what was read; add the units or paths covered"
        )
    evidence = substantive(sections["evidence"])
    if not evidence:
        result.errors.append(
            "Evidence is empty; record the commands, tests, or artifacts actually inspected"
        )
    residual = substantive(sections["residual risk"])
    if not residual:
        result.errors.append("Residual risk is empty; state what could still be wrong")
    not_reviewed = substantive(sections["not reviewed"])
    if not not_reviewed:
        result.errors.append(
            "Not reviewed is empty; state what was out of scope even when the answer is 'nothing'"
        )

    findings = parse_findings(sections["findings"])
    counts = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        if finding.severity not in SEVERITIES:
            result.errors.append(
                f"unknown severity label [{finding.severity}]; use one of "
                + ", ".join(SEVERITIES)
            )
            continue
        counts[finding.severity] += 1
        if finding.severity in EVIDENCE_REQUIRED and not has_field(finding.text, "evidence"):
            result.errors.append(
                f"[{finding.severity}] finding has no evidence: field: {finding.text!r}"
            )
        if finding.severity == "blocking" and not has_field(finding.text, "verify"):
            result.errors.append(
                f"[blocking] finding has no verify: field, so nobody can confirm the fix: "
                f"{finding.text!r}"
            )
        if finding.severity != "praise" and len(finding.text.split()) < 4:
            result.warnings.append(
                f"[{finding.severity}] finding is too terse to act on: {finding.text!r}"
            )

    unlabelled = [
        line.strip()
        for line in sections["findings"]
        if line.strip().startswith(("- ", "* ", "+ ")) and not SEVERITY_LABEL.match(line.strip())
    ]
    for line in unlabelled:
        result.errors.append(f"finding without a severity label: {line!r}")

    if not findings:
        result.warnings.append(
            "Findings is empty; record at least what was checked and found acceptable"
        )

    verdict = parse_verdict(sections["verdict"])
    result.verdict = verdict
    result.counts = counts
    if verdict is None:
        result.errors.append("Verdict is empty; state one of " + ", ".join(VERDICTS.values()))
        return result
    if verdict not in VERDICTS.values():
        result.errors.append(
            f"unknown verdict {verdict!r}; use one of " + ", ".join(VERDICTS.values())
        )
        return result

    blocking = counts["blocking"]
    if verdict in {"APPROVE", "APPROVE WITH COMMENTS"} and blocking:
        result.errors.append(
            f"verdict {verdict} contradicts {blocking} open blocking finding(s); "
            "resolve them or record REQUEST CHANGES"
        )
    if verdict == "REQUEST CHANGES" and blocking == 0:
        result.warnings.append(
            "REQUEST CHANGES with no blocking finding; say which finding blocks, or use "
            "APPROVE WITH COMMENTS"
        )
    if verdict == "NEEDS MORE EVIDENCE" and len(evidence) == 0:
        result.errors.append("NEEDS MORE EVIDENCE requires a stated evidence gap")
    if result.coverage == "partial" and verdict in {"APPROVE", "APPROVE WITH COMMENTS"}:
        result.warnings.append(
            "partial coverage recorded with an approving verdict; confirm another reviewer "
            "covered the remainder, or record NEEDS MORE EVIDENCE"
        )
    if verdict == "NEEDS MORE EVIDENCE" and len(evidence) < 2:
        result.warnings.append(
            "NEEDS MORE EVIDENCE usually names what was checked and what is missing"
        )
    return result


def render(result: Result, path: Path) -> str:
    lines = [
        f"{path}: {'VALID' if result.valid else 'INVALID'} "
        f"(verdict: {result.verdict}, coverage: {result.coverage})"
    ]
    if result.counts:
        counts = ", ".join(f"{name}={value}" for name, value in sorted(result.counts.items()))
        lines.append(f"findings: {counts}")
    lines += [f"error: {message}" for message in result.errors]
    lines += [f"warning: {message}" for message in result.warnings]
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="review_record_check.py",
        description="Check a review record for completeness and verdict consistency.",
        epilog="Truth of a finding is not checkable here; cite evidence in the record instead.",
    )
    parser.add_argument("record", type=Path, help="path to the markdown review record")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as failures (exit 1)"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = args.record.read_text(encoding="utf-8")
    except OSError as error:
        print(f"review_record_check: {error}", file=sys.stderr)
        return 2

    result = check(text)
    if args.json:
        json.dump(result.as_dict(), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render(result, args.record))
    if not result.valid or (args.strict and result.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
