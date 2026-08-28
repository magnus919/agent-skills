#!/usr/bin/env python3
"""Offline regression tests for AnyDoc hosted-OCR privacy boundaries."""

import importlib.machinery
import io
import os
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "anydoc"
FIXTURES = ROOT / "fixtures"
SCANNED = FIXTURES / "scanned-image-only.pdf"
TEXT_PDF = FIXTURES / "fixture-text.pdf"
PINNED = "@firecrawl/anydoc@0.2.4"

cli = importlib.machinery.SourceFileLoader(
    "anydoc_hosted_ocr_wrapper", str(SCRIPT)
).load_module()


def run_in_process(arguments):
    """Run cli.main() in-process; return (code, stdout, stderr)."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = cli.main(arguments)
        except SystemExit as exc:
            code = exc.code if exc.code is not None else 0
    return code, stdout.getvalue(), stderr.getvalue()


def test_selected_release_and_timeout_contract():
    assert cli.PINNED == PINNED
    assert cli.LOCAL_RUN_TIMEOUT == 120
    assert cli.HOSTED_RUN_TIMEOUT > 300


def test_local_command_is_the_default_and_never_enables_hosted_ocr():
    command = cli.build_cli_command("report.pdf", None, None, "reject")
    assert command == ["npx", "-y", PINNED, "report.pdf"]
    assert "hosted" not in command
    assert "--api-key" not in command
    assert "--api-url" not in command


def test_hosted_command_is_explicit_but_wrapper_confirmation_is_not_forwarded():
    command = cli.build_cli_command("scan.pdf", "out.md", None, "hosted")
    assert command == [
        "npx",
        "-y",
        PINNED,
        "scan.pdf",
        "-o",
        "out.md",
        "--ocr",
        "hosted",
    ]
    assert "--allow-hosted-upload" not in command
    assert "--api-key" not in command


def test_hosted_mode_without_upload_authorization_stops_before_cli_spawn():
    with mock.patch.object(cli, "runtime_errors", return_value=[]), mock.patch.object(
        cli, "run_cli"
    ) as run_cli:
        code, stdout, stderr = run_in_process(
            ["convert", str(SCANNED), "--ocr", "hosted"]
        )
    assert code == 2
    assert stdout == ""
    assert "--allow-hosted-upload" in stderr
    assert "whole document" in stderr
    run_cli.assert_not_called()


def test_upload_authorization_without_hosted_mode_is_rejected():
    with mock.patch.object(cli, "run_cli") as run_cli:
        code, stdout, stderr = run_in_process(
            ["convert", str(TEXT_PDF), "--allow-hosted-upload"]
        )
    assert code == 2
    assert stdout == ""
    assert "only valid with --ocr hosted" in stderr
    run_cli.assert_not_called()


def test_hosted_dry_run_is_explicit_and_does_not_disclose_environment_values():
    secret = "hosted-test-secret-never-print"
    private_endpoint = "https://private.example.invalid"
    with mock.patch.dict(
        os.environ,
        {
            "FIRECRAWL_API_KEY": secret,
            "FIRECRAWL_API_URL": private_endpoint,
        },
        clear=False,
    ):
        code, stdout, stderr = run_in_process(
            [
                "convert",
                str(SCANNED),
                "--ocr",
                "hosted",
                "--allow-hosted-upload",
                "--dry-run",
            ]
        )
    assert code == 0
    assert stderr == ""
    assert "--ocr hosted" in stdout
    assert "whole-document upload authorized" in stdout
    assert secret not in stdout
    assert private_endpoint not in stdout
    assert "--api-key" not in stdout


def test_api_key_on_argv_is_rejected_without_echoing_the_secret():
    secret = "argv-secret-never-print"
    code, stdout, stderr = run_in_process(
        [
            "convert",
            str(SCANNED),
            "--ocr",
            "hosted",
            "--allow-hosted-upload",
            "--api-key",
            secret,
        ]
    )
    assert code == 2
    assert secret not in stdout
    assert secret not in stderr
    assert "FIRECRAWL_API_KEY" in stderr


def test_local_conversion_does_not_forward_hosted_mode_even_when_credentials_exist():
    completed = subprocess.CompletedProcess([], 0, stdout="# Local\n", stderr="")
    with mock.patch.dict(
        os.environ, {"FIRECRAWL_API_KEY": "ambient-secret"}, clear=False
    ), mock.patch.object(cli, "runtime_errors", return_value=[]), mock.patch.object(
        cli, "run_cli", return_value=completed
    ) as run_cli:
        code, stdout, stderr = run_in_process(["convert", str(TEXT_PDF)])
    assert code == 0
    assert stdout == "# Local\n"
    assert stderr == ""
    command = run_cli.call_args.args[0]
    assert "--ocr" not in command
    assert "hosted" not in command
    assert "ambient-secret" not in command
    assert run_cli.call_args.kwargs["timeout"] == cli.LOCAL_RUN_TIMEOUT


def test_hosted_mode_uses_long_timeout_and_redacts_reflected_environment_secret():
    secret = "reflected-secret-never-print"
    completed = subprocess.CompletedProcess(
        [],
        1,
        stdout="",
        stderr=f"anydoc: Firecrawl Parse rejected the API key: {secret}",
    )
    with mock.patch.dict(
        os.environ, {"FIRECRAWL_API_KEY": secret}, clear=False
    ), mock.patch.object(cli, "runtime_errors", return_value=[]), mock.patch.object(
        cli, "run_cli", return_value=completed
    ) as run_cli:
        code, stdout, stderr = run_in_process(
            [
                "convert",
                str(SCANNED),
                "--ocr",
                "hosted",
                "--allow-hosted-upload",
                "--json",
            ]
        )
    assert code == 1
    assert secret not in stdout
    assert secret not in stderr
    assert "[REDACTED]" in stdout
    assert "[REDACTED]" in stderr
    assert run_cli.call_args.kwargs["timeout"] == cli.HOSTED_RUN_TIMEOUT


def test_needs_ocr_and_hosted_failures_have_distinct_safe_routes():
    error_class, hint = cli.error_class_hint("anydoc: page 1 of 1 needs OCR")
    assert error_class == "needs-ocr"
    assert "local OCR" in hint
    assert "explicit" in hint

    error_class, hint = cli.error_class_hint(
        "anydoc: Firecrawl Parse keyless limit reached, set FIRECRAWL_API_KEY"
    )
    assert error_class == "hosted-rate-limit"
    assert "retry" in hint.lower()
    assert "print" in hint.lower()
