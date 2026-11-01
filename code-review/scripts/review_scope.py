#!/usr/bin/env python3
"""Deterministic scope and risk evidence for a code review.

The tool answers one question before any judgment happens: *what is actually
in this change, and how much review attention does it deserve?* It reads the
diff from git (never the network) and emits the same bytes for the same commit
range.

It deliberately does not find defects. It publishes the facts a reviewer would
otherwise assemble by hand and get wrong: size, file classes, risk-bearing
paths, whether tests moved with the source, and a defensible review budget.

Usage:
    review_scope.py --base origin/main --head HEAD --json
    review_scope.py --base origin/main --head HEAD --markdown
    review_scope.py --staged --json

Exit codes:
    0  scope produced
    1  scope could not be produced (bad ref, not a git repo)
    2  usage error
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Reviewers find defects reliably at roughly 200-500 effective LOC/hour, and
# detection degrades as a session runs past about an hour. The tool uses the
# conservative end of that band and caps the session, so the budget is a floor
# for attention, never a target to hit.
LOC_PER_HOUR = 300
MAX_SESSION_MINUTES = 60

# Attention tiers. These route scrutiny; they are not defect thresholds.
TIER_BOUNDARIES = ((200, "small"), (400, "standard"), (1000, "large"))
OVERSIZED_TIER = "oversized"

# Risk terms live inside compound filenames all the time
# (credential-session-authority.md, tenant-isolation.md). An exact path-segment
# match silently misses those, so a hyphen, dot, or underscore also ends a term.
TERM_LEFT = r"(^|[/_.-])"
TERM_RIGHT = r"([/_.-]|$)"


def _term(alternation: str) -> str:
    """Compile a risk vocabulary into a path-matching expression."""
    return rf"{TERM_LEFT}(?:{alternation}){TERM_RIGHT}"


RISK_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "authentication",
        (
            _term("auth|authn|authz|login|logout|session|sessions|oauth|saml|oidc|sso"),
            _term(
                "password|passwd|credential|credentials|token|tokens|jwt|apikey|api_key"
            ),
        ),
    ),
    ("cryptography", (_term("crypto|cipher|encrypt|decrypt|hmac|signature|signing|tls|ssl"),)),
    ("authorization-policy", (_term("policy|policies|rbac|permissions|acl|iam|tenant|tenants"),)),
    ("payment-or-billing", (_term("payment|payments|billing|invoice|checkout|pricing|ledger"),)),
    ("data-migration", (_term("migrations?|migrate|alembic|flyway|liquibase"),)),
    ("destructive-data-path", (_term("delete|purge|truncate|drop|retention|gdpr|erase"),)),
    (
        "dependency-manifest",
        (
            r"(^|/)(package\.json|package-lock\.json|pnpm-lock\.yaml|yarn\.lock|"
            r"go\.(mod|sum)|Cargo\.(toml|lock)|requirements[^/]*\.txt|poetry\.lock|"
            r"pyproject\.toml|Gemfile(\.lock)?|composer\.(json|lock)|pom\.xml|"
            r"build\.gradle(\.kts)?)$",
        ),
    ),
    (
        "ci-or-build-config",
        (
            r"(^|/)(\.github/workflows/|\.gitlab-ci\.yml$|Jenkinsfile$|\.circleci/|"
            r"azure-pipelines|Dockerfile|\.dockerignore|Makefile$)",
        ),
    ),
    ("infrastructure-as-code", (r"(^|/)(terraform|\.tf$|\.tfvars$|helm|charts?/|k8s/|kubernetes/|ansible/|cloudformation|pulumi)",)),
    (
        "public-contract",
        (r"(^|/)(openapi|swagger|asyncapi|\.proto$|graphql|schema\.(json|graphql|yaml)$|api/|routes?/)",),
    ),
    ("concurrency", (_term("lock|mutex|semaphore|queue|worker|scheduler|async|thread|parallel"),)),
)
RISK_PATTERNS = tuple(
    (label, re.compile("|".join(patterns), re.IGNORECASE)) for label, patterns in RISK_RULES
)

TEST_NAME_HINTS = (
    r"(^|/)test_{stem}\.py$",
    r"(^|/){stem}_test\.py$",
    r"(^|/)tests?/test_{stem}\.py$",
    r"(^|/){stem}\.(test|spec)\.(js|jsx|ts|tsx|mjs|cjs)$",
    r"(^|/){stem}_test\.(go|rb|ex)$",
    r"(^|/){stem}Test\.(java|kt|cs|php)$",
    r"(^|/)Test{stem}\.(java|kt|cs)$",
    r"(^|/){stem}_spec\.rb$",
    r"(^|/)test[_-]{stem}\.sh$",
)

SOURCE_SUFFIXES = frozenset(
    ".c .cc .cpp .cs .ex .exs .go .h .hpp .java .js .jsx .kt .kts .lua .m .mm "
    ".php .pl .py .rb .rs .scala .sh .swift .ts .tsx .vue .svelte".split()
)
DOC_SUFFIXES = frozenset({".md", ".mdx", ".rst", ".adoc", ".txt"})
CONFIG_SUFFIXES = frozenset(
    {".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".properties"}
)
BUILD_FILES = frozenset({"dockerfile", "makefile", "jenkinsfile"})
GENERATED_MARKERS = (
    re.compile(r"(^|/)(vendor|third_party|node_modules|dist|build|gen|generated)(/|$)"),
    re.compile(r"(_pb2\.py|\.pb\.go|\.g\.dart|\.min\.(js|css)|\.generated\.\w+)$"),
    re.compile(
        r"(^|/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|Cargo\.lock|poetry\.lock|composer\.lock)$"
    ),
    # Catalog/plugin projections and report directories are produced by
    # generators, not written by hand. Add project-specific paths with --exclude.
    re.compile(
        r"(^|/)(\.claude-plugin/marketplace\.json|\.codex-plugin/plugin\.json|"
        r"\.agents/plugins/marketplace\.json|llms\.txt)$"
    ),
    re.compile(r"(^|/)(graphify-out|test-results)/"),
)


class ScopeError(RuntimeError):
    """The diff could not be read."""


@dataclass
class FileEntry:
    path: str
    status: str
    added: int
    deleted: int
    binary: bool
    kind: str
    generated: bool
    risks: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise ScopeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def resolve_range(repo: Path, base: str | None, head: str | None, staged: bool) -> tuple[str, str]:
    """Return the two revisions the diff is taken between."""
    if staged:
        _git(repo, "rev-parse", "--verify", "HEAD")
        return "HEAD", "index"
    head = head or "HEAD"
    if base is None:
        base = _default_base(repo, head)
    for ref in (base, head):
        try:
            _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
        except ScopeError as error:
            raise ScopeError(f"cannot resolve revision {ref!r}: {error}") from error
    return base, head


def _default_base(repo: Path, head: str) -> str:
    """Prefer the merge base with origin's default branch, then the parent."""
    for candidate in ("origin/main", "origin/master", "main", "master"):
        try:
            _git(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}")
        except ScopeError:
            continue
        merge_base = _git(repo, "merge-base", candidate, head).strip()
        if merge_base:
            return merge_base
    try:
        return _git(repo, "rev-parse", "--verify", f"{head}^").strip()
    except ScopeError as error:
        raise ScopeError("cannot determine a base revision; pass --base") from error


