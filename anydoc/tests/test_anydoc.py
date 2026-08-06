#!/usr/bin/env python3
"""Unit tests for the anydoc wrapper (`anydoc/scripts/anydoc`).

Offline by design: the core tests need no node, no npx, and no network.
Real-CLI tests (converting the committed fixtures through the pinned CLI)
are opt-in and skip gracefully when the toolchain is unavailable.
"""

import importlib.machinery
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # anydoc/
SCRIPT = ROOT / "scripts" / "anydoc"
FIXTURES = ROOT / "fixtures"

DOCX = FIXTURES / "fixture-handmade-outline.docx"
CSV = FIXTURES / "fixture-sheet.csv"
SCANNED = FIXTURES / "scanned-image-only.pdf"
ENCRYPTED = FIXTURES / "encrypted--errors.odt"
MALFORMED = FIXTURES / "empty--errors.docx"
UNSUPPORTED = FIXTURES / "unsupported.xyz"
TABLES = FIXTURES / "fixture-handmade-tables.docx"

PINNED = "@firecrawl/anydoc@0.1.6"

cli = importlib.machinery.SourceFileLoader("anydoc_wrapper", str(SCRIPT)).load_module()


def run_in_process(arguments):
    """Run cli.main() in-process; return (code, stdout, stderr)."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = cli.main(arguments)
        except SystemExit as exc:
            code = exc.code if exc.code is not None else 0
    return code, stdout.getvalue(), stderr.getvalue()


def run_script(arguments, env=None, cwd=None, input_bytes=None, timeout=120):
    """Run the wrapper as a subprocess; return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + arguments,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=cwd,
        input=input_bytes,
        timeout=timeout,
    )


def minimal_path_env():
    """A PATH containing only a python3 symlink (no node, no npx)."""
    tmp = Path(tempfile.mkdtemp())
    bindir = tmp / "bin"
    bindir.mkdir()
    os.symlink(sys.executable, bindir / "python3")
    env = os.environ.copy()
    env["PATH"] = str(bindir)
    return tmp, env


def node_shim_env(version_line):
    """A PATH whose `node` is a shim printing `version_line`."""
    tmp, env = minimal_path_env()
    bindir = tmp / "bin2"
    bindir.mkdir()
    shim = bindir / "node"
    shim.write_text("#!/bin/sh\n%s\n" % version_line)
    shim.chmod(0o755)
    env["PATH"] = str(bindir) + os.pathsep + env["PATH"]
    return tmp, env


