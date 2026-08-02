#!/usr/bin/env python3
"""Acceptance-criteria testability checker for qa-methodology.

Scans a markdown spec or acceptance-criteria block for vague, untestable
language and flags criteria that lack an observable outcome.

Testable criteria have concrete, verifiable outcomes (status codes, return
values, observable side effects, numeric thresholds). Untestable criteria
use vague verbs ("should handle", "should be efficient", "should work
properly") with no observable verification path.

Input: a markdown file path argument, or stdin if no path given.

Exit codes:
  0  all detected acceptance criteria are testable
  1  one or more acceptance criteria are untestable
  2  malformed or missing input (bad path, empty input, usage error)
"""

import argparse
import re
import sys

# Patterns that indicate vague, untestable language.
VAGUE_PATTERNS = [
    re.compile(r"\bshould\s+handle\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+efficient\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+fast\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+robust\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+secure\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+reliable\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+scalable\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+user.friendly\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+intuitive\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+performant\b", re.IGNORECASE),
    re.compile(r"\bshould\s+work\s+(correctly|properly|well)\b", re.IGNORECASE),
    re.compile(r"\bshould\s+gracefully\b", re.IGNORECASE),
    re.compile(r"\bhandle\s+(errors?\s+)?gracefully\b", re.IGNORECASE),
    re.compile(r"\bshould\s+support\b(?!\s+\d)", re.IGNORECASE),
    re.compile(r"\bshould\s+appropriately\b", re.IGNORECASE),
    re.compile(r"\bas\s+(needed|required|appropriate)\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+easy\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+clean\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+maintainable\b", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+readable\b", re.IGNORECASE),
]

# Patterns that indicate a concrete, testable outcome.
TESTABLE_PATTERNS = [
    re.compile(r"\breturns?\s+\d{3}\b", re.IGNORECASE),
    re.compile(r"\breturns?\s+(true|false|null|nil|none)\b", re.IGNORECASE),
    re.compile(r"\breturns?\s+\{", re.IGNORECASE),
    re.compile(r"\breturns?\s+\[", re.IGNORECASE),
    re.compile(r"\breturns?\s+[\"']", re.IGNORECASE),
    re.compile(r"\bexit\s+code\s+\d", re.IGNORECASE),
    re.compile(r"\bexits?\s+(with\s+)?\d", re.IGNORECASE),
    re.compile(r"\bthrows?\s+\w*Error\b", re.IGNORECASE),
    re.compile(r"\braises?\s+\w*Error\b", re.IGNORECASE),
    re.compile(r"\bstatus\s+code\s+\d{3}\b", re.IGNORECASE),
    re.compile(r"\bHTTP\s+\d{3}\b", re.IGNORECASE),
    re.compile(r"\b\d{3}\s+(OK|Created|Bad Request|Not Found|Error)\b", re.IGNORECASE),
    re.compile(r"\bwithin\s+\d+\s*(ms|s|seconds|milliseconds|minutes)\b", re.IGNORECASE),
    re.compile(r"\bless\s+than\s+\d", re.IGNORECASE),
    re.compile(r"\bat\s+most\s+\d", re.IGNORECASE),
    re.compile(r"\bat\s+least\s+\d", re.IGNORECASE),
    re.compile(r"\bexactly\s+\d", re.IGNORECASE),
    re.compile(r"\b\d+(\.\d+)?%", re.IGNORECASE),
    re.compile(r"\bdisplays?\b", re.IGNORECASE),
    re.compile(r"\brenders?\b", re.IGNORECASE),
    re.compile(r"\bnavigates?\s+to\b", re.IGNORECASE),
    re.compile(r"\bredir(e)?cts?\b", re.IGNORECASE),
    re.compile(r"\blog(s|ged|ging)?\s+(the|a|an|this)\b", re.IGNORECASE),
    re.compile(r"\bsends?\s+(an?\s+)?(email|notification|request|event)\b", re.IGNORECASE),
    re.compile(r"\bcreates?\s+(a|an|the)\b", re.IGNORECASE),
    re.compile(r"\bdeletes?\s+(a|an|the)\b", re.IGNORECASE),
    re.compile(r"\bupdates?\s+(a|an|the)\b", re.IGNORECASE),
    re.compile(r"\bstores?\s+(a|an|the|in)\b", re.IGNORECASE),
    re.compile(r"\bcontains?\b", re.IGNORECASE),
    re.compile(r"\bequals?\b", re.IGNORECASE),
    re.compile(r"\bmatches?\s+(the\s+)?(pattern|regex|schema)\b", re.IGNORECASE),
    re.compile(r"\bis\s+(empty|non-empty|present|absent)\b", re.IGNORECASE),
    re.compile(r"\bwith\s+\{[^}]+\}", re.IGNORECASE),
    re.compile(r"\bwhen\s+\w+", re.IGNORECASE),
]

# AC line patterns: markdown list items or Given/When/Then or numbered criteria.
AC_LINE_RE = re.compile(
    r"^\s*(?:[-*+]\s+|\d+[.)]\s+|AC[-_]?\d*[:.]\s*|Given\s|When\s|Then\s)",
    re.IGNORECASE,
)

# Also match lines that start with "should" or "shall" or "must" (common AC phrasing)
SHOULD_LINE_RE = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:the\s+)?(?:system|api|app|application|service|server|user|it)\s+"
    r"(?:should|shall|must)\b",
    re.IGNORECASE,
)


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="check-ac-testability.py",
        description=(
            "Check acceptance criteria in a markdown spec for testability. "
            "Flags vague criteria (unobservable verbs, no measurable outcome) "
            "and passes concrete ones (observable outcomes with verification path)."
        ),
        epilog=(
            "Exit codes: 0 all testable, 1 untestable criteria found, "
            "2 malformed/missing input."
        ),
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        metavar="SPEC_FILE",
        help=(
            "Path to a markdown spec file containing acceptance criteria "
            "(default: stdin)."
        ),
    )
    return parser.parse_args(argv)


