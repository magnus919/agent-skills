"""Tests for n1-query-spotter.py.

Covers: query call inside a loop (attribute and bare-name forms), no finding
when queries live outside loops, high-confidence vs possible classification,
nested loops, --json output, --extra-methods, stdin input, --help, and error
paths (missing file, unparseable source).

Discoverable by both pytest and unittest (unittest.TestCase classes).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import suppress

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
SPOTTER = os.path.join(SCRIPTS_DIR, "n1-query-spotter.py")


def run_spotter(args, stdin_data=None):
    cmd = [sys.executable, SPOTTER, *args]
    proc = subprocess.run(
        cmd,
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


def write_source(code):
    """Write Python source to a temp file; return its path."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(code)
        path = handle.name
    return path


def cleanup(path):
    with suppress(OSError):
        os.unlink(path)


class TestN1SpotterFindings(unittest.TestCase):
    def test_flags_query_call_inside_loop(self):
        code = (
            "import db\n"
            "def list_orders(orders):\n"
            "    result = []\n"
            "    for order in orders:\n"
            "        result.append(db.query('SELECT * FROM items WHERE order_id=?', order.id))\n"
            "    return result\n"
        )
        path = write_source(code)
        try:
            rc, stdout, _ = run_spotter([path])
            self.assertEqual(rc, 1)
            self.assertIn("potential N+1", stdout)
            self.assertIn("inside loop at line 4", stdout)
        finally:
            cleanup(path)

    def test_flags_attribute_query_in_loop(self):
        code = (
            "def send_receipts(customers):\n"
            "    for customer in customers:\n"
            "        account = customer.accounts.get(account_id=customer.default_account_id)\n"
            "        email_receipt(account)\n"
        )
        path = write_source(code)
        try:
            rc, stdout, _ = run_spotter([path])
            self.assertEqual(rc, 1)
            self.assertIn("potential N+1", stdout)
            self.assertIn(".get(", stdout)
        finally:
            cleanup(path)

    def test_no_finding_when_query_outside_loop(self):
        code = (
            "import db\n"
            "def list_orders(order_ids):\n"
            "    placeholders = ','.join('?' for _ in order_ids)\n"
            "    return db.query(f'SELECT * FROM orders WHERE id IN ({placeholders})', *order_ids)\n"
        )
        path = write_source(code)
        try:
            rc, stdout, _ = run_spotter([path])
            self.assertEqual(rc, 0)
            self.assertEqual(stdout.strip(), "")
        finally:
            cleanup(path)

    def test_no_finding_without_query_calls(self):
        code = "def add(a, b):\n    return a + b\n"
        path = write_source(code)
        try:
            rc, stdout, _ = run_spotter([path])
            self.assertEqual(rc, 0)
            self.assertEqual(stdout.strip(), "")
        finally:
            cleanup(path)

    def test_nested_loop_detection(self):
        code = (
            "def flatten(teams):\n"
            "    for team in teams:\n"
            "        for member in team.members:\n"
            "            profile = profiles.find(member.profile_id)\n"
        )
        path = write_source(code)
        try:
            rc, stdout, _ = run_spotter([path])
            self.assertEqual(rc, 1)
            self.assertIn("potential N+1", stdout)
            self.assertIn("profiles.find", stdout)
        finally:
            cleanup(path)

    def test_while_loop_detection(self):
        code = (
            "def drain(queue):\n"
            "    while queue:\n"
            "        item = queue.pop()\n"
            "        row = db.execute('SELECT * FROM jobs WHERE id=?', item.id)\n"
        )
        path = write_source(code)
        try:
            rc, stdout, _ = run_spotter([path])
            self.assertEqual(rc, 1)
            self.assertIn("inside loop", stdout)
        finally:
            cleanup(path)


class TestN1SpotterConfidence(unittest.TestCase):
    def test_high_confidence_when_loop_var_referenced(self):
        code = (
            "def render(users):\n"
            "    for user in users:\n"
            "        posts = db.query(posts_by_author, user.id)\n"
        )
        path = write_source(code)
        try:
            _, stdout, _ = run_spotter([path, "--json"])
            report = json.loads(stdout)
            self.assertEqual(report["count"], 1)
            self.assertEqual(report["findings"][0]["confidence"], "high")
            self.assertEqual(report["findings"][0]["loop_targets"], ["user"])
        finally:
            cleanup(path)

    def test_possible_confidence_without_loop_var(self):
        code = "def process(rows):\n    for _ in rows:\n        db.query('SELECT 1')\n"
        path = write_source(code)
        try:
            _, stdout, _ = run_spotter([path, "--json"])
            report = json.loads(stdout)
            self.assertEqual(report["count"], 1)
            self.assertEqual(report["findings"][0]["confidence"], "possible")
        finally:
            cleanup(path)


class TestN1SpotterCli(unittest.TestCase):
    def test_help_exits_zero(self):
        rc, stdout, _ = run_spotter(["--help"])
        self.assertEqual(rc, 0)
        self.assertIn("potential N+1", stdout)

    def test_json_output_parseable(self):
        code = "def go(items):\n    for item in items:\n        row = db.get(item.id)\n"
        path = write_source(code)
        try:
            rc, stdout, _ = run_spotter([path, "--json"])
            self.assertEqual(rc, 1)
            report = json.loads(stdout)
            self.assertEqual(report["count"], 1)
            self.assertEqual(report["findings"][0]["file"], path)
        finally:
            cleanup(path)

    def test_stdin_input(self):
        code = "for row in rows:\n    fetch(row.id)\n"
        rc, stdout, _ = run_spotter([], stdin_data=code)
        self.assertEqual(rc, 1)
        self.assertIn("<stdin>", stdout)

    def test_extra_methods_flag(self):
        code = "def go(items):\n    for item in items:\n        engine.raw_query(item.id)\n"
        path = write_source(code)
        try:
            rc_without, _, _ = run_spotter([path])
            rc_with, stdout, _ = run_spotter([path, "--extra-methods", "raw_query"])
            self.assertEqual(rc_without, 0)
            self.assertEqual(rc_with, 1)
            self.assertIn("raw_query", stdout)
        finally:
            cleanup(path)

    def test_missing_file_exit_two(self):
        rc, _, stderr = run_spotter(["/nonexistent/nope.py"])
        self.assertEqual(rc, 2)
        self.assertIn("ERROR", stderr)

    def test_parse_error_exit_two(self):
        path = write_source("def broken(:\n    pass\n")
        try:
            rc, _, stderr = run_spotter([path])
            self.assertEqual(rc, 2)
            self.assertIn("cannot parse", stderr)
        finally:
            cleanup(path)

    def test_empty_file_exit_zero(self):
        path = write_source("")
        try:
            rc, stdout, _ = run_spotter([path])
            self.assertEqual(rc, 0)
            self.assertEqual(stdout.strip(), "")
        finally:
            cleanup(path)


if __name__ == "__main__":
    unittest.main()
