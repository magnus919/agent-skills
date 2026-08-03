#!/usr/bin/env python3
"""Tests for documents/scripts/validate-documents.py.

Runs standalone (``python3 documents/tests/test_validate_documents.py``) and is
discovered by scripts/check-artifacts.py's ``unittest`` discovery pass. Every
test is environment-independent: renderer availability is simulated by
monkeypatching the module's renderer-discovery functions, never by assuming a
renderer is or is not installed.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "documents" / "scripts"
FIXTURES_DIR = REPO_ROOT / "documents" / "fixtures"

SPEC = importlib.util.spec_from_file_location(
    "validate_documents", SCRIPTS_DIR / "validate-documents.py"
)
vd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vd)

FIXTURES = ["sample.pdf", "sample.docx", "sample.xlsx", "sample.pptx"]


class StructuralValidationTests(unittest.TestCase):
    def test_all_fixtures_pass(self):
        for name in FIXTURES:
            with self.subTest(fixture=name):
                report = vd.validate_files([str(FIXTURES_DIR / name)])
                self.assertEqual(report["status"], "ok")
                self.assertEqual(report["exit_code"], 0)
                self.assertEqual(report["files"][0]["status"], "pass")

    def test_each_format_detected(self):
        expected = {
            "sample.pdf": "pdf",
            "sample.docx": "docx",
            "sample.xlsx": "xlsx",
            "sample.pptx": "pptx",
        }
        for name, fmt in expected.items():
            with self.subTest(fixture=name):
                report = vd.validate_files([str(FIXTURES_DIR / name)])
                self.assertEqual(report["files"][0]["format"], fmt)

    def test_json_output_has_status_and_ok(self):
        report = vd.validate_files([str(FIXTURES_DIR / "sample.pdf")])
        self.assertIn("status", report)
        self.assertIn("ok", report)
        self.assertTrue(report["ok"])
        self.assertTrue(json.dumps(report))  # serializable

    def test_broken_pdf_fails(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"this is not a pdf at all")
            path = tmp.name
        try:
            report = vd.validate_files([path])
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["exit_code"], 1)
            self.assertEqual(report["files"][0]["status"], "fail")
        finally:
            os.unlink(path)

    def test_corrupt_zip_fails(self):
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"PK\x03\x04 not really a zip")
            path = tmp.name
        try:
            report = vd.validate_files([path])
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["exit_code"], 1)
        finally:
            os.unlink(path)

    def test_missing_file_is_error(self):
        report = vd.validate_files([str(REPO_ROOT / "documents" / "fixtures" / "nope.pdf")])
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["exit_code"], 2)

    def test_unsupported_extension_skipped(self):
        report = vd.validate_files([str(REPO_ROOT / "documents" / "SKILL.md")])
        self.assertEqual(report["files"][0]["status"], "skipped")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["exit_code"], 0)


class RenderCheckTests(unittest.TestCase):
    def setUp(self):
        # Force "no renderer installed" for deterministic degradation tests.
        self.orig_pdf = vd.find_pdf_renderer
        self.orig_office = vd.find_office_renderer
        vd.find_pdf_renderer = lambda: None
        vd.find_office_renderer = lambda: None

    def tearDown(self):
        vd.find_pdf_renderer = self.orig_pdf
        vd.find_office_renderer = self.orig_office

    def test_render_check_unavailable_without_renderer(self):
        for name in FIXTURES:
            with self.subTest(fixture=name):
                report = vd.validate_files([str(FIXTURES_DIR / name)], render_check=True)
                self.assertEqual(report["status"], "unavailable")
                self.assertEqual(report["exit_code"], 0)
                self.assertEqual(report["files"][0]["render"]["status"], "unavailable")

    def test_render_check_unavailable_for_unsupported_file(self):
        report = vd.validate_files([str(REPO_ROOT / "documents" / "SKILL.md")], render_check=True)
        self.assertEqual(report["status"], "unavailable")
        self.assertEqual(report["exit_code"], 0)

    def test_render_ok_with_pdf_renderer(self):
        vd.find_pdf_renderer = lambda: "/usr/bin/env-test-pdftoppm"
        vd.find_office_renderer = lambda: None
        # Renderer discovery is stubbed; render_pdf is stubbed to success so no
        # real binary is required.
        original = vd.render_pdf
        vd.render_pdf = lambda path, tmpdir: {"status": "ok", "renderer": "pdftoppm", "pages": 1}
        try:
            report = vd.validate_files([str(FIXTURES_DIR / "sample.pdf")], render_check=True)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["exit_code"], 0)
            self.assertEqual(report["files"][0]["render"]["status"], "ok")
        finally:
            vd.render_pdf = original

    def test_render_failure_fails_report(self):
        vd.find_pdf_renderer = lambda: "/usr/bin/env-test-pdftoppm"
        original = vd.render_pdf
        vd.render_pdf = lambda path, tmpdir: {"status": "failed", "renderer": "pdftoppm", "reason": "boom"}
        try:
            report = vd.validate_files([str(FIXTURES_DIR / "sample.pdf")], render_check=True)
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["exit_code"], 1)
        finally:
            vd.render_pdf = original

    def test_render_pdf_dispatches_renderer_specific_args(self):
        # Each supported PDF renderer has its own CLI; a machine with only
        # mutool or ghostscript (no pdftoppm) must still render correctly.
        import tempfile as _tf

        captured = {}

        def fake_run(cmd, capture_output, timeout):
            captured["cmd"] = cmd
            return subprocess.CompletedProcess(cmd, 0, b"", b"")

        original_run = vd.subprocess.run
        original_find = vd.find_pdf_renderer
        vd.subprocess.run = fake_run
        try:
            with _tf.TemporaryDirectory() as tmp:
                vd.find_pdf_renderer = lambda: "/usr/bin/pdftoppm"
                vd.render_pdf(FIXTURES_DIR / "sample.pdf", Path(tmp))
                self.assertIn("-png", captured["cmd"])
                self.assertNotIn("draw", captured["cmd"])

                vd.find_pdf_renderer = lambda: "/usr/bin/mutool"
                vd.render_pdf(FIXTURES_DIR / "sample.pdf", Path(tmp))
                self.assertIn("draw", captured["cmd"])
                self.assertIn("-o", captured["cmd"])

                vd.find_pdf_renderer = lambda: "/usr/bin/gs"
                vd.render_pdf(FIXTURES_DIR / "sample.pdf", Path(tmp))
                self.assertIn("-sDEVICE=png16m", captured["cmd"])
                self.assertTrue(any(arg.startswith("-sOutputFile=") for arg in captured["cmd"]))
        finally:
            vd.subprocess.run = original_run
            vd.find_pdf_renderer = original_find


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "validate-documents.py")] + list(args),
            capture_output=True,
            text=True,
        )

    def test_help_exits_zero_and_advertises_json(self):
        proc = self.run_cli("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("--render-check", proc.stdout)

    def test_cli_json_on_fixture(self):
        proc = self.run_cli("--json", str(FIXTURES_DIR / "sample.xlsx"))
        self.assertEqual(proc.returncode, 0)
        report = json.loads(proc.stdout)
        self.assertEqual(report["status"], "ok")

    def test_cli_exit_1_on_broken(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"junk")
            path = tmp.name
        try:
            proc = self.run_cli("--json", path)
            self.assertEqual(proc.returncode, 1)
        finally:
            os.unlink(path)

    def test_cli_render_check_unavailable_when_no_renderer(self):
        # The CLI uses the real renderer discovery; run it only when we can
        # force the no-renderer path via the module-level stub in-process,
        # which is covered by RenderCheckTests. Here we only assert the CLI
        # accepts the flag and returns 0 or 1 without crashing.
        proc = self.run_cli("--render-check", "--json", str(FIXTURES_DIR / "sample.pdf"))
        self.assertIn(proc.returncode, (0, 1))
        report = json.loads(proc.stdout)
        self.assertIn(report["status"], ("ok", "unavailable", "fail"))


if __name__ == "__main__":
    unittest.main()
