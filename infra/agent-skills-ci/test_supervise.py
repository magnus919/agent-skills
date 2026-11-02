"""Recovery boundaries for the host controller; no Docker daemon required."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("supervise", Path(__file__).with_name("supervise.py"))
supervise = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervise)


class RecoveryTests(unittest.TestCase):
    def test_runner_identity_accepts_actual_bom_format(self):
        actual = "\ufeff" + json.dumps({"agentId": 22, "agentName": "agent-skills-ci-saru"})
        self.assertEqual(supervise.parse_runner_id(actual), 22)

    def test_interrupted_registration_reconciles_only_own_pool(self):
        with patch.object(
            supervise,
            "api",
            side_effect=[
                {
                    "runners": [
                        {"id": 1, "name": "gpuslut01-agent-skills-eval"},
                        {"id": 2, "name": "agent-skills-ci-saru"},
                    ]
                },
                None,
            ],
        ) as api:
            supervise.reconcile(Path("unused"), "agent-skills-ci-saru")
            self.assertEqual(api.call_args.args, (Path("unused"), "/2", "DELETE"))
            self.assertEqual(api.call_count, 2)

    def test_old_worker_cleanup_precedes_missing_config_or_credentials(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch.object(supervise.Path, "home", return_value=root),
                patch.object(supervise, "cleanup") as cleanup,
                patch.object(supervise, "api") as api,
                patch.object(
                    sys,
                    "argv",
                    [
                        "supervise.py",
                        "--host",
                        "saru",
                        "--token-file",
                        str(root / "missing-token"),
                        "--deny-file",
                        str(root / "missing-config"),
                    ],
                ),
            ):
                with self.assertRaises(FileNotFoundError):
                    supervise.main()
                cleanup.assert_called_once_with(
                    "agent-skills-ci-saru", "agent-skills-ci-saru-network"
                )
                api.assert_not_called()

    def test_wrong_identity_is_never_deleted(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "identity"
            state.write_text("123")
            with patch.object(supervise, "api", return_value={"name": "gpu-evaluator"}) as api:
                with self.assertRaisesRegex(RuntimeError, "different runner"):
                    supervise.unregister(Path("unused"), state, "agent-skills-ci-saru")
                self.assertEqual(api.call_count, 1)
                self.assertTrue(state.exists())

    def test_failed_deletion_retains_recovery_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "identity"
            state.write_text("123")
            with patch.object(
                supervise,
                "api",
                side_effect=[{"name": "agent-skills-ci-saru"}, RuntimeError("API unavailable")],
            ):
                with self.assertRaisesRegex(RuntimeError, "API unavailable"):
                    supervise.unregister(Path("unused"), state, "agent-skills-ci-saru")
                self.assertEqual(state.read_text(), "123")

    def test_cleanup_failure_prevents_replacement(self):
        present = subprocess.CompletedProcess([], 0)
        still_present = subprocess.CompletedProcess([], 0, stdout="container-id\n")
        with (
            patch.object(supervise.subprocess, "run", return_value=present),
            patch.object(supervise, "docker", side_effect=[present, still_present]),
            self.assertRaisesRegex(RuntimeError, "cleanup not confirmed"),
        ):
            supervise.cleanup("worker", "guard")

    def test_private_or_missing_external_address_fails_closed(self):
        with (
            patch.object(supervise.subprocess, "check_output", return_value=json.dumps([])),
            patch.object(supervise.urllib.request, "urlopen", side_effect=TimeoutError),
            self.assertRaises(TimeoutError),
        ):
            supervise.addresses()


if __name__ == "__main__":
    unittest.main()
