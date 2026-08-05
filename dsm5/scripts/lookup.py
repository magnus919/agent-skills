#!/usr/bin/env python3
"""lookup.py — keyword search across the dsm5 skill's references/ library.

Finds where a topic lives in the reference library so agents and humans can
route a question to the right file.  Pure Python 3 stdlib, no dependencies,
no side effects.

Examples:
    python3 lookup.py "insomnia"                 # grouped matches + ranking
    python3 lookup.py "insomnia" --json          # machine-readable output
    python3 lookup.py --list                     # files with their H1 titles
    python3 lookup.py "mania" --max 5 -q         # just the recommended files

Exit codes: 0 = matches found, 1 = no matches (or missing references dir),
2 = usage error.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Lines of surrounding context to show for each match (before and after).
CONTEXT = 2
DEFAULT_MAX = 10

H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$")


def references_dir() -> Path:
    """The skill's references/ directory, resolved relative to this script."""
    return Path(__file__).resolve().parent.parent / "references"


def h1_title(path: Path):
    """Return the text of the file's first H1 heading, or None if absent."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                m = H1_RE.match(line)
                if m:
                    return m.group(1).strip()
    except OSError:
        pass
    return None


def list_references():
    """Return [(filename, title_or_None), ...] sorted by filename."""
    refs = references_dir()
    return [
        (p.name, h1_title(p))
        for p in sorted(refs.glob("*.md"))
    ]


def search(query: str, max_per_file: int):
    """Case-insensitive search across reference files.

    Returns (results, recommended) where results is a list of match dicts
    {"file", "line", "text", "context"} (line is 1-based, context is the
    surrounding lines excluding the match itself) and recommended is a list
    of {"file", "title", "matches"} sorted by match count descending, then
    filename.  Match counts are total per file; only the first max_per_file
    matches per file are emitted.
    """
    refs = references_dir()
    q = query.lower()
    results = []
    counts = {}

    for p in sorted(refs.glob("*.md")):
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            print(f"warning: cannot read {p.name}: {exc}", file=sys.stderr)
            continue

        hits = [i for i, line in enumerate(lines) if q in line.lower()]
        counts[p.name] = len(hits)

        for idx in hits[:max_per_file]:
            lo = max(0, idx - CONTEXT)
            hi = min(len(lines), idx + CONTEXT + 1)
            context = [
                lines[i].rstrip("\n")
                for i in range(lo, hi)
                if i != idx
            ]
            results.append({
                "file": p.name,
                "line": idx + 1,
                "text": lines[idx].rstrip("\n"),
                "context": context,
            })

    recommended = [
        {"file": name, "title": h1_title(refs / name), "matches": count}
        for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        if count > 0
    ]
    return results, recommended


def print_human(query: str, results, recommended) -> None:
    """Grouped, readable output for a terminal."""
    by_file = {}
    for r in results:
        by_file.setdefault(r["file"], []).append(r)

    total = len(results)
    print(f"{total} match(es) for {query!r} in {len(by_file)} file(s)\n")

    for fname in sorted(by_file):
        print(fname)
        for r in by_file[fname]:
            print(f"  line {r['line']}: {r['text']}")
            for ctx_line in r["context"]:
                print(f"    | {ctx_line}")
        print()

    if recommended:
        print("Best reference files to read:")
        for rec in recommended:
            title = f" — {rec['title']}" if rec["title"] else ""
            plural = "" if rec["matches"] == 1 else "es"
            print(f"  {rec['file']}{title} ({rec['matches']} match{plural})")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="lookup.py",
        description="Search the dsm5 skill's references/ library for a keyword or phrase.",
    )
    parser.add_argument(
        "query", nargs="?",
        help="keyword or phrase to search for (omit with --list)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="emit machine-readable JSON instead of human text",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="list every reference file with its H1 title and exit",
    )
    parser.add_argument(
        "--max", type=int, default=DEFAULT_MAX, metavar="N",
        help=f"cap the number of matches shown per file (default {DEFAULT_MAX})",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="print only the recommended file names (one per line)",
    )
    args = parser.parse_args(argv)

    if args.max < 1:
        parser.error("--max must be at least 1")

    refs = references_dir()
    if not refs.is_dir():
        print(
            f"error: references directory not found at {refs}",
            file=sys.stderr,
        )
        return 1

    if args.list:
        entries = list_references()
        if not entries:
            print("error: no reference files found.", file=sys.stderr)
            return 1
        for name, title in entries:
            if title:
                print(f"{name}\n  {title}")
            else:
                print(name)
        return 0

    if args.query is None:
        parser.error("a search query is required (or use --list)")

    results, recommended = search(args.query, args.max)

    if args.json:
        print(json.dumps({
            "query": args.query,
            "results": results,
            "recommended_files": recommended,
        }, indent=2))
    elif args.quiet:
        for rec in recommended:
            print(rec["file"])
    else:
        print_human(args.query, results, recommended)

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
