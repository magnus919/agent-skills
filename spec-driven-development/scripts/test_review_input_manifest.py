"""Tests for the review input manifest helper."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("review_input_manifest.py")
SPEC = importlib.util.spec_from_file_location("review_input_manifest", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
manifest_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest_module)


class ReviewInputManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "src").mkdir()
        (self.root / "docs" / "design.md").write_text("design bytes\n", encoding="utf-8")
        (self.root / "README.md").write_text("project context\n", encoding="utf-8")
        (self.root / "src" / "service.py").write_text("def run(): pass\n", encoding="utf-8")

    def test_manifest_hashes_explicit_inputs_without_copying_content(self) -> None:
        result = manifest_module.build_manifest(
            str(self.root), "docs/design.md", ["README.md", "src/service.py"]
        )
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["target"]["path"], "docs/design.md")
        self.assertEqual(result["target"]["sha256"], hashlib.sha256(b"design bytes\n").hexdigest())
        self.assertEqual(
            [item["path"] for item in result["context"]],
            ["README.md", "src/service.py"],
        )
        self.assertNotIn("design bytes", json.dumps(result))
        self.assertNotIn(str(self.root), json.dumps(result))
        self.assertEqual(len(result["bundle_sha256"]), 64)

    def test_context_order_does_not_change_bundle_hash(self) -> None:
        first = manifest_module.build_manifest(
            str(self.root), "docs/design.md", ["README.md", "src/service.py"]
        )
        second = manifest_module.build_manifest(
            str(self.root), "docs/design.md", ["src/service.py", "README.md"]
        )
        self.assertEqual(first["bundle_sha256"], second["bundle_sha256"])

    def test_changed_content_changes_file_and_bundle_hash(self) -> None:
        first = manifest_module.build_manifest(str(self.root), "docs/design.md", ["README.md"])
        (self.root / "README.md").write_text("changed context\n", encoding="utf-8")
        second = manifest_module.build_manifest(str(self.root), "docs/design.md", ["README.md"])
        self.assertNotEqual(first["context"][0]["sha256"], second["context"][0]["sha256"])
        self.assertNotEqual(first["bundle_sha256"], second["bundle_sha256"])

    def test_duplicate_resolved_context_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate"):
            manifest_module.build_manifest(
                str(self.root), "docs/design.md", ["README.md", "./README.md"]
            )

    def test_target_cannot_also_be_context(self) -> None:
        with self.assertRaisesRegex(ValueError, "target"):
            manifest_module.build_manifest(
                str(self.root), "docs/design.md", ["docs/design.md"]
            )

    def test_missing_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not exist"):
            manifest_module.build_manifest(str(self.root), "docs/missing.md", [])

    def test_directory_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            manifest_module.build_manifest(str(self.root), "src", [])

    def test_symlink_escape_is_rejected(self) -> None:
        outside = Path(self.temp.name).parent / f"{Path(self.temp.name).name}-outside"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(outside.unlink)
        link = self.root / "outside.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable")
        with self.assertRaisesRegex(ValueError, "escapes"):
            manifest_module.build_manifest(str(self.root), "docs/design.md", ["outside.md"])

    def test_cli_emits_json_and_rejects_outside_paths(self) -> None:
        ok = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root),
             "--target", "docs/design.md", "--context", "README.md"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(ok.stdout)["target"]["path"], "docs/design.md")

        outside = self.root.parent / f"{self.root.name}-outside-file"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(outside.unlink)
        denied = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root),
             "--target", str(outside)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(denied.returncode, 2)
        self.assertIn("escapes review root", denied.stderr)


if __name__ == "__main__":
    unittest.main()
