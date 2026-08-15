#!/usr/bin/env python3
"""Tests for scripts/check-skill-tests.py."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent

# The script under test is hyphenated (check-skill-tests.py), so load it via
# importlib rather than a normal import, matching scripts/test-eval-coverage.py.
_spec = importlib.util.spec_from_file_location(
    "check_skill_tests", SCRIPT_DIR / "check-skill-tests.py"
)
assert _spec is not None
assert _spec.loader is not None
check_skill_tests: Any = importlib.util.module_from_spec(_spec)
sys.modules["check_skill_tests"] = check_skill_tests
_spec.loader.exec_module(check_skill_tests)


def test_test_like_detection() -> None:
    assert check_skill_tests.is_test_like("foo/scripts/test-foo.sh")
    assert check_skill_tests.is_test_like("foo/scripts/test_thing.sh")
    assert check_skill_tests.is_test_like("foo/scripts/foo_test.py")
    assert check_skill_tests.is_test_like("foo/scripts/foo-test.bash")
    assert check_skill_tests.is_test_like("foo/scripts/foo.bats")
    assert check_skill_tests.is_test_like("foo/scripts/test-foo.sh.orig")
    assert not check_skill_tests.is_test_like("foo/scripts/check-ac-testability.py")
    assert not check_skill_tests.is_test_like("foo/scripts/run-tool.py")
    assert not check_skill_tests.is_test_like("foo/scripts/README.md")


def test_python_test_detection() -> None:
    assert check_skill_tests.is_python_test("foo/scripts/test_foo.py")
    assert not check_skill_tests.is_python_test("foo/scripts/test-foo.sh")
    assert not check_skill_tests.is_python_test("foo/scripts/foo_test.py")
    assert not check_skill_tests.is_python_test("foo/scripts/helper.py")


def test_shell_script_path_detection() -> None:
    assert check_skill_tests.is_shell_script_path("foo/scripts/test-foo.sh")
    assert check_skill_tests.is_shell_script_path("foo/scripts/run.bash")
    assert check_skill_tests.is_shell_script_path("foo/scripts/test-foo.bats")
    assert not check_skill_tests.is_shell_script_path("foo/scripts/test_foo.py")
    assert not check_skill_tests.is_shell_script_path("foo/scripts/foo_test.py")
    assert not check_skill_tests.is_shell_script_path("foo/scripts/run.py")


def test_malformed_path_detection() -> None:
    assert check_skill_tests.is_malformed_path("")
    assert check_skill_tests.is_malformed_path("/abs/path/test.sh")
    assert check_skill_tests.is_malformed_path("foo/../scripts/test.sh")
    assert check_skill_tests.is_malformed_path("foo/scripts\\test.sh")
    assert check_skill_tests.is_malformed_path("foo/test.sh")
    assert not check_skill_tests.is_malformed_path("foo/scripts/test.sh")
    assert not check_skill_tests.is_malformed_path("restic/scripts/test-restic-preflight.sh")


def test_covered_vs_uncovered_classification() -> None:
    registered = ["restic/scripts/test-restic-preflight.sh"]
    tracked = [
        "restic/scripts/test-restic-preflight.sh",  # registered -> covered
        "ai-governance/scripts/test_governance_maturity.py",  # python test -> covered
        "foo/scripts/test-foo.sh",  # unregistered shell -> uncovered
        "foo/scripts/foo_test.py",  # test-like python, not test_*.py -> uncovered
        "foo/scripts/foo.bats",  # unregistered bats -> uncovered
        "foo/scripts/run-tool.py",  # not test-like -> ignored
    ]
    uncovered = check_skill_tests.uncovered_tests(tracked, registered)
    assert set(uncovered) == {
        "foo/scripts/foo.bats",
        "foo/scripts/foo_test.py",
        "foo/scripts/test-foo.sh",
    }


def test_registry_consistency_duplicate() -> None:
    errors = check_skill_tests.registry_consistency_errors(
        [
            "restic/scripts/test-restic-preflight.sh",
            "restic/scripts/test-restic-preflight.sh",
        ]
    )
    assert any("duplicate registry entry" in error for error in errors)


def test_registry_consistency_python_test_rejected() -> None:
    errors = check_skill_tests.registry_consistency_errors(["foo/scripts/test_foo.py"])
    assert any("not a shell test script" in error for error in errors)


def test_registry_consistency_malformed_path_rejected() -> None:
    errors = check_skill_tests.registry_consistency_errors(["../scripts/test.sh"])
    assert any("malformed registry path" in error for error in errors)


def test_registry_consistency_clean_registry_passes() -> None:
    errors = check_skill_tests.registry_consistency_errors(check_skill_tests.all_registered_paths())
    assert errors == []


def test_stale_registry_paths() -> None:
    stale = check_skill_tests.stale_registry_paths(
        [
            "restic/scripts/test-restic-preflight.sh",
            "epub/scripts/test_epub_skill.sh",
        ],
        {"epub/scripts/test_epub_skill.sh"},
    )
    assert stale == ["restic/scripts/test-restic-preflight.sh"]


def test_check_flags_unregistered_fixture(tmp_path: Path) -> None:
    script_dir = tmp_path / "zzz-tmp-skill" / "scripts"
    script_dir.mkdir(parents=True)
    (script_dir / "test_unregistered.sh").write_text("#!/bin/sh\nset -e\nexit 0\n")
    tracked = ["zzz-tmp-skill/scripts/test_unregistered.sh"]
    errors = check_skill_tests.check_files(tracked, set(tracked))
    assert any("test_unregistered.sh" in error for error in errors)
    assert any("check-skill-tests.py" in error for error in errors)


def test_check_clean_when_registry_complete() -> None:
    registered = set(check_skill_tests.all_registered_paths())
    assert check_skill_tests.check_files([], registered) == []


def test_run_registry_paths_exist() -> None:
    missing = [path for path, _ in check_skill_tests.RUN_TESTS if not (ROOT / path).is_file()]
    assert missing == []


def test_manual_registry_paths_exist() -> None:
    missing = [path for path in check_skill_tests.MANUAL_TESTS if not (ROOT / path).is_file()]
    assert missing == []


def test_registry_has_no_duplicate_paths() -> None:
    paths = check_skill_tests.all_registered_paths()
    assert len(paths) == len(set(paths))


def test_repository_has_no_uncovered_skill_tests() -> None:
    known = check_skill_tests.skill_script_files()
    errors = check_skill_tests.check_files(known, set(known))
    assert errors == []
