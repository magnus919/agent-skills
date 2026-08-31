"""Offline tests for the bundled openlibrary CLI (scripts/openlibrary).

Four test classes per skill-builder contract:
  1. --help output
  2. argument-error paths
  3. --dry-run behavior
  4. mocked-client logic (requests mocked at the client-call site)

Plus one env-guarded live class: Open Library is a keyless public API, so a
small bounded set of live GETs runs ONLY when OPENLIBRARY_LIVE_TESTS=1; they
skip cleanly otherwise (proxy-trap reruns pass with them skipped).
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import unittest
from unittest import mock

import requests

SCRIPT = pathlib.Path(__file__).resolve().parent / "openlibrary"
LOADER = importlib.machinery.SourceFileLoader("openlibrary_cli", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
ol_cli = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(ol_cli)

EDITION_KEY = "/books/" + "OL34854896M"
WORK_KEY = "/works/" + "OL1168083W"
AUTHOR_KEY = "/authors/" + "OL118077A"


def run_cli(*argv):
    """Invoke main() with argv[0] prepended; returns (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with mock.patch.object(ol_cli.sys, "argv", ["openlibrary", *argv]):
        with mock.patch.object(ol_cli.sys, "stdout", out), \
             mock.patch.object(ol_cli.sys, "stderr", err), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                ol_cli.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 0
    return code, out.getvalue(), err.getvalue()


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", headers=None,
                 url="https://openlibrary.org/x"):
        self.status_code = status_code
        self._payload = payload
        self.text = text or (json.dumps(payload) if payload is not None else "")
        self.headers = headers or {}
        self.url = url

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


# === Class 1: help output ===


class HelpOutputTests(unittest.TestCase):
    def test_help_lists_all_subcommands(self):
        code, out, _ = run_cli("--help")
        self.assertEqual(code, 0)
        for noun in ("search", "search-authors", "author", "work",
                     "isbn", "editions", "ratings"):
            self.assertIn(noun, out)

    def test_help_mentions_keyless_setup(self):
        _, out, _ = run_cli("--help")
        self.assertIn("No API key", out)

    def test_subcommand_help_mentions_flags(self):
        _, out, _ = run_cli("search", "--help")
        for flag in ("--query", "--limit", "--offset", "--sort", "--lang"):
            self.assertIn(flag, out)

    def test_editions_help_documents_pagination(self):
        _, out, _ = run_cli("editions", "--help")
        self.assertIn("--limit", out)
        self.assertIn("--offset", out)


# === Class 2: argument errors ===


class ArgumentErrorTests(unittest.TestCase):
    def test_search_requires_query(self):
        code, _, err = run_cli("search")
        self.assertEqual(code, 2)
        self.assertIn("--query", err)

    def test_no_command_prints_help_and_exits(self):
        code, out, _ = run_cli()
        self.assertEqual(code, 1)
        self.assertIn("usage:", out)

    def test_unknown_subcommand_fails(self):
        code, _, err = run_cli("frobnicate")
        self.assertEqual(code, 2)
        self.assertIn("invalid choice", err)

    def test_sort_rejects_unknown_values_client_side(self):
        # A bogus sort value makes Open Library return a plain-text HTTP 500,
        # so the CLI validates sort choices before ever sending.
        code, _, err = run_cli("search", "--query", "dune", "--sort", "bogus")
        self.assertEqual(code, 2)
        self.assertIn("--sort", err)


# === Class 3: dry-run behavior ===


class DryRunTests(unittest.TestCase):
    def test_dry_run_isbn_reports_302_resolution_plan(self):
        code, out, _ = run_cli("--dry-run", "--json", "isbn", "9780451524935")
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["command"], "isbn")
        self.assertIn("/isbn/9780451524935.json", plan["url"])
        self.assertIn("302", plan["note"])

    def test_dry_run_editions_emits_query_params(self):
        code, out, _ = run_cli("--json", "--dry-run", "editions",
                               WORK_KEY, "--limit", "5")
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertEqual(plan["key"], "OL1168083W")
        self.assertEqual(plan["params"]["limit"], 5)

    def test_dry_run_ratings_plans_both_endpoints(self):
        code, out, _ = run_cli("--dry-run", "--json", "ratings", "OL45804W")
        self.assertEqual(code, 0)
        plan = json.loads(out)
        joined = " ".join(plan["urls"])
        self.assertIn("/ratings.json", joined)
        self.assertIn("/bookshelves.json", joined)

    def test_dry_run_never_touches_network(self):
        with mock.patch.object(requests, "get") as req:
            code, _, _ = run_cli("--dry-run", "work", WORK_KEY)
            self.assertEqual(code, 0)
            req.assert_not_called()


