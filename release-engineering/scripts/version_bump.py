#!/usr/bin/env python3
"""Compute the next SemVer version from Conventional Commits.

Reads the current version either from --current-version or --from-file
(package.json / pyproject.toml) and the commit history either from a
--commits-file (one commit message per line, or full message blocks in
the format "type(scope): subject" with an optional "BREAKING CHANGE:"
footer) or from a --git-range (runs `git log`).

Bump rules (Conventional Commits 1.0.0):
  - BREAKING CHANGE footer, or a `!` after the type/scope  -> MAJOR
  - feat                                                    -> MINOR
  - fix and all other types                                 -> PATCH
  - 0.x versions (initial development): MAJOR bumps become MINOR,
    MINOR bumps become PATCH (the public API is not yet stable).

Pre-release handling (--pre-release alpha|beta|rc):
  - If the current version is already a pre-release with the SAME tag
    and a numeric suffix (e.g. 1.2.0-alpha.1), the next pre-release
    increments the number without bumping the core (1.2.0-alpha.2).
  - Otherwise the core is bumped per the rules above and the tag is
    applied with a fresh ".1" suffix (e.g. 1.3.0-beta.1).
  - When --pre-release is omitted, the core is bumped per the rules
    above and a stable version is emitted; a pre-release current
    version is not carried into the result (e.g. 1.2.0-alpha.1 with a
    feat commit -> 1.3.0).

Output is a single line with the next version, or structured JSON with
--json.

Exit codes:
  0  success
  1  input error (unreadable file, invalid current version, no commits,
     git failure)
  2  usage error (argparse)
"""

import argparse
import json
import re
import subprocess
import sys

# Strict SemVer 2.0.0 (from semver.org): no leading zeros, optional
# pre-release and build metadata.
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Conventional Commit header: type[!][(scope)!]: description
CONVENTIONAL_RE = re.compile(r"^([a-zA-Z]+)(!)?(?:\(([^)]+)\))?(!)?:(.*)$")

# Breaking-change footer marker (BREAKING CHANGE or the deprecated
# BREAKING-CHANGE alias), matched case-insensitively for robustness.
BREAKING_FOOTER_RE = re.compile(r"breaking[- ]change\s*:", re.IGNORECASE)

