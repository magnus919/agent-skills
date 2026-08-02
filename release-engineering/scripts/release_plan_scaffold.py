#!/usr/bin/env python3
"""Scaffold a release plan markdown document.

Fills the release-plan template structure (see templates/release-plan.md)
from flags: metadata table, overview and scope (with an in-scope table),
versioning and artifacts, timeline and milestones, owners and RACI, risks
and mitigations, rollout plan, rollback contingency, communication plan,
post-release monitoring, and sign-offs.

Scope items come either from --scope (semicolon-separated) or
--git-range (commit subjects and short SHAs read via `git log`).

Output is written to --output <file> if given, otherwise to stdout.
--json emits a machine-parseable object containing the parsed fields and
the fully rendered document (the rendered markdown is also written to
--output when given). Output is deterministic: no timestamps, no
environment-dependent defaults.

Exit codes:
  0  success
  1  input error (git failure, cannot write output file)
  2  usage error (argparse)
"""

import argparse
import json
import re
import subprocess
import sys

# Conventional-commit prefix used to infer the Type column in the
# in-scope table (e.g. "feat(api): add endpoint" -> "feat").
CONVENTIONAL_PREFIX_RE = re.compile(r"^([a-z]+)(?:\([^)]*\))?!?:\s*")


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="release_plan_scaffold.py",
        description=(
            "Scaffold a release plan markdown document following the "
            "release-plan template structure, filling in the provided fields."
        ),
        epilog=(
            "Exit codes: 0 success, 1 input error, 2 usage error.\n\n"
            "Examples:\n"
            "  release_plan_scaffold.py --version 1.2.3 --name 'Acme 1.2.3' \\\n"
            "      --date 2026-08-15 --owner 'Jane Doe' \\\n"
            "      --milestones 'Branch cut;Release candidate;GA' \\\n"
            "      --scope 'feat: new API;fix: retry bug' \\\n"
            "      --risks 'DB migration late;API contract change' \\\n"
            "      --output release-plan.md\n"
            "  release_plan_scaffold.py --version 1.2.3 --git-range main..HEAD --json\n"
        ),
    )
    parser.add_argument(
        "--version",
        metavar="X.Y.Z",
        required=True,
        help="Version this release plan covers (required).",
    )
    parser.add_argument(
        "--name",
        metavar="NAME",
        default=None,
        help="Release name (default: 'Release <version>').",
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        default="TBD",
        help="Target release date (default: TBD).",
    )
    parser.add_argument(
        "--owner",
        metavar="NAME",
        default="TBD",
        help="Release manager / accountable owner (default: TBD).",
    )
    parser.add_argument(
        "--milestones",
        metavar="M1;M2",
        help="Semicolon-separated timeline milestones.",
    )
    scope_source = parser.add_mutually_exclusive_group()
    scope_source.add_argument(
        "--scope",
        metavar="ITEM1;ITEM2",
        help="Semicolon-separated scope items.",
    )
    scope_source.add_argument(
        "--git-range",
        metavar="FROM..TO",
        help=(
            "Git revision range; commit subjects and short SHAs become the "
            "scope items (via git log)."
        ),
    )
    parser.add_argument(
        "--risks",
        metavar="R1;R2",
        help="Semicolon-separated risks with mitigations.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write the rendered markdown to this file instead of stdout.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help=(
            "Output the parsed fields and rendered document as JSON on "
            "stdout (the markdown is still written to --output if given)."
        ),
    )
    return parser.parse_args(argv)