# === Class 4: mocked client logic ===


EDITION_RECORD = {
    "type": {"key": "/type/edition"},
    "key": EDITION_KEY,
    "title": "Nineteen Eighty-Four",
    "authors": None,                      # real records ship authors:null sometimes
    "works": [{"key": WORK_KEY}],
    "covers": [12054527, -1],
    "number_of_pages": 328,
    "publish_date": "1993?",
    "publishers": ["Signet Classics"],
    "description": {"type": "/type/text", "value": "A dystopian classic."},
}

WORK_RECORD = {
    "type": {"key": "/type/work"},
    "key": WORK_KEY,
    "title": "Nineteen Eighty-Four",
    "authors": [{"author": {"key": AUTHOR_KEY},
                 "type": {"key": "/type/author_role"}}],
    "subjects": ["Totalitarianism"],
    "description": "A dystopian classic.",
    "covers": [-1],
}


class MockedClientTests(unittest.TestCase):
    """Mock requests.get at the client-call site; zero network in this class."""

    def setUp(self):
        ol_cli.QUIET = False
        ol_cli.GLOBAL_FLAGS.update(json=True, dry_run=False, quiet=False)

    def test_isbn_surfaces_resolved_edition_and_work_keys(self):
        # The edition record carries works[] but authors:null, so the CLI
        # follows the work link once to recover author keys.
        edition = FakeResponse(
            200, EDITION_RECORD,
            url="https://openlibrary.org/books/" + "OL34854896M.json")
        work = FakeResponse(200, WORK_RECORD)
        with mock.patch.object(requests, "get", side_effect=[edition, work]) as req:
            code, out, _ = run_cli("--json", "isbn", "9780451524935")
        self.assertEqual(code, 0)
        self.assertEqual(req.call_count, 2)
        data = json.loads(out)
        self.assertEqual(data["edition_key"], "OL34854896M")
        self.assertEqual(data["work_keys"], ["OL1168083W"])
        # Cover URLs point at the SEPARATE covers host, skipping -1 placeholders.
        self.assertEqual(data["cover_url"], (
            "https://covers.openlibrary.org/b/id/"
            + "12054527-M.jpg"))

    def test_isbn_falls_back_to_work_authors_when_edition_has_none(self):
        edition = FakeResponse(200, EDITION_RECORD)
        work = FakeResponse(200, WORK_RECORD)
        with mock.patch.object(requests, "get", side_effect=[edition, work]) as req:
            code, out, _ = run_cli("--json", "isbn", "9780451524935")
        self.assertEqual(code, 0)
        self.assertEqual(req.call_count, 2)
        self.assertTrue(req.call_args_list[1].args[0].endswith(WORK_KEY + ".json"))
        self.assertEqual(json.loads(out)["authors"], ["OL118077A"])

    def test_work_with_explicit_null_authors_returns_empty_array(self):
        # Real-world work records sometimes carry an explicit "authors": null;
        # the CLI must render '?' and hand off [] instead of raising TypeError.
        record = dict(WORK_RECORD, authors=None)
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, record)):
            code, out, _ = run_cli("--json", "work", WORK_KEY)
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIsInstance(data["authors"], list)
        self.assertEqual(data["authors"], [])
        ol_cli.GLOBAL_FLAGS.update(json=False)
        try:
            with mock.patch.object(requests, "get",
                                   return_value=FakeResponse(200, record)):
                human_code, human_out, _ = run_cli("work", WORK_KEY)
        finally:
            ol_cli.GLOBAL_FLAGS.update(json=True)
        self.assertEqual(human_code, 0)
        self.assertIn("?", human_out)

    def test_isbn_and_work_emit_same_json_type_under_authors_key(self):
        # Symmetry contract: any "authors"-keyed field across CLI commands is a
        # JSON array of bare OL…A key strings. Downstream jq pipelines can
        # treat .authors identically regardless of the entry command.
        edition_authored = {
            "type": {"key": "/type/edition"},
            "key": EDITION_KEY,
            "title": "Nineteen Eighty-Four",
            "authors": [{"key": AUTHOR_KEY}],
            "works": [{"key": WORK_KEY}],
        }
        edition = FakeResponse(200, edition_authored)
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, WORK_RECORD)):
            _, work_out, _ = run_cli("--json", "work", WORK_KEY)
            _, isbn_out, _ = run_cli("--json", "isbn", "9780451524935")
        work_data = json.loads(work_out)
        isbn_data = json.loads(isbn_out)
        for data in (work_data, isbn_data):
            self.assertIsInstance(data["authors"], list)
            self.assertNotIsInstance(data["authors"], str)
            self.assertTrue(all(
                isinstance(k, str) and k.endswith("A")
                for k in data["authors"]))
        self.assertEqual(isbn_data["authors"], ["OL118077A"])
        self.assertEqual(work_data["authors"], ["OL118077A"])

    def test_edition_key_only_author_refs_become_bare_keys_in_json(self):
        edition_authored = {
            "type": {"key": "/type/edition"},
            "key": EDITION_KEY,
            "title": "Nineteen Eighty-Four",
            "authors": [{"key": "/authors/" + "OL118077A"},
                        {"key": "/authors/" + "OL7862984A"}],
            "works": [{"key": WORK_KEY}],
        }
        edition = FakeResponse(200, edition_authored)
        with mock.patch.object(requests, "get", return_value=edition) as req:
            code, out, _ = run_cli("--json", "isbn", "9780451524935")
        self.assertEqual(code, 0)
        self.assertEqual(req.call_count, 1)  # no fallback read needed
        data = json.loads(out)
        self.assertEqual(data["authors"],
                         sorted(["OL118077A", "OL7862984A"]))

    def test_isbn_human_output_still_shows_comma_joined_labels(self):
        # The display surface is unchanged: comma-joined names on stdout while
        # --json carries the array shape.
        edition = FakeResponse(200, {
            "type": {"key": "/type/edition"}, "key": EDITION_KEY,
            "title": "Nineteen Eighty-Four",
            "authors": [{"name": "George Orwell"}, {"name": "Thomas Pynchon"}],
            "works": [{"key": WORK_KEY}]})
        ol_cli.GLOBAL_FLAGS.update(json=False)
        try:
            with mock.patch.object(requests, "get", return_value=edition):
                code, out, _ = run_cli("isbn", "9780451524935")
        finally:
            ol_cli.GLOBAL_FLAGS.update(json=True)
        self.assertEqual(code, 0)
        self.assertIn("George Orwell, Thomas Pynchon", out)

    def test_work_json_authors_are_bare_keys_array(self):
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, WORK_RECORD)):
            code, out, _ = run_cli("--json", "work", WORK_KEY)
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIsInstance(data["authors"], list)
        self.assertEqual(data["authors"], ["OL118077A"])
        self.assertRegex(data["authors"][0], r"^OL\d+A$")

    def test_isbn_work_author_pipeline_handoff_is_executable(self):
        """Mock the documented ISBN -> work -> author jq handoff end to end."""
        edition = FakeResponse(200, EDITION_RECORD)
        work = FakeResponse(200, WORK_RECORD)
        author = FakeResponse(200, {"name": "George Orwell", "bio": "Writer"})
        with mock.patch.object(requests, "get",
                               side_effect=[edition, work, work, author]) as req:
            isbn_code, isbn_out, _ = run_cli("--json", "isbn", "9780451524935")
            isbn_data = json.loads(isbn_out)
            work_code, work_out, _ = run_cli(
                "--json", "work", isbn_data["work_keys"][0])
            work_data = json.loads(work_out)
            author_code, author_out, _ = run_cli(
                "--json", "author", work_data["authors"][0])
        self.assertEqual((isbn_code, work_code, author_code), (0, 0, 0))
        self.assertEqual(req.call_count, 4)
        self.assertEqual(work_data["authors"][0], "OL118077A")
        self.assertEqual(json.loads(author_out)["key"], "OL118077A")

    def test_work_pipeline_handoff_fields_have_stable_json_types(self):
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, WORK_RECORD)):
            _, out, _ = run_cli("--json", "work", WORK_KEY)
        data = json.loads(out)
        self.assertIsInstance(data["key"], str)
        self.assertIsInstance(data["title"], str)
        self.assertIsInstance(data["authors"], list)
        self.assertTrue(all(isinstance(key, str) for key in data["authors"]))
        self.assertIsInstance(data["subjects"], list)

    def test_work_record_with_non_dict_author_entries_is_tolerated(self):
        # Malformed wiki payloads can smuggle bare strings into authors[];
        # tolerate-and-filter beats crash.
        record = dict(WORK_RECORD,
                      authors=[{"author": {"key": AUTHOR_KEY}}, None])
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, record)):
            code, out, _ = run_cli("--json", "work", WORK_KEY)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["authors"], ["OL118077A"])

    def test_isbn_handoff_fields_have_stable_json_types(self):
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(
                                   200, dict(EDITION_RECORD, authors=None),
                                   url="https://openlibrary.org/books/x.json")):
            _, out, _ = run_cli("--json", "isbn", "9780451524935")
        data = json.loads(out)
        for key in ("edition_key", "title", "description"):
            self.assertIsInstance(data[key], str)
        for key in ("authors", "work_keys", "publishers", "subjects"):
            self.assertIsInstance(data[key], list)

    def test_merge_redirect_stub_in_http_200_is_followed_with_json_suffix(self):
        # Merged-away keys answer 200 with {type:/type/redirect, location},
        # NOT a 3xx — the client must detect the stub and refetch. Stub
        # locations are bare keys without .json; extension-less URLs redirect
        # to HTML pages, so the client must append the suffix itself.
        stub = FakeResponse(200, {"type": {"key": "/type/redirect"},
                                  "location": WORK_KEY})
        work = FakeResponse(200, WORK_RECORD)
        with mock.patch.object(requests, "get", side_effect=[stub, work]) as req:
            code, out, _ = run_cli("--json", "work", "OL24776360W")
        self.assertEqual(code, 0)
        self.assertEqual(
            req.call_args_list[1].args[0],
            "https://openlibrary.org" + WORK_KEY + ".json")
        self.assertEqual(json.loads(out)["title"], "Nineteen Eighty-Four")

    def test_redirect_stub_chain_beyond_hop_budget_warns_instead_of_silence(self):
        # A work that keeps resolving into further merge stubs exhausts the
        # bounded walk; the CLI must say so (stderr warning) rather than emit
        # an unexplained /type/redirect payload.
        stub = FakeResponse(200, {"type": {"key": "/type/redirect"},
                                  "location": WORK_KEY})
        responses = [stub] * (ol_cli.MAX_REDIRECT_HOPS + 1)
        with mock.patch.object(requests, "get",
                               side_effect=responses) as req:
            code, out, err = run_cli("--json", "work", "OL24776360W")
        self.assertEqual(code, 0)
        self.assertEqual(req.call_count, ol_cli.MAX_REDIRECT_HOPS + 1)
        self.assertIn("did not resolve", err)
        # Without the resolution the command degrades to an empty-shaped
        # record; the stderr warning is what keeps that from being silent.
        self.assertEqual(json.loads(out), {
            "key": "OL24776360W", "title": "?", "authors": [],
            "description": "", "subjects": [], "cover_url": None})

    def test_text_wrapper_dict_is_unwrapped(self):
        self.assertEqual(ol_cli.unwrap_text({"type": "/type/text", "value": "hi"}), "hi")
        self.assertEqual(ol_cli.unwrap_text("plain"), "plain")
        self.assertEqual(ol_cli.unwrap_text(None), "")

    def test_normalize_olid_accepts_bare_and_path_forms(self):
        self.assertEqual(ol_cli.normalize_olid("/works/" + "OL123W"), "OL123W")
        self.assertEqual(ol_cli.normalize_olid("OL23919A"), "OL23919A")
        self.assertEqual(ol_cli.normalize_olid(""), "")

    def test_cover_url_rejects_negative_placeholder_ids(self):
        self.assertIsNone(ol_cli.cover_url("b/id", -1))
        self.assertIsNone(ol_cli.cover_url("a/id", None))
        self.assertTrue(ol_cli.cover_url("b/id", 12054527).startswith(
            "https://covers.openlibrary.org/b/id/"))

    def test_search_sends_query_and_sort_params(self):
        payload = {"numFound": 1, "docs": [
            {"key": "/works/" + "OL1W", "title": "Dune",
             "author_name": ["Frank Herbert"], "first_publish_year": 1965,
             "edition_count": 90, "cover_edition_key": "OL1M",
             "has_fulltext": True}]}
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, payload)) as req:
            code, out, _ = run_cli("--json", "search", "--query", "dune",
                                   "--limit", "2", "--sort", "editions")
        self.assertEqual(code, 0)
        req.assert_called_once()
        sent = req.call_args.kwargs["params"]
        self.assertEqual(sent["q"], "dune")
        self.assertEqual(sent["sort"], "editions")
        data = json.loads(out)
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["key"], "/works/" + "OL1W")

    def test_empty_search_results_are_success_not_error(self):
        # Malformed queries parse loosely and return 200-empty; the CLI must
        # report zero results without failing.
        payload = {"numFound": 0, "docs": []}
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, payload)):
            code, out, _ = run_cli("--json", "search", "--query", 'title:"unclosed')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["total"], 0)

    def test_editions_parses_entries_and_computes_next_offset(self):
        payload = {"size": 6,
                   "links": {"self": "/works/x/editions.json?limit=3",
                             "next": "/works/x/editions.json?limit=3&offset=3"},
                   "entries": [
                       {"key": "/books/" + "OL1M", "title": "Ed. One",
                        "publishers": ["Ace"], "publish_date": "1965",
                        "isbn_13": ["9780000000002"]},
                       {"key": "/books/" + "OL2M", "title": "Ed. Two",
                        "publishers": [], "publish_date": "1980", "isbn_13": []},
                       {"key": "/books/" + "OL3M", "title": "Ed. Three",
                        "publishers": ["NEL"], "publish_date": "1974",
                        "isbn_13": ["9781111111113"]},
                   ]}
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(200, payload)) as req:
            code, out, _ = run_cli("--json", "editions", "OL81699W", "--limit", "3")
        self.assertEqual(code, 0)
        self.assertEqual(req.call_args.kwargs["params"]["offset"], 0)
        data = json.loads(out)
        self.assertEqual(data["size"], 6)
        self.assertEqual(len(data["editions"]), 3)
        self.assertEqual(data["next_offset"], 3)

    def test_ratings_joins_ratings_and_bookshelves(self):
        ratings = FakeResponse(200, {"summary": {"average": 3.97, "count": 119},
                                     "counts": {"5": 56, "4": 29}})
        shelves = FakeResponse(200, {"counts": {"want_to_read": 1191,
                                                "currently_reading": 97}})
        with mock.patch.object(requests, "get", side_effect=[ratings, shelves]) as req:
            code, out, _ = run_cli("--json", "ratings", "OL45804W")
        self.assertEqual(code, 0)
        self.assertTrue(req.call_args_list[0].args[0].endswith("/ratings.json"))
        self.assertTrue(req.call_args_list[1].args[0].endswith("/bookshelves.json"))
        data = json.loads(out)
        self.assertAlmostEqual(data["average"], 3.97)
        self.assertEqual(data["bookshelves"]["want_to_read"], 1191)

    def test_404_reports_not_found_without_traceback(self):
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(404, None)):
            code, out, _ = run_cli("work", "OL999999999W")
        self.assertEqual(code, 0)
        self.assertIn("not found", out.lower())

    def test_server_error_names_status_and_dies(self):
        # run_cli captures SystemExit; a 500 must exit 1 with the status named.
        with mock.patch.object(requests, "get",
                               return_value=FakeResponse(500, text="Internal Server Error")):
            code, _, err = run_cli("work", "OL1W")
        self.assertEqual(code, 1)
        self.assertIn("500", err)

    def test_user_agent_carries_mailto_when_email_configured(self):
        original = ol_cli.ENV_EMAIL
        try:
            ol_cli.ENV_EMAIL = "reader@example.org"
            resp = FakeResponse(200, WORK_RECORD)
            with mock.patch.object(requests, "get", return_value=resp) as req:
                run_cli("work", WORK_KEY)
            ua = req.call_args.kwargs["headers"]["User-Agent"]
            self.assertIn("(mailto:reader@example.org)", ua)
        finally:
            ol_cli.ENV_EMAIL = original


# === Class 5: env-guarded live probes (keyless public API) ===
# Run only with OPENLIBRARY_LIVE_TESTS=1; skipped otherwise so the proxy-trap
# rerun proves zero egress for everything above.


@unittest.skipUnless(os.getenv("OPENLIBRARY_LIVE_TESTS") == "1",
                     "live probes disabled (set OPENLIBRARY_LIVE_TESTS=1)")
class LiveGuardedTests(unittest.TestCase):
    def test_live_isbn_resolves_through_302(self):
        code, out, _ = run_cli("--json", "isbn", "9780451524935")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertRegex(data["edition_key"], r"^OL\d+M$")
        self.assertRegex(data["work_keys"][0], r"^OL\d+W$")
        self.assertTrue(data["title"])

    def test_live_editions_listing_returns_entries(self):
        code, out, _ = run_cli("--json", "editions", "OL81699W", "--limit", "3")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertGreaterEqual(data["size"], 1)


if __name__ == "__main__":
    unittest.main()
