#!/usr/bin/env python3
"""Strict SemVer 2.0.0 validation and precedence tooling.

Three mutually exclusive modes:
  --check VERSION   Validate a version; exits 0 if valid, 1 if invalid
                    (the reason is printed either way).
  --compare A B     Compare two versions; prints lt, gt, or eq.
  --sort V1 V2 ...  Sort versions ascending by SemVer precedence.

Precedence follows SemVer 2.0.0 section 11: MAJOR.MINOR.PATCH compared
numerically; pre-release versions sort below the same core without a
pre-release; numeric pre-release identifiers sort below alphanumeric
ones; build metadata is ignored for precedence.

Output is human-readable by default, or machine-parseable JSON with
--json (a single JSON object on stdout; errors still go to stderr).

Exit codes:
  0  success
  1  invalid version (--check) or invalid input (--compare/--sort)
  2  usage error (argparse)
"""

import argparse
import json
import re
import sys

# Strict SemVer 2.0.0 grammar (semver.org): no leading zeros, optional
# pre-release and build metadata.
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

NUMERIC_RE = re.compile(r"^\d+$")
BUILD_IDENT_RE = re.compile(r"^[0-9a-zA-Z-]+$")


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="semver_check.py",
        description=(
            "Validate strict SemVer 2.0.0 versions and apply SemVer "
            "precedence (compare and sort)."
        ),
        epilog=(
            "Exit codes: 0 success, 1 invalid version / invalid input, "
            "2 usage error.\n\n"
            "Examples:\n"
            "  semver_check.py --check 1.2.3\n"
            "  semver_check.py --check 01.2.3\n"
            "  semver_check.py --compare 1.2.3 1.2.4\n"
            "  semver_check.py --sort 1.0.0-beta.2 1.0.0-alpha.1 1.0.0 1.0.0+build\n"
            "  semver_check.py --check 1.2.3-alpha.1 --json\n"
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        metavar="VERSION",
        help=(
            "Validate a version: exits 0 and prints 'valid' if it conforms "
            "to SemVer 2.0.0, exits 1 and prints a reason otherwise."
        ),
    )
    mode.add_argument(
        "--compare",
        nargs=2,
        metavar=("A", "B"),
        help="Compare two versions; prints lt, gt, or eq.",
    )
    mode.add_argument(
        "--sort",
        nargs="+",
        metavar="VERSION",
        help="Sort the given versions ascending by SemVer precedence.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as machine-parseable JSON instead of text.",
    )
    return parser.parse_args(argv)


def parse_semver(text):
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


def invalid_reason(text):
    """Produce a human-readable reason why a version is invalid.

    Returns a generic message when the specific defect is not obvious.
    """
    value = text.strip()
    if not value:
        return "version is empty"

    match = re.match(r"^([0-9]*)\.([0-9]*)\.([0-9]*)(.*)$", value)
    if not match:
        return "expected MAJOR.MINOR.PATCH (e.g. 1.2.3)"

    major_raw, minor_raw, patch_raw, rest = match.groups()
    for name, raw in (("MAJOR", major_raw), ("MINOR", minor_raw), ("PATCH", patch_raw)):
        if raw == "":
            return "{} component is missing".format(name)
        if not raw.isdigit():
            return "{} component must be numeric, got '{}'".format(name, raw)
        if len(raw) > 1 and raw.startswith("0"):
            return "{} component must not have leading zeros, got '{}'".format(
                name, raw
            )

    if not rest:
        return "invalid SemVer 2.0.0 version"

    if rest.startswith("+"):
        build = rest[1:]
        if not _valid_build(build):
            return "invalid build metadata: '{}'".format(build)
        return "invalid SemVer 2.0.0 version"

    if rest.startswith("-"):
        prerelease = rest[1:]
        build = None
        if "+" in prerelease:
            prerelease, build = prerelease.split("+", 1)
        if not _valid_prerelease(prerelease):
            return "invalid pre-release identifiers: '{}'".format(prerelease)
        if build is not None and not _valid_build(build):
            return "invalid build metadata: '{}'".format(build)
        return "invalid SemVer 2.0.0 version"

    return "unexpected characters after PATCH: '{}'".format(rest)


def _valid_prerelease(identifiers):
    """Validate dot-separated pre-release identifiers."""
    if not identifiers:
        return False
    for ident in identifiers.split("."):
        if ident == "":
            return False
        if ident.isdigit():
            if len(ident) > 1 and ident.startswith("0"):
                return False
        elif not re.match(r"^[0-9a-zA-Z-]+$", ident) or not re.search(r"[a-zA-Z-]", ident):
            # Alphanumeric identifiers must contain at least one letter/hyphen.
            return False
    return True


