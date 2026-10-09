"""Challenge provenance/rubric contract tests; semantic labels remain advisory."""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval_runner.grader import grade_output
from eval_runner.models import AdapterOutput, ExitStatus

ROOT = Path(__file__).resolve().parents[2]


def test_exact_fragments_and_canonical_assertions_preserved():
    data = json.loads(
        (Path(__file__).parent / "fixtures/business_agent_judge_challenges.json").read_text()
    )
    assert data["advisory_only"] is True
    assert len(data["challenges"]) == 2
    for challenge in data["challenges"]:
        cases = json.loads((ROOT / challenge["skill"] / "evals/evals.json").read_text())["evals"]
        case = next(c for c in cases if c["id"] == challenge["case_id"])
        assert challenge["assertion"] in case["assertions"]
        assert challenge["source"]["reviewer_kind"] == "model_teacher"
        assert challenge["source"]["advisory_verdict"] == "met"
        fragments = challenge["negative"]["verbatim_fragments"]
        for fragment in fragments:
            assert hashlib.sha256(fragment["text"].encode()).hexdigest() == fragment["sha256"]
        assert challenge["negative"]["verdict"] == "not_met"
        assert challenge["corrected"]["verdict"] == "met"
        assert challenge["missing"]["verdict"] == "not_shown"
        for text in [
            "\n\n".join(f["text"] for f in fragments),
            challenge["corrected"]["text"],
            challenge["missing"]["text"],
        ]:
            result = grade_output(
                case["id"],
                [challenge["assertion"]],
                AdapterOutput(ExitStatus.COMPLETED, response=text),
            )
            assert result.pass_count == 0
            assert result.fail_count == 0
            assert result.manual_count == 1


def test_sdd_output_flaw_fragments_have_source_provenance():
    data = json.loads(
        (Path(__file__).parent / "fixtures/business_agent_judge_challenges.json").read_text()
    )
    flaw = data["generated_output_flaws"][0]
    assert flaw["source"]["reviewer_kind"] == "model_teacher"
    assert len(flaw["source"]["response_sha256"]) == 64
    assert len(flaw["verbatim_fragments"]) == 3
    for fragment in flaw["verbatim_fragments"]:
        assert hashlib.sha256(fragment["text"].encode()).hexdigest() == fragment["sha256"]
