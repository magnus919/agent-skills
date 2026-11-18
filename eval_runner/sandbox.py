"""Sandbox staging for isolated skill evaluation trials.

Stages only the production-visible skill surface into a temporary directory,
excluding eval manifests, rubrics, oracles, and verifier code. The candidate
skill is mounted read-only to prevent self-modification during a trial.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path

EXCLUDED_DIRS = {"evals", "eval", "tests", "__pycache__", ".git"}
EXCLUDED_FILES = {"evals.json", "rubric.md", "baseline-protocol.md"}
EXCLUDED_SUFFIXES = {".pyc"}

PRODUCTION_SURFACE = {"SKILL.md", "README.md", "references", "templates", "scripts", "assets"}
RUNTIME_DECLARATION = "runtime-resources.json"


def skill_package_root(skill_path: Path) -> Path:
    """Resolve the known bundle layout while preserving a standalone skill root."""
    parent = skill_path.parent
    package = parent.parent
    if (
        parent.name == "skills"
        and (package / "SKILL.md").is_file()
        and (package / "manifest.yaml").is_file()
    ):
        return package
    return skill_path


def _runtime_surface(package: Path) -> set[str]:
    allowed = set(PRODUCTION_SURFACE)
    if (package / "manifest.yaml").is_file():
        allowed.add("skills")
    declaration = package / RUNTIME_DECLARATION
    if not declaration.exists() and not declaration.is_symlink():
        return allowed
    _reject_symlinks(declaration, package)
    if not declaration.is_file():
        raise ValueError(f"runtime resource declaration must be a file: {declaration}")
    names = json.loads(declaration.read_text(encoding="utf-8"))
    if not isinstance(names, list) or any(
        not isinstance(name, str)
        or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", name)
        or name in EXCLUDED_DIRS
        or not (package / name).is_dir()
        for name in names
    ):
        raise ValueError(f"invalid runtime resource declaration: {declaration}")
    return allowed.union(names)


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


def _copy_skill_surface(source: Path, destination: Path) -> None:
    allowed = _runtime_surface(source)
    destination.mkdir()
    for item in source.iterdir():
        if _is_excluded(item, source):
            continue
        if item.name not in allowed and item.is_dir():
            continue
        _reject_symlinks(item, source)
        target = destination / item.name
        if item.name == "skills" and item.is_dir():
            target.mkdir()
            for child in item.iterdir():
                if child.is_dir() and (child / "SKILL.md").is_file():
                    _copy_skill_surface(child, target / child.name)
        elif item.is_dir():
            shutil.copytree(
                item,
                target,
                ignore=shutil.ignore_patterns(*EXCLUDED_DIRS, *EXCLUDED_FILES, "*.pyc"),
                symlinks=True,
            )
        else:
            shutil.copy2(item, target, follow_symlinks=False)


def stage_skill_sandbox(skill_path: Path, *, readonly: bool = True) -> Path:
    """Copy the skill package and return the staged entry point directory."""
    if skill_path.is_symlink():
        raise ValueError(f"skill path must not be a symlink: {skill_path}")
    package = skill_package_root(skill_path)
    if package.is_symlink() or (package != skill_path and skill_path.parent.is_symlink()):
        raise ValueError(f"sandbox source contains symlink in package path: {skill_path}")

    staging_root = Path(tempfile.mkdtemp(prefix="eval-sandbox-"))
    staged = staging_root / package.name
    entry = staged / skill_path.relative_to(package)
    try:
        _copy_skill_surface(package, staged)
        _reject_symlinks(staged, staging_root)
        if not entry.is_dir():
            raise ValueError(f"staged skill entry point is absent: {skill_path}")
        if readonly:
            for root, dirs, files in os.walk(staged):
                for f in files:
                    _set_readonly(Path(root) / f)
                for d in dirs:
                    _set_readonly(Path(root) / d)
            _set_readonly(staged)
    except Exception:
        cleanup_sandbox(staged)
        raise
    return entry


def stage_baseline_sandbox(skill_path: Path) -> Path:
    """Create an empty skill directory (no SKILL.md) for the no-skill baseline."""
    staging_root = Path(tempfile.mkdtemp(prefix="eval-baseline-"))
    staged = staging_root / skill_path.name
    staged.mkdir()
    return staged


def stage_paired_sandboxes(
    skill_path: Path,
    *,
    comparison_mode: str = "skill_vs_no_skill",
    baseline_skill_path: Path | None = None,
) -> tuple[Path, Path]:
    """Stage an explicitly labeled no-skill diagnostic or pinned skill pair."""
    if comparison_mode not in {"skill_vs_no_skill", "pinned_skill_vs_skill"}:
        raise ValueError("unsupported paired comparison mode")
    if comparison_mode == "pinned_skill_vs_skill" and baseline_skill_path is None:
        raise ValueError("pinned_skill_vs_skill requires --baseline-skill-path")
    if comparison_mode == "skill_vs_no_skill" and baseline_skill_path is not None:
        raise ValueError("skill_vs_no_skill does not accept a baseline skill snapshot")

    candidate = stage_skill_sandbox(skill_path, readonly=True)
    try:
        if baseline_skill_path is None:
            baseline = stage_baseline_sandbox(skill_path)
        else:
            baseline = stage_skill_sandbox(baseline_skill_path, readonly=True)
    except Exception:
        cleanup_sandbox(candidate)
        raise
    return candidate, baseline


def cleanup_sandbox(staged_path: Path) -> None:
    """Remove a staged sandbox without following replacement symlinks."""
    staging_root = staged_path.parent
    if staging_root.name == "skills" and staged_path.parents[2].name.startswith("eval-sandbox-"):
        staging_root = staged_path.parents[2]
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
