"""Deterministic grader for eval assertions.

Checks machine-parseable assertions against AdapterOutput. Assertions follow
a convention-based format:

    response_contains:<substring>
    response_not_contains:<substring>
    exit_status:<status>
    artifact_exists:<filename>
    environment_state:<key>=<value>
    activation_evidence_contains:<substring>
    tool_event_count_gte:<n>

Assertions that do not match a known pattern are reported as requiring manual
review and do not affect the pass/fail verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import AdapterOutput, ExitStatus


class AssertionVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    MANUAL_REVIEW = "manual_review"
    INFRA_ERROR = "infra_error"


@dataclass(frozen=True)
class AssertionResult:
    assertion: str
    verdict: AssertionVerdict
    detail: str = ""


@dataclass
class GradeResult:
    case_id: str
    passed: bool
    results: list[AssertionResult] = field(default_factory=list)
    infra_error: bool = False

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.verdict == AssertionVerdict.PASS)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if r.verdict == AssertionVerdict.FAIL)

    @property
    def manual_count(self) -> int:
        return sum(1 for r in self.results if r.verdict == AssertionVerdict.MANUAL_REVIEW)


def _check_assertion(assertion: str, output: AdapterOutput) -> AssertionResult:
    if ":" not in assertion:
        return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "no recognized pattern")

    kind, _, value = assertion.partition(":")
    kind = kind.strip().lower()
    value = value.strip()

    if kind == "response_contains":
        if output.response and value in output.response:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(assertion, AssertionVerdict.FAIL, f"'{value}' not in response")

    if kind == "response_not_contains":
        if output.response is None or value not in output.response:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(assertion, AssertionVerdict.FAIL, f"'{value}' found in response")

    if kind == "exit_status":
        expected = value.lower()
        actual = output.exit_status.value
        if actual == expected:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(
            assertion, AssertionVerdict.FAIL, f"expected {expected}, got {actual}"
        )

    if kind == "artifact_exists":
        if value in output.artifacts:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(assertion, AssertionVerdict.FAIL, f"'{value}' not in artifacts")

    if kind == "environment_state":
        if "=" not in value:
            return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "malformed key=value")
        key, _, expected_val = value.partition("=")
        if output.environment_state and key in output.environment_state:
            actual_val = str(output.environment_state[key])
            if actual_val == expected_val:
                return AssertionResult(assertion, AssertionVerdict.PASS)
            return AssertionResult(
                assertion, AssertionVerdict.FAIL, f"{key}={actual_val}, expected {expected_val}"
            )
        return AssertionResult(
            assertion, AssertionVerdict.FAIL, f"key '{key}' not in environment_state"
        )

    if kind == "activation_evidence_contains":
        if output.activation_evidence and value in output.activation_evidence:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(
            assertion, AssertionVerdict.FAIL, f"'{value}' not in activation_evidence"
        )

    if kind == "tool_event_count_gte":
        try:
            threshold = int(value)
        except ValueError:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "non-integer threshold"
            )
        if len(output.tool_events) >= threshold:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(
            assertion, AssertionVerdict.FAIL, f"{len(output.tool_events)} < {threshold}"
        )

    return AssertionResult(
        assertion, AssertionVerdict.MANUAL_REVIEW, f"unknown assertion kind '{kind}'"
    )


def grade_output(case_id: str, assertions: list[str], output: AdapterOutput) -> GradeResult:
    """Grade an adapter output against a list of assertions.

    Infrastructure errors (non-completed exit status) are distinguished from
    skill failures: all assertions are marked infra_error and the grade is
    not-pass, but the infra_error flag is set.
    """
    if output.exit_status != ExitStatus.COMPLETED:
        results = [
            AssertionResult(
                a, AssertionVerdict.INFRA_ERROR, f"exit_status={output.exit_status.value}"
            )
            for a in assertions
        ]
        return GradeResult(case_id=case_id, passed=False, results=results, infra_error=True)

    results = [_check_assertion(a, output) for a in assertions]
    passed = all(
        r.verdict in (AssertionVerdict.PASS, AssertionVerdict.MANUAL_REVIEW) for r in results
    )
    return GradeResult(case_id=case_id, passed=passed, results=results)
