import hashlib
import hmac
import json
import os
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

CLI = Path(__file__).parents[1] / "scripts" / "fireflies"

class Handler(BaseHTTPRequestHandler):
    calls = []
    response = {"data": {"ok": True}}
    status = 200
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.__class__.calls.append((dict(self.headers), json.loads(body)))
        self.send_response(self.__class__.status); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps(self.__class__.response).encode())
    def log_message(self, *_): pass

class FirefliesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
        cls.endpoint = "http://127.0.0.1:%s/graphql" % cls.server.server_port
    @classmethod
    def tearDownClass(cls): cls.server.shutdown()
    def run_cli(self, *args, key=False):
        env = os.environ.copy(); env.pop("FIREFLIES_API_KEY", None)
        if key: env["FIREFLIES_API_KEY"] = "test-key"
        return subprocess.run(["python3", str(CLI), *args], text=True, capture_output=True, env=env)
    def test_dry_run_needs_no_key_and_no_http(self):
        Handler.calls.clear(); result=self.run_cli("transcripts","list","--dry-run","--json")
        self.assertEqual(result.returncode,0); self.assertEqual(Handler.calls,[]); self.assertTrue(json.loads(result.stdout)["dry_run"])
    def test_read_uses_bearer_and_payload(self):
        Handler.calls.clear(); Handler.response={"data":{"users":[]}}
        result=self.run_cli("--endpoint",self.endpoint,"users","list","--json",key=True)
        self.assertEqual(result.returncode,0); self.assertEqual(Handler.calls[-1][0]["Authorization"],"Bearer test-key"); self.assertIn("query Users",Handler.calls[-1][1]["query"])
    def test_graphql_error_json_and_exit_five(self):
        Handler.response={"errors":[{"message":"denied","code":"auth_failed"}]}
        result=self.run_cli("--endpoint",self.endpoint,"users","list","--json",key=True)
        self.assertEqual(result.returncode,5); self.assertEqual(json.loads(result.stdout)["errors"][0]["message"],"denied"); self.assertIn("GraphQL error",result.stderr)
        Handler.response={"data":{"ok":True}}
    def test_http_error_with_graphql_errors_exits_five(self):
        Handler.status=400; Handler.response={"errors":[{"message":"denied","code":"auth_failed"}]}
        result=self.run_cli("--endpoint",self.endpoint,"users","list","--json",key=True)
        self.assertEqual(result.returncode,5); self.assertEqual(json.loads(result.stdout)["errors"][0]["message"],"denied"); self.assertIn("GraphQL error",result.stderr)
        Handler.status=200; Handler.response={"data":{"ok":True}}
    def test_generic_guards(self):
        self.assertEqual(self.run_cli("query","--document","mutation { x }","--json").returncode,2)
        self.assertEqual(self.run_cli("mutation","--document","mutation { x }","--json").returncode,6)
    def test_limit_json_and_help_examples(self):
        self.assertEqual(self.run_cli("transcripts","list","--limit","51","--json").returncode,2)
        result=self.run_cli("transcripts","list","--dry-run","--json"); json.loads(result.stdout); self.assertEqual(result.stderr,"")
        self.assertIn("Examples:",self.run_cli("transcripts","list","--help").stdout)
    def test_webhook_signatures(self):
        with tempfile.NamedTemporaryFile("wb",delete=False) as f: f.write(b'{"event":"meeting.transcribed"}'); path=f.name
        digest=hmac.new(b"test",Path(path).read_bytes(),hashlib.sha256).hexdigest()
        self.assertTrue(json.loads(self.run_cli("webhook","verify","--secret","test","--signature","sha256="+digest,"--body",path,"--json").stdout)["valid"])
        self.assertFalse(json.loads(self.run_cli("webhook","verify","--secret","test","--signature","sha256=bad","--body",path,"--json").stdout)["valid"])
        os.unlink(path)
    def test_mutation_dry_run_payload(self):
        result=self.run_cli("meetings","rename","abc","--title","New","--dry-run","--json")
        payload=json.loads(result.stdout)["payload"]; self.assertIn("updateMeetingTitle",payload["query"]); self.assertEqual(payload["variables"]["input"]["id"],"abc")
    def test_source_faithful_dry_run_payloads(self):
        live=json.loads(self.run_cli("live","add","--meeting-id","meeting-id","--action-item","Follow up","--dry-run","--json").stdout)["payload"]
        self.assertIn("createLiveActionItem(input: $input) { success }",live["query"])
        self.assertEqual(live["variables"],{"input":{"meeting_id":"meeting-id","prompt":"Follow up"}})
        deleted=json.loads(self.run_cli("askfred","delete","thread-id","--dry-run","--json").stdout)["payload"]
        self.assertIn("id title transcript_id user_id created_at",deleted["query"])
        self.assertEqual(deleted["variables"],{"id":"thread-id"})
        analytics=json.loads(self.run_cli("analytics","--start","2026-01-01","--end","2026-01-31","--dry-run","--json").stdout)["payload"]
        self.assertIn("$startTime",analytics["query"]); self.assertIn("$endTime",analytics["query"])
        self.assertEqual(analytics["variables"],{"startTime":"2026-01-01","endTime":"2026-01-31"})
        transcript=json.loads(self.run_cli("transcripts","get","transcript-id","--dry-run","--json").stdout)["payload"]
        self.assertIn("negative_pct neutral_pct positive_pct",transcript["query"])
        audit=json.loads(self.run_cli("audit-events","--filter",'{"category":"MEETING_OPERATIONS"}',"--dry-run","--json").stdout)["payload"]
        self.assertIn("events { id time action actor { user_id } resource { type id } }",audit["query"])

if __name__ == "__main__": unittest.main()
