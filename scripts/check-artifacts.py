#!/usr/bin/env python3
"""Validate runnable repository artifacts selected from the Git index."""

import argparse
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / name for name in result.stdout.decode().split("\0") if name]


def is_shell_script(path: Path) -> bool:
    if path.suffix in {".sh", ".bash"}:
        return True
    try:
        first_line = path.open("rb").readline().decode("utf-8", "replace")
    except OSError:
        return False
    return first_line.startswith("#!") and any(
        shell in first_line for shell in ("/sh", "/bash", "env sh", "env bash")
    )


def test_directories(files: list[Path]) -> list[Path]:
    directories = set()
    for path in files:
        for parent in path.parents:
            if parent.name == "tests":
                directories.add(parent)
                break
            if parent == ROOT:
                break
    return sorted(directories)


def run_checks(files: list[Path]) -> list[str]:
    errors = []
    for path in files:
        relative = path.relative_to(ROOT)
        if path.suffix == ".py":
            try:
                compile(path.read_bytes(), str(relative), "exec")
            except (OSError, SyntaxError) as error:
                errors.append(f"python {relative}: {error}")
        elif path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                errors.append(f"json {relative}: {error}")
        if is_shell_script(path):
            result = subprocess.run(
                ["bash", "-n", str(path)], cwd=ROOT, text=True, capture_output=True
            )
            if result.returncode:
                errors.append(f"bash -n {relative}: {result.stderr.strip()}")

    for directory in test_directories(files):
        relative = directory.relative_to(ROOT)
        result = unittest.TextTestRunner(verbosity=0).run(
            unittest.defaultTestLoader.discover(str(directory))
        )
        if not result.wasSuccessful():
            errors.append(
                f"unittest discover {relative}: "
                f"{len(result.failures)} failures, {len(result.errors)} errors"
            )
    return errors


def self_check() -> None:
    files = [ROOT / "example/tests/test_example.py", ROOT / "elsewhere/file.py"]
    assert test_directories(files) == [ROOT / "example/tests"]
    assert is_shell_script(ROOT / "scripts/check-artifacts.py") is False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return 0

    errors = run_checks(tracked_files())
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
