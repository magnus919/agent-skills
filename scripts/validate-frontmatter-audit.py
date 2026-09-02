#!/usr/bin/env python3
"""Audit canonical skill descriptions for actionable routing metadata."""

# Keep the verb vocabulary readable as a single audited list.
# ruff: noqa: SIM905

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

IMPERATIVE_VERBS = set(
    (
        "add administer analyze apply assess audit automate author backup browse build "
        "calculate capture chain check clean compare configure connect control convert "
        "create debug define deploy design diagnose discover document draft edit "
        "evaluate export extract fetch find fix format generate guide identify "
        "implement import ingest inspect install interact investigate load maintain "
        "make manage migrate model monitor operate optimize organize parse plan play "
        "prepare process publish query read refactor release remove render repair "
        "research resolve restore review reverse-engineer route run scan scaffold "
        "scrape search secure select send set simulate start stop structure summarize "
        "sync teach test track train transform translate troubleshoot update use "
        "validate verify visualize write"
    ).split()
)
BOUNDARY = re.compile(
    r"\b(?:do not use(?: this skill)? for|not for|when not to use|unlike|distinct from)\b",
    re.IGNORECASE,
)
HEADING = re.compile(r"^\s*#{1,6}\s+When not to use\s*#*\s*$", re.IGNORECASE)
BOUNDARY_WORD = re.compile(
    r"\b(?:avoid|belongs?|choose|defer|do not|don't|does not|never|not|only|"
    r"outside|prefer|prerequisite|required?|requires?|rather than|route|see|"
    r"skip|use|when)\b",
    re.IGNORECASE,
)
STOPWORDS = set(
    (
        "this that with from into when where which your their they them for and the "
        "use skill tasks work across before after only rather than does not have has "
        "will without using need needs agent"
    ).split()
)


def files(root: Path) -> list[Path]:
    """Return every canonical entry point, matching validate-skills.rb."""
    return sorted(
        path
        for path in root.glob("**/SKILL.md")
        if "agent-council/profiles/skills/" not in path.relative_to(root).as_posix()
    )


def parse(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    """Parse frontmatter and return the remaining markdown body."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None, text, "missing YAML frontmatter"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, text, f"invalid YAML: {exc}"
    if not isinstance(data, dict):
        return None, text, "frontmatter must be a mapping"
    return data, text[match.end() :], None


def has_body_boundary(body: str) -> bool:
    """Return whether a substantive When-not-to-use section exists."""
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not HEADING.match(line):
            continue
        section: list[str] = []
        for candidate in lines[index + 1 :]:
            if re.match(r"^\s*#{1,6}\s+", candidate):
                break
            visible = re.sub(r"<!--.*?-->", "", candidate).strip()
            if visible and not re.fullmatch(r"[-*_]{3,}", visible):
                section.append(visible)
        if any(
            len(re.findall(r"[A-Za-z0-9]+", line)) >= 3 and BOUNDARY_WORD.search(line)
            for line in section
        ):
            return True
    return False


def audit(root: Path) -> dict[str, Any]:
    """Audit all canonical descriptions below *root*."""
    violations: list[dict[str, str]] = []
    skill_files = files(root)
    for path in skill_files:
        relative = path.relative_to(root).as_posix()
        data, body, error = parse(path)
        if error:
            violations.append({"path": relative, "rule": "frontmatter", "message": error})
            continue

        if data is None:
            continue
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            violations.append(
                {"path": relative, "rule": "description", "message": "description is empty"}
            )
            continue

        cleaned = re.sub(r"\ADeprecated:\s*", "", description.strip(), flags=re.IGNORECASE)
        opener = re.match(r"[A-Za-z]+(?:-[A-Za-z]+)?", cleaned)
        if not opener or opener.group().lower() not in IMPERATIVE_VERBS:
            violations.append(
                {
                    "path": relative,
                    "rule": "imperative-opener",
                    "message": f"starts with {opener.group() if opener else ''!r}",
                }
            )

        terms = {
            term.lower()
            for term in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", description)
            if term.lower() not in STOPWORDS
        }
        if len(terms) < 2:
            violations.append(
                {
                    "path": relative,
                    "rule": "positive-trigger",
                    "message": "needs at least two concrete trigger terms",
                }
            )
        if not BOUNDARY.search(description) and not has_body_boundary(body):
            violations.append(
                {
                    "path": relative,
                    "rule": "negative-boundary",
                    "message": "name a nearest alternative or explicit non-use boundary",
                }
            )

    return {
        "files_audited": len(skill_files),
        "violations": violations,
        "ok": not violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit canonical skill frontmatter descriptions")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit(Path(args.root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Audited {report['files_audited']} canonical descriptions")
        for violation in report["violations"]:
            print(f"{violation['path']}: {violation['rule']}: {violation['message']}")
        result = "PASS" if report["ok"] else f"FAIL ({len(report['violations'])} violations)"
        print(result)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
