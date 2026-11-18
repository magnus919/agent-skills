"""Independently compare the audited fixture to the actual CLI request boundary."""

import json
import runpy
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("skill", ["ghost", "transistor", "confluence-cli"])
def test_fixture_preview_and_explicitly_confirmed_request(skill, monkeypatch, capsys):
    package = ROOT / skill
    fixture = json.loads((package / "evals/fixtures/audit-write.json").read_text())
    assert fixture["authorization"] == "pending"
    script = package / "scripts" / skill
    calls = []

    def request(method, url, **kwargs):
        calls.append((method.lower(), url, kwargs))
        response = requests.Response()
        response.status_code = 204 if skill == "ghost" else 200
        response._content = (
            b'{"results":[{"id":"42","key":"DOCS"}]}'
            if method.lower() == "get"
            else b'{"id":"123","title":"Launch notes"}'
        )
        return response

    monkeypatch.setattr(requests, "request", request)
    monkeypatch.setattr(requests, "delete", lambda url, **kwargs: request("delete", url, **kwargs))
    monkeypatch.setenv("GHOST_URL", "https://example.test")
    monkeypatch.setenv("GHOST_ADMIN_KEY", "fixture:" + "00" * 32)
    monkeypatch.setenv("TRANSISTOR_API_KEY", "fixture")
    monkeypatch.setenv("CONFLUENCE_EMAIL", "fixture@example.test")
    monkeypatch.setenv("CONFLUENCE_API_TOKEN", "fixture")
    monkeypatch.setenv("CONFLUENCE_SERVER", "https://example.test")

    def run(*flags):
        monkeypatch.setattr(sys, "argv", [str(script), "--json", *fixture["command"], *flags])
        runpy.run_path(str(script), run_name="__main__")

    with pytest.raises(SystemExit) as refusal:
        run()
    assert refusal.value.code == 1
    assert not calls
    capsys.readouterr()

    run("--dry-run")
    preview = json.loads(capsys.readouterr().out)
    assert preview["dry_run"] is True
    assert not calls

    run("--yes")
    if skill == "confluence-cli":
        assert [method for method, _, _ in calls] == ["get", "post"]
        _, _, call = calls[-1]
        assert call["json"]["title"] == preview["title"]
        assert call["json"]["parentId"] == preview["parent_id"]
        assert call["json"]["body"]["value"] == preview["body_html"]
    else:
        method, url, _ = calls[0]
        assert len(calls) == 1
        assert method == preview["method"].lower() == "delete"
        if skill == "transistor":
            assert url.endswith(preview["path"])
        else:
            assert url == preview["url"]
        assert fixture["command"][-1] in url
