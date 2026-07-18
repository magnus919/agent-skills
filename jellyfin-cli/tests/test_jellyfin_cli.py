import contextlib
import importlib.machinery
import importlib.util
import io
import json
import pathlib
import subprocess
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "jellyfin-cli"
LOADER = importlib.machinery.SourceFileLoader("jellyfin_cli", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
jellyfin_cli = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(jellyfin_cli)


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

    def get_next_up(self, user_id, limit=10):
        self.next_up_calls.append((user_id, limit))
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
                  sort_order="Ascending", start_index=0):
        self.items_calls.append((parent_id, types, limit, sort_by, sort_order, start_index))
        return {
            "Items": [{"Name": "Arrival", "Type": "Movie", "Id": "movie-1",
                       "ProductionYear": 2016}],
            "StartIndex": start_index,
            "TotalRecordCount": 1,
        }


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

        client.get_next_up("user-1", limit=3)
        client.get_item("item-1", "user-1")
        client.get_items("library-1", types=["Movie", "Series"], limit=4, start_index=2)

        self.assertEqual(calls, [
            ("/Shows/NextUp", {"userId": "user-1", "limit": 3}),
            ("/Items/item-1", {"userId": "user-1"}),
            ("/Items", {"parentId": "library-1", "limit": 4, "sortBy": "SortName",
                        "sortOrder": "Ascending", "startIndex": 2, "recursive": True,
                        "includeItemTypes": "Movie,Series"}),
        ])

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
        self.assertEqual(client.next_up_calls, [("user-1", 3)])

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
                                              "--limit", "4", "--start-index", "2"])
        self.assertEqual(json.loads(output.getvalue()), {
            "items": [{"id": "movie-1", "name": "Arrival", "type": "Movie", "year": 2016}],
            "start_index": 2,
            "total_record_count": 1,
        })
        self.assertEqual(client.items_calls, [("library-1", ["Movie"], 4, "SortName", "Ascending", 2)])

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


if __name__ == "__main__":
    unittest.main()
