#!/usr/bin/env python3
"""Deterministic tests for the telemetry/scripts/telemetry-check tool.

Runs the script as a subprocess so the tests exercise the real CLI surface
(--help, --json, --rules, --scrape, --targets, exit codes, JSON payloads).
Rules fixtures are written to temp directories at test time; scrape-target
tests probe a real local listening socket for the reachable case and a
just-released port for the unreachable case, so no external network is needed.
Also asserts the read-only contract: the script never opens files in write mode.
"""
import json
import re
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "telemetry-check"
FIXTURES = ROOT / "fixtures"


def run_script(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def load_json(proc):
    return json.loads(proc.stdout)


def free_port():
    """Bind a socket to an ephemeral port and return (port, socket); caller closes."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    return sock.getsockname()[1], sock


class HelpTests(unittest.TestCase):
    def test_help_exits_zero_and_advertises_capabilities(self):
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--json", proc.stdout)
        self.assertIn("rule", proc.stdout.lower())
        self.assertIn("scrape", proc.stdout.lower())
        self.assertIn("read-only", proc.stdout.lower())

    def test_version_flag(self):
        proc = run_script("--version")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("telemetry-check", proc.stdout)

    def test_no_args_is_usage_error(self):
        proc = run_script()
        self.assertEqual(proc.returncode, 2)


class RulesFileTests(unittest.TestCase):
    def test_valid_fixture_parses_to_json_and_passes(self):
        proc = run_script("--rules", str(FIXTURES / "prometheus-rules.yml"), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = load_json(proc)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["checks"][0]["status"], "ok")
        self.assertEqual(payload["checks"][0]["groups"], 2)
        self.assertEqual(payload["checks"][0]["rules"], 4)
        self.assertEqual(payload["checks"][0]["errors"], [])

    def test_malformed_yaml_is_rejected(self):
        bad = "groups:\n  - name: bad\n   rules:\n     - record: x\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.yml"
            path.write_text(bad, encoding="utf-8")
            proc = run_script("--rules", str(path), "--json")
        self.assertNotEqual(proc.returncode, 0)
        payload = load_json(proc)
        self.assertFalse(payload["ok"])
        self.assertIn("invalid YAML", payload["checks"][0]["error"])

    def test_duplicate_group_names_detected(self):
        rules = (
            "groups:\n"
            "  - name: g1\n"
            "    rules:\n"
            "      - record: a_total\n"
            "        expr: sum(foo)\n"
            "  - name: g1\n"
            "    rules:\n"
            "      - alert: B\n"
            "        expr: up == 0\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.yml"
            path.write_text(rules, encoding="utf-8")
            proc = run_script("--rules", str(path), "--json")
        self.assertEqual(proc.returncode, 1)
        errors = load_json(proc)["checks"][0]["errors"]
        self.assertTrue(any("repeated" in error for error in errors))

    def test_rule_errors_detected(self):
        rules = (
            "groups:\n"
            "  - name: g1\n"
            "    rules:\n"
            "      - record: bad{name}\n"
            "        alert: AlsoAlert\n"
            "        for: 5x\n"
            "        labels:\n"
            "          severity: 5\n"
            "      - record: ok_name\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "errors.yml"
            path.write_text(rules, encoding="utf-8")
            proc = run_script("--rules", str(path), "--json")
        self.assertEqual(proc.returncode, 1)
        errors = load_json(proc)["checks"][0]["errors"]
        joined = "\n".join(errors)
        self.assertIn("only one of 'record' and 'alert'", joined)
        self.assertIn("braces present in recording rule name", joined)
        self.assertIn("invalid duration", joined)
        self.assertIn("not a YAML string", joined)
        self.assertIn("field 'expr' must be set", joined)

    def test_unbalanced_expression_is_detected(self):
        rules = (
            "groups:\n"
            "  - name: g1\n"
            "    rules:\n"
            "      - record: a_total\n"
            "        expr: sum(foo\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unbalanced.yml"
            path.write_text(rules, encoding="utf-8")
            proc = run_script("--rules", str(path), "--json")
        self.assertEqual(proc.returncode, 1)
        errors = load_json(proc)["checks"][0]["errors"]
        self.assertTrue(any("unbalanced" in error for error in errors))

    def test_quoted_numeric_label_value_is_accepted(self):
        rules = (
            "groups:\n"
            "  - name: g1\n"
            "    rules:\n"
            "      - alert: HighCPU\n"
            "        expr: cpu_usage > 0.9\n"
            "        labels:\n"
            "          severity: \"5\"\n"
            "          team: platform\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "quoted.yml"
            path.write_text(rules, encoding="utf-8")
            proc = run_script("--rules", str(path), "--json")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(load_json(proc)["checks"][0]["errors"], [])

    def test_warning_only_findings_are_not_fatal(self):
        rules = (
            "groups:\n"
            "  - name: g1\n"
            "    rules:\n"
            "      - record: my rule\n"
            "        expr: sum(foo)\n"
            "        extra_field: 1\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "warn.yml"
            path.write_text(rules, encoding="utf-8")
            proc = run_script("--rules", str(path), "--json")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        check = load_json(proc)["checks"][0]
        self.assertEqual(check["status"], "ok")
        self.assertTrue(any("metric-name pattern" in w for w in check["warnings"]))
        self.assertTrue(any("unknown rule field" in w for w in check["warnings"]))

    def test_block_scalar_expression_parses(self):
        rules = (
            "groups:\n"
            "  - name: g1\n"
            "    rules:\n"
            "      - alert: SlowQueries\n"
            "        expr: |\n"
            "          histogram_quantile(0.99,\n"
            "            sum by (le) (rate(query_duration_seconds_bucket[5m])))\n"
            "        for: 15m\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "block.yml"
            path.write_text(rules, encoding="utf-8")
            proc = run_script("--rules", str(path), "--json")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(load_json(proc)["checks"][0]["errors"], [])

    def test_missing_rules_file_is_fatal(self):
        proc = run_script("--rules", "/nonexistent/rules.yml", "--json")
        self.assertEqual(proc.returncode, 1)
        payload = load_json(proc)
        self.assertEqual(payload["checks"][0]["status"], "error")


class ScrapeTargetTests(unittest.TestCase):
    def test_scrape_config_probes_reachable_and_unreachable(self):
        reachable_port, listener = free_port()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                unreachable_port, probe = free_port()
                probe.close()
                config = (
                    "scrape_configs:\n"
                    "  - job_name: local\n"
                    "    static_configs:\n"
                    "      - targets:\n"
                    "          - '127.0.0.1:%d'\n"
                    "          - '127.0.0.1:%d'\n" % (reachable_port, unreachable_port)
                )
                path = Path(tmp) / "scrape.yml"
                path.write_text(config, encoding="utf-8")
                proc = run_script(
                    "--scrape", str(path), "--json", "--timeout", "1"
                )
        finally:
            listener.close()
        self.assertEqual(proc.returncode, 1)
        check = load_json(proc)["checks"][0]
        self.assertEqual(check["status"], "issues")
        by_target = {entry["target"]: entry for entry in check["targets"]}
        self.assertTrue(by_target["127.0.0.1:%d" % reachable_port]["reachable"])
        self.assertFalse(by_target["127.0.0.1:%d" % unreachable_port]["reachable"])

    def test_targets_plain_list_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.txt"
            path.write_text("127.0.0.1:1\n127.0.0.1:2\n", encoding="utf-8")
            proc = run_script("--targets", str(path), "--json", "--timeout", "1")
        self.assertEqual(proc.returncode, 1)
        check = load_json(proc)["checks"][0]
        self.assertEqual(len(check["targets"]), 2)
        self.assertTrue(all(not entry["reachable"] for entry in check["targets"]))

    def test_targets_yaml_list_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.yml"
            path.write_text("- 127.0.0.1:1\n- 127.0.0.1:2\n", encoding="utf-8")
            proc = run_script("--targets", str(path), "--json", "--timeout", "1")
        self.assertEqual(proc.returncode, 1)
        check = load_json(proc)["checks"][0]
        self.assertEqual(len(check["targets"]), 2)


class ReadOnlyContractTests(unittest.TestCase):
    def test_script_never_opens_files_for_writing(self):
        source = SCRIPT.read_text(encoding="utf-8")
        pattern = re.compile(r"open\([^)]*['\"][w]['\"]")
        self.assertIsNone(pattern.search(source))
        self.assertIn("read-only", source.lower())


if __name__ == "__main__":
    unittest.main()
