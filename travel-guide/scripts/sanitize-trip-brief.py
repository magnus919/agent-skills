#!/usr/bin/env python3
"""Create a sanitized travel-guide JSON model for sharing."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

DEFAULT_FIELDS = {
    "start_date",
    "end_date",
    "travelers",
    "lodging",
    "address",
    "exact_address",
    "booking_reference",
    "confirmation",
    "email",
    "phone",
    "private_notes",
    "budget",
    "known_preferences",
    "constraints",
}
REPLACEMENTS = {
    "start_date": None,
    "end_date": None,
    "travelers": ["the travel party"],
    "lodging": "lodging withheld",
    "address": "address withheld",
    "exact_address": "address withheld",
    "booking_reference": "booking reference withheld",
    "confirmation": "confirmation withheld",
    "email": "contact withheld",
    "phone": "contact withheld",
    "private_notes": "private note withheld",
    "budget": {"label": "budget withheld"},
    "known_preferences": ["preferences withheld"],
    "constraints": ["constraints withheld"],
}
URL_KEYS = {"url", "href", "booking_url", "map_url"}


def normalize_key(key):
    return str(key).lower().replace("-", "_").replace(" ", "_")


def scrub_url(value):
    if not isinstance(value, str) or not value.startswith(("http://", "https://")):
        return value
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def sanitize(value, fields, redactions, path=""):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            normalized = normalize_key(key)
            child_path = "%s.%s" % (path, key) if path else str(key)
            if normalized in fields:
                result[key] = copy.deepcopy(REPLACEMENTS.get(normalized, "[redacted]"))
                redactions.append(child_path)
                continue
            if normalized in URL_KEYS:
                cleaned = scrub_url(child)
                if cleaned != child:
                    redactions.append(child_path + " (query/fragment removed)")
                result[key] = cleaned
            else:
                result[key] = sanitize(child, fields, redactions, child_path)
        return result
    if isinstance(value, list):
        return [sanitize(child, fields, redactions, "%s[%d]" % (path, index)) for index, child in enumerate(value)]
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--profile", choices=("shareable",), default="shareable")
    parser.add_argument("--redact", help="comma-separated field names to redact instead of the default shareable set")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a machine-readable report")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.brief.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error("input file does not exist: %s" % args.brief)
    except json.JSONDecodeError as exc:
        print("invalid JSON: %s" % exc, file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("input root must be a JSON object", file=sys.stderr)
        return 1

    fields = {normalize_key(field.strip()) for field in args.redact.split(",") if field.strip()} if args.redact else set(DEFAULT_FIELDS)
    redactions = []
    sanitized = sanitize(data, fields, redactions)
    if not isinstance(sanitized, dict):
        print("sanitizer produced a non-object root", file=sys.stderr)
        return 1
    sanitized["privacy_mode"] = "shareable"
    sanitized.setdefault("privacy", {})
    if isinstance(sanitized["privacy"], dict):
        sanitized["privacy"]["redacted_fields"] = sorted(fields)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sanitized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report = {
        "status": "ok",
        "profile": args.profile,
        "input": str(args.brief),
        "output": str(args.output),
        "redaction_count": len(redactions),
        "redactions": redactions,
        "fields": sorted(fields),
    }
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print("wrote %s (%d redactions)" % (args.output, len(redactions)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
