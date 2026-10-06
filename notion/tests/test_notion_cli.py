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
    "properties": {
        "title": {"type": "title", "title": [{"plain_text": "Meeting notes"}]},
        "Status": {"id": "status-id", "type": "status", "status": {"id": "status-done", "name": "Done"}},
        "Notes": {"id": "rich-id", "type": "rich_text", "rich_text": [{"plain_text": "Verified details"}]},
        "Stage": {"type": "select", "select": {"id": "select-review", "name": "Review"}},
        "Approved": {"type": "checkbox", "checkbox": True},
        "Estimate": {"type": "number", "number": 4.5},
        "Notes": {"id": "rich-id", "type": "rich_text", "rich_text": [{"plain_text": "Verified details"}]},
    },
}


class StubNotionServer:
    """Minimal stub of the Notion API surface used by notion-cli."""

    def __init__(self):
        self.requests = []  # (method, path, body) recorded by the stub
        self.page = SAMPLE_PAGE
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
                if "/properties/status-id" in self.path:
                    self._respond({"object": "property_item", "id": "status-id", "type": "status",
                                   "status": {"id": "status-done", "name": "Done"}})
                elif "/properties/rich%3Aid" in self.path:
                    self._respond({"object": "list", "type": "property_item", "has_more": False,
                                   "next_cursor": None, "property_item": {"id": "rich%3Aid", "type": "rich_text"},
                                   "results": [{"object": "property_item", "id": "rich%3Aid", "type": "rich_text",
                                                "rich_text": {"plain_text": "first"}},
                                               {"object": "property_item", "id": "rich%3Aid", "type": "rich_text",
                                                "rich_text": {"plain_text": "second"}}]})
                elif "/properties/rich-id" in self.path:
                    query = self.path.split("?", 1)[1] if "?" in self.path else ""
                    if "start_cursor=next" in query:
                        results = [{"object": "property_item", "id": "rich-id", "type": "rich_text",
                                    "rich_text": {"plain_text": "second"}}]
                        has_more = False
                        cursor = None
                    else:
                        results = [{"object": "property_item", "id": "rich-id", "type": "rich_text",
                                    "rich_text": {"plain_text": "first"}}]
                        has_more = True
                        cursor = "next"
                    self._respond({"object": "list", "type": "property_item", "has_more": has_more,
                                   "next_cursor": cursor, "property_item": {"id": "rich-id", "type": "rich_text"},
                                   "results": results})
                elif "/properties/missing-has-more" in self.path:
                    self._respond({"object": "list", "type": "property_item",
                                   "property_item": {"id": "missing-has-more", "type": "rich_text"},
                                   "results": []})
                elif "/properties/missing-cursor" in self.path:
                    self._respond({"object": "list", "type": "property_item", "has_more": True,
                                   "property_item": {"id": "missing-cursor", "type": "rich_text"},
                                   "results": []})
                elif "/properties/missing-metadata" in self.path:
                    self._respond({"object": "list", "type": "property_item", "has_more": False,
                                   "results": []})
                elif "/properties/malformed-next" in self.path:
                    query = self.path.split("?", 1)[1] if "?" in self.path else ""
                    if "start_cursor=next" in query:
                        self._respond({"object": "page", "has_more": False})
                    else:
                        self._respond({"object": "list", "type": "property_item", "has_more": True,
                                       "next_cursor": "next",
                                       "property_item": {"id": "malformed-next", "type": "rich_text"},
                                       "results": []})
                elif "/properties/" in self.path:
                    self._respond({"message": "not_found"}, 404)
                elif self.path.startswith("/pages/"):
                    self._respond(stub.page)
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
        self.assertEqual(data["page"]["properties"]["Status"],
                         {"present": True, "type": "status", "value": {"id": "status-done", "name": "Done"},
                          "complete": True})

    def test_pages_get_preserves_typed_property_values(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "pages", "get", "--page-id", "page-1234")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        properties = load_json(proc)["page"]["properties"]
        self.assertEqual(properties["Stage"]["value"]["name"], "Review")
        self.assertIs(properties["Approved"]["value"], True)
        self.assertEqual(properties["Estimate"]["value"], 4.5)
        self.assertEqual(properties["Notes"]["value"], "Verified details")

    def test_pages_get_selected_absent_property_is_explicit(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "pages", "get", "--page-id", "page-1234",
                              "--property", "Status", "--property", "Missing")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        page = load_json(proc)["page"]
        self.assertEqual(page["properties_requested"], ["Status", "Missing"])
        self.assertEqual(page["properties"]["Status"]["value"]["name"], "Done")
        self.assertEqual(page["properties"]["Missing"], {"present": False})

    def test_selected_rich_text_property_reads_all_pages(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "2", "pages", "get", "--page-id", "page-1234",
                              "--property", "Notes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        prop = load_json(proc)["page"]["properties"]["Notes"]
        self.assertEqual(prop["value"], "firstsecond")
        self.assertTrue(prop["complete"])
        self.assertTrue(any("start_cursor=next" in path for method, path, _ in stub.requests if method == "GET"))

    def test_selected_property_id_is_not_double_encoded(self):
        page = dict(SAMPLE_PAGE)
        page["properties"] = dict(SAMPLE_PAGE["properties"],
                                  Notes={"id": "rich%3Aid", "type": "rich_text", "rich_text": []})
        with StubNotionServer() as stub:
            stub.page = page
            proc = run_script(base_env(stub), "--json", "pages", "get", "--page-id", "page-1234",
                              "--property", "Notes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(any("/properties/rich%3Aid" in path for method, path, _ in stub.requests if method == "GET"))

    def test_selected_property_limit_marks_incomplete_value(self):
        with StubNotionServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "1", "pages", "get", "--page-id", "page-1234",
                              "--property", "Notes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        prop = load_json(proc)["page"]["properties"]["Notes"]
        self.assertEqual(prop["value"], "first")
        self.assertFalse(prop["complete"])
        self.assertTrue(prop["has_more"])

    def test_malformed_property_pagination_never_reports_complete(self):
        cases = (("missing-has-more", "invalid_property_pagination_response"),
                 ("missing-cursor", "invalid_property_pagination_response"),
                 ("missing-metadata", "invalid_property_pagination_response"),
                 ("malformed-next", "invalid_property_pagination_response"))
        for property_id, reason in cases:
            with self.subTest(property_id=property_id), StubNotionServer() as stub:
                page = dict(SAMPLE_PAGE)
                page["properties"] = {"Notes": {"id": property_id, "type": "rich_text", "rich_text": []}}
                stub.page = page
                proc = run_script(base_env(stub), "--json", "pages", "get", "--page-id", "page-1234",
                                  "--property", "Notes")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                prop = load_json(proc)["page"]["properties"]["Notes"]
                self.assertFalse(prop["complete"])
                self.assertEqual(prop["incomplete_reason"], reason)

    def test_pages_get_marks_truncated_rich_text(self):
        long_text = "x" * 600
        page = dict(SAMPLE_PAGE)
        page["properties"] = dict(SAMPLE_PAGE["properties"],
                                  Notes={"type": "rich_text", "rich_text": [{"plain_text": long_text}]})
        summary = __import__("runpy").run_path(str(SCRIPT))["summarize_page"](page)
        self.assertTrue(summary["properties"]["Notes"]["truncated"])
        self.assertEqual(summary["properties"]["Notes"]["character_count"], 600)

    def test_page_summaries_distinguish_changed_and_unchanged_properties(self):
        import runpy
        summarize = runpy.run_path(str(SCRIPT))["summarize_page"]
        before = summarize(SAMPLE_PAGE)
        changed_page = dict(SAMPLE_PAGE)
        changed_page["properties"] = dict(SAMPLE_PAGE["properties"],
                                           Status={"type": "status", "status":
                                                   {"id": "status-progress", "name": "In progress"}})
        after = summarize(changed_page)
        self.assertNotEqual(before["properties"]["Status"], after["properties"]["Status"])
        self.assertEqual(before["properties"]["Approved"], after["properties"]["Approved"])

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
