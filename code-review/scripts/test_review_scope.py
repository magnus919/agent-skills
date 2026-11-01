"""Tests for review_scope.py against real temporary git repositories."""

from __future__ import annotations

import importlib.util
import sys
import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("review_scope.py")
spec = importlib.util.spec_from_file_location("review_scope", SCRIPT)
review_scope = importlib.util.module_from_spec(spec)
sys.modules['review_scope'] = review_scope
spec.loader.exec_module(review_scope)

GIT_ENV = {
    "GIT_AUTHOR_NAME": "Test Reviewer",
    "GIT_AUTHOR_EMAIL": "reviewer@example.test",
    "GIT_COMMITTER_NAME": "Test Reviewer",
    "GIT_COMMITTER_EMAIL": "reviewer@example.test",
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00",
}


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        env={**GIT_ENV, "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
    )
    return result.stdout


def write(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "--initial-branch=main")
    write(root, "README.md", "# fixture\n")
    write(root, "app/service.py", "def serve():\n    return 'ok'\n")
    write(root, "app/tests/test_service.py", "def test_serve():\n    assert True\n")
    git(root, "add", "-A")
    git(root, "commit", "-m", "base")
    return root


def commit(repo: Path, message: str = "change") -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


def scope_for(repo: Path, base: str = "HEAD~1", head: str = "HEAD", **kwargs) -> dict:
    resolved_base, resolved_head = review_scope.resolve_range(repo, base, head, False)
    return review_scope.build_scope(repo, resolved_base, resolved_head, False, kwargs.get("tier"))


def test_small_change_gets_small_tier(repo: Path) -> None:
    write(repo, "app/service.py", "def serve():\n    return 'ok'\n\ndef health():\n    return 'ok'\n")
    commit(repo)
    scope = scope_for(repo)
    assert scope["tier"] == "small"
    assert scope["totals"]["files"] == 1
    assert scope["budget"]["estimated_minutes"] == 5


def test_auth_paths_are_flagged_and_reviewed_first(repo: Path) -> None:
    write(repo, "app/auth/session.py", "TOKEN_TTL = 60\n")
    write(repo, "app/service.py", "def serve():\n    return 'ok'\n\n\ndef extra():\n    return 1\n")
    commit(repo)
    scope = scope_for(repo)
    assert "authentication" in scope["risks"]
    assert scope["risks"]["authentication"] == ["app/auth/session.py"]
    assert scope["attention_order"][0] == "app/auth/session.py"
    assert "app/service.py" in scope["attention_order"]


def test_generated_and_lockfiles_do_not_inflate_effective_lines(repo: Path) -> None:
    write(repo, "package-lock.json", "".join(f'{{"n": {i}}}\n' for i in range(300)))
    write(repo, "app/service.py", "def serve():\n    return 'ok'\n")
    commit(repo)
    scope = scope_for(repo)
    assert scope["totals"]["generated_lines"] > 0
    assert scope["totals"]["effective_lines"] < scope["totals"]["generated_lines"] + 10
    assert scope["tier"] == "small"


def test_source_file_is_mapped_to_conventional_test(repo: Path) -> None:
    write(repo, "app/service.py", "def serve():\n    return 'changed'\n")
    commit(repo)
    scope = scope_for(repo)
    entry = next(item for item in scope["files"] if item["path"] == "app/service.py")
    assert entry["tests"] == ["app/tests/test_service.py"]
    assert scope["tests"]["source_files_without_matched_tests"] == []


def test_untested_source_is_reported_as_a_question(repo: Path) -> None:
    write(repo, "app/reporting.py", "def report():\n    return []\n")
    commit(repo)
    scope = scope_for(repo)
    assert "app/reporting.py" in scope["tests"]["source_files_without_matched_tests"]


def test_oversized_change_is_routed_to_split_sessions(repo: Path) -> None:
    body = "".join(f"def f{i}():\n    return {i}\n\n" for i in range(400))
    write(repo, "app/big.py", body)
    commit(repo)
    scope = scope_for(repo)
    assert scope["tier"] == "oversized"
    assert scope["budget"]["sessions"] > 1
    assert scope["budget"]["capped_minutes"] == review_scope.MAX_SESSION_MINUTES


