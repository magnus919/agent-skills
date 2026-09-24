"""Tests for allowed Jev teacher-calibration source-run provenance."""

import unittest

from jev_teacher_source import EXPECTED_PATH, validate_source


class JevTeacherSourceTests(unittest.TestCase):
    def valid_source(self, **overrides):
        metadata = {
            "id": 35989698935,
            "head_branch": "main",
            "event": "push",
            "conclusion": "success",
            "path": EXPECTED_PATH,
        }
        metadata.update(overrides)
        return metadata

    def test_accepts_successful_main_push(self):
        self.assertEqual(validate_source(self.valid_source(), "35989698935"), "push")

    def test_accepts_successful_main_manual_smoke(self):
        self.assertEqual(
            validate_source(self.valid_source(event="workflow_dispatch"), "35989698935"),
            "workflow_dispatch",
        )

    def test_rejects_changed_run_identity_and_invalid_ids(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate_source(self.valid_source(id=35989698936), "35989698935")
        for run_id in ("0", "-1", "not-a-run", "1" * 21):
            with (
                self.subTest(run_id=run_id),
                self.assertRaisesRegex(ValueError, "positive decimal"),
            ):
                validate_source(self.valid_source(), run_id)

    def test_rejects_untrusted_or_unsuccessful_runs(self):
        for change in (
            {"head_branch": "pull/123/head"},
            {"event": "pull_request"},
            {"event": ["workflow_dispatch"]},
            {"conclusion": "failure"},
            {"path": ".github/workflows/jev-teacher-calibration.yml"},
        ):
            with (
                self.subTest(change=change),
                self.assertRaisesRegex(ValueError, "successful main-branch"),
            ):
                validate_source(self.valid_source(**change), "35989698935")

    def test_rejects_missing_or_malformed_metadata(self):
        for metadata in (None, [], {}, {"id": True}):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                validate_source(metadata, "35989698935")


if __name__ == "__main__":
    unittest.main()
