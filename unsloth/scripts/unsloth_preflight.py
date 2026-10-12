#!/usr/bin/env python3
"""Read-only inventory and bounded text-SFT JSONL audit. No GPU imports/network."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import sys
from pathlib import Path

PACKAGES = (
    "unsloth",
    "unsloth_zoo",
    "torch",
    "transformers",
    "trl",
    "peft",
    "datasets",
    "bitsandbytes",
    "triton",
    "xformers",
    "vllm",
)
MAX_LINE_BYTES = 1024 * 1024
MAX_ROWS = 100_000
MAX_ISSUES = 30


def doctor():
    versions = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "schema_version": 1,
        "command": "doctor",
        "python": platform.python_version(),
        "platform": platform.system(),
        "machine": platform.machine(),
        "packages": versions,
        "executables": {
            name: shutil.which(name) is not None
            for name in ("nvidia-smi", "rocminfo", "xpu-smi", "uv", "git", "cmake")
        },
        "compatibility": "not_assessed",
        "gpu_execution": "not_run",
    }


def content_of(row):
    """Return the training payload only, refusing unsupported/ambiguous shapes."""
    if not isinstance(row, dict):
        raise ValueError("row must be an object")
    if any(key in row for key in ("chosen", "rejected", "images", "audio", "tools")):
        raise ValueError("preference, multimodal, or tool data needs a task-specific audit")
    if ("text" in row) == ("messages" in row):
        raise ValueError("supply exactly one of text or messages")
    if "text" in row:
        if not isinstance(row["text"], str) or not row["text"].strip():
            raise ValueError("text must be a nonempty string")
        return {"text": row["text"]}
    messages = row["messages"]
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a nonempty list")
    normalized = []
    for message in messages:
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise ValueError("each message must contain only role and content")
        role, content = message["role"], message["content"]
        if not isinstance(role, str) or role not in ("system", "user", "assistant"):
            raise ValueError("only system, user, assistant text messages are supported")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("message content must be a nonempty string")
        normalized.append({"role": role, "content": content})
    if not any(m["role"] == "assistant" for m in normalized):
        raise ValueError("conversation has no assistant target")
    if not any(m["role"] == "user" for m in normalized):
        raise ValueError("conversation has no user prompt")
    if normalized[-1]["role"] != "assistant":
        raise ValueError("text-SFT conversation must end with an assistant target")
    return {"messages": normalized}


def reject_constant(_value):
    raise ValueError("non-finite JSON number")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def scan(path, *, max_rows=MAX_ROWS, max_line_bytes=MAX_LINE_BYTES):
    report = {
        "rows": 0,
        "valid_rows": 0,
        "invalid_rows": 0,
        "duplicate_rows": 0,
        "formats": [],
        "complete": True,
        "issues": [],
        "issue_count": 0,
    }
    fingerprints = set()
    formats = set()

    def issue(line, reason):
        report["issue_count"] += 1
        if len(report["issues"]) < MAX_ISSUES:
            report["issues"].append({"line": line, "reason": reason})

    try:
        if not Path(path).is_file():
            raise OSError("not a regular file")
        with Path(path).open("rb") as stream:
            line_number = 0
            while True:
                raw = stream.readline(max_line_bytes + 1)
                if not raw:
                    break
                line_number += 1
                if line_number > max_rows:
                    report["complete"] = False
                    issue(line_number, "row limit reached; audit incomplete")
                    break
                if len(raw) > max_line_bytes:
                    report["complete"] = False
                    issue(line_number, "line byte limit exceeded; audit incomplete")
                    break
                report["rows"] += 1
                try:
                    row = json.loads(
                        raw.decode("utf-8"),
                        parse_constant=reject_constant,
                        object_pairs_hook=unique_keys,
                    )
                    payload = content_of(row)
                    encoded = json.dumps(
                        payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
                    ).encode("ascii")
                except (ValueError, UnicodeError, RecursionError):
                    report["invalid_rows"] += 1
                    # Do not copy parser errors: they can contain training text.
                    issue(line_number, "invalid JSON or unsupported text-SFT structure")
                    continue
                report["valid_rows"] += 1
                formats.update(payload)
                fingerprint = hashlib.sha256(encoded).digest()
                if fingerprint in fingerprints:
                    report["duplicate_rows"] += 1
                    issue(line_number, "duplicate training content within split")
                fingerprints.add(fingerprint)
    except OSError:
        report["complete"] = False
        issue(None, "cannot read regular input file")
    if report["rows"] == 0 and report["complete"]:
        issue(None, "empty dataset")
    if len(formats) > 1:
        issue(None, "mixed text and messages formats")
    report["formats"] = sorted(formats)
    return report, fingerprints


def audit(train_path, eval_path=None):
    train, train_hashes = scan(train_path)
    report = {
        "schema_version": 1,
        "command": "dataset",
        "train": train,
        "overlap_unique_rows": None,
        "tokenization": "not_assessed",
        "semantic_leakage": "not_assessed",
        "ok": False,
    }
    bad = train["issue_count"] > 0
    if eval_path is not None:
        evaluation, eval_hashes = scan(eval_path)
        report["eval"] = evaluation
        report["overlap_unique_rows"] = len(train_hashes & eval_hashes)
        report["split_formats_match"] = train["formats"] == evaluation["formats"]
        bad = (
            bad
            or evaluation["issue_count"] > 0
            or report["overlap_unique_rows"] > 0
            or not report["split_formats_match"]
        )
    report["ok"] = not bad
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Exit 0: inventory completed or dataset checks clean; 1: dataset findings "
            "or incomplete scan; 2: CLI misuse. Dataset limits: 100,000 rows/split, "
            "1 MiB/line, 30 issue details/split. No input content is printed."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("doctor", help="inventory; compatibility is not assessed")
    inventory.add_argument("--json", action="store_true", help="emit JSON (also the default)")
    dataset = subparsers.add_parser("dataset", help="audit text-SFT JSONL without tokenization")
    dataset.add_argument("train_file", type=Path)
    dataset.add_argument("--eval-file", type=Path)
    dataset.add_argument("--json", action="store_true", help="emit JSON (also the default)")
    args = parser.parse_args(argv)
    result = doctor() if args.command == "doctor" else audit(args.train_file, args.eval_file)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result.get("ok") is False else 0


if __name__ == "__main__":
    sys.exit(main())
