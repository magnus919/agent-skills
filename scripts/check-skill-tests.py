#!/usr/bin/env python3
"""Run and guard skill-local shell test scripts.

This script is the single source of truth for skill-local shell tests. The
registry below lists every shell test shipped by a skill; entries in
``RUN_TESTS`` are executed in CI, entries in ``MANUAL_TESTS`` are documented
only (they need network access, credentials, external tooling, or
third-party libraries that CI does not install).

``python3 scripts/check-skill-tests.py --run`` executes every ``run`` entry
with ``bash`` and fails if any of them exits non-zero or is missing.

``python3 scripts/check-skill-tests.py`` (the default ``--check``) enforces the
coverage guardrail: every test-like file under a skill's ``scripts/``
directory must either be a pytest-discovered ``test_*.py`` file or be listed
in the registry below. Unregistered files, stale registry entries, and
inconsistent registries fail the check.
"""

import argparse
import subprocess
import sys
from collections.abc import Collection, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Skill-local shell tests executed in CI, as (path, extra args) pairs.
RUN_TESTS: list[tuple[str, list[str]]] = [
    ("restic/scripts/test-restic-preflight.sh", []),
    ("restic/scripts/test-restic-verify.sh", []),
    ("kubernetes/scripts/test-k8s-cli.sh", []),
    ("lastfm/scripts/test-lastfm.sh", []),
    ("data-scientist/scripts/test_campaign_protocol.sh", []),
    ("data-scientist/scripts/test_references_completeness.sh", []),
    ("data-scientist/scripts/test_detect_compute.sh", ["--local"]),
    ("brand-designer/scripts/brand-book_test.sh", []),
    ("flaresolverr/scripts/test-flaresolverr.sh", []),
    # Requires EbookLib (AGPL) and beautifulsoup4 (installed test-only in CI
    # before this script runs); epub-edit/epub-convert additionally require
    # epublib (Python 3.13+) and are skipped, and surfaced as skips, on the
    # Python 3.12 CI runner.
    ("epub/scripts/test_epub_skill.sh", []),
]

# Skill-local shell tests documented but not executed in CI; they need
# network access, credentials, or external tooling.
MANUAL_TESTS: list[str] = [
    "data-scientist/scripts/test_supervision_protocol.sh",
    "tailscale/scripts/test-all.sh",
    "tailscale/skills/headscale-derp/scripts/test-derp-latency.sh",
]


def _file_name(path: str) -> str:
    """Return the basename of a POSIX-style relative path."""
    return path.rsplit("/", 1)[-1]


def is_test_like(path: str) -> bool:
    """True when a skill script file follows a test-file naming convention."""
    name = _file_name(path)
    stem = Path(name).stem
    return (
        stem.startswith("test")
        or stem.endswith("_test")
        or stem.endswith("-test")
        or Path(name).suffix == ".bats"
    )


def is_python_test(path: str) -> bool:
    """True for a pytest-discovered ``scripts/test_*.py`` file."""
    name = _file_name(path)
    return name.startswith("test_") and name.endswith(".py")


def is_shell_script_path(path: str) -> bool:
    """True when a registry entry names a shell script, never a ``test_*.py``."""
    return path.endswith((".sh", ".bash", ".bats")) and not is_python_test(path)


def is_malformed_path(path: str) -> bool:
    """True when a registry path is not a clean relative skill script path."""
    if not path or path.startswith("/") or "\\" in path:
        return True
    if ".." in Path(path).parts:
        return True
    return "/scripts/" not in f"/{path}"


def all_registered_paths() -> list[str]:
    """Return every run and manual registry path."""
    return [path for path, _ in RUN_TESTS] + list(MANUAL_TESTS)


def registry_consistency_errors(registered: Sequence[str]) -> list[str]:
    """Report duplicate, malformed, and non-shell registry entries."""
    errors: list[str] = []
    seen: set[str] = set()
    for path in registered:
        if path in seen:
            errors.append(f"duplicate registry entry: {path}")
        seen.add(path)
        if is_malformed_path(path):
            errors.append(f"malformed registry path: {path}")
        elif not is_shell_script_path(path):
            errors.append(f"registry entry is not a shell test script: {path}")
    return errors


def stale_registry_paths(registered: Sequence[str], known_files: Collection[str]) -> list[str]:
    """Report registry paths that are no longer tracked or present."""
    known = set(known_files)
    return [path for path in registered if path not in known]


def uncovered_tests(tracked: Sequence[str], registered: Collection[str]) -> list[str]:
    """Report test-like files that are neither pytest tests nor registered."""
    known = set(registered)
    uncovered: list[str] = []
    for path in tracked:
        if not is_test_like(path):
            continue
        if is_python_test(path):
            continue
        if path not in known:
            uncovered.append(path)
    return sorted(uncovered)


def _uncovered_message(uncovered: Sequence[str]) -> str:
    listing = "\n".join(f"  - {path}" for path in uncovered)
    return (
        "Uncovered skill test files:\n"
        f"{listing}\n"
        "Fix by renaming to scripts/test_*.py (Python) or registering the shell "
        "test in scripts/check-skill-tests.py."
    )


def check_files(tracked: Sequence[str], known_files: Collection[str]) -> list[str]:
    """Return every guardrail error for the given skill script files."""
    registered = all_registered_paths()
    errors: list[str] = []
    errors.extend(registry_consistency_errors(registered))
    errors.extend(stale_registry_paths(registered, known_files))
    uncovered = uncovered_tests(tracked, registered)
    if uncovered:
        errors.append(_uncovered_message(uncovered))
    return errors


def _git_ls_files(args: Sequence[str]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [name for name in result.stdout.decode("utf-8").split("\0") if name]


def skill_script_files() -> list[str]:
    """List tracked and untracked skill script files, excluding root ``scripts/``."""
    files = _git_ls_files([]) + _git_ls_files(["--others", "--exclude-standard"])
    return [name for name in files if "/scripts/" in name and not name.startswith("scripts/")]


def check_tests() -> int:
    """Run the coverage guardrail; return a process exit code."""
    known_files = skill_script_files()
    errors = check_files(known_files, known_files)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print("skill test coverage check failed.", file=sys.stderr)
        return 1
    print("skill test coverage check passed.")
    return 0


def run_tests() -> int:
    """Run every registered ``run`` shell test; return a process exit code."""
    consistency_errors = registry_consistency_errors(all_registered_paths())
    if consistency_errors:
        for error in consistency_errors:
            print(error, file=sys.stderr)
        print("skill test registry is inconsistent; refusing to run.", file=sys.stderr)
        return 1

    failures: list[str] = []
    for path, args in RUN_TESTS:
        if not (ROOT / path).is_file():
            failures.append(f"missing script: {path}")
            continue
        print(f"=== {path} ===")
        result = subprocess.run(
            ["bash", path, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0:
            failures.append(f"{path} exited with code {result.returncode}")

    print(f"\n{len(RUN_TESTS)} skill-local shell test suites run, {len(failures)} failed.")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("All skill-local shell tests passed.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run and guard skill-local shell test scripts. With no arguments, "
            "the coverage guardrail check runs."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run", action="store_true", help="Run registered shell tests in CI.")
    mode.add_argument(
        "--check",
        action="store_true",
        help="Fail on unregistered, stale, or inconsistent skill test registry entries.",
    )
    args = parser.parse_args(argv)
    if args.run:
        return run_tests()
    return check_tests()


if __name__ == "__main__":
    sys.exit(main())
