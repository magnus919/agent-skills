"""Unit tests for promise-theory/scripts/promise-contract.py.

Run from the repository root:

    python3 -m unittest discover -s promise-theory/tests -p 'test_*.py'

The tests exercise the CLI black-box (subprocess) so they pin the observable
contract: exit codes, stdout/stderr separation, and the --json shape.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts",
    "promise-contract.py",
)

VALID_YAML = """# promise-manifest v1
agents:
  - id: research-agent
    role: literature summarizer
    accepts: [research-direction]
    promises:
      - id: lit-review
        type: capability
        target: human
        body: Survey and summarize literature on promise theory.
        constraint: limit 20 sources
        withdraw: when coordinator withdraws direction
  - id: coordinator
    role: human coordinator
    accepts: [lit-review]
    promises:
      - id: research-direction
        type: intent
        target: research-agent
        body: Provide research direction and review summaries.
expectations:
  - id: exp-lit-review
    from: human
    about: lit-review
    verifier: manual
    severity: impact
"""

VALID_JSON = json.dumps(
    {
        "agents": [
            {
                "id": "research-agent",
                "role": "literature summarizer",
                "accepts": ["research-direction"],
                "promises": [
                    {
                        "id": "lit-review",
                        "type": "capability",
                        "target": "human",
                        "body": "Survey and summarize literature on promise theory.",
                        "constraint": "limit 20 sources",
                        "withdraw": "when coordinator withdraws direction",
                    }
                ],
            },
            {
                "id": "coordinator",
                "role": "human coordinator",
                "accepts": ["lit-review"],
                "promises": [
                    {
                        "id": "research-direction",
                        "type": "intent",
                        "target": "research-agent",
                        "body": "Provide research direction and review summaries.",
                    }
                ],
            },
        ],
        "expectations": [
            {
                "id": "exp-lit-review",
                "from": "human",
                "about": "lit-review",
                "verifier": "manual",
                "severity": "impact",
            }
        ],
    }
)

SCHEMA_BAD_YAML = """agents:
  - id: research-agent
    role: literature summarizer
    promises:
      - id: lit-review
        type: capability
        target: human
        body: Summarize literature.
  - id: research-agent
    promises:
      - id: bad-promise
        type: maybe
        target: human
        body: Invalid type.
      - id: bad-target-promise
        type: capability
        target: 123
        body: Invalid target scalar.
expectations:
  - id: exp-lit-review
    from: human
    about: lit-review
"""

MALFORMED_YAML = """agents:
  - id: research-agent
    role: "unclosed quote
    promises:
