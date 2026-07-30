"""Tests for the cache management module (projects/cache.py).

Validates that:
- Cache set/get roundtrip preserves data.
- Cache write is atomic (valid JSON after any write).
- Cache get for nonexistent key returns None.
- Cache get for corrupted file returns None (graceful degradation).
- Cache delete removes entries.
- Cache clear removes all entries.
- Cache list returns correct keys.
- Cache key validation rejects unsafe keys.
- Cache keys are validated to prevent path traversal.
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import json
import os
from pathlib import Path

import pytest
from binary_analysis.projects.cache import (
    cache_clear,
    cache_delete,
    cache_get,
    cache_list,
    cache_set,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def project_cache_dir(tmp_path: Path) -> str:
    """Fixture: a temp project workspace with cache/ directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True)
    return str(tmp_path)


# ---------------------------------------------------------------------------
# Cache set/get
# ---------------------------------------------------------------------------


class TestCacheSetGet:
    """Tests for cache_set and cache_get."""

    def test_set_and_get_simple(self, project_cache_dir: str) -> None:
        """Setting and getting a simple value roundtrips."""
        cache_set(project_cache_dir, "test-key", {"value": 42})
        result = cache_get(project_cache_dir, "test-key")
        assert result == {"value": 42}

    def test_get_nonexistent_key(self, project_cache_dir: str) -> None:
        """Getting a key that doesn't exist returns None."""
        result = cache_get(project_cache_dir, "nonexistent")
        assert result is None

    def test_set_overwrites_existing(self, project_cache_dir: str) -> None:
        """Setting a key twice overwrites with the new value."""
        cache_set(project_cache_dir, "my-key", {"v": 1})
        cache_set(project_cache_dir, "my-key", {"v": 2})
        result = cache_get(project_cache_dir, "my-key")
        assert result == {"v": 2}

    def test_nested_data(self, project_cache_dir: str) -> None:
        """Nested dicts and lists survive roundtrip."""
        data = {
            "sections": [
                {"name": ".text", "size": 1024},
                {"name": ".data", "size": 512},
            ],
            "functions": ["main", "foo", "bar"],
            "metadata": {"arch": "x86", "bits": 64},
        }
        cache_set(project_cache_dir, "analysis", data)
        result = cache_get(project_cache_dir, "analysis")
        assert result == data

    def test_cache_file_is_valid_json(self, project_cache_dir: str) -> None:
        """The cache file is valid standalone JSON."""
        cache_set(project_cache_dir, "data", {"key": "value"})
        cache_file = os.path.join(project_cache_dir, "cache", "data.json")
        with open(cache_file) as f:
            parsed = json.load(f)
        assert parsed == {"key": "value"}

    def test_auto_adds_json_extension(self, project_cache_dir: str) -> None:
        """Keys without .json get it appended automatically."""
        cache_set(project_cache_dir, "results", [1, 2, 3])
        cache_file = os.path.join(project_cache_dir, "cache", "results.json")
        assert os.path.exists(cache_file)

    def test_corrupted_cache_returns_none(self, project_cache_dir: str) -> None:
        """Getting a corrupted cache file returns None (graceful degradation)."""
        cache_file = os.path.join(project_cache_dir, "cache", "bad.json")
        with open(cache_file, "w") as f:
            f.write("{this is not valid json")
        result = cache_get(project_cache_dir, "bad")
        assert result is None


# ---------------------------------------------------------------------------
# Cache delete
# ---------------------------------------------------------------------------


class TestCacheDelete:
    """Tests for cache_delete."""

    def test_delete_existing(self, project_cache_dir: str) -> None:
        """Deleting an existing cache entry removes it."""
        cache_set(project_cache_dir, "temp", [1, 2])
        assert cache_get(project_cache_dir, "temp") is not None
        result = cache_delete(project_cache_dir, "temp")
        assert result is True
        assert cache_get(project_cache_dir, "temp") is None

    def test_delete_nonexistent(self, project_cache_dir: str) -> None:
        """Deleting a nonexistent key returns False."""
        result = cache_delete(project_cache_dir, "nonexistent")
        assert result is False


# ---------------------------------------------------------------------------
# Cache clear
# ---------------------------------------------------------------------------


