#!/usr/bin/env python3
"""Validate a CHANGELOG.md against the Keep a Changelog conventions.

Checks performed:
  - The first non-empty line is the `# Changelog` title.
  - A `## [Unreleased]` section exists.
  - Version headers use the form `## [X.Y.Z] - YYYY-MM-DD` with a strict
    SemVer version (pre-releases allowed) and a valid ISO-8601 date
    (YYYY-MM-DD or YYYY-MM); the optional `[YANKED]` marker is allowed.
  - Subsection headings use one of the six Keep a Changelog change types
    (Added/Changed/Deprecated/Removed/Fixed/Security), and standalone
    bullets (not under a categorized subsection) name a change type in
    their first word. Bullets under a categorized subsection are
    free-form, matching the canonical Keep a Changelog layout.
  - Every version header (including [Unreleased]) has a matching
    reference link definition (`[X.Y.Z]: https://...`).

Each problem is reported with its line number. Exit 0 when the file is
clean, exit 1 when any problem is found.

Arguments: [changelog.md] (default: CHANGELOG.md), --json.

Exit codes:
  0  changelog is valid
  1  changelog has problems, or the file cannot be read
  2  usage error (argparse)
"""

import argparse
import datetime
import json
import re
import sys

TITLE_RE = re.compile(r"^#\s+Changelog\s*$")
UNRELEASED_HEADER_RE = re.compile(r"^##\s+\[Unreleased\](\s+\[YANKED\])?\s*$")
VERSION_HEADER_RE = re.compile(
    r"^##\s+\[([^\]]+)\]\s*-\s*(\d{4}-\d{2}-\d{2}|\d{4}-\d{2})(\s+\[YANKED\])?\s*$"
)
BULLET_RE = re.compile(r"^-\s+(\S+)")
LINK_REF_RE = re.compile(r"^\[([^\]]+)\]:\s+(\S+)")

CHANGE_TYPES = ("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security")

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="changelog_check.py",
        description=(
            "Validate a CHANGELOG.md against the Keep a Changelog "
            "conventions: title, [Unreleased] section, strict SemVer version "
            "headers with valid dates, allowed change-type bullets, and "
            "consistent reference links."
        ),
        epilog=(
            "Exit codes: 0 valid, 1 problems found / file unreadable, "
            "2 usage error.\n\n"
            "Examples:\n"
            "  changelog_check.py\n"
            "  changelog_check.py CHANGELOG.md\n"
            "  changelog_check.py CHANGELOG.md --json\n"
        ),
    )
    parser.add_argument(
        "changelog",
        nargs="?",
        default="CHANGELOG.md",
        metavar="CHANGELOG.md",
        help="Path to the changelog file (default: CHANGELOG.md).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as machine-parseable JSON instead of text.",
    )
    return parser.parse_args(argv)


def valid_semver(text):
    """Return True if text is a strict SemVer version (pre-releases ok)."""
    return SEMVER_RE.match(text.strip()) is not None


def valid_date(text):
    """Return True if text is a valid YYYY-MM-DD or YYYY-MM date."""
    if len(text) == 10:
        try:
            datetime.date.fromisoformat(text)
            return True
        except ValueError:
            return False
    if len(text) == 7:
        try:
            datetime.datetime.strptime(text, "%Y-%m")
            return True
        except ValueError:
            return False
    return False


