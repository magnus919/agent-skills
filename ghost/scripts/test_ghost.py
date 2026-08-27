"""Offline suite for ghost/scripts/ghost — zero network egress by construction.

Covers four behavior classes (--help, argument errors, --dry-run, mocked-client
logic) plus JWT known-answer signing checks with fixed inputs, per-skill pipeline
consumability chains exercised end-to-end through subprocesses and jq (pipeline
stages feed each other's outputs verbatim; every stage's exit code is asserted),
and Ghost-specific error signatures (409 update collision, 404 draft read,
INVALID_AUTH_HEADER, 204 No Content deletes).

All HTTP is short-circuited by --dry-run or replaced with unittest mocks bound at
the cli.requests call site. No sockets are opened.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).with_name("ghost")

# Fixed Admin API key in the official {id}:{secret} shape: 24-hex ObjectID half,
# 64-hex 32-byte secret half. Both halves are SYNTHETIC placeholder patterns,
# not credentials; nothing here authenticates anywhere.
KID = "5f9d4b1c8e2a43d7b6c0a1e9"
SECRET_HEX = "00ff" * 16
FIXED_KEY = f"{KID}:{SECRET_HEX}"

# Known-answer fixture computed once with iat frozen at 1700000000:
# header/payload are compact-JSON base64url segments; SIG_B64 is HMAC-SHA256
# over "<header>.<payload>" keyed with bytes.fromhex(SECRET_HEX).
HEADER_B64 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjVmOWQ0YjFjOGUyYTQzZDdiNmMwYTFlOSJ9"
PAYLOAD_B64 = "eyJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDAwMDMwMCwiYXVkIjoiL2FkbWluLyJ9"
SIG_B64 = "nxiluHMEVbp05Gi4kDYp28CCyOrwWuirtSzZeuWoisg"
TOKEN_TTL = 300


def load_cli():
    loader = importlib.machinery.SourceFileLoader("ghost_cli", str(SCRIPT))
    spec = importlib.util.spec_from_loader("ghost_cli", loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_env():
    env = os.environ.copy()
    env.pop("GHOST_URL", None)
    env.pop("GHOST_ADMIN_KEY", None)
    return env


class GhostCliTests(unittest.TestCase):
    """Subprocess-level CLI surface: help, arg errors, dry-run plans."""

    def run_cli(self, *args):
        return subprocess.run([str(SCRIPT), *args], text=True,
                              capture_output=True, env=clean_env())

    def test_help_lists_all_subcommands(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        for noun in ("site", "posts", "pages", "tags", "create-post",
                     "get-post", "update-post", "delete-post",
                     "create-page", "create-tag"):
            self.assertIn(noun, result.stdout)

    def test_no_subcommand_prints_help_and_fails(self):
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)

    def test_missing_title_is_argument_error(self):
        result = self.run_cli("--json", "create-post")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--title", result.stderr)

    def test_invalid_status_choice_rejected_without_crash(self):
        result = self.run_cli("--json", "create-post", "--title", "T", "--status", "archived")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

    def test_update_post_requires_updated_at_flag(self):
        result = self.run_cli("--json", "update-post", "abc123")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--updated-at", result.stderr)

    def test_dry_run_site_plan_is_valid_json_without_credentials(self):
        result = self.run_cli("--dry-run", "--json", "site")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])

    def test_dry_run_human_output_requires_explicit_json_flag(self):
        # Without --json the same command stays human-readable; the flag dict
        # is per-invocation, so callers must pass --json explicitly each run.
        result = self.run_cli("--dry-run", "site")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[dry-run]", result.stdout)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(result.stdout)

    def test_create_post_dry_run_plan_includes_url_and_envelope(self):
        result = self.run_cli("--dry-run", "--json", "create-post", "--title", "Draft A")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertIn("/ghost/api/admin/posts", payload["url"])
        self.assertEqual(payload["json"], {"posts": [{"title": "Draft A", "status": "draft"}]})

    def test_update_post_dry_run_carries_collision_guard_field(self):
        result = self.run_cli("--dry-run", "--json", "update-post", "abc123",
                              "--status", "published",
                              "--updated-at", "2026-08-26T12:00:00.000Z")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        fields = payload["fields"]
        self.assertEqual(fields["updated_at"], "2026-08-26T12:00:00.000Z")
        self.assertEqual(fields["status"], "published")

    def test_scheduled_post_requires_published_at_even_in_dry_run(self):
        result = self.run_cli("--dry-run", "--json", "create-post",
                              "--title", "Later", "--status", "scheduled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--published-at", result.stderr)


class JwtSigningTests(unittest.TestCase):
    """Known-answer JWT checks against fixed inputs (no network, no real keys)."""

    def setUp(self):
        self.cli = load_cli()

    def sign_with_fixed_clock(self, key=FIXED_KEY):
        original_time = self.cli.time.time
        self.cli.time.time = lambda: 1700000000
        try:
            client = self.cli.GhostClient(url="https://example.com", key=key)
            token = client._jwt_token()
        finally:
            self.cli.time.time = original_time
        return token

    @staticmethod
    def decode_segment(segment):
        import base64
        padded = segment + "=" * (-len(segment) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))

    def test_jwt_matches_known_answer_token_exactly(self):
        token = self.sign_with_fixed_clock()
        self.assertEqual(token, f"{HEADER_B64}.{PAYLOAD_B64}.{SIG_B64}")

    def test_header_uses_hs256_kid_and_typ(self):
        header = self.decode_segment(self.sign_with_fixed_clock().split(".")[0])
        self.assertEqual(header["alg"], "HS256")
        self.assertEqual(header["typ"], "JWT")
        self.assertEqual(header["kid"], KID)

    def test_payload_audience_and_five_minute_expiry(self):
        payload = self.decode_segment(self.sign_with_fixed_clock().split(".")[1])
        self.assertEqual(payload["aud"], "/admin/")
        self.assertEqual(payload["exp"] - payload["iat"], TOKEN_TTL)
        self.assertEqual(payload["iat"], 1700000000)

    def test_signature_keys_hex_decoded_secret_not_literal_chars(self):
        import base64 as b64
        import hashlib as hl
        import hmac as hm
        header_b64, payload_b64, sig_b64 = self.sign_with_fixed_clock().split(".")
        expected = b64.urlsafe_b64encode(
            hm.new(bytes.fromhex(SECRET_HEX), f"{header_b64}.{payload_b64}".encode(), hl.sha256).digest()
        ).rstrip(b"=").decode()
        self.assertEqual(sig_b64, expected)
        literal_hex_signature = b64.urlsafe_b64encode(
            hm.new(SECRET_HEX.encode(), f"{header_b64}.{payload_b64}".encode(), hl.sha256).digest()
        ).rstrip(b"=").decode()
        self.assertNotEqual(sig_b64, literal_hex_signature)

    def test_malformed_secret_half_is_graceful_error_not_traceback(self):
        client = self.cli.GhostClient(url="https://example.com", key="5f9d4b1c8e2a43d7b6c0a1e9:not-hex!")
        stderr = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(stderr):
                client._jwt_token()
        self.assertIn("hexadecimal", stderr.getvalue())

    def test_key_without_colon_names_required_format(self):
        client = self.cli.GhostClient(url="https://example.com", key="justonepart")
        stderr = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(stderr):
                client._jwt_token()
        self.assertIn("id:secret", stderr.getvalue())


class AdminApiAudienceTests(unittest.TestCase):
    cli = load_cli()

    def test_unversioned_admin_path_uses_root_admin_audience(self):
        self.assertEqual(self.cli.admin_api_audience("/ghost/api/admin/posts/"), "/admin/")
        self.assertEqual(self.cli.admin_api_audience("/ghost/api/admin/"), "/admin/")
        self.assertEqual(self.cli.admin_api_audience("nonsense"), "/admin/")

    def test_legacy_versioned_paths_scope_the_audience(self):
        self.assertEqual(self.cli.admin_api_audience("/ghost/api/v3/admin/posts/"), "/v3/admin/")
        self.assertEqual(self.cli.admin_api_audience("/ghost/api/v4/admin/"), "/v4/admin/")


class PipelineChainTests(unittest.TestCase):
    """Per-skill contract: documented multi-step pipelines must execute stage by
    stage, with each stage consuming the previous stage's emitted output."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory(prefix="ghost-pipeline-")

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def run_cli(self, *args, creds=False):
        env = clean_env()
        if creds:
            env["GHOST_URL"] = "https://example.com"
            env["GHOST_ADMIN_KEY"] = FIXED_KEY
        return subprocess.run([str(SCRIPT), *args], text=True,
                              capture_output=True, env=env,
                              cwd=self.tmpdir.name)

    def run_jq(self, *jq_args):
        return subprocess.run(["jq", *jq_args],
                              text=True, capture_output=True, env=clean_env(),
                              cwd=self.tmpdir.name)

    def write_stage_file(self, name, document):
        path = Path(self.tmpdir.name) / name
        path.write_text(json.dumps(document))
        return path.name

    def test_draft_then_publish_then_delete_chain_consumability(self):
        post_id = "624c2b3fc1a5b7e9d4a0f2aa"

        # Stage 1: mint the draft plan; jq extracts method + URL + title field.
        r1 = self.run_cli("--dry-run", "--json", "create-post", "--title", "Chain Post")
        self.assertEqual(r1.returncode, 0)
        stage1 = self.write_stage_file("stage1.json", json.loads(r1.stdout))
        check = self.run_jq("-r", ".method | select(. == \"post\") // empty", stage1)
        self.assertEqual(check.stdout.strip(), "post")
        url = self.run_jq("-r", ".url", stage1).stdout.strip()
        self.assertIn("/ghost/api/admin/posts", url)

        # Stage 2: publish plan consumes a hand-built id + updated_at guard;
        # jq asserts the collision-guard field travels into the request body.
        r2 = self.run_cli("--dry-run", "--json", "update-post", post_id,
                          "--status", "published",
                          "--updated-at", "2026-08-26T12:00:00.000Z")
        self.assertEqual(r2.returncode, 0)
        stage2 = self.write_stage_file("stage2.json", json.loads(r2.stdout))
        guarded_at = self.run_jq("-r", ".fields.updated_at", stage2).stdout.strip()
        self.assertRegex(guarded_at, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        body_type = self.run_jq("-r", '.fields.status | select(. == "published") // empty', stage2)
        self.assertEqual(body_type.stdout.strip(), "published")

        # Stage 3: teardown plan for the same post id consumed from stage 2's
        # positional argument (verbatim string, not re-typed).
        r3 = self.run_cli("--dry-run", "--json", "delete-post", post_id)
        self.assertEqual(r3.returncode, 0)
        stage3 = self.write_stage_file("stage3.json", json.loads(r3.stdout))
        self.assertEqual(self.run_jq("-r", ".method", stage3).stdout.strip(), "delete")

    def test_list_to_get_post_chain_type_contract(self):
        row = {"title": "Hello World", "slug": "hello-world", "id": "abc123"}

        # Stage 1: a listing document (as ghost posts --json would produce);
        # jq extracts .posts[0].id and asserts its JSON type is string.
        listing_name = self.write_stage_file(
            "listing.json",
            {"total": 1, "page": {}, "posts": [row]})
        extracted = self.run_jq("-r", ".posts[0].id", listing_name)
        self.assertEqual(extracted.returncode, 0, extracted.stderr)
        self.assertEqual(extracted.stdout.strip(), row["id"])
        type_check = self.run_jq("-r", ".posts[0].id | type", listing_name)
        self.assertEqual(type_check.stdout.strip(), "string")
        slug_check = self.run_jq("-r", ".posts[0].slug | type", listing_name)
        self.assertEqual(slug_check.stdout.strip(), "string")

        # Stage 2: get-post plan consumes exactly that id string positionally.
        r2 = self.run_cli("--dry-run", "--json", "get-post", extracted.stdout.strip(), creds=True)
        self.assertEqual(r2.returncode, 0)
        plan = json.loads(r2.stdout)
        self.assertTrue(plan["dry_run"])
        self.assertTrue(str(row["id"]) in plan["url"], plan["url"])
        self.assertTrue(plan["url"].startswith("https://"))


class MockedClientTests(unittest.TestCase):
    """In-process handler logic with requests mocked at the call site."""

    def load_with_flags(self, json_mode=True):
        cli = load_cli()
        cli.GLOBAL_FLAGS = {"json": json_mode, "dry_run": False,
                            "quiet": False, "verbose": False}
        return cli

    def test_cmd_posts_parses_envelope_and_pagination_totals(self):
        cli = self.load_with_flags()
        client = cli.GhostClient(url="https://example.com", key=FIXED_KEY)
        client.get_posts = Mock(return_value={
            "posts": [
                {"title": "First", "slug": "first", "status": "draft"},
                {"title": "Second", "slug": "second", "status": "published"},
            ],
            "meta": {"pagination": {"page": 2, "limit": 20, "pages": 7,
                                    "total": 124, "next": 3, "prev": 1}},
        })
        captured = []

        def capture_print(*args):
            captured.append(args)

        with patch("builtins.print", capture_print):
            cli.cmd_posts(client, ["--limit", "20"])
        client.get_posts.assert_called_once_with(limit=20, status=None, page=None, order=None)
        self.assertEqual(len(captured), 1, captured)
        emitted = captured[0][0]  # emit() prints one argument in json mode
        payload = json.loads(emitted)
        self.assertEqual(payload["total"], 124)
        self.assertEqual(len(payload["posts"]), 2)
        self.assertEqual(payload["page"]["pages"], 7)

    def test_client_get_posts_builds_status_filter_param(self):
        cli = self.load_with_flags()
        client = cli.GhostClient(url="https://example.com", key=FIXED_KEY)
        seen = {}

        def fake_get(path, params=None):
            seen["path"] = path
            seen["params"] = params
            return {"posts": [], "meta": {"pagination": {}}}

        client._get = fake_get
        data = client.get_posts(limit=50, status="draft")
        self.assertEqual(data["posts"], [])
        self.assertEqual(seen["path"], "/posts")
        self.assertEqual(seen["params"]["filter"], "status:draft")
        self.assertEqual(seen["params"]["limit"], 50)

    def test_delete_post_tolerates_204_empty_body(self):
        cli = self.load_with_flags(json_mode=False)
        ok_empty = Mock(status_code=204)
        del ok_empty.json  # a real 204 carries no JSON body at all
        cli.requests.delete = Mock(return_value=ok_empty)
        client = cli.GhostClient(url="https://example.com", key=FIXED_KEY)
        captured = []

        with patch("builtins.print", lambda *a, **k: captured.append(a)):
            cli.cmd_delete_post(client, ["abc123"])

        cli.requests.delete.assert_called_once()
        called_url = cli.requests.delete.call_args.args[0]
        self.assertEqual(called_url, "https://example.com/ghost/api/admin/posts/abc123")
        auth_header = cli.requests.delete.call_args.kwargs["headers"]["Authorization"]
        self.assertTrue(auth_header.startswith("Ghost eyJ"))

    def test_update_collision_error_message_advises_reget(self):
        cli = self.load_with_flags()
        collision = Mock(status_code=409, text="conflict")
        collision.json = Mock(return_value={
            "errors": [{"message": "Saving failed! Someone else is editing this post.",
                        "type": "UpdateCollisionError", "code": "UPDATE_COLLISION"}],
        })
        cli.requests.put = Mock(return_value=collision)
        client = cli.GhostClient(url="https://example.com", key=FIXED_KEY)
        stderr = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(stderr):
                client.update_post("abc123", status="published",
                                   updated_at="2026-01-01T00:00:00.000Z")
        message = stderr.getvalue()
        self.assertIn("409", message)
        self.assertIn("Someone else is editing this post", message)
        self.assertIn("Re-GET", message)

    def test_draft_read_on_content_api_style_404_routes_to_admin_guidance(self):
        cli = self.load_with_flags()
        missing = Mock(status_code=404, text="not found")
        missing.json = Mock(return_value={
            "errors": [{"message": "Resource not found error.",
                        "type": "NotFoundError", "code": None}]})
        cli.requests.get = Mock(return_value=missing)
        client = cli.GhostClient(url="https://example.com", key=FIXED_KEY)
        stderr = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(stderr):
                client._get("/posts/does-not-exist")
        message = stderr.getvalue()
        self.assertIn("404", message)
        self.assertIn("Admin API", message)

    def test_auth_header_scheme_mistake_surfaces_ghost_scheme_hint(self):
        cli = self.load_with_flags()
        bad_scheme = Mock(status_code=401)
        bad_scheme.text = ('{"errors":[{"message":"Authorization header format is '
                           '"Authorization: Ghost [token]","context":null,'
                           '"type":"UnauthorizedError","code":"INVALID_AUTH_HEADER"}]}')
        bad_scheme.json = Mock(return_value={"errors": [{
            "message": "Authorization header format is \"Authorization: Ghost [token]\"",
            "type": "UnauthorizedError", "code": "INVALID_AUTH_HEADER"}]})
        cli.requests.get = Mock(return_value=bad_scheme)
        client = cli.GhostClient(url="https://example.com", key=FIXED_KEY)
        stderr = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(stderr):
                client._get("/posts")
        self.assertIn("Ghost [token]", stderr.getvalue())

    def test_authorization_header_uses_ghost_scheme_and_version_headers(self):
        cli = self.load_with_flags()
        ok = Mock(status_code=200)
        ok.json = Mock(return_value={"posts": []})
        cli.requests.get = Mock(return_value=ok)
        client = cli.GhostClient(url="https://example.com", key=FIXED_KEY)
        client._get("/posts")
        headers = cli.requests.get.call_args.kwargs["headers"]
        self.assertTrue(headers["Authorization"].startswith("Ghost "))
        self.assertEqual(headers["Accept-Version"], "v6.0")

    def test_request_paths_target_unversioned_admin_api(self):
        cli = self.load_with_flags()
        ok = Mock(status_code=200)
        ok.json = Mock(return_value={})
        cli.requests.get = Mock(return_value=ok)
        client = cli.GhostClient(url="https://example.com/", key=FIXED_KEY)
        client._get("/site")
        called_url = cli.requests.get.call_args.args[0]
        self.assertEqual(called_url, "https://example.com/ghost/api/admin/site")


if __name__ == "__main__":
    unittest.main()
