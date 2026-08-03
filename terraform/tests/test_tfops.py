#!/usr/bin/env python3
"""Deterministic tests for the terraform/scripts/tfops wrapper.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, mutation gate, state-file analysis). No terraform binary is
required; the TERRAFORM environment variable can point at a fake binary for
delegate-path coverage.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "tfops"
FIXTURE = ROOT / "tests" / "fixtures" / "fixture-state.json"


def run_script(*args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


class HelpTests(unittest.TestCase):
    def test_help_exits_zero_without_binary(self):
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        for flag in ("--dry-run", "--yes", "--force"):
            self.assertIn(flag, proc.stdout)

    def test_subcommand_help_exits_zero(self):
        for command in ("doctor", "validate", "plan", "apply", "state", "import"):
            proc = run_script(command, "--help")
            self.assertEqual(proc.returncode, 0, command)
            self.assertIn("--json", proc.stdout)


class StateAnalysisTests(unittest.TestCase):
    def test_plan_state_json_is_parseable(self):
        proc = run_script("plan", "--state", str(FIXTURE), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["plan"]["resource_count"], 4)
        self.assertEqual(payload["plan"]["managed_resources"], 3)
        self.assertEqual(payload["plan"]["data_resources"], 1)
        self.assertIn("module.vpc", payload["plan"]["modules"])
        self.assertEqual(payload["plan"]["tainted"], ["aws_instance.db"])

    def test_state_json_lists_resources(self):
        proc = run_script("state", "--state", str(FIXTURE), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["resource_count"], 4)
        addresses = {r["address"] for r in payload["resources"]}
        self.assertIn("module.vpc.aws_vpc.main", addresses)
        self.assertIn("aws_instance.web", addresses)

    def test_plan_rejects_non_state_file_as_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write("{\"not\": \"state\"}")
            bad_path = handle.name
        try:
            proc = run_script("plan", "--state", bad_path, "--json")
        finally:
            os.unlink(bad_path)
        self.assertEqual(proc.returncode, 1)
        json.loads(proc.stdout)  # error path still emits parseable JSON


class MutationGateTests(unittest.TestCase):
    def test_apply_requires_yes(self):
        proc = run_script("apply", "--state", str(FIXTURE), "--json")
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("--yes", payload["error"])

    def test_apply_dry_run_previews_without_mutating(self):
        proc = run_script("apply", "--state", str(FIXTURE), "--dry-run", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])

    def test_apply_taint_guard_refuses_without_force(self):
        proc = run_script("apply", "--state", str(FIXTURE), "--yes", "--json")
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertIn("tainted", payload["error"])
        self.assertEqual(payload["tainted"], ["aws_instance.db"])

    def test_apply_taint_guard_skipped_with_force(self):
        fake = FakeTerraformBinary()
        try:
            proc = run_script(
                "apply", "--state", str(FIXTURE), "--yes", "--force", "--json",
                env_extra={"TERRAFORM": fake.path},
            )
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn("apply", payload["command"])

    def test_import_requires_yes(self):
        proc = run_script("import", "aws_instance.web", "i-0abc123def456", "--json")
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertIn("--yes", payload["error"])

    def test_import_dry_run_previews(self):
        proc = run_script("import", "aws_instance.web", "i-0abc123def456", "--dry-run", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["dry_run"])


class DelegatePathTests(unittest.TestCase):
    def test_plan_without_state_requires_binary(self):
        proc = run_script("plan", "--json", env_extra={"TERRAFORM": "/nonexistent/tf"})
        self.assertEqual(proc.returncode, 127)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])

    def test_doctor_reports_missing_binary(self):
        proc = run_script("doctor", "--json", env_extra={"TERRAFORM": "/nonexistent/tf"})
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["binary_found"])

    def test_validate_delegates_to_fake_binary(self):
        fake = FakeTerraformBinary()
        try:
            proc = run_script("validate", "--json", env_extra={"TERRAFORM": fake.path})
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn("validate", " ".join(payload["command"]))


class FakeTerraformBinary:
    """A fake terraform binary that answers version/validate/apply/plan calls."""

    def __init__(self) -> None:
        self._dir = tempfile.mkdtemp(prefix="tfops-fake-")
        self.path = os.path.join(self._dir, "terraform")
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(
                "#!/usr/bin/env bash\n"
                "set -e\n"
                'printf "Terraform v1.15.8 (fake)\\n"\n'
                'if [ "$1" = "validate" ]; then exit 0; fi\n'
                'if [ "$1" = "apply" ]; then exit 0; fi\n'
                'if [ "$1" = "plan" ]; then printf "no changes\\n"; exit 0; fi\n'
                'if [ "$1" = "import" ]; then exit 0; fi\n'
            )
        os.chmod(self.path, 0o755)

    def cleanup(self) -> None:
        for entry in os.listdir(self._dir):
            os.unlink(os.path.join(self._dir, entry))
        os.rmdir(self._dir)


if __name__ == "__main__":
    unittest.main()