"""


class PromiseContractCliTest(unittest.TestCase):
    """Black-box CLI tests."""

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, SCRIPT, *args], capture_output=True, text=True
        )

    def write_tmp(self, name, content, binary=False):
        path = os.path.join(self.tmpdir, name)
        mode = "wb" if binary else "w"
        kwargs = {} if binary else {"encoding": "utf-8"}
        with open(path, mode, **kwargs) as fh:
            fh.write(content)
        return path

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmp.name
        self.valid_path = self.write_tmp("valid.yaml", VALID_YAML)
        self.valid_json_path = self.write_tmp("valid.json", VALID_JSON)

    def tearDown(self):
        self._tmp.cleanup()

    # -- basics -------------------------------------------------------------

    def test_help_names_subcommands_and_flags(self):
        p = self.run_cli("--help")
        self.assertEqual(p.returncode, 0)
        out = p.stdout.lower()
        for needle in ("lint", "render", "--json", "--dry-run"):
            self.assertIn(needle, out)

    def test_version_is_dotted_triple(self):
        p = self.run_cli("--version")
        self.assertEqual(p.returncode, 0)
        version = p.stdout.strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")

    # -- valid contracts ----------------------------------------------------

    def test_valid_yaml_lints_clean(self):
        p = self.run_cli("lint", self.valid_path)
        self.assertEqual(p.returncode, 0)
        self.assertIn("valid", p.stdout.lower())
        self.assertIn("cover", p.stdout.lower())

    def test_valid_json_lints_clean(self):
        p = self.run_cli("lint", self.valid_json_path)
        self.assertEqual(p.returncode, 0)
        self.assertIn("valid", p.stdout.lower())

    def test_valid_lint_json_shape(self):
        p = self.run_cli("lint", self.valid_path, "--json")
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        self.assertEqual(
            set(data), {"valid", "errors", "warnings", "coverage", "bindings"}
        )
        self.assertIs(data["valid"], True)
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["coverage"]["uncovered"], [])
        self.assertEqual(data["coverage"]["total"], 1)
        self.assertEqual(data["coverage"]["covered"], 1)
        for b in data["bindings"]:
            self.assertEqual(set(b), {"promise_id", "promiser", "acceptor"})
        binding_ids = {b["promise_id"] for b in data["bindings"]}
        self.assertEqual(binding_ids, {"lit-review", "research-direction"})

    def test_yaml_json_parity(self):
        y = json.loads(self.run_cli("lint", self.valid_path, "--json").stdout)
        j = json.loads(self.run_cli("lint", self.valid_json_path, "--json").stdout)
        self.assertIs(y["valid"], True)
        self.assertIs(j["valid"], True)
        self.assertEqual(
            (y["coverage"]["total"], y["coverage"]["covered"]),
            (j["coverage"]["total"], j["coverage"]["covered"]),
        )
        self.assertEqual(
            {b["promise_id"] for b in y["bindings"]},
            {b["promise_id"] for b in j["bindings"]},
        )

    # -- coverage gap -------------------------------------------------------

    def test_coverage_gap_rejected(self):
        gap = self.write_tmp(
            "gap.yaml", VALID_YAML.replace("about: lit-review", "about: nonexistent-promise")
        )
        p = self.run_cli("lint", gap)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("exp-lit-review", combined)
        self.assertIn("nonexistent-promise", combined)

    def test_coverage_gap_json(self):
        gap = self.write_tmp(
            "gap.json", VALID_JSON.replace("lit-review", "nonexistent-promise", 1)
        )
        p = self.run_cli("lint", gap, "--json")
        self.assertEqual(p.returncode, 1)
        data = json.loads(p.stdout)
        self.assertIs(data["valid"], False)
        self.assertTrue(data["errors"])
        self.assertEqual(data["coverage"]["uncovered"], ["exp-lit-review"])

    # -- schema violations --------------------------------------------------

    def test_schema_violations_accumulated(self):
        bad = self.write_tmp("schema-bad.yaml", SCHEMA_BAD_YAML)
        p = self.run_cli("lint", bad)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        for needle in ("research-agent", "role", "maybe", "123"):
            self.assertIn(needle, combined)

    def test_duplicate_agent_id_reported(self):
        bad = self.write_tmp(
            "dup-agent.yaml",
            VALID_YAML.replace("  - id: coordinator", "  - id: research-agent"),
        )
        p = self.run_cli("lint", bad)
        self.assertEqual(p.returncode, 1)
        self.assertIn("research-agent", p.stdout + p.stderr)

    def test_duplicate_promise_id_across_agents_reported(self):
        manifest = """agents:
  - id: research-agent
    role: literature summarizer
    promises:
      - id: shared-promise
        type: capability
        target: human
        body: Write the summary.
  - id: reviewer
    role: reviewer
    promises:
      - id: shared-promise
        type: capability
        target: human
        body: Review the summary.
expectations:
  - id: exp-shared
    from: human
    about: shared-promise
"""
        path = self.write_tmp("dup-promise.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertIn("shared-promise", p.stdout + p.stderr)

    def test_duplicate_expectation_id_reported(self):
        manifest = VALID_YAML + "  - id: exp-lit-review\n    from: human\n    about: lit-review\n"
        path = self.write_tmp("dup-exp.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertIn("exp-lit-review", p.stdout + p.stderr)

    # -- bindings -----------------------------------------------------------

    def test_self_acceptance_rejected(self):
        manifest = """agents:
  - id: research-agent
    role: literature summarizer
    accepts: [lit-review]
    promises:
      - id: lit-review
        type: capability
        target: human
        body: Survey and summarize literature.
expectations:
  - id: exp-lit-review
    from: human
    about: lit-review
"""
        path = self.write_tmp("self-bind.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertIn("self-acceptance", p.stdout + p.stderr)
        self.assertIn("lit-review", p.stdout + p.stderr)

    def test_dangling_accept_rejected(self):
        manifest = """agents:
  - id: research-agent
    role: literature summarizer
    accepts: [ghost-promise]
    promises:
      - id: lit-review
        type: capability
        target: human
        body: Survey and summarize literature.
expectations:
  - id: exp-lit-review
    from: human
    about: lit-review
"""
        path = self.write_tmp("dangling.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertIn("ghost-promise", p.stdout + p.stderr)

    def test_target_all_broadcast_lints_clean(self):
        manifest = """agents:
  - id: research-agent
    role: literature summarizer
    promises:
      - id: broadcast-note
        type: intent
        target: all
        body: Publish a weekly reading list.
expectations:
  - id: exp-broadcast
    from: human
    about: broadcast-note
