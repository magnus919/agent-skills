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


def _require_contained(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"sandbox source escapes skill root: {path}") from exc


def _reject_symlinks(path: Path, root: Path) -> None:
    """Fail closed if *path* or anything beneath it is a symlink."""
    if path.is_symlink():
        raise ValueError(f"sandbox source contains symlink: {path}")
    _require_contained(path, root)
    if not path.is_dir():
        return
    for current_root, dirs, files in os.walk(path, followlinks=False):
        current = Path(current_root)
        _require_contained(current, root)
        for name in [*dirs, *files]:
            child = current / name
            if child.is_symlink():
                raise ValueError(f"sandbox source contains symlink: {child}")
            _require_contained(child, root)


def _is_excluded(path: Path, skill_root: Path) -> bool:
    rel = path.relative_to(skill_root)
    parts = rel.parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return True
    if path.name in EXCLUDED_FILES:
        return True
    return path.suffix in EXCLUDED_SUFFIXES


def _set_readonly(path: Path) -> None:
    current = path.stat().st_mode
    path.chmod(current & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def stage_skill_sandbox(skill_path: Path, *, readonly: bool = True) -> Path:
    """Copy production-visible skill surface into a fresh temp directory.

    Returns the staged skill directory path. Caller is responsible for cleanup
    (typically via tempfile.TemporaryDirectory context).
    """
    if skill_path.is_symlink():
        raise ValueError(f"skill path must not be a symlink: {skill_path}")
    skill_root = skill_path.resolve()
    items: list[Path] = []
    for item in skill_path.iterdir():
        if _is_excluded(item, skill_path):
            continue
        if item.name not in PRODUCTION_SURFACE and item.is_dir():
            continue
        _reject_symlinks(item, skill_root)
        items.append(item)

    staging_root = Path(tempfile.mkdtemp(prefix="eval-sandbox-"))
    staged = staging_root / skill_path.name
    staged.mkdir()

    for item in items:
        dest = staged / item.name
        if item.is_dir():
            shutil.copytree(
                item,
                dest,
                ignore=shutil.ignore_patterns(*EXCLUDED_DIRS),
                symlinks=True,
            )
        else:
            shutil.copy2(item, dest, follow_symlinks=False)

    _reject_symlinks(staged, staging_root)

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
    try:
        baseline = stage_baseline_sandbox(skill_path)
    except Exception:
        cleanup_sandbox(candidate)
        raise
    return candidate, baseline


def cleanup_sandbox(staged_path: Path) -> None:
    """Remove a staged sandbox without following replacement symlinks."""
    staging_root = staged_path.parent
    open_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        root_fd = os.open(staging_root, open_flags)
    except FileNotFoundError:
        return
    except OSError:
        # A replacement symlink must be unlinked, never traversed. If the path
        # changed to anything else, fail closed and leave it for inspection.
        if staging_root.is_symlink():
            staging_root.unlink()
            return
        raise

    try:
        for _root, _dirs, _files, dir_fd in os.fwalk(
            ".",
            topdown=True,
            follow_symlinks=False,
            dir_fd=root_fd,
        ):
            current_mode = stat.S_IMODE(os.fstat(dir_fd).st_mode)
            os.fchmod(dir_fd, current_mode | stat.S_IWUSR)
    finally:
        os.close(root_fd)

    # rmtree uses descriptor-relative operations on supported Unix platforms
    # and refuses to descend through symlinks introduced after the fwalk.
    shutil.rmtree(staging_root)
