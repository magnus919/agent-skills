#!/usr/bin/env python3
"""Emit a content-hash manifest for an explicitly selected review input set."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any

CHUNK_SIZE = 1024 * 1024


def _fingerprint(path: Path, relative_path: str) -> dict[str, Any]:
    digest = hashlib.sha256()
    byte_count = 0
    try:
        with path.open("rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise ValueError(f"not a regular file: {relative_path}")
            for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                byte_count += len(chunk)
                digest.update(chunk)
            after = os.fstat(stream.fileno())
    except OSError as exc:
        raise ValueError(f"cannot read {relative_path}: {exc}") from exc

    before_state = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    after_state = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if before_state != after_state or byte_count != after.st_size:
        raise ValueError(f"file changed while being hashed: {relative_path}")

    return {
        "path": relative_path,
        "size_bytes": byte_count,
        "sha256": digest.hexdigest(),
    }


def _resolve_input(value: str, root: Path) -> tuple[str, Path]:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
        relative = resolved.relative_to(root)
    except FileNotFoundError as exc:
        raise ValueError(f"input does not exist: {value}") from exc
    except OSError as exc:
        raise ValueError(f"cannot resolve input {value}: {exc}") from exc
    except ValueError as exc:
        raise ValueError(f"input escapes review root: {value}") from exc

    if not resolved.is_file():
        raise ValueError(f"input is not a regular file: {value}")
    return relative.as_posix(), resolved


def build_manifest(root_value: str, target_value: str, context_values: list[str]) -> dict[str, Any]:
    root = Path(root_value).resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"review root is not a directory: {root_value}")

    target_path, target_file = _resolve_input(target_value, root)
    target = _fingerprint(target_file, target_path)

    context_inputs = [_resolve_input(value, root) for value in context_values]
    context_paths = [relative for relative, _ in context_inputs]
    if target_path in context_paths:
        raise ValueError("target must not also be listed as context")
    if len(set(context_paths)) != len(context_paths):
        raise ValueError("context inputs contain duplicate resolved paths")

    context = [
        _fingerprint(path, relative)
        for relative, path in sorted(context_inputs, key=lambda item: item[0])
    ]
    payload: dict[str, Any] = {
        "schema_version": 1,
        "target": target,
        "context": context,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["bundle_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hash one review target and its explicitly selected local context files."
    )
    parser.add_argument("--root", default=".", help="Root that all review inputs must remain inside")
    parser.add_argument("--target", required=True, help="Target artifact path")
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Explicit supporting file path; repeat for each file",
    )
    args = parser.parse_args()

    try:
        manifest = build_manifest(args.root, args.target, args.context)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
