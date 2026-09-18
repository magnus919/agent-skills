"""Portable semantic-progress and finality oracle for scripted agent transcripts.

This is a generic transcript grader, not an agent runtime and not an
integration with any specific harness. It evaluates the repository-agnostic
semantic-progress contract: judge semantic state, declared dependencies, and
declared stage actions — never elapsed time, raw iteration counts, request
identifiers, or repeated observation of unchanged state. Identical repetition
is a failure for checks (identical re-polls) and equally for unproductive work
turns (stuck work), while mechanism changes, escalations, and any number of
turns that change the semantic state remain allowed.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

ACCEPTED_STATES = frozenset({"accepted", "finished"})
BLOCKED_DEPENDENCY_STATES = frozenset({"pending", "failed"})
TERMINAL_ACTIONS = frozenset({"advance", "deliver", "complete"})
CHECK_ACTION = "check"
UNPRODUCTIVE_ACTIONS = frozenset({"work", "check"})
KNOWN_ACTIONS = frozenset(
    {"work", "check", "advance", "deliver", "complete", "mechanism_change", "escalate"}
)


@dataclass(frozen=True)
class ProgressVerdict:
    passed: bool
    reason: str
    checks_for_state: int
    identical_repolls: int


def _validate_transcript(transcript: Mapping[str, Any]) -> None:
    if not isinstance(transcript, Mapping):
        raise ValueError("transcript: must be a mapping")
    case_id = transcript.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id: must be a non-empty string")
    turns = transcript.get("turns")
    if not isinstance(turns, list) or not turns:
        raise ValueError("turns: must be a non-empty list")
    for index, turn in enumerate(turns):
        prefix = f"turns[{index}]"
        if not isinstance(turn, Mapping):
            raise ValueError(f"{prefix}: must be a mapping")
        for required in ("observation", "action"):
            if required not in turn:
                raise ValueError(f"{prefix}: missing '{required}'")
            if not isinstance(turn[required], Mapping):
                raise ValueError(f"{prefix}.{required}: must be a mapping")
        observation = turn["observation"]
        for required in ("stage", "deliverable_state", "dependency_state"):
            value = observation.get(required)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{prefix}.observation.{required}: must be a non-empty string")
        if "dependency_required_for_next_stage" not in observation:
            raise ValueError(f"{prefix}.observation: missing 'dependency_required_for_next_stage'")
        if not isinstance(observation["dependency_required_for_next_stage"], bool):
            raise ValueError(
                f"{prefix}.observation.dependency_required_for_next_stage: must be a boolean"
            )
        if "semantic_state" not in observation:
            raise ValueError(f"{prefix}.observation: missing 'semantic_state'")
        if not isinstance(observation["semantic_state"], Mapping):
            raise ValueError(f"{prefix}.observation.semantic_state: must be a mapping")
        kind = turn["action"].get("kind")
        if not isinstance(kind, str) or kind not in KNOWN_ACTIONS:
            raise ValueError(f"{prefix}.action.kind: unrecognized action kind {kind!r}")


def _semantic_fingerprint(observation: Mapping[str, Any]) -> str:
    payload = {
        "stage": observation["stage"],
        "deliverable_state": observation["deliverable_state"],
        "dependency_state": observation["dependency_state"],
        "dependency_required_for_next_stage": observation["dependency_required_for_next_stage"],
        "semantic_state": observation["semantic_state"],
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def evaluate_transcript(transcript: Mapping[str, Any]) -> ProgressVerdict:
    """Evaluate a portable semantic-progress/finality transcript."""
    _validate_transcript(transcript)
    checks_by_fingerprint: dict[str, int] = {}
    identical_repolls = 0
    previous_fingerprint: str | None = None
    previous_action_kind: str | None = None

    for index, turn in enumerate(transcript["turns"]):
        observation = turn["observation"]
        action_kind = turn["action"]["kind"]
        fingerprint = _semantic_fingerprint(observation)
        deliverable_state = observation["deliverable_state"]
        dependency_state = observation["dependency_state"]
        dependency_required = observation["dependency_required_for_next_stage"]

        if (
            deliverable_state in ACCEPTED_STATES
            and not dependency_required
            and action_kind not in TERMINAL_ACTIONS
        ):
            return ProgressVerdict(
                passed=False,
                reason=(
                    f"turns[{index}]: accepted/finished deliverable with no dependency "
                    f"required for the next stage must advance, deliver, or complete "
                    f"immediately; found action '{action_kind}'"
                ),
                checks_for_state=checks_by_fingerprint.get(fingerprint, 0),
                identical_repolls=identical_repolls,
            )

        if (
            dependency_required
            and dependency_state in BLOCKED_DEPENDENCY_STATES
            and action_kind == CHECK_ACTION
        ):
            checks_by_fingerprint[fingerprint] = checks_by_fingerprint.get(fingerprint, 0) + 1
            count = checks_by_fingerprint[fingerprint]
            if count > 1:
                identical_repolls += 1
                return ProgressVerdict(
                    passed=False,
                    reason=(
                        f"turns[{index}]: identical re-poll — check repeated for an unchanged "
                        f"semantic state (fingerprint {fingerprint[:12]}) while the declared "
                        f"stage action remains untaken; a volatile change such as a new "
                        f"timestamp or request ID is not progress; require a mechanism "
                        f"change or escalation"
                    ),
                    checks_for_state=count,
                    identical_repolls=identical_repolls,
                )

        if (
            previous_fingerprint is not None
            and fingerprint == previous_fingerprint
            and action_kind in UNPRODUCTIVE_ACTIONS
            and previous_action_kind == action_kind
        ):
            return ProgressVerdict(
                passed=False,
                reason=(
                    f"turns[{index}]: stuck work — action '{action_kind}' repeated against "
                    f"an unchanged semantic state (fingerprint {fingerprint[:12]}) while the "
                    f"declared stage action remains untaken; repeating identical effort "
                    f"without a semantic change is not progress; declare a mechanism "
                    f"change, escalate, or produce a changed semantic state"
                ),
                checks_for_state=checks_by_fingerprint.get(fingerprint, 0),
                identical_repolls=identical_repolls,
            )

        previous_fingerprint = fingerprint
        previous_action_kind = action_kind

    return ProgressVerdict(
        passed=True,
        reason="all turns satisfy the semantic-progress and finality contract",
        checks_for_state=max(checks_by_fingerprint.values(), default=0),
        identical_repolls=identical_repolls,
    )
