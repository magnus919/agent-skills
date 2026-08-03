"""Tests for bundle-budget-checker.py.

Covers: total and per-chunk budget enforcement, both input shapes (structured
chunks list and name->bytes mapping), human unit parsing (250KB, 1.5MB), --json
output, no-budget report mode, --help, and error paths (missing file, malformed
JSON, bad budget value).

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import suppress

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(SCRIPTS_DIR, "bundle-budget-checker.py")


def run_checker(args):
    cmd = [sys.executable, CHECKER, *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return proc.returncode, proc.stdout, proc.stderr


def write_report(data):
    """Write a JSON bundle report to a temp file; return its path."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as handle:
        json.dump(data, handle)
        path = handle.name
    return path


def cleanup(path):
    with suppress(OSError):
        os.unlink(path)


class TestBundleBudgetBudgets(unittest.TestCase):
    def test_within_total_budget(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 100000}]})
        try:
            rc, _, _ = run_checker([path, "--total", "250KB"])
            self.assertEqual(rc, 0)
        finally:
            cleanup(path)

    def test_over_total_budget(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 300000}]})
        try:
            rc, _, stderr = run_checker([path, "--total", "250KB"])
            self.assertEqual(rc, 1)
            self.assertIn("over budget", stderr)
        finally:
            cleanup(path)

    def test_over_chunk_budget(self):
        path = write_report(
            {"chunks": [{"name": "main.js", "size": 180000}, {"name": "vendor.js", "size": 90000}]}
        )
        try:
            rc, stdout, _ = run_checker([path, "--chunk", "120KB"])
            self.assertEqual(rc, 1)
            self.assertIn("main.js", stdout)
            self.assertIn("OVER", stdout)
        finally:
            cleanup(path)

    def test_all_chunks_within_chunk_budget(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 100000}]})
        try:
            rc, stdout, _ = run_checker([path, "--chunk", "200KB"])
            self.assertEqual(rc, 0)
            self.assertIn("OK", stdout)
        finally:
            cleanup(path)

    def test_total_and_chunk_combined(self):
        path = write_report(
            {"chunks": [{"name": "main.js", "size": 80000}, {"name": "vendor.js", "size": 80000}]}
        )
        try:
            # Within both budgets: total 160 KB <= 200 KB, each chunk <= 100 KB.
            rc_ok, _, _ = run_checker([path, "--total", "200KB", "--chunk", "100KB"])
            self.assertEqual(rc_ok, 0)
            # Over chunk budget but within total: one chunk over 100 KB.
            rc_chunk, _, _ = run_checker([path, "--total", "300KB", "--chunk", "75KB"])
            self.assertEqual(rc_chunk, 1)
            # Over total but within chunk budget.
            rc_total, _, _ = run_checker([path, "--total", "100KB", "--chunk", "100KB"])
            self.assertEqual(rc_total, 1)
        finally:
            cleanup(path)

    def test_no_budget_reports_only(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 180000}]})
        try:
            rc, stdout, _ = run_checker([path])
            self.assertEqual(rc, 0)
            self.assertIn("unset", stdout)
            self.assertIn("within budget", stdout)
        finally:
            cleanup(path)


class TestBundleBudgetFormats(unittest.TestCase):
    def test_mapping_input_shape(self):
        path = write_report({"main.js": 180000, "vendor.js": 90000})
        try:
            rc, stdout, _ = run_checker([path, "--total", "300KB"])
            self.assertEqual(rc, 0)
            self.assertIn("main.js", stdout)
            self.assertIn("vendor.js", stdout)
        finally:
            cleanup(path)

    def test_empty_chunks_list(self):
        path = write_report({"chunks": []})
        try:
            rc, stdout, _ = run_checker([path, "--total", "100KB"])
            self.assertEqual(rc, 0)
            self.assertIn("within budget", stdout)
        finally:
            cleanup(path)


class TestBundleBudgetParsing(unittest.TestCase):
    def test_unit_parsing_variants(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 1024}]})
        try:
            rc_ok, _, _ = run_checker([path, "--total", "1.5KB"])
            self.assertEqual(rc_ok, 0)
            rc_bin, _, _ = run_checker([path, "--total", "1KiB"])
            self.assertEqual(rc_bin, 0)
            rc_over, _, _ = run_checker([path, "--total", "512B"])
            self.assertEqual(rc_over, 1)
        finally:
            cleanup(path)

    def test_plain_byte_budget(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 512000}]})
        try:
            rc, _, _ = run_checker([path, "--total", "512000"])
            self.assertEqual(rc, 0)
        finally:
            cleanup(path)

    def test_mib_budget(self):
        path = write_report({"chunks": [{"name": "app.js", "size": 1500000}]})
        try:
            rc, _, _ = run_checker([path, "--total", "2MiB"])
            self.assertEqual(rc, 0)
        finally:
            cleanup(path)


class TestBundleBudgetCli(unittest.TestCase):
    def test_help_exits_zero(self):
        rc, stdout, _ = run_checker(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("budget", stdout)

    def test_json_output_parseable(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 300000}]})
        try:
            rc, stdout, _ = run_checker([path, "--total", "250KB", "--json"])
            self.assertEqual(rc, 1)
            report = json.loads(stdout)
            self.assertTrue(report["over_budget"])
            self.assertEqual(report["total"]["status"], "over")
            self.assertEqual(report["chunks"][0]["name"], "main.js")
        finally:
            cleanup(path)

    def test_json_within_budget(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 100000}]})
        try:
            rc, stdout, _ = run_checker([path, "--total", "250KB", "--json"])
            self.assertEqual(rc, 0)
            report = json.loads(stdout)
            self.assertFalse(report["over_budget"])
            self.assertEqual(report["chunks"][0]["status"], "ok")
        finally:
            cleanup(path)

    def test_missing_file_exit_two(self):
        rc, _, stderr = run_checker(["/nonexistent/report.json", "--total", "100KB"])
        self.assertEqual(rc, 2)
        self.assertIn("ERROR", stderr)

    def test_malformed_json_exit_two(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as handle:
            handle.write("{not json")
            path = handle.name
        try:
            rc, _, stderr = run_checker([path, "--total", "100KB"])
            self.assertEqual(rc, 2)
            self.assertIn("invalid JSON", stderr)
        finally:
            cleanup(path)

    def test_bad_budget_value_exit_two(self):
        path = write_report({"chunks": [{"name": "main.js", "size": 1000}]})
        try:
            rc, _, stderr = run_checker([path, "--total", "lots"])
            self.assertEqual(rc, 2)
            self.assertIn("cannot parse budget", stderr)
        finally:
            cleanup(path)

    def test_wrong_top_level_shape_exit_two(self):
        path = write_report(["main.js", "vendor.js"])
        try:
            rc, _, stderr = run_checker([path, "--total", "100KB"])
            self.assertEqual(rc, 2)
            self.assertIn("must be a JSON object", stderr)
        finally:
            cleanup(path)


if __name__ == "__main__":
    unittest.main()
