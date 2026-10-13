import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import nli_score_contract as nli


def fixture():
    return {
        "schema_version": 1,
        "model_revision": "a" * 40,
        "mode": "single_label",
        "candidate_labels": ["billing", "technical"],
        "nli_label_ids": {"contradiction": 0, "neutral": 1, "entailment": 2},
        "rows": [{"logits": [[0, 0, 2], [0, 0, 1]]}],
    }


class Tests(unittest.TestCase):
    def test_single_relative_scores(self):
        r = nli.score(fixture())
        self.assertAlmostEqual(sum(r["rows"][0]["scores_in_candidate_order"]), 1)
        self.assertEqual(r["rows"][0]["top_index"], 0)
        self.assertEqual(r["calibration"], "not_assessed")

    def test_independent_and_single_candidate_exception(self):
        x = fixture()
        x["mode"] = "multi_label"
        v = nli.score(x)["rows"][0]["scores_in_candidate_order"]
        self.assertGreater(sum(v), 1)
        x = fixture()
        x["candidate_labels"].pop()
        x["rows"][0]["logits"].pop()
        r = nli.score(x)
        self.assertLess(r["rows"][0]["scores_in_candidate_order"][0], 1)
        self.assertEqual(r["score_semantics"], "independent_entailment_vs_contradiction")

    def test_candidate_changes_existing_score(self):
        x = fixture()
        old = nli.score(x)["rows"][0]["scores_in_candidate_order"][0]
        x["candidate_labels"].append("other")
        x["rows"][0]["logits"].append([0, 0, 3])
        self.assertLess(nli.score(x)["rows"][0]["scores_in_candidate_order"][0], old)

    def test_mapping_permutation_and_neutral_warning(self):
        x = fixture()
        x["nli_label_ids"] = {"entailment": 0, "neutral": 1, "contradiction": 2}
        x["rows"][0]["logits"] = [[2, 0, 0], [1, 0, 0]]
        self.assertEqual(nli.score(x)["rows"], nli.score(fixture())["rows"])
        x = fixture()
        x["mode"] = "multi_label"
        x["rows"][0]["logits"][0] = [0, 100, 2]
        self.assertEqual(nli.score(x)["rows"][0]["neutral_argmax_pairs"], 1)

    def test_binary_head_without_invented_neutral(self):
        x = fixture()
        x["nli_label_ids"] = {"entailment": 0, "contradiction": 1}
        x["rows"][0]["logits"] = [[2, 0], [1, 0]]
        result = nli.score(x)
        self.assertEqual(
            result["rows"][0]["scores_in_candidate_order"],
            nli.score(fixture())["rows"][0]["scores_in_candidate_order"],
        )
        self.assertIsNone(result["rows"][0]["neutral_argmax_pairs"])

    def test_extreme_and_invalid_values(self):
        self.assertEqual(nli.softmax([10000, 10000]), [0.5, 0.5])
        for value in (float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                nli.softmax([0, value])
        for change in (
            lambda r: r.update(schema_version=True),
            lambda r: r["nli_label_ids"].update(entailment=0),
            lambda r: r.update(model_revision="latest"),
            lambda r: r["rows"][0]["logits"].pop(),
        ):
            x = fixture()
            change(x)
            with self.assertRaises(ValueError):
                nli.score(x)

    def test_cli_privacy_and_optimized_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            x = fixture()
            x["private_text"] = "secret context"
            x["model_revision"] = "latest"
            p.write_text(json.dumps(x))
            r = subprocess.run(
                [sys.executable, "-O", nli.__file__, str(p)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(r.returncode, 1)
            self.assertNotIn("secret context", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
