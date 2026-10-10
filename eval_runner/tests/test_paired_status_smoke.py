"""Bounded, offline CLI smoke for unresolved semantic status reporting."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        skill = temp / "smoke-skill"
        evals = skill / "evals"
        evals.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: smoke-skill\n---\n# Smoke\n")
        manifest = evals / "evals.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "skill_name": "smoke-skill",
                    "evals": [
                        {
                            "id": "manual-status",
                            "prompt": "Give a bounded response.",
                            "expected_output": "A response that needs semantic review.",
                            "assertions": ["The response follows the intended policy."],
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        output_dir = temp / "paired-output"
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "eval_runner.paired",
                str(manifest),
                "--adapter",
                "fake",
                "--output-dir",
                str(output_dir),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        assert "adapter: fake" in completed.stdout
        assert "strict candidate semantic gate: HOLD" in completed.stdout
        assert "paired comparison evidence: HOLD" in completed.stdout

        reports = list((output_dir / "reports").glob("*.comparison.json"))
        assert len(reports) == 1
        report = json.loads(reports[0].read_text(encoding="utf-8"))
        assert report["paired_delta"] == "insufficient_evidence"
        for side in ("candidate", "baseline"):
            assert report[side]["semantic_verdict"] == "not_assessed"
            assert not report[side]["passed"]


if __name__ == "__main__":
    main()
    print("Offline paired status smoke passed.")
