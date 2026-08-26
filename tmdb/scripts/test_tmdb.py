import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).with_name("tmdb")


def load_cli():
    loader = importlib.machinery.SourceFileLoader("tmdb_cli", str(SCRIPT))
    spec = importlib.util.spec_from_loader("tmdb_cli", loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TmdbCliTests(unittest.TestCase):
    def run_cli(self, *args):
        env = os.environ.copy()
        env.pop("TMDB_ACCESS_TOKEN", None)
        env.pop("TMDB_API_KEY", None)
        return subprocess.run([str(SCRIPT), *args], text=True, capture_output=True, env=env)

    def test_help_lists_entry_points(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("find", result.stdout)
        self.assertIn("movie", result.stdout)

    def test_missing_required_search_term_is_argument_error(self):
        result = self.run_cli("movie", "search")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--term", result.stderr)

    def test_dry_run_find_emits_json_without_credentials(self):
        result = self.run_cli("--dry-run", "--json", "find", "tt0111161")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)["dry_run"])

    def test_mocked_external_lookup_uses_source_and_parses_results(self):
        cli = load_cli()
        client = cli.TMDBClient()
        client.find_external = Mock(return_value={"movie_results": [{"id": 550, "title": "Fight Club"}]})
        cli.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        with patch("builtins.print") as printed:
            cli.cmd_find(client, ["tt0137523", "--source", "imdb_id"])
        payload = json.loads(printed.call_args.args[0])
        self.assertEqual(payload["movie_results"][0]["id"], 550)
        client.find_external.assert_called_once_with("tt0137523", "imdb_id")

    def test_mocked_detail_passes_append_to_response(self):
        cli = load_cli()
        client = cli.TMDBClient()
        client.get_movie = Mock(return_value={"id": 550, "title": "Fight Club", "credits": {"cast": []}})
        cli.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        with patch("builtins.print"):
            cli.cmd_movie_detail(client, ["550", "--append", "credits,videos"])
        client.get_movie.assert_called_once_with("550", "credits,videos")


if __name__ == "__main__":
    unittest.main()
