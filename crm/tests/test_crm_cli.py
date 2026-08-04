#!/usr/bin/env python3
"""Deterministic tests for crm/scripts/crm-cli.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --limit, mutation gate, exit codes, JSON payloads). A local
stdlib HTTP server stubs the HubSpot CRM v3 API (contacts, deals, pipelines,
search), so no external network or HubSpot account is needed. Also asserts the
read-only contract: reads never call write methods, and the mutation gate
refuses to move a deal without --dry-run or --yes.
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
SCRIPT = ROOT / "scripts" / "crm-cli"

CONTACT = {"id": "51", "properties": {"firstname": "Ada", "lastname": "Lovelace",
                                      "email": "ada@example.com", "company": "Analytical",
                                      "createdate": "2026-01-01T00:00:00Z"}}
DEAL = {"id": "901", "properties": {"dealname": "Acme renewal", "amount": "12000",
                                    "pipeline": "default", "dealstage": "appointmentscheduled",
                                    "hs_lastmodifieddate": "2026-01-02T00:00:00Z"}}
PIPELINE = {"id": "default", "label": "Default pipeline",
            "stages": [{"id": "appointmentscheduled", "label": "Appointment Scheduled",
                        "displayOrder": 0}]}


class StubHubSpotServer:
    """Minimal stub of the HubSpot CRM v3 API surface used by crm-cli."""

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
                if "/objects/contacts?" in self.path:
                    self._json({"results": [CONTACT], "total": 1, "paging": {}})
                elif "/objects/contacts/" in self.path:
                    self._json(CONTACT)
                elif "/objects/deals?" in self.path:
                    self._json({"results": [DEAL], "total": 1, "paging": {}})
                elif "/pipelines/deals" in self.path:
                    self._json({"results": [PIPELINE]})
                else:
                    self._json({"message": "not_found"}, 404)

            def do_POST(self):  # noqa: N802
                body = self._read_body()
                stub.requests.append(("POST", self.path, body))
                if "/search" in self.path:
                    limit = body.get("limit", 20)
                    self._json({"results": [CONTACT][:limit], "total": 1})
                else:
                    self._json({"message": "not_found"}, 404)

            def do_PATCH(self):  # noqa: N802
                body = self._read_body()
                stub.requests.append(("PATCH", self.path, body))
                if "/objects/deals/" in self.path:
                    updated = json.loads(json.dumps(DEAL))
                    updated["properties"]["dealstage"] = body.get("properties", {}).get("dealstage")
                    self._json(updated)
                else:
                    self._json({"message": "not_found"}, 404)

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
    env["HUBSPOT_TOKEN"] = "pat-test"
    env["HUBSPOT_API_BASE"] = f"http://127.0.0.1:{stub.port}/"
    return env


def load_json(proc):
    return json.loads(proc.stdout)


class CrmCliTests(unittest.TestCase):
    def test_help_lists_json_and_bounded_reads(self):
        proc = run_script(dict(os.environ), "--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("--limit", proc.stdout)

    def test_help_works_without_token(self):
        env = dict(os.environ)
        env.pop("HUBSPOT_TOKEN", None)
        proc = run_script(env, "contacts", "list", "--help")
        self.assertEqual(proc.returncode, 0)

    def test_contacts_list(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "--json", "--limit", "5", "contacts", "list")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["contacts"][0]["email"], "ada@example.com")

    def test_contacts_get(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "--json", "contacts", "get", "--id", "51")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(load_json(proc)["contact"]["id"], "51")

    def test_contacts_search(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "--json", "contacts", "search", "--query", "ada")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["contacts"][0]["firstname"], "Ada")

    def test_search_sends_limit(self):
        with StubHubSpotServer() as stub:
            run_script(base_env(stub), "--json", "--limit", "3", "contacts", "search",
                       "--query", "ada")
        posts = [body for method, path, body in stub.requests
                 if method == "POST" and "/search" in path]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].get("limit"), 3)

    def test_deals_list_pipeline_view(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "--json", "deals", "list",
                              "--pipeline", "default", "--stage", "appointmentscheduled")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["deals"][0]["dealname"], "Acme renewal")
        gets = [path for method, path, _ in stub.requests if method == "GET"]
        self.assertTrue(any("objects/deals?" in path for path in gets))

    def test_pipelines_list(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "--json", "pipelines", "list")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["pipelines"][0]["id"], "default")
        self.assertEqual(data["pipelines"][0]["stages"][0]["id"], "appointmentscheduled")

    def test_update_stage_requires_confirmation(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "deals", "update-stage", "--id", "901",
                              "--stage", "closedwon")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to move", proc.stderr)
        self.assertEqual(stub.requests, [], "no API call may be made without confirmation")

    def test_update_stage_dry_run_does_not_patch(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "--json", "deals", "update-stage", "--id", "901",
                              "--stage", "closedwon", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertTrue(data["dry_run"])
        self.assertEqual(stub.requests, [], "dry-run must not reach the API")

    def test_update_stage_with_yes_patches(self):
        with StubHubSpotServer() as stub:
            proc = run_script(base_env(stub), "--json", "deals", "update-stage", "--id", "901",
                              "--stage", "closedwon", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = load_json(proc)
        self.assertEqual(data["deal"]["dealstage"], "closedwon")
        self.assertTrue(any(method == "PATCH" for method, _path, _body in stub.requests))

    def test_missing_token_errors_cleanly(self):
        env = dict(os.environ)
        env.pop("HUBSPOT_TOKEN", None)
        proc = run_script(env, "--json", "contacts", "list")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("HUBSPOT_TOKEN", proc.stdout)

    def test_read_only_contract_no_write_opens(self):
        source = SCRIPT.read_text()
        writes = [line for line in source.splitlines()
                  if line.strip().startswith("open(") and ("'w'" in line or '"w"' in line)]
        self.assertEqual(writes, [], "script must never open files in write mode")


if __name__ == "__main__":
    unittest.main()