def parse_semicolon_list(value):
    """Split a semicolon-separated string into a trimmed, non-empty list."""
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def fetch_git_scope(git_range):
    """Fetch (short_sha, subject) pairs for a git revision range.

    Returns (items, None) on success or (None, error_message).
    items = [{"sha": str, "subject": str}, ...]
    """
    try:
        proc = subprocess.run(
            ["git", "log", "--reverse", "--format=%h%x00%s", git_range],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except OSError as exc:
        return None, "cannot run git: {}".format(exc)
    if proc.returncode != 0:
        message = proc.stderr.strip() or "git exited {}".format(proc.returncode)
        return None, "git log failed for range '{}': {}".format(git_range, message)
    items = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x00", 1)
        sha = parts[0].strip() if parts else ""
        subject = parts[1].strip() if len(parts) > 1 else ""
        if subject:
            items.append({"sha": sha, "subject": subject})
    return items, None


def infer_type(subject):
    """Infer a change type from a conventional-commit subject prefix."""
    match = CONVENTIONAL_PREFIX_RE.match(subject)
    if not match:
        return "TBD"
    ctype = match.group(1)
    if ctype == "revert":
        return "fix"
    return ctype


def render_plan(fields):
    """Render the release plan markdown from parsed fields (deterministic)."""
    lines = []
    lines.append("# Release Plan: {}".format(fields["name"]))
    lines.append("")
    lines.append("## Metadata")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append("| Release name | {} |".format(fields["name"]))
    lines.append("| Version | {} |".format(fields["version"]))
    lines.append("| Target date (GA) | {} |".format(fields["date"]))
    lines.append("| Release manager (DRI) | {} |".format(fields["owner"]))
    lines.append("| Status | Draft |")
    lines.append("")
    lines.append("## 1. Overview and Scope")
    lines.append("")
    lines.append("### Objective")
    lines.append("")
    lines.append(
        "_TBD - one or two sentences: the user/business outcome this release "
        "delivers and how success is measured._"
    )
    lines.append("")
    lines.append("### In Scope")
    lines.append("")
    lines.append("| ID | Item | Type (feat/fix/chore/security) | Source (PR/commit) |")
    lines.append("|----|------|--------------------------------|--------------------|")
    if fields["scope"]:
        for index, item in enumerate(fields["scope"], start=1):
            source = fields["scope_sources"][index - 1] or "—"
            lines.append(
                "| S-{} | {} | {} | {} |".format(
                    index, item, infer_type(item), source
                )
            )
    else:
        lines.append("| S-1 | _TBD_ | TBD | — |")
    lines.append("")
    lines.append("### Out of Scope")
    lines.append("")
    lines.append("- _TBD - list items excluded from this release and why._")
    lines.append("")
    lines.append("## 2. Versioning and Artifacts")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append("| Version scheme | TBD (SemVer / CalVer) |")
    lines.append("| Primary artifact(s) | TBD |")
    lines.append("| Artifact digest(s) | TBD |")
    lines.append("| SBOM / provenance | TBD |")
    lines.append("| Promotion policy | TBD (build once, promote the same artifact) |")
    lines.append("")
    lines.append("## 3. Timeline and Milestones")
    lines.append("")
    lines.append("| Milestone | Date | Owner | Exit Criteria |")
    lines.append("|-----------|------|-------|---------------|")
    if fields["milestones"]:
        for milestone in fields["milestones"]:
            lines.append("| {} | TBD | TBD | TBD |".format(milestone))
    else:
        lines.append("| _TBD_ | TBD | TBD | TBD |")
    lines.append("")
    lines.append("## 4. Owners and RACI")
    lines.append("")
    lines.append("| Activity | R | A | C | I |")
    lines.append("|----------|---|---|---|---|")
    for activity in (
        "Scope definition",
        "Build & test",
        "Deploy",
        "Rollback decision",
        "Comms",
        "Post-release monitoring",
    ):
        lines.append("| {} | TBD | TBD | TBD | TBD |".format(activity))
    lines.append("")
    lines.append("## 5. Risks and Mitigations")
    lines.append("")
    lines.append("| ID | Risk | Probability (H/M/L) | Impact (H/M/L) | Mitigation | Owner |")
    lines.append("|----|------|---------------------|----------------|------------|-------|")
    if fields["risks"]:
        for index, risk in enumerate(fields["risks"], start=1):
            lines.append("| R-{} | {} | TBD | TBD | TBD | TBD |".format(index, risk))
    else:
        lines.append("| R-1 | _TBD_ | TBD | TBD | TBD | TBD |")
    lines.append("")
    lines.append("## 6. Rollout Plan")
    lines.append("")
    lines.append(
        "- _TBD - strategy (canary / blue-green / rolling / ring / feature-flag), "
        "staged progression, gates, and auto-rollback triggers._"
    )
    lines.append("")
    lines.append("## 7. Rollback Contingency")
    lines.append("")
    lines.append(
        "- _TBD - decision authority, time-box, known-good artifact, and "
        "special cases; see rollback-runbook.md._"
    )
    lines.append("")
    lines.append("## 8. Communication Plan")
    lines.append("")
    lines.append(
        "- _TBD - internal announcements, support handoff, customer comms, "
        "and status page cadence._"
    )
    lines.append("")
    lines.append("## 9. Post-Release Monitoring")
    lines.append("")
    lines.append(
        "- _TBD - metrics to watch (DORA, SLIs) and on-call coverage window._"
    )
    lines.append("")
    lines.append("## 10. Sign-offs")
    lines.append("")
    lines.append("| Role | Name | Date | Decision |")
    lines.append("|------|------|------|----------|")
    lines.append("| Engineering lead (quality) | TBD | TBD | Approved / Not approved |")
    lines.append("| SRE / operations (rollback + monitoring ready) | TBD | TBD | Approved / Not approved |")
    lines.append("| Product owner (scope + comms) | TBD | TBD | Approved / Not approved |")
    lines.append(
        "| Release manager (final) | {} | TBD | GO / NO-GO / GO WITH CONDITIONS |".format(
            fields["owner"]
        )
    )
    return "\n".join(lines) + "\n"


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)

    name = args.name if args.name else "Release {}".format(args.version)
    milestones = parse_semicolon_list(args.milestones)
    risks = parse_semicolon_list(args.risks)

    if args.git_range:
        scope_items, err = fetch_git_scope(args.git_range)
        if err:
            print("error: {}".format(err), file=sys.stderr)
            return 1
        scope_source = "git-range"
    else:
        scope_items = [
            {"sha": None, "subject": item}
            for item in parse_semicolon_list(args.scope)
        ]
        scope_source = "flags"

    fields = {
        "version": args.version,
        "name": name,
        "date": args.date,
        "owner": args.owner,
        "milestones": milestones,
        "scope": [item["subject"] for item in scope_items],
        "scope_sources": [item["sha"] for item in scope_items],
        "risks": risks,
        "scope_source": scope_source,
    }

    document = render_plan(fields)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(document)
        except OSError as exc:
            print("error: cannot write '{}': {}".format(args.output, exc), file=sys.stderr)
            return 1

    if args.json_output:
        payload = dict(fields)
        payload["document"] = document
        print(json.dumps(payload, indent=2))
    elif not args.output:
        print(document, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
