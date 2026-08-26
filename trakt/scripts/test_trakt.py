#!/usr/bin/env python3
"""Offline tests for the Trakt discovery CLI."""
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase, mock

SCRIPT = Path(__file__).with_name("trakt")
loader = importlib.machinery.SourceFileLoader("trakt_cli", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
trakt = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = trakt
loader.exec_module(trakt)


def _response(items, headers):
    response = mock.Mock(status_code=200)
    response.json.return_value = items
    response.headers = headers
    return response


FULL_PAGINATION_HEADERS = {
    "X-Pagination-Page": "2",
    "X-Pagination-Limit": "1",
    "X-Pagination-Page-Count": "3405",
    "X-Pagination-Item-Count": "10",
}


class TraktCliTests(TestCase):
    """Original CLI surface coverage: help, errors, dry-run, header injection."""

    def run_cli(self, *args, **kwargs):
        env = os.environ.copy()
        env.pop("TRAKT_CLIENT_ID", None)
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)

    def test_help_lists_discovery_groups(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("movie", result.stdout)
        self.assertIn("tv", result.stdout)

    def test_argument_error_is_nonzero(self):
        result = self.run_cli("movie", "unknown")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_dry_run_json_is_valid_without_network(self):
        result = self.run_cli("--dry-run", "--json", "movie", "trending")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload, {"dry_run": True})

    @mock.patch.object(trakt.requests, "get")
    def test_client_injects_required_header_pair(self, get):
        response = _response([{"movie": {"title": "Example"}}], {})
        get.return_value = response
        client = trakt.TraktClient(client_id="CLIENT_ID")
        client.movie_trending(limit=4)
        headers = get.call_args.kwargs["headers"]
        self.assertEqual(headers["trakt-api-key"], "CLIENT_ID")
        self.assertEqual(headers["trakt-api-version"], "2")
        self.assertEqual(headers["Content-Type"], "application/json")

    @mock.patch.object(trakt, "die")
    @mock.patch.object(trakt.requests, "get")
    def test_client_reports_http_error(self, get, die):
        response = mock.Mock(status_code=403)
        response.json.return_value = {"message": "forbidden"}
        response.headers = {}
        get.return_value = response
        trakt.TraktClient(client_id="CLIENT_ID").movie_popular()
        die.assert_called_once()
        self.assertIn("403", die.call_args.args[0])


class PaginationRequestTests(TestCase):
    """--page/--limit flow from argv into request query parameters."""

    def setUp(self):
        flags = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        patcher = mock.patch.object(trakt, "GLOBAL_FLAGS", flags)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_page_two_is_sent_as_query_parameter(self):
        client = trakt.TraktClient(client_id="CLIENT_ID")
        client._get = mock.Mock(return_value=([], {"page": 2}))
        with mock.patch("builtins.print"):
            trakt.cmd_discovery(client, "movie", "trending", ["--page", "2"])
        client._get.assert_called_once_with("/movies/trending", {"page": 2, "limit": 10})

    @mock.patch.object(trakt.requests, "get")
    def test_requests_get_receives_page_and_limit_params(self, get):
        get.return_value = _response([], {})
        client = trakt.TraktClient(client_id="CLIENT_ID")
        client.tv_popular(page=3, limit=25)
        self.assertEqual(get.call_args.kwargs["params"], {"page": 3, "limit": 25})

    def test_every_discovery_command_accepts_explicit_page_and_limit(self):
        pairs = [("movie", action) for action in ("trending", "popular", "anticipated")]
        pairs += [("tv", action) for action in ("trending", "popular", "anticipated")]
        segments = {"movie": "movies", "tv": "shows"}
        keys = {"movie": "movies", "tv": "shows"}
        for resource, action in pairs:
            with self.subTest(command=f"{resource} {action}"):
                client = trakt.TraktClient(client_id="CLIENT_ID")
                client._get = mock.Mock(return_value=(None, {}))
                with mock.patch("builtins.print") as printed:
                    trakt.cmd_discovery(client, resource, action, ["--page", "3", "--limit", "7"])
                expected_path = f"/{segments[resource]}/{action}"
                client._get.assert_called_once_with(expected_path, {"page": 3, "limit": 7})
                if trakt.GLOBAL_FLAGS["json"]:
                    self.assertEqual(json.loads(printed.call_args.args[0]), {keys[resource]: [], "pagination": {}})
                else:
                    self.assertIn("No", printed.call_args.args[0])

    def test_dry_run_json_accepts_page_without_network_or_credentials(self):
        env = os.environ.copy()
        env.pop("TRAKT_CLIENT_ID", None)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--dry-run", "--json", "tv", "anticipated", "--page", "2"],
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)["dry_run"])


