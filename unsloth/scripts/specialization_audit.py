#!/usr/bin/env python3
"""Read-only provenance/split and verifier-receipt audits; never executes code."""

import argparse
import hashlib
import json
import math
from pathlib import Path

MAX_LINE = 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_ROWS = 100000
CATEGORIES = {"correct", "incorrect", "malformed", "adversarial", "timeout", "infrastructure_error"}


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def text(value):
    return isinstance(value, str) and bool(value.strip())


def hash_id(value):
    return (
        isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    )


def read_rows(path, limit=MAX_ROWS):
    """Bound line allocation and total bytes; no partial scan can pass."""
    size = 0
    with Path(path).open("rb") as stream:
        for number in range(1, limit + 2):
            raw = stream.readline(MAX_LINE + 1)
            if not raw:
                return
            size += len(raw)
            if number > limit or len(raw) > MAX_LINE or size > MAX_TOTAL:
                raise ValueError("scan_limit")
            try:
                value = json.loads(raw)
            except (ValueError, UnicodeError) as exc:
                raise ValueError("invalid_json") from exc
            if not isinstance(value, dict):
                raise ValueError("row_not_object")
            yield number, value


def validate_data(row):
    if not all(text(row.get(k)) for k in ("id", "group_id")):
        raise ValueError("missing_identity")
    source = row.get("source")
    if not isinstance(source, dict) or not all(
        text(source.get(k)) for k in ("uri", "revision", "rights")
    ):
        raise ValueError("missing_provenance")
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        raise ValueError("unsupported_messages")
    if any(
        not isinstance(m, dict)
        or set(m) != {"role", "content"}
        or m["role"] not in {"system", "user", "assistant"}
        or not text(m["content"])
        for m in messages
    ):
        raise ValueError("unsupported_messages")
    if messages[-1]["role"] != "assistant" or not any(m["role"] == "user" for m in messages):
        raise ValueError("missing_target_or_prompt")
    return digest(messages[:-1]), digest(messages)


def data_audit(paths, limit=MAX_ROWS):
    findings, counts = [], {}
    identities, groups, prompts, content = {}, {}, {}, {}
    for split, path in paths.items():
        counts[split] = 0
        try:
            for line, row in read_rows(path, limit):
                counts[split] += 1
                prompt, full = validate_data(row)
                for kind, key, seen, cross_only in (
                    ("duplicate_id", digest(row["id"]), identities, False),
                    ("group_leakage", digest(row["group_id"]), groups, True),
                    ("prompt_overlap", prompt, prompts, True),
                    ("duplicate_content", full, content, False),
                ):
                    if key in seen and (not cross_only or seen[key][0] != split):
                        findings.append(
                            {
                                "code": kind,
                                "split": split,
                                "line": line,
                                "first_split": seen[key][0],
                                "first_line": seen[key][1],
                            }
                        )
                    else:
                        seen.setdefault(key, (split, line))
        except (ValueError, OSError) as exc:
            code = str(exc) if isinstance(exc, ValueError) else "unreadable_file"
            findings.append({"code": code, "split": split})
        if not counts[split]:
            findings.append({"code": "empty_split", "split": split})
    return {
        "schema_version": 1,
        "audit": "provenance_and_splits",
        "counts": counts,
        "findings": findings,
        "checks_clear": not findings,
        "behavior": "not_assessed",
    }


def reward_audit(path):
    findings = []
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_TOTAL + 1)
        if len(raw) > MAX_TOTAL:
            raise ValueError("scan_limit")
        record = json.loads(raw)
        if (
            not isinstance(record, dict)
            or type(record.get("schema_version")) is not int
            or record["schema_version"] != 1
        ):
            raise ValueError("invalid_contract")
        if not all(hash_id(record.get(k)) for k in ("verifier_sha256", "suite_sha256")):
            raise ValueError("unpinned_verifier")
        cases = record.get("cases")
        if not isinstance(cases, list) or not cases or len(cases) > MAX_ROWS:
            raise ValueError("invalid_roster")
        seen, categories = set(), set()
        for line, case in enumerate(cases, 1):
            if not isinstance(case, dict) or not text(case.get("id")) or case["id"] in seen:
                raise ValueError("invalid_case_identity")
            seen.add(case["id"])
            category = case.get("category")
            if category not in CATEGORIES:
                raise ValueError("invalid_category")
            categories.add(category)
            label = case.get("label")
            if (
                not isinstance(label, dict)
                or label.get("kind") not in {"human", "reference"}
                or not text(label.get("evidence"))
            ):
                raise ValueError("untrusted_label_provenance")
            reward = case.get("reward")
            if type(reward) not in (int, float) or not math.isfinite(reward):
                raise ValueError("nonfinite_reward")
            expected, status = case.get("expected_correct"), case.get("execution_status")
            if category in {"timeout", "infrastructure_error"}:
                if expected is not None or status != category or reward != 0:
                    findings.append({"code": "failure_misclassified", "line": line})
                continue
            if type(expected) is not bool or status not in {"passed", "failed"}:
                raise ValueError("invalid_outcome")
            if expected != (category == "correct"):
                raise ValueError("contradictory_label")
            if (status == "passed") != expected:
                findings.append(
                    {
                        "code": "false_acceptance" if status == "passed" else "false_rejection",
                        "line": line,
                    }
                )
            if (expected and reward <= 0) or (not expected and reward > 0):
                findings.append({"code": "reward_order_violation", "line": line})
        for category in sorted(CATEGORIES - categories):
            findings.append({"code": "missing_challenge_category", "category": category})
    except (OSError, ValueError, TypeError, KeyError) as exc:
        code = str(exc) if type(exc) is ValueError else "invalid_or_unreadable_contract"
        # Never print parser messages containing private input text.
        if isinstance(exc, (json.JSONDecodeError, UnicodeError)):
            code = "invalid_json"
        findings.append({"code": code})
    return {
        "schema_version": 1,
        "audit": "verifier_receipts",
        "findings": findings,
        "checks_clear": not findings,
        "execution": "not_performed",
        "release": "not_assessed",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    data = commands.add_parser("data")
    for split in ("train", "development", "test"):
        data.add_argument("--" + split, type=Path, required=True)
    data.add_argument("--max-rows", type=int, default=MAX_ROWS)
    reward = commands.add_parser("rewards")
    reward.add_argument("receipts", type=Path)
    args = parser.parse_args()
    if args.command == "data":
        if not 1 <= args.max_rows <= MAX_ROWS:
            parser.error("max-rows must be between 1 and 100000")
        report = data_audit(
            {s: getattr(args, s) for s in ("train", "development", "test")}, args.max_rows
        )
    else:
        report = reward_audit(args.receipts)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["checks_clear"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
