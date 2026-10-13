#!/usr/bin/env python3
"""Read-only TabPFN package inventory and task-manifest leakage/capacity screen."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path

MAX_BYTES = 16 * 1024 * 1024


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("invalid_time")
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid_time") from exc
    if result.tzinfo is None:
        raise ValueError("timezone_required")
    return result


def number(value):
    return type(value) in (float, int) and math.isfinite(value)


def audit(record):
    if (
        not isinstance(record, dict)
        or type(record.get("schema_version")) is not int
        or record["schema_version"] != 1
    ):
        raise ValueError("invalid_contract")
    if record.get("task") not in {"classification", "regression"}:
        raise ValueError("unsupported_task")
    checkpoint = record.get("checkpoint")
    if not isinstance(checkpoint, dict) or any(
        not isinstance(checkpoint.get(k), str) or not checkpoint[k].strip()
        for k in ("version", "revision", "license_decision", "package_version")
    ):
        raise ValueError("missing_checkpoint_record")
    policy = record.get("capacity")
    if not isinstance(policy, dict) or any(
        type(policy.get(k)) is not int or policy[k] < 1 for k in ("max_train_rows", "max_features")
    ):
        raise ValueError("invalid_capacity_policy")
    cutoff = timestamp(record.get("training_cutoff"))
    eval_cutoff = timestamp(record.get("evaluation_cutoff"))
    if eval_cutoff < cutoff:
        raise ValueError("evaluation_before_training")
    splits = record.get("splits")
    if not isinstance(splits, dict) or set(splits) != {"train", "calibration", "test"}:
        raise ValueError("three_splits_required")
    findings, ids, groups, content, classes, counts = [], set(), {}, {}, set(), {}
    width = None
    for split in ("train", "calibration", "test"):
        rows = splits[split]
        if not isinstance(rows, list) or not rows:
            raise ValueError("empty_or_invalid_split")
        counts[split] = len(rows)
        if split == "train" and len(rows) > policy["max_train_rows"]:
            findings.append({"code": "row_capacity", "split": split})
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict) or any(
                not isinstance(row.get(k), str) or not row[k].strip() for k in ("id", "group_id")
            ):
                raise ValueError("invalid_row_identity")
            identity = hashlib.sha256(row["id"].encode()).hexdigest()
            if identity in ids:
                findings.append({"code": "duplicate_id", "split": split, "row": index})
            ids.add(identity)
            group = hashlib.sha256(row["group_id"].encode()).hexdigest()
            if group in groups and groups[group] != split:
                findings.append({"code": "group_leakage", "split": split, "row": index})
            groups.setdefault(group, split)
            features = row.get("features")
            if not isinstance(features, list) or not features:
                raise ValueError("invalid_features")
            if width is None:
                width = len(features)
            if len(features) != width:
                raise ValueError("inconsistent_columns")
            if len(features) > policy["max_features"]:
                findings.append({"code": "feature_capacity", "split": split, "row": index})
            if any(v is not None and not isinstance(v, str) and not number(v) for v in features):
                raise ValueError("invalid_feature_value")
            key = hashlib.sha256(json.dumps(features, ensure_ascii=False).encode()).hexdigest()
            if key in content and content[key] != split:
                findings.append({"code": "exact_feature_overlap", "split": split, "row": index})
            content.setdefault(key, split)
            prediction = timestamp(row.get("prediction_time"))
            available = timestamp(row.get("feature_available_time"))
            label_available = timestamp(row.get("label_available_time"))
            if available > prediction:
                findings.append({"code": "future_feature", "split": split, "row": index})
            if label_available > (cutoff if split == "train" else eval_cutoff):
                findings.append({"code": "immature_label", "split": split, "row": index})
            if split == "train" and prediction > cutoff:
                findings.append({"code": "future_training_row", "row": index})
            if split != "train" and prediction <= cutoff:
                findings.append({"code": "nonforward_holdout", "split": split, "row": index})
            target = row.get("target")
            if record["task"] == "regression":
                if not number(target):
                    raise ValueError("invalid_regression_target")
            else:
                if type(target) not in (str, int, bool) or (
                    isinstance(target, str) and not target.strip()
                ):
                    raise ValueError("invalid_class_target")
                key = (type(target).__name__, str(target))
                if split == "train":
                    classes.add(key)
                elif key not in classes:
                    findings.append({"code": "unseen_class", "split": split, "row": index})
    if record["task"] == "classification" and len(classes) < 2:
        findings.append({"code": "single_training_class"})
    return {
        "schema_version": 1,
        "counts": counts,
        "features": width,
        "findings": findings,
        "checks_clear": not findings,
        "runtime": "not_run",
        "license": "not_verified",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    check = sub.add_parser("audit")
    check.add_argument("manifest", type=Path)
    args = parser.parse_args()
    if args.command == "doctor":
        versions = {}
        for name in ("tabpfn", "torch", "pandas", "scikit-learn"):
            try:
                versions[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                versions[name] = None
        report = {"packages": versions, "imports": "not_run", "model": "not_loaded"}
        code = 0
    else:
        try:
            with args.manifest.open("rb") as f:
                raw = f.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("size_limit")
            report = audit(json.loads(raw))
            report["input_sha256"] = hashlib.sha256(raw).hexdigest()
            code = 0 if report["checks_clear"] else 1
        except (OSError, ValueError, TypeError, KeyError):
            report = {
                "checks_clear": False,
                "error": "invalid_or_unreadable_manifest",
                "runtime": "not_run",
            }
            code = 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