def _diff(repo: Path, base: str, head: str, staged: bool, *flags: str) -> list[str]:
    spec = ["diff", "--cached"] if staged else ["diff", f"{base}...{head}"]
    return _git(repo, *spec, "-z", *flags).split("\0")[:-1]


def parse_name_status(tokens: list[str]) -> dict[str, str]:
    """Map path -> status letter from `--name-status -z` tokens."""
    statuses: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        status = tokens[index][:1]
        index += 1
        if status in {"R", "C"}:
            if index + 1 >= len(tokens):
                break
            statuses[tokens[index + 1]] = status
            index += 2
        else:
            if index >= len(tokens):
                break
            statuses[tokens[index]] = status
            index += 1
    return statuses


def parse_numstat(tokens: list[str]) -> dict[str, tuple[int, int, bool]]:
    """Map path -> (added, deleted, binary) from `--numstat -z` tokens."""
    counts: dict[str, tuple[int, int, bool]] = {}
    index = 0
    while index < len(tokens):
        record = tokens[index]
        index += 1
        parts = record.split("\t")
        if len(parts) < 2:
            continue
        added_raw, deleted_raw = parts[0], parts[1]
        binary = added_raw == "-" and deleted_raw == "-"
        added = 0 if binary else int(added_raw)
        deleted = 0 if binary else int(deleted_raw)
        if parts[2:]:
            path = "\t".join(parts[2:])
        else:
            path = tokens[index + 1] if index + 1 < len(tokens) else ""
            index += 2
        if path:
            counts[path] = (added, deleted, binary)
    return counts


