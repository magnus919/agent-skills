"""Tests for bmad/scripts/check-spec.py.

The module under test is loaded by path (importlib) rather than imported by name,
matching the repository's pattern for skill-local script tests.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).with_name("check-spec.py")
_spec = importlib.util.spec_from_file_location("check_spec", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
check_spec = importlib.util.module_from_spec(_spec)
sys.modules["check_spec"] = check_spec
_spec.loader.exec_module(check_spec)

VALID_SPEC = """\
---
status: ready-for-dev
slug: example
owner: human
created: 2026-08-23
---

# Example Change

## Why

The outcome and why it matters.

## Capabilities

- The system can do the thing.

## Constraints

- Technical boundary.

## Non-goals

- Out of scope.

## Success signal

- Observable criterion.

## Verification

- Tests:
"""

def test_valid_spec_passes(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(VALID_SPEC, encoding="utf-8")
    assert check_spec.main([str(spec)]) == 0

def test_missing_section_fails(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        VALID_SPEC.replace("## Non-goals", "## Deferred"),
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 1

def test_invalid_status_fails(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        VALID_SPEC.replace("status: ready-for-dev", "status: maybe"),
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 1

def test_missing_frontmatter_status_warns_but_passes(tmp_path) -> None:
    spec = tmp_path / "INTENT.md"
    spec.write_text(
        VALID_SPEC.replace("status: ready-for-dev\n", ""),
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 0

def test_unreadable_file_fails(tmp_path) -> None:
    assert check_spec.main([str(tmp_path / "missing.md")]) == 1

def test_json_output_is_machine_readable(tmp_path, capsys) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(VALID_SPEC, encoding="utf-8")
    check_spec.main(["--json", str(spec)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["valid"] is True
    assert payload["files"][0]["path"] == str(spec)

def test_multiple_files_reported(tmp_path, capsys) -> None:
    good = tmp_path / "good.md"
    good.write_text(VALID_SPEC, encoding="utf-8")
    bad = tmp_path / "bad.md"
    bad.write_text("# Only a title\n", encoding="utf-8")
    assert check_spec.main([str(good), str(bad)]) == 1
    captured = capsys.readouterr()
    assert "1/2 spec(s) valid" in captured.out

def test_frontmatter_parser_handles_quoted_values() -> None:
    fields = check_spec.extract_frontmatter("---\nstatus: 'done'\nslug: \"x\"\n---\n# t\n")
    assert fields == {"status": "done", "slug": "x"}

def test_status_vocabulary_contains_resumable_states() -> None:
    assert "blocked" in check_spec.STATUS_VOCABULARY
    assert "ready-for-dev" in check_spec.STATUS_VOCABULARY

def test_section_present_is_case_insensitive() -> None:
    headings = check_spec.collect_headings("## why\n### Capabilities\n#### non-goals\n")
    assert check_spec.section_present(headings, "Why")
    assert check_spec.section_present(headings, "Non-goals")
    assert not check_spec.section_present(headings, "Constraints")

@pytest.mark.parametrize("status", check_spec.STATUS_VOCABULARY)
def test_every_vocabulary_status_is_accepted(tmp_path, status: str) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        VALID_SPEC.replace("status: ready-for-dev", f"status: {status}"),
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 0

def test_heading_inside_fence_does_not_count(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    body = VALID_SPEC.replace(
        "## Constraints\n\n- Technical boundary.\n",
        "```markdown\n## Constraints\n```\n",
    )
    spec.write_text(body, encoding="utf-8")
    assert check_spec.main([str(spec)]) == 1

def test_non_utf8_file_fails_gracefully(tmp_path, capsys) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_bytes(VALID_SPEC.encode("utf-8") + b"\xff")
    assert check_spec.main([str(spec)]) == 1
    captured = capsys.readouterr()
    assert "FAIL" in captured.out

def test_utf8_bom_does_not_disable_status_check(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_bytes(b"\xef\xbb\xbf" + VALID_SPEC.replace("status: ready-for-dev", "status: maybe").encode("utf-8"))
    assert check_spec.main([str(spec)]) == 1

def test_inline_yaml_comment_in_status_is_accepted(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        VALID_SPEC.replace("status: ready-for-dev", "status: ready-for-dev  # pending owner review"),
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 0

def test_delimiter_trailing_whitespace_does_not_disable_status_check(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    body = VALID_SPEC.replace(
        "status: ready-for-dev",
        "status: maybe",
    )
    body = body.replace("---\n", "--- \n").replace("\n---\n# Example Change", "\n---\t\n# Example Change")
    spec.write_text(body, encoding="utf-8")
    assert check_spec.main([str(spec)]) == 1

def test_quoted_status_with_inline_comment_is_accepted(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        VALID_SPEC.replace(
            "status: ready-for-dev",
            'status: "draft"  # pending owner review',
        ),
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 0

def test_leading_blank_line_does_not_disable_status_check(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        "\n\n" + VALID_SPEC.replace("status: ready-for-dev", "status: maybe"),
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 1

def test_indented_closing_delimiter_does_not_disable_status_check(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    body = VALID_SPEC.replace("status: ready-for-dev", "status: maybe").replace(
        "\n---\n\n# Example Change", "\n ---\n\n# Example Change"
    )
    spec.write_text(body, encoding="utf-8")
    assert check_spec.main([str(spec)]) == 1

def test_mismatched_fence_marker_does_not_close_code_block(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    body = VALID_SPEC.replace("## Constraints", "## Deferred").replace(
        "## Capabilities",
        "## Capabilities\n\n```\nsome code\n~~~\n## Constraints (inside code block)\n```",
        1,
    )
    spec.write_text(body, encoding="utf-8")
    assert check_spec.main([str(spec)]) == 1

def test_unclosed_frontmatter_fails_closed(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    body = VALID_SPEC.replace("\n---\n\n# Example Change", "\n\n# Example Change")
    spec.write_text(body, encoding="utf-8")
    assert check_spec.main([str(spec)]) == 1

def test_malformed_long_dash_opener_fails_closed(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    body = VALID_SPEC.replace("---\n", "----\n", 1)
    spec.write_text(body, encoding="utf-8")
    assert check_spec.main([str(spec)]) == 1


def test_empty_well_formed_frontmatter_is_accepted(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        "---\n---\n\n" + VALID_SPEC.split("\n\n", 1)[1],
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 0


def test_closing_delimiter_without_trailing_newline_is_accepted(tmp_path) -> None:
    spec = tmp_path / "SPEC.md"
    spec.write_text(
        VALID_SPEC.rstrip("\n") + "\n",
        encoding="utf-8",
    )
    assert check_spec.main([str(spec)]) == 0
