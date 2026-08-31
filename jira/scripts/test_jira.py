"""Offline tests for the bundled jira CLI (scripts/jira).

Four test classes per skill-builder contract:
  1. --help output
  2. argument-error paths
  3. --dry-run behavior
  4. mocked-client logic (requests mocked at the client-call site)

Zero network calls in every test; the proxy-trap rerun proves egress-freedom.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import pathlib
import unittest
from unittest import mock

import requests

SCRIPT = pathlib.Path(__file__).resolve().parent / "jira"
LOADER = importlib.machinery.SourceFileLoader("jira_cli", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
jira_cli = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(jira_cli)


def run_cli(*argv, env_email="ops@example.com", env_token="test-token-123",
            clear_env=False):
    """Invoke main() with argv[0] prepended; returns (exit_code, stdout, stderr).

    clear_env=True strips JIRA_EMAIL/JIRA_API_TOKEN to exercise lazy-auth paths.
    """
    out, err = io.StringIO(), io.StringIO()
    code = 0
    if clear_env:
        env = {}
    else:
        env = {"JIRA_EMAIL": env_email or "", "JIRA_API_TOKEN": env_token or ""}
    with mock.patch.dict("os.environ", env, clear=True):
        with mock.patch.object(jira_cli.sys, "argv", ["jira", *argv]):
            with mock.patch.object(jira_cli.sys, "stdout", out), \
                 mock.patch.object(jira_cli.sys, "stderr", err), \
                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    jira_cli.main()
                except SystemExit as exc:
                    code = exc.code if isinstance(exc.code, int) else 0
    return code, out.getvalue(), err.getvalue()


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text or (json.dumps(payload) if payload is not None else "")
        self.headers = headers or {}

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class SearchPageFactory:
    """Builds legacy-offset search pages for pagination tests."""

    def __init__(self, total, page_size=2, key_prefix="PROJ"):
        self.total = total
        self.page_size = page_size
        self.key_prefix = key_prefix

    def issue(self, n):
        return {"key": f"{self.key_prefix}-{n}",
                "fields": {"summary": f"issue {n}",
                           "status": {"name": "Open"},
                           "issuetype": {"name": "Task"},
                           "assignee": None,
                           "priority": {"name": "Medium"}}}

    def page(self, start_at):
        issues = [self.issue(n) for n in range(
            start_at + 1, min(start_at + self.page_size, self.total) + 1)]
        return {"issues": issues, "startAt": start_at,
                "maxResults": self.page_size, "total": self.total}


# === Class 1: help output ===


class HelpOutputTests(unittest.TestCase):
    def test_help_lists_all_subcommands(self):
        code, out, _ = run_cli("--help")
        self.assertEqual(code, 0)
        for noun in ("me", "list", "view", "projects", "create",
                     "comment", "transition", "transitions", "count"):
            self.assertIn(noun, out)

    def test_subcommand_help_mentions_flags(self):
        _, out, _ = run_cli("list", "--help")
        for flag in ("--jql", "--max", "--project"):
            self.assertIn(flag, out)


# === Class 2: argument errors ===


class ArgumentErrorTests(unittest.TestCase):
    def test_missing_required_jql_on_count(self):
        code, _, err = run_cli("count")
        self.assertEqual(code, 2)
        self.assertIn("--jql", err)

    def test_transition_requires_to_flag(self):
        code, _, err = run_cli("transition", "PROJ-1")
        self.assertEqual(code, 2)
        self.assertIn("--to", err)

    def test_no_command_prints_help_and_exits(self):
        code, out, _ = run_cli()
        self.assertEqual(code, 1)
        self.assertIn("usage:", out)

    def test_unknown_subcommand_fails(self):
        code, _, err = run_cli("frobnicate")
        self.assertEqual(code, 2)
        self.assertIn("invalid choice", err)


# === Class 3: dry-run behavior ===


class DryRunTests(unittest.TestCase):
    def test_dry_run_count_emits_plan_json_without_credentials(self):
        # No JIRA_EMAIL/JIRA_API_TOKEN set at all — lazy auth must not fire.
        code, out, _ = run_cli("--json", "--dry-run", "count",
                               "--jql", "status=Open", clear_env=True)
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["command"], "count")
        self.assertIn("status=Open", plan["jql"])

    def test_dry_run_create_reports_payload_shape(self):
        code, out, _ = run_cli("--json", "--dry-run", "create",
                               "--project", "PROJ", "--summary", "Test issue")
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertEqual(plan["command"], "create")
        self.assertEqual(plan["project"], "PROJ")

    def test_dry_run_never_touches_network(self):
        with mock.patch.object(requests, "request") as req:
            code, out, _ = run_cli("--dry-run", "list", "--project", "PROJ")
            self.assertEqual(code, 0)
            req.assert_not_called()


# === Class 4: mocked client logic ===


class MockedClientTests(unittest.TestCase):
    def setUp(self):
        self.flags = dict(jira_cli.GLOBAL_FLAGS)
        jira_cli.GLOBAL_FLAGS.update(json=True, dry_run=False, quiet=False)
        # Module-level ENV_* constants are captured at import; pin them here so
        # run_cli's env dict is the single source of auth truth in tests.
        self._env = (jira_cli.ENV_EMAIL, jira_cli.ENV_TOKEN)
        jira_cli.ENV_EMAIL = "ops@example.com"
        jira_cli.ENV_TOKEN = "test-token-123"

    def tearDown(self):
        jira_cli.ENV_EMAIL, jira_cli.ENV_TOKEN = self._env
        jira_cli.GLOBAL_FLAGS.clear()
        jira_cli.GLOBAL_FLAGS.update(self.flags)

    def test_list_single_page_parses_issue_rows(self):
        page = SearchPageFactory(total=2, page_size=50)
        resp = FakeResponse(200, page.page(0))
        with mock.patch.object(requests, "request", return_value=resp) as req:
            code, out, _ = run_cli("list", "--project", "PROJ", "--json")
        self.assertEqual(code, 0)
        req.assert_called_once()
        data = json.loads(out)
        self.assertEqual(data["total"], 2)
        self.assertEqual([i["key"] for i in data["issues"]],
                         ["PROJ-1", "PROJ-2"])
        self.assertEqual(data["issues"][0]["assignee"], "Unassigned")

    def test_list_multipage_follows_offset_pagination(self):
        factory = SearchPageFactory(total=5, page_size=2)
        responses = [FakeResponse(200, factory.page(s)) for s in (0, 2, 4)]

        captured = []

        def fake_request(method, url, **kwargs):
            captured.append(kwargs["params"]["startAt"])
            return responses[len(captured) - 1]

        with mock.patch.object(requests, "request", side_effect=fake_request):
            code, out, _ = run_cli("list", "--project", "PROJ", "--max", "100",
                                   "--json")
        self.assertEqual(code, 0)
        self.assertEqual(captured, [0, 2, 4])
        data = json.loads(out)
        self.assertEqual(data["total"], 5)

    def test_list_multipage_stops_on_empty_page_when_total_shrinks(self):
        # Page 1 full, then `total` drops below startAt -> empty page terminates.
        factory = SearchPageFactory(total=4, page_size=2)
        first = factory.page(0)
        second = {"issues": [], "startAt": 2, "maxResults": 2, "total": 2}
        responses = [FakeResponse(200, first), FakeResponse(200, second)]

        def fake_request(method, url, **kwargs):
            return responses.pop(0)

        with mock.patch.object(requests, "request", side_effect=fake_request):
            code, out, _ = run_cli("list", "--max", "60", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(len(data["issues"]), 2)

    def test_error_envelope_is_parsed_into_message(self):
        resp = FakeResponse(400, {"errorMessages": [],
                                  "errors": {"resolution": "Resolution is required"}})
        with mock.patch.object(requests, "request", return_value=resp):
            code, _, err = run_cli("comment", "PROJ-1", "-m", "hi")
        self.assertEqual(code, 1)
        self.assertIn("resolution: Resolution is required", err)

    def test_rate_limit_surfaces_retry_after(self):
        resp = FakeResponse(429, {"errorMessages": []},
                            headers={"Retry-After": "42",
                                     "RateLimit-Reason": "jira-burst-based"})
        with mock.patch.object(requests, "request", return_value=resp):
            code, _, err = run_cli("me")
        self.assertEqual(code, 1)
        self.assertIn("429", err)
        self.assertIn("42", err)
        self.assertIn("jira-burst-based", err)

    def test_auth_failure_names_env_vars(self):
        resp = FakeResponse(401, {"errorMessages": ["Unauthorized"]})
        with mock.patch.object(requests, "request", return_value=resp):
            code, _, err = run_cli("me")
        self.assertEqual(code, 1)
        self.assertIn("JIRA_EMAIL", err)
        self.assertIn("401", err)

    def test_transitions_listing_formats_rows(self):
        payload = {"transitions": [
            {"id": "31", "name": "Done",
             "to": {"name": "Done",
                    "statusCategory": {"key": "completed"}}},
            {"id": "11", "name": "Start Progress",
             "to": {"name": "In Progress",
                    "statusCategory": {"key": "in-flight"}}},
        ]}
        resp = FakeResponse(200, payload)
        with mock.patch.object(requests, "request", return_value=resp):
            code, out, _ = run_cli("transitions", "PROJ-1", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual([t["id"] for t in data["transitions"]], ["31", "11"])

    def test_transition_resolves_name_to_id_and_posts_resolution(self):
        listing = FakeResponse(200, {"transitions": [
            {"id": "31", "name": "Done",
             "to": {"name": "Done",
                    "statusCategory": {"key": "completed"}}}]})

        posted = []

        def fake_request(method, url, **kwargs):
            if method == "GET":
                return listing
            posted.append((url, kwargs.get("json")))
            return FakeResponse(204, None, text="")

        with mock.patch.object(requests, "request", side_effect=fake_request):
            code, out, _ = run_cli("transition", "PROJ-1", "--to", "Done",
                                   "--resolution", "Fixed", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(len(posted), 1)
        url, body = posted[0]
        self.assertIn("/issue/PROJ-1/transitions", url)
        self.assertEqual(body["transition"], {"id": "31"})
        self.assertEqual(body["fields"]["resolution"], {"name": "Fixed"})

    def test_transition_unknown_name_lists_available_options(self):
        listing = FakeResponse(200, {"transitions": [
            {"id": "11", "name": "Start Progress",
             "to": {"name": "In Progress",
                    "statusCategory": {"key": "in-flight"}}}]})
        with mock.patch.object(requests, "request", return_value=listing):
            code, _, err = run_cli("transition", "PROJ-1", "--to", "Done")
        self.assertEqual(code, 1)
        self.assertIn("Available: 11=Start Progress", err)

    def test_count_uses_approximate_count_endpoint(self):
        resp = FakeResponse(200, {"count": 153})

        with mock.patch.object(requests, "request", return_value=resp) as req:
            code, out, _ = run_cli("count", "--jql", "status=Open", "--json")
        self.assertEqual(code, 0)
        url = req.call_args.kwargs["url"]
        self.assertIn("/search/approximate-count", url)
        self.assertEqual(req.call_args.kwargs["json"], {"jql": "status=Open"})
        self.assertEqual(json.loads(out)["count"], 153)

    def test_view_extracts_plain_text_from_adf_description(self):
        adf = {"type": "doc", "version": 1, "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "First paragraph"}]},
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Second paragraph"}]},
        ]}
        payload = {"key": "PROJ-9", "fields": {
            "summary": "Broken flow", "status": {"name": "Open"},
            "issuetype": {"name": "Bug"}, "assignee": None,
            "description": adf}}
        with mock.patch.object(requests, "request",
                               return_value=FakeResponse(200, payload)):
            code, out, _ = run_cli("view", "PROJ-9", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn("First paragraph\nSecond paragraph",
                      data["description"])
        self.assertEqual(data["assignee"], "Unassigned")


if __name__ == "__main__":
    unittest.main()
