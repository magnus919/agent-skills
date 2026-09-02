from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("vite-doctor")


class ViteDoctorTest(unittest.TestCase):
    def run_doctor(self, project: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SCRIPT), "--project", str(project), "--json", *extra],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_reports_lock_config_and_names_without_env_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "package.json").write_text(
                json.dumps({"devDependencies": {"vite": "^6.0.0"}}), encoding="utf-8"
            )
            (project / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n", encoding="utf-8")
            (project / "vite.config.ts").write_text("export default {}\n", encoding="utf-8")
            (project / ".env.local").write_text("VITE_PUBLIC=do-not-print\nSECRET=never-print\n", encoding="utf-8")
            result = self.run_doctor(project)
            self.assertEqual(0, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual("pnpm", payload["package_manager"]["name"])
            self.assertEqual(["vite.config.ts"], payload["config_files"])
            self.assertEqual([".env.local"], payload["env_file_names"])
            self.assertIn("^6.0.0", json.dumps(payload))
            self.assertNotIn("do-not-print", result.stdout)
            self.assertNotIn("never-print", result.stdout)

    def test_missing_project_is_bounded_error(self) -> None:
        result = self.run_doctor(Path("/path/that/does/not/exist"))
        self.assertEqual(1, result.returncode)
        self.assertIn("not a directory", result.stderr)

    def test_invalid_timeout_is_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_doctor(Path(directory), "--timeout", "0")
            self.assertEqual(2, result.returncode)
            self.assertIn("positive", result.stderr)


if __name__ == "__main__":
    unittest.main()
