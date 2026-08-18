#!/usr/bin/env python3
"""Dependency-free, read-only first-pass profiler for CSV/TSV/JSONL."""
import argparse
import csv
import hashlib
import json
import math
import pathlib
import sys
from collections import Counter


def _delimiter(text, requested):
    if requested:
        return requested
    try:
        return csv.Sniffer().sniff(text[:8192], delimiters=",\t;|").delimiter
    except csv.Error:
        return ","


def load(path, delimiter=None, max_rows=None):
    p = pathlib.Path(path)
    raw = p.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows = []
    sampled = False
    if p.suffix.lower() in (".jsonl", ".ndjson"):
        headers = set()
        with p.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
                if not isinstance(record, dict):
                    raise ValueError(f"JSONL line {line_number} is not an object")
                if max_rows is not None and len(rows) >= max_rows:
                    sampled = True
                    break
                rows.append(record)
                headers.update(record)
        headers = sorted(headers)
        rows = [{h: record.get(h) for h in headers} for record in rows]
    else:
        with p.open("r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(8192)
            handle.seek(0)
            dialect = csv.excel
            dialect.delimiter = _delimiter(sample, delimiter)
            reader = csv.DictReader(handle, dialect=dialect)
            headers = reader.fieldnames or []
            for record in reader:
                if max_rows is not None and len(rows) >= max_rows:
                    sampled = True
                    break
                rows.append(record)
    return p, digest, headers, rows, sampled


def profile(path, delimiter=None, max_rows=None, include_values=False):
    p, digest, headers, rows, sampled = load(path, delimiter, max_rows)
    columns = {}
    for header in headers:
        values = [record.get(header) for record in rows]
        nonempty = [value for value in values if value not in (None, "")]
        missing = sum(value in (None, "") for value in values)
        numbers = []
        for value in nonempty:
            try:
                parsed = float(str(value).strip())
                if math.isfinite(parsed):
                    numbers.append(parsed)
            except (TypeError, ValueError):
                pass
        field = {
            "rows": len(values),
            "missing": missing,
            "missing_fraction": (missing / len(values) if values else 0),
            "distinct": len(set(map(str, nonempty))),
            "numeric_parse_fraction": (len(numbers) / len(nonempty) if nonempty else 0),
            "min": min(numbers) if numbers else None,
            "max": max(numbers) if numbers else None,
        }
        if include_values:
            field["top_values"] = Counter(map(str, nonempty)).most_common(5)
        columns[header] = field
    tuples = [tuple(record.get(header) for header in headers) for record in rows]
    duplicate_rows = sum(count - 1 for count in Counter(tuples).values() if count > 1)
    return {
        "file": str(p),
        "sha256": digest,
        "rows_profiled": len(rows),
        "sampled": sampled,
        "columns": headers,
        "duplicate_rows_in_profile": duplicate_rows,
        "fields": columns,
    }


def main():
    parser = argparse.ArgumentParser(description="Profile CSV, TSV, or JSONL without modifying input.")
    parser.add_argument("input")
    parser.add_argument("--output", default="-")
    parser.add_argument("--delimiter")
    parser.add_argument("--max-rows", type=int)
    parser.add_argument("--include-values", action="store_true", help="Include raw top values; off by default for privacy.")
    args = parser.parse_args()
    if args.max_rows is not None and args.max_rows < 1:
        parser.error("--max-rows must be a positive integer")
    try:
        input_path = pathlib.Path(args.input).resolve(strict=True)
        if args.output != "-":
            output_path = pathlib.Path(args.output).resolve()
            if output_path.exists() and input_path.samefile(output_path):
                print("Error: --output must not overwrite or alias the input", file=sys.stderr)
                return 2
        result = profile(input_path, args.delimiter, args.max_rows, args.include_values)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: cannot profile input: {exc}", file=sys.stderr)
        return 2
    try:
        text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output == "-":
            print(text, end="")
        else:
            pathlib.Path(args.output).write_text(text, encoding="utf-8")
    except (OSError, IsADirectoryError, TypeError, ValueError) as exc:
        print(f"Error: cannot write profile: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