def test_output_is_deterministic(repo: Path) -> None:
    write(repo, "app/service.py", "def serve():\n    return 'changed'\n")
    commit(repo)
    first = json.dumps(scope_for(repo), sort_keys=True)
    second = json.dumps(scope_for(repo), sort_keys=True)
    assert first == second


def test_staged_diff_is_reviewable_before_commit(repo: Path) -> None:
    write(repo, "app/service.py", "def serve():\n    return 'staged'\n")
    git(repo, "add", "-A")
    base, head = review_scope.resolve_range(repo, None, None, True)
    scope = review_scope.build_scope(repo, base, head, True, None)
    assert scope["range"]["head"] == "index"
    assert scope["totals"]["files"] == 1


def test_cli_emits_json_and_markdown(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(repo, "app/service.py", "def serve():\n    return 'changed'\n")
    commit(repo)
    assert review_scope.main(["--repo", str(repo), "--base", "HEAD~1", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tier"] in {"small", "standard", "large", "oversized"}

    assert review_scope.main(["--repo", str(repo), "--base", "HEAD~1", "--markdown"]) == 0
    rendered = capsys.readouterr().out
    assert rendered.startswith("# Review scope")
    assert "Attention order" in rendered


def test_cli_rejects_unknown_revision(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = review_scope.main(["--repo", str(repo), "--base", "does-not-exist", "--json"])
    assert code == 1
    assert "does-not-exist" in capsys.readouterr().err


def test_tier_override_is_honoured(repo: Path) -> None:
    write(repo, "app/service.py", "def serve():\n    return 'changed'\n")
    commit(repo)
    scope = scope_for(repo, tier="large")
    assert scope["tier"] == "large"


def test_compound_risk_filenames_are_flagged(repo: Path) -> None:
    write(repo, "app/credential-session-authority.md", "contract\n")
    write(repo, "app/tenant-isolation.md", "contract\n")
    commit(repo)
    scope = scope_for(repo)
    assert "authentication" in scope["risks"]
    assert "app/credential-session-authority.md" in scope["risks"]["authentication"]
    assert "authorization-policy" in scope["risks"]
    assert "app/tenant-isolation.md" in scope["risks"]["authorization-policy"]


def test_harmless_words_are_not_flagged_as_risk_terms(repo: Path) -> None:
    # "author", "retained", and "sessionless" contain risk substrings but are not
    # separated risk terms; over-matching would make every review look sensitive.
    write(repo, "app/author.py", "def author():\n    return 'me'\n")
    write(repo, "app/retained_notes.md", "notes\n")
    write(repo, "app/sessionless.py", "VALUE = 1\n")
    commit(repo)
    scope = scope_for(repo)
    assert scope["risks"] == {}


def test_generated_catalog_projections_do_not_inflate_effective_lines(repo: Path) -> None:
    write(repo, "llms.txt", "- [x](x/SKILL.md)\n" * 400)
    write(repo, ".claude-plugin/marketplace.json", '{}\n')
    write(repo, "app/service.py", "def serve():\n    return 'ok'\n")
    commit(repo)
    scope = scope_for(repo)
    assert scope["totals"]["generated_lines"] >= 400
    assert scope["totals"]["effective_lines"] < 50
    assert scope["tier"] == "small"
    assert "llms.txt" in scope["generated_paths"]


def test_exclude_glob_marks_project_specific_output(repo: Path) -> None:
    write(repo, "reports/summary.json", "".join(f'{{"row": {i}}}\n' for i in range(300)))
    write(repo, "app/service.py", "def serve():\n    return 'ok'\n")
    commit(repo)
    base, head = review_scope.resolve_range(repo, "HEAD~1", "HEAD", False)
    scope = review_scope.build_scope(
        repo, base, head, False, None, excludes=("reports/*.json",)
    )
    assert scope["totals"]["effective_lines"] < 50
    assert "reports/summary.json" in scope["generated_paths"]
    assert scope["exclude_patterns"] == ["reports/*.json"]
