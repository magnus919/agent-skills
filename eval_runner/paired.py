"""Paired evaluation orchestrator.

Runs matched candidate and baseline trials in clean, isolated environments,
grades both with a deterministic verifier, and produces a case-level comparison
report. The candidate skill is staged read-only; the baseline has no skill.
Mutable state is reset for every trial.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .adapter import HarnessAdapter
from .comparison import build_comparison_report, format_comparison_summary, write_comparison_report
from .grader import grade_output
from .manifest import build_manifest, write_manifest
from .models import AdapterInput, EvalCase
from .path_safety import contained_path
from .sandbox import cleanup_sandbox, stage_paired_sandboxes


def run_paired_trial(
    adapter: HarnessAdapter,
    case: EvalCase,
    skill_path: Path,
    output_dir: Path,
    model: str,
    model_label: str | None = None,
) -> dict[str, Any]:
    """Run one case in candidate and baseline conditions, grade, and compare."""
    candidate_sandbox, baseline_sandbox = stage_paired_sandboxes(skill_path)

    try:
        candidate_output_dir = contained_path(output_dir, "candidate", case.id)
        baseline_output_dir = contained_path(output_dir, "baseline", case.id)

        candidate_input = AdapterInput(
            skill_path=candidate_sandbox,
            case=case,
            work_dir=contained_path(output_dir, "work", "candidate", case.id),
            output_dir=candidate_output_dir,
            model=model,
            permissions={"skill_readonly": True, "grader_visible": False},
            limits={"timeout_seconds": 120, "network_policy": "unspecified"},
        )

        baseline_input = AdapterInput(
            skill_path=baseline_sandbox,
            case=case,
            work_dir=contained_path(output_dir, "work", "baseline", case.id),
            output_dir=baseline_output_dir,
            model=model,
            permissions={"skill_readonly": False, "grader_visible": False},
            limits={"timeout_seconds": 120, "network_policy": "unspecified"},
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
) -> list[dict[str, Any]]:
    """Run all cases as paired trials and return comparison reports."""
    reports = []
    for case in cases:
        report = run_paired_trial(adapter, case, skill_path, output_dir, model, model_label)
        reports.append(report)
    return reports


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

    print(f"paired evaluation: {skill_path.name}")
    print(f"adapter: {adapter.name} v{adapter.version}")
    print(f"cases:   {len(cases)}")
    print(f"output:  {output_dir}")
    print()

    reports = run_paired_evaluation(
        adapter,
        cases,
        skill_path,
        output_dir,
        args.model,
        args.model_label,
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

    print(
        f"summary: {len(reports)} case(s), {improvements} improvement(s), {regressions} regression(s)"
    )
    return 1 if regressions > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
