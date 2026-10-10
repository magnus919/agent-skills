#!/usr/bin/env python3
"""Deterministic tests for the terraform/scripts/tfops wrapper.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, mutation gate, state-file analysis). No terraform binary is
required. Run locally with:
`python3 -m unittest discover -s terraform/tests -p 'test_*.py'`.
The TERRAFORM environment variable can point at a fake binary for delegate-path
coverage.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "tfops"
FIXTURE = ROOT / "tests" / "fixtures" / "fixture-state.json"


def plan_json(*, resource_changes=None, resource_drift=None, **extra) -> str:
    payload = {"format_version": "1.0", "prior_state": {}, "errored": False}
    if resource_changes is not None:
        payload["resource_changes"] = resource_changes
    if resource_drift is not None:
        payload["resource_drift"] = resource_drift
    payload.update(extra)
    return json.dumps(payload)


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
    def test_missing_binary_reports_unchecked_guard(self):
        proc = run_script("apply", "--yes", "--plan", "unused.tfplan", "--json",
                          env_extra={"TERRAFORM": "/nonexistent/tfops-test-binary"})
        self.assertEqual(proc.returncode, 127)
        self.assertEqual(json.loads(proc.stdout)["guard"], "unchecked")

    def test_real_first_provisioning_plan_without_prior_state(self):
        fixture = ROOT / "tests/fixtures/terraform-1.13.3-first-plan.json"
        fake = FakeTerraformBinary()
        try:
            proc = run_script("apply", "--plan", fake.plan_path, "--yes", "--json",
                              env_extra={"TERRAFORM": fake.path,
                                         "FAKE_PLAN_JSON": fixture.read_text(),
                                         "FAKE_COMMAND_LOG": fake.command_log})
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        finally:
            fake.cleanup()

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

    def test_apply_requires_saved_plan_even_with_state_file(self):
        proc = run_script("apply", "--state", str(FIXTURE), "--yes", "--json")
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["guard"], "unchecked")
        self.assertIn("--plan", payload["error"])

    def test_apply_rejects_missing_or_invalid_guard_evidence(self):
        fake = FakeTerraformBinary()
        try:
            for value in ('{"format_version":"1.0","resource_changes":[]}', 'not json'):
                proc = run_script(
                    "apply", "--plan", fake.plan_path, "--yes", "--json",
                    env_extra={"TERRAFORM": fake.path, "FAKE_PLAN_JSON": value},
                )
                self.assertEqual(proc.returncode, 2)
                self.assertEqual(json.loads(proc.stdout)["guard"], "unchecked")
        finally:
            fake.cleanup()

    def test_apply_blocks_detected_drift_and_taint_by_default(self):
        fake = FakeTerraformBinary()
        plans = [
            plan_json(resource_changes=[], resource_drift=[{"address": "aws_instance.db"}]),
            plan_json(resource_changes=[{"address": "aws_instance.db", "action_reason": "replace_because_tainted"}], resource_drift=[]),
        ]
        try:
            for plan in plans:
                proc = run_script(
                    "apply", "--plan", fake.plan_path, "--yes", "--json",
                    env_extra={"TERRAFORM": fake.path, "FAKE_PLAN_JSON": plan, "FAKE_COMMAND_LOG": fake.command_log},
                )
                self.assertEqual(proc.returncode, 2)
                payload = json.loads(proc.stdout)
                self.assertEqual(payload["guard"], "checked")
                self.assertFalse(payload["ok"])
        finally:
            fake.cleanup()

    def test_apply_uses_exact_saved_plan_after_clean_guard(self):
        fake = FakeTerraformBinary()
        try:
            proc = run_script(
                "apply", "--plan", fake.plan_path, "--yes", "--json",
                env_extra={"TERRAFORM": fake.path, "FAKE_PLAN_JSON": plan_json(), "FAKE_COMMAND_LOG": fake.command_log},
            )
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["guard"], "checked")
        commands = Path(fake.command_log).read_text().splitlines()
        inspected = next(line.removeprefix("show:") for line in commands if line.startswith("show:"))
        applied = next(line.removeprefix("apply:") for line in commands if line.startswith("apply:"))
        self.assertEqual(inspected, applied)
        self.assertNotEqual(applied, fake.plan_path)
        self.assertNotIn("-auto-approve", payload["command"])

    def test_force_bypasses_findings_only_after_valid_plan_check(self):
        fake = FakeTerraformBinary()
        tainted = plan_json(resource_changes=[{"address": "aws_instance.db", "action_reason": "replace_because_tainted"}], resource_drift=[])
        try:
            proc = run_script(
                "apply", "--plan", fake.plan_path, "--yes", "--force", "--json",
                env_extra={"TERRAFORM": fake.path, "FAKE_PLAN_JSON": tainted, "FAKE_COMMAND_LOG": fake.command_log},
            )
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["guard"], "bypassed")
        self.assertEqual(payload["tainted"], ["aws_instance.db"])

    def test_clean_plan_with_omitted_empty_change_collections_is_valid(self):
        fake = FakeTerraformBinary()
        try:
            proc = run_script(
                "apply", "--plan", fake.plan_path, "--yes", "--json",
                env_extra={"TERRAFORM": fake.path, "FAKE_PLAN_JSON": plan_json(), "FAKE_COMMAND_LOG": fake.command_log},
            )
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["guard"], "checked")
        self.assertEqual(payload["drifted"], [])

    def test_plan_save_binds_refresh_and_apply_checks_exact_plan(self):
        fake = FakeTerraformBinary()
        output_plan = os.path.join(fake._dir, "reviewed.tfplan")
        try:
            proc = run_script(
                "plan", "--save-plan", output_plan, "--json",
                env_extra={"TERRAFORM": fake.path},
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            plan_payload = json.loads(proc.stdout)
            self.assertIn("-refresh=true", plan_payload["command"])
            metadata = json.loads(Path(output_plan + ".tfops.json").read_text())
            self.assertTrue(metadata["refresh_enabled"])
            self.assertEqual(metadata["sha256"], hashlib.sha256(Path(output_plan).read_bytes()).hexdigest())
            proc = run_script(
                "apply", "--plan", output_plan, "--yes", "--json",
                env_extra={"TERRAFORM": fake.path, "FAKE_PLAN_JSON": plan_json(), "FAKE_COMMAND_LOG": fake.command_log},
            )
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["guard"], "checked")
        commands = Path(fake.command_log).read_text().splitlines()
        inspected = next(line.removeprefix("show:") for line in commands if line.startswith("show:"))
        applied = next(line.removeprefix("apply:") for line in commands if line.startswith("apply:"))
        self.assertEqual(inspected, applied)
        self.assertNotEqual(applied, output_plan)

    def test_failed_plan_regeneration_invalidates_old_sidecar(self):
        fake = FakeTerraformBinary()
        try:
            proc = run_script(
                "plan", "--save-plan", fake.plan_path, "--json",
                env_extra={"TERRAFORM": fake.path, "FAKE_PLAN_EXIT": "1"},
            )
            self.assertEqual(proc.returncode, 1)
            json.loads(proc.stdout)
            self.assertFalse(Path(fake.plan_path + ".tfops.json").exists())
            proc = run_script(
                "apply", "--plan", fake.plan_path, "--yes", "--json",
                env_extra={"TERRAFORM": fake.path},
            )
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["guard"], "unchecked")

    def test_plan_sidecar_write_failure_emits_one_final_json_result(self):
        fake = FakeTerraformBinary()
        try:
            proc = run_script(
                "plan", "--save-plan", fake.plan_path, "--json",
                env_extra={"TERRAFORM": fake.path, "FAKE_SIDECAR_DIR": "1"},
            )
        finally:
            fake.cleanup()
        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["guard"], "unchecked")
        self.assertIn("could not bind saved plan", payload["error"])

    def test_apply_rejects_plan_hash_mismatch_and_missing_metadata(self):
        fake = FakeTerraformBinary()
        try:
            Path(fake.plan_path).write_text("modified")
            proc = run_script("apply", "--plan", fake.plan_path, "--yes", "--json", env_extra={"TERRAFORM": fake.path})
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["guard"], "unchecked")
        finally:
            fake.cleanup()

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
        self.plan_path = os.path.join(self._dir, "reviewed.tfplan")
        self.command_log = tempfile.mktemp(prefix="tfops-fake-commands-")
        with open(self.plan_path, "w", encoding="utf-8") as handle:
            handle.write("fake plan")
        with open(self.plan_path + ".tfops.json", "w", encoding="utf-8") as handle:
            json.dump({"schema_version": 1, "sha256": hashlib.sha256(b"fake plan").hexdigest(), "refresh_enabled": True}, handle)
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(
                "#!/usr/bin/env bash\n"
                "set -e\n"
                'if [ "$1" = "version" ]; then printf "Terraform v1.15.8 (fake)\\n"; exit 0; fi\n'
                'if [ "$1" = "validate" ]; then exit 0; fi\n'
                'if [ "$1" = "show" ]; then printf "show:%s\\n" "$3" >> "$FAKE_COMMAND_LOG"; printf "%s" "$FAKE_PLAN_JSON"; exit 0; fi\n'
                'if [ "$1" = "apply" ]; then for arg in "$@"; do last=$arg; done; printf "apply:%s\\n" "$last" >> "$FAKE_COMMAND_LOG"; exit 0; fi\n'
                'if [ "$1" = "plan" ]; then for arg in "$@"; do case "$arg" in -out=*) out="${arg#-out=}"; printf "fake plan" > "$out";; esac; done; if [ "${FAKE_SIDECAR_DIR:-}" = "1" ]; then mkdir "$out.tfops.json"; fi; printf "no changes\\n"; exit "${FAKE_PLAN_EXIT:-0}"; fi\n'
                'if [ "$1" = "import" ]; then exit 0; fi\n'
            )
        os.chmod(self.path, 0o755)

    def cleanup(self) -> None:
        shutil.rmtree(self._dir)


if __name__ == "__main__":
    unittest.main()