class TestCacheClear:
    """Tests for cache_clear."""

    def test_clear_removes_all(self, project_cache_dir: str) -> None:
        """Clearing the cache removes all entries."""
        for i in range(5):
            cache_set(project_cache_dir, f"key-{i}", i)
        assert cache_list(project_cache_dir) == ["key-0", "key-1", "key-2", "key-3", "key-4"]
        count = cache_clear(project_cache_dir)
        assert count == 5
        assert cache_list(project_cache_dir) == []

    def test_clear_empty_cache(self, project_cache_dir: str) -> None:
        """Clearing an empty cache returns 0."""
        count = cache_clear(project_cache_dir)
        assert count == 0

    def test_clear_returns_count(self, project_cache_dir: str) -> None:
        """cache_clear returns the number of removed entries."""
        cache_set(project_cache_dir, "a", 1)
        cache_set(project_cache_dir, "b", 2)
        cache_set(project_cache_dir, "c", 3)
        count = cache_clear(project_cache_dir)
        assert count == 3


# ---------------------------------------------------------------------------
# Cache list
# ---------------------------------------------------------------------------


class TestCacheList:
    """Tests for cache_list."""

    def test_empty_cache_list(self, project_cache_dir: str) -> None:
        """Listing an empty cache returns empty list."""
        assert cache_list(project_cache_dir) == []

    def test_lists_keys_sorted(self, project_cache_dir: str) -> None:
        """Listing returns sorted keys without .json extension."""
        cache_set(project_cache_dir, "zzz", 3)
        cache_set(project_cache_dir, "aaa", 1)
        cache_set(project_cache_dir, "mmm", 2)
        assert cache_list(project_cache_dir) == ["aaa", "mmm", "zzz"]

    def test_skips_non_files(self, project_cache_dir: str) -> None:
        """Only .json files are listed; directories and other files are skipped."""
        cache_set(project_cache_dir, "good", 1)
        # Create a subdirectory
        (Path(project_cache_dir) / "cache" / "subdir").mkdir(exist_ok=True)
        # Create a non-json file
        (Path(project_cache_dir) / "cache" / "readme.txt").write_text("hello")
        keys = cache_list(project_cache_dir)
        assert keys == ["good"]


# ---------------------------------------------------------------------------
# Cache key validation
# ---------------------------------------------------------------------------


class TestCacheKeyValidation:
    """Tests for cache key validation in cache_set/cache_get."""

    def test_valid_keys(self, project_cache_dir: str) -> None:
        """Various valid cache keys work."""
        valid_keys = [
            "analysis-results",
            "metadata_v2",
            "sections.123",
            "a",
            "functions-list",
        ]
        for key in valid_keys:
            cache_set(project_cache_dir, key, {"test": True})
            assert cache_get(project_cache_dir, key) == {"test": True}

    def test_empty_key_raises(self, project_cache_dir: str) -> None:
        """Empty cache keys are rejected."""
        with pytest.raises(ValueError, match="must not be empty"):
            cache_set(project_cache_dir, "", {"data": 1})

    def test_null_byte_key_raises(self, project_cache_dir: str) -> None:
        """Null bytes in cache keys are rejected."""
        with pytest.raises(ValueError, match="null bytes"):
            cache_set(project_cache_dir, "bad\x00key", {"data": 1})

    def test_path_separator_key_raises(self, project_cache_dir: str) -> None:
        """Path separators in cache keys are rejected."""
        for sep in ["/", "\\"]:
            with pytest.raises(ValueError, match="path separators"):
                cache_set(project_cache_dir, f"evil{sep}key", {"data": 1})

    def test_dot_prefix_key_raises(self, project_cache_dir: str) -> None:
        """Dot-prefixed cache keys are rejected."""
        with pytest.raises(ValueError, match="start with a dot"):
            cache_set(project_cache_dir, ".hidden", {"data": 1})

    def test_special_char_key_raises(self, project_cache_dir: str) -> None:
        """Special characters in cache keys are rejected."""
        with pytest.raises(ValueError, match="invalid characters"):
            cache_set(project_cache_dir, "my key", {"data": 1})


# ---------------------------------------------------------------------------
# Atomic cache writes
# ---------------------------------------------------------------------------


class TestAtomicCacheWrites:
    """Tests verifying atomic write properties for cache."""

    def test_no_temp_files_left_behind(self, project_cache_dir: str) -> None:
        """After cache_set, no .tmp files remain."""
        cache_set(project_cache_dir, "data", {"hello": "world"})
        cache_path = Path(project_cache_dir) / "cache"
        tmp_files = list(cache_path.glob("*.tmp"))
        assert len(tmp_files) == 0

    def test_cache_file_is_complete_json(self, project_cache_dir: str) -> None:
        """Cache file is always complete, valid JSON."""
        data = {
            "items": list(range(100)),
            "metadata": {"format": "PE", "arch": "x86_64"},
        }
        cache_set(project_cache_dir, "bulk", data)
        result = cache_get(project_cache_dir, "bulk")
        assert result == data
