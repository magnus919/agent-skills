"""Challenge leakage, verifier false positives, incomplete scans and privacy."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import specialization_audit as audit


def example(identity, group, prompt):
    return {
        "id": identity,
        "group_id": group,
        "source": {
            "uri": "local:reviewed",
            "revision": "immutable-source-id",
            "rights": "approved internal use",
        },
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "answer"},
        ],
    }


def receipts():
    cases = []
    for category in sorted(audit.CATEGORIES):
        incomplete = category in {"timeout", "infrastructure_error"}
        correct = category == "correct"
        cases.append(
            {
                "id": category,
                "category": category,
                "label": {"kind": "reference", "evidence": "reviewed challenge fixture"},
                "expected_correct": None if incomplete else correct,
                "execution_status": category if incomplete else "passed" if correct else "failed",
                "reward": 1 if correct else 0,
            }
        )
    return {
        "schema_version": 1,
        "verifier_sha256": "a" * 64,
        "suite_sha256": "b" * 64,
        "cases": cases,
    }


class SpecializationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def splits(self, rows=None):
        rows = rows or [
            example("a", "repo-a", "private first"),
            example("b", "repo-b", "private second"),
            example("c", "repo-c", "private third"),
        ]
        paths = {}
        for split, row in zip(("train", "development", "test"), rows, strict=True):
            path = self.root / (split + ".jsonl")
            path.write_text(json.dumps(row) + "\n")
            paths[split] = path
        return paths

    def reward_report(self, record):
        path = self.root / "receipt.json"
        path.write_text(json.dumps(record))
        return audit.reward_audit(path)

    def test_clean_is_not_behavioral_pass(self):
        report = audit.data_audit(self.splits())
        self.assertTrue(report["checks_clear"])
        self.assertEqual(report["behavior"], "not_assessed")

    def test_source_group_and_prompt_leak_despite_different_targets(self):
        rows = [
            example("a", "repo", "secret prompt"),
            example("b", "repo", "secret prompt"),
            example("c", "other", "third"),
        ]
        rows[1]["messages"][-1]["content"] = "different answer"
        report = audit.data_audit(self.splits(rows))
        self.assertEqual(
            {f["code"] for f in report["findings"]}, {"group_leakage", "prompt_overlap"}
        )
        self.assertNotIn("secret", json.dumps(report))

    def test_duplicate_ids_and_content(self):
        rows = [
            example("a", "repo-a", "p"),
            example("a", "repo-b", "p"),
            example("c", "repo-c", "q"),
        ]
        codes = {f["code"] for f in audit.data_audit(self.splits(rows))["findings"]}
        self.assertIn("duplicate_id", codes)
        self.assertIn("duplicate_content", codes)

    def test_unsupported_tools_and_missing_rights(self):
        for change in (
            lambda r: r["source"].pop("rights"),
            lambda r: r["messages"][0].update(tool_calls=[]),
        ):
            rows = [example("a", "a", "p"), example("b", "b", "q"), example("c", "c", "r")]
            change(rows[0])
            self.assertFalse(audit.data_audit(self.splits(rows))["checks_clear"])

    def test_scan_limit_and_empty_split(self):
        paths = self.splits()
        paths["train"].write_text(paths["train"].read_text() * 2)
        paths["test"].write_text("")
        codes = {f["code"] for f in audit.data_audit(paths, limit=1)["findings"]}
        self.assertIn("scan_limit", codes)
        self.assertIn("empty_split", codes)

    def test_reward_challenges_complete_but_not_executed(self):
        report = self.reward_report(receipts())
        self.assertTrue(report["checks_clear"])
        self.assertEqual(report["execution"], "not_performed")
        self.assertEqual(report["release"], "not_assessed")

    def test_false_positive_reward_and_missing_category(self):
        record = receipts()
        bad = next(c for c in record["cases"] if c["category"] == "incorrect")
        bad.update(execution_status="passed", reward=1)
        record["cases"] = [c for c in record["cases"] if c["category"] != "adversarial"]
        codes = {f["code"] for f in self.reward_report(record)["findings"]}
        self.assertTrue(
            {"false_acceptance", "reward_order_violation", "missing_challenge_category"} <= codes
        )

    def test_teacher_labels_and_nonfinite_rewards_rejected(self):
        for change in (
            lambda c: c["label"].update(kind="model_teacher"),
            lambda c: c.update(reward=float("nan")),
            lambda c: c.update(reward=True),
        ):
            record = receipts()
            change(record["cases"][0])
            self.assertFalse(self.reward_report(record)["checks_clear"])

    def test_timeout_is_not_wrong_answer_or_positive_reward(self):
        record = receipts()
        c = next(c for c in record["cases"] if c["category"] == "timeout")
        c.update(expected_correct=False, execution_status="failed")
        self.assertIn(
            "failure_misclassified", {f["code"] for f in self.reward_report(record)["findings"]}
        )

    def test_wrong_utf8_and_json_never_print_private_text(self):
        path = self.root / "broken.json"
        for raw in (b'{"private password":', b"\xffprivate password"):
            path.write_bytes(raw)
            result = audit.reward_audit(path)
            self.assertNotIn("password", json.dumps(result))
            self.assertFalse(result["checks_clear"])

    def test_cli_fails_under_optimized_python(self):
        path = self.root / "reward.json"
        record = receipts()
        record["cases"].pop()
        path.write_text(json.dumps(record))
        result = subprocess.run(
            [sys.executable, "-O", str(Path(audit.__file__)), "rewards", str(path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
