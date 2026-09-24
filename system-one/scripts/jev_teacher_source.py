#!/usr/bin/env python3
"""Validate trusted GitHub Actions provenance for Jev teacher calibration."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

EXPECTED_PATH = ".github/workflows/skill-eval.yml"
ALLOWED_EVENTS = frozenset({"push", "workflow_dispatch"})


def validate_source(metadata: Any, expected_run_id: str) -> str:
    """Return the allowed source event or reject untrusted/incomplete metadata."""
    if not re.fullmatch(r"[1-9][0-9]{0,19}", expected_run_id):
        raise ValueError("source run ID must be a positive decimal integer")
    if not isinstance(metadata, dict):
        raise ValueError("GitHub returned invalid workflow-run metadata")

    run_id = metadata.get("id")
    if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id != int(expected_run_id):
        raise ValueError("GitHub run metadata does not match the requested source ID")

    event = metadata.get("event")
    if (
        metadata.get("head_branch") != "main"
        or metadata.get("conclusion") != "success"
        or metadata.get("path") != EXPECTED_PATH
        or not isinstance(event, str)
        or event not in ALLOWED_EVENTS
    ):
        raise ValueError(
            "source must be a successful main-branch skill-eval run triggered by push or workflow_dispatch"
        )
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run-id", required=True)
    args = parser.parse_args()
    try:
        metadata = json.load(sys.stdin)
        event = validate_source(metadata, args.source_run_id)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Source verification failed: {exc}", file=sys.stderr)
        return 2
    print(f"Verified successful main-branch skill-eval source ({event})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