"""
        path = self.write_tmp("target-all.yaml", manifest)
        p = self.run_cli("lint", path, "--json")
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        self.assertIs(data["valid"], True)
        self.assertEqual(data["coverage"]["uncovered"], [])

    # -- enums / optional fields --------------------------------------------

    def test_bad_enums_rejected(self):
        manifest = """agents:
  - id: research-agent
    role: literature summarizer
    promises:
      - id: lit-review
        type: capability
        target: human
        body: Survey and summarize literature.
expectations:
  - id: exp-lit-review
    from: human
    about: lit-review
    verifier: magic
    severity: critical
"""
        path = self.write_tmp("bad-enum.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("magic", combined)
        self.assertIn("critical", combined)

    def test_bad_from_rejected(self):
        manifest = VALID_YAML.replace("from: human\n", "from: ghost-agent\n")
        path = self.write_tmp("bad-from.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertIn("ghost-agent", p.stdout + p.stderr)

    def test_bad_expires_rejected_and_valid_durations_accepted(self):
        bad = self.write_tmp(
            "bad-expires.yaml",
            VALID_YAML.replace("withdraw: when coordinator withdraws direction\n",
                               "withdraw: when coordinator withdraws direction\n        expires: next-tuesday\n"),
        )
        p = self.run_cli("lint", bad)
        self.assertEqual(p.returncode, 1)
        self.assertIn("next-tuesday", p.stdout + p.stderr)

        for good in ("PT15M", "P30D", "2025-12-31", "2025-12-31T23:59:59Z", "2025-12-31T23:59:59+00:00"):
            manifest = VALID_YAML.replace(
                "withdraw: when coordinator withdraws direction\n",
                f"withdraw: when coordinator withdraws direction\n        expires: {good}\n",
            )
            path = self.write_tmp(f"expires-{good.replace(':', '-').replace('+', '-')}.yaml", manifest)
            p = self.run_cli("lint", path)
            self.assertEqual(p.returncode, 0, f"expires {good} rejected: {p.stdout + p.stderr}")

    def test_empty_constraint_and_withdraw_rejected(self):
        manifest = """agents:
  - id: research-agent
    role: literature summarizer
    promises:
      - id: lit-review
        type: capability
        target: human
        body: Survey and summarize literature.
        constraint: ""
        withdraw: "   "
expectations:
  - id: exp-lit-review
    from: human
    about: lit-review
"""
        path = self.write_tmp("empty-constraint.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("constraint", combined)
        self.assertIn("withdraw", combined)

    def test_empty_expectations_rejected(self):
        manifest = VALID_YAML.replace(
            "expectations:\n  - id: exp-lit-review\n    from: human\n    about: lit-review\n    verifier: manual\n    severity: impact\n",
            "expectations: []\n",
        )
        path = self.write_tmp("empty-exps.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertIn("expectations", p.stdout + p.stderr)

    def test_reserved_agent_ids_rejected(self):
        manifest = """agents:
  - id: human
    role: human coordinator
    promises:
      - id: human-review
        type: capability
        target: research-agent
        body: Review agent output.
  - id: research-agent
    role: literature summarizer
    promises:
      - id: lit-review
        type: capability
        target: human
        body: Survey and summarize literature.
expectations:
  - id: exp-lit-review
    from: human
    about: lit-review
"""
        path = self.write_tmp("reserved.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertIn("human", p.stdout + p.stderr)
        # the 'all' token must be rejected identically
        manifest_all = manifest.replace("id: human", "id: all", 1)
        path_all = self.write_tmp("reserved-all.yaml", manifest_all)
        p2 = self.run_cli("lint", path_all)
        self.assertEqual(p2.returncode, 1)
        self.assertIn("all", p2.stdout + p2.stderr)

    def test_self_promise_wrong_target_rejected(self):
        manifest = """agents:
  - id: research-agent
    role: literature summarizer
    promises:
      - id: self-commit
        type: self-promise
        target: coordinator
        body: Commit to quality checks on my own output.
  - id: coordinator
    role: human coordinator
    promises:
      - id: research-direction
        type: intent
        target: research-agent
        body: Provide research direction.
expectations:
  - id: exp-self-commit
    from: human
    about: self-commit
