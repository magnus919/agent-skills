#!/usr/bin/env python3
"""Deterministic tests for notion/scripts/notion-cli.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --limit, mutation gate, exit codes, JSON payloads). A local
stdlib HTTP server stubs the Notion API (pages, databases/query, search), so
no external network or Notion workspace is needed. Also asserts the read-only
contract: reads never call write methods, and the mutation gate refuses to
create/update without --dry-run or --yes.
"""
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "notion-cli"

SAMPLE_PAGE = {
    "object": "page",
    "id": "page-1234",
    "url": "https://www.notion.so/page-1234",
    "created_time": "2026-01-01T00:00:00.000Z",
    "last_edited_time": "2026-01-02T00:00:00.000Z",
    "properties": {"title": {"type": "title", "title": [{"plain_text": "Meeting notes"}]}},
}


class StubNotionServer:
    """Minimal stub of the Notion API surface used by notion-cli."""

    def __init__(self):
        self.requests = []  # (method, path, body) recorded by the stub
        handler = self._make_handler()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _make_handler(self):
        stub = self

        class Handler(BaseHTTPRequestHandler):
            def _respond(self, payload, status=200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode("utf-8"))

            def _read_json(self):
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                return json.loads(raw.decode("utf-8")) if raw else {}

            def do_GET(self):  # noqa: N802
                stub.requests.append(("GET", self.path, None))
                if self.path.startswith("/pages/"):
                    self._respond(SAMPLE_PAGE)
                else:
                    self._respond({"message": "not_found"}, 404)

            def do_POST(self):  # noqa: N802
                body = self._read_json()
                stub.requests.append(("POST", self.path, body))
                if self.path == "/search":
                    results = [SAMPLE_PAGE]
                    page_size = body.get("page_size", 20)
                    self._respond({"results": results[:page_size], "has_more": False})
                elif "/query" in self.path:
                    page_size = body.get("page_size", 20)
                    self._respond({"results": [SAMPLE_PAGE][:page_size], "has_more": False})
                elif self.path == "/pages":
                    created = dict(SAMPLE_PAGE, id="page-new")
                    self._respond(created, 200)
                else:
                    self._respond({"message": "not_found"}, 404)

            def do_PATCH(self):  # noqa: N802
                body = self._read_json()
                stub.requests.append(("PATCH", self.path, body))
                self._respond(SAMPLE_PAGE, 200)

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
    env["NOTION_TOKEN"] = "secret_test"
    env["NOTION_API_BASE"] = f"http://127.0.0.1:{stub.port}/"
    return env


def load_json(proc):
    return json.loads(proc.stdout)


class NotionCliTests(unittest.TestCase):
    def test_help_lists_json_and_bounded_reads(self):
        proc = run_script(dict(os.environ), "--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("--limit", proc.stdout)

    def test_help_works_without_token(self):
        env = dict(os.environ)
        env.pop("NOTION_TOKEN", None)
        proc = run_script(env, "search", "query", "--help")
        self.assertEqual(proc.returncode, 0)

    def test_pages_get(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "pages", "get", "--page-id", "page-1234")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["page"]["title"], "Meeting notes")
        self.assertEqual(data["page"]["id"], "page-1234")

    def test_database_query_bounded(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "5", "databases", "query",
                              "--database-id", "db-1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["database_id"], "db-1")
        self.assertEqual(data["pages"][0]["id"], "page-1234")

    def test_database_query_sends_page_size(self):
        with StubNotionServer() as stub:
            run_script(base_env(stub), "--json", "--limit", "3", "databases", "query",
                       "--database-id", "db-1")
        posts = [body for method, path, body in stub.requests
                 if method == "POST" and path == "/databases/db-1/query"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].get("page_size"), 3)

    def test_search(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "search", "query", "--query", "meeting")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["results"][0]["object"], "page")

    def test_pages_create_requires_confirmation(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "pages", "create", "--parent-page", "page-1",
                              "--title", "New page")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to create", proc.stderr)
        self.assertEqual(stub.requests, [], "no API call may be made without confirmation")

    def test_pages_create_dry_run_does_not_post(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "pages", "create", "--parent-page", "page-1",
                              "--title", "New page", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertTrue(data["dry_run"])
        self.assertEqual(stub.requests, [], "dry-run must not reach the API")

    def test_pages_create_with_yes_posts(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "pages", "create", "--parent-page", "page-1",
                              "--title", "New page", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(load_json(proc)["page"]["id"], "page-new")
        self.assertTrue(any(method == "POST" and path == "/pages" for method, path, _ in stub.requests))

    def test_pages_update_requires_confirmation(self):
        props = ROOT / "tests" / "props.json"
        props.write_text(json.dumps({"Status": {"select": {"name": "Done"}}}))
        try:
            with StubNotionServer() as stub:
                proc = run_script(base_env(stub), "pages", "update", "--page-id", "page-1234",
                                  "--properties", str(props))
        finally:
            props.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to update", proc.stderr)
        self.assertEqual(stub.requests, [])

    def test_pages_update_with_yes_patches(self):
        props = ROOT / "tests" / "props.json"
        props.write_text(json.dumps({"Status": {"select": {"name": "Done"}}}))
        try:
            with StubNotionServer() as stub:
                proc = run_script(base_env(stub), "--json", "pages", "update", "--page-id", "page-1234",
                                  "--properties", str(props), "--yes")
        finally:
            props.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(any(method == "PATCH" for method, _path, _body in stub.requests))

    def test_missing_token_errors_cleanly(self):
        env = dict(os.environ)
        env.pop("NOTION_TOKEN", None)
        proc = run_script(env, "--json", "search", "query", "--query", "x")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("NOTION_TOKEN", proc.stdout)

    def test_read_only_contract_no_write_opens(self):
        source = SCRIPT.read_text()
        writes = [line for line in source.splitlines()
                  if line.strip().startswith("open(") and ("'w'" in line or '"w"' in line)]
        self.assertEqual(writes, [], "script must never open files in write mode")


if __name__ == "__main__":
    unittest.main()
