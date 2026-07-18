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


if __name__ == "__main__":
    unittest.main()