def classify(path: str) -> str:
    """Bucket a path by the kind of review attention it needs."""
    if is_test(path):
        return "test"
    if is_generated(path):
        return "generated"
    if re.search(r"(^|/)(migrations?|alembic|flyway)/", path, re.IGNORECASE):
        return "migration"
    if re.search(r"(^|/)\.github/workflows/", path) or Path(path).suffix.lower() in CONFIG_SUFFIXES:
        return "config"
    if Path(path).suffix.lower() in DOC_SUFFIXES:
        return "docs"
    if Path(path).name.lower() in BUILD_FILES:
        return "config"
    if Path(path).suffix.lower() in SOURCE_SUFFIXES:
        return "source"
    return "other"


def is_test(path: str) -> bool:
    return bool(
        re.search(
            r"(^|/)(tests?|spec|__tests__)/|(^|/)test_[^/]+\.py$|_test\.(py|go|rb|ex)$|"
            r"\.(test|spec)\.(js|jsx|ts|tsx|mjs|cjs)$|[Tt]est\.(java|kt|cs|php)$",
            path,
        )
    )


def is_generated(path: str) -> bool:
    return any(marker.search(path) for marker in GENERATED_MARKERS)


def matches_exclude(path: str, patterns: tuple[str, ...]) -> bool:
    """True when a path matches a caller-supplied exclusion glob."""
    return any(
        fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern.rstrip("/") + "/*")
        for pattern in patterns
    )


def risk_labels(path: str) -> list[str]:
    return sorted(label for label, pattern in RISK_PATTERNS if pattern.search(path))


def find_tests(source_path: str, tracked: list[str]) -> list[str]:
    """Map a changed source file to likely test files by name convention."""
    stem = Path(source_path).stem
    if stem.startswith("test_") or stem.endswith(("_test", "_spec", "Test")):
        return []
    patterns = [re.compile(hint.format(stem=re.escape(stem))) for hint in TEST_NAME_HINTS]
    return sorted({path for path in tracked if any(p.search(path) for p in patterns)})


def tier_for(lines: int) -> str:
    for boundary, name in TIER_BOUNDARIES:
        if lines <= boundary:
            return name
    return OVERSIZED_TIER


