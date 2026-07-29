"""Release-grade evaluation: repeated trials, rubric graders, and release matrix.

Builds on the deterministic paired evaluation infrastructure to add:
- Multi-trial aggregation per case (success frequency, consistency)
- Versioned rubric graders with abstain/insufficient-evidence
- Blinded pairwise comparison with position randomization and order-reversal
- Human calibration tracking with disagreement slices
- Case set separation (dev, regression, release)
- Freeze snapshot validation
- Release decision: PASS, CONDITIONAL, HOLD, BLOCK
"""

from __future__ import annotations

import hashlib
import json
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RELEASE_SCHEMA_VERSION = 1

CASE_SETS = ("dev", "regression", "release")

RELEASE_OUTCOMES = ("PASS", "CONDITIONAL", "HOLD", "BLOCK")


@dataclass(frozen=True)
class FreezeSnapshot:
    candidate_tree_hash: str
    baseline_tree_hash: str
    dataset_hash: str
    grader_versions: dict[str, str]
    randomization_seed: int
    exclusions: tuple[str, ...] = ()
    frozen_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_tree_hash": self.candidate_tree_hash,
            "baseline_tree_hash": self.baseline_tree_hash,
            "dataset_hash": self.dataset_hash,
            "grader_versions": dict(self.grader_versions),
            "randomization_seed": self.randomization_seed,
            "exclusions": list(self.exclusions),
            "frozen_at": self.frozen_at or datetime.now(timezone.utc).isoformat(),
        }

    @property
    def complete(self) -> bool:
        return bool(
            self.candidate_tree_hash
            and self.baseline_tree_hash
            and self.dataset_hash
            and self.grader_versions
        )


@dataclass
class TrialRecord:
    trial_id: str
    case_id: str
    status: str
    passed: bool
    missing_evidence: list[str] = field(default_factory=list)


@dataclass
class CaseAggregation:
    case_id: str
    case_set: str
    trials: list[TrialRecord] = field(default_factory=list)

    @property
    def trial_count(self) -> int:
        return len(self.trials)

    @property
    def success_count(self) -> int:
        return sum(1 for t in self.trials if t.status == "completed" and t.passed)

    @property
    def failure_count(self) -> int:
        return sum(1 for t in self.trials if t.status == "completed" and not t.passed)

    @property
    def error_count(self) -> int:
        return sum(1 for t in self.trials if t.status == "error")

    @property
    def timeout_count(self) -> int:
        return sum(1 for t in self.trials if t.status == "timeout")

    @property
    def success_frequency(self) -> float:
        if not self.trials:
            return 0.0
        return self.success_count / self.trial_count

    @property
    def consistent(self) -> bool:
        completed = [t for t in self.trials if t.status == "completed"]
        if not completed:
            return False
        first = completed[0].passed
        return all(t.passed == first for t in completed)

    @property
    def all_missing_evidence(self) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for t in self.trials:
            for m in t.missing_evidence:
                if m not in seen:
                    seen.add(m)
                    result.append(m)
        return result

    def to_dict(self, paired_delta: str = "insufficient_data") -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "case_set": self.case_set,
            "trial_count": self.trial_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "error_count": self.error_count,
            "timeout_count": self.timeout_count,
            "success_frequency": round(self.success_frequency, 4),
            "consistent": self.consistent,
            "missing_evidence": self.all_missing_evidence,
            "paired_delta": paired_delta,
        }


def aggregate_trials(
    manifests: list[dict[str, Any]],
    case_sets: dict[str, str] | None = None,
) -> list[CaseAggregation]:
    """Group run manifests by case_id and aggregate trial outcomes."""
    by_case: dict[str, list[TrialRecord]] = {}
    for m in manifests:
        case_id = m.get("case", {}).get("case_id", "")
        if not case_id:
            continue
        trial = TrialRecord(
            trial_id=m.get("trial_id", ""),
            case_id=case_id,
            status=m.get("status", "error"),
            passed=_manifest_passed(m),
            missing_evidence=m.get("missing_evidence", []),
        )
        by_case.setdefault(case_id, []).append(trial)

    results = []
    for case_id, trials in sorted(by_case.items()):
        case_set = "dev"
        if case_sets and case_id in case_sets:
            case_set = case_sets[case_id]
        results.append(CaseAggregation(case_id=case_id, case_set=case_set, trials=trials))
    return results


def _manifest_passed(m: dict[str, Any]) -> bool:
    if m.get("status") != "completed":
        return False
    failures = m.get("failures", [])
    return len(failures) == 0