PRE_RELEASE_TAGS = ("alpha", "beta", "rc")


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="version_bump.py",
        description=(
            "Compute the next SemVer version from Conventional Commits. "
            "BREAKING CHANGE (or type!/scope!) bumps MAJOR, feat bumps "
            "MINOR, everything else bumps PATCH, with 0.x handling."
        ),
        epilog=(
            "Exit codes: 0 success, 1 input error, 2 usage error.\n\n"
            "Examples:\n"
            "  version_bump.py --current-version 1.2.3 --commits-file commits.txt\n"
            "  version_bump.py --current-version 1.2.3 --git-range main..HEAD\n"
            "  version_bump.py --from-file package.json --commits-file commits.txt\n"
            "  version_bump.py --current-version 1.2.0-alpha.1 --commits-file commits.txt --pre-release alpha\n"
            "  version_bump.py --current-version 1.2.3 --commits-file commits.txt --json\n"
        ),
    )
    version_source = parser.add_mutually_exclusive_group(required=True)
    version_source.add_argument(
        "--current-version",
        metavar="X.Y.Z",
        help="Current version to bump (strict SemVer, optional pre-release/build).",
    )
    version_source.add_argument(
        "--from-file",
        metavar="FILE",
        help=(
            "Read the current version from a package.json or pyproject.toml "
            "file (the 'version' field)."
        ),
    )
    commits_source = parser.add_mutually_exclusive_group(required=True)
    commits_source.add_argument(
        "--commits-file",
        metavar="FILE",
        help=(
            "File with one commit message per line (or message blocks) in "
            "Conventional Commits format; optional 'BREAKING CHANGE:' footer."
        ),
    )
    commits_source.add_argument(
        "--git-range",
        metavar="FROM..TO",
        help="Git revision range (e.g. 'main..HEAD'); subjects are read via git log.",
    )
    parser.add_argument(
        "--pre-release",
        choices=PRE_RELEASE_TAGS,
        metavar="TAG",
        help=(
            "Emit a pre-release with the given tag (alpha, beta, or rc) and "
            "an incrementing numeric suffix."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as machine-parseable JSON instead of text.",
    )
    return parser.parse_args(argv)


def parse_current_version(text):
    """Parse a SemVer string into components, or None if invalid."""
    match = SEMVER_RE.match(text.strip())
    if not match:
        return None
    return {
        "major": int(match.group(1)),
        "minor": int(match.group(2)),
        "patch": int(match.group(3)),
        "prerelease": match.group(4),
        "build": match.group(5),
    }


def split_commits(text):
    """Split raw text into commit message blocks.

    A new commit block starts at any line matching the Conventional
    Commits header format; all following lines (body/footer) belong to
    that commit until the next header line. This accepts both
    one-message-per-line files and full `git log --format=%B` output.
    """
    commits = []
    current = None
    for line in text.splitlines():
        if CONVENTIONAL_RE.match(line):
            if current is not None:
                commits.append(current)
            current = {"header": line, "body": []}
        elif current is not None:
            current["body"].append(line)
    if current is not None:
        commits.append(current)
    return commits


def classify_commit(commit):
    """Classify one commit block; returns a dict or None if not a CC commit."""
    match = CONVENTIONAL_RE.match(commit["header"])
    if not match:
        return None
    ctype = match.group(1).lower()
    breaking = bool(match.group(2)) or bool(match.group(4))
    if not breaking:
        for line in commit["body"]:
            if BREAKING_FOOTER_RE.search(line):
                breaking = True
                break
    return {"type": ctype, "breaking": breaking, "header": commit["header"]}


def compute_bump(commits):
    """Determine the bump level (major/minor/patch) from classified commits."""
    if any(c["breaking"] for c in commits):
        return "major"
    if any(c["type"] == "feat" and not c["breaking"] for c in commits):
        return "minor"
    return "patch"


def bump_core(current, level):
    """Bump MAJOR.MINOR.PATCH per level, with 0.x handling."""
    major, minor, patch = current["major"], current["minor"], current["patch"]
    if level == "major":
        if major == 0:
            return (major, minor + 1, 0)
        return (major + 1, 0, 0)
    if level == "minor":
        if major == 0:
            return (major, minor, patch + 1)
        return (major, minor + 1, 0)
    return (major, minor, patch + 1)


def compute_next(current, level, prerelease_tag):
    """Compute the next version string from current, bump level, and tag."""
    if prerelease_tag is not None and current["prerelease"]:
        parts = current["prerelease"].split(".")
        if (
            len(parts) == 2
            and parts[0] == prerelease_tag
            and parts[1].isdigit()
        ):
            # Same pre-release series: increment the numeric suffix without
            # bumping the core (e.g. 1.2.0-alpha.1 -> 1.2.0-alpha.2).
            return "{}.{}.{}-{}.{}".format(
                current["major"],
                current["minor"],
                current["patch"],
                prerelease_tag,
                int(parts[1]) + 1,
            )
    core = bump_core(current, level)
    if prerelease_tag is None:
        return "{}.{}.{}".format(*core)
    return "{}.{}.{}-{}.1".format(core[0], core[1], core[2], prerelease_tag)


def read_version_from_file(path):
    """Read the current version from package.json or pyproject.toml.

    Returns (version, None) on success or (None, error_message).
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        return None, "cannot read '{}': {}".format(path, exc)

    if path.endswith(".json"):
        try:
            data = json.loads(content)
        except ValueError as exc:
            return None, "invalid JSON in '{}': {}".format(path, exc)
        if not isinstance(data, dict):
            return None, "'{}' must be a JSON object".format(path)
        version = data.get("version")
        if not isinstance(version, str) or not version.strip():
            return None, "no string 'version' field in '{}'".format(path)
        return version.strip(), None

    if path.endswith(".toml"):
        for line in content.splitlines():
            match = re.match(r"^\s*version\s*=\s*['\"]([^'\"]+)['\"]\s*$", line)
            if match:
                return match.group(1), None
        return None, "no 'version' field found in '{}'".format(path)

    return None, "unsupported file type (expected .json or .toml): '{}'".format(path)


def fetch_git_log(git_range):
    """Fetch commit messages for a git revision range.

    Returns (text, None) on success or (None, error_message).
    """
    try:
        proc = subprocess.run(
            ["git", "log", "--reverse", "--pretty=format:%B", git_range],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except OSError as exc:
        return None, "cannot run git: {}".format(exc)
    if proc.returncode != 0:
        message = proc.stderr.strip() or "git exited {}".format(proc.returncode)
        return None, "git log failed for range '{}': {}".format(git_range, message)
    return proc.stdout, None


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)

    if args.current_version:
        current_text = args.current_version
    else:
        current_text, err = read_version_from_file(args.from_file)
        if err:
            print("error: {}".format(err), file=sys.stderr)
            return 1

    current = parse_current_version(current_text)
    if current is None:
        print(
            "error: invalid current version: '{}'".format(current_text),
            file=sys.stderr,
        )
        return 1

    if args.commits_file:
        try:
            with open(args.commits_file, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as exc:
            print("error: cannot read commits file: {}".format(exc), file=sys.stderr)
            return 1
        source = "commits-file"
    else:
        raw, err = fetch_git_log(args.git_range)
        if err:
            print("error: {}".format(err), file=sys.stderr)
            return 1
        source = "git-range"

    commits = split_commits(raw)
    classified = [c for c in (classify_commit(c) for c in commits) if c is not None]
    if not classified:
        print("error: no conventional commits found in input", file=sys.stderr)
        return 1

    level = compute_bump(classified)
    next_version = compute_next(current, level, args.pre_release)
    breaking_count = sum(1 for c in classified if c["breaking"])
    commit_count = len(classified)

    result = {
        "current_version": current_text,
        "next_version": next_version,
        "bump": level,
        "commit_count": commit_count,
        "breaking_count": breaking_count,
        "prerelease": args.pre_release,
        "source": source,
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print("current version: {}".format(current_text))
        print("next version:    {}".format(next_version))
        print(
            "bump:            {} ({} commit{}, {} breaking)".format(
                level,
                commit_count,
                "" if commit_count == 1 else "s",
                breaking_count,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
