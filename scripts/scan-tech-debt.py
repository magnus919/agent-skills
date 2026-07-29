#!/usr/bin/env python3
"""Scan for TODO, FIXME, HACK, and XXX markers in tracked source files.

Reports technical debt markers with file, line, and surrounding context.
Used in CI to prevent unlinked tech debt from accumulating.
"""

import subprocess
import sys
from pathlib import Path

MARKERS = ("TODO", "FIXME", "HACK", "XXX")
EXCLUDE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache",
                ".pytest_cache", ".ruff_cache", "dist", "build", "logs", ".hermes"}
EXCLUDE_PATTERNS = {"*.pyc", "*.pyo", "*.egg-info", "*.whl", "*.min.js", "*.min.css"}


def is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    return any(path.match(pat) for pat in EXCLUDE_PATTERNS)


def scan_file(filepath: Path) -> list[tuple[int, str, str]]:
    """Return list of (line_number, marker, context) for marker occurrences."""
    findings: list[tuple[int, str, str]] = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            for marker in MARKERS:
                if marker in stripped:
                    # Extract the comment content after the marker
                    idx = stripped.index(marker)
                    context = stripped[idx:].rstrip()
                    findings.append((lineno, marker, context))
                    break
    return findings


def main() -> int:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard",
             "*.py", "*.rb", "*.sh", "*.js", "*.ts", "*.yml", "*.yaml", "*.toml", "*.md"],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        print("ERROR: Failed to list tracked files.", file=sys.stderr)
        return 1

    total = 0
    for relpath in result.stdout.strip().splitlines():
        if not relpath:
            continue
        filepath = Path(relpath)
        if is_excluded(filepath):
            continue
        findings = scan_file(filepath)
        for lineno, marker, context in findings:
            if total == 0:
                print("\nTechnical debt markers found:\n")
            print(f"  {filepath}:{lineno}  [{marker}] {context}")
            total += 1

    if total > 0:
        print(f"\n{total} technical debt marker(s) found.")
        print("Consider linking each marker to an issue (e.g., TODO(#123)).")
        return 0

    print("No technical debt markers found in tracked source files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
