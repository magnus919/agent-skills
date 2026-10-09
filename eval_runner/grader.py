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


class SemanticVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_ASSESSED = "not_assessed"


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
    execution_status: str = "completed"
    semantic_verdict: str = SemanticVerdict.NOT_ASSESSED.value
    evidence_complete: bool = False

    @property
    def execution_success(self) -> bool:
        return self.execution_status == "completed" and not self.infra_error

    @property
    def assertion_count(self) -> int:
        return len(self.results)

    @property
    def resolved_count(self) -> int:
        return self.pass_count + self.fail_count

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
        if not value:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "empty expected value"
            )
        if output.response is None:
            return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "response missing")
        if value in output.response:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(assertion, AssertionVerdict.FAIL, f"'{value}' not in response")

    if kind == "response_not_contains":
        if not value:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "empty forbidden value"
            )
        if output.response is None:
            return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "response missing")
        if value not in output.response:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(assertion, AssertionVerdict.FAIL, f"'{value}' found in response")

    if kind == "exit_status":
        expected = value.lower()
        if expected not in {status.value for status in ExitStatus}:
            return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "unknown exit status")
        actual = output.exit_status.value
        if actual == expected:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(
            assertion, AssertionVerdict.FAIL, f"expected {expected}, got {actual}"
        )

    if kind == "artifact_exists":
        if not value:
            return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "empty artifact path")
        if not output.artifact_inventory_complete:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "artifact inventory incomplete"
            )
        if value in output.artifacts:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(assertion, AssertionVerdict.FAIL, f"'{value}' not in artifacts")

    if kind == "environment_state":
        if "=" not in value:
            return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "malformed key=value")
        key, _, expected_val = value.partition("=")
        if not key:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "empty environment key"
            )
        if output.environment_state is None:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "environment state missing"
            )
        if key in output.environment_state:
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
        if not value:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "empty expected value"
            )
        if output.activation_evidence is None:
            return AssertionResult(
                assertion, AssertionVerdict.MANUAL_REVIEW, "activation evidence missing"
            )
        if value in output.activation_evidence:
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
        if threshold < 0:
            return AssertionResult(assertion, AssertionVerdict.MANUAL_REVIEW, "negative threshold")
        if len(output.tool_events) >= threshold:
            return AssertionResult(assertion, AssertionVerdict.PASS)
        return AssertionResult(
            assertion, AssertionVerdict.FAIL, f"{len(output.tool_events)} < {threshold}"
        )

    return AssertionResult(
        assertion, AssertionVerdict.MANUAL_REVIEW, f"unknown assertion kind '{kind}'"
    )


def grade_output(case_id: str, assertions: list[str], output: AdapterOutput) -> GradeResult:
    """Grade output without treating unknown or absent evidence as a pass.

    ``passed`` is retained for compatibility and means a semantic pass only.
    Infrastructure completion, assertion evidence, and semantic verdict are
    also exposed independently.
    """
    if output.exit_status != ExitStatus.COMPLETED:
        results = [
            AssertionResult(
                a, AssertionVerdict.INFRA_ERROR, f"exit_status={output.exit_status.value}"
            )
            for a in assertions
        ]
        return GradeResult(
            case_id=case_id,
            passed=False,
            results=results,
            infra_error=True,
            execution_status=output.exit_status.value,
            semantic_verdict=SemanticVerdict.NOT_ASSESSED.value,
            evidence_complete=False,
        )

    results = [_check_assertion(a, output) for a in assertions]
    has_failure = any(r.verdict == AssertionVerdict.FAIL for r in results)
    all_pass = bool(results) and all(r.verdict == AssertionVerdict.PASS for r in results)
    if has_failure:
        verdict = SemanticVerdict.FAIL
    elif all_pass:
        verdict = SemanticVerdict.PASS
    else:
        verdict = SemanticVerdict.NOT_ASSESSED
    return GradeResult(
        case_id=case_id,
        passed=verdict == SemanticVerdict.PASS,
        results=results,
        execution_status=output.exit_status.value,
        semantic_verdict=verdict.value,
        evidence_complete=bool(results)
        and all(r.verdict in (AssertionVerdict.PASS, AssertionVerdict.FAIL) for r in results),
    )