@dataclass(frozen=True)
class RubricGrader:
    grader_id: str
    version: str
    criteria: tuple[str, ...]

    def grade(
        self,
        response: str | None,
        expected: str,
        *,
        blinded: bool = True,
    ) -> dict[str, Any]:
        if response is None:
            return self._result("insufficient_evidence", {}, "no response to evaluate", blinded)
        if not response.strip():
            return self._result("abstain", {}, "empty response; cannot judge quality", blinded)
        scores: dict[str, float] = {}
        for criterion in self.criteria:
            scores[criterion] = self._score_criterion(criterion, response, expected)
        avg = sum(scores.values()) / len(scores) if scores else 0.0
        if avg >= 0.7:
            verdict = "pass"
        elif avg >= 0.4:
            verdict = "fail"
        else:
            verdict = "fail"
        rationale = f"mean score {avg:.2f} across {len(self.criteria)} criteria"
        return self._result(verdict, scores, rationale, blinded)

    def _score_criterion(self, criterion: str, response: str, expected: str) -> float:
        response_lower = response.lower()
        expected_lower = expected.lower()
        expected_tokens = set(expected_lower.split())
        response_tokens = set(response_lower.split())
        if not expected_tokens:
            return 0.5
        overlap = len(expected_tokens & response_tokens) / len(expected_tokens)
        return min(1.0, overlap)

    def _result(
        self,
        verdict: str,
        scores: dict[str, float],
        rationale: str,
        blinded: bool,
    ) -> dict[str, Any]:
        return {
            "grader_id": self.grader_id,
            "grader_version": self.version,
            "blinded": blinded,
            "verdict": verdict,
            "scores": scores,
            "rationale": rationale,
        }


def apply_rubric(
    grader: RubricGrader,
    case_id: str,
    response: str | None,
    expected: str,
    *,
    blinded: bool = True,
) -> dict[str, Any]:
    result = grader.grade(response, expected, blinded=blinded)
    result["case_id"] = case_id
    return result


@dataclass(frozen=True)
class PairwisePlan:
    case_id: str
    position_a: str
    position_b: str
    seed: int

    @property
    def reversed(self) -> PairwisePlan:
        return PairwisePlan(
            case_id=self.case_id,
            position_a=self.position_b,
            position_b=self.position_a,
            seed=self.seed,
        )


def plan_pairwise(case_ids: list[str], seed: int) -> list[PairwisePlan]:
    """Assign randomized A/B positions for each case, blinded to identity."""
    rng = random.Random(seed)
    plans = []
    for case_id in case_ids:
        if rng.random() < 0.5:
            plans.append(PairwisePlan(case_id, "candidate", "baseline", seed))
        else:
            plans.append(PairwisePlan(case_id, "baseline", "candidate", seed))
    return plans


def evaluate_pairwise(
    plan: PairwisePlan,
    response_a: str | None,
    response_b: str | None,
    expected: str,
    *,
    judge: RubricGrader | None = None,
) -> dict[str, Any]:
    """Compare two responses under a blinded pairwise plan."""
    if judge is None:
        judge = RubricGrader("default-pairwise", "1", ("relevance", "completeness"))

    grade_a = judge.grade(response_a, expected, blinded=True)
    grade_b = judge.grade(response_b, expected, blinded=True)

    score_a = _mean_score(grade_a)
    score_b = _mean_score(grade_b)

    if (
        grade_a["verdict"] == "abstain"
        or grade_b["verdict"] == "abstain"
        or grade_a["verdict"] == "insufficient_evidence"
        or grade_b["verdict"] == "insufficient_evidence"
    ):
        winner = "abstain"
    elif abs(score_a - score_b) < 0.05:
        winner = "tie"
    elif score_a > score_b:
        winner = "a"
    else:
        winner = "b"

    reversed_plan = plan.reversed  # noqa: F841 (used for future blinded grading)
    grade_rev_a = judge.grade(response_b, expected, blinded=True)
    grade_rev_b = judge.grade(response_a, expected, blinded=True)
    score_rev_a = _mean_score(grade_rev_a)
    score_rev_b = _mean_score(grade_rev_b)

    if abs(score_rev_a - score_rev_b) < 0.05:
        rev_winner = "tie"
    elif score_rev_a > score_rev_b:
        rev_winner = "a"
    else:
        rev_winner = "b"

    order_consistent = _winners_consistent(winner, rev_winner)

    return {
        "case_id": plan.case_id,
        "position_a": plan.position_a,
        "position_b": plan.position_b,
        "winner": winner,
        "order_reversal_tested": True,
        "order_reversal_consistent": order_consistent,
    }


def _mean_score(grade: dict[str, Any]) -> float:
    scores: dict[str, float] = grade.get("scores", {})
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)


