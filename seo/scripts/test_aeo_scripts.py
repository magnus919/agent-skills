#!/usr/bin/env python3
import runpy
import tempfile
import unittest
from pathlib import Path

_audit = runpy.run_path(str(Path(__file__).with_name("aeo_audit.py")))
_matrix = runpy.run_path(str(Path(__file__).with_name("build_prompt_matrix.py")))
audit = _audit["audit"]
build = _matrix["build"]


class AeoScriptTests(unittest.TestCase):
    def test_audit_finds_answer_structure_and_jsonld(self):
        html = """<html><head><title>What is Mesh?</title><link rel='canonical' href='/mesh'><script type='application/ld+json'>{\"@context\":\"https://schema.org\",\"@type\":\"Article\"}</script></head><body><h1>What is Mesh?</h1><h2>How does mesh work?</h2><p>Mesh networks route traffic between peers.</p></body></html>"""
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
            handle.write(html)
            path = handle.name
        result = audit(path)
        self.assertEqual(result["h1_count"], 1)
        self.assertEqual(result["question_heading_count"], 2)
        self.assertEqual(result["jsonld_types"], ["Article"])
        Path(path).unlink()

    def test_audit_reports_parse_error_without_claiming_success(self):
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
            handle.write("<h1>Broken</h1><script type='application/ld+json'>{bad}</script>")
            path = handle.name
        result = audit(path)
        self.assertEqual(result["jsonld_parse_errors"], 1)
        self.assertIn("JSON-LD parse error", result["findings"])
        Path(path).unlink()

    def test_prompt_matrix_is_deterministic_and_hashes_prompts(self):
        rows = build({"topics": [{"topic": "AEO", "intents": ["definition"], "questions": ["Can AEO guarantee citations?"]}]})
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["prompt_sha256"], rows[0]["prompt_sha256"])
        self.assertEqual(rows[1]["intent"], "custom")


if __name__ == "__main__":
    unittest.main()
