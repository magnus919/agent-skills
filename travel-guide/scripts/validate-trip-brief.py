#!/usr/bin/env python3
"""Validate the portable travel-guide JSON content model."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_MARKERS = (
    "[fill:",
    "{{",
    "replace with",
    "add a sourced",
    "https://example.org",
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://[^\s]+$")


def parse_date(value, label, errors):
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not DATE_RE.match(value):
        errors.append("%s must use YYYY-MM-DD" % label)
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        errors.append("%s is not a real calendar date: %s" % (label, value))
        return None


def walk_strings(value, path=""):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = "%s.%s" % (path, key) if path else str(key)
            yield from walk_strings(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, "%s[%d]" % (path, index))
    elif isinstance(value, str):
        yield path, value


def validate(data, strict=False):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return ["the root value must be a JSON object"], []

    required = ("schema_version", "title", "trip", "thesis", "anchors", "days", "sources")
    for key in required:
        if key not in data:
            errors.append("missing top-level field: %s" % key)

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    trip = data.get("trip")
    if not isinstance(trip, dict):
        errors.append("trip must be an object")
        trip = {}
    for key in ("destination", "duration_days"):
        if not trip.get(key):
            errors.append("trip.%s is required" % key)
    if not isinstance(trip.get("duration_days"), int) or trip.get("duration_days", 0) < 1:
        errors.append("trip.duration_days must be a positive integer")
    if "travelers" in trip and not isinstance(trip["travelers"], list):
        errors.append("trip.travelers must be an array")
    if "route" in trip and not isinstance(trip["route"], list):
        errors.append("trip.route must be an array")

    start = parse_date(trip.get("start_date"), "trip.start_date", errors)
    end = parse_date(trip.get("end_date"), "trip.end_date", errors)
    if start and end:
        if end < start:
            errors.append("trip.end_date must not precede trip.start_date")
        elif (end - start).days + 1 != trip.get("duration_days"):
            warnings.append("trip.duration_days does not equal the inclusive date span")

    thesis = data.get("thesis")
    if not isinstance(thesis, str) or not thesis.strip():
        errors.append("thesis must be a non-empty string")
    elif strict and len(thesis.strip()) < 40:
        errors.append("strict mode requires a trip thesis of at least 40 characters")

    anchors = data.get("anchors")
    if not isinstance(anchors, list):
        errors.append("anchors must be an array")
        anchors = []
    minimum_anchors = 3 if strict else 1
    if len(anchors) < minimum_anchors:
        errors.append("%s mode requires at least %d anchor(s)" % ("strict" if strict else "normal", minimum_anchors))
    for index, anchor in enumerate(anchors):
        prefix = "anchors[%d]" % index
        if not isinstance(anchor, dict):
            errors.append("%s must be an object" % prefix)
            continue
        for key in ("title", "place", "why", "best_window", "cost", "booking", "failure_mode"):
            value = anchor.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append("%s.%s is required" % (prefix, key))
        image = anchor.get("image")
        if image is not None and not isinstance(image, dict):
            errors.append("%s.image must be an object" % prefix)
        if not isinstance(anchor.get("source_ids", []), list):
            errors.append("%s.source_ids must be an array" % prefix)
        elif strict and not anchor.get("source_ids"):
            errors.append("%s.source_ids must cite at least one source in strict mode" % prefix)

    days = data.get("days")
    if not isinstance(days, list):
        errors.append("days must be an array")
        days = []
    if len(days) < 1:
        errors.append("days must contain at least one day card")
    for index, day in enumerate(days):
        prefix = "days[%d]" % index
        if not isinstance(day, dict):
            errors.append("%s must be an object" % prefix)
            continue
        for key in ("day", "label", "anchor", "texture", "pause", "alternative", "practical"):
            if not isinstance(day.get(key), (str, int)) or not str(day.get(key)).strip():
                errors.append("%s.%s is required" % (prefix, key))
        if not isinstance(day.get("source_ids", []), list):
            errors.append("%s.source_ids must be an array" % prefix)
        kind = day.get("kind")
        if kind is not None and (not isinstance(kind, str) or kind.strip().lower() not in ("arrive", "city", "excursion", "coast")):
            warnings.append("%s.kind should be one of arrive, city, excursion, coast" % prefix)

    sources = data.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        sources = []
    if len(sources) < 1:
        errors.append("sources must contain at least one entry")
    source_ids = set()
    for index, source in enumerate(sources):
        prefix = "sources[%d]" % index
        if not isinstance(source, dict):
            errors.append("%s must be an object" % prefix)
            continue
        source_id = source.get("id")
        if not source_id or source_id in source_ids:
            errors.append("%s.id must be present and unique" % prefix)
        source_ids.add(source_id)
        for key in ("title", "url", "retrieved"):
            value = source.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append("%s.%s is required" % (prefix, key))
        if source.get("url") and not URL_RE.match(str(source["url"])):
            errors.append("%s.url must be an http(s) URL" % prefix)
        parse_date(source.get("retrieved"), "%s.retrieved" % prefix, errors)

    for path, value in walk_strings(data):
        lowered = value.lower()
        if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
            warnings.append("placeholder-like text at %s" % path)
            if strict:
                errors.append("strict mode rejects placeholder-like text at %s" % path)

    for collection_name in ("anchors", "days", "special", "skip", "practical"):
        collection = data.get(collection_name, [])
        if not isinstance(collection, list):
            continue
        for index, item in enumerate(collection):
            if not isinstance(item, dict):
                continue
            source_refs = item.get("source_ids", [])
            if not isinstance(source_refs, list):
                continue
            for source_id in source_refs:
                if source_id not in source_ids:
                    errors.append("%s[%d].source_ids references unknown source: %s" % (collection_name, index, source_id))

    profile = data.get("profile", {})
    if profile and not isinstance(profile, dict):
        errors.append("profile must be an object")
    if strict and isinstance(profile, dict) and profile.get("open_questions"):
        errors.append("strict mode requires profile.open_questions to be empty")

    privacy_mode = data.get("privacy_mode", "private")
    if privacy_mode not in ("private", "shareable"):
        errors.append("privacy_mode must be private or shareable")

    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--strict", action="store_true", help="treat placeholder-like draft content as an error")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a machine-readable report")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.brief.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error("input file does not exist: %s" % args.brief)
    except json.JSONDecodeError as exc:
        report = {"status": "error", "path": str(args.brief), "errors": ["invalid JSON: %s" % exc]}
        if args.as_json:
            print(json.dumps(report, indent=2))
        else:
            print("ERROR: %s" % report["errors"][0], file=sys.stderr)
        return 1

    errors, warnings = validate(data, strict=args.strict)
    report = {
        "status": "ok" if not errors else "fail",
        "path": str(args.brief),
        "strict": args.strict,
        "errors": errors,
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print("status: %s" % report["status"])
        for warning in warnings:
            print("warning: %s" % warning)
        for error in errors:
            print("error: %s" % error)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
