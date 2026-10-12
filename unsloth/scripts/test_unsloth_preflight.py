"""Offline tests of data rejection, leakage checks, bounds, and CLI semantics."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("unsloth_preflight.py")
SPEC = importlib.util.spec_from_file_location("unsloth_preflight", SCRIPT)
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, name, rows):
        path = self.root / name
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    def test_clean_separate_text_splits(self):
        train = self.write("train", [{"text": "alpha"}])
        valid = self.write("valid", [{"text": "beta"}])
        result = preflight.audit(train, valid)
        self.assertTrue(result["ok"])
        self.assertEqual(result["overlap_unique_rows"], 0)
        self.assertEqual(result["tokenization"], "not_assessed")

    def test_metadata_does_not_hide_overlap_or_duplicates(self):
        train = self.write("train", [{"text": "same", "id": 1}, {"id": 2, "text": "same"}])
        valid = self.write("valid", [{"text": "same", "id": 3}])
        result = preflight.audit(train, valid)
        self.assertFalse(result["ok"])
        self.assertEqual(result["overlap_unique_rows"], 1)
        self.assertEqual(result["train"]["duplicate_rows"], 1)

    def test_valid_chat(self):
        row = {
            "messages": [
                {"role": "system", "content": "Be brief"},
                {"role": "user", "content": "2+3?"},
                {"role": "assistant", "content": "5"},
            ]
        }
        self.assertTrue(preflight.audit(self.write("train", [row]))["ok"])

    def test_rejects_unsupported_shapes(self):
        rows = [
            [],
            {},
            {"text": " "},
            {"text": "a", "messages": []},
            {"text": "a", "chosen": "b"},
            {"messages": [{"role": "user", "content": "no answer"}]},
            {"messages": [{"role": ["user"], "content": "a"}]},
            {"messages": [{"role": "assistant", "content": [{"type": "image"}]}]},
            {"messages": [{"role": "assistant", "content": "x", "tool_calls": []}]},
        ]
        result = preflight.audit(self.write("train", rows))
        self.assertEqual(result["train"]["invalid_rows"], len(rows))
        self.assertFalse(result["ok"])

    def test_trailing_user_is_rejected(self):
        row = {
            "messages": [
                {"role": "assistant", "content": "x"},
                {"role": "user", "content": "unanswered"},
            ]
        }
        self.assertFalse(preflight.audit(self.write("train", [row]))["ok"])

    def test_malformed_json_does_not_echo_data(self):
        path = self.root / "private"
        path.write_text('private-secret-not-json\n{"text":"valid"}\n')
        result = preflight.audit(path)
        self.assertNotIn("private-secret", json.dumps(result))
        self.assertEqual(result["train"]["valid_rows"], 1)
        self.assertFalse(result["ok"])

    def test_rejects_duplicate_keys_and_nonfinite_json(self):
        path = self.root / "bad"
        path.write_text('{"text":"a","text":"b"}\n{"text":"a","score":NaN}\n')
        self.assertEqual(preflight.audit(path)["train"]["invalid_rows"], 2)

    def test_invalid_utf8(self):
        path = self.root / "bad"
        path.write_bytes(b"\xff\n")
        self.assertFalse(preflight.audit(path)["ok"])

    def test_empty_missing_and_directory_inputs_fail(self):
        for path in (self.write("empty", []), self.root / "missing", self.root):
            with self.subTest(path=path):
                self.assertFalse(preflight.audit(path)["ok"])

    def test_mixed_formats_fail(self):
        chat = {
            "messages": [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
        }
        train = self.write("train", [{"text": "a"}, chat])
        self.assertFalse(preflight.audit(train)["ok"])
        train = self.write("train", [{"text": "a"}])
        valid = self.write("valid", [chat])
        self.assertFalse(preflight.audit(train, valid)["split_formats_match"])

    def test_audit_limits_never_claim_complete(self):
        path = self.write("train", [{"text": "one"}, {"text": "two"}])
        for kwargs in ({"max_rows": 1}, {"max_line_bytes": 5}):
            report, _ = preflight.scan(path, **kwargs)
            self.assertFalse(report["complete"])
            self.assertGreater(report["issue_count"], 0)

    def test_error_details_are_bounded(self):
        report = preflight.audit(self.write("train", [{}] * 50))["train"]
        self.assertEqual(report["issue_count"], 50)
        self.assertEqual(len(report["issues"]), 30)

    def test_doctor_missing_packages_not_compatibility_success(self):
        with patch.object(
            preflight.importlib.metadata,
            "version",
            side_effect=preflight.importlib.metadata.PackageNotFoundError,
        ):
            result = preflight.doctor()
        self.assertTrue(all(value is None for value in result["packages"].values()))
        self.assertEqual(result["compatibility"], "not_assessed")
        self.assertEqual(result["gpu_execution"], "not_run")

    def test_cli_exit_codes_and_json(self):
        good = self.write("good", [{"text": "works"}])
        for args, code in (
            (["dataset", str(good), "--json"], 0),
            (["dataset", str(self.root / "missing"), "--json"], 1),
            (["doctor", "--json"], 0),
            ([], 2),
        ):
            run = subprocess.run(
                [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=10
            )
            self.assertEqual(run.returncode, code, run.stderr)
            if code != 2:
                self.assertEqual(json.loads(run.stdout)["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