def check_changelog(text):
    """Validate changelog text; returns (valid, problems).

    problems is a list of {"line": int, "message": str} dicts.
    """
    problems = []
    lines = text.splitlines()

    non_empty = [i for i, line in enumerate(lines) if line.strip()]
    if not non_empty:
        return False, [{"line": 1, "message": "file is empty"}]

    if not TITLE_RE.match(lines[non_empty[0]].strip()):
        problems.append(
            {
                "line": non_empty[0] + 1,
                "message": "expected '# Changelog' title as the first non-empty line",
            }
        )

    # Pass 1: section headers, subsection headings, bullets, link refs.
    in_section = False
    subsection = None
    has_unreleased = False
    seen_headers = []
    seen_links = set()
    for idx, raw in enumerate(lines):
        line = raw.rstrip()
        stripped = line.strip()
        lineno = idx + 1

        if line.startswith("## "):
            # A version section resets any subsection context.
            in_section = False
            subsection = None
            if stripped.startswith("## ["):
                if UNRELEASED_HEADER_RE.match(stripped):
                    in_section = True
                    has_unreleased = True
                    seen_headers.append(("Unreleased", lineno))
                    continue
                match = VERSION_HEADER_RE.match(stripped)
                if not match:
                    problems.append(
                        {
                            "line": lineno,
                            "message": (
                                "malformed version header (expected "
                                "'## [Unreleased]' or '## [X.Y.Z] - YYYY-MM-DD'): "
                                "'{}'".format(stripped)
                            ),
                        }
                    )
                    continue
                version, date_text = match.group(1), match.group(2)
                if not valid_semver(version):
                    problems.append(
                        {
                            "line": lineno,
                            "message": (
                                "version '{}' is not strict SemVer".format(version)
                            ),
                        }
                    )
                if not valid_date(date_text):
                    problems.append(
                        {
                            "line": lineno,
                            "message": (
                                "invalid release date '{}' in header".format(date_text)
                            ),
                        }
                    )
                seen_headers.append((version, lineno))
                in_section = True
            continue

        if not in_section:
            continue

        if line.startswith("### "):
            heading_word = ""
            remainder = stripped[len("### "):]
            if remainder.split():
                heading_word = remainder.split()[0].rstrip(":,").strip()
            if heading_word and heading_word not in CHANGE_TYPES:
                problems.append(
                    {
                        "line": lineno,
                        "message": (
                            "subsection heading '{}' is not a Keep a Changelog "
                            "type (Added/Changed/Deprecated/Removed/Fixed/Security)"
                        ).format(stripped),
                    }
                )
            subsection = heading_word
            continue

        if stripped.startswith("- "):
            bullet_match = BULLET_RE.match(stripped)
            if not bullet_match:
                continue
            first_word = bullet_match.group(1).rstrip(":,").strip()
            # Bullets under a categorized subsection (e.g. ### Added) are
            # already categorized and are free-form; standalone bullets must
            # name the change type themselves.
            if subsection is None and first_word not in CHANGE_TYPES:
                problems.append(
                    {
                        "line": lineno,
                        "message": (
                            "bullet '{}' is not under a change-type subsection "
                            "and does not start with a Keep a Changelog type "
                            "(Added/Changed/Deprecated/Removed/Fixed/Security)"
                        ).format(stripped),
                    }
                )
            continue

        if stripped.startswith("["):
            link_match = LINK_REF_RE.match(stripped)
            if link_match:
                seen_links.add(link_match.group(1))

    if not has_unreleased:
        problems.append(
            {"line": 1, "message": "missing '## [Unreleased]' section"}
        )

    # Pass 2: every version header needs a matching reference link.
    for header, lineno in seen_headers:
        if header not in seen_links:
            problems.append(
                {
                    "line": lineno,
                    "message": (
                        "missing reference link for '[{}]' "
                        "(add a '[{}]: <url>' definition)".format(header, header)
                    ),
                }
            )

    return len(problems) == 0, problems


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    try:
        with open(args.changelog, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print("error: cannot read '{}': {}".format(args.changelog, exc), file=sys.stderr)
        return 1

    valid, problems = check_changelog(text)

    if args.json_output:
        print(
            json.dumps(
                {
                    "file": args.changelog,
                    "valid": valid,
                    "problem_count": len(problems),
                    "problems": problems,
                },
                indent=2,
            )
        )
    else:
        if not problems:
            print("valid: {} conforms to Keep a Changelog".format(args.changelog))
        else:
            for problem in problems:
                print(
                    "{}:{}: {}".format(
                        args.changelog, problem["line"], problem["message"]
                    )
                )
            print(
                "invalid: {} problem{} found in {}".format(
                    len(problems), "" if len(problems) == 1 else "s", args.changelog
                )
            )

    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
