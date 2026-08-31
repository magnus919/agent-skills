import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPT = pathlib.Path(__file__).resolve().parent / "jellyfin"
LOADER = importlib.machinery.SourceFileLoader("jellyfin_cli", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
jellyfin_cli = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(jellyfin_cli)


def clean_env():
    env = os.environ.copy()
    for var in ("JELLYFIN_URL", "JELLYFIN_API_KEY", "JELLYFIN_TOKEN",
                "JELLYFIN_USER_ID", "JELLYFIN_DEVICE_ID", "JELLYFIN_PASSWORD"):
        env.pop(var, None)
    return env


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, text="", headers=None):
        self.status_code = status_code
        self._json = json_body
        self.text = text or (json.dumps(json_body) if json_body is not None else "")
        self.headers = headers or {}

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


class FakeClient:
    def __init__(self, libraries=None, dry_run=False):
        self.dry_run = dry_run
        self.libraries = libraries
        self.recent_calls = []

    def get_libraries(self):
        return self.libraries

    def get_recent(self, user_id, limit=10, include_types=None):
        self.recent_calls.append((user_id, limit, include_types))
        return [{"Name": "Arrival", "Type": "Movie", "Id": "movie-1"}]


class NavigationFakeClient:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.next_up_calls = []
        self.item_calls = []
        self.items_calls = []
        self.seasons_calls = []
        self.episodes_calls = []

    def get_next_up(self, user_id, limit=10, series_id=None):
        self.next_up_calls.append((user_id, limit, series_id))
        return {
            "Items": [{"Name": "The Signal", "Type": "Episode", "Id": "episode-1",
                       "SeriesName": "Voyagers", "IndexNumber": 4}],
            "StartIndex": 0,
            "TotalRecordCount": 9,
        }

    def get_item(self, item_id, user_id):
        self.item_calls.append((item_id, user_id))
        return {"Name": "The Signal", "Type": "Episode", "Id": item_id,
                "SeriesName": "Voyagers", "IndexNumber": 4,
                "Overview": "A message arrives."}

    def get_items(self, parent_id, types=None, limit=50, sort_by="SortName",
                  sort_order="Ascending", start_index=0, user_id=None):
        self.items_calls.append((parent_id, types, limit, sort_by, sort_order,
                                 start_index, user_id))
        return {
            "Items": [{"Name": "Arrival", "Type": "Movie", "Id": "movie-1",
                       "ProductionYear": 2016}],
            "StartIndex": start_index,
            "TotalRecordCount": 1,
        }

    def get_seasons(self, series_id, user_id):
        self.seasons_calls.append((series_id, user_id))
        return {"Items": [{"Name": "Season 1", "Type": "Season", "Id": "season-1",
                           "ParentIndexNumber": 1}],
                "TotalRecordCount": 1}

    def get_episodes(self, series_id, season_id, user_id):
        self.episodes_calls.append((series_id, season_id, user_id))
        return {"Items": [{"Name": "The Signal", "Type": "Episode", "Id": "episode-1",
                           "ParentIndexNumber": 1, "IndexNumber": 4}],
                "TotalRecordCount": 1}


