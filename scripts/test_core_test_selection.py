#!/usr/bin/env python3
"""Ensure local and CI core test selections use the shared manifest."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "core-test-files.txt"
MAKEFILE = ROOT / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
FILTER = "sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d'"


def manifest_entries() -> list[str]:
    return [
        line.strip()
        for line in MANIFEST.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_core_manifest_is_nonempty_and_files_exist() -> None:
    entries = manifest_entries()
    assert entries
    assert all((ROOT / entry).is_file() or (ROOT / entry).is_dir() for entry in entries)
    assert len(entries) == len(set(entries))


def test_makefile_consumes_shared_core_manifest() -> None:
    makefile = MAKEFILE.read_text()
    assert "core-test-files.txt" in makefile
    assert "$(CORE_TESTS)" in makefile


def test_makefile_filters_comments_and_blank_lines_like_ci() -> None:
    makefile = MAKEFILE.read_text()
    # Make doubles the dollar sign so the shell receives the same expression as CI.
    assert "grep -Ev '^[[:space:]]*\\#|^[[:space:]]*$$'" in makefile


def test_make_and_ci_filtering_semantics_match() -> None:
    sample = "# comment\n  # indented comment\n\n  scripts/example.py  \n\t\n"
    expected = ["scripts/example.py"]
    filtered = subprocess.run(
        ["sed", "-e", "/^[[:space:]]*#/d", "-e", "/^[[:space:]]*$/d"],
        input=sample,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    assert [line.strip() for line in filtered] == expected
    assert FILTER in WORKFLOW.read_text()


def test_required_ci_consumes_shared_core_manifest() -> None:
    workflow = WORKFLOW.read_text()
    assert "core-test-files.txt" in workflow
    assert "mapfile -t core_tests" in workflow
    assert '"${core_tests[@]}"' in workflow


def test_manifest_contains_required_validation_modules() -> None:
    assert set(manifest_entries()) >= {
        "scripts/test-eval-validation.py",
        "scripts/test-eval-coverage.py",
        "scripts/test_check_skill_tests.py",
        "scripts/test_core_test_selection.py",
        "eval_runner/tests/",
    }
