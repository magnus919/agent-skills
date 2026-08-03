"""Tests for check-eval-overlap.py.

Covers: clean corpora (exit 0), exact-duplicate eval files (exit 1), partial
overlap above and below the threshold, JSON report shape, directory recursion,
token n-gram mode, the --shingle-size flag, missing-path errors, an empty eval
file, a training corpus too short to shingle, and --help.

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(SCRIPTS_DIR, "check-eval-overlap.py")

TRAIN_PARAGRAPH = (
    "The quick brown fox jumps over the lazy dog near the riverbank while the "
    "sun sets behind the mountains and the evening train crosses the old bridge."
)
EVAL_SENTENCE = (
    "The quick brown fox jumps over the lazy dog near the riverbank"
)
UNIQUE_FILLER = (
    "blueberry pancakes with maple syrup served at the corner cafe on tuesday "
    "morning while the radio played classical music and the barista practiced "
    "latte art with carefully steamed milk and a gentle hand."
)


def run_checker(args):
    proc = subprocess.run(
        [sys.executable, CHECKER, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TempCorpora(unittest.TestCase):
    """Per-test temporary train/ and eval/ directories."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.train = os.path.join(self.root, "train")
        self.eval_dir = os.path.join(self.root, "eval")
        os.makedirs(self.train)
        os.makedirs(self.eval_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def write_train(self, name, content):
        path = os.path.join(self.train, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def write_eval(self, name, content):
        path = os.path.join(self.eval_dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path


class TestOverlapDetection(TempCorpora):
    def test_help_exits_zero(self):
        rc, stdout, _ = run_checker(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("overlap", stdout)

    def test_clean_corpora_exit_zero(self):
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        self.write_eval("eval.txt", UNIQUE_FILLER)
        rc, stdout, _ = run_checker(["--train", self.train, "--eval", self.eval_dir])
        self.assertEqual(rc, 0)
        self.assertIn("No leakage", stdout)
        self.assertIn("ok", stdout)

    def test_exact_duplicate_flags_leak(self):
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        self.write_eval("eval.txt", TRAIN_PARAGRAPH)
        rc, stdout, _ = run_checker(["--train", self.train, "--eval", self.eval_dir])
        self.assertEqual(rc, 1)
        self.assertIn("LEAK", stdout)
        self.assertIn("Leakage detected in 1", stdout)

    def test_partial_overlap_above_threshold_flags_leak(self):
        # Eval reuses the whole train sentence (53 shingles) plus ~210 chars of
        # unique filler, so overlap is roughly 20% and must be flagged.
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        self.write_eval("eval.txt", EVAL_SENTENCE + " " + UNIQUE_FILLER[:210])
        rc, stdout, _ = run_checker(["--train", self.train, "--eval", self.eval_dir])
        self.assertEqual(rc, 1)
        self.assertIn("LEAK", stdout)

    def test_overlap_below_threshold_clean(self):
        # Eval reuses one sentence (~54 shingles) plus unique filler (~210
        # shingles), for roughly 20-25% overlap. A raised threshold must accept
        # it; the default threshold flags the same input (see the partial-overlap
        # test above).
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        self.write_eval("eval.txt", EVAL_SENTENCE + " " + UNIQUE_FILLER)
        rc, stdout, _ = run_checker(
            ["--train", self.train, "--eval", self.eval_dir, "--max-overlap-fraction", "0.30"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("No leakage", stdout)


class TestOverlapCli(TempCorpora):
    def test_json_report_shape(self):
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        self.write_eval("eval.txt", TRAIN_PARAGRAPH)
        rc, stdout, _ = run_checker(
            ["--train", self.train, "--eval", self.eval_dir, "--json"]
        )
        self.assertEqual(rc, 1)
        report = json.loads(stdout)
        self.assertEqual(report["tool"], "check-eval-overlap.py")
        self.assertEqual(report["train_files"], 1)
        self.assertEqual(report["eval_files"], 1)
        self.assertEqual(len(report["leaked"]), 1)
        entry = report["files"][0]
        self.assertEqual(entry["verdict"], "LEAK")
        self.assertAlmostEqual(entry["fraction"], 1.0, places=4)
        self.assertGreater(entry["shared"], 0)

    def test_directory_recursion(self):
        nested = os.path.join(self.train, "nested")
        os.makedirs(nested)
        with open(os.path.join(nested, "corpus.txt"), "w", encoding="utf-8") as handle:
            handle.write(TRAIN_PARAGRAPH)
        self.write_eval("eval.txt", TRAIN_PARAGRAPH)
        rc, _, _ = run_checker(["--train", self.train, "--eval", self.eval_dir])
        self.assertEqual(rc, 1)

    def test_multiple_eval_files_partial_leak(self):
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        self.write_eval("clean.txt", UNIQUE_FILLER)
        self.write_eval("duplicate.txt", TRAIN_PARAGRAPH)
        rc, stdout, _ = run_checker(["--train", self.train, "--eval", self.eval_dir])
        self.assertEqual(rc, 1)
        self.assertIn("Leakage detected in 1 of 2", stdout)

    def test_token_ngram_mode(self):
        tokens = "alpha beta gamma delta epsilon"
        self.write_train("train.txt", tokens)
        self.write_eval("eval.txt", tokens)
        rc, stdout, _ = run_checker(
            ["--train", self.train, "--eval", self.eval_dir, "--token-ngram", "3"]
        )
        self.assertEqual(rc, 1)
        self.assertIn("token-3", stdout)

    def test_shingle_size_flag(self):
        # A short shared word is invisible at size 8 but flagged at size 4.
        self.write_train("train.txt", "zebra crossing")
        self.write_eval("eval.txt", "zebra")
        rc_default, _, _ = run_checker(["--train", self.train, "--eval", self.eval_dir])
        rc_small, stdout, _ = run_checker(
            ["--train", self.train, "--eval", self.eval_dir, "--shingle-size", "4"]
        )
        self.assertEqual(rc_default, 0)
        self.assertEqual(rc_small, 1)
        self.assertIn("LEAK", stdout)


class TestOverlapErrors(TempCorpora):
    def test_missing_path_exit_two(self):
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        rc, _, stderr = run_checker(
            ["--train", self.train, "--eval", os.path.join(self.root, "nope")]
        )
        self.assertEqual(rc, 2)
        self.assertIn("ERROR", stderr)

    def test_empty_eval_file_handled(self):
        self.write_train("train.txt", TRAIN_PARAGRAPH)
        self.write_eval("empty.txt", "")
        rc, _, _ = run_checker(["--train", self.train, "--eval", self.eval_dir])
        self.assertEqual(rc, 0)

    def test_train_corpus_too_short_exit_two(self):
        self.write_train("tiny.txt", "hi")
        self.write_eval("eval.txt", TRAIN_PARAGRAPH)
        rc, _, stderr = run_checker(["--train", self.train, "--eval", self.eval_dir])
        self.assertEqual(rc, 2)
        self.assertIn("no shingles", stderr)

    def test_missing_train_required_flag(self):
        rc, _, _ = run_checker(["--eval", self.eval_dir])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