def review_budget(lines: int) -> dict[str, int]:
    """Estimate reviewer attention for the effective diff size."""
    minutes = max(5, round(lines / LOC_PER_HOUR * 60)) if lines else 0
    return {
        "effective_lines": lines,
        "estimated_minutes": minutes,
        "capped_minutes": min(minutes, MAX_SESSION_MINUTES),
        "sessions": max(1, -(-minutes // MAX_SESSION_MINUTES)) if minutes else 0,
        "loc_per_hour": LOC_PER_HOUR,
        "max_session_minutes": MAX_SESSION_MINUTES,
    }


def build_scope(
    repo: Path,
    base: str,
    head: str,
    staged: bool,
    tier_override: str | None,
    excludes: tuple[str, ...] = (),
) -> dict:
    statuses = parse_name_status(_diff(repo, base, head, staged, "--name-status"))
    counts = parse_numstat(_diff(repo, base, head, staged, "--numstat"))
    tracked = sorted(_git(repo, "ls-files").splitlines())

    files: list[FileEntry] = []
    for path in sorted(set(statuses) | set(counts)):
        added, deleted, binary = counts.get(path, (0, 0, False))
        entry = FileEntry(
            path=path,
            status=statuses.get(path, "M"),
            added=added,
            deleted=deleted,
            binary=binary,
            kind=classify(path),
            generated=is_generated(path) or matches_exclude(path, excludes),
        )
        entry.risks = risk_labels(path)
        files.append(entry)

    for entry in files:
        if entry.kind == "source":
            entry.tests = find_tests(entry.path, tracked)

    effective = sum(f.added + f.deleted for f in files if not f.generated)
    untested = sorted(f.path for f in files if f.kind == "source" and not f.tests)

    by_kind: dict[str, dict[str, int]] = {}
    for entry in files:
        bucket = by_kind.setdefault(entry.kind, {"files": 0, "added": 0, "deleted": 0})
        bucket["files"] += 1
        bucket["added"] += entry.added
        bucket["deleted"] += entry.deleted

    risks: dict[str, list[str]] = {}
    for entry in files:
        for label in entry.risks:
            risks.setdefault(label, []).append(entry.path)

    return {
        "schema_version": 1,
        "range": {"base": base, "head": head, "merge_base_semantics": not staged},
        "totals": {
            "files": len(files),
            "added": sum(f.added for f in files),
            "deleted": sum(f.deleted for f in files),
            "effective_lines": effective,
            "generated_lines": sum(f.added + f.deleted for f in files if f.generated),
            "binary_files": sum(1 for f in files if f.binary),
        },
        "tier": tier_override or tier_for(effective),
        "exclude_patterns": list(excludes),
        "budget": review_budget(effective),
        "by_kind": {kind: by_kind[kind] for kind in sorted(by_kind)},
        "risks": {label: sorted(risks[label]) for label in sorted(risks)},
        "tests": {
            "changed": sorted(f.path for f in files if f.kind == "test"),
            "source_files_with_tests": sum(1 for f in files if f.kind == "source" and f.tests),
            "source_files_without_matched_tests": untested,
        },
        "files": [
            {
                "path": f.path,
                "status": f.status,
                "added": f.added,
                "deleted": f.deleted,
                "binary": f.binary,
                "kind": f.kind,
                "generated": f.generated,
                "risks": f.risks,
                "tests": f.tests,
            }
            for f in files
        ],
        "generated_paths": sorted(f.path for f in files if f.generated),
        "attention_order": attention_order(files),
    }


def attention_order(files: list[FileEntry]) -> list[str]:
    """Order paths by review value: risk-bearing first, then size, then provenance."""
    kind_rank = {
        "source": 0,
        "migration": 1,
        "config": 2,
        "other": 3,
        "test": 4,
        "docs": 5,
        "generated": 6,
    }

    def key(entry: FileEntry) -> tuple:
        return (
            0 if entry.risks else 1,
            kind_rank.get(entry.kind, 7),
            -(entry.added + entry.deleted),
            entry.path,
        )

    return [entry.path for entry in sorted(files, key=key)]


def render_markdown(scope: dict) -> str:
    totals = scope["totals"]
    budget = scope["budget"]
    lines = [
        "# Review scope",
        "",
        f"- Range: `{scope['range']['base']}...{scope['range']['head']}`",
        f"- Tier: **{scope['tier']}**",
        f"- Size: {totals['files']} files, +{totals['added']}/-{totals['deleted']} "
        f"({totals['effective_lines']} effective lines, {totals['generated_lines']} generated)",
        f"- Budget: ~{budget['estimated_minutes']} min across {budget['sessions']} session(s), "
        f"capped at {budget['capped_minutes']} min each",
        "",
        "## Risk-bearing paths",
        "",
    ]
    if scope["risks"]:
        for label, paths in scope["risks"].items():
            lines.append(f"- **{label}**: " + ", ".join(f"`{path}`" for path in paths))
    else:
        lines.append(
            "- None detected by path convention. Absence of a match is not evidence of safety."
        )
    lines += ["", "## Attention order", ""]
    lines += [f"{index}. `{path}`" for index, path in enumerate(scope["attention_order"], start=1)]
    if scope["tests"]["source_files_without_matched_tests"]:
        lines += ["", "## Changed source without a conventionally matched test", ""]
        lines += [f"- `{path}`" for path in scope["tests"]["source_files_without_matched_tests"]]
        lines += [
            "",
            "A missing match is a question for the author, not a finding: tests may live "
            "elsewhere, or the path may be unreachable in practice.",
        ]
    lines += ["", "## Kind breakdown", "", "| Kind | Files | Added | Deleted |", "|---|---|---|---|"]
    for kind, data in scope["by_kind"].items():
        lines.append(f"| {kind} | {data['files']} | {data['added']} | {data['deleted']} |")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="review_scope.py",
        description="Emit deterministic scope, risk, and attention-budget evidence for a review.",
        epilog="The tool describes the diff; it does not judge it. Findings need human or test evidence.",
    )
    parser.add_argument("--repo", default=".", help="repository path (default: current directory)")
    parser.add_argument("--base", help="base revision (default: merge base with origin/main)")
    parser.add_argument("--head", help="head revision (default: HEAD)")
    parser.add_argument(
        "--staged", action="store_true", help="review the staged index instead of a commit range"
    )
    parser.add_argument(
        "--tier",
        choices=["small", "standard", "large", "oversized"],
        help="override the path-derived attention tier",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="treat matching paths as generated (repeatable); use for project-specific build output",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="emit machine-readable JSON (default)")
    output.add_argument("--markdown", action="store_true", help="emit a human-readable summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = Path(args.repo).expanduser()
    try:
        base, head = resolve_range(repo, args.base, args.head, args.staged)
        scope = build_scope(repo, base, head, args.staged, args.tier, tuple(args.exclude))
    except ScopeError as error:
        print(f"review_scope: {error}", file=sys.stderr)
        return 1
    if args.markdown:
        sys.stdout.write(render_markdown(scope))
    else:
        json.dump(scope, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
