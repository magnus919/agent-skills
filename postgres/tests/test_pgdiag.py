#!/usr/bin/env python3
"""Deterministic tests for the postgres/scripts/pgdiag diagnostic tool.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --check selection, --plan-for, exit codes, JSON payloads).
No PostgreSQL server is required: a fake psql stub is written to a temp
directory at test time and pointed at with --psql. The stub also enforces
the read-only contract by failing any invocation that does not carry the
default_transaction_read_only session setting.
"""
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "pgdiag"

STUB_TEMPLATE = """\
#!/usr/bin/env python3
import os
import sys

args = sys.argv[1:]
sqls = []
index = 0
while index < len(args):
    if args[index] == "-c":
        sqls.append(args[index + 1])
        index += 2
    else:
        index += 1

if not any("default_transaction_read_only" in item for item in sqls):
    print("read-only session setting missing", file=sys.stderr)
    sys.exit(1)

sql = sqls[-1]

if os.environ.get("PGDIAG_STUB_FAIL") == "1":
    print("injected psql failure", file=sys.stderr)
    sys.exit(1)

if "server_version" in sql:
    print("mydb|dba|16.4|160004|f|2026-07-01 08:00:00+00")
elif "pg_stat_archiver" in sql:
    print("42|0|00000001000000000000002A|2026-07-01 00:00:00+00||")
elif "application_name" in sql:
    print("standby-1|streaming|sync|10.0.0.5|0/2A000000|0/2A000000|0/2A000000|0/2A000000")
elif "pg_last_wal_receive_lsn" in sql:
    print("f|0/2A000000|0/2A000000")
elif "pg_extension" in sql:
    print("plpgsql|1.0")
elif "idx_scan DESC" in sql:
    print("public|orders|orders_pkey|12345|24680|12000")
elif "idx_scan = 0" in sql:
    print("public|events|events_created_at_idx|0")
elif "pg_index" in sql:
    pass
elif "seq_tup_read DESC" in sql:
    print("public|orders|5000|1500000|120")
elif "n_dead_tup > 0" in sql:
    print("public|orders|100000|5000|4.8")
elif "pg_stat_activity" in sql:
    print("active|12")
    print("idle|38")
elif "current_setting" in sql:
    print("max_connections|100")
    print("wal_level|replica")
    print("archive_mode|on")
elif "pg_database_size" in sql:
    print("mydb|128 MB")
elif "EXPLAIN" in sql:
    print('[{"Plan": {"Node Type": "Seq Scan", "Plan Rows": 1000}}]')
elif "current_database()" in sql:
    print("mydb|dba|16.4|160004|f|2026-07-01 08:00:00+00")
else:
    pass
"""


def write_stub(directory: Path) -> Path:
    stub = directory / "fake-psql"
    stub.write_text(STUB_TEMPLATE, encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    return stub


def run_script(*args: str, fail: bool = False) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if fail:
        env["PGDIAG_STUB_FAIL"] = "1"
    with tempfile.TemporaryDirectory() as tmp:
        stub = write_stub(Path(tmp))
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--psql", str(stub), *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
    return proc


class HelpTests(unittest.TestCase):
    def test_help_exits_zero_without_cluster(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("read-only", proc.stdout.lower())
        self.assertIn("default_transaction_read_only", proc.stdout)

    def test_version_flag(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("pgdiag", proc.stdout)


class JsonRunTests(unittest.TestCase):
    def test_full_json_run_is_parseable(self):
        proc = run_script("--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["server"]["version"], "16.4")
        self.assertEqual(payload["server"]["database"], "mydb")
        names = [check["name"] for check in payload["checks"]]
        self.assertIn("identity", names)
        self.assertIn("config", names)
        self.assertIn("index_usage", names)
        self.assertIn("bloat", names)
        self.assertIn("wal_archive", names)
        self.assertIn("replication", names)
        self.assertIn("extensions", names)
        self.assertIn("databases", names)
        for check in payload["checks"]:
            self.assertEqual(check["status"], "ok", check["name"])

    def test_text_output_mentions_server_and_checks(self):
        proc = run_script()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Server identity and version", proc.stdout)
        self.assertIn("WAL archiving health", proc.stdout)

    def test_check_subset_selection(self):
        proc = run_script("--check", "identity", "--check", "config", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual([check["name"] for check in payload["checks"]], ["identity", "config"])

    def test_unknown_check_is_usage_error(self):
        proc = run_script("--check", "bogus", "--json")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown check", proc.stderr)

    def test_psql_error_recorded_per_check_but_run_continues(self):
        proc = run_script("--json", fail=True)
        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        names = [check["name"] for check in payload["checks"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(check["status"] == "error" for check in payload["checks"]))


class BinaryAvailabilityTests(unittest.TestCase):
    def test_missing_psql_returns_127_with_json_error(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--psql", "/nonexistent/psql", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 127)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("psql binary not found", payload["error"])


class PlanForTests(unittest.TestCase):
    def test_plan_for_single_select_included(self):
        proc = run_script("--plan-for", "SELECT 1", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        plan_check = payload["checks"][-1]
        self.assertEqual(plan_check["name"], "plan")
        self.assertEqual(plan_check["status"], "ok")
        self.assertIsInstance(plan_check["plan"], list)

    def test_plan_for_rejects_write_statement(self):
        proc = run_script("--plan-for", "INSERT INTO t VALUES (1)", "--json")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("read-only statement", proc.stdout)

    def test_plan_for_rejects_multiple_statements(self):
        proc = run_script("--plan-for", "SELECT 1; SELECT 2", "--json")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
