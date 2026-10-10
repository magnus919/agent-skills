"""Freeze and preflight bounded Jev qualification inputs without dispatching calls."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "docs" / "fair-skill-evaluation-qualification-v1.json"
PLAN = ROOT / "docs" / "fair-skill-evaluation-pilot-v1.json"
CONTRACT = ROOT / "eval_runner" / "fair-pilot-evidence-contracts-v2.json"
CANDIDATE_MAP = ROOT / "docs" / "fair-skill-evaluation-candidate-references-v1.json"
BASELINE_MAP = ROOT / "docs" / "fair-skill-evaluation-baseline-references-v1.json"
CHALLENGES = ROOT / "eval_runner" / "tests" / "fixtures" / "business_agent_judge_challenges.json"
LABELS = {"met", "not_met", "not_shown"}
SPLITS = {"development", "held_out"}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _reference_content(revision: str, skill: str, relative: str, expected_hash: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{revision}:{skill}/{relative}"],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"cannot resolve pinned source {revision}:{skill}/{relative}")
    if _sha256(result.stdout) != expected_hash:
        raise ValueError(f"pinned source hash mismatch: {skill}/{relative}")
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"pinned source is not UTF-8: {skill}/{relative}") from exc


def _validate_source_fact(
    fact_id: str,
    fact: dict[str, Any],
    record: dict[str, Any],
    expected_pins: dict[str, str],
) -> None:
    """Check source-fact pins and any exact evidence anchors."""
    source = fact.get("source")
    if not isinstance(source, dict):
        raise ValueError(f"source fact has no source object: {fact_id}")
    kind = source.get("kind", "reference")
    path = source.get("path")
    source_hash = source.get("sha256")
    excerpt = source.get("evidence_excerpt")
    if not isinstance(path, str) or not isinstance(source_hash, str):
        raise ValueError(f"source fact has an invalid source pin: {fact_id}")
    if excerpt is not None and (not isinstance(excerpt, str) or not excerpt.strip()):
        raise ValueError(f"source fact has an invalid evidence excerpt: {fact_id}")

    if kind == "reference":
        if expected_pins.get(path) != source_hash:
            raise ValueError(f"source fact pin mismatch: {fact_id}")
        if excerpt is not None:
            content = _reference_content(
                record["source_revision"], record["skill"], path, source_hash
            )
            if excerpt not in content:
                raise ValueError(f"source fact evidence excerpt mismatch: {fact_id}")
        return

    if kind != "eval_expected_output":
        raise ValueError(f"unsupported source fact source kind: {fact_id}")
    if (
        path != "evals/evals.json"
        or source.get("case_id") != record["case_id"]
        or source.get("field") != "expected_output"
        or source.get("provided_to_jev") is not False
        or excerpt is None
    ):
        raise ValueError(f"invalid eval-contract source fact provenance: {fact_id}")
    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "show",
            f"{record['source_revision']}:{record['skill']}/{path}",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode or _sha256(result.stdout) != source_hash:
        raise ValueError(f"eval-contract source fact pin mismatch: {fact_id}")
    try:
        manifest = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"eval-contract source fact is not valid UTF-8 JSON: {fact_id}") from exc
    case = next(
        (item for item in manifest.get("evals", []) if item.get("id") == record["case_id"]),
        None,
    )
    expected_output = case.get("expected_output") if isinstance(case, dict) else None
    if not isinstance(expected_output, str) or excerpt not in expected_output:
        raise ValueError(f"eval-contract source fact evidence excerpt mismatch: {fact_id}")


def _historical_excerpt(record: dict[str, Any], fixture: dict[str, Any]) -> str:
    reference = record["artifact_reference"]
    if reference.get("path") != CHALLENGES.relative_to(ROOT).as_posix():
        raise ValueError("historical challenge path is not pinned")
    artifact_record = reference["record"]
    parent = record["parent_artifact"]
    if artifact_record.startswith("challenges/"):
        _, challenge_id, variant = artifact_record.split("/", 2)
        challenge = next(
            (item for item in fixture["challenges"] if item["id"] == challenge_id), None
        )
        if challenge is None:
            raise ValueError("historical challenge reference is unknown")
        if (
            parent.get("response_sha256") != challenge["source"]["response_sha256"]
            or parent.get("run") != challenge["source"]["run"]
        ):
            raise ValueError("historical parent artifact identity mismatch")
        fragments = challenge[variant]["verbatim_fragments"]
    elif artifact_record == "generated_output_flaws/policy-translation-fidelity":
        flaw = fixture["generated_output_flaws"][0]
        if (
            parent.get("response_sha256") != flaw["source"]["response_sha256"]
            or parent.get("run") != flaw["source"]["run"]
        ):
            raise ValueError("historical parent artifact identity mismatch")
        fragments = flaw["verbatim_fragments"]
    else:
        raise ValueError("historical artifact reference is unsupported")
    for fragment in fragments:
        if _sha256(fragment["text"].encode()) != fragment["sha256"]:
            raise ValueError("historical artifact fragment hash mismatch")
    return "\n\n".join(fragment["text"] for fragment in fragments)


def _audit_module() -> Any:
    scripts = ROOT / "system-one" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    return importlib.import_module("jev_eval_audit")


def _contains_key(value: Any, forbidden: set[str]) -> bool:
    if isinstance(value, dict):
        return bool(forbidden & set(value)) or any(
            _contains_key(item, forbidden) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden) for item in value)
    return False


def build_qualification_report(*, include_request_payloads: bool = False) -> dict[str, Any]:
    """Validate the frozen dossier and construct exact offline request payloads."""
    dossier = json.loads(DOSSIER.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    contract_bytes = CONTRACT.read_bytes()
    contract = json.loads(contract_bytes)
    candidate_data = json.loads(CANDIDATE_MAP.read_text(encoding="utf-8"))
    baseline_data = json.loads(BASELINE_MAP.read_text(encoding="utf-8"))
    candidate_map = candidate_data["cases"]
    baseline_map = baseline_data["cases"]
    challenge_fixture = json.loads(CHALLENGES.read_text(encoding="utf-8"))
    if dossier.get("schema_version") != 1 or dossier.get("dispatch_authorized") is not False:
        raise ValueError("qualification dossier must be v1 and non-dispatchable")
    records = dossier.get("records")
    if not isinstance(records, list) or len(records) != 12:
        raise ValueError("qualification dossier must contain exactly 12 frozen cases")
    ids = [record.get("id") for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("qualification case IDs must be unique")
    if (
        sum(record.get("split") == "development" for record in records) != 7
        or sum(record.get("split") == "held_out" for record in records) != 5
        or dossier.get("splits") != {"development": 7, "held_out": 5}
    ):
        raise ValueError(
            "qualification split metadata and records must contain seven development and five held-out cases"
        )

    plan_by_key = {f"{item['skill']}/{item['case_id']}": item for item in plan["pilot"]}
    source_facts = dossier.get("source_facts")
    if not isinstance(source_facts, dict):
        raise ValueError("qualification source facts must be a pinned object")
    expected_ids = {item["case_id"] for item in plan["pilot"]}
    if (
        candidate_data.get("schema_version") != 1
        or baseline_data.get("schema_version") != 1
        or set(candidate_map) != expected_ids
        or set(baseline_map) != expected_ids
    ):
        raise ValueError("candidate and baseline reference maps must cover all pilot cases")
    audit = _audit_module()
    payloads: list[dict[str, Any]] = []
    wire_requests: list[dict[str, Any]] = []
    kind_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}
    split_counts: dict[str, int] = {}
    for record in records:
        if record.get("split") not in SPLITS or record.get("expected_label") not in LABELS:
            raise ValueError(f"invalid split or expected label in {record.get('id')}")
        if record.get("label_review_status") != "pending_independent_agent_review":
            raise ValueError(f"label review status must remain pending for {record['id']}")
        skill, case_id = record["skill"], record["case_id"]
        key = f"{skill}/{case_id}"
        pilot_case = plan_by_key.get(key)
        if pilot_case is None:
            raise ValueError(f"qualification case is outside pilot: {key}")
        if record.get("source_revision") != pilot_case["candidate_revision"]:
            raise ValueError(f"qualification source revision mismatch: {record['id']}")
        pins = record.get("source_pins")
        if not isinstance(pins, list) or not pins:
            raise ValueError(f"qualification case has no pinned source: {record['id']}")
        expected_pins = candidate_map[case_id]
        if {pin["path"]: pin["sha256"] for pin in pins} != expected_pins:
            raise ValueError(f"qualification source map mismatch: {record['id']}")
        for fact_id in record.get("source_fact_ids", []):
            fact = source_facts.get(fact_id)
            if not isinstance(fact, dict) or fact.get("case_key") != key:
                raise ValueError(f"source fact is missing or mis-scoped: {fact_id}")
            _validate_source_fact(fact_id, fact, record, expected_pins)

        if "artifact_reference" in record:
            response = _historical_excerpt(record, challenge_fixture)
            if response != record["response"]:
                raise ValueError(f"historical excerpt changed: {record['id']}")
            if _sha256(response.encode()) != record["response_sha256"]:
                raise ValueError(f"historical excerpt hash mismatch: {record['id']}")
        else:
            response = record["response"]
            if _sha256(response.encode()) != record["response_sha256"]:
                raise ValueError(f"authored response hash mismatch: {record['id']}")
        case_contract = contract["cases"][key]
        if record["task_prompt_sha256"] != case_contract["task_inputs"]["prompt_sha256"]:
            raise ValueError(f"task prompt hash mismatch: {record['id']}")
        prompt_result = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "show",
                f"{pilot_case['candidate_revision']}:{skill}/evals/evals.json",
            ],
            capture_output=True,
            check=False,
        )
        if prompt_result.returncode:
            raise ValueError(f"cannot load pinned task manifest for {record['id']}")
        manifest = json.loads(prompt_result.stdout)
        task_case = next(item for item in manifest["evals"] if item["id"] == case_id)
        prompt = task_case["prompt"]
        if _sha256(prompt.encode()) != record["task_prompt_sha256"]:
            raise ValueError(f"pinned task prompt changed: {record['id']}")

        sources = []
        for pin in pins:
            content = _reference_content(
                record["source_revision"], skill, pin["path"], pin["sha256"]
            )
            sources.append({"path": pin["path"], "sha256": pin["sha256"], "content": content})
        judgment_context = {
            "task_prompt": prompt,
            "task_input_sha256": record["task_prompt_sha256"],
            "authoritative_sources": sources,
            "evidence_contract_sha256": _sha256(contract_bytes),
        }
        group = {
            "skill": skill,
            "case_id": case_id,
            "side": "candidate",
            "response": response,
            "response_sha256": record["response_sha256"],
            "assertions": [record["assertion"]],
            "judgment_context": judgment_context,
        }
        request = audit.build_request(group, question_variant="deployed")
        encoded = json.dumps(
            request, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        if len(encoded) > dossier["batch_plan"]["max_request_payload_bytes"]:
            raise ValueError(f"qualification request exceeds payload limit: {record['id']}")
        if _contains_key(
            request,
            {
                "expected_label",
                "label_basis",
                "source_fact_ids",
                "split",
                "sample_kind",
                "label_review_status",
                "expected_output",
                "evidence_excerpt",
            },
        ):
            raise ValueError(f"qualification label leaked into Jev request: {record['id']}")
        payloads.append(
            {
                "id": record["id"],
                "split": record["split"],
                "skill": skill,
                "case_id": case_id,
                "sample_kind": record["sample_kind"],
                "expected_label": record["expected_label"],
                "label_review_status": record["label_review_status"],
                "label_basis": record["label_basis"],
                "source_fact_ids": record["source_fact_ids"],
                "source_revision": record["source_revision"],
                "source_pins": pins,
                "response_sha256": record["response_sha256"],
                "question_input_sha256": audit.question_input_sha256(request),
                "request_payload_sha256": _sha256(encoded),
                "request_payload_bytes": len(encoded),
            }
        )
        wire_requests.append(request)
        for counters, label in (
            (kind_counts, record["sample_kind"]),
            (label_counts, record["expected_label"]),
            (split_counts, record["split"]),
        ):
            counters[label] = counters.get(label, 0) + 1

    paraphrases = [record for record in records if record.get("semantic_equivalence_pair")]
    if (
        len(paraphrases) != 2
        or len({record["expected_label"] for record in paraphrases}) != 1
        or {record["split"] for record in paraphrases} != {"development"}
    ):
        raise ValueError("semantic paraphrase control must be a same-label development-only pair")
    if (
        len({record["assertion"] for record in paraphrases}) != 1
        or len({record["response_sha256"] for record in paraphrases}) != 2
    ):
        raise ValueError(
            "semantic paraphrases must share the assertion but differ in artifact bytes"
        )

    report = {
        "status": "ready_for_independent_agent_review_not_dispatch",
        "dispatch_authorized": False,
        "live_attempts": 0,
        "model": audit.MODEL,
        "endpoint": audit.ENDPOINT,
        "question_variant": "deployed",
        "assertions_per_request": 1,
        "shared_cap": dossier["shared_cap"],
        "initial_request_cap": dossier["batch_plan"]["initial_request_cap"],
        "reserved_follow_up_attempts": dossier["batch_plan"]["reserved_follow_up_attempts"],
        "request_count": len(payloads),
        "split_counts": split_counts,
        "sample_kind_counts": kind_counts,
        "proposed_label_counts": label_counts,
        "qualification_source_sha256": _sha256(DOSSIER.read_bytes()),
        "contract_sha256": _sha256(contract_bytes),
        "requests": payloads,
    }
    # The live runner needs exact payloads, but the ordinary preflight CLI and
    # its saved report intentionally expose only hashes and metadata.
    if include_request_payloads:
        report["_request_payloads"] = wire_requests
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the complete request dossier")
    args = parser.parse_args()
    try:
        report = build_qualification_report()
    except (OSError, ValueError, KeyError, StopIteration, subprocess.SubprocessError) as exc:
        report = {"status": "preflight_error", "dispatch_authorized": False, "error": str(exc)}
    print(json.dumps(report, indent=2 if args.json else None, sort_keys=True))
    return 0 if report.get("status") == "ready_for_independent_agent_review_not_dispatch" else 1


if __name__ == "__main__":
    raise SystemExit(main())