class PaginationHeaderTests(TestCase):
    """X-Pagination-* normalization and missing-header degradation."""

    def test_all_four_headers_map_onto_stable_keys(self):
        pagination = trakt.normalize_pagination(dict(FULL_PAGINATION_HEADERS))
        self.assertEqual(
            pagination,
            {"page": 2, "limit": 1, "page_count": 3405, "item_count": 10},
        )

    def test_lowercase_header_names_are_normalized(self):
        lower = {key.lower(): value for key, value in FULL_PAGINATION_HEADERS.items()}
        self.assertEqual(trakt.normalize_pagination(lower)["page_count"], 3405)

    def test_missing_headers_degrade_to_empty_object(self):
        self.assertEqual(trakt.normalize_pagination({}), {})

    def test_unparseable_and_partial_values_are_skipped(self):
        headers = {"X-Pagination-Page": "2", "X-Pagination-Limit": "", "X-Pagination-Item-Count": "not-a-number"}
        pagination = trakt.normalize_pagination(headers)
        self.assertEqual(pagination, {"page": 2})

    @mock.patch.object(trakt.requests, "get")
    def test_response_without_pagination_headers_yields_empty_pagination_object(self, get):
        get.return_value = _response([{"movie": {"title": "Example"}}], {"Content-Type": "application/json"})
        _, pagination = trakt.TraktClient(client_id="CLIENT_ID").movie_trending()
        self.assertEqual(pagination, {})


class DiscoveryOutputTests(TestCase):
    """Stable JSON shapes beside the new pagination metadata."""

    def json_payload_for(self, resource, endpoint, argv, items, headers=None):
        flags = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        client = trakt.TraktClient(client_id="CLIENT_ID")
        if hasattr(client, f"{resource}_{endpoint}"):
            setattr(client, f"{resource}_{endpoint}",
                    mock.Mock(return_value=(items, trakt.normalize_pagination(headers or {}))))
        else:
            client._get = mock.Mock(return_value=(items, trakt.normalize_pagination(headers or {})))
        with mock.patch.object(trakt, "GLOBAL_FLAGS", flags), mock.patch("builtins.print") as printed:
            trakt.cmd_discovery(client, resource, endpoint, argv)
        return json.loads(printed.call_args.args[0])

    def test_movie_trending_json_keeps_movies_key_beside_pagination(self):
        payload = self.json_payload_for(
            "movie", "trending", ["--page", "2"],
            [{"movie": {"title": "Heat", "year": 1995, "ids": {"tmdb": 949}}}],
            FULL_PAGINATION_HEADERS,
        )
        self.assertIn("movies", payload)
        self.assertEqual(payload["pagination"],
                         {"page": 2, "limit": 1, "page_count": 3405, "item_count": 10})
        entry = payload["movies"][0]
        self.assertEqual(entry["movie"]["title"], "Heat")
        self.assertEqual(entry["movie"]["ids"]["tmdb"], 949)

    def test_tv_popular_json_keeps_show_objects_directly_nested(self):
        payload = self.json_payload_for(
            "tv", "popular", ["--limit", "5"],
            [{"title": "Poirot", "year": 1989, "ids": {"tvdb": 70739}}][:1],
            FULL_PAGINATION_HEADERS,
        )
        self.assertIn("shows", payload)
        self.assertEqual(payload["shows"][0]["title"], "Poirot")
        self.assertEqual(payload["shows"][0]["ids"]["tvdb"], 70739)
        self.assertEqual(payload["pagination"]["page_count"], 3405)

    def test_tv_trending_keeps_wrapper_shape_in_json(self):
        payload = self.json_payload_for(
            "tv", "trending", [],
            [{"show": {"title": "Severance", "ids": {"tvdb": 365278}}}],
            FULL_PAGINATION_HEADERS,
        )
        self.assertIn("show", payload["shows"][0])
        self.assertEqual(payload["pagination"]["item_count"], 10)

    def test_human_output_states_current_and_total_pages(self):
        client = trakt.TraktClient(client_id="CLIENT_ID")
        client.movie_trending = mock.Mock(return_value=(
            [{"movie": {"title": "Heat", "year": 1995, "ids": {"tmdb": 949}}}],
            {"page": 2, "limit": 1, "page_count": 3405, "item_count": 10},
        ))
        with mock.patch.object(trakt, "GLOBAL_FLAGS",
                               {"json": False, "dry_run": False, "quiet": False, "verbose": False}), \
             mock.patch("builtins.print") as printed:
            trakt.cmd_discovery(client, "movie", "trending", ["--page", "2"])
        output = printed.call_args.args[0]
        self.assertIn("Heat", output)
        self.assertIn("Page 2 of 3405", output)

    def test_human_output_without_pagination_headers_prints_no_page_line(self):
        client = trakt.TraktClient(client_id="CLIENT_ID")
        client.tv_popular = mock.Mock(return_value=(
            [{"show": {"title": "Fargo", "year": 2014, "ids": {"tvdb": 269584}}}], {},
        ))
        with mock.patch.object(trakt, "GLOBAL_FLAGS",
                               {"json": False, "dry_run": False, "quiet": False, "verbose": False}), \
             mock.patch("builtins.print") as printed:
            trakt.cmd_discovery(client, "tv", "popular", [])
        output = printed.call_args.args[0]
        self.assertIn("Fargo", output)
        self.assertNotIn("Page ", output)


if __name__ == "__main__":
    import unittest

    unittest.main()
