#!/usr/bin/env python3
"""Deterministic tests for litellm/scripts/litellm-health.

The probe runs as a subprocess so every assertion lands on the real CLI:
--help, --json, --check subsets, --key handling, exit codes, and JSON
payloads. A local stdlib HTTP server impersonates the four LiteLLM gateway
routes the probe reads, so no network or real proxy is involved. The final
test class pins the probe's read-only contract twice over: against observed
stub traffic (GET only) and against the script source (no write-mode opens).
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
SCRIPT = ROOT / "scripts" / "litellm-health"

MASTER_KEY = "sk-test-master-key"


def run_probe(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def parse_stdout_json(proc):
    return json.loads(proc.stdout)


class FakeGatewayRoutes:
    """Route table + request journal shared by the fake gateway servers."""

    def __init__(self):
        self.seen = []

    def handler_class(self):
        journal = self.seen

        class Routes(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _bearer(self):
                return self.headers.get("Authorization", "")

            def _reply(self, code, payload):
                body = payload.encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                journal.append(("GET", self.path))
                if self.path == "/health/liveliness":
                    self._reply(200, "I'm alive!")
                elif self.path == "/health/readiness":
                    self._reply(200, json.dumps({"status": "healthy", "db": "connected"}))
                elif self.path == "/v1/models":
                    if self._bearer() != f"Bearer {MASTER_KEY}":
                        self._reply(401, json.dumps({"error": "Unauthorized"}))
                    else:
                        self._reply(
                            200,
                            json.dumps(
                                {
                                    "object": "list",
                                    "data": [
                                        {"id": "gpt-4o"},
                                        {"id": "claude-sonnet"},
                                    ],
                                }
                            ),
                        )
                elif self.path == "/model/info":
                    if self._bearer() != f"Bearer {MASTER_KEY}":
                        self._reply(401, json.dumps({"error": "Unauthorized"}))
                    else:
                        self._reply(
                            200,
                            json.dumps(
                                [
                                    {
                                        "model_name": "gpt-4o",
                                        "litellm_params": {"api_key": "*************"},
                                        "model_info": {"max_tokens": 16384},
                                    }
                                ]
                            ),
                        )
                else:
                    self._reply(404, "not found")

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0) or 0)
                if length:
                    self.rfile.read(length)
                journal.append(("POST", self.path))
                self._reply(405, "probe must never POST")

        return Routes


class FakeGatewayServer:
    """One-shot ThreadingHTTPServer bound to an ephemeral loopback port."""

    def __init__(self, routes):
        self.routes = routes
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), routes.handler_class())
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}"


def idle_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def server_with_overridden_get(get_behavior):
    """Build a running fake gateway whose GET replies come from get_behavior.

    get_behavior(handler) is called with the live handler instance so it can
    use _reply(). The journal still records each GET.
    """
    routes = FakeGatewayRoutes()
    base_handler_class = routes.handler_class()

    class OverriddenRoutes(base_handler_class):
        def do_GET(self):
            routes.seen.append(("GET", self.path))
            get_behavior(self)

    server = FakeGatewayServer.__new__(FakeGatewayServer)
    server.routes = routes
    server.httpd = ThreadingHTTPServer(("127.0.0.1", 0), OverriddenRoutes)
    server.port = server.httpd.server_address[1]
    server.thread = threading.Thread(target=server.httpd.serve_forever, daemon=True)
    server.start()
    return server


class CliSurfaceTests(unittest.TestCase):
    def test_help_without_any_server(self):
        proc = run_probe("--help")
        self.assertEqual(proc.returncode, 0)
        for flag in ("--json", "--check", "--key", "--timeout"):
            self.assertIn(flag, proc.stdout)

    def test_unknown_flag_is_a_usage_error(self):
        proc = run_probe("--bogus")
        self.assertEqual(proc.returncode, 2)

    def test_zero_timeout_rejected_as_usage_error(self):
        proc = run_probe("--timeout", "0", "--check", "health")
        self.assertEqual(proc.returncode, 2)

    def test_negative_timeout_rejected_as_usage_error(self):
        proc = run_probe("--timeout", "-3", "--check", "health")
        self.assertEqual(proc.returncode, 2)


class LivenessReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = FakeGatewayRoutes()
        cls.gateway = FakeGatewayServer(cls.routes)
        cls.gateway.start()

    @classmethod
    def tearDownClass(cls):
        cls.gateway.stop()

    def test_liveliness_ok_body_and_exit_code(self):
        proc = run_probe(
            "--url", self.gateway.url, "--check", "health", "--json"
        )
        self.assertEqual(proc.returncode, 0)
        check = parse_stdout_json(proc)["checks"][0]
        self.assertTrue(check["ok"])
        self.assertEqual(check["status_code"], 200)
        self.assertIn("alive", check["body"].lower())

    def test_readiness_reports_db_state(self):
        proc = run_probe(
            "--url", self.gateway.url, "--check", "readiness", "--json"
        )
        self.assertEqual(proc.returncode, 0)
        check = parse_stdout_json(proc)["checks"][0]
        self.assertTrue(check["ok"])
        self.assertEqual((check["status"], check["db"]), ("healthy", "connected"))

    def test_readiness_503_fails_with_database_hint(self):
        def always_503(inner_self):
            inner_self._reply(503, json.dumps({"error": "db unavailable"}))

        gateway = server_with_overridden_get(always_503)
        try:
            proc = run_probe(
                "--url", gateway.url, "--check", "readiness", "--json"
            )
            self.assertEqual(proc.returncode, 1)
            check = parse_stdout_json(proc)["checks"][0]
            self.assertFalse(check["ok"])
            self.assertEqual(check["status_code"], 503)
            self.assertIn("database", check["hint"].lower())
        finally:
            gateway.stop()

    def test_liveliness_500_fails(self):
        def broken_liveliness(inner_self):
            inner_self._reply(500, "boom")

        gateway = server_with_overridden_get(broken_liveliness)
        try:
            proc = run_probe("--url", gateway.url, "--check", "health", "--json")
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(parse_stdout_json(proc)["checks"][0]["ok"])
        finally:
            gateway.stop()


class KeyedRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = FakeGatewayRoutes()
        cls.gateway = FakeGatewayServer(cls.routes)
        cls.gateway.start()

    @classmethod
    def tearDownClass(cls):
        cls.gateway.stop()

    def test_models_without_key_is_reported_not_run(self):
        proc = run_probe("--url", self.gateway.url, "--check", "models", "--json")
        self.assertEqual(proc.returncode, 1)
        check = parse_stdout_json(proc)["checks"][0]
        self.assertTrue(check["skipped_missing_key"])
        self.assertFalse(check["ok"])

    def test_wrong_key_surfaces_the_401(self):
        proc = run_probe(
            "--url",
            self.gateway.url,
            "--check",
            "models",
            "--key",
            "sk-not-the-key",
            "--json",
        )
        self.assertEqual(proc.returncode, 1)
        check = parse_stdout_json(proc)["checks"][0]
        self.assertEqual(check["status_code"], 401)
        self.assertIn("key", check["hint"].lower())

    def test_models_lists_aliases_for_master_key(self):
        proc = run_probe(
            "--url", self.gateway.url, "--check", "models", "--key", MASTER_KEY, "--json"
        )
        self.assertEqual(proc.returncode, 0)
        check = parse_stdout_json(proc)["checks"][0]
        self.assertTrue(check["ok"])
        self.assertEqual(check["model_ids"], ["gpt-4o", "claude-sonnet"])

    def test_model_info_counts_registered_deployments(self):
        proc = run_probe(
            "--url",
            self.gateway.url,
            "--check",
            "model_info",
            "--key",
            MASTER_KEY,
            "--json",
        )
        self.assertEqual(proc.returncode, 0)
        check = parse_stdout_json(proc)["checks"][0]
        self.assertTrue(check["ok"])
        self.assertEqual(check["deployment_count"], 1)


class ExitCodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = FakeGatewayRoutes()
        cls.gateway = FakeGatewayServer(cls.routes)
        cls.gateway.start()

    @classmethod
    def tearDownClass(cls):
        cls.gateway.stop()

    def test_everything_green_is_exit_zero(self):
        proc = run_probe(
            "--url",
            self.gateway.url,
            "--check",
            "health",
            "--check",
            "readiness",
            "--check",
            "models",
            "--check",
            "model_info",
            "--key",
            MASTER_KEY,
            "--json",
        )
        self.assertEqual(proc.returncode, 0)
        checks = parse_stdout_json(proc)["checks"]
        self.assertEqual(len(checks), 4)
        for check in checks:
            self.assertTrue(check["ok"], f"{check['name']} should pass: {check}")

    def test_dead_port_maps_to_exit_one(self):
        proc = run_probe(
            "--url", f"http://127.0.0.1:{idle_port()}", "--check", "health"
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("FAIL", proc.stdout)

    def test_hanging_route_maps_to_exit_124(self):
        def sleepy_get(inner_self):
            time.sleep(2.0)
            inner_self._reply(200, "I'm alive!")

        gateway = server_with_overridden_get(sleepy_get)
        try:
            proc = run_probe(
                "--url", gateway.url, "--check", "health", "--timeout", "0.5"
            )
            self.assertEqual(proc.returncode, 124)
            self.assertIn("timed out", proc.stdout)
        finally:
            gateway.stop()


class ReadOnlyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = FakeGatewayRoutes()
        cls.gateway = FakeGatewayServer(cls.routes)
        cls.gateway.start()

    @classmethod
    def tearDownClass(cls):
        cls.gateway.stop()

    def test_observed_traffic_is_exclusively_get(self):
        marker = len(self.routes.seen)
        run_probe(
            "--url",
            self.gateway.url,
            "--check",
            "health",
            "--check",
            "readiness",
            "--check",
            "models",
            "--check",
            "model_info",
            "--key",
            MASTER_KEY,
        )
        issued = list(self.routes.seen[marker:])
        self.assertGreater(len(issued), 0, "probe made no requests")
        for method, path in issued:
            self.assertEqual(
                method, "GET", f"probe issued {method} against {path}"
            )

    def test_source_contains_no_write_mode_file_opens(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for forbidden in ("'w'", '"w"', "'a'", '"a"'):
                self.assertNotIn(forbidden, stripped)

    def test_source_declares_get_and_no_other_method(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('method="GET"', source)
        for other in ('method="POST"', 'method="PUT"', 'method="DELETE"', "data="):
            self.assertNotIn(other, source)


if __name__ == "__main__":
    unittest.main()
