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
    def _install_fake_npx(self, tmp: str, report: dict) -> tuple[dict[str, str], Path]:
        root = Path(tmp)
        fake_bin = root / "bin"
        fake_bin.mkdir()
        capture = root / "delegate.json"
        fake_npx = fake_bin / "npx"
        fake_npx.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "with open(os.environ['PW_CAPTURE_FILE'], 'w', encoding='utf-8') as f:\n"
            "    json.dump({'args': sys.argv[1:], 'target': os.environ.get('PW_SMOKE_URL')}, f)\n"
            f"print({json.dumps(json.dumps(report))})\n",
            encoding="utf-8",
        )
        fake_npx.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
        env["PW_CAPTURE_FILE"] = str(capture)
        return env, capture

    def test_smoke_forwards_config_spec_and_cli_url_over_environment(self):
        report = {
            "stats": {"expected": 1, "unexpected": 0, "flaky": 0, "skipped": 0},
            "suites": [{"specs": [{
                "title": "visit page",
                "file": "e2e/home.spec.ts",
                "tests": [{
                    "title": "loads the target",
                    "status": "expected",
                    "annotations": [{"type": "pwrun-navigation", "description": "http://127.0.0.1:34567/"}],
                    "results": [{"status": "passed"}],
                }],
            }]}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            env, capture = self._install_fake_npx(tmp, report)
            env["PW_SMOKE_URL"] = "https://inherited.example"
            env["BASE_URL"] = "https://base.example"
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "smoke", "--json", "--config", "custom.config.ts",
                 "--spec", "e2e/home.spec.ts", "--url", "http://127.0.0.1:34567"],
                capture_output=True,
                text=True,
                cwd=tmp,
                env=env,
                timeout=30,
            )
            delegated = json.loads(capture.read_text(encoding="utf-8"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--config", delegated["args"])
        config_index = delegated["args"].index("--config")
        self.assertEqual(delegated["args"][config_index + 1], "custom.config.ts")
        self.assertIn("e2e/home.spec.ts", delegated["args"])
        self.assertEqual(delegated["target"], "http://127.0.0.1:34567")
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["requested_url"], "http://127.0.0.1:34567")
        self.assertEqual(payload["url_source"], "--url")
        evidence = payload["navigation_evidence"]
        self.assertTrue(evidence["verified"])
        self.assertTrue(evidence["requested_target_origin_observed"])
        self.assertEqual(evidence["observed"][0]["url"], "http://127.0.0.1:34567/")

    def test_smoke_environment_precedence_and_unverified_output(self):
        report = {"stats": {}, "suites": []}
        with tempfile.TemporaryDirectory() as tmp:
            env, capture = self._install_fake_npx(tmp, report)
            env["PW_SMOKE_URL"] = "https://smoke.example/path"
            env["BASE_URL"] = "https://base.example"
            for key, expected_url, expected_source in (
                (None, "https://smoke.example/path", "PW_SMOKE_URL environment"),
                ("PW_SMOKE_URL", "https://base.example", "BASE_URL environment"),
                ("BASE_URL", "http://localhost:3000", "pwrun default"),
            ):
                if key:
                    env.pop(key)
                proc = subprocess.run(
                    [sys.executable, str(SCRIPT), "smoke", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                    env=env,
                    timeout=30,
                )
                delegated = json.loads(capture.read_text(encoding="utf-8"))
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(delegated["target"], expected_url)
                payload = json.loads(proc.stdout)
                self.assertEqual(payload["requested_url"], expected_url)
                self.assertEqual(payload["url_source"], expected_source)
                self.assertFalse(payload["navigation_evidence"]["verified"])
                self.assertIsNone(payload["navigation_evidence"]["requested_target_origin_observed"])

    def test_smoke_reports_runtime_target_mismatch(self):
        report = {
            "stats": {"expected": 1, "unexpected": 0, "flaky": 0, "skipped": 0},
            "suites": [{"specs": [{
                "title": "visit another host",
                "file": "e2e/other.spec.ts",
                "tests": [{
                    "title": "loads an unrelated page",
                    "status": "expected",
                    "annotations": [{"type": "pwrun-navigation", "description": "https://elsewhere.example/"}],
                    "results": [{"status": "passed"}],
                }],
            }]}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            env, _ = self._install_fake_npx(tmp, report)
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "smoke", "--json", "--url", "https://target.example"],
                capture_output=True,
                text=True,
                cwd=tmp,
                env=env,
                timeout=30,
            )
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(payload["requested_url"], "https://target.example")
        self.assertTrue(payload["navigation_evidence"]["verified"])
        self.assertFalse(payload["navigation_evidence"]["requested_target_origin_observed"])
        self.assertEqual(payload["navigation_evidence"]["observed"][0]["url"], "https://elsewhere.example/")

    @unittest.skipUnless(shutil.which("node") is None, "node present; missing-toolchain path not exercised")
    def test_smoke_without_node_reports_missing_dependency(self):
        proc = run_script("smoke", "--json")
        self.assertEqual(proc.returncode, 127)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("node", payload["error"])
        self.assertEqual(payload["requested_url"], "http://localhost:3000")
        self.assertFalse(payload["navigation_evidence"]["verified"])

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
