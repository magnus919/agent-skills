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


class GenreListParserTests(unittest.TestCase):
    """Regression coverage for `tmdb genre list --type movie|tv`."""

    def run_cli(self, *args):
        env = os.environ.copy()
        env.pop("TMDB_ACCESS_TOKEN", None)
        env.pop("TMDB_API_KEY", None)
        return subprocess.run([str(SCRIPT), *args], text=True, capture_output=True, env=env)

    def test_documented_nested_form_parses_and_dispatches(self):
        result = self.run_cli("--dry-run", "--json", "genre", "list", "--type", "movie")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)["dry_run"])

    def test_flat_form_is_clean_rejection_not_crash(self):
        result = self.run_cli("--json", "genre", "--type", "tv")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("invalid choice", result.stderr)

    def test_missing_type_is_argument_error(self):
        result = self.run_cli("--json", "genre", "list")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--type", result.stderr)

    def test_dispatch_passes_tail_args_without_raw_argv_token_search(self):
        cli = load_cli()
        captured = {}
        real_client_factory = cli.TMDBClient

        def fake_client(dry_run=False):
            return real_client_factory(dry_run=dry_run)

        def fake_handler(client, args):
            captured["args"] = args

        cli.cmd_genre_list = fake_handler
        with patch.object(cli.sys, "argv", ["tmdb", "--dry-run", "genre", "list", "--type", "tv"]):
            cli.main()
        self.assertEqual(captured["args"], ["--type", "tv"])
        self.assertEqual(cli.GLOBAL_FLAGS.get("dry_run"), True)
        fake_client  # client construction stays credential-free


class TvSearchEndpointTests(unittest.TestCase):
    """TV search must hit /search/tv via client.search_tv and format TV fields."""

    def load_with_flags(self):
        cli = load_cli()
        cli.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        return cli

    def test_json_output_uses_search_tv_and_preserves_tv_shape(self):
        cli = self.load_with_flags()
        client = cli.TMDBClient()
        client.search_tv = Mock(return_value={
            "page": 1,
            "total_results": 1,
            "results": [{"id": 9626, "name": "Poirot", "first_air_date": "1989-01-08",
                         "vote_average": 7.9}],
        })
        client.search_movie = Mock(side_effect=AssertionError("/search/movie must not be used"))
        with patch("builtins.print") as printed:
            cli.cmd_tv_search(client, ["--term", "Poirot"])
        payload = json.loads(printed.call_args.args[0])
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["results"][0]["name"], "Poirot")
        self.assertEqual(payload["results"][0]["first_air_date"], "1989-01-08")
        client.search_tv.assert_called_once_with("Poirot")
        client.search_movie.assert_not_called()

    def test_human_output_formats_name_and_first_air_date_year(self):
        cli = load_cli()
        cli.GLOBAL_FLAGS = {"json": False, "dry_run": False, "quiet": False, "verbose": False}
        client = cli.TMDBClient()
        client.search_tv = Mock(return_value={
            "total_results": 1,
            "results": [{"id": 9626, "name": "Poirot", "first_air_date": "1989-01-08",
                         "vote_average": 7.9}],
        })
        with patch("builtins.print") as printed:
            cli.cmd_tv_search(client, ["--term", "Poirot"])
        line = printed.call_args.args[0]
        self.assertIn("Poirot", line)
        self.assertIn("(1989)", line)


class FindExternalSourceTests(unittest.TestCase):
    """Exactly the official eight external_source values are accepted."""

    def test_all_official_sources_are_accepted_parameterized(self):
        cli = load_cli()
        cli.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        self.assertEqual(len(cli.EXTERNAL_SOURCES), 8)
        for source in cli.EXTERNAL_SOURCES:
            with self.subTest(source=source):
                client = cli.TMDBClient()
                client.find_external = Mock(return_value={})
                with patch("builtins.print"):
                    cli.cmd_find(client, [f"ext-{source}", "--source", source])
                client.find_external.assert_called_once_with(f"ext-{source}", source)

    def test_freebase_sources_are_rejected_parameterized(self):
        for retired in ("freebase_mid", "freebase_id"):
            with self.subTest(source=retired):
                result = self.run_cli("--json", "find", "ABC123", "--source", retired)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn(retired, result.stderr)
                self.assertIn("invalid choice", result.stderr)

    def run_cli(self, *args):
        env = os.environ.copy()
        env.pop("TMDB_ACCESS_TOKEN", None)
        env.pop("TMDB_API_KEY", None)
        return subprocess.run([str(SCRIPT), *args], text=True, capture_output=True, env=env)


if __name__ == "__main__":
    unittest.main()
