#!/usr/bin/env python3
"""Validate every eval manifest against the repository-owned v1 contract."""

import sys
from pathlib import Path

from eval_validation import find_skill_manifests, validate_manifest

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    manifests = find_skill_manifests(ROOT)
    errors = []
    for manifest in manifests:
        errors.extend(validate_manifest(manifest, ROOT).errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Validated {len(manifests)} eval manifests against repository schema v1 and semantic repository checks."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
