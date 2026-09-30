"""Regression tests challenge safety and the scope of evidence claims."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("harness.py")
SPEC = importlib.util.spec_from_file_location("harness", SCRIPT)
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)


class HarnessTests(unittest.TestCase):
    def test_audit_never_claims_effectiveness(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("Everything passes!")
            result = harness.audit(root)
            self.assertEqual(result["behavior"], "not_assessed")
            self.assertEqual(result["causal_bottleneck"], "not_assessed")
            self.assertNotIn("overall", result)

    def test_preview_no_write(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "new"
            harness.scaffold(root, False)
            self.assertFalse(root.exists())

    def test_apply_preserves_existing_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("user work")
            (root / "handoff.md").symlink_to(root / "missing")
            harness.scaffold(root, True)
            self.assertEqual((root / "AGENTS.md").read_text(), "user work")
            self.assertTrue((root / "handoff.md").is_symlink())
            self.assertFalse((root / "missing").exists())
            self.assertEqual(
                json.loads((root / "harness-state.json").read_text())["tasks"][0]["status"],
                "pending",
            )

    def test_reapply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            harness.scaffold(root, True)
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            harness.scaffold(root, True)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_shell_string_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "checks.json"
            p.write_text('["echo ok; touch bad"]')
            with self.assertRaises(ValueError):
                harness.commands_from(p)

    def test_verify_preview_does_not_execute(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cmd = [sys.executable, "-c", "open('bad', 'w').write('ran')"]
            result = harness.verify(root, [cmd], False, 1)
            self.assertFalse(result["executed"])
            self.assertFalse((root / "bad").exists())

    def test_nonzero_stops_and_keeps_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            result = harness.verify(
                Path(d),
                [[sys.executable, "-c", "raise SystemExit(3)"], [sys.executable, "-c", "pass"]],
                True,
                2,
            )
            self.assertFalse(result["all_commands_exit_zero"])
            self.assertEqual(len(result["results"]), 1)
            self.assertEqual(result["results"][0]["returncode"], 3)

    def test_timeout_is_failure(self):
        with tempfile.TemporaryDirectory() as d:
            result = harness.verify(
                Path(d), [[sys.executable, "-c", "import time; time.sleep(10)"]], True, 0.05
            )
            self.assertEqual(result["results"][0]["status"], "timeout")
            self.assertFalse(result["all_commands_exit_zero"])

    def test_stub_is_not_acceptance_and_output_is_not_exposed(self):
        with tempfile.TemporaryDirectory() as d:
            result = harness.verify(Path(d), [[sys.executable, "-c", "print('SECRET')"]], True, 2)
            self.assertTrue(result["all_commands_exit_zero"])
            self.assertEqual(result["acceptance"], "not_assessed")
            self.assertNotIn("stdout", result["results"][0])
            self.assertFalse(result["feature_state_changed"])

    def test_existing_report_rejected_before_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            report = root / "report.json"
            report.write_text("preserve")
            commands = root / "checks.json"
            commands.write_text(
                json.dumps([[sys.executable, "-c", "open('bad','w').write('ran')"]])
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "verify",
                    "--target",
                    d,
                    "--commands",
                    str(commands),
                    "--execute",
                    "--report",
                    str(report),
                ],
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report.read_text(), "preserve")
            self.assertFalse((root / "bad").exists())

    def test_cli_failure_exit_and_report(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            commands = root / "checks.json"
            commands.write_text(json.dumps([[sys.executable, "-c", "raise SystemExit(5)"]]))
            report = root / "run.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "verify",
                    "--target",
                    d,
                    "--commands",
                    str(commands),
                    "--execute",
                    "--report",
                    str(report),
                ],
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(report.read_text())["results"][0]["returncode"], 5)

    def test_missing_executable_is_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            result = harness.verify(Path(d), [["/nonexistent/harness-tool"]], True, 1)
            self.assertEqual(result["results"][0]["status"], "launch_error")

    def test_output_limit_stops_without_raw_output(self):
        with tempfile.TemporaryDirectory() as d:
            result = harness.verify(
                Path(d), [[sys.executable, "-c", "print('X' * 500000)"]], True, 2, 128
            )
            outcome = result["results"][0]
            self.assertEqual(outcome["status"], "output_limit")
            self.assertFalse(outcome["output_complete"])
            self.assertEqual(sum(outcome["output_bytes"].values()), 128)
            self.assertFalse(result["all_commands_exit_zero"])

    def test_stdin_closed_for_noninteractive_checks(self):
        with tempfile.TemporaryDirectory() as d:
            result = harness.verify(Path(d), [[sys.executable, "-c", "input('prompt')"]], True, 2)
            self.assertEqual(result["results"][0]["status"], "failed")

    def test_checkpoint_records_current_and_finished_outcomes(self):
        with tempfile.TemporaryDirectory() as d:
            records = []

            def observe(record):
                records.append(json.loads(json.dumps(record)))

            result = harness.verify(
                Path(d), [[sys.executable, "-c", "pass"]], True, 2, checkpoint=observe
            )
            self.assertEqual(records[0]["execution_state"], "running")
            self.assertIn("current_command", records[1])
            self.assertEqual(records[-1]["results"][0]["status"], "exit_zero")
            self.assertEqual(result["execution_state"], "finished")

    def test_cli_html_escapes_content(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "<script>"
            root.mkdir()
            report = Path(d) / "audit.html"
            r = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "audit",
                    "--target",
                    str(root),
                    "--html",
                    str(report),
                ],
                capture_output=True,
            )
            self.assertEqual(r.returncode, 0)
            self.assertIn("&lt;script&gt;", report.read_text())
            self.assertNotIn("<script>", report.read_text())

    def test_cli_all_steps_and_atomic_report(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "project"
            scaffold = subprocess.run(
                [sys.executable, str(SCRIPT), "scaffold", "--target", str(root), "--apply"],
                capture_output=True,
            )
            self.assertEqual(scaffold.returncode, 0)
            commands = Path(d) / "checks.json"
            commands.write_text(json.dumps([[sys.executable, "-c", "raise SystemExit(0)"]]))
            report = Path(d) / "run.json"
            r = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "verify",
                    "--target",
                    str(root),
                    "--commands",
                    str(commands),
                    "--execute",
                    "--report",
                    str(report),
                ],
                capture_output=True,
            )
            self.assertEqual(r.returncode, 0)
            output = json.loads(report.read_text())
            self.assertEqual(output["execution_state"], "finished")
            self.assertEqual(output["acceptance"], "not_assessed")
            self.assertEqual(
                json.loads((root / "harness-state.json").read_text())["tasks"][0]["status"],
                "pending",
            )
            self.assertFalse(list(Path(d).glob(".harness-report-*")))


if __name__ == "__main__":
    unittest.main()
