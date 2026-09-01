#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "validate_frontmatter_audit", Path(__file__).parent / "validate-frontmatter-audit.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("unable to load audit module")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
audit = _module.audit


class FrontmatterAuditTests(unittest.TestCase):
    def write_skill(self, root: Path, name: str, description: str, body: str = "") -> None:
        path = root / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name.name}\ndescription: {description}\n---\n\n{body}", encoding="utf-8"
        )

    def test_accepts_imperative_positive_and_boundary_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root, Path("example"), "Query PromQL metrics. Do not use this skill for LogQL."
            )
            report = audit(root)
            self.assertTrue(report["ok"])
            self.assertEqual(report["files_audited"], 1)

    def test_rejects_noun_opener_and_missing_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(root, Path("example"), "A metrics helper for dashboards.")
            report = audit(root)
            self.assertFalse(report["ok"])
            self.assertEqual(
                {item["rule"] for item in report["violations"]},
                {"imperative-opener", "negative-boundary"},
            )

    def test_accepts_substantive_when_not_to_use_section(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                Path("example"),
                "Query PromQL metrics.",
                "## When not to use\nUse grafana for dashboard editing.\n",
            )
            self.assertTrue(audit(root)["ok"])

    def test_discovers_nested_bundle_skills_but_excludes_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(
                root,
                Path("bundle/skills/nested"),
                "Query PromQL metrics. Do not use this skill for LogQL.",
            )
            self.write_skill(
                root,
                Path("agent-council/profiles/skills/profile"),
                "Query PromQL metrics. Do not use this skill for LogQL.",
            )
            report = audit(root)
            self.assertTrue(report["ok"])
            self.assertEqual(report["files_audited"], 1)


if __name__ == "__main__":
    unittest.main()
