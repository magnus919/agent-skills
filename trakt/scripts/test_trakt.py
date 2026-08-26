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


class TraktCliTests(TestCase):
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
        response = mock.Mock(status_code=200)
        response.json.return_value = [{"movie": {"title": "Example"}}]
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
        get.return_value = response
        trakt.TraktClient(client_id="CLIENT_ID").movie_popular()
        die.assert_called_once()
        self.assertIn("403", die.call_args.args[0])


if __name__ == "__main__":
    import unittest

    unittest.main()
