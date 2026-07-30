"""Cache management for project analysis data.

Provides atomic cache read/write operations using the atomic write utility.
Cached data is stored in the project's cache/ directory as JSON files.

Key guarantees:
- All cache writes use atomic_write_json (tempfile + os.rename).
- Cache cleanup (clean command) removes all cache files atomically.
- Cache keys are validated to prevent path traversal.
"""

from __future__ import annotations

import contextlib
import json
import os
from typing import Any

from binary_analysis.projects.atomic import atomic_write_json

# Cache subdirectory within a project workspace
CACHE_DIRNAME = "cache"

# Valid characters for cache keys (alphanumeric, underscore, hyphen, dot)
_VALID_KEY_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")


def _validate_cache_key(key: str) -> str:
    """Validate a cache key to prevent path traversal and invalid chars.

    Args:
        key: The cache key to validate.

    Returns:
        The validated key (unchanged if valid).

    Raises:
        ValueError: If the key is invalid.
    """
    if not key or not key.strip():
        raise ValueError("Cache key must not be empty")

    key = key.strip()

    if "\x00" in key:
        raise ValueError("Cache key must not contain null bytes")

    if "/" in key or "\\" in key:
        raise ValueError("Cache key must not contain path separators")

    if key.startswith("."):
        raise ValueError("Cache key must not start with a dot")

    invalid_chars = [c for c in key if c not in _VALID_KEY_CHARS]
    if invalid_chars:
        raise ValueError(f"Cache key contains invalid characters: {''.join(invalid_chars)}")

    if not key.endswith(".json"):
        key = key + ".json"

    return key


def _cache_path(project_path: str, key: str) -> str:
    """Resolve the full path for a cache entry.

    Args:
        project_path: Absolute path to the project workspace directory.
        key: Validated cache key.

    Returns:
        Full path to the cache file.
    """
    return os.path.join(project_path, CACHE_DIRNAME, key)


def cache_get(project_path: str, key: str) -> Any:
    """Retrieve a cached value.

    Args:
        project_path: Absolute path to the project workspace directory.
        key: Cache key (must be a safe filename).

    Returns:
        The cached data, or None if the key doesn't exist or is corrupted.

    Raises:
        ValueError: If the cache key is invalid.
    """
    key = _validate_cache_key(key)
    cache_file = _cache_path(project_path, key)

    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted cache entry — return None so caller can regenerate
        return None


def cache_set(project_path: str, key: str, value: Any) -> None:
    """Atomically store a value in the cache.

    Uses atomic_write_json to ensure cache entries are never partially
    written. Invalid or non-serializable values raise before any file is
    touched.

    Args:
        project_path: Absolute path to the project workspace directory.
        key: Cache key (must be a safe filename).
        value: JSON-serializable value to cache.

    Raises:
        ValueError: If the cache key is invalid.
        TypeError: If the value is not JSON-serializable.
    """
    key = _validate_cache_key(key)
    cache_file = _cache_path(project_path, key)

    # Ensure cache directory exists
    cache_dir = os.path.dirname(cache_file)
    os.makedirs(cache_dir, exist_ok=True)

    # Serialize via JSON round-trip to validate types
    json_str = json.dumps(value, ensure_ascii=False)

    # Atomic write
    atomic_write_json(cache_file, json.loads(json_str))


def cache_delete(project_path: str, key: str) -> bool:
    """Delete a cached entry.

    Args:
        project_path: Absolute path to the project workspace directory.
        key: Cache key.

    Returns:
        True if the entry was deleted, False if it didn't exist.

    Raises:
        ValueError: If the cache key is invalid.
    """
    key = _validate_cache_key(key)
    cache_file = _cache_path(project_path, key)

    if not os.path.exists(cache_file):
        return False

    try:
        os.unlink(cache_file)
    except OSError:
        return False
    return True


def cache_clear(project_path: str) -> int:
    """Remove all cached entries for a project.

    Deletes all files in the cache/ directory but does not remove
    the directory itself. Uses shutil.rmtree for efficiency, or
    individual deletes if that fails.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        Number of cache entries removed.
    """
    import shutil

    cache_dir = os.path.join(project_path, CACHE_DIRNAME)

    if not os.path.exists(cache_dir):
        return 0

    count = 0
    try:
        # Count entries before clearing
        entries = [e for e in os.listdir(cache_dir) if os.path.isfile(os.path.join(cache_dir, e))]
        count = len(entries)
    except OSError:
        pass

    # Remove all files and recreate empty directory
    try:
        shutil.rmtree(cache_dir)
    except OSError:
        # Fall back to individual deletes
        for entry in os.listdir(cache_dir):
            with contextlib.suppress(OSError):
                os.unlink(os.path.join(cache_dir, entry))
        return count

    os.makedirs(cache_dir, exist_ok=True)
    return count


def cache_list(project_path: str) -> list[str]:
    """List all cached keys for a project.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        Sorted list of cache keys (without .json extension).
    """
    cache_dir = os.path.join(project_path, CACHE_DIRNAME)

    if not os.path.exists(cache_dir):
        return []

    keys: list[str] = []
    try:
        for entry in os.listdir(cache_dir):
            if entry.endswith(".json") and os.path.isfile(os.path.join(cache_dir, entry)):
                keys.append(entry[:-5])  # Remove .json
    except OSError:
        pass

    return sorted(keys)