def _valid_build(identifiers):
    """Validate dot-separated build metadata identifiers."""
    if not identifiers:
        return False
    return all(BUILD_IDENT_RE.match(ident) for ident in identifiers.split("."))


def compare_precedence(a, b):
    """Compare two parsed versions by SemVer precedence.

    Returns -1 if a < b, 0 if equal, 1 if a > b. Build metadata is ignored.
    """
    for key in ("major", "minor", "patch"):
        if a[key] != b[key]:
            return -1 if a[key] < b[key] else 1

    pa, pb = a["prerelease"], b["prerelease"]
    if pa == pb:
        return 0
    if pa is None:
        return 1
    if pb is None:
        return -1

    ia, ib = pa.split("."), pb.split(".")
    for x, y in zip(ia, ib):
        xn, yn = x.isdigit(), y.isdigit()
        if xn and yn:
            if int(x) != int(y):
                return -1 if int(x) < int(y) else 1
        elif xn != yn:
            # Numeric identifiers always sort below alphanumeric ones.
            return -1 if xn else 1
        else:
            if x != y:
                return -1 if x < y else 1
    if len(ia) != len(ib):
        return -1 if len(ia) < len(ib) else 1
    return 0


def relation_word(a, b):
    """Map compare_precedence output to lt/gt/eq."""
    cmp_result = compare_precedence(a, b)
    return "eq" if cmp_result == 0 else ("lt" if cmp_result < 0 else "gt")


def _parsed_payload(parsed):
    """Serialize a parsed version dict for JSON output."""
    return {
        "major": parsed["major"],
        "minor": parsed["minor"],
        "patch": parsed["patch"],
        "prerelease": parsed["prerelease"],
        "build": parsed["build"],
    }


def handle_check(args, version_text):
    """Run --check mode; returns exit code."""
    parsed = parse_semver(version_text)
    if parsed is not None:
        if args.json_output:
            print(
                json.dumps(
                    {
                        "version": version_text,
                        "valid": True,
                        "reason": None,
                        "parsed": _parsed_payload(parsed),
                    },
                    indent=2,
                )
            )
        else:
            print("valid: {}".format(version_text))
        return 0

    reason = invalid_reason(version_text)
    if args.json_output:
        print(
            json.dumps(
                {
                    "version": version_text,
                    "valid": False,
                    "reason": reason,
                    "parsed": None,
                },
                indent=2,
            )
        )
    else:
        print("invalid: {} ({})".format(version_text, reason))
    return 1


def handle_compare(args):
    """Run --compare mode; returns exit code."""
    a_text, b_text = args.compare[0], args.compare[1]
    a, b = parse_semver(a_text), parse_semver(b_text)
    if a is None or b is None:
        bad = a_text if a is None else b_text
        print(
            "error: invalid version '{}': {}".format(bad, invalid_reason(bad)),
            file=sys.stderr,
        )
        return 1
    relation = relation_word(a, b)
    if args.json_output:
        print(
            json.dumps(
                {"a": a_text, "b": b_text, "relation": relation}, indent=2
            )
        )
    else:
        print(relation)
    return 0


def handle_sort(args):
    """Run --sort mode; returns exit code."""
    parsed = {}
    for version in args.sort:
        item = parse_semver(version)
        if item is None:
            print(
                "error: invalid version '{}': {}".format(
                    version, invalid_reason(version)
                ),
                file=sys.stderr,
            )
            return 1
        parsed[version] = item

    # Stable sort by precedence; equal-precedence versions keep input order.
    sorted_versions = sorted(parsed.keys(), key=lambda v: _sort_key(parsed[v]))
    if args.json_output:
        print(json.dumps({"sorted": sorted_versions}, indent=2))
    else:
        for version in sorted_versions:
            print(version)
    return 0


def _sort_key(parsed):
    """Sort key: numeric core, then pre-release mapping for precedence."""
    # Map pre-release identifiers to a comparable tuple:
    # pre-release versions sort below no-pre-release (2^63 sentinel),
    # numeric identifiers sort below alphanumeric ones.
    prerelease = parsed["prerelease"]
    if prerelease is None:
        return (parsed["major"], parsed["minor"], parsed["patch"], 2 ** 63, ())
    key = []
    for ident in prerelease.split("."):
        if ident.isdigit():
            key.append((0, int(ident)))
        else:
            key.append((1, ident))
    return (parsed["major"], parsed["minor"], parsed["patch"], -1, tuple(key))


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    if args.check is not None:
        return handle_check(args, args.check)
    if args.compare is not None:
        return handle_compare(args)
    return handle_sort(args)


if __name__ == "__main__":
    sys.exit(main())