class WrapperCoreTests(unittest.TestCase):
    """Offline wrapper behavior: help, usage errors, pre-validation, plans."""

    def test_script_is_executable_and_has_shebang(self):
        mode = stat.S_IMODE(SCRIPT.stat().st_mode)
        self.assertTrue(mode & stat.S_IXUSR, "scripts/anydoc must be executable")
        with SCRIPT.open("rb") as handle:
            first = handle.readline().decode("utf-8", "replace").strip()
        self.assertEqual(first, "#!/usr/bin/env python3")

    def test_direct_execution_via_shebang(self):
        result = subprocess.run(
            [str(SCRIPT), "info"], capture_output=True, text=True, timeout=60
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("anydoc", result.stdout)
        self.assertIn("0.1.6", result.stdout)

    def test_help_exits_zero_with_usage_and_examples(self):
        for arguments in (
            ["--help"],
            ["convert", "--help"],
            ["batch", "--help"],
            ["info", "--help"],
        ):
            with self.subTest(arguments=arguments):
                code, stdout, stderr = run_in_process(arguments)
                self.assertEqual(code, 0, stderr)
                self.assertIn("usage", stdout.lower())
                self.assertIn("Example", stdout)
                self.assertEqual(stderr, "")

    def test_batch_help_documents_exit_semantics(self):
        _, stdout, _ = run_in_process(["batch", "--help"])
        self.assertIn("1 when any", stdout)
        self.assertIn("input failed", stdout)

    def test_help_works_without_node_on_path(self):
        tmp, env = minimal_path_env()
        try:
            for arguments in (
                ["--help"],
                ["convert", "--help"],
                ["batch", "--help"],
                ["info", "--help"],
            ):
                with self.subTest(arguments=arguments):
                    result = run_script(arguments, env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("usage", result.stdout.lower())
                    self.assertIn("Example", result.stdout)
                    self.assertEqual(result.stderr, "")
        finally:
            shutil.rmtree(tmp)

    def test_usage_errors_exit_2(self):
        # Each usage error must exit 2 on stderr and name the offending token
        # OR the missing input (argparse names the missing subcommand for an
        # unknown root option).
        cases = (
            (["--bogus"], "command"),
            (["convert", str(DOCX), "--bogus"], "--bogus"),
            (["convert"], "required"),
            (["batch"], "required"),
        )
        for arguments, needle in cases:
            with self.subTest(arguments=arguments):
                code, stdout, stderr = run_in_process(arguments)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertIn(needle, stderr)
                self.assertIn("usage", stderr.lower())
                self.assertNotIn("Traceback", stderr)

    def test_info_reports_tool_and_version(self):
        code, stdout, stderr = run_in_process(["info"])
        self.assertEqual(code, 0, stderr)
        self.assertIn("anydoc", stdout)
        self.assertIn("0.1.6", stdout)
        self.assertEqual(stderr, "")

    def test_info_version_prints_exact_version(self):
        code, stdout, stderr = run_in_process(["info", "--version"])
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stdout.strip(), "0.1.6")
        self.assertEqual(stderr, "")

    def test_convert_missing_input_prevalidation(self):
        code, stdout, stderr = run_in_process(
            ["convert", "/nonexistent/anydoc-input.docx"]
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("/nonexistent/anydoc-input.docx", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_convert_directory_input_prevalidation(self):
        code, stdout, stderr = run_in_process(["convert", str(FIXTURES)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn(str(FIXTURES), stderr)
        self.assertIn("directory", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_convert_output_path_is_directory(self):
        code, stdout, stderr = run_in_process(
            ["convert", str(DOCX), "-o", str(FIXTURES)]
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("directory", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_convert_invalid_format_exit_2(self):
        code, stdout, stderr = run_in_process(
            ["convert", str(DOCX), "-f", "bogus"]
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("invalid format 'bogus'", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_convert_dry_run_plans_without_executing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.md"
            code, stdout, stderr = run_in_process(
                ["convert", str(DOCX), "-o", str(out), "--dry-run"]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("npx -y " + PINNED, stdout)
            self.assertIn(str(DOCX), stdout)
            self.assertEqual(stderr, "")
            self.assertFalse(out.exists(), "dry-run must not create outputs")

    def test_convert_dry_run_json(self):
        code, stdout, stderr = run_in_process(
            ["convert", str(DOCX), "--dry-run", "--json"]
        )
        self.assertEqual(code, 0, stderr)
        doc = json.loads(stdout)
        self.assertTrue(doc["dry_run"])
        self.assertEqual(doc["command"], "convert")
        self.assertIn("npx -y " + PINNED, doc["command_line"])
        self.assertEqual(stderr, "")

    def test_batch_dry_run_json_plan_and_no_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            code, stdout, stderr = run_in_process(
                [
                    "batch",
                    str(DOCX),
                    str(CSV),
                    "--out-dir",
                    str(out_dir),
                    "--dry-run",
                    "--json",
                ]
            )
            self.assertEqual(code, 0, stderr)
            doc = json.loads(stdout)
            self.assertTrue(doc["dry_run"])
            self.assertEqual(doc["command"], "batch")
            self.assertEqual(len(doc["plan"]), 2)
            for entry in doc["plan"]:
                self.assertIn("input", entry)
                self.assertIn("output", entry)
                self.assertIn("command", entry)
                self.assertIn("npx -y " + PINNED, entry["command"])
            self.assertEqual(stderr, "")
            self.assertFalse(out_dir.exists(), "dry-run must not create out-dir")

    def test_batch_dry_run_marks_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.docx"
            code, stdout, stderr = run_in_process(
                [
                    "batch",
                    str(DOCX),
                    str(missing),
                    "--out-dir",
                    str(Path(tmp) / "out"),
                    "--dry-run",
                    "--json",
                ]
            )
            self.assertEqual(code, 0, stderr)
            doc = json.loads(stdout)
            self.assertEqual(len(doc["plan"]), 2)
            self.assertFalse(doc["plan"][0]["would_fail"])
            self.assertTrue(doc["plan"][1]["would_fail"])
            self.assertIn("not found", doc["plan"][1]["error"])

    def test_batch_dry_run_defaults_out_dir_to_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr = run_in_process(
                [
                    "batch",
                    str(DOCX),
                    "--dry-run",
                    "--json",
                ],
            )
            self.assertEqual(code, 0, stderr)
            doc = json.loads(stdout)
            self.assertEqual(doc["out_dir"], str(Path.cwd()))

    def test_batch_requires_inputs(self):
        code, stdout, stderr = run_in_process(["batch"])
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")

    def test_convert_json_error_stays_parseable(self):
        code, stdout, stderr = run_in_process(
            ["convert", "/nonexistent/anydoc-input.docx", "--json"]
        )
        self.assertEqual(code, 1)
        doc = json.loads(stdout)
        self.assertFalse(doc["ok"])
        self.assertEqual(doc["exit_code"], 1)
        self.assertIn("not found", doc["error"])
        self.assertIn("not found", stderr)

    def test_node_missing_error_via_minimal_path(self):
        tmp, env = minimal_path_env()
        try:
            result = run_script(["convert", str(DOCX)], env=env)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("node", result.stderr.lower())
            self.assertIn("20", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        finally:
            shutil.rmtree(tmp)

    def test_node_too_old_error_via_shim(self):
        tmp, env = node_shim_env('echo "v18.20.0"')
        try:
            result = run_script(["convert", str(DOCX)], env=env)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("v18.20.0", result.stderr)
            self.assertIn("20", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        finally:
            shutil.rmtree(tmp)

    @unittest.skipUnless(shutil.which("node"), "node not on PATH")
    def test_npx_missing_error_via_path_with_node(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            bindir = tmp / "bin"
            bindir.mkdir()
            os.symlink(sys.executable, bindir / "python3")
            node_bin = tmp / "bin2"
            node_bin.mkdir()
            os.symlink(Path(shutil.which("node")), node_bin / "node")
            env = os.environ.copy()
            env["PATH"] = str(node_bin) + os.pathsep + str(bindir)
            result = run_script(["convert", str(DOCX)], env=env)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("npx", result.stderr)
            self.assertIn(PINNED, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        finally:
            shutil.rmtree(tmp)

    def test_hint_mapping_for_known_error_classes(self):
        cases = (
            (
                "anydoc: unsupported input: PDF has no extractable text "
                "(Scanned, 1 pages): OCR is required",
                "no-ocr",
                ("OCR", "Firecrawl Parse", "not retry"),
            ),
            ("anydoc: document is encrypted", "encrypted", ("encrypted", "unencrypted")),
            (
                "anydoc: malformed document: not a readable zip archive: "
                "invalid Zip archive: Could not find EOCD",
                "malformed",
                ("malformed", "corrupt", "zip"),
            ),
            (
                "anydoc: unsupported input: unrecognized file content and "
                "extension: unsupported.xyz",
                "unsupported",
                ("unsupported", "-f"),
            ),
            (
                "anydoc: resource limit exceeded (max_entry_bytes): "
                "word/document.xml declares 201326759 decompressed bytes",
                "resource-limit",
                (),
            ),
        )
        for message, expected_class, keywords in cases:
            with self.subTest(message=message):
                error_class, hint = cli.error_class_hint(message)
                self.assertEqual(error_class, expected_class)
                if keywords:
                    self.assertIsNotNone(hint)
                    for keyword in keywords:
                        self.assertIn(keyword, hint)

    def test_build_cli_command_shape(self):
        self.assertEqual(
            cli.build_cli_command("report.docx", "out.md", "csv"),
            ["npx", "-y", PINNED, "report.docx", "-o", "out.md", "-f", "csv"],
        )
        self.assertEqual(
            cli.build_cli_command("report.docx", None, None),
            ["npx", "-y", PINNED, "report.docx"],
        )
        # stdin passes through as `-`
        self.assertEqual(
            cli.build_cli_command("-", None, "csv"),
            ["npx", "-y", PINNED, "-", "-f", "csv"],
        )
        # a dash-leading filename is protected with `--`
        self.assertEqual(
            cli.build_cli_command("-weird", "o.md", None),
            ["npx", "-y", PINNED, "--", "-weird", "-o", "o.md"],
        )

    @unittest.skipUnless(shutil.which("node") and shutil.which("npx"), "toolchain missing")
    def test_runtime_errors_empty_when_toolchain_present(self):
        self.assertEqual(cli.runtime_errors(), [])

    def test_format_aliases_accepted(self):
        code, _stdout, stderr = run_in_process(
            ["convert", str(DOCX), "-f", "docm", "--dry-run"]
        )
        self.assertEqual(code, 0, stderr)


class RealCliTests(unittest.TestCase):
    """End-to-end conversions through the pinned CLI; skip when unavailable."""

    skip_reason = None

    @classmethod
    def setUpClass(cls):
        if not shutil.which("npx") or not shutil.which("node"):
            cls.skip_reason = "npx/node not available"
            return
        try:
            proc = subprocess.run(
                ["npx", "-y", PINNED, "--version"],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired):
            cls.skip_reason = "pinned CLI unavailable"
            return
        if proc.returncode != 0 or "0.1.6" not in proc.stdout:
            cls.skip_reason = "pinned CLI unavailable"
            return
        cls.skip_reason = None

    def setUp(self):
        if self.__class__.skip_reason:
            self.skipTest(self.__class__.skip_reason)

    def _parse_ok_json(self, result):
        """Assert a successful --json run and return its parsed document."""
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        doc = json.loads(result.stdout)
        self.assertTrue(doc["ok"])
        self.assertEqual(doc["exit_code"], 0)
        return doc

    def test_convert_to_stdout(self):
        result = run_script(["convert", str(DOCX)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("# ", result.stdout)
        self.assertIn("## ", result.stdout)

    def test_convert_to_file_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.md"
            result = run_script(["convert", str(DOCX), "-o", str(out)])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")
            self.assertTrue(out.exists())
            content = out.read_text(encoding="utf-8")
            self.assertIn("## ", content)

    def test_convert_silently_overwrites_seeded_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.md"
            out.write_text("SENTINEL\n", encoding="utf-8")
            result = run_script(["convert", str(DOCX), "-o", str(out)])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")
            content = out.read_text(encoding="utf-8")
            self.assertNotIn("SENTINEL", content)
            self.assertIn("## ", content)

    def test_convert_fresh_cwd_creates_no_stray_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script(["convert", str(DOCX)], cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertFalse((Path(tmp) / "out.md").exists())
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_convert_stdin_csv(self):
        result = run_script(
            ["convert", "-", "-f", "csv"], input_bytes="a,b\n1,2\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("| a | b |", result.stdout)
        self.assertIn("| 1 | 2 |", result.stdout)

    def test_convert_empty_stdin_errors_without_hanging(self):
        result = run_script(["convert", "-"], input_bytes="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("anydoc", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_convert_extensionless_file_with_fmt_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.write_bytes(CSV.read_bytes())
            result = run_script(["convert", str(data), "-f", "csv"])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("| Kind | Value | Note |", result.stdout)

    def test_convert_scanned_pdf_hint(self):
        result = run_script(["convert", str(SCANNED)])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("OCR", result.stderr)
        self.assertIn("Firecrawl Parse", result.stderr)
        self.assertIn("not retry", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_convert_encrypted_hint(self):
        result = run_script(["convert", str(ENCRYPTED)])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("encrypted", result.stderr)
        self.assertIn("unencrypted", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_convert_malformed_hint(self):
        result = run_script(["convert", str(MALFORMED)])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("malformed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_convert_unsupported_hint(self):
        result = run_script(["convert", str(UNSUPPORTED)])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("unsupported", result.stderr)
        self.assertIn("-f", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_convert_json_success_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.md"
            result = run_script(
                ["convert", str(DOCX), "-o", str(out), "--json"]
            )
            doc = self._parse_ok_json(result)
            self.assertEqual(doc["output"], str(out))

    def test_convert_json_success_embeds_markdown(self):
        result = run_script(["convert", str(DOCX), "--json"])
        doc = self._parse_ok_json(result)
        self.assertIn("## ", doc["markdown"])

    def test_convert_json_failure(self):
        result = run_script(["convert", str(SCANNED), "--json"])
        self.assertEqual(result.returncode, 1)
        doc = json.loads(result.stdout)
        self.assertFalse(doc["ok"])
        self.assertEqual(doc["exit_code"], 1)
        self.assertEqual(doc["error_class"], "no-ocr")
        self.assertIn("OCR", result.stderr)

    def test_batch_mixed_continues_past_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_script(
                [
                    "batch",
                    str(DOCX),
                    str(ENCRYPTED),
                    str(TABLES),
                    "--out-dir",
                    str(out_dir),
                ]
            )
            self.assertEqual(result.returncode, 1)
            stdout = result.stdout
            self.assertIn("ok %s" % DOCX, stdout)
            self.assertIn("FAIL %s" % ENCRYPTED, stdout)
            self.assertIn("ok %s" % TABLES, stdout)
            self.assertIn("summary: 3 total, 2 succeeded, 1 failed", stdout)
            self.assertTrue((out_dir / "fixture-handmade-outline.md").exists())
            self.assertTrue((out_dir / "fixture-handmade-tables.md").exists())
            self.assertFalse((out_dir / "encrypted--errors.md").exists())
            self.assertIn("encrypted", result.stderr)
            self.assertIn("hint", result.stderr)

    def test_batch_all_valid_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_script(
                [
                    "batch",
                    str(DOCX),
                    str(CSV),
                    "--out-dir",
                    str(out_dir),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertIn("summary: 2 total, 2 succeeded, 0 failed", result.stdout)
            self.assertTrue((out_dir / "fixture-handmade-outline.md").exists())
            self.assertTrue((out_dir / "fixture-sheet.md").exists())

    def test_batch_json_all_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script(
                [
                    "batch",
                    str(DOCX),
                    str(CSV),
                    "--out-dir",
                    str(Path(tmp) / "out"),
                    "--json",
                ]
            )
            doc = self._parse_ok_json(result)
            self.assertEqual(doc["summary"], {"total": 2, "succeeded": 2, "failed": 0})
            self.assertEqual([f["status"] for f in doc["files"]], ["ok", "ok"])

    def test_batch_json_mixed_keeps_stdout_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script(
                [
                    "batch",
                    str(DOCX),
                    str(ENCRYPTED),
                    "--out-dir",
                    str(Path(tmp) / "out"),
                    "--json",
                ]
            )
            self.assertEqual(result.returncode, 1)
            doc = json.loads(result.stdout)
            self.assertFalse(doc["ok"])
            self.assertEqual(doc["exit_code"], 1)
            self.assertEqual(doc["summary"], {"total": 2, "succeeded": 1, "failed": 1})
            self.assertIn("encrypted", result.stderr)

    def test_batch_duplicates_convert_per_occurrence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_script(
                ["batch", str(DOCX), str(DOCX), "--out-dir", str(out_dir)]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("summary: 2 total, 2 succeeded, 0 failed", result.stdout)
            self.assertEqual(
                sorted(p.name for p in out_dir.iterdir()), ["fixture-handmade-outline.md"]
            )

    def test_batch_same_basename_collision_last_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            a_dir = Path(tmp) / "a"
            b_dir = Path(tmp) / "b"
            a_dir.mkdir()
            b_dir.mkdir()
            (a_dir / "same.docx").write_bytes(DOCX.read_bytes())
            (b_dir / "same.docx").write_bytes(TABLES.read_bytes())
            out_dir = Path(tmp) / "out"
            result = run_script(
                [
                    "batch",
                    str(a_dir / "same.docx"),
                    str(b_dir / "same.docx"),
                    "--out-dir",
                    str(out_dir),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                sorted(p.name for p in out_dir.iterdir()), ["same.md"]
            )
            content = (out_dir / "same.md").read_text(encoding="utf-8")
            self.assertIn("| Head A | Head B | Head C |", content)


if __name__ == "__main__":
    unittest.main()
