"""Production resource staging for real catalog packages."""

import json
import sys
from pathlib import Path

import pytest

from eval_runner.cli_adapter import CliSubprocessAdapter
from eval_runner.models import AdapterInput, EvalCase, ExitStatus
from eval_runner.sandbox import cleanup_sandbox, stage_skill_sandbox

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("skill", "resources"),
    [
        ("tailscale", ("skills/headscale-deploy/SKILL.md", "skills/headscale-backup/SKILL.md")),
        ("workflow-architect", ("skills/observer/SKILL.md", "skills/bundle-builder/SKILL.md")),
        (
            "community-guides",
            (
                "examples/apartment-guide.md",
                "examples/apartment-plan.json",
                "examples/apartment-facilitator.md",
            ),
        ),
        ("agent-council", ("agent_council/cli.py", "pyproject.toml")),
        ("documents", ("fixtures/sample.pdf",)),
    ],
)
def test_shipped_resources_survive_staging(skill, resources):
    staged = stage_skill_sandbox(ROOT / skill)
    try:
        for relative_path in resources:
            assert (staged / relative_path).read_bytes() == (
                ROOT / skill / relative_path
            ).read_bytes()
        assert not (staged / "evals").exists()
        assert not list(staged.glob("skills/*/evals"))
    finally:
        cleanup_sandbox(staged)


def test_nested_skill_retains_parent_paths_and_cleans_up():
    staged = stage_skill_sandbox(ROOT / "workflow-architect/skills/bundle-builder")
    staging_root = staged.parents[2]
    try:
        assert (staged / "SKILL.md").is_file()
        assert (staged / "../../templates/skill-skeleton.md").is_file()
        assert not (staged / "../../evals").exists()
    finally:
        cleanup_sandbox(staged)
    assert not staging_root.exists()


@pytest.mark.parametrize("name", ["../outside", "evals", "missing", "/tmp", "examples/nested"])
def test_runtime_declaration_rejects_unsafe_or_missing_directory(tmp_path, name):
    (tmp_path / "runtime-resources.json").write_text(json.dumps([name]))
    (tmp_path / "evals").mkdir()
    with pytest.raises(ValueError, match="invalid runtime resource declaration"):
        stage_skill_sandbox(tmp_path)


def test_declared_directory_still_excludes_evaluation_assets(tmp_path):
    (tmp_path / "runtime-resources.json").write_text('["examples"]')
    examples = tmp_path / "examples"
    examples.mkdir()
    (examples / "demo.md").write_text("production sample")
    (examples / "rubric.md").write_text("grader-only sample")
    (examples / "evals").mkdir()
    staged = stage_skill_sandbox(tmp_path)
    try:
        assert (staged / "examples/demo.md").read_text() == "production sample"
        assert not (staged / "examples/rubric.md").exists()
        assert not (staged / "examples/evals").exists()
    finally:
        cleanup_sandbox(staged)


def test_subprocess_can_use_the_packaged_entry_point(tmp_path):
    staged = stage_skill_sandbox(ROOT / "workflow-architect/skills/bundle-builder")
    try:
        script = """
import os
from pathlib import Path
skill = Path(os.environ["EVAL_SKILL_DIR"])
assert (skill / "SKILL.md").is_file()
assert (skill / "../../templates/skill-skeleton.md").is_file()
assert not (skill / "../../evals").exists()
print("loaded the staged bundle entry point")
"""
        adapter = CliSubprocessAdapter([sys.executable, "-c", script])
        output = adapter.execute(
            AdapterInput(
                staged,
                EvalCase("staged-entry", "Read the entry point", "", [], []),
                tmp_path / "work",
                tmp_path / "output",
            )
        )
        assert output.exit_status is ExitStatus.COMPLETED
        assert output.response == "loaded the staged bundle entry point\n"
    finally:
        cleanup_sandbox(staged)
