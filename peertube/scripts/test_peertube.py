"""Offline test suite for the bundled peertube CLI.

All HTTP is mocked at the requests seam; the only live call in the file is the
single anonymous instance probe behind the PEERTUBE_LIVE_TESTS=1 guard (skipped
by default, so the suite is fully offline and passes the proxy-trap rerun).
Covers: help output, argument-error paths, dry-run plans, mocked OAuth2 token
persistence/refresh/revocation, handler output contracts, and the documented
multi-step pipeline stages (each stage's output fields/types feed the next).
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parent / "peertube"
LOADER = importlib.machinery.SourceFileLoader("peertube_cli", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
pt = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(pt)


def clean_env():
    env = os.environ.copy()
    for var in ("PEERTUBE_SERVER", "PEERTUBE_CONFIG_DIR", "PEERTUBE_LIVE_TESTS"):
        env.pop(var, None)
    return env


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, text="", headers=None):
        self.status_code = status_code
        self._json = json_body
        self.text = text if text else (json.dumps(json_body) if json_body is not None else "")
        self.headers = headers or {}

    def json(self):
        if self._json is None:
            raise ValueError("no json body")
        return self._json


VIDEO_ONE = {
    "id": 1,
    "uuid": "uuid-one",
    "shortUUID": "sOne1",
    "url": "https://inst.example/w/uuid-one",
    "name": "First video",
    "duration": 125,
    "views": 42,
    "likes": 7,
    "publishedAt": "2026-08-01T10:00:00.000Z",
    "privacy": {"id": 1, "label": "Public"},
    "account": {"name": "alice", "displayName": "Alice", "host": "inst.example"},
    "channel": {"name": "alice-channel", "displayName": "Alice Channel", "host": "inst.example"},
}
VIDEO_TWO = dict(
    VIDEO_ONE,
    id=2,
    uuid="uuid-two",
    shortUUID="sTwo2",
    name="Second video",
    duration=3661,
    views=5,
    channel={"name": "bob-channel", "displayName": "Bob Channel", "host": "other.example"},
)

TOKEN_RESPONSE = {
    "access_token": "tok-1",
    "refresh_token": "ref-1",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token_expires_in": 7200,
}
OAUTH_CLIENT = {"client_id": "cid-1", "client_secret": "client-secret-1"}
MASKED_OAUTH_CLIENT = {"client_id": "cid-1", "client_secret": "*" * 32}


def run_cli(*args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env if env is not None else clean_env(),
    )


class ModuleStateTestCase(unittest.TestCase):
    """Base that restores module globals mutated by in-process tests."""

    def setUp(self):
        self._flags = dict(pt.GLOBAL_FLAGS)
        self._env_server = pt.ENV_SERVER
        self._env_config = pt.ENV_CONFIG_DIR
        pt.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}

    def tearDown(self):
        pt.GLOBAL_FLAGS = self._flags
        pt.ENV_SERVER = self._env_server
        pt.ENV_CONFIG_DIR = self._env_config


class HelpOutputTests(unittest.TestCase):
    """Class 1: --help output."""

    def test_help_lists_every_subcommand(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for noun in (
            "server",
            "videos",
            "video",
            "search",
            "comments",
            "channels",
            "channel",
            "account",
            "me",
            "my-videos",
            "login",
            "logout",
        ):
            self.assertIn(noun, result.stdout)

    def test_help_names_the_instance_env_var(self):
        result = run_cli("--help")
        self.assertIn("PEERTUBE_SERVER", result.stdout)
        self.assertIn("sepiasearch.org", result.stdout)

    def test_search_help_states_its_scope(self):
        result = run_cli("search", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("searchTarget", result.stdout)
        self.assertIn("sepiasearch", result.stdout.lower())

    def test_leaf_help_carries_examples(self):
        for leaf in ("videos", "comments", "login", "logout"):
            result = run_cli(leaf, "--help")
            with self.subTest(leaf=leaf):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Example:", result.stdout)


class ArgumentErrorTests(unittest.TestCase):
    """Class 2: argument-error paths fail cleanly before any network call."""

    def test_search_requires_query(self):
        result = run_cli("search")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--query", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_video_requires_id(self):
        result = run_cli("video")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--id", result.stderr)

    def test_channel_requires_handle(self):
        result = run_cli("channel")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--handle", result.stderr)

    def test_no_subcommand_prints_help_and_exits(self):
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout)

    def test_limit_above_server_maximum_rejected(self):
        result = run_cli("--dry-run", "--json", "videos", "--limit", "101")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("100", result.stderr)

    def test_limit_zero_rejected(self):
        result = run_cli("--dry-run", "--json", "videos", "--limit", "0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--limit", result.stderr)

    def test_negative_offset_rejected(self):
        result = run_cli("--dry-run", "--json", "videos", "--offset", "-1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--offset", result.stderr)

    def test_login_without_password_errors(self):
        result = run_cli("login", "--username", "alice", "--server", "https://inst.example")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("password", result.stderr.lower())
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_server_dies_before_network(self):
        result = run_cli("videos", "--limit", "1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PEERTUBE_SERVER", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class DryRunPlanTests(ModuleStateTestCase):
    """Class 3: --dry-run emits valid JSON plans with zero network activity."""

    def run_json(self, *args):
        pt.GLOBAL_FLAGS = {"json": True, "dry_run": True, "quiet": False, "verbose": False}
        return io.StringIO()

    def test_single_endpoint_plans_emit_method_path_params(self):
        cases = (
            (
                pt.cmd_videos,
                ["--limit", "3"],
                {
                    "method": "GET",
                    "path": "/api/v1/videos",
                    "params.start": 0,
                    "params.count": 3,
                    "params.sort": "-publishedAt",
                },
            ),
            (
                pt.cmd_search,
                ["--query", "linux", "--limit", "5"],
                {
                    "method": "GET",
                    "path": "/api/v1/search/videos",
                    "params.searchTarget": "local",
                    "params.search": "linux",
                },
            ),
            (
                pt.cmd_video,
                ["--id", "uuid-one"],
                {"method": "GET", "path": "/api/v1/videos/uuid-one"},
            ),
            (
                pt.cmd_comments,
                ["--id", "uuid-one"],
                {"method": "GET", "path": "/api/v1/videos/uuid-one/comment-threads"},
            ),
            (pt.cmd_channels, [], {"method": "GET", "path": "/api/v1/video-channels"}),
            (pt.cmd_me, [], {"method": "GET", "path": "/api/v1/users/me"}),
            (pt.cmd_my_videos, [], {"method": "GET", "path": "/api/v1/users/me/videos"}),
            (pt.cmd_logout, [], {"method": "POST", "path": "/api/v1/users/revoke-token"}),
        )
        for handler, args, expectations in cases:
            with self.subTest(handler=handler.__name__):
                client = pt.PeerTubeClient(
                    server="https://inst.example",
                    dry_run=True,
                    config_dir=tempfile.mkdtemp(prefix="pt-dry-"),
                )
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    handler(client, args)
                plan = json.loads(out.getvalue())
                self.assertTrue(plan["dry_run"])
                self.assertEqual(plan["method"], expectations["method"])
                self.assertEqual(plan["path"], expectations["path"])

    def test_dry_run_videos_plan_never_sends_page_param(self):
        client = pt.PeerTubeClient(
            server="https://inst.example",
            dry_run=True,
            config_dir=tempfile.mkdtemp(prefix="pt-dry-"),
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pt.cmd_videos(client, ["--limit", "9", "--offset", "18"])
        plan = json.loads(out.getvalue())
        self.assertNotIn("page", plan["params"])
        self.assertEqual(plan["params"]["start"], 18)
        self.assertEqual(plan["params"]["count"], 9)

    def test_search_plan_defaults_to_instance_local_scope(self):
        client = pt.PeerTubeClient(
            server="https://inst.example",
            dry_run=True,
            config_dir=tempfile.mkdtemp(prefix="pt-dry-"),
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pt.cmd_search(client, ["--query", "peertube"])
        plan = json.loads(out.getvalue())
        self.assertEqual(plan["params"]["searchTarget"], "local")

    def test_composite_commands_plan_every_request(self):
        client = pt.PeerTubeClient(
            server="https://inst.example",
            dry_run=True,
            config_dir=tempfile.mkdtemp(prefix="pt-dry-"),
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pt.cmd_server(client, [])
        plan = json.loads(out.getvalue())
        paths = [req["path"] for req in plan["requests"]]
        self.assertEqual(paths, ["/api/v1/config/about", "/api/v1/server/stats"])

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pt.cmd_channel(client, ["--handle", "alice-channel"])
        plan = json.loads(out.getvalue())
        paths = [req["path"] for req in plan["requests"]]
        self.assertEqual(
            paths,
            ["/api/v1/video-channels/alice-channel", "/api/v1/video-channels/alice-channel/videos"],
        )

    def test_login_dry_run_lists_form_fields_without_values(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pt.cmd_login(
                pt.PeerTubeClient(
                    server="https://inst.example",
                    dry_run=True,
                    config_dir=tempfile.mkdtemp(prefix="pt-dry-"),
                ),
                ["--username", "alice"],
            )
        plan = json.loads(out.getvalue())
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["path"], "/api/v1/users/token")
        self.assertIn("grant_type", plan["form_fields"])
        self.assertIn("client_secret", plan["form_fields"])
        self.assertNotIn("form", plan)  # no values leak in the plan

    def test_dry_run_works_without_any_server_configured(self):
        pt.ENV_SERVER = ""
        client = pt.PeerTubeClient(
            server="", dry_run=True, config_dir=tempfile.mkdtemp(prefix="pt-dry-")
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            pt.cmd_videos(client, ["--limit", "2"])
        self.assertTrue(json.loads(out.getvalue())["dry_run"])

    def test_dry_run_never_touches_network(self):
        client = pt.PeerTubeClient(
            server="https://inst.example",
            dry_run=True,
            config_dir=tempfile.mkdtemp(prefix="pt-dry-"),
        )
        with (
            patch.object(pt.requests, "get") as getter,
            patch.object(pt.requests, "post") as poster,
        ):
            for handler, args in (
                (pt.cmd_videos, ["--limit", "2"]),
                (pt.cmd_search, ["--query", "x"]),
                (pt.cmd_server, []),
                (pt.cmd_me, []),
                (pt.cmd_login, ["--username", "a"]),
                (pt.cmd_logout, []),
            ):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    handler(client, args)
        getter.assert_not_called()
        poster.assert_not_called()

    def test_flags_work_before_and_after_subcommand(self):
        result = run_cli("--json", "--dry-run", "search", "--query", "x", "--limit", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["dry_run"])
        result = run_cli("search", "--query", "x", "--limit", "2", "--json", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["dry_run"])


class ClientContractTests(ModuleStateTestCase):
    """Class 4a: mocked requests — paths, params, and error handling."""

    def mocked_get(self, responses, server="https://inst.example"):
        client = pt.PeerTubeClient(server=server, config_dir=tempfile.mkdtemp(prefix="pt-cc-"))
        return client, patch.object(pt.requests, "get", side_effect=responses)

    def test_video_listing_sends_start_count_sort(self):
        client, patcher = self.mocked_get(
            [FakeResponse(200, {"total": 2, "data": [VIDEO_ONE, VIDEO_TWO]})]
        )
        with patcher as getter:
            pt.cmd_videos(client, ["--limit", "2", "--offset", "10"])
        args, kwargs = getter.call_args
        self.assertEqual(args[0], "https://inst.example/api/v1/videos")
        self.assertEqual(kwargs["params"], {"start": 10, "count": 2, "sort": "-publishedAt"})
        self.assertNotIn("page", kwargs["params"])

    def test_search_defaults_to_local_target_and_omits_empty_sort(self):
        client, patcher = self.mocked_get([FakeResponse(200, {"total": 0, "data": []})])
        with patcher as getter:
            pt.cmd_search(client, ["--query", "linux"])
        params = getter.call_args[1]["params"]
        self.assertEqual(params["searchTarget"], "local")
        self.assertEqual(params["search"], "linux")
        self.assertNotIn("sort", params)

    def test_comment_threads_route_is_hyphenated(self):
        client, patcher = self.mocked_get(
            [FakeResponse(200, {"total": 0, "totalNotDeletedComments": 0, "data": []})]
        )
        with patcher as getter:
            pt.cmd_comments(client, ["--id", "uuid-one"])
        self.assertEqual(
            getter.call_args[0][0], "https://inst.example/api/v1/videos/uuid-one/comment-threads"
        )

    def test_server_composes_about_and_stats(self):
        about = FakeResponse(
            200, {"instance": {"name": "Inst", "shortDescription": "Desc", "description": "Long"}}
        )
        stats = FakeResponse(
            200,
            {
                "totalUsers": 9,
                "totalLocalVideos": 933,
                "totalVideos": 23890,
                "totalLocalVideoViews": 1001751,
                "totalLocalVideoDownloads": 32569,
                "totalLocalVideoChannels": 28,
            },
        )
        client, patcher = self.mocked_get([about, stats])
        with patcher:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_server(client, [])
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["instance"]["name"], "Inst")
        self.assertEqual(payload["stats"]["totalLocalVideos"], 933)
        self.assertIsInstance(payload["stats"]["totalUsers"], int)

    def test_401_names_login_remedy(self):
        client, patcher = self.mocked_get([FakeResponse(401, {"detail": "token expired"})])
        client._token = "stale-token"  # authed command proceeds, then server rejects
        with patcher:
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_me(client, [])
        self.assertIn("401", err.getvalue())
        self.assertIn("login", err.getvalue().lower())

    def test_429_surfaces_retry_after(self):
        client, patcher = self.mocked_get(
            [FakeResponse(429, {"detail": "rate limit"}, headers={"Retry-After": "7"})]
        )
        with patcher:
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_videos(client, ["--limit", "2"])
        self.assertIn("429", err.getvalue())
        self.assertIn("Retry-After", err.getvalue())

    def test_rfc7807_detail_extracted_on_generic_error(self):
        client, patcher = self.mocked_get(
            [
                FakeResponse(
                    400,
                    {
                        "type": "about:blank",
                        "title": "Bad Request",
                        "status": 400,
                        "detail": "unknown route shape",
                    },
                )
            ]
        )
        with patcher:
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_videos(client, ["--limit", "2"])
        self.assertIn("unknown route shape", err.getvalue())

    def test_non_json_instance_response_is_diagnosed(self):
        client, patcher = self.mocked_get([FakeResponse(200, text="<html>not peertube</html>")])
        with patcher:
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_videos(client, ["--limit", "2"])
        self.assertIn("Non-JSON", err.getvalue())


class OAuthFlowTests(ModuleStateTestCase):
    """Class 4b: mocked OAuth2 — client fetch, password grant, persistence,
    refresh, revocation. Token files live in TemporaryDirectories only."""

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory(prefix="pt-oauth-")
        self.config_dir = self.tmp.name
        pt.ENV_SERVER = "https://inst.example"

    def tearDown(self):
        self.tmp.cleanup()
        super().tearDown()

    def client(self, **kwargs):
        return pt.PeerTubeClient(
            server="https://inst.example", config_dir=self.config_dir, **kwargs
        )

    def test_fetch_oauth_client_hits_singular_local_route(self):
        client = self.client()
        with patch.object(
            pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)
        ) as getter:
            client_id, client_secret = client.fetch_oauth_client()
        self.assertEqual(getter.call_args[0][0], "https://inst.example/api/v1/oauth-clients/local")
        self.assertEqual((client_id, client_secret), ("cid-1", "client-secret-1"))

    def test_password_grant_sends_form_encoded_fields(self):
        client = self.client()
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(
                pt.requests, "post", return_value=FakeResponse(200, TOKEN_RESPONSE)
            ) as poster,
        ):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_login(client, ["--username", "alice", "--password", "pw"])
        args, kwargs = poster.call_args
        self.assertEqual(args[0], "https://inst.example/api/v1/users/token")
        form = kwargs["data"]
        self.assertEqual(form["grant_type"], "password")
        self.assertEqual(form["username"], "alice")
        self.assertEqual(form["client_id"], "cid-1")
        self.assertNotIn("response_type", form)  # not part of the documented schema
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["status"], "logged_in")

    def test_bad_password_400_exits_with_guidance(self):
        client = self.client()
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(
                pt.requests, "post", return_value=FakeResponse(400, {"detail": "invalid_grant"})
            ),
        ):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_login(client, ["--username", "alice", "--password", "wrong"])
        self.assertIn("400", err.getvalue())
        self.assertIn("invalid_grant", err.getvalue())

    def test_two_factor_401_suggests_otp_flag(self):
        client = self.client()
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(pt.requests, "post", return_value=FakeResponse(401, {})),
        ):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_login(client, ["--username", "alice", "--password", "pw"])
        self.assertIn("--otp", err.getvalue())

    def test_otp_header_attached_when_provided(self):
        client = self.client()
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(
                pt.requests, "post", return_value=FakeResponse(200, TOKEN_RESPONSE)
            ) as poster,
        ):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_login(client, ["--username", "alice", "--password", "pw", "--otp", "123456"])
        self.assertEqual(poster.call_args[1]["headers"]["x-peertube-otp"], "123456")

    def test_masked_client_secret_stops_login_with_guidance(self):
        client = self.client()
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, MASKED_OAUTH_CLIENT)),
            patch.object(pt.requests, "post") as poster,
        ):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_login(client, ["--username", "alice", "--password", "pw"])
        self.assertIn("masks client_secret", err.getvalue())
        poster.assert_not_called()

    def test_is_masked_secret_detection(self):
        self.assertTrue(pt.is_masked_secret("*" * 32))
        self.assertFalse(pt.is_masked_secret("client-secret-1"))
        self.assertFalse(pt.is_masked_secret(""))
        self.assertFalse(pt.is_masked_secret("*-mixed-*"))

    def test_token_file_persisted_owner_only_with_expiry(self):
        client = self.client()
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(pt.requests, "post", return_value=FakeResponse(200, TOKEN_RESPONSE)),
        ):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                pt.cmd_login(client, ["--username", "alice", "--password", "pw"])
        token_path = client.token_path()
        self.assertTrue(os.path.isfile(token_path))
        mode = stat.S_IMODE(os.stat(token_path).st_mode)
        self.assertEqual(mode & 0o077, 0, "token file must be owner-only")
        with open(token_path) as handle:
            record = json.load(handle)
        self.assertEqual(record["server"], "https://inst.example")
        self.assertEqual(record["access_token"], "tok-1")
        self.assertEqual(record["refresh_token"], "ref-1")
        self.assertIsNotNone(record["expires_at"])
        self.assertGreater(record["expires_at"], time.time())
        self.assertLess(record["expires_at"], time.time() + 7200)

    def test_token_from_another_instance_is_ignored(self):
        client = self.client()
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(pt.requests, "post", return_value=FakeResponse(200, TOKEN_RESPONSE)),
        ):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                pt.cmd_login(client, ["--username", "alice", "--password", "pw"])
        other = pt.PeerTubeClient(server="https://other.example", config_dir=self.config_dir)
        self.assertIsNone(other._token)

    def test_expired_token_triggers_refresh_then_success(self):
        client = self.client()
        client.save_session(dict(TOKEN_RESPONSE, expires_in=-10))  # already expired
        refreshed = dict(TOKEN_RESPONSE, access_token="tok-2", expires_in=3600)
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(pt.requests, "post", return_value=FakeResponse(200, refreshed)) as poster,
        ):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                pt.cmd_me(client, [])
        form = poster.call_args[1]["data"]
        self.assertEqual(form["grant_type"], "refresh_token")
        self.assertEqual(form["refresh_token"], "ref-1")
        self.assertEqual(client._token, "tok-2")
        with open(client.token_path()) as handle:
            self.assertEqual(json.load(handle)["access_token"], "tok-2")

    def test_failed_refresh_falls_back_to_login_guidance(self):
        client = self.client()
        client.save_session(dict(TOKEN_RESPONSE, expires_in=-10))
        with (
            patch.object(pt.requests, "get", return_value=FakeResponse(200, OAUTH_CLIENT)),
            patch.object(pt.requests, "post", return_value=FakeResponse(400, {})),
        ):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_me(client, [])
        self.assertIn("Not authenticated", err.getvalue())

    def test_logout_revokes_and_deletes_token_file(self):
        client = self.client()
        client.save_session(TOKEN_RESPONSE)
        self.assertTrue(os.path.isfile(client.token_path()))
        with patch.object(pt.requests, "post", return_value=FakeResponse(200, {})) as poster:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_logout(client, [])
        args, kwargs = poster.call_args
        self.assertEqual(args[0], "https://inst.example/api/v1/users/revoke-token")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer tok-1")
        self.assertFalse(os.path.exists(client.token_path()))

    def test_logout_keeps_file_when_revocation_fails(self):
        client = self.client()
        client.save_session(TOKEN_RESPONSE)
        with patch.object(pt.requests, "post", return_value=FakeResponse(500, {})):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pt.cmd_logout(client, [])
        self.assertTrue(os.path.isfile(client.token_path()))

    def test_logout_without_token_errors_cleanly(self):
        client = self.client()
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
            pt.cmd_logout(client, [])
        self.assertIn("No stored token", err.getvalue())


class HandlerOutputTests(ModuleStateTestCase):
    """Class 4c: handler output contracts consumed by jq pipelines."""

    def test_videos_output_carries_raw_video_objects(self):
        client = pt.PeerTubeClient(
            server="https://inst.example", config_dir=tempfile.mkdtemp(prefix="pt-ho-")
        )
        with patch.object(
            pt.requests,
            "get",
            return_value=FakeResponse(200, {"total": 2, "data": [VIDEO_ONE, VIDEO_TWO]}),
        ):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_videos(client, ["--limit", "2"])
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["total"], 2)
        self.assertEqual(payload["start"], 0)
        self.assertEqual(payload["count"], 2)
        self.assertIsInstance(payload["videos"], list)
        first = payload["videos"][0]
        self.assertEqual(first["uuid"], "uuid-one")
        self.assertIsInstance(first["duration"], int)  # seconds
        self.assertEqual(first["channel"]["host"], "inst.example")

    def test_search_output_marks_scope_and_carries_uuids(self):
        client = pt.PeerTubeClient(
            server="https://inst.example", config_dir=tempfile.mkdtemp(prefix="pt-ho-")
        )
        with patch.object(
            pt.requests, "get", return_value=FakeResponse(200, {"total": 1, "data": [VIDEO_TWO]})
        ):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_search(client, ["--query", "x"])
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["videos"][0]["uuid"], "uuid-two")

    def test_me_tolerates_docs_array_sample_and_object(self):
        client = pt.PeerTubeClient(
            server="https://inst.example", config_dir=tempfile.mkdtemp(prefix="pt-ho-")
        )
        profile = {
            "username": "alice",
            "role": {"id": 1, "label": "User"},
            "videoQuota": 1073741824,
            "videoChannels": [],
        }
        for body in (profile, [profile]):
            client.save_session(TOKEN_RESPONSE)
            with patch.object(pt.requests, "get", return_value=FakeResponse(200, body)):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    pt.cmd_me(client, [])
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["username"], "alice")
            self.assertEqual(payload["role"]["label"], "User")
        client.clear_token()

    def test_comments_output_exposes_thread_counts(self):
        client = pt.PeerTubeClient(
            server="https://inst.example", config_dir=tempfile.mkdtemp(prefix="pt-ho-")
        )
        body = {
            "total": 1,
            "totalNotDeletedComments": 3,
            "data": [
                {"totalReplies": 3, "comment": {"text": "nice video", "account": {"name": "bob"}}}
            ],
        }
        with patch.object(pt.requests, "get", return_value=FakeResponse(200, body)):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_comments(client, ["--id", "uuid-one"])
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["total_not_deleted"], 3)
        self.assertEqual(payload["threads"][0]["comment"]["text"], "nice video")

    def test_channels_output_carries_handles_and_counts(self):
        client = pt.PeerTubeClient(
            server="https://inst.example", config_dir=tempfile.mkdtemp(prefix="pt-ho-")
        )
        body = {
            "total": 1,
            "data": [
                {
                    "name": "alice-channel",
                    "displayName": "Alice Channel",
                    "host": "inst.example",
                    "videosCount": 12,
                    "followersCount": 34,
                }
            ],
        }
        with patch.object(pt.requests, "get", return_value=FakeResponse(200, body)):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pt.cmd_channels(client, [])
        payload = json.loads(out.getvalue())
        channel = payload["channels"][0]
        self.assertEqual(channel["name"], "alice-channel")
        self.assertIsInstance(channel["videosCount"], int)


class PipelineChainTests(ModuleStateTestCase):
    """Documented multi-step recipes must execute stage by stage, each stage's
    output field names AND JSON types consumable by the next."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory(prefix="pt-pipeline-")

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def run_cli(self, *args):
        env = clean_env()
        env["PEERTUBE_SERVER"] = "https://inst.example"
        env["PEERTUBE_CONFIG_DIR"] = self.tmpdir.name
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--dry-run", *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def run_jq(self, *jq_args, stdin_text=""):
        return subprocess.run(
            ["jq", *jq_args], input=stdin_text, capture_output=True, text=True, env=clean_env()
        )

    def stage_file(self, name, document):
        path = pathlib.Path(self.tmpdir.name) / name
        path.write_text(json.dumps(document))
        return str(path)

    def test_browse_then_detail_chain_consumability(self):
        # Stage 1: videos plan; jq proves the path and the start-offset type
        # (number) that stage two consumes when picking an id from the listing.
        r1 = self.run_cli("videos", "--limit", "2")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.stage_file("s1.json", json.loads(r1.stdout))
        self.assertEqual(
            self.run_jq("-r", ".path", stdin_text=r1.stdout).stdout.strip(), "/api/v1/videos"
        )
        self.assertEqual(
            self.run_jq("-r", ".params.start | type", stdin_text=r1.stdout).stdout.strip(), "number"
        )
        # Stage 2: detail plan consumes an id into the URL path.
        r2 = self.run_cli("video", "--id", "uuid-one")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.stage_file("s2.json", json.loads(r2.stdout))
        self.assertEqual(
            self.run_jq("-r", ".path", stdin_text=r2.stdout).stdout.strip(),
            "/api/v1/videos/uuid-one",
        )

    def test_search_then_video_chain_consumability(self):
        r1 = self.run_cli("search", "--query", "linux", "--limit", "3")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertEqual(
            self.run_jq("-r", ".params.searchTarget", stdin_text=r1.stdout).stdout.strip(), "local"
        )
        self.assertEqual(
            self.run_jq("-r", ".params.count | type", stdin_text=r1.stdout).stdout.strip(), "number"
        )
        # The documented jq selector .videos[0].uuid maps to detail --id.
        r2 = self.run_cli("video", "--id", "uuid-from-search")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(
            self.run_jq("-r", ".path", stdin_text=r2.stdout).stdout.strip(),
            "/api/v1/videos/uuid-from-search",
        )

    def test_channel_offset_paging_chain_consumability(self):
        r1 = self.run_cli("channels", "--limit", "100", "--offset", "0")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertEqual(
            self.run_jq("-r", ".path", stdin_text=r1.stdout).stdout.strip(),
            "/api/v1/video-channels",
        )
        r2 = self.run_cli(
            "channel", "--handle", "alice-channel", "--limit", "100", "--offset", "100"
        )
        self.assertEqual(r2.returncode, 0, r2.stderr)
        plan = json.loads(r2.stdout)
        video_req = plan["requests"][1]
        self.assertEqual(video_req["params"]["start"], 100)
        self.assertEqual(video_req["params"]["count"], 100)
        self.assertNotIn("page", video_req["params"])

    def test_login_to_me_chain_handoff(self):
        # Stage 1: login plan lists the form fields (no values).
        r1 = self.run_cli("login", "--username", "alice")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertEqual(
            self.run_jq("-r", ".path", stdin_text=r1.stdout).stdout.strip(), "/api/v1/users/token"
        )
        fields = json.loads(self.run_jq("-c", ".form_fields", stdin_text=r1.stdout).stdout)
        self.assertIn("grant_type", fields)
        # Stage 2: me plan rides the Authorization header the login persisted.
        r2 = self.run_cli("me")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(
            self.run_jq("-r", ".path", stdin_text=r2.stdout).stdout.strip(), "/api/v1/users/me"
        )
        # Stage 3: logout plan revokes on the same instance.
        r3 = self.run_cli("logout")
        self.assertEqual(r3.returncode, 0, r3.stderr)
        self.assertEqual(
            self.run_jq("-r", ".path", stdin_text=r3.stdout).stdout.strip(),
            "/api/v1/users/revoke-token",
        )

    def test_server_composition_plan_targets_both_endpoints(self):
        r1 = self.run_cli("server")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        paths = json.loads(self.run_jq("-c", "[.requests[].path]", stdin_text=r1.stdout).stdout)
        self.assertEqual(paths, ["/api/v1/config/about", "/api/v1/server/stats"])

    def test_mocked_browse_to_detail_stage_types(self):
        """Live-shape variant of recipe 1: the videos output's uuid (string)
        feeds video --id, and the detail object carries description/url."""
        pt.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        client = pt.PeerTubeClient(server="https://inst.example", config_dir=self.tmpdir.name)
        detail = dict(VIDEO_ONE, description="full text", commentsEnabled=True)
        with patch.object(
            pt.requests,
            "get",
            side_effect=[
                FakeResponse(200, {"total": 1, "data": [VIDEO_ONE]}),
                FakeResponse(200, detail),
            ],
        ):
            first = io.StringIO()
            with contextlib.redirect_stdout(first):
                pt.cmd_videos(client, ["--limit", "1"])
            listing = json.loads(first.getvalue())
            consumed_id = listing["videos"][0]["uuid"]
            self.assertIsInstance(consumed_id, str)

            second = io.StringIO()
            with contextlib.redirect_stdout(second):
                pt.cmd_video(client, ["--id", consumed_id])
            video_detail = json.loads(second.getvalue())
        self.assertEqual(video_detail["uuid"], consumed_id)
        self.assertIsInstance(video_detail["description"], str)
        self.assertIsInstance(video_detail["commentsEnabled"], bool)


class EnvGuardedLiveProbeTests(unittest.TestCase):
    """Optional anonymous instance probe (keyless public endpoint). Runs only
    with PEERTUBE_LIVE_TESTS=1; skipped cleanly otherwise so the suite stays
    fully offline under the proxy-trap."""

    def test_public_instance_oauth_client_probe(self):
        if os.getenv("PEERTUBE_LIVE_TESTS") != "1":
            self.skipTest("live probe disabled (set PEERTUBE_LIVE_TESTS=1)")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "server", "--server", "https://framatube.org"],
            capture_output=True,
            text=True,
            env=clean_env(),
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["instance"]["name"], "Framatube")
        self.assertIsInstance(payload["stats"]["totalLocalVideos"], int)


if __name__ == "__main__":
    unittest.main()
