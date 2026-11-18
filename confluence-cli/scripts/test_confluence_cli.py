"""Exercise the CLI entry point with an in-memory transport."""

import json
import runpy
import sys
from pathlib import Path

import pytest
import requests

SCRIPT = Path(__file__).with_name("confluence-cli")
CREATE = (
    "create", "--space", "DOCS", "--title", "Example", "--parent", "17",
    "--body", "<p>Fixture page</p>",
)


def run_cli(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), *args])
    runpy.run_path(str(SCRIPT), run_name="__main__")


def test_unconfirmed_create_refuses_before_requests(monkeypatch, capsys):
    monkeypatch.setenv("CONFLUENCE_EMAIL", "audit@example.test")
    monkeypatch.setenv("CONFLUENCE_API_TOKEN", "dummy")
    monkeypatch.setattr(requests, "request", lambda *a, **kw: pytest.fail("unexpected request"))
    with pytest.raises(SystemExit) as result:
        run_cli(monkeypatch, *CREATE)
    assert result.value.code == 1
    assert "--yes" in capsys.readouterr().err


def test_dry_run_includes_the_html_and_parent_without_credentials(monkeypatch, capsys):
    monkeypatch.delenv("CONFLUENCE_EMAIL", raising=False)
    monkeypatch.delenv("CONFLUENCE_API_TOKEN", raising=False)
    monkeypatch.setattr(requests, "request", lambda *a, **kw: pytest.fail("unexpected request"))
    run_cli(monkeypatch, *CREATE, "--dry-run", "--json")
    plan = json.loads(capsys.readouterr().out)
    assert plan["space"] == "DOCS"
    assert plan["title"] == "Example"
    assert plan["parent_id"] == "17"
    assert plan["body_html"] == "<p>Fixture page</p>"


def test_confirmed_create_resolves_space_then_posts(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_EMAIL", "audit@example.test")
    monkeypatch.setenv("CONFLUENCE_API_TOKEN", "dummy")
    monkeypatch.setenv("CONFLUENCE_SERVER", "https://example.test")
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        response = requests.Response()
        response.status_code = 200 if method == "GET" else 201
        response._content = (
            b'{"results":[{"id":"5","key":"DOCS"}]}'
            if method == "GET" else b'{"id":"26","title":"Example"}'
        )
        return response

    monkeypatch.setattr(requests, "request", request)
    run_cli(monkeypatch, "--yes", *CREATE)
    assert [call[0] for call in calls] == ["GET", "POST"]
    assert calls[-1][1].endswith("/wiki/api/v2/pages")
    assert calls[-1][2]["json"] == {
        "spaceId": "5",
        "title": "Example",
        "parentId": "17",
        "body": {"representation": "storage", "value": "<p>Fixture page</p>"},
    }