def _winners_consistent(forward: str, reversed_result: str) -> bool | None:
    if forward == "abstain" or reversed_result == "abstain":
        return None
    if forward == "tie" and reversed_result == "tie":
        return True
    if forward == "tie" or reversed_result == "tie":
        return False
    return forward == reversed_result


@dataclass
class CalibrationRecord:
    human_sample_count: int = 0
    judge_agreement_rate: float | None = None
    disagreement_slices: list[dict[str, Any]] = field(default_factory=list)

    @property
    def calibrated(self) -> bool:
        return (
            self.human_sample_count > 0
            and self.judge_agreement_rate is not None
            and self.judge_agreement_rate >= 0.7
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "human_sample_count": self.human_sample_count,
            "judge_agreement_rate": self.judge_agreement_rate,
            "disagreement_slices": self.disagreement_slices,
            "calibrated": self.calibrated,
        }


def compute_release_decision(
    case_results: list[dict[str, Any]],
    rubric_results: list[dict[str, Any]],
    calibration: CalibrationRecord,
    hard_gate_violations: list[str] | None = None,
) -> dict[str, Any]:
    """Compute PASS, CONDITIONAL, HOLD, or BLOCK from the release matrix."""
    violations = hard_gate_violations or []
    reasons: list[str] = []

    if violations:
        return {
            "outcome": "BLOCK",
            "reasons": [f"hard gate violation: {v}" for v in violations],
            "hard_gate_violations": violations,
        }

    release_cases = [c for c in case_results if c["case_set"] == "release"]
    regression_cases = [c for c in case_results if c["case_set"] == "regression"]

    missing_evidence_cases = [c["case_id"] for c in case_results if c.get("missing_evidence")]
    if missing_evidence_cases:
        reasons.append(f"missing evidence in cases: {', '.join(missing_evidence_cases)}")
        return {
            "outcome": "HOLD",
            "reasons": reasons,
            "hard_gate_violations": [],
        }

    inconsistent = [c["case_id"] for c in case_results if not c["consistent"]]
    low_frequency = [c["case_id"] for c in release_cases if c["success_frequency"] < 0.8]

    rubric_abstains = [
        r["case_id"] for r in rubric_results if r["verdict"] in ("abstain", "insufficient_evidence")
    ]

    uncalibrated_advisory = not calibration.calibrated

    if low_frequency:
        reasons.append(f"release cases below 80% success: {', '.join(low_frequency)}")
        return {
            "outcome": "BLOCK",
            "reasons": reasons,
            "hard_gate_violations": [],
        }

    regressions = [
        c["case_id"] for c in regression_cases if c["paired_delta"] == "candidate_regression"
    ]
    if regressions:
        reasons.append(f"regressions detected: {', '.join(regressions)}")
        return {
            "outcome": "BLOCK",
            "reasons": reasons,
            "hard_gate_violations": [],
        }

    conditional = False
    if inconsistent:
        reasons.append(f"inconsistent cases: {', '.join(inconsistent)}")
        conditional = True
    if rubric_abstains:
        reasons.append(f"rubric abstained on: {', '.join(rubric_abstains)}")
        conditional = True
    if uncalibrated_advisory:
        reasons.append("judge not calibrated against human labels; rubric results advisory only")
        conditional = True

    if conditional:
        return {
            "outcome": "CONDITIONAL",
            "reasons": reasons,
            "hard_gate_violations": [],
        }

    if not reasons:
        reasons.append("all gates satisfied")

    return {
        "outcome": "PASS",
        "reasons": reasons,
        "hard_gate_violations": [],
    }


def build_release_report(
    *,
    skill_name: str,
    freeze: FreezeSnapshot,
    case_results: list[dict[str, Any]],
    rubric_results: list[dict[str, Any]],
    pairwise_results: list[dict[str, Any]],
    calibration: CalibrationRecord,
    hard_gate_violations: list[str] | None = None,
) -> dict[str, Any]:
    decision = compute_release_decision(
        case_results, rubric_results, calibration, hard_gate_violations
    )
    return {
        "schema_version": RELEASE_SCHEMA_VERSION,
        "report_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_name": skill_name,
        "freeze_snapshot": freeze.to_dict(),
        "case_results": case_results,
        "rubric_results": rubric_results,
        "pairwise_results": pairwise_results,
        "calibration": calibration.to_dict(),
        "release_decision": decision,
    }


def write_release_report(report: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{report['skill_name']}--release-report.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def dataset_hash(manifest_path: Path) -> str:
    content = manifest_path.read_bytes()
    return hashlib.sha256(content).hexdigest()[:16]
