#!/usr/bin/env python3
"""Offline tests for the read-only React doctor."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("react-doctor.py")

class DoctorTests(unittest.TestCase):
    def run_doctor(self, root, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args, str(root)], capture_output=True, text=True)

    def test_json_reports_react_vite_signals_without_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(json.dumps({"dependencies": {"react": "18", "react-dom": "18"}}), encoding="utf-8")
            (root / "vite.config.ts").write_text("export default {}", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src/App.tsx").write_text("export default function App() {}", encoding="utf-8")
            (root / ".env.local").write_text("VITE_PUBLIC=visible\nSECRET=do-not-print\n", encoding="utf-8")
            output = self.run_doctor(root, "--json")
            self.assertEqual(output.returncode, 0)
            report = json.loads(output.stdout)
            self.assertEqual(report["checks"][0]["status"], "ok")
            env_check = next(check for check in report["checks"] if check["name"] == "public-env-names")
            self.assertIn("VITE_PUBLIC", env_check["names"])
            self.assertNotIn("do-not-print", output.stdout)

    def test_missing_project_is_usage_error(self):
        output = self.run_doctor(Path("/definitely/not/a/project"))
        self.assertEqual(output.returncode, 2)
        self.assertIn("does not exist", output.stderr)

    def test_malformed_package_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text("{broken", encoding="utf-8")
            output = self.run_doctor(root, "--json")
            self.assertEqual(output.returncode, 0)
            self.assertTrue(any("not valid JSON" in warning for warning in json.loads(output.stdout)["warnings"]))

    def test_help_is_available(self):
        output = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(output.returncode, 0)
        self.assertIn("read-only", output.stdout.lower())

if __name__ == "__main__":
    unittest.main()
