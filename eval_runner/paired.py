"""Paired evaluation orchestrator.

Runs matched candidate and baseline trials in clean, isolated environments,
grades both with a deterministic verifier, and produces a case-level comparison
report. The baseline is either an explicitly pinned old skill or a separately
labeled no-skill diagnostic. Mutable state is reset for every trial.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .adapter import HarnessAdapter
from .comparison import build_comparison_report, format_comparison_summary, write_comparison_report
from .evidence_contract import load_evidence_contracts
from .grader import grade_output
from .manifest import build_manifest, write_manifest
from .models import AdapterInput, EvalCase
from .path_safety import contained_path, validate_case_id
from .reference_inputs import build_context, validate_references
from .runner import load_cases
from .sandbox import cleanup_sandbox, stage_paired_sandboxes

COMPARISON_MODES = {"skill_vs_no_skill", "pinned_skill_vs_skill"}
COMPARISON_POLICIES = {"complete_package", "instruction_only"}
FULL_REVISION = re.compile(r"(?:[a-f0-9]{40}|[a-f0-9]{64})\Z")


def _snapshot_cases(skill_path: Path) -> list[EvalCase]:
    manifest = skill_path / "evals" / "evals.json"
    return load_cases(manifest) if manifest.is_file() else []


def _verify_snapshot_revision(skill_path: Path, expected_revision: str | None) -> str:
    """Require a clean skill directory at the explicitly declared Git commit."""
    if expected_revision is None or not FULL_REVISION.fullmatch(expected_revision):
        raise ValueError("pinned comparisons require full candidate and baseline revision SHAs")
    try:
        actual = subprocess.run(
            ["git", "-C", str(skill_path), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ValueError(f"cannot verify skill snapshot revision: {skill_path}") from exc
    if actual.returncode or actual.stdout.strip() != expected_revision:
        raise ValueError(f"skill snapshot revision mismatch: {skill_path}")
    tracked_skill = subprocess.run(
        ["git", "-C", str(skill_path), "ls-files", "--error-unmatch", "--", "SKILL.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked_skill.returncode:
        raise ValueError(f"skill snapshot is not tracked at the declared revision: {skill_path}")
    status = subprocess.run(
        [
            "git",
            "-C",
            str(skill_path),
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--ignored=matching",
            "--",
            ".",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode:
        raise ValueError(f"cannot verify skill snapshot cleanliness: {skill_path}")
    if status.stdout.strip():
        raise ValueError(f"skill snapshot has changed or untracked files: {skill_path}")
    return expected_revision


def _load_baseline_reference_map(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "cases"}:
        raise ValueError("baseline reference map must contain schema_version and cases")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("unsupported baseline reference map version")
    if not isinstance(data["cases"], dict):
        raise ValueError("baseline reference map cases must be an object")
    references_by_case: dict[str, dict[str, str]] = {}
    for case_id, references in data["cases"].items():
        validate_case_id(case_id)
        validate_references(references)
        references_by_case[case_id] = references
    return references_by_case


def _snapshot_input_record(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "condition": metadata["condition"],
        "context_sha256": metadata.get("context_sha256"),
        "sources": metadata["sources"],
    }


def run_paired_trial(
    adapter: HarnessAdapter,
    case: EvalCase,
    skill_path: Path,
    output_dir: Path,
    model: str,
    model_label: str | None = None,
    request_limits: dict[str, Any] | None = None,
    *,
    comparison_mode: str = "skill_vs_no_skill",
    baseline_skill_path: Path | None = None,
    comparison_policy: str | None = None,
    candidate_revision: str | None = None,
    baseline_revision: str | None = None,
    baseline_reference_map: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Run one case in candidate and baseline conditions, grade, and compare."""
    if comparison_mode not in COMPARISON_MODES:
        raise ValueError("unsupported paired comparison mode")
    if comparison_mode == "pinned_skill_vs_skill":
        if comparison_policy not in COMPARISON_POLICIES:
            raise ValueError("pinned comparisons require --comparison-policy")
        if baseline_skill_path is None:
            raise ValueError("pinned_skill_vs_skill requires --baseline-skill-path")
        candidate_revision = _verify_snapshot_revision(skill_path, candidate_revision)
        baseline_revision = _verify_snapshot_revision(baseline_skill_path, baseline_revision)
    else:
        if baseline_skill_path is not None:
            raise ValueError("skill_vs_no_skill does not accept a baseline skill snapshot")
        if comparison_policy is not None or candidate_revision or baseline_revision:
            raise ValueError("comparison policy and snapshot revisions require a pinned comparison")
        if baseline_reference_map:
            raise ValueError("a baseline reference map requires a pinned comparison")
        comparison_policy = "no_skill_diagnostic"

    baseline_reference_map = baseline_reference_map or {}
    candidate_cases = _snapshot_cases(skill_path)
    candidate_snapshot_case = next(
        (snapshot_case for snapshot_case in candidate_cases if snapshot_case.id == case.id), None
    )
    if comparison_mode == "pinned_skill_vs_skill" and candidate_snapshot_case is None:
        raise ValueError(f"candidate snapshot has no matching eval case: {case.id}")
    candidate_case = replace(
        case,
        skill_references=(
            candidate_snapshot_case.skill_references
            if candidate_snapshot_case is not None
            else case.skill_references
        ),
    )

    candidate_contract = load_evidence_contracts(skill_path, candidate_cases).get(case.id)
    baseline_case = case
    if comparison_mode == "pinned_skill_vs_skill":
        assert baseline_skill_path is not None
        if comparison_policy == "instruction_only":
            candidate_case = replace(candidate_case, skill_references={})
            baseline_case = replace(case, skill_references={})
        else:
            baseline_cases = _snapshot_cases(baseline_skill_path)
            baseline_snapshot_case = next(
                (snapshot_case for snapshot_case in baseline_cases if snapshot_case.id == case.id),
                None,
            )
            if case.id in baseline_reference_map:
                baseline_references = baseline_reference_map[case.id]
                validate_references(baseline_references)
            elif baseline_snapshot_case is not None:
                baseline_references = baseline_snapshot_case.skill_references
            else:
                raise ValueError(
                    "complete_package comparison requires a matching baseline eval case "
                    "or an explicit baseline reference map"
                )
            baseline_case = replace(case, skill_references=baseline_references)

    candidate_sandbox, baseline_sandbox = stage_paired_sandboxes(
        skill_path,
        comparison_mode=comparison_mode,
        baseline_skill_path=baseline_skill_path,
    )
    limits = {"network_policy": "unspecified"}
    if request_limits is not None:
        limits.update(request_limits)

    try:
        if comparison_mode == "pinned_skill_vs_skill":
            assert baseline_skill_path is not None
            _verify_snapshot_revision(skill_path, candidate_revision)
            _verify_snapshot_revision(baseline_skill_path, baseline_revision)
        max_skill_chars = getattr(adapter, "max_skill_chars", None)
        _, candidate_preflight = build_context(
            candidate_sandbox, candidate_case.skill_references, max_skill_chars
        )
        _, baseline_preflight = build_context(
            baseline_sandbox, baseline_case.skill_references, max_skill_chars
        )

        trial_root = contained_path(output_dir, "runs", uuid.uuid4().hex)
        candidate_output_dir = contained_path(trial_root, "outputs", "candidate", case.id)
        baseline_output_dir = contained_path(trial_root, "outputs", "baseline", case.id)

        candidate_input = AdapterInput(
            skill_path=candidate_sandbox,
            case=candidate_case,
            work_dir=contained_path(trial_root, "work", "candidate", case.id),
            output_dir=candidate_output_dir,
            model=model,
            permissions={"skill_readonly": True, "grader_visible": False},
            limits=dict(limits),
            harness_config={
                "comparison_mode": comparison_mode,
                "comparison_policy": comparison_policy,
                "arm": "candidate",
                "pair_id": trial_root.name,
                "snapshot_revision": candidate_revision,
                **(
                    {"preflight_context_sha256": candidate_preflight["context_sha256"]}
                    if candidate_preflight.get("context_sha256")
                    else {}
                ),
                **(
                    {
                        "evidence_contract_sha256": candidate_contract["evidence_contract_sha256"],
                        "oracle_type": candidate_contract["oracle_type"],
                    }
                    if candidate_contract
                    else {}
                ),
            },
        )

        baseline_input = AdapterInput(
            skill_path=baseline_sandbox,
            case=baseline_case,
            work_dir=contained_path(trial_root, "work", "baseline", case.id),
            output_dir=baseline_output_dir,
            model=model,
            permissions={
                "skill_readonly": baseline_skill_path is not None,
                "grader_visible": False,
            },
            limits=dict(limits),
            harness_config={
                "comparison_mode": comparison_mode,
                "comparison_policy": comparison_policy,
                "arm": "baseline",
                "pair_id": trial_root.name,
                "snapshot_revision": baseline_revision,
                **(
                    {"preflight_context_sha256": baseline_preflight["context_sha256"]}
                    if baseline_preflight.get("context_sha256")
                    else {}
                ),
                **(
                    {
                        "evidence_contract_sha256": candidate_contract["evidence_contract_sha256"],
                        "oracle_type": candidate_contract["oracle_type"],
                    }
                    if candidate_contract
                    else {}
                ),
            },
        )

        c_started = datetime.now(timezone.utc)
        candidate_result = adapter.execute(candidate_input)
        c_finished = datetime.now(timezone.utc)

        b_started = datetime.now(timezone.utc)
        baseline_result = adapter.execute(baseline_input)
        b_finished = datetime.now(timezone.utc)

        reported_model = model_label or model
        candidate_manifest = build_manifest(
            adapter_name=adapter.name,
            adapter_version=adapter.version,
            harness_name=adapter.name,
            harness_version=adapter.version,
            model_provider="unspecified" if not reported_model else reported_model.split("/")[0],
            model_id=reported_model or "unspecified",
            adapter_input=candidate_input,
            adapter_output=candidate_result,
            started_at=c_started,
            finished_at=c_finished,
        )

        baseline_manifest = build_manifest(
            adapter_name=adapter.name,
            adapter_version=adapter.version,
            harness_name=adapter.name,
            harness_version=adapter.version,
            model_provider="unspecified" if not reported_model else reported_model.split("/")[0],
            model_id=reported_model or "unspecified",
            adapter_input=baseline_input,
            adapter_output=baseline_result,
            started_at=b_started,
            finished_at=b_finished,
        )

        manifests_dir = contained_path(output_dir, "manifests")
        write_manifest(candidate_manifest, manifests_dir)
        write_manifest(baseline_manifest, manifests_dir)

        candidate_grade = grade_output(case.id, case.assertions, candidate_result)
        baseline_grade = grade_output(case.id, case.assertions, baseline_result)

        report = build_comparison_report(
            skill_name=skill_path.name,
            case_id=case.id,
            candidate_grade=candidate_grade,
            baseline_grade=baseline_grade,
            candidate_manifest=candidate_manifest,
            baseline_manifest=baseline_manifest,
            comparison_mode=comparison_mode,
            comparison_policy=comparison_policy,
            snapshot_revisions={
                "candidate": candidate_revision,
                "baseline": baseline_revision,
            },
            snapshot_inputs={
                "candidate": _snapshot_input_record(candidate_preflight),
                "baseline": _snapshot_input_record(baseline_preflight),
            },
        )

        write_comparison_report(report, contained_path(output_dir, "reports"))

        return report

    finally:
        try:
            cleanup_sandbox(candidate_sandbox)
        finally:
            cleanup_sandbox(baseline_sandbox)


