"""Capture declared task inputs once and present identical copies to each arm."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .reference_inputs import read_binary_source

_MAX_FIXTURE_BYTES = 5 * 1024 * 1024
_MAX_TRIAL_BYTES = 16 * 1024 * 1024


def capture_fixtures(skill_root: Path, paths: list[str]) -> dict[str, bytes]:
    fixtures = {}
    remaining = _MAX_TRIAL_BYTES
    for relative in paths:
        data = read_binary_source(skill_root, relative, min(_MAX_FIXTURE_BYTES, remaining))
        fixtures[relative] = data
        remaining -= len(data)
    return fixtures


def fixture_hashes(fixtures: dict[str, bytes]) -> dict[str, str]:
    return {relative: hashlib.sha256(data).hexdigest()[:16] for relative, data in fixtures.items()}


def write_fixtures(fixtures: dict[str, bytes], directory: Path) -> Path | None:
    if not fixtures:
        return None
    directory.mkdir(parents=True, exist_ok=False)
    for relative, data in fixtures.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
        path.chmod(0o400)
    return directory