def extract_ac_lines(text):
    """Extract lines that look like acceptance criteria from markdown text."""
    ac_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if AC_LINE_RE.match(line) or SHOULD_LINE_RE.match(line):
            ac_lines.append(stripped)
    return ac_lines


def classify_ac(text):
    """Classify a single AC line as testable or untestable.

    Returns (verdict, reasons) where verdict is 'testable' or 'untestable'
    and reasons is a list of strings explaining why.
    """
    vague_hits = []
    for pat in VAGUE_PATTERNS:
        m = pat.search(text)
        if m:
            vague_hits.append(m.group(0))

    testable_hits = []
    for pat in TESTABLE_PATTERNS:
        m = pat.search(text)
        if m:
            testable_hits.append(m.group(0))

    # If there are concrete observable outcomes, it's testable
    # even if it also has a vague phrase (the concrete part dominates)
    if testable_hits:
        return "testable", ["has observable outcome: {}".format(testable_hits[0])]

    if vague_hits:
        reasons = ["vague language: {}".format(h) for h in vague_hits]
        reasons.append("no observable outcome specified")
        return "untestable", reasons

    # No vague pattern AND no testable pattern: could be a non-criterion line
    # If it has no "should/shall/must" verb, treat as not-an-AC
    if re.search(r"\b(should|shall|must)\b", text, re.IGNORECASE):
        # Has requirement language but no observable outcome
        return "untestable", ["requirement stated but no observable outcome or verification path"]

    # Not a requirement statement at all
    return "testable", ["no requirement language detected; treated as context"]


def check_testability(text):
    """Run testability check on the full text.

    Returns (results, exit_code) where results is a list of dicts.
    """
    ac_lines = extract_ac_lines(text)

    if not ac_lines:
        # No ACs found — nothing to flag
        return [], 0

    results = []
    has_untestable = False

    for line in ac_lines:
        verdict, reasons = classify_ac(line)
        results.append({
            "criterion": line,
            "verdict": verdict,
            "reasons": reasons,
        })
        if verdict == "untestable":
            has_untestable = True

    exit_code = 1 if has_untestable else 0
    return results, exit_code


def format_results(results):
    """Format results as human-readable output."""
    if not results:
        return "No acceptance criteria detected in input."

    lines = []
    for r in results:
        icon = "PASS" if r["verdict"] == "testable" else "FAIL"
        lines.append("[{}] {}".format(icon, r["criterion"]))
        for reason in r["reasons"]:
            lines.append("       {}".format(reason))
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)

    # Read input
    try:
        if args.input == "-":
            source_text = sys.stdin.read()
        else:
            with open(args.input, "r", encoding="utf-8") as fh:
                source_text = fh.read()
    except OSError as exc:
        print("error: cannot read input: {}".format(exc), file=sys.stderr)
        return 2

    if not source_text.strip():
        print("error: input is empty", file=sys.stderr)
        return 2

    results, exit_code = check_testability(source_text)
    print(format_results(results))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
