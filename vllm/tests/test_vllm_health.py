#!/usr/bin/env python3
"""Deterministic tests for the vllm/scripts/vllm-health probe.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --check subsets, exit codes, JSON payloads). A local
stdlib HTTP server stubs the vLLM endpoints (/health, /version, /v1/models,
/load, /metrics), so no external network or vLLM server is needed. Also
asserts the read-only contract: the script never opens files in write mode.
"""
import json
import socket
import subprocess
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "vllm-health"


def run_script(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def load_json(proc):
    return json.loads(proc.stdout)


class StubVLLMServer:
    """Minimal read-only stub of the vLLM HTTP surface."""

    def __init__(self):
        handler = self._make_handler()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @staticmethod
    def _make_handler():
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == "/health":
                    self._send(200, "OK")
                elif self.path == "/version":
                    self._send(200, "v0.26.0")
                elif self.path == "/v1/models":
                    self._send(
                        200,
                        json.dumps({"object": "list", "data": [{"id": "test-model"}]}),
                    )
                elif self.path == "/load":
                    self._send(200, json.dumps({"model": "test-model", "state": "OK"}))
                elif self.path == "/metrics":
                    self._send(200, "vllm:gpu_cache_usage_perc 0.42\nvllm:num_requests_running 3\n")
                else:
                    self._send(404, "not found")

            def _send(self, code, body):
                payload = body.encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        return Handler

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def url(self):
        return f"http://127.0.0.1:{self.port}"


class SlowVLLMServer(StubVLLMServer):
    """A stub that responds slowly, for timeout testing."""

    @staticmethod
    def _make_handler():
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                time.sleep(2.0)
                payload = b"OK"
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        return Handler


class LargeMetricsServer(StubVLLMServer):
    """A stub whose /metrics body exceeds the probe's read bound."""

    @staticmethod
    def _make_handler():
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == "/metrics":
                    payload = (b"vllm:gpu_cache_usage_perc 0.5\n" + b"x" * 80 * 1024)
                else:
                    payload = b"OK"
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        return Handler


def free_port():
    """Return a currently-unused local port (socket is closed after)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class HelpTests(unittest.TestCase):
    def test_help_exits_zero_and_advertises_capabilities(self):
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("--check", proc.stdout)
        self.assertIn("health", proc.stdout)

    def test_usage_error_exits_two(self):
        proc = run_script("--not-a-real-flag")
        self.assertEqual(proc.returncode, 2)


class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = StubVLLMServer()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_health_check_passes(self):
        proc = run_script("--url", self.server.url(), "--check", "health")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("OK", proc.stdout)
        self.assertIn("health", proc.stdout)

    def test_models_check_parses_served_models(self):
        proc = run_script("--url", self.server.url(), "--check", "models", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = load_json(proc)
        checks = payload["checks"]
        self.assertEqual(checks[0]["ok"], True)
        self.assertIn("test-model", checks[0]["model_ids"])

    def test_all_checks_pass_with_json(self):
        proc = run_script("--url", self.server.url(), "--json")
        self.assertEqual(proc.returncode, 0)
        payload = load_json(proc)
        self.assertEqual(len(payload["checks"]), 5)
        for check in payload["checks"]:
            self.assertTrue(check["ok"], f"{check['name']} should pass: {check}")

    def test_metrics_check_reads_key_vllm_gauges(self):
        proc = run_script("--url", self.server.url(), "--check", "metrics", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = load_json(proc)
        observed = payload["checks"][0]["key_metrics_present"]
        self.assertTrue(observed["vllm:gpu_cache_usage_perc"])
        self.assertTrue(observed["vllm:num_requests_running"])

    def test_unreachable_server_fails_with_exit_one(self):
        proc = run_script("--url", f"http://127.0.0.1:{free_port()}", "--check", "health")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("FAIL", proc.stdout)

    def test_timeout_emits_documented_exit_code_124(self):
        slow = SlowVLLMServer()
        slow.start()
        try:
            proc = run_script("--url", slow.url(), "--check", "health", "--timeout", "0.5")
            self.assertEqual(proc.returncode, 124)
            self.assertIn("timed out", proc.stdout)
        finally:
            slow.stop()

    def test_metrics_read_is_bounded_and_reports_truncation(self):
        large = LargeMetricsServer()
        large.start()
        try:
            proc = run_script("--url", large.url(), "--check", "metrics", "--json")
            self.assertEqual(proc.returncode, 0)
            payload = load_json(proc)
            check = payload["checks"][0]
            self.assertTrue(check["ok"])
            self.assertTrue(check["truncated"])
            self.assertEqual(check["bytes_read"], 64 * 1024)
        finally:
            large.stop()

    def test_models_check_parses_from_stub(self):
        """The models check parses the stub's served model list (positive path)."""
        proc = run_script(
            "--url", f"http://127.0.0.1:{self.server.port}", "--check", "models", "--json"
        )
        payload = load_json(proc)
        self.assertEqual(payload["checks"][0]["ok"], True)


class ReadOnlyContractTests(unittest.TestCase):
    def test_script_never_opens_files_for_writing(self):
        source = (SCRIPT).read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            self.assertNotIn("'w'", stripped)
            self.assertNotIn('"w"', stripped)
            self.assertNotIn("'a'", stripped)
            self.assertNotIn('"a"', stripped)

    def test_script_only_issues_get_requests(self):
        source = (SCRIPT).read_text(encoding="utf-8")
        self.assertIn('method="GET"', source)


if __name__ == "__main__":
    unittest.main()
