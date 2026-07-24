"""Eval runner CLI — loads cases, dispatches to an adapter, writes manifests."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .adapter import HarnessAdapter
from .cli_adapter import CliSubprocessAdapter
from .fake_adapter import FakeAdapter
from .manifest import build_manifest, write_manifest
from .models import AdapterInput, EvalCase


def load_cases(manifest_path: Path) -> list[EvalCase]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases: list[EvalCase] = []
    for entry in data.get("evals", []):
        cases.append(
            EvalCase(
                id=entry["id"],
                prompt=entry["prompt"],
                expected_output=entry["expected_output"],
                assertions=entry.get("assertions", []),
                files=entry.get("files", []),
            )
        )
    return cases


def resolve_skill_path(manifest_path: Path) -> Path:
    return manifest_path.parent.parent


def build_adapter(args: argparse.Namespace) -> HarnessAdapter:
    if args.adapter == "fake":
        return FakeAdapter()
    if args.adapter == "cli":
        if not args.command:
            print("error: --command required for cli adapter", file=sys.stderr)
            raise SystemExit(2)
        import shlex

        command = shlex.split(args.command)
        return CliSubprocessAdapter(
            command,
            prompt_mode=args.prompt_mode,
            prompt_flag=args.prompt_flag,
            timeout_seconds=args.timeout,
            extra_args=args.extra_args.split() if args.extra_args else [],
        )
    print(f"error: unknown adapter '{args.adapter}'", file=sys.stderr)
    raise SystemExit(2)


def run_trial(
    adapter: HarnessAdapter,
    case: EvalCase,
    skill_path: Path,
    output_dir: Path,
    model: str,
) -> Path:
    work_dir = output_dir / "work" / case.id
    case_output_dir = output_dir / "trials" / case.id

    adapter_input = AdapterInput(
        skill_path=skill_path,
        case=case,
        work_dir=work_dir,
        output_dir=case_output_dir,
        model=model,
        limits={"timeout_seconds": 120, "network_policy": "unspecified"},
    )

    started_at = datetime.now(timezone.utc)
    result = adapter.execute(adapter_input)
    finished_at = datetime.now(timezone.utc)

    manifest = build_manifest(
        adapter_name=adapter.name,
        adapter_version=adapter.version,
        harness_name=adapter.name,
        harness_version=adapter.version,
        model_provider="unspecified" if not model else model.split("/")[0],
        model_id=model or "unspecified",
        adapter_input=adapter_input,
        adapter_output=result,
        started_at=started_at,
        finished_at=finished_at,
    )

    return write_manifest(manifest, output_dir / "manifests")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="eval-runner",
        description="Run eval cases against a candidate skill via a harness adapter.",
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="path to an evals.json manifest",
    )
    parser.add_argument(
        "--adapter",
        choices=["fake", "cli"],
        default="fake",
        help="adapter to use (default: fake)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("eval-output"),
        help="directory for run artifacts (default: eval-output)",
    )
    parser.add_argument(
        "--model",
        default="",
        help="model identifier (e.g. anthropic/claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--case",
        dest="case_id",
        default=None,
        help="run only this case ID",
    )
    parser.add_argument("--command", default=None, help="CLI command for cli adapter")
    parser.add_argument("--prompt-mode", default="stdin", choices=["stdin", "arg"])
    parser.add_argument("--prompt-flag", default="--prompt")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--extra-args", default=None)
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
    adapter = build_adapter(args)
    output_dir = args.output_dir.resolve()

    print(f"adapter: {adapter.name} v{adapter.version}")
    print(f"skill:   {skill_path.name}")
    print(f"cases:   {len(cases)}")
    print(f"output:  {output_dir}")
    print()

    failures = 0
    for case in cases:
        print(f"  [{case.id}] running...", end=" ", flush=True)
        manifest_file = run_trial(adapter, case, skill_path, output_dir, args.model)
        status = json.loads(manifest_file.read_text(encoding="utf-8"))["status"]
        if status == "completed":
            print(f"ok -> {manifest_file.name}")
        else:
            print(f"{status} -> {manifest_file.name}")
            failures += 1

    print()
    print(f"done: {len(cases)} trial(s), {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