"""
        path = self.write_tmp("self-promise-bad.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("self-promise", combined)
        self.assertIn("coordinator", combined)

    def test_valid_self_promise_accepted(self):
        manifest = VALID_YAML.replace(
            "        body: Provide research direction and review summaries.\n",
            "        body: Provide research direction and review summaries.\n      - id: self-quality\n        type: self-promise\n        target: coordinator\n        body: Self-check my own output.\n",
        )
        path = self.write_tmp("self-promise-ok.yaml", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    # -- malformed / robustness ----------------------------------------------

    def test_malformed_yaml_no_traceback(self):
        path = self.write_tmp("malformed.yaml", MALFORMED_YAML)
        p = self.run_cli("lint", path)
        self.assertIn(p.returncode, (1, 2))
        self.assertNotIn("Traceback", p.stdout + p.stderr)
        self.assertNotIn("Traceback (most recent call last)", p.stderr)

    def test_blank_file_no_traceback(self):
        path = self.write_tmp("blank.yaml", "  \n\n  \n")
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("parse", (p.stdout + p.stderr).lower())

    def test_non_utf8_bytes_no_traceback(self):
        path = self.write_tmp("bad.bin", b"\xff\xfe" + b"agents:\n", binary=True)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("UnicodeDecodeError", p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_crlf_and_bom_accepted(self):
        src = VALID_YAML.encode("utf-8")
        crlf = self.write_tmp("crlf.yaml", src.replace(b"\n", b"\r\n"), binary=True)
        bom = self.write_tmp("bom.yaml", b"\xef\xbb\xbf" + src, binary=True)
        for path in (crlf, bom):
            p = self.run_cli("lint", path)
            self.assertEqual(p.returncode, 0, f"{path}: {p.stdout + p.stderr}")

    def test_json_type_errors_no_traceback(self):
        manifest = json.dumps(
            {
                "agents": [
                    {
                        "id": "research-agent",
                        "role": "literature summarizer",
                        "promises": [
                            {
                                "id": "lit-review",
                                "type": "capability",
                                "target": ["human"],
                                "body": 42,
                            }
                        ],
                    }
                ],
                "expectations": [{"id": "exp-lit-review", "from": "human", "about": "lit-review"}],
            }
        )
        path = self.write_tmp("type-error.json", manifest)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("TypeError", p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_deep_nesting_no_recursion_traceback(self):
        path = self.write_tmp("deep.json", "[" * 5000 + "0" + "]" * 5000)
        p = self.run_cli("lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("RecursionError", p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_missing_file_exits_2(self):
        p = self.run_cli("lint", os.path.join(self.tmpdir, "does-not-exist.yaml"))
        self.assertEqual(p.returncode, 2)
        self.assertIn("does-not-exist.yaml", p.stderr)

    def test_usage_errors_exit_2(self):
        cases = [
            ["frobnicate"],
            ["lint", "--bogus", self.valid_path],
            ["lint"],
            ["render"],
        ]
        for args in cases:
            p = self.run_cli(*args)
            self.assertEqual(p.returncode, 2, args)
            self.assertTrue(p.stderr.strip(), args)
            self.assertNotIn("Traceback", p.stderr)

    # -- --json / --dry-run / render ----------------------------------------

    def test_json_stdout_is_pure_json_on_failure(self):
        path = self.write_tmp("gap.yaml", VALID_YAML.replace("about: lit-review", "about: nope"))
        p = self.run_cli("lint", path, "--json")
        self.assertEqual(p.returncode, 1)
        data = json.loads(p.stdout)  # must parse: no prose on stdout
        self.assertIs(data["valid"], False)
        self.assertTrue(data["errors"])

    def test_dry_run_no_writes_and_same_output(self):
        normal = self.run_cli("lint", self.valid_path)
        dry = self.run_cli("lint", "--dry-run", self.valid_path)
        self.assertEqual(dry.returncode, 0)
        self.assertEqual(dry.stdout, normal.stdout)
        # lint is read-only: the fixture must be byte-identical afterwards
        with open(self.valid_path, "r", encoding="utf-8") as fh:
            self.assertEqual(fh.read(), VALID_YAML)

    def test_render_names_graph_entities(self):
        p = self.run_cli("render", self.valid_path)
        self.assertEqual(p.returncode, 0)
        for needle in ("research-agent", "coordinator", "lit-review", "research-direction"):
            self.assertIn(needle, p.stdout)

    def test_render_json_is_parseable(self):
        p = self.run_cli("render", self.valid_path, "--json")
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        agent_ids = {a["id"] for a in data["agents"]}
        promise_ids = {pr["id"] for pr in data["promises"]}
        self.assertEqual(agent_ids, {"research-agent", "coordinator"})
        self.assertEqual(promise_ids, {"lit-review", "research-direction"})
        binding_ids = {b["promise_id"] for b in data["bindings"]}
        self.assertEqual(binding_ids, {"lit-review", "research-direction"})

    def test_render_invalid_input_exits_1_no_traceback(self):
        bad = self.write_tmp("schema-bad.yaml", SCHEMA_BAD_YAML)
        p = self.run_cli("render", bad)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("Traceback", p.stdout + p.stderr)
        self.assertTrue(p.stderr.strip())


if __name__ == "__main__":
    unittest.main()
