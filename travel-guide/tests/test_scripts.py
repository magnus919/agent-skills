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

    def _filled_brief(self):
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        data["trip"]["route"] = [{"place": "Lisbon", "nights": 3}, {"place": "Sintra", "nights": 1}]
        data["thesis"] = ("A week in Lisbon with enough structure to protect the good parts of the day "
                          "and enough slack for the city to interrupt the plan.")
        data["anchors"] = [{
            "title": "A quiet first look",
            "place": "Miradouro da Graça",
            "why": "It gives the travelers orientation without a checklist.",
            "best_window": "Late morning",
            "cost": "Free",
            "booking": "No booking",
            "failure_mode": "Rain sends the walk indoors.",
            "source_ids": ["S1"],
        }]
        data["days"] = [{
            "day": 1,
            "label": "Arrive without proving anything",
            "kind": "arrive",
            "anchor": "A short orientation walk",
            "texture": "A first meal chosen for ease",
            "pause": "Leave the afternoon unassigned",
            "alternative": "A nearby café and an early night.",
            "practical": "Transfer and check-in caveat.",
            "source_ids": ["S4"],
        }]
        return data

    def test_renderer_adds_journey_line_for_multi_stop_route(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            brief = directory / "brief.json"
            brief.write_text(json.dumps(self._filled_brief()), encoding="utf-8")
            output = directory / "dossier.html"
            result = run_script("render-travel-guide.py", brief, "--output", output, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = output.read_text(encoding="utf-8")
            self.assertIn('class="journey"', rendered)
            self.assertIn("Sintra", rendered)
            self.assertIn("3 nights", rendered)

    def test_renderer_adds_glance_strip_and_meters(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            brief = directory / "brief.json"
            brief.write_text(json.dumps(self._filled_brief()), encoding="utf-8")
            output = directory / "dossier.html"
            result = run_script("render-travel-guide.py", brief, "--output", output, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = output.read_text(encoding="utf-8")
            self.assertIn('id="glance"', rendered)
            self.assertIn('class="glance-day kind-arrive"', rendered)
            self.assertIn('class="trip-meters"', rendered)
            self.assertIn("Slow to moderate", rendered)

    def test_renderer_skips_journey_line_for_single_stop_route(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            brief = directory / "brief.json"
            data = self._filled_brief()
            data["trip"]["route"] = [{"place": "Lisbon", "nights": 7}]
            brief.write_text(json.dumps(data), encoding="utf-8")
            output = directory / "dossier.html"
            result = run_script("render-travel-guide.py", brief, "--output", output, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = output.read_text(encoding="utf-8")
            self.assertNotIn('class="journey"', rendered)

    def test_visual_system_css_is_present(self):
        css = (ROOT / "styles" / "travel-dossier.css").read_text(encoding="utf-8")
        self.assertIn("counter-increment: sheet", css)
        self.assertIn(".glance-grid", css)
        self.assertIn(".trip-meters", css)
        self.assertIn("filter: sepia", css)

    def test_validator_warns_on_unknown_kind(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            brief = directory / "brief.json"
            data = self._filled_brief()
            data["days"][0]["kind"] = "mountain"
            brief.write_text(json.dumps(data), encoding="utf-8")
            result = run_script("validate-trip-brief.py", brief, "--json")
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertTrue(any("kind" in warning for warning in payload["warnings"]))

    def test_section_footer_shows_next_section_and_watermark(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            brief = directory / "brief.json"
            brief.write_text(json.dumps(self._filled_brief()), encoding="utf-8")
            output = directory / "dossier.html"
            result = run_script("render-travel-guide.py", brief, "--output", output, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = output.read_text(encoding="utf-8")
            self.assertIn('class="section-footer"', rendered)
            self.assertIn("Next:", rendered)
            self.assertIn("Trip at a glance", rendered)
            self.assertIn('class="route-watermark"', rendered)
            self.assertIn("End of dossier", rendered)

    def test_section_footer_field_notes_repeat_model_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            brief = directory / "brief.json"
            data = self._filled_brief()
            data["anchors"][0]["failure_mode"] = "Rain sends the walk indoors."
            data["days"][0]["alternative"] = "A nearby café and an early night."
            data["practical"] = [{"label": "Recheck before departure", "value": "Museum hours change seasonally.", "source_ids": ["S1"]}]
            brief.write_text(json.dumps(data), encoding="utf-8")
            output = directory / "dossier.html"
            result = run_script("render-travel-guide.py", brief, "--output", output, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = output.read_text(encoding="utf-8")
            self.assertIn("If it goes wrong", rendered)
            self.assertIn("Rain sends the walk indoors.", rendered)
            self.assertIn("Plan B", rendered)
            self.assertIn("A nearby café and an early night.", rendered)
            self.assertIn("Recheck before departure", rendered)
            self.assertIn("Museum hours change seasonally.", rendered)


if __name__ == "__main__":
    unittest.main()
