#!/usr/bin/env python3
"""Deterministic tests for slack/scripts/slack-cli.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --limit, mutation gate, exit codes, JSON payloads). A local
stdlib HTTP server stubs the Slack Web API methods, so no external network or
Slack workspace is needed. Also asserts the read-only contract: the script
never opens files in write mode, and the mutation gate refuses to send without
--dry-run or --yes.
"""
import json
import os
import socket
import subprocess
import sys
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "slack-cli"

VALID_CHANNEL = {"id": "C123", "name": "general", "is_channel": True, "is_private": False, "num_members": 42}
VALID_MESSAGE = {"ts": "1712345678.000001", "user": "U1", "type": "message",
                 "channel": "C123", "text": "hello from tests", "thread_ts": ""}


class StubSlackServer:
    """Minimal read-only stub of the Slack Web API surface."""

    def __init__(self):
        self.posted = []  # (method, fields) recorded by the stub
        handler = self._make_handler()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _make_handler(self):
        stub = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                fields = {k: v for k, v in urllib.parse.parse_qsl(raw.decode("utf-8"))}
                method = self.path.strip("/")
                stub.posted.append((method, fields))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                if method == "conversations.list":
                    payload = {"ok": True, "channels": [VALID_CHANNEL],
                               "response_metadata": {"next_cursor": ""}}
                elif method == "conversations.history":
                    payload = {"ok": True, "messages": [VALID_MESSAGE],
                               "response_metadata": {"next_cursor": ""}}
                elif method == "conversations.replies":
                    payload = {"ok": True, "messages": [dict(VALID_MESSAGE, thread_ts="1712345678.000001")],
                               "response_metadata": {"next_cursor": ""}}
                elif method == "chat.postMessage":
                    payload = {"ok": True, "ts": "1712345679.000002", "channel": fields.get("channel", ""),
                               "message": {"ts": "1712345679.000002", "user": "U1", "type": "message",
                                           "text": fields.get("text", "")}}
                elif method == "search.messages":
                    payload = {"ok": True,
                               "messages": {"total": 1, "matches": [dict(VALID_MESSAGE, channel="C123")]}}
                elif method == "files.list":
                    payload = {"ok": True, "files": [{"id": "F1", "name": "notes.md", "title": "notes",
                                                      "filetype": "text", "size": 512}],
                               "response_metadata": {"next_cursor": ""}}
                else:
                    payload = {"ok": False, "error": "method_not_supported"}
                self.wfile.write(json.dumps(payload).encode("utf-8"))

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
    env["SLACK_TOKEN"] = "xoxb-test-token"
    env["SLACK_API_BASE"] = f"http://127.0.0.1:{stub.port}/"
    return env


def load_json(proc):
    return json.loads(proc.stdout)


class SlackCliTests(unittest.TestCase):
    def test_help_lists_json_and_bounded_reads(self):
        proc = run_script(dict(os.environ), "--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("--limit", proc.stdout)

    def test_help_works_without_token(self):
        env = dict(os.environ)
        env.pop("SLACK_TOKEN", None)
        proc = run_script(env, "channels", "list", "--help")
        self.assertEqual(proc.returncode, 0)

    def test_channels_list_json(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "5", "channels", "list")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertTrue(data["ok"])
        self.assertEqual(data["channels"][0]["id"], "C123")

    def test_limit_is_bounded_in_request(self):
        with StubSlackServer() as stub:
            run_script(base_env(stub), "--json", "--limit", "3", "channels", "list")
            methods = [m for m, _ in stub.posted]
            fields = dict(stub.posted[methods.index("conversations.list")][1])
        self.assertEqual(fields.get("limit"), "3")

    def test_messages_send_requires_confirmation(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "messages", "send", "--channel", "C123",
                              "--text", "hello")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to send", proc.stderr)
        self.assertEqual(stub.posted, [], "no API call may be made without confirmation")

    def test_messages_send_dry_run_does_not_post(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "--json", "messages", "send", "--channel", "C123",
                              "--text", "hello", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertTrue(data["dry_run"])
        self.assertEqual(stub.posted, [], "dry-run must not reach the API")

    def test_messages_send_with_yes_posts(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "--json", "messages", "send", "--channel", "C123",
                              "--text", "hello", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["ts"], "1712345679.000002")
        methods = [m for m, _ in stub.posted]
        self.assertIn("chat.postMessage", methods)

    def test_messages_list(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "--json", "messages", "list", "--channel", "C123")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(load_json(proc)["messages"][0]["text"], "hello from tests")

    def test_threads_list(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "--json", "threads", "list",
                              "--channel", "C123", "--ts", "1712345678.000001")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(load_json(proc)["thread_ts"], "1712345678.000001")

    def test_search(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "--json", "search", "messages", "--query", "hello")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["total_matches"], 1)
        self.assertEqual(data["matches"][0]["channel"], "C123")

    def test_files_list(self):
        with StubSlackServer() as stub:
            proc = run_script(base_env(stub), "--json", "files", "list")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(load_json(proc)["files"][0]["id"], "F1")

    def test_missing_token_errors_cleanly(self):
        env = dict(os.environ)
        env.pop("SLACK_TOKEN", None)
        env["SLACK_API_BASE"] = "http://127.0.0.1:1/"
        proc = run_script(env, "--json", "channels", "list")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("SLACK_TOKEN", proc.stdout)

    def test_webhook_verify_valid_signature(self):
        import hashlib
        import hmac
        import time
        secret = "signing-secret"
        body = b'{"event": {"type": "message"}}'
        timestamp = str(int(time.time()))
        base = f"v0:{timestamp}:".encode() + body
        signature = "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()
        body_file = ROOT / "tests" / "webhook-body.json"
        body_file.write_bytes(body)
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file), "--signature", signature,
                              "--timestamp", timestamp, "--secret", secret)
        finally:
            body_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(load_json(proc)["verified"])

    def test_webhook_verify_rejects_bad_signature(self):
        import time
        body_file = ROOT / "tests" / "webhook-body.json"
        body_file.write_bytes(b'{"event": {}}')
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file),
                              "--signature", "v0=" + "0" * 64,
                              "--timestamp", str(int(time.time())), "--secret", "signing-secret")
        finally:
            body_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("does not match", proc.stdout)

    def test_webhook_verify_rejects_stale_timestamp(self):
        stale = str(int(__import__("time").time()) - 600)
        body_file = ROOT / "tests" / "webhook-body.json"
        body_file.write_bytes(b"{}")
        try:
            proc = run_script(dict(os.environ), "--json", "webhook", "verify",
                              "--body-file", str(body_file),
                              "--signature", "v0=" + "0" * 64,
                              "--timestamp", stale, "--secret", "s")
        finally:
            body_file.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("replay window", proc.stdout)

    def test_read_only_contract_no_write_opens(self):
        source = SCRIPT.read_text()
        writes = [line for line in source.splitlines()
                  if line.strip().startswith("open(") and ("'w'" in line or '"w"' in line)]
        self.assertEqual(writes, [], "script must never open files in write mode")


if __name__ == "__main__":
    unittest.main()
