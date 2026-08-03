#!/usr/bin/env python3
"""Bundle budget checker for frontend-engineering.

Compares a JavaScript/CSS bundle size report against total and per-chunk byte
budgets and fails when a budget is exceeded, so a performance regression stops
the build instead of shipping silently.

Input: a JSON file describing bundle chunks, in either of two shapes:

  {"chunks": [{"name": "main.js", "size": 180000}, ...]}   # structured
  {"main.js": 180000, "vendor.js": 90000}                  # name -> bytes

Budgets accept human units: 250KB, 1.5MB, 512000, 10 B (decimal KB/MB/GB or
binary KiB/MiB/GiB).

Exit codes:
  0  all sizes within budget
  1  one or more chunks or the total exceed budget
  2  usage or input error (missing file, malformed JSON, bad budget value)
"""

import argparse
import json
import re
import sys
from pathlib import Path

_UNIT_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(b|kb|kib|mb|mib|gb|gib)?\s*$", re.IGNORECASE)
_MULTIPLIERS = {
    "b": 1,
    "kb": 1000,
    "kib": 1024,
    "mb": 1000**2,
    "mib": 1024**2,
    "gb": 1000**3,
    "gib": 1024**3,
}


def parse_size(text):
    """Parse '250KB', '1.5MB', or plain byte counts into an int, or None."""
    match = _UNIT_RE.match(text)
    if not match:
        return None
    value = float(match.group(1))
    unit = (match.group(2) or "b").lower()
    return int(value * _MULTIPLIERS[unit])


def human_size(size):
    """Render a byte count in a compact human unit (binary)."""
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GiB"


def load_chunks(path):
    """Load a bundle report into [(name, bytes)]; raises ValueError on bad input."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc.strerror}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc.msg}") from exc

    if isinstance(raw, dict):
        if "chunks" in raw:
            chunks = raw["chunks"]
            if not isinstance(chunks, list):
                raise ValueError(f"{path}: 'chunks' must be a list")
            return [
                (str(entry["name"]), int(entry["size"]))
                for entry in chunks
                if "name" in entry and "size" in entry
            ]
        return [(str(name), int(size)) for name, size in raw.items()]
    raise ValueError(f"{path}: report must be a JSON object of chunk names to sizes")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="bundle-budget-checker.py",
        description=(
            "Check a bundle size report against total and per-chunk budgets. "
            'Report format: {"chunks": [{"name": ..., "size": bytes}]} '
            "or a plain {name: bytes} mapping."
        ),
        epilog="Exit codes: 0 within budget, 1 over budget, 2 usage or input error.",
    )
    parser.add_argument("report", metavar="REPORT.json", help="bundle size report")
    parser.add_argument(
        "--total",
        metavar="SIZE",
        default=None,
        help="total budget for all chunks, e.g. 500KB or 512000",
    )
    parser.add_argument(
        "--chunk",
        metavar="SIZE",
        default=None,
        help="per-chunk budget, e.g. 120KB; each chunk is checked individually",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    total_budget = parse_size(args.total) if args.total is not None else None
    chunk_budget = parse_size(args.chunk) if args.chunk is not None else None
    if args.total is not None and total_budget is None:
        print(f"ERROR: cannot parse budget {args.total!r}", file=sys.stderr)
        return 2
    if args.chunk is not None and chunk_budget is None:
        print(f"ERROR: cannot parse budget {args.chunk!r}", file=sys.stderr)
        return 2
    if total_budget is not None and total_budget < 0:
        print("ERROR: --total must not be negative", file=sys.stderr)
        return 2
    if chunk_budget is not None and chunk_budget < 0:
        print("ERROR: --chunk must not be negative", file=sys.stderr)
        return 2

    try:
        chunks = load_chunks(args.report)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    total = sum(size for _, size in chunks)
    rows = []
    over_budget = False
    for name, size in chunks:
        over = chunk_budget is not None and size > chunk_budget
        over_budget = over_budget or over
        rows.append(
            {
                "name": name,
                "bytes": size,
                "budget": chunk_budget,
                "status": "over" if over else "ok",
            }
        )
    total_over = total_budget is not None and total > total_budget
    over_budget = over_budget or total_over

    if args.json:
        print(
            json.dumps(
                {
                    "total": {
                        "bytes": total,
                        "budget": total_budget,
                        "status": "over" if total_over else "ok",
                    },
                    "chunks": rows,
                    "over_budget": over_budget,
                },
                indent=2,
            )
        )
    else:
        print("Bundle budget report")
        for row in rows:
            status = "OVER" if row["status"] == "over" else "OK"
            budget_text = human_size(row["budget"]) if row["budget"] is not None else "unset"
            print(
                f"  {row['name']:<24} {human_size(row['bytes']):>10}  "
                f"budget {budget_text:>8}  {status}"
            )
        total_budget_text = human_size(total_budget) if total_budget is not None else "unset"
        total_status = "OVER" if total_over else "OK"
        print(
            f"  {'total':<24} {human_size(total):>10}  "
            f"budget {total_budget_text:>8}  {total_status}"
        )
        if over_budget:
            print("Result: over budget", file=sys.stderr)
        else:
            print("Result: within budget")
    return 1 if over_budget else 0


if __name__ == "__main__":
    sys.exit(main())
