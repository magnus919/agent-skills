"""Offline test suite for the bundled transistor CLI.

All HTTP is mocked at the client seam (TransistorClient._request is replaced
by a FakeTransport that records method/path/params/body and returns canned
JSON:API documents) — the suite is fully offline and passes the proxy-trap
rerun. Transistor is a keyed API, so there are deliberately NO live-call test
cases (the AGENTS.md network policy is mock-everything for keyed APIs).

Covers the four contract behavior classes: --help output, argument-error
paths, --dry-run plans, and mocked parsing of canned JSON:API compound
documents (data/attributes/relationships/included[]), plus the documented
multi-step pipelines (each stage's output fields AND JSON types feed the
next: shows -> episodes, episode-create -> episode-update(audio) ->
episode-publish, analytics -> summed downloads).
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parent / "transistor"
LOADER = importlib.machinery.SourceFileLoader("transistor_cli", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
ts = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ts  # so unittest.mock.patch("transistor_cli....") resolves
LOADER.exec_module(ts)

SHOW_ID = "132543"
EPISODE_ID = "3056098"
DRAFT_ID = "3056099"

# Canned JSON:API compound documents mirroring the documented response shapes
# (developers.transistor.fm): top-level `data`, resource objects with
# `attributes` + `relationships`, compound documents with `included[]`, and
# collection pagination under `meta` (currentPage/totalPages/totalCount).
SHOW_RESOURCE = {
    "id": SHOW_ID,
    "type": "show",
    "attributes": {
        "title": "The Caffeine Show",
        "slug": "the-caffeine-show",
        "description": "A podcast covering all things coffee and caffeine",
        "show_type": "episodic",
        "private": False,
        "feed_url": "https://feeds.transistor.fm/the-caffeine-show",
        "time_zone": "UTC",
        "author": "Jimmy Podcaster",
        "website": "https://example.com/caffeine",
    },
    "relationships": {"episodes": {"data": []}},
}

USER_DOC = {
    "data": {
        "id": "173455",
        "type": "user",
        "attributes": {"name": "Jimmy Podcaster", "time_zone": "UTC", "image_url": None},
    }
}

SHOWS_DOC = {"data": [SHOW_RESOURCE], "meta": {"currentPage": 0, "totalPages": 1, "totalCount": 1}}
SHOW_DOC = {"data": SHOW_RESOURCE}

EPISODE_RESOURCE = {
    "id": EPISODE_ID,
    "type": "episode",
    "attributes": {
        "title": "How To Roast Coffee",
        "number": 1,
        "season": 1,
        "status": "published",
        "published_at": "2020-07-01 00:00:00 UTC",
        "duration": 568,
        "duration_in_mmss": "09:28",
        "media_url": "https://media.transistor.fm/ba1d5241/c1ae0a3a.mp3",
        "share_url": "https://share.transistor.fm/s/ba1d5241",
        "audio_processing": False,
        "processing_failure": None,
    },
    "relationships": {"show": {"data": {"id": SHOW_ID, "type": "show"}}},
}

DRAFT_RESOURCE = dict(
    EPISODE_RESOURCE,
    id=DRAFT_ID,
    attributes=dict(
        EPISODE_RESOURCE["attributes"],
        title="Unfinished Episode",
        number=2,
        status="draft",
        published_at=None,
        media_url="",
    ),
)

# Compound document: episode collection with the parent show in included[].
EPISODES_DOC = {
    "data": [EPISODE_RESOURCE, DRAFT_RESOURCE],
    "included": [SHOW_RESOURCE],
    "meta": {"currentPage": 1, "totalPages": 3, "totalCount": 25},
}
EPISODE_DOC = {"data": EPISODE_RESOURCE}
DRAFT_DOC = {"data": DRAFT_RESOURCE}
NO_AUDIO_DOC = {
    "data": dict(EPISODE_RESOURCE, attributes=dict(EPISODE_RESOURCE["attributes"], media_url=""))
}

CREATED_DRAFT_RESOURCE = dict(
    DRAFT_RESOURCE,
    id="3056100",
    attributes=dict(DRAFT_RESOURCE["attributes"], title="Fresh Draft", number=None, season=2),
)
CREATE_DOC = {"data": CREATED_DRAFT_RESOURCE}

PUBLISH_DOC = {
    "data": {
        "id": EPISODE_ID,
        "type": "episode",
        "attributes": {
            "status": "published",
            "published_at": "2026-08-29 12:00:00 UTC",
            "media_url": EPISODE_RESOURCE["attributes"]["media_url"],
        },
        "relationships": {},
    }
}

SHOW_ANALYTICS_DOC = {
    "data": {
        "id": "the-caffeine-show",
        "type": "show_analytics",
        "attributes": {
            "downloads": [
                {"date": "15-08-2026", "downloads": 4},
                {"date": "16-08-2026", "downloads": 6},
            ],
            "start_date": "08-15-2026",
            "end_date": "08-16-2026",
        },
        "relationships": {"show": {"data": {"id": SHOW_ID, "type": "show"}}},
    },
    "included": [dict(SHOW_RESOURCE, attributes={"title": "The Caffeine Show"})],
}

EPISODE_ANALYTICS_DOC = {
    "data": dict(
        SHOW_ANALYTICS_DOC["data"],
        id=EPISODE_ID,
        type="episode_analytics",
        relationships={"episode": {"data": {"id": EPISODE_ID, "type": "episode"}}},
    )
}

AUDIO_UPLOAD_DOC = {
    "data": {
        "id": "upload-1",
        "type": "audio_upload",
        "attributes": {
            "upload_url": "https://storage.example.com/uploads/episode1.mp3?sig=stub",
            "content_type": "audio/mpeg",
            "expires_in": 600,
            "audio_url": "https://uploads.example.com/episode1.mp3",
        },
    }
}

SUBSCRIBER_RESOURCE = {
    "id": "709423",
    "type": "subscriber",
    "attributes": {
        "email": "arthur@example.com",
        "status": "default",
        "feed_url": "https://subscribers.example.com/a52a98c03f28eb",
        "subscribe_url": "https://subscribe.example.com/a52a98c03f28eb",
        "has_downloads": False,
    },
    "relationships": {"show": {"data": {"id": SHOW_ID, "type": "show"}}},
}
SUBSCRIBERS_DOC = {
    "data": [SUBSCRIBER_RESOURCE],
    "meta": {"currentPage": 0, "totalPages": 1, "totalCount": 1},
}
SUBSCRIBER_BATCH_DOC = {
    "data": [
        SUBSCRIBER_RESOURCE,
        dict(
            SUBSCRIBER_RESOURCE,
            id="709424",
            attributes=dict(SUBSCRIBER_RESOURCE["attributes"], email="beatrice@example.com"),
        ),
    ]
}

WEBHOOK_RESOURCE = {
    "id": "104325",
    "type": "webhook",
    "attributes": {"event_name": "episode_published", "url": "https://example.com/hook"},
    "relationships": {"show": {"data": {"id": SHOW_ID, "type": "show"}}},
}
WEBHOOKS_DOC = {"data": [WEBHOOK_RESOURCE]}


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, text=""):
        self.status_code = status_code
        self._json = json_body
        self.text = text if text else (json.dumps(json_body) if json_body is not None else "")

    def json(self):
        if self._json is None:
            raise ValueError("no json body")
        return self._json


class FakeTransport:
    """Stands in for TransistorClient._request: records every call and serves
    canned JSON:API documents by (method, path)."""

    def __init__(self, routes=None):
        self.routes = routes or {}
        self.calls = []

    def __call__(self, method, path, params=None, body=None):
        self.calls.append({"method": method, "path": path, "params": params, "body": body})
        for (m, p), doc in self.routes.items():
            if m == method and path == p:
                return doc
        for (m, p), doc in self.routes.items():
            if m == method and path.startswith(p):
                return doc
        raise AssertionError(f"unexpected request: {method} {path} {params} {body}")


def make_client(routes=None):
    client = ts.TransistorClient(key="test-key", dry_run=False)
    client._request = FakeTransport(routes)
    return client


def run_handler(client, handler, *argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        handler(client, list(argv))
    return out.getvalue()


def run_cli(*args):
    env = os.environ.copy()
    env.pop("TRANSISTOR_API_KEY", None)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
    )


class ModuleStateTestCase(unittest.TestCase):
    """Base that restores module globals mutated by in-process tests."""

    def setUp(self):
        self._flags = dict(ts.GLOBAL_FLAGS)
        self._quiet = ts.QUIET
        ts.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}

    def tearDown(self):
        ts.GLOBAL_FLAGS = self._flags
        ts.QUIET = self._quiet


class HelpOutputTests(unittest.TestCase):
    """Class 1: --help output."""

    def test_help_lists_every_subcommand(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for noun in (
            "user",
            "shows",
            "show-update",
            "episodes",
            "episode-create",
            "episode-update",
            "episode-publish",
            "authorize-upload",
            "analytics",
            "episode-analytics",
            "subscribers",
            "subscriber-create",
            "subscriber-batch",
            "subscriber-delete",
            "webhooks",
            "webhook-create",
            "webhook-delete",
        ):
            self.assertIn(noun, result.stdout)

    def test_help_names_the_env_var_and_docs_url(self):
        result = run_cli("--help")
        self.assertIn("TRANSISTOR_API_KEY", result.stdout)
        self.assertIn("dashboard.transistor.fm/account", result.stdout)
        self.assertIn("developers.transistor.fm", result.stdout)

    def test_leaf_help_carries_examples_and_flags(self):
        for leaf in ("episodes", "episode-publish", "authorize-upload", "analytics"):
            result = run_cli(leaf, "--help")
            with self.subTest(leaf=leaf):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--", result.stdout)

    def test_no_command_prints_help_and_exits_one(self):
        result = run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("usage", result.stdout)


class ArgumentErrorTests(unittest.TestCase):
    """Class 2: argument-error paths fail cleanly before any network call."""

    def assertCleanError(self, result, needle):
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(needle, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_episode_requires_id(self):
        self.assertCleanError(run_cli("episode"), "--id")

    def test_episode_create_requires_show_and_title(self):
        self.assertCleanError(run_cli("episode-create", "--show", SHOW_ID), "--title")

    def test_analytics_requires_show(self):
        self.assertCleanError(run_cli("analytics"), "--show")

    def test_analytics_dates_require_each_other(self):
        self.assertCleanError(
            run_cli("analytics", "--show", SHOW_ID, "--start-date", "01-09-2026"),
            "end_date must be used together",
        )

    def test_analytics_dates_reject_wrong_format(self):
        self.assertCleanError(
            run_cli(
                "analytics",
                "--show",
                SHOW_ID,
                "--start-date",
                "2026-09-01",
                "--end-date",
                "2026-09-07",
            ),
            "dd-mm-yyyy",
        )

    def test_episode_update_with_no_fields_dies(self):
        self.assertCleanError(run_cli("episode-update", "--id", EPISODE_ID), "Nothing to update")

    def test_subscriber_delete_requires_arguments(self):
        self.assertCleanError(run_cli("subscriber-delete"), "--id")

    def test_missing_api_key_dies_before_network(self):
        result = run_cli("shows")
        self.assertCleanError(result, "TRANSISTOR_API_KEY")


class DryRunPlanTests(ModuleStateTestCase):
    """Class 3: --dry-run emits valid JSON plans with zero network activity."""

    def run_json(self, handler, client, *argv):
        out = run_handler(client, handler, *argv)
        return json.loads(out)

    def test_plan_shape_covers_method_path_params_body(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(ts.cmd_user, client)
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["method"], "GET")
        self.assertEqual(plan["path"], "")

    def test_episodes_plan_carries_documented_params(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(
            ts.cmd_episodes, client, "--show", SHOW_ID, "--status", "draft", "--per", "5"
        )
        self.assertEqual(plan["method"], "GET")
        self.assertEqual(plan["path"], "/episodes")
        self.assertEqual(plan["params"]["show_id"], SHOW_ID)
        self.assertEqual(plan["params"]["status"], "draft")
        self.assertEqual(plan["params"]["pagination[per]"], 5)
        # pagination[page] only appears when requested (API default is page 0,
        # but the CLI does not send params the user did not ask for).
        self.assertNotIn("pagination[page]", plan["params"])

    def test_limit_alias_feeds_per_param(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(ts.cmd_episodes, client, "--limit", "7")
        self.assertEqual(plan["params"]["pagination[per]"], 7)

    def test_create_plan_sends_bracket_keys(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(
            ts.cmd_episode_create, client, "--show", SHOW_ID, "--title", "Fresh Draft"
        )
        self.assertEqual(plan["method"], "POST")
        self.assertEqual(plan["path"], "/episodes")
        self.assertEqual(plan["body"]["episode[show_id]"], SHOW_ID)
        self.assertEqual(plan["body"]["episode[title]"], "Fresh Draft")

    def test_publish_plan_is_the_dedicated_publish_endpoint(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(ts.cmd_episode_publish, client, "--id", EPISODE_ID)
        self.assertEqual(plan["method"], "PATCH")
        self.assertEqual(plan["path"], f"/episodes/{EPISODE_ID}/publish")
        self.assertEqual(plan["body"], {"episode[status]": "published"})

    def test_schedule_plan_carries_published_at(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(
            ts.cmd_episode_publish,
            client,
            "--id",
            EPISODE_ID,
            "--status",
            "scheduled",
            "--published-at",
            "2026-09-03 09:00:00",
        )
        self.assertEqual(plan["body"]["episode[status]"], "scheduled")
        self.assertEqual(plan["body"]["episode[published_at]"], "2026-09-03 09:00:00")

    def test_update_plan_attaches_audio_without_publishing(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(
            ts.cmd_episode_update,
            client,
            "--id",
            EPISODE_ID,
            "--audio-url",
            "https://uploads.example.com/episode1.mp3",
        )
        self.assertEqual(plan["method"], "PATCH")
        self.assertEqual(plan["path"], f"/episodes/{EPISODE_ID}")
        self.assertEqual(
            plan["body"], {"episode[audio_url]": "https://uploads.example.com/episode1.mp3"}
        )

    def test_authorize_upload_plan_does_not_leak_urls(self):
        client = ts.TransistorClient(dry_run=True)
        out = run_handler(client, ts.cmd_authorize_upload, "--filename", "Episode1.mp3")
        plan = json.loads(out)
        self.assertEqual(plan["method"], "GET")
        self.assertEqual(plan["params"], {"filename": "Episode1.mp3"})
        self.assertIn("then_put", plan)
        self.assertIn("HTTP PUT", plan["then_put"]["how"])

    def test_batch_plan_sends_email_array(self):
        client = ts.TransistorClient(dry_run=True)
        plan = self.run_json(
            ts.cmd_subscriber_batch,
            client,
            "--show",
            SHOW_ID,
            "--email",
            "one@example.com",
            "--email",
            "two@example.com",
        )
        self.assertEqual(plan["path"], "/subscribers/batch")
        self.assertEqual(plan["body"]["emails[]"], ["one@example.com", "two@example.com"])
        self.assertEqual(plan["body"]["show_id"], SHOW_ID)

    def test_cli_json_dry_run_subprocess_is_valid_json(self):
        result = run_cli(
            "--json", "--dry-run", "episodes", "--show", SHOW_ID, "--status", "published"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["path"], "/episodes")
        self.assertEqual(plan["params"]["status"], "published")


class JSONAPIDocumentTests(ModuleStateTestCase):
    """Class 4: mocked parsing of canned JSON:API compound documents."""

    def test_user_parses_data_attributes(self):
        client = make_client({("GET", ""): USER_DOC})
        out = run_handler(client, ts.cmd_user)
        payload = json.loads(out)
        self.assertEqual(payload["id"], "173455")
        self.assertEqual(payload["name"], "Jimmy Podcaster")
        self.assertEqual(payload["time_zone"], "UTC")

    def test_shows_parses_collection_and_meta(self):
        client = make_client({("GET", "/shows"): SHOWS_DOC})
        payload = json.loads(run_handler(client, ts.cmd_shows))
        self.assertEqual(payload["meta"]["totalPages"], 1)
        show = payload["shows"][0]
        self.assertEqual(show["id"], SHOW_ID)
        self.assertEqual(show["title"], "The Caffeine Show")
        self.assertEqual(show["feed_url"], "https://feeds.transistor.fm/the-caffeine-show")

    def test_episodes_compound_document_includes_show(self):
        client = make_client({("GET", "/episodes"): EPISODES_DOC})
        payload = json.loads(run_handler(client, ts.cmd_episodes, "--include", "show"))
        self.assertEqual(payload["meta"]["totalCount"], 25)
        first = payload["episodes"][0]
        self.assertIsInstance(first["id"], str)
        self.assertEqual(first["title"], "How To Roast Coffee")
        self.assertEqual(first["status"], "published")
        self.assertIsInstance(first["season"], int)
        self.assertIsInstance(first["duration"], int)
        self.assertEqual(first["show_id"], SHOW_ID)
        draft = payload["episodes"][1]
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["published_at"], "")
        # Human mode also prints the included[] show summary via log().
        ts.GLOBAL_FLAGS = {"json": False, "dry_run": False, "quiet": False, "verbose": False}
        human = run_handler(client, ts.cmd_episodes, "--include", "show")
        ts.GLOBAL_FLAGS = {"json": True, "dry_run": False, "quiet": False, "verbose": False}
        self.assertIn("included show: The Caffeine Show", human)

    def test_episode_relationships_expose_show_id(self):
        client = make_client({("GET", f"/episodes/{EPISODE_ID}"): EPISODE_DOC})
        payload = json.loads(
            run_handler(client, ts.cmd_episode, "--id", EPISODE_ID, "--include", "show")
        )
        self.assertEqual(payload["show_id"], SHOW_ID)
        self.assertEqual(payload["media_url"], EPISODE_RESOURCE["attributes"]["media_url"])

    def test_analytics_sums_downloads_array(self):
        client = make_client({("GET", f"/analytics/{SHOW_ID}"): SHOW_ANALYTICS_DOC})
        payload = json.loads(run_handler(client, ts.cmd_analytics, "--show", SHOW_ID))
        self.assertEqual(payload["downloads_total"], 10)
        self.assertEqual(payload["days"], 2)
        self.assertIsInstance(payload["downloads"], list)
        row = payload["downloads"][0]
        self.assertIsInstance(row["downloads"], int)

    def test_subscribers_list_parses_envelope(self):
        client = make_client({("GET", "/subscribers"): SUBSCRIBERS_DOC})
        payload = json.loads(run_handler(client, ts.cmd_subscribers, "--show", SHOW_ID))
        sub = payload["subscribers"][0]
        self.assertEqual(sub["email"], "arthur@example.com")
        self.assertEqual(sub["subscribe_url"], SUBSCRIBER_RESOURCE["attributes"]["subscribe_url"])

    def test_webhooks_list_parses_event_names(self):
        client = make_client({("GET", "/webhooks"): WEBHOOKS_DOC})
        payload = json.loads(run_handler(client, ts.cmd_webhooks, "--show", SHOW_ID))
        self.assertEqual(payload["webhooks"][0]["event_name"], "episode_published")


class WritePathTests(ModuleStateTestCase):
    """Mocked write commands must send the documented bracket-key bodies and
    the dedicated publish endpoint."""

    def test_episode_create_posts_show_id_and_title(self):
        client = make_client({("POST", "/episodes"): CREATE_DOC})
        payload = json.loads(
            run_handler(
                client,
                ts.cmd_episode_create,
                "--show",
                SHOW_ID,
                "--title",
                "Fresh Draft",
                "--season",
                "2",
                "--audio-url",
                "https://uploads.example.com/x.mp3",
            )
        )
        call = client._request.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(call["body"]["episode[show_id]"], SHOW_ID)
        self.assertEqual(call["body"]["episode[title]"], "Fresh Draft")
        self.assertEqual(call["body"]["episode[season]"], 2)
        self.assertEqual(call["body"]["episode[audio_url]"], "https://uploads.example.com/x.mp3")
        self.assertEqual(payload["status"], "draft")

    def test_created_draft_points_at_publish_recipe(self):
        client = make_client({("POST", "/episodes"): CREATE_DOC})
        ts.GLOBAL_FLAGS = {"json": False, "dry_run": False, "quiet": False, "verbose": False}
        out = run_handler(
            client, ts.cmd_episode_create, "--show", SHOW_ID, "--title", "Fresh Draft"
        )
        self.assertIn(f"episode-publish --id {CREATED_DRAFT_RESOURCE['id']}", out)

    def test_publish_sends_status_to_publish_endpoint(self):
        client = make_client(
            {
                ("GET", f"/episodes/{EPISODE_ID}"): EPISODE_DOC,
                ("PATCH", f"/episodes/{EPISODE_ID}/publish"): PUBLISH_DOC,
            }
        )
        payload = json.loads(run_handler(client, ts.cmd_episode_publish, "--id", EPISODE_ID))
        call = client._request.calls[-1]
        self.assertEqual(call["method"], "PATCH")
        self.assertEqual(call["path"], f"/episodes/{EPISODE_ID}/publish")
        self.assertEqual(call["body"], {"episode[status]": "published"})
        self.assertEqual(payload["status"], "published")

    def test_unpublish_sends_draft_status(self):
        client = make_client(
            {
                ("GET", f"/episodes/{EPISODE_ID}"): EPISODE_DOC,
                ("PATCH", f"/episodes/{EPISODE_ID}/publish"): PUBLISH_DOC,
            }
        )
        run_handler(client, ts.cmd_episode_publish, "--id", EPISODE_ID, "--status", "draft")
        self.assertEqual(client._request.calls[-1]["body"], {"episode[status]": "draft"})

    def test_show_update_sends_show_bracket_keys(self):
        client = make_client({("PATCH", f"/shows/{SHOW_ID}"): SHOW_DOC})
        run_handler(
            client,
            ts.cmd_show_update,
            "--id",
            SHOW_ID,
            "--title",
            "New Title",
            "--author",
            "New Author",
        )
        call = client._request.calls[0]
        self.assertEqual(call["method"], "PATCH")
        self.assertEqual(call["body"], {"show[title]": "New Title", "show[author]": "New Author"})


class PipelineChainTests(ModuleStateTestCase):
    """Documented multi-step recipes must execute stage by stage, each stage's
    output field names AND JSON types consumable by the next."""

    def test_shows_then_filtered_episodes_pipeline(self):
        client = make_client({("GET", "/shows"): SHOWS_DOC, ("GET", "/episodes"): EPISODES_DOC})
        first = json.loads(run_handler(client, ts.cmd_shows))
        consumed_show_id = first["shows"][0]["id"]
        self.assertIsInstance(consumed_show_id, str)
        second = json.loads(run_handler(client, ts.cmd_episodes, "--show", consumed_show_id))
        self.assertEqual(client._request.calls[1]["params"]["show_id"], consumed_show_id)
        self.assertEqual(second["episodes"][0]["show_id"], consumed_show_id)

    def test_analytics_date_pair_pipeline(self):
        client = make_client({("GET", f"/analytics/{SHOW_ID}"): SHOW_ANALYTICS_DOC})
        payload = json.loads(
            run_handler(
                client,
                ts.cmd_analytics,
                "--show",
                SHOW_ID,
                "--start-date",
                "15-08-2026",
                "--end-date",
                "16-08-2026",
            )
        )
        call = client._request.calls[0]
        self.assertEqual(call["params"], {"start_date": "15-08-2026", "end_date": "16-08-2026"})
        self.assertEqual(payload["downloads_total"], 10)

    def test_create_then_attach_audio_then_publish_pipeline(self):
        client = make_client(
            {
                ("POST", "/episodes"): CREATE_DOC,
                ("PATCH", f"/episodes/{CREATED_DRAFT_RESOURCE['id']}"): {
                    "data": CREATED_DRAFT_RESOURCE
                },
                ("GET", f"/episodes/{CREATED_DRAFT_RESOURCE['id']}"): {
                    "data": dict(
                        CREATED_DRAFT_RESOURCE,
                        attributes=dict(
                            CREATED_DRAFT_RESOURCE["attributes"],
                            media_url="https://uploads.example.com/final.mp3",
                        ),
                    )
                },
                ("PATCH", f"/episodes/{CREATED_DRAFT_RESOURCE['id']}/publish"): {
                    "data": dict(
                        CREATED_DRAFT_RESOURCE,
                        attributes=dict(
                            CREATED_DRAFT_RESOURCE["attributes"],
                            status="published",
                            published_at="2026-08-29 12:00:00 UTC",
                        ),
                    )
                },
            }
        )
        # Stage 1: create -> returns the draft id (str) consumed downstream.
        created = json.loads(
            run_handler(client, ts.cmd_episode_create, "--show", SHOW_ID, "--title", "Fresh Draft")
        )
        self.assertEqual(created["status"], "draft")
        self.assertIsInstance(created["id"], str)
        draft_id = created["id"]
        # Stage 2: attach audio via the metadata PATCH (id + audio_url feed in).
        run_handler(
            client,
            ts.cmd_episode_update,
            "--id",
            draft_id,
            "--audio-url",
            "https://uploads.example.com/final.mp3",
        )
        attach_call = client._request.calls[1]
        self.assertEqual(attach_call["path"], f"/episodes/{draft_id}")
        self.assertEqual(
            attach_call["body"], {"episode[audio_url]": "https://uploads.example.com/final.mp3"}
        )
        # Stage 3: publish on the dedicated endpoint reuses the same id (str).
        published = json.loads(run_handler(client, ts.cmd_episode_publish, "--id", draft_id))
        publish_call = client._request.calls[-1]
        self.assertEqual(publish_call["path"], f"/episodes/{draft_id}/publish")
        self.assertEqual(publish_call["body"], {"episode[status]": "published"})
        self.assertEqual(published["status"], "published")
        self.assertIsInstance(published["published_at"], str)

    def test_episodes_then_episode_analytics_pipeline(self):
        client = make_client(
            {
                ("GET", "/episodes"): EPISODES_DOC,
                ("GET", f"/analytics/episodes/{EPISODE_ID}"): EPISODE_ANALYTICS_DOC,
            }
        )
        listing = json.loads(
            run_handler(client, ts.cmd_episodes, "--show", SHOW_ID, "--status", "published")
        )
        consumed_episode_id = listing["episodes"][0]["id"]
        self.assertIsInstance(consumed_episode_id, str)
        stats = json.loads(
            run_handler(client, ts.cmd_episode_analytics, "--id", consumed_episode_id)
        )
        self.assertEqual(
            client._request.calls[1]["path"], f"/analytics/episodes/{consumed_episode_id}"
        )
        self.assertEqual(stats["episode_id"], consumed_episode_id)
        self.assertEqual(stats["downloads_total"], 10)

    def test_authorize_upload_then_attach_then_publish(self):
        client = make_client(
            {
                ("GET", "/episodes/authorize_upload"): AUDIO_UPLOAD_DOC,
            }
        )
        with (
            patch("transistor_cli.requests.request") as req_mock,
            patch("transistor_cli.requests.put") as put_mock,
            tempfile.TemporaryDirectory(prefix="ts-upload-") as tmpdir,
        ):
            fake_audio = pathlib.Path(tmpdir) / "episode1.mp3"
            fake_audio.write_bytes(b"ID3")
            req_mock.return_value = FakeResponse(200, AUDIO_UPLOAD_DOC)
            put_mock.return_value = FakeResponse(200, {})
            authorized = json.loads(
                run_handler(
                    client,
                    ts.cmd_authorize_upload,
                    "--filename",
                    "Episode1.mp3",
                    "--file",
                    str(fake_audio),
                )
            )
        self.assertEqual(authorized["content_type"], "audio/mpeg")
        self.assertIsInstance(authorized["expires_in"], int)
        audio_url = authorized["audio_url"]
        self.assertIsInstance(audio_url, str)
        # The documented flow: attach audio via episode[audio_url], then publish.
        client2 = make_client(
            {
                ("PATCH", f"/episodes/{EPISODE_ID}"): EPISODE_DOC,
                ("GET", f"/episodes/{EPISODE_ID}"): EPISODE_DOC,
                ("PATCH", f"/episodes/{EPISODE_ID}/publish"): PUBLISH_DOC,
            }
        )
        json.loads(
            run_handler(
                client2, ts.cmd_episode_update, "--id", EPISODE_ID, "--audio-url", audio_url
            )
        )
        self.assertEqual(client2._request.calls[0]["body"], {"episode[audio_url]": audio_url})
        json.loads(run_handler(client2, ts.cmd_episode_publish, "--id", EPISODE_ID))
        self.assertEqual(client2._request.calls[-1]["path"], f"/episodes/{EPISODE_ID}/publish")


class PublishGuardTests(ModuleStateTestCase):
    """The publish guard: refuse to publish episodes with no audio attached
    (unless --force), since publishing pushes an unplayable item to feeds."""

    def test_publish_without_audio_dies_with_recipe(self):
        client = make_client({("GET", f"/episodes/{EPISODE_ID}"): NO_AUDIO_DOC})
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
            run_handler(client, ts.cmd_episode_publish, "--id", EPISODE_ID)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("no audio yet", stderr.getvalue())
        self.assertIn("episode-update", stderr.getvalue())

    def test_force_publishes_without_audio(self):
        client = make_client(
            {
                ("GET", f"/episodes/{EPISODE_ID}"): NO_AUDIO_DOC,
                ("PATCH", f"/episodes/{EPISODE_ID}/publish"): PUBLISH_DOC,
            }
        )
        payload = json.loads(
            run_handler(client, ts.cmd_episode_publish, "--id", EPISODE_ID, "--force")
        )
        self.assertEqual(payload["status"], "published")

    def test_publish_with_audio_skips_guard(self):
        client = make_client(
            {
                ("GET", f"/episodes/{EPISODE_ID}"): EPISODE_DOC,
                ("PATCH", f"/episodes/{EPISODE_ID}/publish"): PUBLISH_DOC,
            }
        )
        payload = json.loads(run_handler(client, ts.cmd_episode_publish, "--id", EPISODE_ID))
        self.assertEqual(payload["status"], "published")


class ErrorSignatureTests(unittest.TestCase):
    """HTTP error signatures: 401/403/404/429 and JSON:API errors[] bodies."""

    def run_status(self, status_code, body=None):
        client = ts.TransistorClient(key="test-key", dry_run=False)
        stderr = io.StringIO()
        with patch("transistor_cli.requests.request") as req_mock:
            req_mock.return_value = FakeResponse(status_code, body)
            with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
                client.list_shows()
        return ctx.exception.code, stderr.getvalue()

    def test_401_names_the_env_var(self):
        code, err = self.run_status(401, {"message": "Unauthorized"})
        self.assertEqual(code, 1)
        self.assertIn("401", err)
        self.assertIn("TRANSISTOR_API_KEY", err)

    def test_403_explains_role_access(self):
        _, err = self.run_status(403, {"message": "Forbidden"})
        self.assertIn("403", err)
        self.assertIn("role", err)

    def test_404_suggests_id_or_slug(self):
        _, err = self.run_status(404, {"message": "Not Found"})
        self.assertIn("404", err)
        self.assertIn("slug", err)

    def test_429_states_the_rate_limit_window(self):
        _, err = self.run_status(429, {"message": "Too Many Requests"})
        self.assertIn("429", err)
        self.assertIn("10 requests per 10 seconds", err)

    def test_errors_envelope_is_flattened(self):
        body = {
            "errors": [{"title": "Unprocessable Entity", "detail": "Status can't be published"}]
        }
        _, err = self.run_status(422, body)
        self.assertIn("422", err)
        self.assertIn("Unprocessable Entity", err)
        self.assertIn("Status can't be published", err)


class ScriptConventionsTests(unittest.TestCase):
    """SCRIPT-GATES-adjacent invariants: imports whitelist, no tech-debt
    markers, executable bit, stdlib+requests only."""

    def test_executable_bit(self):
        mode = stat.S_IMODE(os.stat(SCRIPT).st_mode)
        self.assertTrue(mode & stat.S_IXUSR, "scripts/transistor must stay executable")

    def test_imports_are_stdlib_plus_requests(self):
        text = SCRIPT.read_text()
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                module = stripped.split()[1].split(".")[0].rstrip(",")
                self.assertIn(
                    module,
                    {
                        "argparse",
                        "json",
                        "os",
                        "re",
                        "sys",
                        "warnings",
                        "typing",
                        "requests",
                    },
                    f"unexpected import: {stripped}",
                )

    def test_no_tech_debt_markers(self):
        for i, line in enumerate(SCRIPT.read_text().splitlines(), start=1):
            if "#" in line:
                comment = line.split("#", 1)[1]
                for marker in ("TODO", "FIXME", "HACK", "XXX"):
                    self.assertNotIn(marker, comment, f"line {i}: {marker} marker")


if __name__ == "__main__":
    unittest.main()
