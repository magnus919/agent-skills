"""Tests for risk-prioritize.py.

Covers: P×I ranking math (ordering, ties), --json output parseability,
exit codes, --help, malformed input handling, and idempotency.

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
RISK_SCRIPT = os.path.join(SCRIPTS_DIR, "risk-prioritize.py")


def run_risk(args, stdin_data=None):
    """Run risk-prioritize.py with given args, return (returncode, stdout, stderr)."""
    cmd = [sys.executable, RISK_SCRIPT] + args
    proc = subprocess.run(
        cmd,
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestRiskPrioritizeRankingMath(unittest.TestCase):
    """P×I ranking math: ordering and ties."""

    def test_basic_ordering(self):
        """Higher P×I scores rank first."""
        items = [
            {"id": "low", "probability": 1, "impact": 1},
            {"id": "high", "probability": 5, "impact": 5},
            {"id": "mid", "probability": 3, "impact": 4},
        ]
        rc, out, _ = run_risk(["--json"], json.dumps(items))
        self.assertEqual(rc, 0)
        results = json.loads(out)
        self.assertEqual(results[0]["id"], "high")
        self.assertEqual(results[0]["score"], 25)
        self.assertEqual(results[1]["id"], "mid")
        self.assertEqual(results[1]["score"], 12)
        self.assertEqual(results[2]["id"], "low")
        self.assertEqual(results[2]["score"], 1)

    def test_score_computation(self):
        """Score equals probability × impact."""
        items = [{"id": "x", "probability": 4, "impact": 3}]
        rc, out, _ = run_risk(["--json"], json.dumps(items))
        self.assertEqual(rc, 0)
        results = json.loads(out)
        self.assertEqual(results[0]["score"], 12)
        self.assertEqual(results[0]["score"], 4 * 3)

    def test_deterministic_tie_break(self):
        """Equal scores are broken by id ascending."""
        items = [
            {"id": "zeta", "probability": 3, "impact": 4},
            {"id": "alpha", "probability": 4, "impact": 3},
            {"id": "mid", "probability": 2, "impact": 6},  # invalid but tests ordering logic
        ]
        # Use valid items only (impact 1-5)
        items = [
            {"id": "zeta", "probability": 3, "impact": 4},
            {"id": "alpha", "probability": 4, "impact": 3},
            {"id": "beta", "probability": 2, "impact": 5},  # score 10
        ]
        rc, out, _ = run_risk(["--json"], json.dumps(items))
        self.assertEqual(rc, 0)
        results = json.loads(out)
        # zeta=12, alpha=12, beta=10
        # tie at 12: alpha < zeta alphabetically
        self.assertEqual(results[0]["id"], "alpha")
        self.assertEqual(results[1]["id"], "zeta")
        self.assertEqual(results[2]["id"], "beta")

    def test_ranks_sequential(self):
        """Ranks are sequential starting at 1."""
        items = [
            {"id": "a", "probability": 5, "impact": 5},
            {"id": "b", "probability": 1, "impact": 1},
            {"id": "c", "probability": 3, "impact": 3},
        ]
        rc, out, _ = run_risk(["--json"], json.dumps(items))
        self.assertEqual(rc, 0)
        results = json.loads(out)
        self.assertEqual([r["rank"] for r in results], [1, 2, 3])


class TestRiskPrioritizeJsonOutput(unittest.TestCase):
    """--json output is machine-parseable."""

    def test_json_parseable(self):
        """--json output parses with json.loads."""
        items = [{"id": "test", "probability": 2, "impact": 3}]
        rc, out, _ = run_risk(["--json"], json.dumps(items))
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_json_fields(self):
        """--json output has id, probability, impact, score, rank fields."""
        items = [{"id": "x", "probability": 5, "impact": 4}]
        rc, out, _ = run_risk(["--json"], json.dumps(items))
        self.assertEqual(rc, 0)
        data = json.loads(out)
        entry = data[0]
        self.assertEqual(entry["id"], "x")
        self.assertEqual(entry["probability"], 5)
        self.assertEqual(entry["impact"], 4)
        self.assertEqual(entry["score"], 20)
        self.assertEqual(entry["rank"], 1)

    def test_human_output_by_default(self):
        """Without --json, output is a human-readable table."""
        items = [{"id": "x", "probability": 5, "impact": 4}]
        rc, out, _ = run_risk([], json.dumps(items))
        self.assertEqual(rc, 0)
        self.assertIn("Rank", out)
        self.assertIn("Score", out)
        self.assertIn("x", out)


class TestRiskPrioritizeExitCodes(unittest.TestCase):
    """Exit codes are correct for various inputs."""

    def test_success_exit_0(self):
        """Valid input exits 0."""
        items = [{"id": "ok", "probability": 1, "impact": 1}]
        rc, _, _ = run_risk(["--json"], json.dumps(items))
        self.assertEqual(rc, 0)

    def test_malformed_json_exit_1(self):
        """Invalid JSON exits 1."""
        rc, _, err = run_risk([], "{not valid json")
        self.assertEqual(rc, 1)
        self.assertIn("error", err.lower())

    def test_not_array_exit_1(self):
        """Non-array JSON exits 1."""
        rc, _, err = run_risk([], '{"key": "value"}')
        self.assertEqual(rc, 1)
        self.assertIn("array", err.lower())

    def test_empty_array_exit_1(self):
        """Empty array exits 1."""
        rc, _, err = run_risk([], "[]")
        self.assertEqual(rc, 1)
        self.assertIn("at least one", err.lower())

    def test_missing_field_exit_1(self):
        """Missing required field exits 1."""
        rc, _, err = run_risk([], '[{"id": "x", "probability": 3}]')
        self.assertEqual(rc, 1)
        self.assertIn("impact", err.lower())

    def test_out_of_range_exit_1(self):
        """probability/impact outside 1-5 exits 1."""
        rc, _, err = run_risk([], '[{"id": "x", "probability": 6, "impact": 3}]')
        self.assertEqual(rc, 1)
        self.assertIn("1-5", err)

    def test_non_integer_exit_1(self):
        """Float probability exits 1."""
        rc, _, err = run_risk([], '[{"id": "x", "probability": 3.5, "impact": 3}]')
        self.assertEqual(rc, 1)
        self.assertIn("integer", err.lower())

    def test_empty_input_exit_1(self):
        """Empty input exits 1."""
        rc, _, err = run_risk([], "")
        self.assertEqual(rc, 1)
        self.assertIn("empty", err.lower())


class TestRiskPrioritizeNoTraceback(unittest.TestCase):
    """Malformed input never produces a Python traceback."""

    def test_no_traceback_invalid_json(self):
        """No traceback on invalid JSON."""
        rc, out, err = run_risk([], "{invalid")
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)

    def test_no_traceback_missing_file(self):
        """No traceback on missing file."""
        rc, out, err = run_risk(["/nonexistent/path/file.json"])
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)


class TestRiskPrioritizeHelp(unittest.TestCase):
    """--help works correctly."""

    def test_help_exits_0(self):
        """--help exits 0."""
        rc, out, _ = run_risk(["--help"])
        self.assertEqual(rc, 0)

    def test_help_has_usage(self):
        """--help output describes usage."""
        rc, out, _ = run_risk(["--help"])
        self.assertIn("usage", out.lower())
        self.assertIn("risk-prioritize", out.lower())


class TestRiskPrioritizeIdempotency(unittest.TestCase):
    """Running twice on the same input yields identical output."""

    def test_idempotent_json(self):
        """Two runs produce identical JSON output."""
        items = [
            {"id": "a", "probability": 5, "impact": 5},
            {"id": "b", "probability": 3, "impact": 3},
        ]
        input_data = json.dumps(items)
        rc1, out1, _ = run_risk(["--json"], input_data)
        rc2, out2, _ = run_risk(["--json"], input_data)
        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 0)
        self.assertEqual(out1, out2)

    def test_idempotent_table(self):
        """Two runs produce identical table output."""
        items = [{"id": "x", "probability": 2, "impact": 4}]
        input_data = json.dumps(items)
        rc1, out1, _ = run_risk([], input_data)
        rc2, out2, _ = run_risk([], input_data)
        self.assertEqual(rc1, 0)
        self.assertEqual(out1, out2)

    def test_no_input_mutation(self):
        """Input file is not modified by the script."""
        items = [{"id": "x", "probability": 5, "impact": 5}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            json.dump(items, tmp)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "r") as f:
                before = f.read()
            rc, _, _ = run_risk([tmp_path])
            self.assertEqual(rc, 0)
            with open(tmp_path, "r") as f:
                after = f.read()
            self.assertEqual(before, after)
        finally:
            os.unlink(tmp_path)

    def test_no_artifacts_created(self):
        """No new files appear after running the script."""
        items = [{"id": "x", "probability": 5, "impact": 5}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir=tempfile.gettempdir()
        ) as tmp:
            json.dump(items, tmp)
            tmp_path = tmp.name
        tmp_dir = tempfile.gettempdir()
        before_files = set(os.listdir(tmp_dir))
        try:
            rc, _, _ = run_risk([tmp_path])
            self.assertEqual(rc, 0)
            after_files = set(os.listdir(tmp_dir))
            new_files = after_files - before_files
            # Filter out files from other processes
            script_artifacts = [
                f for f in new_files if "risk" in f.lower() or "priorit" in f.lower()
            ]
            self.assertEqual(script_artifacts, [])
        finally:
            os.unlink(tmp_path)


class TestRiskPrioritizeFileInput(unittest.TestCase):
    """File path input works correctly."""

    def test_file_input(self):
        """Reading from a file path works."""
        items = [{"id": "file-test", "probability": 4, "impact": 2}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            json.dump(items, tmp)
            tmp_path = tmp.name
        try:
            rc, out, _ = run_risk(["--json", tmp_path])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data[0]["id"], "file-test")
            self.assertEqual(data[0]["score"], 8)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
