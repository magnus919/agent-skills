#!/usr/bin/env python3
"""Validate that AGENTS.md documented commands still work.

Parses AGENTS.md for code blocks containing shell commands and validates
basic structure and existence of referenced scripts/commands.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_MD = ROOT / "AGENTS.md"


def extract_code_blocks(content: str) -> list[tuple[int, str]]:
    """Extract shell code blocks with their starting line numbers."""
    blocks = []
    in_block = False
    block_lines: list[str] = []
    block_start = 0
    lang = ""

    for i, line in enumerate(content.splitlines(), 1):
        if line.strip().startswith("```") and not in_block:
            in_block = True
            block_start = i
            lang = line.strip()[3:].strip().lower()
            block_lines = []
        elif line.strip() == "```" and in_block:
            in_block = False
            if lang in ("sh", "shell", "bash", ""):
                blocks.append((block_start, "\n".join(block_lines)))
        elif in_block:
            block_lines.append(line)

    return blocks


def validate_references(blocks: list[tuple[int, str]]) -> tuple[int, int, list[str]]:
    """Check that referenced scripts and commands exist in the repo.

    Returns (pass_count, fail_count, error_messages).
    """
    errors: list[str] = []
    script_ref_pattern = re.compile(r"scripts/[\w./-]+")

    for lineno, block in blocks:
        refs = script_ref_pattern.findall(block)
        for ref in refs:
            full_path = ROOT / ref
            if not full_path.exists():
                errors.append(f"AGENTS.md:{lineno}: referenced script '{ref}' does not exist")

    # Check that AGENTS.md references requirements-dev.txt if it mentions pip install
    content = AGENTS_MD.read_text()
    if "pip install" in content and "requirements-dev.txt" not in content:
        errors.append("AGENTS.md mentions pip install but not requirements-dev.txt")

    pass_count = len(blocks) - len([e for e in errors if "does not exist" in e])
    fail_count = len([e for e in errors if "does not exist" in e])
    return pass_count, fail_count, errors


def main() -> int:
    if not AGENTS_MD.exists():
        print("AGENTS.md not found.", file=sys.stderr)
        return 1

    content = AGENTS_MD.read_text()

    # Structural checks
    issues: list[str] = []

    # Check for required sections
    required_sections = [
        ("How to Load Skills", "loading instructions"),
        ("Best Practices", "best practices"),
    ]
    for section, description in required_sections:
        if f"## {section}" not in content:
            issues.append(f"AGENTS.md missing '{section}' section ({description})")

    # Extract and validate code blocks
    blocks = extract_code_blocks(content)
    if not blocks:
        issues.append("AGENTS.md contains no shell code blocks with commands")

    _, _fail_count, ref_errors = validate_references(blocks)
    issues.extend(ref_errors)

    if issues:
        for issue in issues:
            print(f"  ERROR: {issue}", file=sys.stderr)
        print(f"\n{len(issues)} issue(s) found in AGENTS.md.", file=sys.stderr)
        return 1

    print("AGENTS.md validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