class JellyfinCliTests(unittest.TestCase):
    def setUp(self):
        self.flags = jellyfin_cli.GLOBAL_FLAGS
        self.env_user_id = jellyfin_cli.ENV_USER_ID
        jellyfin_cli.GLOBAL_FLAGS = {"json": True, "dry_run": False}

    def tearDown(self):
        jellyfin_cli.GLOBAL_FLAGS = self.flags
        jellyfin_cli.ENV_USER_ID = self.env_user_id

    def test_hardened_recent_and_libraries_contracts(self):
        output = io.StringIO()
        libraries = FakeClient(libraries={"Items": [{"Name": "Films", "Id": "lib-1", "CollectionType": "movies"}]})
        with contextlib.redirect_stdout(output):
            jellyfin_cli.cmd_libraries(libraries, [])
        self.assertEqual(json.loads(output.getvalue())["libraries"][0]["name"], "Films")

        calls = []
        client = jellyfin_cli.JellyfinClient()
        client._get = lambda path, params=None: calls.append((path, params)) or []
        client.get_recent("user-1", limit=3, include_types=["Movie", "Episode"])
        self.assertEqual(calls, [("/Items/Latest", {"userId": "user-1", "includeItemTypes": "Movie,Episode", "limit": 3, "fields": "DateCreated"})])

        recent = FakeClient()
        with contextlib.redirect_stdout(io.StringIO()):
            jellyfin_cli.cmd_recent(recent, ["--user-id", "user-1", "--movies", "--limit", "2"])
        self.assertEqual(recent.recent_calls, [("user-1", 2, ["Movie"])])

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            jellyfin_cli.cmd_recent(recent, ["--movies", "--episodes"])

        result = subprocess.run(
            [str(SCRIPT), "recent", "--movies", "--episodes"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("not allowed with argument", result.stderr)

    def test_recent_requires_user_before_network_and_dry_run_previews_request(self):
        jellyfin_cli.ENV_USER_ID = ""
        client = FakeClient()
        error = io.StringIO()
        with contextlib.redirect_stderr(error), self.assertRaises(SystemExit):
            jellyfin_cli.cmd_recent(client, [])
        self.assertIn("JELLYFIN_USER_ID", error.getvalue())
        self.assertEqual(client.recent_calls, [])

        dry_run = FakeClient(dry_run=True)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            jellyfin_cli.cmd_recent(dry_run, ["--movies", "--limit", "2"])
        self.assertEqual(json.loads(output.getvalue()), {
            "dry_run": True,
            "path": "/Items/Latest",
            "params": {"userId": None, "includeItemTypes": "Movie", "limit": 2, "fields": "DateCreated"},
        })
        self.assertEqual(dry_run.recent_calls, [])

    def test_navigation_client_contracts(self):
        calls = []
        client = jellyfin_cli.JellyfinClient()
        client._get = lambda path, params=None: calls.append((path, params)) or {}

        client.get_next_up("user-1", limit=3, series_id="series-1")
        client.get_item("item-1", "user-1")
        client.get_items("library-1", types=["Movie", "Series"], limit=4, start_index=2,
                         user_id="user-1")

        self.assertEqual(calls, [
            ("/Shows/NextUp", {"userId": "user-1", "limit": 3, "seriesId": "series-1"}),
            ("/Items/item-1", {"userId": "user-1"}),
            ("/Items", {"parentId": "library-1", "limit": 4, "sortBy": "SortName",
                        "sortOrder": "Ascending", "startIndex": 2, "recursive": True,
                        "userId": "user-1",
                        "includeItemTypes": "Movie,Series"}),
        ])

    def test_authorization_header_builds_media_browser_scheme(self):
        header = jellyfin_cli.build_authorization_header("dev-42")
        self.assertTrue(header.startswith("MediaBrowser "))
        self.assertIn('Client="jellyfin-cli"', header)
        self.assertIn('DeviceId="dev-42"', header)
        for required in ("Client=", "Device=", "DeviceId=", "Version="):
            self.assertIn(required, header)
        self.assertNotIn("Token=", header)  # pre-token form carries no token segment
        with_token = jellyfin_cli.build_authorization_header("dev-42", token="tok-1")
        self.assertIn('Token="tok-1"', with_token)

    def test_next_up_item_and_browse_parse_results_as_json(self):
        client = NavigationFakeClient()

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            jellyfin_cli.cmd_next_up(client, ["--user-id", "user-1", "--limit", "3"])
        self.assertEqual(json.loads(output.getvalue()), {
            "items": [{"id": "episode-1", "name": "The Signal", "type": "Episode",
                       "series": "Voyagers", "episode_number": 4}],
            "total_record_count": 9,
        })
        self.assertEqual(client.next_up_calls, [("user-1", 3, None)])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            jellyfin_cli.cmd_item(client, ["--id", "episode-1", "--user-id", "user-1"])
        self.assertEqual(json.loads(output.getvalue()), {
            "id": "episode-1", "name": "The Signal", "type": "Episode",
            "series": "Voyagers", "episode_number": 4, "overview": "A message arrives.",
        })
        self.assertEqual(client.item_calls, [("episode-1", "user-1")])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            jellyfin_cli.cmd_browse(client, ["--library-id", "library-1", "--type", "Movie",
                                              "--limit", "4", "--start-index", "2",
                                              "--user-id", "user-1"])
        self.assertEqual(json.loads(output.getvalue()), {
            "items": [{"id": "movie-1", "name": "Arrival", "type": "Movie", "year": 2016}],
            "start_index": 2,
            "total_record_count": 1,
        })
        self.assertEqual(client.items_calls,
                         [("library-1", ["Movie"], 4, "SortName", "Ascending", 2, "user-1")])

    def test_user_scoped_navigation_requires_user_before_network(self):
        jellyfin_cli.ENV_USER_ID = ""
        for handler, arguments in (
            (jellyfin_cli.cmd_next_up, []),
            (jellyfin_cli.cmd_item, ["--id", "item-1"]),
        ):
            client = NavigationFakeClient()
            with self.subTest(handler=handler.__name__), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                handler(client, arguments)
            self.assertEqual(client.next_up_calls, [])
            self.assertEqual(client.item_calls, [])

    def test_navigation_dry_runs_do_not_call_network_and_emit_requests(self):
        cases = (
            (jellyfin_cli.cmd_next_up, ["--limit", "3"], {"path": "/Shows/NextUp", "params": {"userId": None, "limit": 3}}),
            (jellyfin_cli.cmd_next_up, ["--limit", "3", "--series-id", "s1"], {"path": "/Shows/NextUp", "params": {"userId": None, "limit": 3, "seriesId": "s1"}}),
            (jellyfin_cli.cmd_item, ["--id", "item-1"], {"path": "/Items/item-1", "params": {"userId": None}}),
            (jellyfin_cli.cmd_browse, ["--library-id", "library-1", "--type", "Movie,Series", "--limit", "4", "--start-index", "2"], {"path": "/Items", "params": {"parentId": "library-1", "limit": 4, "sortBy": "SortName", "sortOrder": "Ascending", "startIndex": 2, "recursive": True, "includeItemTypes": "Movie,Series"}}),
        )
        for handler, arguments, request in cases:
            client = NavigationFakeClient(dry_run=True)
            output = io.StringIO()
            with self.subTest(handler=handler.__name__), contextlib.redirect_stdout(output):
                handler(client, arguments)
            self.assertEqual(json.loads(output.getvalue()), {"dry_run": True, **request})
            self.assertEqual(client.next_up_calls, [])
            self.assertEqual(client.item_calls, [])
            self.assertEqual(client.items_calls, [])

    def test_navigation_commands_dispatch_and_leaf_help_has_examples(self):
        for command, arguments in (
            ("next-up", ["--user-id", "user-1", "--limit", "2"]),
            ("item", ["--id", "item-1", "--user-id", "user-1"]),
            ("browse", ["--library-id", "library-1", "--limit", "2"]),
        ):
            result = subprocess.run([str(SCRIPT), "--json", "--dry-run", command, *arguments],
                                    capture_output=True, text=True)
            with self.subTest(command=command):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(json.loads(result.stdout)["dry_run"])

            help_result = subprocess.run([str(SCRIPT), command, "--help"], capture_output=True, text=True)
            with self.subTest(help_command=command):
                self.assertEqual(help_result.returncode, 0)
                self.assertIn("Example:", help_result.stdout)


class LoginAuthSequenceTests(unittest.TestCase):
    """The login path must demonstrate the researched auth sequence:
    complete pre-token MediaBrowser header on POST /Users/AuthenticateByName,
    AccessToken returned, Token= header for everything after."""

    def run_cli(self, *args):
        return subprocess.run([str(SCRIPT), *args], text=True, capture_output=True,
                              env=clean_env(), cwd=tempfile.gettempdir())

    def test_help_lists_login_and_every_subcommand(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        for noun in ("login", "info", "recent", "search", "next-up", "item",
                     "seasons", "episodes", "browse", "libraries", "stats"):
            self.assertIn(noun, result.stdout)

    def test_login_requires_username(self):
        result = self.run_cli("login")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--username", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_login_dry_run_previews_pre_token_header_without_network(self):
        result = self.run_cli("--dry-run", "--json", "login", "--username", "alice")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["path"], "/Users/AuthenticateByName")
        header = payload["authorization_header"]
        self.assertIn("MediaBrowser", header)
        for part in ("Client=", "Device=", "DeviceId=", "Version="):
            self.assertIn(part, header)
        self.assertNotIn("Token=", header)  # pre-token: no token exists yet
        self.assertTrue(payload["pre_token_header"])

    def test_login_strips_trailing_slash_from_server_override(self):
        result = self.run_cli("--dry-run", "--json", "login", "--username", "bob",
                              "--server", "http://box.local:8096/")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["server"], "http://box.local:8096")

    def test_mocked_login_sends_media_browser_header_and_returns_session(self):
        cli = jellyfin_cli
        cli.GLOBAL_FLAGS = {"json": True, "dry_run": False}
        captured = {}
        response = FakeResponse(200, json_body={
            "User": {"Name": "alice", "Id": "6eec632a-ff0d-4d09-aad0-bf9e90b14bc6"},
            "SessionInfo": {"UserId": "6eec632a-ff0d-4d09-aad0-bf9e90b14bc6"},
            "AccessToken": "at-1234",
            "ServerId": "srv-1",
        })
        with patch.object(cli.requests, "post") as poster:
            poster.return_value = response
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                cli.cmd_login(cli.JellyfinClient(url="http://s:8096", device_id="dev-9"),
                              ["--username", "alice", "--password", "pw"])
            captured["call"] = poster.call_args
        cli.GLOBAL_FLAGS = {"json": False, "dry_run": False}

        args, kwargs = captured["call"]
        self.assertTrue(args[0].endswith("/Users/AuthenticateByName"))
        header = kwargs["headers"]["Authorization"]
        self.assertIn("MediaBrowser", header)
        self.assertIn('DeviceId="dev-9"', header)
        self.assertNotIn("Token=", header)  # pre-token header on the login call itself
        self.assertEqual(kwargs["json"], {"Username": "alice", "Pw": "pw"})
        session = json.loads(output.getvalue())
        self.assertEqual(session["user_id"], "6eec632a-ff0d-4d09-aad0-bf9e90b14bc6")
        self.assertEqual(session["access_token"], "at-1234")
        self.assertIn('Token="at-1234"', session["authorization_header"])

    def test_mocked_login_error_paths_do_not_crash(self):
        cli = jellyfin_cli
        cli.GLOBAL_FLAGS = {"json": False, "dry_run": False}
        for status, expected_fragment in ((400, "400"), (401, "401"), (403, "403")):
            with self.subTest(status=status):
                response = FakeResponse(status, text="Error processing request.")
                with patch.object(cli.requests, "post", return_value=response), \
                        contextlib.redirect_stderr(io.StringIO()) as stderr, \
                        self.assertRaises(SystemExit):
                    cli.cmd_login(cli.JellyfinClient(url="http://s:8096", device_id="d"),
                                  ["--username", "alice", "--password", "bad"])
                self.assertIn(expected_fragment, stderr.getvalue())
        cli.GLOBAL_FLAGS = {"json": False, "dry_run": False}

    def test_reads_require_a_credential_before_network(self):
        cli = jellyfin_cli
        client = cli.JellyfinClient()
        client.key = ""
        client.token = ""
        error = io.StringIO()
        with contextlib.redirect_stderr(error), self.assertRaises(SystemExit):
            client._get("/System/Info")
        self.assertIn("JELLYFIN_API_KEY", error.getvalue())

    def test_client_headers_use_modern_authorization_scheme(self):
        cli = jellyfin_cli
        client = cli.JellyfinClient(key="k-1", device_id="dev-1")
        headers = client._headers()
        self.assertIn('Token="k-1"', headers["Authorization"])
        self.assertTrue(headers["Authorization"].startswith("MediaBrowser "))
        self.assertNotIn("X-Emby-Token", headers)  # one token channel per request
        token_client = cli.JellyfinClient(token="t-1", device_id="dev-1")
        token_headers = token_client._headers()
        self.assertIn('Token="t-1"', token_headers["Authorization"])
        self.assertNotIn("X-Emby-Token", token_headers)

    def test_captured_requests_carry_token_in_exactly_one_channel(self):
        """VAL-JF-009: the access token (or API key) appears in exactly ONE
        channel per request — the MediaBrowser Token= parameter — and the
        legacy X-Emby-Token header is never sent alongside it."""
        cli = jellyfin_cli
        captured = []
        response = FakeResponse(200, json_body={"Items": [], "TotalRecordCount": 0})
        for client in (cli.JellyfinClient(key="k-capture", device_id="dev-cap"),
                       cli.JellyfinClient(token="t-capture", device_id="dev-cap")):
            with patch.object(cli.requests, "get",
                              side_effect=lambda url, **kw: captured.append(kw) or response):
                client._get("/Items")
        self.assertEqual(len(captured), 2)
        for kwargs in captured:
            self.assertIn("headers", kwargs)
            headers = kwargs["headers"]
            self.assertIn("Token=", headers["Authorization"])
            self.assertNotIn("X-Emby-Token", headers)
            channel_count = sum(
                1 for value in headers.values()
                if "Token=" in value or value.lower() == "x-emby-token"
            )
            self.assertEqual(channel_count, 1)


class TvNavigationCommandTests(unittest.TestCase):
    """seasons/episodes commands close the search → seasons → episodes walk."""

    def setUp(self):
        self.flags = jellyfin_cli.GLOBAL_FLAGS
        self.env_user_id = jellyfin_cli.ENV_USER_ID
        jellyfin_cli.GLOBAL_FLAGS = {"json": True, "dry_run": False}
        jellyfin_cli.ENV_USER_ID = ""

    def tearDown(self):
        jellyfin_cli.GLOBAL_FLAGS = self.flags
        jellyfin_cli.ENV_USER_ID = self.env_user_id

    def test_seasons_and_episodes_emit_items_and_consume_ids(self):
        client = NavigationFakeClient()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            jellyfin_cli.cmd_seasons(client, ["--series-id", "series-1",
                                              "--user-id", "user-1"])
        seasons = json.loads(output.getvalue())
        self.assertEqual(seasons["items"][0]["name"], "Season 1")
        self.assertEqual(seasons["items"][0]["season_number"], 1)
        self.assertEqual(client.seasons_calls, [("series-1", "user-1")])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            jellyfin_cli.cmd_episodes(client, ["--series-id", "series-1",
                                               "--season-id", "season-1",
                                               "--user-id", "user-1"])
        episodes = json.loads(output.getvalue())
        self.assertEqual(episodes["items"][0]["episode_number"], 4)
        self.assertEqual(client.episodes_calls, [("series-1", "season-1", "user-1")])

    def test_seasons_and_episodes_require_user_before_network(self):
        for handler, arguments in (
            (jellyfin_cli.cmd_seasons, ["--series-id", "series-1"]),
            (jellyfin_cli.cmd_episodes, ["--series-id", "series-1"]),
        ):
            client = NavigationFakeClient()
            with self.subTest(handler=handler.__name__), \
                    contextlib.redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit):
                handler(client, arguments)
            self.assertEqual(client.seasons_calls, [])
            self.assertEqual(client.episodes_calls, [])

    def test_seasons_and_episodes_dry_run_previews_requests(self):
        cases = (
            (jellyfin_cli.cmd_seasons, ["--series-id", "s1"],
             {"path": "/Shows/s1/Seasons", "params": {"userId": None}}),
            (jellyfin_cli.cmd_episodes, ["--series-id", "s1", "--season-id", "se1",
                                         "--limit", "7"],
             {"path": "/Shows/s1/Episodes",
              "params": {"userId": None, "limit": 7, "startIndex": 0,
                         "seasonId": "se1"}}),
        )
        for handler, arguments, request in cases:
            client = NavigationFakeClient(dry_run=True)
            output = io.StringIO()
            with self.subTest(handler=handler.__name__), \
                    contextlib.redirect_stdout(output):
                handler(client, arguments)
            self.assertEqual(json.loads(output.getvalue()),
                             {"dry_run": True, **request})
            self.assertEqual(client.seasons_calls, [])
            self.assertEqual(client.episodes_calls, [])


