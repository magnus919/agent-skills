"""Sandbox staging for isolated skill evaluation trials.

Stages only the production-visible skill surface into a temporary directory,
excluding eval manifests, rubrics, oracles, and verifier code. The candidate
skill is mounted read-only to prevent self-modification during a trial.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path

EXCLUDED_DIRS = {"evals", "eval", "tests", "__pycache__", ".git"}
EXCLUDED_FILES = {"evals.json", "rubric.md", "baseline-protocol.md"}
EXCLUDED_SUFFIXES = {".pyc"}

PRODUCTION_SURFACE = {"SKILL.md", "README.md", "references", "templates", "scripts", "assets"}


def _is_excluded(path: Path, skill_root: Path) -> bool:
    rel = path.relative_to(skill_root)
    parts = rel.parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return True
    if path.name in EXCLUDED_FILES:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    return False


def _set_readonly(path: Path) -> None:
    current = path.stat().st_mode
    path.chmod(current & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def stage_skill_sandbox(skill_path: Path, *, readonly: bool = True) -> Path:
    """Copy production-visible skill surface into a fresh temp directory.

    Returns the staged skill directory path. Caller is responsible for cleanup
    (typically via tempfile.TemporaryDirectory context).
    """
    staging_root = Path(tempfile.mkdtemp(prefix="eval-sandbox-"))
    staged = staging_root / skill_path.name
    staged.mkdir()

    for item in skill_path.iterdir():
        if _is_excluded(item, skill_path):
            continue
        if item.name not in PRODUCTION_SURFACE and item.is_dir():
            continue
        dest = staged / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*EXCLUDED_DIRS))
        else:
            shutil.copy2(item, dest)

    if readonly:
        for root, dirs, files in os.walk(staged):
            for f in files:
                _set_readonly(Path(root) / f)
            for d in dirs:
                _set_readonly(Path(root) / d)
        _set_readonly(staged)

    return staged


def stage_baseline_sandbox(skill_path: Path) -> Path:
    """Create an empty skill directory (no SKILL.md) for the no-skill baseline."""
    staging_root = Path(tempfile.mkdtemp(prefix="eval-baseline-"))
    staged = staging_root / skill_path.name
    staged.mkdir()
    return staged


def stage_paired_sandboxes(skill_path: Path) -> tuple[Path, Path]:
    """Stage both candidate (with skill, read-only) and baseline (empty) sandboxes.

    Returns (candidate_path, baseline_path).
    """
    candidate = stage_skill_sandbox(skill_path, readonly=True)
    baseline = stage_baseline_sandbox(skill_path)
    return candidate, baseline


def cleanup_sandbox(staged_path: Path) -> None:
    """Remove a staged sandbox, restoring write permissions first."""
    if not staged_path.exists():
        return
    for root, dirs, files in os.walk(staged_path):
        for d in dirs:
            p = Path(root) / d
            p.chmod(p.stat().st_mode | stat.S_IWUSR)
        for f in files:
            p = Path(root) / f
            p.chmod(p.stat().st_mode | stat.S_IWUSR)
    staged_path.chmod(staged_path.stat().st_mode | stat.S_IWUSR)
    shutil.rmtree(staged_path.parent, ignore_errors=True)
