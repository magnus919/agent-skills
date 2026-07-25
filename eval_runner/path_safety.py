"""Validation and containment helpers for repository-controlled eval paths."""

from __future__ import annotations

import errno
import hashlib
import os
import re
import stat
from pathlib import Path, PurePosixPath

_CASE_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*", re.ASCII)


def validate_case_id(case_id: str) -> str:
    """Return a safe case ID or raise ValueError for unsafe input."""
    if (
        not isinstance(case_id, str)
        or len(case_id) > 64
        or _CASE_ID_RE.fullmatch(case_id) is None
    ):
        raise ValueError(
            "invalid eval case ID: expected 1-64 lowercase ASCII letters or digits "
            "separated by single hyphens"
        )
    return case_id


def validate_relative_path(path_text: str) -> str:
    """Return a schema-compatible relative POSIX path or raise ValueError."""
    if not isinstance(path_text, str) or not path_text or not path_text.strip():
        raise ValueError("invalid relative path: expected a non-empty path")
    if any(ord(character) < 32 or ord(character) == 127 for character in path_text):
        raise ValueError("invalid relative path: control characters are forbidden")
    if "\\" in path_text or path_text.endswith("/"):
        raise ValueError("invalid relative path: backslashes and trailing slashes are forbidden")

    lexical_parts = path_text.split("/")
    if any(part in {"", ".", ".."} for part in lexical_parts):
        raise ValueError("invalid relative path: '.', '..', and empty components are forbidden")

    pure = PurePosixPath(path_text)
    if pure.is_absolute() or not pure.parts:
        raise ValueError("invalid relative path: expected a relative POSIX path")
    return path_text


def hash_contained_file(root: Path, relative_path: str) -> str | None:
    """Hash a regular file beneath root without following symlinks.

    Returns ``None`` when the path is absent or not a regular file. Every path
    component is opened descriptor-relatively with ``O_NOFOLLOW`` so a
    validation-to-read symlink swap cannot redirect the read outside ``root``.
    """
    validate_relative_path(relative_path)
    root_path = root.resolve(strict=True)
    parts = PurePosixPath(relative_path).parts
    opened_fds: list[int] = []

    try:
        current_fd = os.open(
            root_path,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
        opened_fds.append(current_fd)

        for component in parts[:-1]:
            current_fd = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=current_fd,
            )
            opened_fds.append(current_fd)

        file_fd = os.open(
            parts[-1],
            os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW,
            dir_fd=current_fd,
        )
        opened_fds.append(file_fd)
        if not stat.S_ISREG(os.fstat(file_fd).st_mode):
            return None

        digest = hashlib.sha256()
        while chunk := os.read(file_fd, 64 * 1024):
            digest.update(chunk)
        return digest.hexdigest()[:16]
    except FileNotFoundError:
        return None
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise ValueError(
                f"unsafe symlink component in contained path: {relative_path}"
            ) from exc
        raise
    finally:
        for descriptor in reversed(opened_fds):
            os.close(descriptor)


def contained_path(root: Path, *parts: str) -> Path:
    """Resolve a child path and require it to remain beneath *root*."""
    resolved_root = root.resolve()
    candidate = resolved_root.joinpath(*parts).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"output path escapes designated root: {candidate}") from exc
    return candidate
