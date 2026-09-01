#!/usr/bin/env python3
"""Execute every canonical eval case with the deterministic fake adapter.

This checks runner plumbing and isolated output only. It deliberately does not
interpret fake responses as semantic grading evidence.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from eval_runner.fake_adapter import FakeAdapter  # noqa: E402
from eval_runner.models import AdapterInput, EvalCase, ExitStatus  # noqa: E402


def skills() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z", "**/SKILL.md"], cwd=ROOT).decode()
    return sorted(
        Path(path).parent
        for path in output.split("\0")
        if path and "/agent-council/profiles/skills/" not in path
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter = FakeAdapter()
    records = []
    failures = []
    skill_paths = skills()
    for skill in skill_paths:
        manifest = skill / "evals/evals.json"
        data = json.loads(manifest.read_text())
        for raw in data["evals"]:
            case = EvalCase(
                raw["id"],
                raw["prompt"],
                raw["expected_output"],
                raw["assertions"],
                raw.get("files", []),
                raw.get("case_set", "dev"),
            )
            result = adapter.execute(
                AdapterInput(
                    skill.resolve(),
                    case,
                    output_dir,
                    output_dir,
                    limits={"network_policy": "disabled"},
                )
            )
            ok = result.exit_status is ExitStatus.COMPLETED
            records.append(
                {
                    "skill": str(skill),
                    "case_id": case.id,
                    "status": result.exit_status.value,
                    "adapter": adapter.name,
                    "adapter_version": adapter.version,
                }
            )
            if not ok:
                failures.append(f"{skill}:{case.id}")
    report = {
        "runner": "all-canonical-fake-v1",
        "adapter": adapter.name,
        "adapter_version": adapter.version,
        "semantic_grading": "not_performed",
        "skill_count": len(skill_paths),
        "case_count": len(records),
        "failures": failures,
        "records": records,
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: report[key]
                for key in (
                    "runner",
                    "adapter",
                    "skill_count",
                    "case_count",
                    "failures",
                    "semantic_grading",
                )
            },
            indent=2,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
