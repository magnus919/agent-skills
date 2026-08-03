#!/usr/bin/env python3
"""Deterministic tests for the playwright/scripts/pwrun harness.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --help --json, doctor, inventory, report, smoke). No node or browser
is required: report analysis and inventory run on stdlib alone, and smoke
degrades gracefully when the Node toolchain is missing.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "pwrun"
FIXTURE = ROOT / "tests" / "fixtures" / "sample-report.json"


def run_script(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )


class HelpTests(unittest.TestCase):
    def test_help_exits_zero_and_advertises_json(self):
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        for command in ("doctor", "inventory", "report", "smoke"):
            self.assertIn(command, proc.stdout)

    def test_help_json_emits_parseable_json(self):
        proc = run_script("--help", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["name"], "pwrun")
        self.assertIn("--json", [flag["name"] for flag in payload["flags"]])

    def test_subcommand_help_exits_zero(self):
        for command in ("doctor", "inventory", "report", "smoke"):
            proc = run_script(command, "--help")
            self.assertEqual(proc.returncode, 0, command)
            self.assertIn("--json", proc.stdout)


class ReportTests(unittest.TestCase):
    def test_report_summarizes_fixture(self):
        proc = run_script("report", "--report", str(FIXTURE), "--json")
        self.assertEqual(proc.returncode, 1, proc.stderr)  # unexpected failures present
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["stats"]["expected"], 5)
        self.assertEqual(payload["stats"]["unexpected"], 1)
        self.assertEqual(payload["stats"]["skipped"], 1)
        self.assertEqual(len(payload["failures"]), 1)
        failure = payload["failures"][0]
        self.assertEqual(failure["title"], "completes the purchase with a saved card")
        self.assertIn("Place order", failure["error"])
        self.assertIn("5 expected, 1 unexpected", payload["summary"])

    def test_report_flag_survives_subcommand_position(self):
        # --report before the subcommand must survive argparse namespace merging.
        proc = run_script("--report", str(FIXTURE), "report", "--json")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["stats"]["unexpected"], 1)

    def test_report_requires_file(self):
        proc = run_script("report", "--json")
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertIn("--report", payload["error"])

    def test_report_rejects_non_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write("this is not json")
            bad_path = handle.name
        try:
            proc = run_script("report", "--report", bad_path, "--json")
        finally:
            os.unlink(bad_path)
        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)  # error path still emits parseable JSON
        self.assertFalse(payload["ok"])


class InventoryTests(unittest.TestCase):
    def test_inventory_describes_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "playwright.config.ts").write_text(
                "export default { projects: [ { name: 'chromium' }, { name: 'firefox' } ] };\n",
                encoding="utf-8",
            )
            (Path(tmp) / "e2e").mkdir()
            (Path(tmp) / "e2e" / "checkout.spec.ts").write_text("import { test } from '@playwright/test';\n", encoding="utf-8")
            proc = run_script("inventory", "--json", cwd=tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["config"], "playwright.config.ts")
        self.assertIn("chromium", payload["projects"])
        self.assertEqual(payload["spec_count"], 1)
        self.assertTrue(payload["specs"][0].endswith("e2e/checkout.spec.ts"))

    def test_inventory_no_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_script("inventory", "--json", cwd=tmp)
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIsNone(payload["config"])
        self.assertEqual(payload["spec_count"], 0)


class DoctorTests(unittest.TestCase):
    def test_doctor_emits_json_without_toolchain(self):
        proc = run_script("doctor", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("node_found", payload)
        self.assertIn("config", payload)
        self.assertIn("browsers_available", payload)

    def test_doctor_config_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "playwright.config.js").write_text("module.exports = {};\n", encoding="utf-8")
            proc = run_script("doctor", "--json", cwd=tmp)
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["config"], "playwright.config.js")


class SmokeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node") is None, "node present; missing-toolchain path not exercised")
    def test_smoke_without_node_reports_missing_dependency(self):
        proc = run_script("smoke", "--json")
        self.assertEqual(proc.returncode, 127)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("node", payload["error"])
        # The command parses without any extra flags; defaults are applied.
        self.assertIn("url", payload)

    @unittest.skipIf(shutil.which("node") is None, "node absent; delegate path not exercised")
    def test_smoke_with_node_emits_json_envelope(self):
        proc = run_script("smoke", "--json")
        # With node present but no guaranteed playwright install, the delegate
        # exits 0 (pass), 1 (playwright/npx error surfaced as JSON), or 124.
        self.assertIn(proc.returncode, (0, 1, 124))
        payload = json.loads(proc.stdout)
        self.assertIn("ok", payload)
        self.assertIn("command", payload)


if __name__ == "__main__":
    unittest.main()
