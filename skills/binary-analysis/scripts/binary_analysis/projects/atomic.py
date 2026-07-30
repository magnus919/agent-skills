"""Atomic file write utility using tempfile + os.rename.

Provides safe atomic write patterns for all persistent state:
manifests, audit logs, cache, and reports.

Key guarantees:
- Writes to a temporary file first (in the same directory as the target).
- os.rename is atomic on the same filesystem — it either replaces or it doesn't.
- A process crash mid-write leaves the previous valid state intact.
- The target file is never partially written or truncated.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from typing import Any


def atomic_write_text(
    path: str,
    content: str,
    encoding: str = "utf-8",
    mode: int = 0o644,
) -> None:
    """Atomically write text content to a file.

    Writes content to a temporary file in the same directory, then atomically
    renames it to the target path. If the process crashes mid-write, the
    temporary file is left behind and the target file is unaffected.

    Args:
        path: Target file path.
        content: Text content to write.
        encoding: Character encoding (default utf-8).
        mode: File permissions (default 0o644).
    """
    dirname = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dirname, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, path)  # Atomic rename on same filesystem
    except BaseException:
        # Clean up temp file on any error, then re-raise
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise


def atomic_write_json(
    path: str,
    data: dict[str, Any],
    indent: int = 2,
    encoding: str = "utf-8",
    mode: int = 0o644,
) -> None:
    """Atomically write JSON data to a file.

    Serializes the data to JSON, then atomically writes it using
    atomic_write_text. Invalid JSON data (non-serializable) raises
    before any file is touched.

    Args:
        path: Target file path.
        data: JSON-serializable dict to write.
        indent: JSON indentation level.
        encoding: Character encoding.
        mode: File permissions.
    """
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    atomic_write_text(path, content, encoding=encoding, mode=mode)


def atomic_append_text(
    path: str,
    line: str,
    encoding: str = "utf-8",
    mode: int = 0o644,
) -> None:
    """Atomically append a single line to a file.

    For append-only files like audit logs (events.jsonl), this reads the
    existing content, appends the line, and writes atomically. This ensures
    no partial lines or interleaving in the canonical file.

    Args:
        path: Target file path.
        line: Single line to append (newline added if not present).
        encoding: Character encoding.
        mode: File permissions.
    """
    if not line.endswith("\n"):
        line += "\n"

    # Read existing content or start fresh
    try:
        with open(path, encoding=encoding) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = ""

    new_content = existing + line
    atomic_write_text(path, new_content, encoding=encoding, mode=mode)


def atomic_write_binary(
    path: str,
    data: bytes,
    mode: int = 0o644,
) -> None:
    """Atomically write binary data to a file.

    Writes binary data to a temporary file, then renames atomically.

    Args:
        path: Target file path.
        data: Binary content to write.
        mode: File permissions.
    """
    dirname = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dirname, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise


def atomic_write_lines(
    path: str,
    lines: list[str],
    encoding: str = "utf-8",
    mode: int = 0o644,
) -> None:
    """Atomically write a list of lines to a file.

    Each line is written with a trailing newline.

    Args:
        path: Target file path.
        lines: List of lines to write.
        encoding: Character encoding.
        mode: File permissions.
    """
    content = "".join(line if line.endswith("\n") else line + "\n" for line in lines)
    atomic_write_text(path, content, encoding=encoding, mode=mode)
