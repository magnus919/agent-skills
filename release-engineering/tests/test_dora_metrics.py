"""Tests for dora_metrics.py.

Covers: the five DORA metrics (deployment frequency, change lead time,
change failure rate, failed deployment recovery time, deployment rework
rate), environment scoping, unavailable-metric guards, --json output, and
exit codes.

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
DORA_METRICS = os.path.join(SCRIPTS_DIR, "dora_metrics.py")

HAPPY_EVENTS = {
    "deployments": [
        {
            "started_at": "2026-01-01T00:00:00Z",
            "finished_at": "2026-01-01T00:30:00Z",
            "commit_sha": "aaa",
            "environment": "prod",
            "success": True,
            "unplanned": False,
        },
        {
            "started_at": "2026-01-02T00:00:00Z",
            "finished_at": "2026-01-02T00:30:00Z",
            "commit_sha": "bbb",
            "environment": "prod",
            "success": False,
            "unplanned": True,
        },
        {
            "started_at": "2026-01-02T01:00:00Z",
            "finished_at": "2026-01-02T01:15:00Z",
            "commit_sha": "ccc",
            "environment": "prod",
            "success": True,
            "unplanned": True,
        },
        {
            "started_at": "2026-01-03T00:00:00Z",
            "finished_at": "2026-01-03T00:30:00Z",
            "commit_sha": "ddd",
            "environment": "prod",
            "success": True,
            "unplanned": False,
        },
    ],
    "commits": [
        {"sha": "aaa", "created_at": "2025-12-31T12:00:00Z"},
        {"sha": "bbb", "created_at": "2026-01-01T12:00:00Z"},
        {"sha": "ccc", "created_at": "2026-01-02T00:45:00Z"},
        {"sha": "ddd", "created_at": "2026-01-03T00:00:00Z"},
    ],
}


def run_dora(args):
    """Run dora_metrics.py with given args, return (returncode, stdout, stderr)."""
    cmd = [sys.executable, DORA_METRICS] + args
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return proc.returncode, proc.stdout, proc.stderr


def write_events(events):
    """Write an events dict to a temp JSON file and return its path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(events, tmp)
        return tmp.name


