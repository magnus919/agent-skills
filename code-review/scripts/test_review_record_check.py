"""Tests for review_record_check.py, including the shipped template."""

from __future__ import annotations

import importlib.util
import sys
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("review_record_check.py")
spec = importlib.util.spec_from_file_location("review_record_check", SCRIPT)
review_record_check = importlib.util.module_from_spec(spec)
sys.modules['review_record_check'] = review_record_check
spec.loader.exec_module(review_record_check)

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "review-record.md"

VALID_RECORD = """# Review record — retry handling

## Scope

- Base: 8f2c1ab
- Head: 33de901
- Files changed: 2 (+48/-12, 60 effective)
- Attention tier: small
- Coverage: full
- Change type: fix

## Intent

"The worker should stop dropping the final error when retries are exhausted."

## Evidence

- `pytest worker/tests -q` — 41 passed, exit 0
- Read `worker/retry.py:70-95` — the exhaustion branch returns None

## Findings

- [blocking] The exhaustion path returns None instead of the last error — evidence: `worker/retry.py:88` — verify: `test_retry_keeps_final_error` fails before the fix and passes after
- [question] Is the 3-attempt cap intentional for the batch path?

## Verdict

REQUEST CHANGES

## Residual risk

- Retry timing under jitter is untested, but behavior is unchanged by this patch.

## Not reviewed

- The scheduler caller, which is outside this diff.
"""


def test_valid_record_passes() -> None:
    result = review_record_check.check(VALID_RECORD)
    assert result.valid, result.errors
    assert result.verdict == "REQUEST CHANGES"
    assert result.counts["blocking"] == 1
    assert result.counts["question"] == 1


def test_missing_section_is_an_error() -> None:
    text = VALID_RECORD.replace("## Not reviewed\n\n- The scheduler caller, which is outside this diff.\n", "")
    result = review_record_check.check(text)
    assert not result.valid
    assert any("not reviewed" in error.lower() for error in result.errors)


def test_approval_with_open_blocking_finding_is_rejected() -> None:
    result = review_record_check.check(VALID_RECORD.replace("REQUEST CHANGES", "APPROVE"))
    assert not result.valid
    assert any("contradicts" in error for error in result.errors)


def test_blocking_finding_requires_evidence_and_verification() -> None:
    text = VALID_RECORD.replace(
        "- [blocking] The exhaustion path returns None instead of the last error — evidence: "
        "`worker/retry.py:88` — verify: `test_retry_keeps_final_error` fails before the fix and passes after",
        "- [blocking] The exhaustion path looks wrong",
    )
    result = review_record_check.check(text)
    assert not result.valid
    errors = " ".join(result.errors)
    assert "no evidence" in errors
    assert "no verify" in errors


def test_unknown_severity_label_is_rejected() -> None:
    text = VALID_RECORD.replace("[question]", "[major]")
    result = review_record_check.check(text)
    assert not result.valid
    assert any("unknown severity" in error for error in result.errors)


def test_unlabelled_finding_is_rejected() -> None:
    text = VALID_RECORD.replace("- [question] Is the 3-attempt cap", "- Is the 3-attempt cap")
    result = review_record_check.check(text)
    assert not result.valid
    assert any("without a severity label" in error for error in result.errors)


def test_placeholder_sections_do_not_count_as_content() -> None:
    text = VALID_RECORD.replace("## Residual risk\n\n- Retry timing under jitter is untested, but behavior is unchanged by this patch.", "## Residual risk\n\n- TBD")
    result = review_record_check.check(text)
    assert not result.valid
    assert any("Residual risk is empty" in error for error in result.errors)


def test_request_changes_without_blocking_warns_only() -> None:
    text = VALID_RECORD.replace("[blocking]", "[should-fix]")
    result = review_record_check.check(text)
    assert result.valid, result.errors
    assert any("REQUEST CHANGES with no blocking" in warning for warning in result.warnings)


def test_unknown_verdict_is_rejected() -> None:
    result = review_record_check.check(VALID_RECORD.replace("REQUEST CHANGES", "LOOKS FINE TO ME"))
    assert not result.valid
    assert any("unknown verdict" in error for error in result.errors)


def test_headings_with_markup_and_numbering_are_recognised() -> None:
    text = VALID_RECORD.replace("## Scope", "## 1. Scope").replace("## Findings", "## **Findings**")
    result = review_record_check.check(text)
    assert result.valid, result.errors


def test_subheading_inside_findings_keeps_findings() -> None:
    text = VALID_RECORD.replace("## Verdict", "### Blocking\n\n### Questions\n\n## Verdict")
    result = review_record_check.check(text)
    assert result.valid, result.errors
    assert result.counts["blocking"] == 1


def test_evidence_gap_verdict_needs_stated_gap() -> None:
    text = VALID_RECORD.replace("REQUEST CHANGES", "NEEDS MORE EVIDENCE")
    result = review_record_check.check(text)
    assert result.valid, result.errors
    assert result.counts["blocking"] == 1


def test_shipped_template_satisfies_the_contract() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    result = review_record_check.check(template)
    assert result.valid, result.errors
    assert result.verdict == "APPROVE WITH COMMENTS"


def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = tmp_path / "good.md"
    good.write_text(VALID_RECORD, encoding="utf-8")
    assert review_record_check.main([str(good)]) == 0
    assert "VALID" in capsys.readouterr().out

    bad = tmp_path / "bad.md"
    bad.write_text(VALID_RECORD.replace("REQUEST CHANGES", "APPROVE"), encoding="utf-8")
    assert review_record_check.main([str(bad), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is False
    assert payload["verdict"] == "APPROVE"

    assert review_record_check.main([str(tmp_path / "missing.md")]) == 2


def test_strict_promotes_warnings(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "warn.md"
    path.write_text(VALID_RECORD.replace("[blocking]", "[should-fix]"), encoding="utf-8")
    assert review_record_check.main([str(path)]) == 0
    capsys.readouterr()
    assert review_record_check.main([str(path), "--strict"]) == 1


def test_missing_coverage_is_an_error() -> None:
    text = VALID_RECORD.replace("- Coverage: full\n", "")
    result = review_record_check.check(text)
    assert not result.valid
    assert any("Coverage" in error for error in result.errors)


def test_partial_coverage_must_state_what_was_read() -> None:
    text = VALID_RECORD.replace("- Coverage: full", "- Coverage: partial")
    result = review_record_check.check(text)
    assert not result.valid
    assert any("does not say what was read" in error for error in result.errors)


def test_partial_coverage_with_approval_warns() -> None:
    text = VALID_RECORD.replace("- Coverage: full", "- Coverage: partial (retry.py only)")
    text = text.replace("REQUEST CHANGES", "APPROVE WITH COMMENTS")
    text = text.replace(
        "- [blocking] The exhaustion path returns None instead of the last error — evidence: "
        "`worker/retry.py:88` — verify: `test_retry_keeps_final_error` fails before the fix and passes after",
        "- [question] Is the exhaustion path intended to return the last error?",
    )
    result = review_record_check.check(text)
    assert result.valid, result.errors
    assert result.coverage == "partial"
    assert any("partial coverage" in warning for warning in result.warnings)


def test_partial_coverage_with_resolution_is_accepted() -> None:
    text = VALID_RECORD.replace("- Coverage: full", "- Coverage: partial (worker/retry.py only)")
    result = review_record_check.check(text)
    assert result.valid, result.errors
    assert result.coverage == "partial"
    assert result.warnings == []
