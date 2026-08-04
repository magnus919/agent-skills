#!/usr/bin/env python3
"""Deterministic tests for email/scripts/email-cli.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --limit, mutation gate, exit codes, JSON payloads). A local
stdlib HTTP server stubs the SendGrid v3 API (mail/send, suppression
bounces/spam_reports). Webhook signature verification uses fixed ECDSA P-256
test vectors generated offline with OpenSSL (independent of this
implementation), so the valid-signature path is cross-checked against a
reference signing tool. No external network is needed.
"""
import base64
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "email-cli"

# Fixed ECDSA P-256 vectors: signature over SHA256("1712345678" + body)
# generated with OpenSSL (openssl dgst -sha256 -sign) as an independent
# cross-check of the stdlib verifier embedded in email-cli.
WEBHOOK_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwOVzJT7nlfguzr/GSiBh0EAp7fQX
YqMhYoJ0lChYC6LnXnC1y5BQiF5SxM7tjj69z9NeMnM9fQvZ4h65V0AYaQ==
-----END PUBLIC KEY-----
"""
WEBHOOK_BODY = b'{"RecordType":"Delivery","MessageID":"m1"}'
WEBHOOK_TIMESTAMP = "1712345678"
WEBHOOK_SIGNATURE = "MEUCID/YPP4118Tr+6IPyV+OlrV0IktxgRWcQk+a2BOKkeP/AiEA7XPfz1DejTxPuCXkFCnXEPhSPy4L2nDwuvC20TZBiZ8="

BOUNCE = {"email": "bad@example.com", "created": "2026-08-01T00:00:00Z",
          "reason": "550 invalid mailbox", "status": "5.1.1"}
SPAM = {"email": "spam@example.com", "created": "2026-08-01T00:00:00Z",
        "ip": "1.2.3.4", "reason": "user complaint"}


class StubSendGridServer:
    """Minimal stub of the SendGrid v3 API surface used by email-cli."""

    def __init__(self):
        self.requests = []  # (method, path, body)
        handler = self._make_handler()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _make_handler(self):
        stub = self

        class Handler(BaseHTTPRequestHandler):
            def _read_body(self):
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                return json.loads(raw.decode("utf-8")) if raw else {}

            def _json(self, payload, status=200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode("utf-8"))

            def do_GET(self):  # noqa: N802
                stub.requests.append(("GET", self.path, None))
                if "/suppression/bounces" in self.path:
                    self._json([BOUNCE])
                elif "/suppression/spam_reports" in self.path:
                    self._json([SPAM])
                else:
                    self._json({"errors": [{"message": "not_found"}]}, 404)

            def do_POST(self):  # noqa: N802
                body = self._read_body()
                stub.requests.append(("POST", self.path, body))
                if self.path == "/v3/mail/send":
                    self.send_response(202)
                    self.send_header("X-Message-Id", "msg-test-0001")
                    self.end_headers()
                else:
                    self._json({"errors": [{"message": "not_found"}]}, 404)

            def log_message(self, *args):  # silence stderr
                pass

        return Handler

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


def run_script(env, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def base_env(stub):
    env = dict(os.environ)
    env["SENDGRID_API_KEY"] = "SG.test-key"
    env["SENDGRID_API_BASE"] = f"http://127.0.0.1:{stub.port}/v3"
    return env


def load_json(proc):
    return json.loads(proc.stdout)


def write_webhook_files(tmpdir):
    body_file = tmpdir / "webhook-body.json"
    key_file = tmpdir / "public-key.pem"
    body_file.write_bytes(WEBHOOK_BODY)
    key_file.write_text(WEBHOOK_PUBLIC_KEY)
    return body_file, key_file


class EmailCliTests(unittest.TestCase):
    def test_help_lists_json_and_bounded_reads(self):
        proc = run_script(dict(os.environ), "--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("--limit", proc.stdout)

    def test_help_works_without_api_key(self):
        env = dict(os.environ)
        env.pop("SENDGRID_API_KEY", None)
        proc = run_script(env, "deliverability", "bounces", "--help")
        self.assertEqual(proc.returncode, 0)

    def test_send_requires_confirmation(self):
        with StubSendGridServer() as stub:
            proc = run_script(base_env(stub), "send", "--to", "a@example.com",
                              "--from", "b@example.com", "--subject", "Hi", "--body", "Hello")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to send", proc.stderr)
        self.assertEqual(stub.requests, [], "no API call may be made without confirmation")

    def test_send_dry_run_does_not_post(self):
        with StubSendGridServer() as stub:
            proc = run_script(base_env(stub), "--json", "send", "--to", "a@example.com",
                              "--from", "b@example.com", "--subject", "Hi", "--body", "Hello",
                              "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertTrue(data["dry_run"])
        self.assertEqual(stub.requests, [], "dry-run must not reach the API")

    def test_send_with_yes_posts(self):
        with StubSendGridServer() as stub:
            proc = run_script(base_env(stub), "--json", "send", "--to", "a@example.com",
                              "--from", "b@example.com", "--subject", "Hi", "--body", "Hello",
                              "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["message_id"], "msg-test-0001")
        posts = [body for method, path, body in stub.requests
                 if method == "POST" and path == "/v3/mail/send"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["personalizations"][0]["to"][0]["email"], "a@example.com")

    def test_deliverability_bounces(self):
        with StubSendGridServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "5", "deliverability", "bounces")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["kind"], "bounces")
        self.assertEqual(data["items"][0]["email"], "bad@example.com")

    def test_deliverability_spam_reports(self):
        with StubSendGridServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "5", "deliverability", "spam-reports")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["kind"], "spam_reports")
        self.assertEqual(data["items"][0]["email"], "spam@example.com")

    def test_deliverability_limit_is_bounded_in_request(self):
        with StubSendGridServer() as stub:
            run_script(base_env(stub), "--json", "--limit", "7", "deliverability", "bounces")
        gets = [path for method, path, _ in stub.requests if method == "GET"]
        self.assertTrue(any("/suppression/bounces?limit=7" in path for path in gets))

    def test_webhook_verify_valid_signature(self):
        tmp = ROOT / "tests"
        body_file, key_file = write_webhook_files(tmp)
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file), "--signature", WEBHOOK_SIGNATURE,
                              "--timestamp", WEBHOOK_TIMESTAMP,
                              "--public-key-file", str(key_file), "--max-age", "0")
        finally:
            body_file.unlink(missing_ok=True)
            key_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(load_json(proc)["verified"])

    def test_webhook_verify_rejects_tampered_body(self):
        tmp = ROOT / "tests"
        body_file = tmp / "webhook-body.json"
        key_file = tmp / "public-key.pem"
        body_file.write_bytes(b'{"RecordType":"Delivery","MessageID":"FORGED"}')
        key_file.write_text(WEBHOOK_PUBLIC_KEY)
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file), "--signature", WEBHOOK_SIGNATURE,
                              "--timestamp", WEBHOOK_TIMESTAMP,
                              "--public-key-file", str(key_file), "--max-age", "0")
        finally:
            body_file.unlink(missing_ok=True)
            key_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("does not match", proc.stdout)

    def test_webhook_verify_rejects_wrong_key(self):
        tmp = ROOT / "tests"
        body_file, key_file = write_webhook_files(tmp)
        other_key = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEefPWWSDlPHw0mRIqmQHcvmNx6ArM
SCPBuBGQ9ObEdv7Wyfnu/T99Aa1eD3Nfd3YG+WKUvNUEw5qXX2EXJIP/Kw==
-----END PUBLIC KEY-----
"""
        key_file.write_text(other_key)
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file), "--signature", WEBHOOK_SIGNATURE,
                              "--timestamp", WEBHOOK_TIMESTAMP,
                              "--public-key-file", str(key_file), "--max-age", "0")
        finally:
            body_file.unlink(missing_ok=True)
            key_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("does not match", proc.stdout)

    def test_webhook_verify_rejects_stale_timestamp(self):
        tmp = ROOT / "tests"
        body_file, key_file = write_webhook_files(tmp)
        stale = str(int(__import__("time").time()) - 3600)
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file), "--signature", WEBHOOK_SIGNATURE,
                              "--timestamp", stale, "--public-key-file", str(key_file))
        finally:
            body_file.unlink(missing_ok=True)
            key_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("replay window", proc.stdout)

    def test_webhook_verify_rejects_malformed_signature(self):
        tmp = ROOT / "tests"
        body_file, key_file = write_webhook_files(tmp)
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file), "--signature", "not-base64!!",
                              "--timestamp", WEBHOOK_TIMESTAMP,
                              "--public-key-file", str(key_file), "--max-age", "0")
        finally:
            body_file.unlink(missing_ok=True)
            key_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("base64", proc.stdout)

    def test_missing_api_key_errors_cleanly(self):
        env = dict(os.environ)
        env.pop("SENDGRID_API_KEY", None)
        proc = run_script(env, "--json", "deliverability", "bounces")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("SENDGRID_API_KEY", proc.stdout)

    def test_read_only_contract_no_write_opens(self):
        source = SCRIPT.read_text()
        writes = [line for line in source.splitlines()
                  if line.strip().startswith("open(") and ("'w'" in line or '"w"' in line)]
        self.assertEqual(writes, [], "script must never open files in write mode")


if __name__ == "__main__":
    unittest.main()