class SearchHintIdFallbackTests(unittest.TestCase):
    """SearchHint carries both Id and (deprecated) ItemId; newer servers omit ItemId."""

    def test_prefers_current_id_falls_back_to_deprecated_item_id(self):
        jellyfin_cli.GLOBAL_FLAGS = {"json": True, "dry_run": False}
        try:
            client = Mock()
            client.dry_run = False
            client.search = Mock(return_value={
                "SearchHints": [
                    {"Id": "new-id", "ItemId": "legacy-id", "Name": "Both", "Type": "Series"},
                    {"Id": "only-new", "Name": "Modern", "Type": "Movie"},
                    {"ItemId": "legacy-only", "Name": "Old server", "Type": "Movie"},
                ],
                "TotalRecordCount": 3,
            })
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                jellyfin_cli.cmd_search(client, ["--query", "dune"])
            results = json.loads(output.getvalue())["results"]
            self.assertEqual([r["id"] for r in results],
                             ["new-id", "only-new", "legacy-only"])
        finally:
            jellyfin_cli.GLOBAL_FLAGS = {"json": False, "dry_run": False}


class SearchRequiresQueryTests(unittest.TestCase):
    def test_missing_query_is_argument_error(self):
        result = subprocess.run([str(SCRIPT), "search"], capture_output=True,
                                text=True, env=clean_env())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--query", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class PipelineChainTests(unittest.TestCase):
    """Documented multi-step pipelines must execute stage by stage, each stage
    consuming the previous stage's emitted output (field names AND types)."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory(prefix="jellyfin-pipeline-")

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def run_cli(self, *args):
        return subprocess.run([str(SCRIPT), "--dry-run", "--json", *args],
                              text=True, capture_output=True, env=clean_env(),
                              cwd=self.tmpdir.name)

    def run_jq(self, *jq_args):
        return subprocess.run(["jq", *jq_args], text=True, capture_output=True,
                              env=clean_env(), cwd=self.tmpdir.name)

    def write_stage_file(self, name, document):
        path = pathlib.Path(self.tmpdir.name) / name
        path.write_text(json.dumps(document))
        return str(path)

    def test_search_then_item_chain_consumability(self):
        # Stage 1: search plan; jq extracts the query field (string) the next
        # stage would resolve into an item id.
        r1 = self.run_cli("search", "--query", "dune", "--type", "Movie")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        stage1 = self.write_stage_file("stage1.json", json.loads(r1.stdout))
        term = self.run_jq("-r", ".params.searchTerm", stage1).stdout.strip()
        self.assertEqual(term, "dune")
        types_check = self.run_jq("-r", ".params.includeItemTypes | type", stage1)
        self.assertEqual(types_check.stdout.strip(), "string")

        # Stage 2: item detail plan consumes a hand-built id from stage 1's
        # contract (results[].id is a string); jq proves the id travels into
        # the request path.
        r2 = self.run_cli("item", "--id", "movie-123", "--user-id", "user-9")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        stage2 = self.write_stage_file("stage2.json", json.loads(r2.stdout))
        item_path = self.run_jq("-r", ".path", stage2).stdout.strip()
        self.assertEqual(item_path, "/Items/movie-123")
        user_id = self.run_jq("-r", ".params.userId", stage2).stdout.strip()
        self.assertEqual(user_id, "user-9")

        # Stage 3: next-up plan consumes the same user id and proves it is a
        # JSON string parameter on /Shows/NextUp.
        r3 = self.run_cli("next-up", "--user-id", "user-9", "--limit", "5")
        self.assertEqual(r3.returncode, 0, r3.stderr)
        stage3 = self.write_stage_file("stage3.json", json.loads(r3.stdout))
        self.assertEqual(self.run_jq("-r", ".params.userId", stage3).stdout.strip(),
                         "user-9")
        self.assertEqual(self.run_jq("-r", ".path", stage3).stdout.strip(),
                         "/Shows/NextUp")

    def test_libraries_then_browse_chain_consumability(self):
        # Stage 1: libraries plan; jq type-checks the id field browse consumes.
        r1 = self.run_cli("libraries")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        stage1 = self.write_stage_file("stage1.json", json.loads(r1.stdout))
        self.assertEqual(self.run_jq("-r", ".path", stage1).stdout.strip(),
                         "/Library/MediaFolders")

        # Stage 2: browse plan consumes a library id and paginates by
        # startIndex (number type asserted via jq).
        r2 = self.run_cli("browse", "--library-id", "lib-77", "--start-index", "100")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        stage2 = self.write_stage_file("stage2.json", json.loads(r2.stdout))
        parent = self.run_jq("-r", ".params.parentId", stage2).stdout.strip()
        self.assertEqual(parent, "lib-77")
        start_index_type = self.run_jq("-r", ".params.startIndex | type", stage2)
        self.assertEqual(start_index_type.stdout.strip(), "number")

        # Stage 3: seasons plan consumes a series id discovered by browsing.
        r3 = self.run_cli("seasons", "--series-id", "series-2", "--user-id", "user-1")
        self.assertEqual(r3.returncode, 0, r3.stderr)
        stage3 = self.write_stage_file("stage3.json", json.loads(r3.stdout))
        self.assertEqual(self.run_jq("-r", ".path", stage3).stdout.strip(),
                         "/Shows/series-2/Seasons")

    def test_login_to_recent_chain_previews_token_handoff(self):
        # Stage 1: login plan emits the pre-token header the server requires.
        r1 = self.run_cli("login", "--username", "alice")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        stage1 = self.write_stage_file("stage1.json", json.loads(r1.stdout))
        header = self.run_jq("-r", ".authorization_header", stage1).stdout.strip()
        self.assertIn("MediaBrowser", header)
        self.assertNotIn("Token=", header)

        # Stage 2: user-scoped read plan; the user id login would capture is a
        # string parameter on /Items/Latest (shape: bare array per research).
        r2 = self.run_cli("recent", "--user-id", "6eec632a", "--limit", "20")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        stage2 = self.write_stage_file("stage2.json", json.loads(r2.stdout))
        self.assertEqual(self.run_jq("-r", ".path", stage2).stdout.strip(),
                         "/Items/Latest")
        user_id_type = self.run_jq("-r", ".params.userId | type", stage2)
        self.assertEqual(user_id_type.stdout.strip(), "string")
        self.assertEqual(self.run_jq("-r", ".params.fields", stage2).stdout.strip(),
                         "DateCreated")


class DispatchHardeningTests(unittest.TestCase):
    """main() must dispatch on the first UNCONSUMED subcommand token.

    A value-flag pair whose value NAMES a subcommand while sitting before the
    real command (e.g. `--server search browse ...`) used to make argparse
    dispatch the wrong subparser (the token was swallowed as the flag's value
    and the real command shifted into the value slot). The hardened dispatch
    lifts such pairs out of the top-level argv and re-attaches them to the
    command tail, where parse_known_args already tolerates unknown flags.
    Every other pre-command token still reaches argparse so its errors are
    byte-identical to the pre-hardening CLI.
    """

    def run_cli(self, *args):
        return subprocess.run([str(SCRIPT), *args], text=True, capture_output=True,
                              env=clean_env(), cwd=tempfile.gettempdir())

    def test_flag_value_equal_to_subcommand_dispatches_browse_not_search(self):
        # The exact mis-slice scenario: `--server search` must not dispatch
        # the `search` sub-parser; the real command is `browse`.
        result = self.run_cli("--server", "search", "browse",
                              "--library-id", "lib-1", "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["path"], "/Items")
        self.assertEqual(payload["params"]["parentId"], "lib-1")

    def test_value_hijack_variants_dispatch_the_real_command(self):
        cases = (
            (("recent", "--user-id", "u1", "--limit", "3"), "/Items/Latest"),
            (("search", "--query", "dune"), "/Search/Hints"),
            (("next-up", "--user-id", "u1"), "/Shows/NextUp"),
            (("item", "--id", "i1", "--user-id", "u1"), "/Items/i1"),
            (("seasons", "--series-id", "s1", "--user-id", "u1"), "/Shows/s1/Seasons"),
            (("episodes", "--series-id", "s1", "--user-id", "u1"), "/Shows/s1/Episodes"),
            (("libraries",), "/Library/MediaFolders"),
            (("stats",), "/Items/Counts"),
        )
        for command, expected_path in cases:
            with self.subTest(command=command):
                result = self.run_cli("--server", "search", *command,
                                      "--dry-run", "--json")
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["path"], expected_path)

    def test_hijack_variants_cover_flag_command_and_no_flag_value_commands(self):
        # info emits a `requests` array instead of a path/params pair.
        result = self.run_cli("--server", "search", "info", "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["requests"][0]["path"], "/System/Info")

        # login keeps its plan shape; the misplaced pair rides along as the
        # server value rather than being dropped.
        result = self.run_cli("--server", "search", "login", "--username", "alice",
                              "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["path"], "/Users/AuthenticateByName")
        self.assertEqual(payload["server"], "search")
        self.assertTrue(payload["pre_token_header"])

    def test_all_subcommands_dispatch_from_clean_argv(self):
        cases = (
            (("login", "--username", "alice"), "/Users/AuthenticateByName"),
            (("info",), "/System/Info"),
            (("recent", "--user-id", "u1"), "/Items/Latest"),
            (("search", "--query", "dune"), "/Search/Hints"),
            (("next-up", "--user-id", "u1"), "/Shows/NextUp"),
            (("item", "--id", "i1", "--user-id", "u1"), "/Items/i1"),
            (("seasons", "--series-id", "s1", "--user-id", "u1"), "/Shows/s1/Seasons"),
            (("episodes", "--series-id", "s1", "--user-id", "u1"), "/Shows/s1/Episodes"),
            (("browse", "--library-id", "lib-1"), "/Items"),
            (("libraries",), "/Library/MediaFolders"),
            (("stats",), "/Items/Counts"),
        )
        for command, expected_path in cases:
            with self.subTest(command=command[0]):
                result = self.run_cli(*command, "--dry-run", "--json")
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                if "requests" in payload:  # info composes a request array
                    self.assertEqual(payload["requests"][0]["path"], expected_path)
                else:
                    self.assertEqual(payload["path"], expected_path)

    def test_properly_placed_flag_value_still_wins_over_misplaced_pair(self):
        result = self.run_cli("--server", "search", "login",
                              "--server", "http://real:8096",
                              "--username", "alice", "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["server"], "http://real:8096")

    def test_pre_command_tokens_argparse_owns_are_unchanged(self):
        # Unknown flags, stray positionals, a non-subcommand --server value,
        # a dangling value flag, and `--` all keep their pre-hardening
        # argparse errors (exit 2, no traceback, no tolerant dispatch).
        cases = (
            ("--bogus", "info"),
            ("junk", "browse", "--library-id", "lib-1"),
            ("--server", "http://x:8096", "info"),
            ("--server",),
            ("--", "search", "--query", "dune"),
        )
        for argv in cases:
            with self.subTest(argv=argv):
                result = self.run_cli(*argv, "--dry-run", "--json")
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_find_subcommand_token_returns_command_and_pair_indices(self):
        cli = jellyfin_cli
        subs = {"login", "info", "recent", "search", "next-up", "item", "seasons",
                "episodes", "browse", "libraries", "stats"}
        cases = (
            (["jf", "--server", "search", "browse", "--library-id", "L"], (3, 1)),
            (["jf", "browse", "--library-id", "L"], (1, None)),
            (["jf", "--server", "http://x", "info"], (3, None)),
            (["jf", "login", "--server", "search"], (1, None)),
            (["jf", "--bogus", "info"], (None, None)),
            (["jf", "--server"], (None, None)),
            (["jf", "--"], (None, None)),
        )
        for argv, expected in cases:
            with self.subTest(argv=argv):
                self.assertEqual(
                    cli.find_subcommand_token(argv, subs, cli.VALUE_FLAGS), expected)

    def test_split_misplaced_value_pairs_lifts_only_hijacking_pair(self):
        cli = jellyfin_cli
        subs = {"login", "info", "recent", "search", "next-up", "item", "seasons",
                "episodes", "browse", "libraries", "stats"}
        parse_argv, misplaced = cli.split_misplaced_value_pairs(
            ["jf", "--server", "search", "browse", "--library-id", "L"],
            subs, cli.VALUE_FLAGS)
        self.assertEqual(parse_argv, ["jf", "browse", "--library-id", "L"])
        self.assertEqual(misplaced, ["--server", "search"])

        # A value that is not a subcommand name never lifts anything, and
        # clean argv passes through untouched.
        parse_argv, misplaced = cli.split_misplaced_value_pairs(
            ["jf", "--server", "http://x", "info"], subs, cli.VALUE_FLAGS)
        self.assertEqual((parse_argv, misplaced), (["jf", "--server", "http://x", "info"], []))
        parse_argv, misplaced = cli.split_misplaced_value_pairs(
            ["jf", "login", "--server", "search", "--username", "a"],
            subs, cli.VALUE_FLAGS)
        self.assertEqual(misplaced, [])


if __name__ == "__main__":
    unittest.main()
