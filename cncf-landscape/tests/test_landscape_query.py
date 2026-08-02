#!/usr/bin/env python3
"""Offline tests for the CNCF Landscape query client."""

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stderr
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "landscape_query.py"
SPEC = importlib.util.spec_from_file_location("landscape_query", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load landscape_query.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, payload, content_type="application/json", status=200, headers=None):
        self.payload = payload
        self.status = status
        self.headers = {"Content-Type": content_type}
        if headers:
            self.headers.update(headers)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.payload


def fake_opener(response):
    def opener(request, timeout):
        assert timeout == 4.0
        assert request.full_url.endswith("/projects/all.json")
        assert request.headers.get("Accept") == "application/json"
        return response

    return opener


class LandscapeQueryTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {
                "id": "alpha",
                "name": "Alpha Trace",
                "summary": "Tracing for Kubernetes",
                "category": "Observability and Analysis",
                "subcategory": "Observability",
                "maturity": "graduated",
                "oss": True,
                "country": "United States",
                "repositories": [
                    {
                        "primary": True,
                        "stars": 40,
                        "contributors": 12,
                        "license": "Apache License 2.0",
                        "latest_release": "2026-07-01T00:00:00Z",
                    }
                ],
            },
            {
                "id": "beta",
                "name": "Beta Trace",
                "summary": "Tracing for a different runtime",
                "category": "Observability and Analysis",
                "subcategory": "Observability",
                "maturity": "incubating",
                "oss": True,
                "country": "Canada",
                "repositories": [
                    {
                        "primary": True,
                        "stars": 100,
                        "contributors": 4,
                        "license": None,
                        "latest_release": None,
                    }
                ],
            },
            {
                "id": "gamma",
                "name": "Gamma Router",
                "summary": "A gateway",
                "category": "Orchestration & Management",
                "subcategory": "API Gateway",
                "maturity": "sandbox",
                "oss": True,
                "repositories": [],
            },
        ]

    def test_filters_and_sorts_projects(self):
        args = MODULE.build_parser().parse_args(
            [
                "--search",
                "tracing",
                "--category",
                "Observability and Analysis",
                "--subcategory",
                "Observability",
                "--maturity",
                "graduated",
                "--has-license",
                "--has-release",
                "--min-stars",
                "30",
                "--sort",
                "stars",
            ]
        )
        selected = MODULE.select_records(self.records, args)
        self.assertEqual([item["id"] for item in selected], ["alpha"])

    def test_repeated_maturity_filter_and_limit_zero(self):
        args = MODULE.build_parser().parse_args(
            ["--maturity", "graduated", "--maturity", "incubating", "--limit", "0"]
        )
        selected = MODULE.select_records(self.records, args)
        self.assertEqual([item["id"] for item in selected], ["alpha", "beta"])

    def test_run_returns_snapshot_metadata_and_raw_items(self):
        response = FakeResponse(
            json.dumps(self.records).encode("utf-8"),
            headers={"Last-Modified": "Tue, 28 Jul 2026 09:06:48 GMT"},
        )
        args = MODULE.build_parser().parse_args(["--base-url", "https://example.test/api", "--timeout", "4"])
        result = MODULE.run(args, opener=fake_opener(response))
        self.assertEqual(result["endpoint"], "https://example.test/api/projects/all.json")
        self.assertEqual(result["total_records"], 3)
        self.assertEqual(result["returned_records"], 3)
        self.assertEqual(result["last_modified"], "Tue, 28 Jul 2026 09:06:48 GMT")
        self.assertEqual(result["items"][0]["id"], "alpha")

    def test_html_fallback_fails_closed(self):
        response = FakeResponse(b"<html>single page app</html>", content_type="text/html")
        with self.assertRaisesRegex(MODULE.LandscapeError, "Expected JSON"):
            MODULE.fetch_records("https://example.test/api/projects/all.json", 4.0, fake_opener(response))

    def test_malformed_base_url_uses_cli_error_path(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = MODULE.main(["--base-url", "not-a-url", "--timeout", "1"])

        self.assertEqual(exit_code, 2)
        self.assertIn("Error: Invalid Landscape API URL", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_non_object_records_fail_closed(self):
        response = FakeResponse(b"[{}\n,\"not an object\"]")
        with self.assertRaisesRegex(MODULE.LandscapeError, "non-object record"):
            MODULE.fetch_records("https://example.test/api/projects/all.json", 4.0, fake_opener(response))

    def test_negative_limit_is_rejected(self):
        args = MODULE.build_parser().parse_args(["--limit", "-1"])
        with self.assertRaisesRegex(MODULE.LandscapeError, "--limit"):
            MODULE.select_records(self.records, args)


if __name__ == "__main__":
    unittest.main()