def run_paired_evaluation(
    adapter: HarnessAdapter,
    cases: list[EvalCase],
    skill_path: Path,
    output_dir: Path,
    model: str,
    model_label: str | None = None,
    request_limits: dict[str, Any] | None = None,
    *,
    comparison_mode: str = "skill_vs_no_skill",
    baseline_skill_path: Path | None = None,
    comparison_policy: str | None = None,
    candidate_revision: str | None = None,
    baseline_revision: str | None = None,
    baseline_reference_map: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """Run paired trials until complete or the first infrastructure failure."""
    reports = []
    for case in cases:
        report = run_paired_trial(
            adapter,
            case,
            skill_path,
            output_dir,
            model,
            model_label,
            request_limits,
            comparison_mode=comparison_mode,
            baseline_skill_path=baseline_skill_path,
            comparison_policy=comparison_policy,
            candidate_revision=candidate_revision,
            baseline_revision=baseline_revision,
            baseline_reference_map=baseline_reference_map,
        )
        reports.append(report)
        if report["candidate"]["infra_error"] or report["baseline"]["infra_error"]:
            break
    return reports


def infrastructure_error_count(reports: list[dict[str, Any]]) -> int:
    """Count candidate and baseline trials that failed before producing output."""
    return sum(
        bool(report.get(side, {}).get("infra_error"))
        for report in reports
        for side in ("candidate", "baseline")
    )


def summarize_run(
    reports: list[dict[str, Any]],
    selected_case_count: int,
    selected_assertion_count: int | None = None,
) -> dict[str, Any]:
    """Summarize process completion and assertion coverage independently of verdicts."""
    reported = len(reports)
    candidate_assertions = sum(len(r.get("candidate", {}).get("assertions", [])) for r in reports)
    baseline_assertions = sum(len(r.get("baseline", {}).get("assertions", [])) for r in reports)
    candidate_resolved = sum(
        sum(
            a.get("verdict") in {"pass", "fail"}
            for a in r.get("candidate", {}).get("assertions", [])
        )
        for r in reports
    )
    baseline_resolved = sum(
        sum(
            a.get("verdict") in {"pass", "fail"}
            for a in r.get("baseline", {}).get("assertions", [])
        )
        for r in reports
    )
    if selected_assertion_count is None:
        selected_assertion_count = max(candidate_assertions, baseline_assertions)
    triage_complete = (
        selected_case_count > 0
        and reported == selected_case_count
        and infrastructure_error_count(reports) == 0
    )
    candidate_verdicts = [
        r.get("candidate", {}).get("semantic_verdict", "not_assessed") for r in reports
    ]
    both_sides_assessed = all(
        r.get(side, {}).get("evidence_complete") is True
        and r.get(side, {}).get("semantic_verdict") in {"pass", "fail"}
        for r in reports
        for side in ("candidate", "baseline")
    )
    strict_gate_status = (
        "HOLD"
        if not triage_complete or any(v == "not_assessed" for v in candidate_verdicts)
        else "FAIL"
        if any(v == "fail" for v in candidate_verdicts)
        else "PASS"
    )
    return {
        "selected_case_count": selected_case_count,
        "reported_case_count": reported,
        "skipped_case_count": max(0, selected_case_count - reported),
        "candidate_assertion_count": candidate_assertions,
        "candidate_resolved_assertion_count": candidate_resolved,
        "baseline_assertion_count": baseline_assertions,
        "baseline_resolved_assertion_count": baseline_resolved,
        "selected_assertion_count": selected_assertion_count,
        "triage_complete": triage_complete,
        "strict_gate_status": strict_gate_status,
        "paired_comparison_complete": triage_complete and both_sides_assessed,
    }


def main() -> int:
    import argparse

    from .cli_adapter import CliSubprocessAdapter
    from .fake_adapter import FakeAdapter
    from .runner import load_cases, resolve_skill_path

    parser = argparse.ArgumentParser(
        prog="eval-paired",
        description="Run paired candidate vs baseline skill evaluations.",
    )
    parser.add_argument("manifest", type=Path, help="path to an evals.json manifest")
    parser.add_argument("--adapter", choices=["fake", "cli", "openai"], default="fake")
    parser.add_argument("--output-dir", type=Path, default=Path("eval-output-paired"))
    parser.add_argument("--model", default="")
    parser.add_argument(
        "--model-label",
        default=None,
        help="logical model label recorded in artifacts (defaults to --model)",
    )
    parser.add_argument("--case", dest="case_id", default=None)
    parser.add_argument(
        "--comparison-mode",
        choices=sorted(COMPARISON_MODES),
        default="skill_vs_no_skill",
        help="label a no-skill diagnostic or compare two pinned skill snapshots",
    )
    parser.add_argument(
        "--baseline-skill-path",
        type=Path,
        help="old skill snapshot for --comparison-mode pinned_skill_vs_skill",
    )
    parser.add_argument(
        "--comparison-policy",
        choices=sorted(COMPARISON_POLICIES),
        help="compare the full package with each arm's references or SKILL.md instructions only",
    )
    parser.add_argument(
        "--candidate-revision",
        help="full Git commit SHA expected for the candidate skill snapshot",
    )
    parser.add_argument(
        "--baseline-revision",
        help="full Git commit SHA expected for the baseline skill snapshot",
    )
    parser.add_argument(
        "--baseline-reference-map",
        type=Path,
        help="versioned JSON map of case-specific reference paths and hashes from the baseline snapshot",
    )
    parser.add_argument("--command", default=None)
    parser.add_argument("--prompt-mode", default="stdin", choices=["stdin", "arg"])
    parser.add_argument("--prompt-flag", default="--prompt")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--extra-args", default=None)
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible API base URL")
    parser.add_argument("--api-key", default=None, help="API key (optional)")
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument(
        "--max-skill-chars", type=int, default=None, help="truncate skill content to N chars"
    )
    parser.add_argument(
        "--no-thinking", action="store_true", help="disable thinking/reasoning mode (llama.cpp)"
    )
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    if not manifest_path.is_file():
        print(f"error: manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    cases = load_cases(manifest_path)
    if not cases:
        print(f"error: no cases found in {manifest_path}", file=sys.stderr)
        return 2

    if args.case_id:
        cases = [c for c in cases if c.id == args.case_id]
        if not cases:
            print(f"error: case '{args.case_id}' not found", file=sys.stderr)
            return 2

    skill_path = resolve_skill_path(manifest_path)
    if args.comparison_mode == "pinned_skill_vs_skill" and args.baseline_skill_path is None:
        parser.error("--baseline-skill-path is required for pinned_skill_vs_skill")
    if args.comparison_mode == "pinned_skill_vs_skill":
        if args.comparison_policy is None:
            parser.error("--comparison-policy is required for pinned_skill_vs_skill")
        if args.candidate_revision is None or args.baseline_revision is None:
            parser.error(
                "--candidate-revision and --baseline-revision are required for pinned comparisons"
            )
        if args.baseline_reference_map and args.comparison_policy != "complete_package":
            parser.error("--baseline-reference-map requires complete_package comparison policy")
    if args.comparison_mode == "skill_vs_no_skill" and args.baseline_skill_path is not None:
        parser.error("--baseline-skill-path requires pinned_skill_vs_skill mode")
    if args.comparison_mode == "skill_vs_no_skill" and any(
        value is not None
        for value in (
            args.comparison_policy,
            args.candidate_revision,
            args.baseline_revision,
            args.baseline_reference_map,
        )
    ):
        parser.error("snapshot policy and revisions require pinned_skill_vs_skill mode")

    try:
        baseline_reference_map = _load_baseline_reference_map(
            args.baseline_reference_map.resolve() if args.baseline_reference_map else None
        )
    except (OSError, ValueError) as exc:
        print(f"error: invalid baseline reference map: {exc}", file=sys.stderr)
        return 2
    if set(baseline_reference_map) - {case.id for case in cases}:
        print("error: baseline reference map contains an unselected case ID", file=sys.stderr)
        return 2

    if args.adapter == "fake":
        adapter: HarnessAdapter = FakeAdapter()
    elif args.adapter == "cli":
        if not args.command:
            print("error: --command required for cli adapter", file=sys.stderr)
            return 2
        import shlex

        command = shlex.split(args.command)
        adapter = CliSubprocessAdapter(
            command,
            prompt_mode=args.prompt_mode,
            prompt_flag=args.prompt_flag,
            timeout_seconds=args.timeout,
            extra_args=args.extra_args.split() if args.extra_args else [],
        )
    elif args.adapter == "openai":
        if not args.base_url:
            print("error: --base-url required for openai adapter", file=sys.stderr)
            return 2
        if not args.model:
            print("error: --model required for openai adapter", file=sys.stderr)
            return 2
        from .openai_adapter import OpenAICompatAdapter

        adapter = OpenAICompatAdapter(
            base_url=args.base_url,
            model=args.model,
            max_tokens=args.max_tokens,
            timeout_seconds=args.timeout,
            api_key=args.api_key,
            max_skill_chars=args.max_skill_chars,
            chat_template_kwargs={"enable_thinking": False} if args.no_thinking else None,
        )
    else:
        print(f"error: unknown adapter '{args.adapter}'", file=sys.stderr)
        return 2

    output_dir = args.output_dir.resolve()

    request_limits: dict[str, Any] = {"timeout_seconds": args.timeout}
    if args.adapter == "openai":
        request_limits["max_output_tokens"] = args.max_tokens

    print(f"paired evaluation: {skill_path.name}")
    print(f"adapter: {adapter.name} v{adapter.version}")
    print(f"cases:   {len(cases)}")
    print(f"output:  {output_dir}")
    print()

    selected_case_count = len(cases)
    reports = run_paired_evaluation(
        adapter,
        cases,
        skill_path,
        output_dir,
        args.model,
        args.model_label,
        request_limits,
        comparison_mode=args.comparison_mode,
        baseline_skill_path=args.baseline_skill_path,
        comparison_policy=args.comparison_policy,
        candidate_revision=args.candidate_revision,
        baseline_revision=args.baseline_revision,
        baseline_reference_map=baseline_reference_map,
    )

    improvements = 0
    regressions = 0
    for report in reports:
        print(format_comparison_summary(report))
        print()
        delta = report["paired_delta"]
        if delta == "candidate_improvement":
            improvements += 1
        elif delta == "candidate_regression":
            regressions += 1
    infrastructure_errors = infrastructure_error_count(reports)
    selected_assertion_count = sum(len(case.assertions) for case in cases)
    run_summary = summarize_run(reports, selected_case_count, selected_assertion_count)

    print(
        f"summary: {run_summary['reported_case_count']}/{run_summary['selected_case_count']} "
        f"case(s) reported, {run_summary['skipped_case_count']} skipped, "
        f"{improvements} improvement(s), "
        f"{regressions} regression(s), {infrastructure_errors} infrastructure error(s)"
    )
    print(
        "assertion coverage: "
        f"candidate {run_summary['candidate_resolved_assertion_count']}/"
        f"{run_summary['selected_assertion_count']} resolved "
        f"({run_summary['candidate_assertion_count']} observed); "
        f"baseline {run_summary['baseline_resolved_assertion_count']}/"
        f"{run_summary['selected_assertion_count']} resolved "
        f"({run_summary['baseline_assertion_count']} observed)"
    )
    print(f"triage status: {'complete' if run_summary['triage_complete'] else 'incomplete'}")
    print(f"strict candidate semantic gate: {run_summary['strict_gate_status']}")
    print(
        "paired comparison evidence: "
        f"{'complete' if run_summary['paired_comparison_complete'] else 'HOLD'}"
    )
    return 1 if regressions > 0 or infrastructure_errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