class TestDoraMetricsHappyPath(unittest.TestCase):
    """All five metrics compute correctly on well-formed input."""

    def setUp(self):
        self.path = write_events(HAPPY_EVENTS)

    def tearDown(self):
        os.unlink(self.path)

    def test_json_metrics_values(self):
        """Each metric matches the hand-computed expectation."""
        rc, out, _ = run_dora(["--events", self.path, "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out)

        # Deployment frequency: 3 successful over the observation window.
        self.assertTrue(data["deployment_frequency"]["available"])
        self.assertEqual(data["deployment_frequency"]["successful_deployments"], 3)
        self.assertAlmostEqual(
            data["deployment_frequency"]["deployments_per_day"],
            3.0 / 2.020833,
            places=4,
        )

        # Change lead time: median of finished_at - commit created_at over
        # successful deploys with commit data: [12.5h, 30m, 30m] -> 30m.
        self.assertTrue(data["change_lead_time"]["available"])
        self.assertAlmostEqual(data["change_lead_time"]["seconds"], 1800.0, places=3)
        self.assertEqual(data["change_lead_time"]["deployments_measured"], 3)

        # Change failure rate: 1 failed of 4.
        self.assertTrue(data["change_failure_rate"]["available"])
        self.assertAlmostEqual(data["change_failure_rate"]["percent"], 25.0, places=4)

        # Failed deployment recovery time: failed bbb -> next success ccc
        # finished 01:15 Jan 2, bbb started 00:00 Jan 2 -> 75 minutes.
        self.assertTrue(data["failed_deployment_recovery_time"]["available"])
        self.assertAlmostEqual(
            data["failed_deployment_recovery_time"]["seconds"], 4500.0, places=3
        )

        # Deployment rework rate: 2 unplanned of 4.
        self.assertTrue(data["deployment_rework_rate"]["available"])
        self.assertAlmostEqual(data["deployment_rework_rate"]["percent"], 50.0, places=4)

    def test_counts(self):
        """Counts reflect the input deployments."""
        rc, out, _ = run_dora(["--events", self.path, "--json"])
        data = json.loads(out)
        counts = data["deployments"]
        self.assertEqual(
            counts, {"total": 4, "successful": 3, "failed": 1, "unplanned": 2}
        )

    def test_human_output_default(self):
        """Without --json, output is a human-readable table."""
        rc, out, _ = run_dora(["--events", self.path])
        self.assertEqual(rc, 0)
        self.assertIn("deployment frequency", out)
        self.assertIn("change lead time", out)
        self.assertIn("change failure rate", out)
        self.assertIn("failed deployment recovery time", out)
        self.assertIn("deployment rework rate", out)


class TestDoraMetricsGuards(unittest.TestCase):
    """Unavailable-metric guards."""

    def test_unrecovered_failed_deploy_fdrt_unavailable(self):
        """FDRT is unavailable when a failed deploy has no later success."""
        events = {
            "deployments": [
                {
                    "started_at": "2026-01-01T00:00:00Z",
                    "finished_at": "2026-01-01T00:10:00Z",
                    "commit_sha": None,
                    "environment": "prod",
                    "success": True,
                    "unplanned": False,
                },
                {
                    "started_at": "2026-01-02T00:00:00Z",
                    "finished_at": "2026-01-02T00:10:00Z",
                    "commit_sha": None,
                    "environment": "prod",
                    "success": False,
                    "unplanned": True,
                },
            ],
            "commits": [],
        }
        path = write_events(events)
        try:
            rc, out, _ = run_dora(["--events", path, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            fdrt = data["failed_deployment_recovery_time"]
            self.assertFalse(fdrt["available"])
            self.assertIn("not yet recovered", fdrt["reason"])
        finally:
            os.unlink(path)

    def test_no_failed_deployments_fdrt_unavailable(self):
        """FDRT is unavailable when there are no failed deployments."""
        events = {
            "deployments": [
                {
                    "started_at": "2026-01-01T00:00:00Z",
                    "finished_at": "2026-01-01T00:10:00Z",
                    "commit_sha": None,
                    "environment": "prod",
                    "success": True,
                    "unplanned": False,
                }
            ],
            "commits": [],
        }
        path = write_events(events)
        try:
            rc, out, _ = run_dora(["--events", path, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            fdrt = data["failed_deployment_recovery_time"]
            self.assertFalse(fdrt["available"])
            self.assertIn("no failed deployments", fdrt["reason"])
        finally:
            os.unlink(path)

    def test_missing_commit_timestamps_clt_unavailable(self):
        """CLT is unavailable when no deployment has commit timestamp data."""
        events = {
            "deployments": [
                {
                    "started_at": "2026-01-01T00:00:00Z",
                    "finished_at": "2026-01-01T00:10:00Z",
                    "commit_sha": "aaa",
                    "environment": "prod",
                    "success": True,
                    "unplanned": False,
                }
            ],
            "commits": [],
        }
        path = write_events(events)
        try:
            rc, out, _ = run_dora(["--events", path, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            clt = data["change_lead_time"]
            self.assertFalse(clt["available"])
            self.assertEqual(clt["deployments_measured"], 0)
            self.assertEqual(clt["deployments_without_commit_data"], 1)
        finally:
            os.unlink(path)

    def test_no_deployments_all_unavailable(self):
        """An empty deployments array yields unavailable metrics, exit 0."""
        path = write_events({"deployments": [], "commits": []})
        try:
            rc, out, _ = run_dora(["--events", path, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            for key in (
                "deployment_frequency",
                "change_lead_time",
                "change_failure_rate",
                "failed_deployment_recovery_time",
                "deployment_rework_rate",
            ):
                self.assertFalse(data[key]["available"], key)
        finally:
            os.unlink(path)

    def test_environment_scoping(self):
        """Deployments in other environments are excluded."""
        events = {
            "deployments": [
                {
                    "started_at": "2026-01-01T00:00:00Z",
                    "finished_at": "2026-01-01T00:10:00Z",
                    "commit_sha": None,
                    "environment": "staging",
                    "success": False,
                    "unplanned": True,
                }
            ],
            "commits": [],
        }
        path = write_events(events)
        try:
            rc, out, _ = run_dora(["--events", path, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["deployments"]["total"], 0)
            self.assertFalse(data["deployment_frequency"]["available"])
        finally:
            os.unlink(path)

    def test_custom_environment(self):
        """--environment selects a non-default environment."""
        path = write_events(HAPPY_EVENTS)
        try:
            rc, out, _ = run_dora(
                ["--events", path, "--environment", "staging", "--json"]
            )
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["environment"], "staging")
            self.assertEqual(data["deployments"]["total"], 0)
        finally:
            os.unlink(path)


class TestDoraMetricsExitCodes(unittest.TestCase):
    """Exit codes for malformed input and usage errors."""

    def test_missing_events_exit_2(self):
        """Missing --events is a usage error (exit 2)."""
        rc, _, err = run_dora([])
        self.assertEqual(rc, 2)
        self.assertIn("usage", err.lower())

    def test_malformed_json_exit_1(self):
        """Invalid JSON is an input error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{not json")
            path = tmp.name
        try:
            rc, _, err = run_dora(["--events", path])
            self.assertEqual(rc, 1)
            self.assertIn("invalid json", err.lower())
        finally:
            os.unlink(path)

    def test_missing_file_exit_1(self):
        """A missing events file is an input error."""
        rc, _, err = run_dora(["--events", "/nonexistent/events.json"])
        self.assertEqual(rc, 1)
        self.assertIn("error", err.lower())

    def test_success_must_be_boolean_exit_1(self):
        """A non-boolean success field is an input error."""
        events = {
            "deployments": [
                {
                    "started_at": "2026-01-01T00:00:00Z",
                    "finished_at": "2026-01-01T00:10:00Z",
                    "commit_sha": None,
                    "environment": "prod",
                    "success": "true",
                    "unplanned": False,
                }
            ],
            "commits": [],
        }
        path = write_events(events)
        try:
            rc, _, err = run_dora(["--events", path])
            self.assertEqual(rc, 1)
            self.assertIn("boolean", err.lower())
        finally:
            os.unlink(path)

    def test_invalid_timestamp_exit_1(self):
        """An unparseable timestamp is an input error."""
        events = {
            "deployments": [
                {
                    "started_at": "not-a-date",
                    "finished_at": "2026-01-01T00:10:00Z",
                    "commit_sha": None,
                    "environment": "prod",
                    "success": True,
                    "unplanned": False,
                }
            ],
            "commits": [],
        }
        path = write_events(events)
        try:
            rc, _, err = run_dora(["--events", path])
            self.assertEqual(rc, 1)
            self.assertIn("started_at", err.lower())
        finally:
            os.unlink(path)

    def test_no_traceback_on_malformed(self):
        """Malformed input never produces a traceback."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{broken")
            path = tmp.name
        try:
            rc, out, err = run_dora(["--events", path])
            self.assertNotEqual(rc, 0)
            self.assertNotIn("Traceback", err)
            self.assertNotIn("Traceback", out)
        finally:
            os.unlink(path)

    def test_help_exits_0(self):
        """--help exits 0 and describes usage."""
        rc, out, _ = run_dora(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("usage", out.lower())
        self.assertIn("dora_metrics", out.lower())


class TestDoraMetricsDeterminism(unittest.TestCase):
    """Output is deterministic across runs."""

    def test_json_deterministic(self):
        """Two runs produce identical JSON."""
        path = write_events(HAPPY_EVENTS)
        try:
            rc1, out1, _ = run_dora(["--events", path, "--json"])
            rc2, out2, _ = run_dora(["--events", path, "--json"])
            self.assertEqual(rc1, 0)
            self.assertEqual(rc2, 0)
            self.assertEqual(out1, out2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
