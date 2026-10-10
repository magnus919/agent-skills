"""Optional, judgment-only evidence contracts for portable eval-v1 cases."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .models import EvalCase
from .path_safety import validate_case_id, validate_relative_path
from .reference_inputs import MAX_FILE_BYTES, MAX_REFERENCE_BYTES, MAX_REFERENCES, read_source

CONTRACT_PATH = "evals/evidence-contract-v1.json"
PILOT_CONTRACT_PATH = "eval_runner/fair-pilot-evidence-contracts-v2.json"
ORACLE_TYPES = {"deterministic_assertions", "deterministic_fixture", "human_review"}
MAX_JUDGMENT_CONTEXT_BYTES = 100_000
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_LIST_FIELDS = (
    "expected_observable_outcomes",
    "prohibited_behavior",
    "required_evidence",
)


def _full_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_evidence_contracts(skill_root: Path, cases: list[EvalCase]) -> dict[str, dict[str, Any]]:
    """Validate optional hidden judgment data without adding it to task inputs."""
    local_contract = skill_root / CONTRACT_PATH
    repo_root: Path | None = None
    if local_contract.exists() or local_contract.is_symlink():
        source_root, relative_contract, qualified_prefix = skill_root, CONTRACT_PATH, ""
    else:
        for ancestor in (skill_root, *skill_root.parents):
            candidate = ancestor / PILOT_CONTRACT_PATH
            if candidate.is_file() or candidate.is_symlink():
                repo_root = ancestor
                break
        if repo_root is None:
            return {}
        source_root = repo_root
        relative_contract = PILOT_CONTRACT_PATH
        qualified_prefix = skill_root.relative_to(repo_root).as_posix() + "/"

    raw = read_source(source_root, relative_contract, MAX_FILE_BYTES)
    data = json.loads(raw)
    if not isinstance(data, dict) or set(data) != {"schema_version", "cases"}:
        raise ValueError("invalid evidence-contract fields")
    version = data["schema_version"]
    if type(version) is not int or version not in {1, 2}:
        raise ValueError("unsupported evidence-contract version")
    if not isinstance(data["cases"], dict):
        raise ValueError("evidence-contract cases must be an object")

    if qualified_prefix:
        source_cases: dict[str, Any] = {}
        for qualified_case_id, contract in data["cases"].items():
            if qualified_case_id.startswith(qualified_prefix):
                case_id = qualified_case_id[len(qualified_prefix) :]
                source_cases[case_id] = contract
    else:
        source_cases = data["cases"]

    cases_by_id = {case.id: case for case in cases}
    if len(cases_by_id) != len(cases):
        raise ValueError("evidence-contract input cases must have unique IDs")

    validated: dict[str, dict[str, Any]] = {}
    contract_hash = _full_hash(raw)
    for case_id, contract in source_cases.items():
        validate_case_id(case_id)
        if case_id not in cases_by_id:
            raise ValueError("evidence-contract names an unknown case")
        expected_fields = {
            "task_inputs",
            "authoritative_sources",
            *_LIST_FIELDS,
            "oracle_type",
        }
        if version == 2:
            expected_fields.update({"arm_sources", "review_criteria"})
        if not isinstance(contract, dict) or set(contract) != expected_fields:
            raise ValueError(f"invalid evidence-contract fields for {case_id}")

        case = cases_by_id[case_id]
        task_inputs = contract["task_inputs"]
        if not isinstance(task_inputs, dict) or set(task_inputs) != {
            "prompt_sha256",
            "fixture_sha256",
        }:
            raise ValueError(f"invalid task-input hashes for {case_id}")
        if task_inputs["prompt_sha256"] != _full_hash(case.prompt.encode("utf-8")):
            raise ValueError(f"task prompt hash mismatch for {case_id}")
        fixture_hashes = task_inputs["fixture_sha256"]
        if not isinstance(fixture_hashes, dict) or set(fixture_hashes) != set(case.files):
            raise ValueError(f"task fixture hash paths mismatch for {case_id}")
        for relative in case.files:
            actual = _full_hash(read_source(skill_root, relative, MAX_FILE_BYTES))
            if fixture_hashes[relative] != actual:
                raise ValueError(f"task fixture hash mismatch for {case_id}: {relative}")

        sources = contract["authoritative_sources"]
        if not isinstance(sources, list) or len(sources) > MAX_REFERENCES:
            raise ValueError(f"authoritative sources must be a list for {case_id}")
        seen_sources: set[str] = set()
        source_bytes = 0
        for source in sources:
            if not isinstance(source, dict) or set(source) != {"path", "sha256"}:
                raise ValueError(f"invalid authoritative source for {case_id}")
            relative = validate_relative_path(source["path"])
            if relative in seen_sources or not _SHA256.fullmatch(str(source["sha256"])):
                raise ValueError(f"invalid or duplicate authoritative source for {case_id}")
            seen_sources.add(relative)
            source_content = read_source(skill_root, relative, MAX_FILE_BYTES)
            source_bytes += len(source_content)
            if source_bytes > MAX_REFERENCE_BYTES:
                raise ValueError(f"authoritative sources exceed byte limit for {case_id}")
            actual = _full_hash(source_content)
            if source["sha256"] != actual:
                raise ValueError(f"authoritative source hash mismatch for {case_id}: {relative}")

        if version == 2:
            arm_sources = contract["arm_sources"]
            if not isinstance(arm_sources, dict) or set(arm_sources) != {"candidate", "baseline"}:
                raise ValueError(f"arm sources must name candidate and baseline for {case_id}")
            candidate_pins = arm_sources["candidate"]
            baseline_pins = arm_sources["baseline"]
            for arm, pins in (("candidate", candidate_pins), ("baseline", baseline_pins)):
                if not isinstance(pins, dict) or set(pins) != {"revision", "references"}:
                    raise ValueError(f"invalid {arm} source pins for {case_id}")
                if not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", str(pins["revision"])):
                    raise ValueError(f"invalid {arm} snapshot revision for {case_id}")
                references = pins["references"]
                if not isinstance(references, list) or len(references) > MAX_REFERENCES:
                    raise ValueError(f"invalid {arm} reference list for {case_id}")
                paths: set[str] = set()
                for pin in references:
                    if not isinstance(pin, dict) or set(pin) != {"path", "sha256"}:
                        raise ValueError(f"invalid {arm} reference pin for {case_id}")
                    relative = validate_relative_path(pin["path"])
                    if relative in paths or not _SHA256.fullmatch(str(pin["sha256"])):
                        raise ValueError(f"invalid or duplicate {arm} reference for {case_id}")
                    paths.add(relative)
                if arm == "candidate" and references != sources:
                    raise ValueError(
                        f"candidate references disagree with authority sources for {case_id}"
                    )
            criteria = contract["review_criteria"]
            if (
                not isinstance(criteria, list)
                or not criteria
                or any(not isinstance(item, str) or not item.strip() for item in criteria)
            ):
                raise ValueError(f"review criteria must contain nonempty text for {case_id}")

        for field in _LIST_FIELDS:
            values = contract[field]
            if (
                not isinstance(values, list)
                or not values
                or any(not isinstance(value, str) or not value.strip() for value in values)
            ):
                raise ValueError(f"{field} must contain nonempty text for {case_id}")
        if contract["oracle_type"] not in ORACLE_TYPES:
            raise ValueError(f"invalid oracle type for {case_id}")

        validated[case_id] = {
            **contract,
            "evidence_contract_sha256": contract_hash,
        }
    return validated


def build_judgment_context(
    skill_root: Path, case: EvalCase, contract: dict[str, Any]
) -> dict[str, Any]:
    """Build source-grounded judge context; callers must keep it off generation inputs."""
    sources = []
    for pin in contract["authoritative_sources"]:
        content = read_source(skill_root, pin["path"], MAX_FILE_BYTES).decode("utf-8")
        if _full_hash(content.encode("utf-8")) != pin["sha256"]:
            raise ValueError(f"authoritative source changed after validation: {pin['path']}")
        sources.append({"path": pin["path"], "sha256": pin["sha256"], "content": content})
    context = {
        "task_prompt": case.prompt,
        "task_input_sha256": contract["task_inputs"]["prompt_sha256"],
        "authoritative_sources": sources,
        "evidence_contract_sha256": contract["evidence_contract_sha256"],
    }
    encoded = json.dumps(
        context, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode()
    if len(encoded) > MAX_JUDGMENT_CONTEXT_BYTES:
        raise ValueError("judgment context exceeds byte limit")
    return context
