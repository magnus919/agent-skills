#!/usr/bin/env python3
"""Compare two CSV/TSV datasets by shape, key uniqueness, and aggregates."""
import argparse
import csv
import hashlib
import json
import math
import pathlib
import sys
from collections import Counter


def read(path, delimiter=None):
    source = pathlib.Path(path)
    raw = source.read_bytes()
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(8192)
        handle.seek(0)
        try:
            selected = delimiter or csv.Sniffer().sniff(sample, delimiters=",\t;|").delimiter
        except csv.Error:
            selected = delimiter or ","
        rows = list(csv.DictReader(handle, delimiter=selected))
    return rows, hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Reconcile two delimited datasets without modifying them.")
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--key", action="append", required=True)
    parser.add_argument("--sum", dest="sums", action="append", default=[])
    parser.add_argument("--delimiter")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    try:
        before_path = pathlib.Path(args.before).resolve(strict=True)
        after_path = pathlib.Path(args.after).resolve(strict=True)
        before, before_hash = read(before_path, args.delimiter)
        after, after_hash = read(after_path, args.delimiter)
        if args.output != "-":
            output_path = pathlib.Path(args.output).resolve()
            if output_path.exists() and (output_path.samefile(before_path) or output_path.samefile(after_path)):
                print("Error: --output must not overwrite or alias an input", file=sys.stderr)
                return 2
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        print(f"Error: cannot read dataset: {exc}", file=sys.stderr)
        return 2

    def keys(rows):
        return [tuple(row.get(key) for key in args.key) for row in rows]

    before_keys, after_keys = keys(before), keys(after)
    result = {
        "before": {"rows": len(before), "sha256": before_hash, "duplicate_keys": sum(n - 1 for n in Counter(before_keys).values() if n > 1)},
        "after": {"rows": len(after), "sha256": after_hash, "duplicate_keys": sum(n - 1 for n in Counter(after_keys).values() if n > 1)},
        "key": args.key,
        "missing_keys": len(set(before_keys) - set(after_keys)),
        "new_keys": len(set(after_keys) - set(before_keys)),
        "sums": {},
    }
    for column in args.sums:
        def total(rows):
            values = [float(row[column]) for row in rows if row.get(column) not in (None, "")]
            if any(not math.isfinite(value) for value in values):
                raise ValueError("non-finite numeric value")
            return sum(values)
        try:
            before_total, after_total = total(before), total(after)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"Error: cannot sum {column}: {exc}", file=sys.stderr)
            return 2
        result["sums"][column] = {"before": before_total, "after": after_total, "delta": after_total - before_total}
    try:
        text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output == "-":
            print(text, end="")
        else:
            pathlib.Path(args.output).write_text(text, encoding="utf-8")
    except (OSError, IsADirectoryError, TypeError, ValueError) as exc:
        print(f"Error: cannot write reconciliation: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
