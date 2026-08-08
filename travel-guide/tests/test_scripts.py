#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TEMPLATE = ROOT / "templates" / "trip-brief.json"


def run_script(name, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *[str(arg) for arg in args]],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


class TravelGuideScriptsTest(unittest.TestCase):
    def test_template_is_json_and_non_strict_validation_is_ok(self):
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            result = run_script("validate-trip-brief.py", TEMPLATE, "--json")
            report.write_text(result.stdout, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "ok")

    def test_strict_validation_rejects_unfilled_template(self):
        result = run_script("validate-trip-brief.py", TEMPLATE, "--strict", "--json")
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(any("placeholder" in error for error in payload["errors"]))

    def test_renderer_produces_both_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            for mode in ("dossier", "companion"):
                output = output_dir / (mode + ".html")
                result = run_script("render-travel-guide.py", TEMPLATE, "--mode", mode, "--output", output, "--json")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(output.is_file())
                rendered = output.read_text(encoding="utf-8")
                self.assertIn("<!doctype html>", rendered)
                self.assertIn("class=\"cover\"", rendered)
                self.assertIn("@page", rendered)
                self.assertIn("Lisbon, at a human pace", rendered)
                self.assertIn("Sources.", rendered)

    def test_sanitizer_redacts_personal_fields_and_url_query(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "private.json"
            output = directory / "shareable.json"
            data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
            data["trip"]["start_date"] = "2027-04-12"
            data["trip"]["end_date"] = "2027-04-18"
            data["trip"]["travelers"] = ["Alex Example"]
            data["trip"]["budget"] = {"label": "private", "amount_range": "9999"}
            data["profile"] = {"known_preferences": ["botanical gardens"], "constraints": ["avoid crowds"]}
            data["sources"][0]["url"] = "https://example.org/source?token=secret#private"
            source.write_text(json.dumps(data), encoding="utf-8")
            result = run_script("sanitize-trip-brief.py", source, "--profile", "shareable", "--output", output, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            sanitized = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(sanitized["privacy_mode"], "shareable")
            self.assertIsNone(sanitized["trip"]["start_date"])
            self.assertEqual(sanitized["trip"]["travelers"], ["the travel party"])
            self.assertEqual(sanitized["trip"]["budget"], {"label": "budget withheld"})
            self.assertEqual(sanitized["profile"]["known_preferences"], ["preferences withheld"])
            self.assertEqual(sanitized["profile"]["constraints"], ["constraints withheld"])
            self.assertNotIn("token=secret", sanitized["sources"][0]["url"])

    def test_sanitized_model_remains_renderable(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "private.json"
            output = directory / "shareable.json"
            html_output = directory / "shareable.html"
            source.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
            result = run_script("sanitize-trip-brief.py", source, "--output", output, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            render = run_script("render-travel-guide.py", output, "--mode", "companion", "--output", html_output, "--json")
            self.assertEqual(render.returncode, 0, render.stderr)
            self.assertIn('data-privacy-mode="shareable"', html_output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
