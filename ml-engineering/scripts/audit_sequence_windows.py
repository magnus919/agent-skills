#!/usr/bin/env python3
"""Read-only sequence-window availability, boundary and label-leakage checks."""

import argparse
import datetime as dt
import json
from pathlib import Path

MAX_BYTES = 16 * 1024 * 1024


def time(value):
    if not isinstance(value, str):
        raise ValueError("invalid_timestamp")
    try:
        x = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("invalid_timestamp") from e
    if x.tzinfo is None:
        raise ValueError("timezone_required")
    return x


def audit(record):
    if (
        not isinstance(record, dict)
        or type(record.get("schema_version")) is not int
        or record["schema_version"] != 1
    ):
        raise ValueError("invalid_contract")
    if record.get("split_mode") not in {"forward", "entity_holdout"}:
        raise ValueError("invalid_split_mode")
    windows = record.get("windows")
    if not isinstance(windows, list) or not windows:
        raise ValueError("empty_windows")
    cutoff = time(record.get("training_cutoff"))
    matured = time(record.get("evaluation_cutoff"))
    if matured < cutoff:
        raise ValueError("invalid_cutoff_order")
    ids = set()
    targets = {}
    entities = {}
    ranges = {}
    findings = []
    event_identity = {}
    for index, w in enumerate(windows, 1):
        if not isinstance(w, dict) or any(
            not isinstance(w.get(k), str) or not w[k].strip()
            for k in ("id", "entity_id", "target_id")
        ):
            raise ValueError("invalid_identity")
        split = w.get("split")
        if split not in {"train", "development", "test"}:
            raise ValueError("invalid_split")
        if w["id"] in ids:
            findings.append({"code": "duplicate_window", "window": index})
        ids.add(w["id"])
        if w["target_id"] in targets:
            findings.append({"code": "duplicate_target", "window": index})
        targets[w["target_id"]] = split
        previous = entities.setdefault(w["entity_id"], split)
        if record["split_mode"] == "entity_holdout" and previous != split:
            findings.append({"code": "entity_leakage", "window": index})
        origin = time(w.get("prediction_time"))
        label = time(w.get("label_available_time"))
        ranges.setdefault(split, []).append(origin)
        if label > (cutoff if split == "train" else matured):
            findings.append({"code": "immature_label", "window": index})
        if split == "train" and origin > cutoff:
            findings.append({"code": "future_training_window", "window": index})
        if split != "train" and origin <= cutoff:
            findings.append({"code": "nonforward_window", "window": index})
        events = w.get("events")
        if not isinstance(events, list) or not events:
            raise ValueError("empty_events")
        last = None
        seen = set()
        for event in events:
            if not isinstance(event, dict) or any(
                not isinstance(event.get(k), str) or not event[k].strip()
                for k in ("id", "entity_id")
            ):
                raise ValueError("invalid_event")
            event_time = time(event.get("event_time"))
            available = time(event.get("available_time"))
            if event_time > origin or available > origin:
                findings.append({"code": "future_context", "window": index})
            if last is not None and event_time < last:
                findings.append({"code": "unordered_context", "window": index})
            last = event_time
            if event["entity_id"] != w["entity_id"]:
                findings.append({"code": "cross_entity_context", "window": index})
            if event["id"] == w["target_id"]:
                findings.append({"code": "self_in_history", "window": index})
            if event["id"] in seen:
                findings.append({"code": "duplicate_event_in_window", "window": index})
            seen.add(event["id"])
            if event.get("contains_outcome") is not False:
                findings.append({"code": "outcome_in_context_or_unreviewed", "window": index})
            key = (event["entity_id"], event_time, available)
            if event["id"] in event_identity and event_identity[event["id"]] != key:
                findings.append({"code": "event_identity_changed", "window": index})
            event_identity[event["id"]] = key
    if set(ranges) != {"train", "development", "test"}:
        findings.append({"code": "missing_split"})
    if (
        record["split_mode"] == "forward"
        and all(s in ranges for s in ("train", "development", "test"))
        and (
            max(ranges["train"]) >= min(ranges["development"])
            or max(ranges["development"]) >= min(ranges["test"])
        )
    ):
        findings.append({"code": "fold_boundary_overlap"})
    return {
        "schema_version": 1,
        "windows": len(windows),
        "findings": findings,
        "checks_clear": not findings,
        "semantic_feature_leakage": "not_assessed",
        "model_execution": "not_run",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    a = p.parse_args()
    try:
        with a.manifest.open("rb") as f:
            raw = f.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("size_limit")
        result = audit(json.loads(raw))
        code = 0 if result["checks_clear"] else 1
    except (OSError, ValueError, TypeError, KeyError):
        result = {"checks_clear": False, "error": "invalid_or_unreadable_manifest"}
        code = 1
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
