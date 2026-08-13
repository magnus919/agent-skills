"""Unit tests for semantic-spacetime/scripts/semantic-spacetime.py.

Run from the repository root:

    python3 -m unittest discover -s semantic-spacetime/tests -p 'test_*.py'

The tests exercise the CLI black-box (subprocess) so they pin the observable
contract: exit codes (0 ok / 1 invalid model or input / 2 usage or IO),
stdout/stderr separation, --json single-object purity, --dry-run no-writes,
and the never-a-traceback rule. They also cover the sst-model-v1 template
contract (the delimited example lints clean) and the tracked sample fixture.

check-artifacts.py discovers this file with top_level_dir = the tests dir, so
skill-root paths are resolved via explicit sys.path handling below.
"""

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_ROOT)

SCRIPT = os.path.join(SKILL_ROOT, "scripts", "semantic-spacetime.py")
TEMPLATE_PATH = os.path.join(SKILL_ROOT, "templates", "sst-model.yaml.tmpl")
FIXTURE_PATH = os.path.join(SKILL_ROOT, "tests", "fixtures", "sample-model.yaml")
REPO_ROOT = os.path.dirname(SKILL_ROOT)

VALID_YAML = """schema_version: 1
agents:
  - id: operator
    role: workflow operator
    promises:
      - id: deliver-report
        body: Deliver the weekly status report by Friday.
        type: capability
        target: reviewer
  - id: reviewer
    role: semantic reviewer
    promises:
      - id: review-report
        body: Review the report for semantic drift.
        type: capability
        target: operator
nodes:
  - id: report-event
    type: event
  - id: report-thing
    type: thing
edges:
  - from: report-event
    to: report-thing
    link: 1
  - from: report-thing
    to: report-event
    link: 3
acceptances:
  - promise: deliver-report
    from: operator
    to: reviewer
"""

CYCLIC_YAML = """schema_version: 1
agents:
  - id: operator
    role: workflow operator
    promises:
      - id: deliver-report
        body: Deliver the weekly status report by Friday.
nodes:
  - id: a
    type: event
  - id: b
    type: thing
  - id: c
    type: concept
edges:
  - from: a
    to: b
    link: 1
  - from: b
    to: c
    link: 1
  - from: c
    to: a
    link: 1
  - from: a
    to: c
    link: 2
"""

DISCONNECTED_YAML = """schema_version: 1
agents:
  - id: operator
    role: workflow operator
    promises:
      - id: p1
        body: do something
nodes:
  - id: left-a
    type: event
  - id: left-b
    type: thing
  - id: right-x
    type: thing
edges:
  - from: left-a
    to: left-b
    link: 1
  - from: right-x
    to: left-a
    link: 3
"""

MALFORMED_YAML = """schema_version: 1
agents:
  - id: operator
    role: "unclosed quote
    promises:
"""


def _extract_template_example():
    """Extract the machine-delimited example block from the template.

    The block runs from the line exactly '# --- example ---' through the line
    exactly '# --- end example ---' (inclusive). The markers also appear in
    prose inside the template's FILLING GUIDE, so matching must be line-exact.
    """
    with open(TEMPLATE_PATH, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    start = end = None
    for i, line in enumerate(lines):
        if line.strip() == "# --- example ---":
            start = i
        elif line.strip() == "# --- end example ---":
            end = i
    assert start is not None and end is not None and start < end
    return "\n".join(lines[start:end + 1]) + "\n"


class SemanticSpacetimeCliTest(unittest.TestCase):
    """Black-box CLI tests for the sst-model-v1 tool."""

    def run_cli(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, SCRIPT, *args], capture_output=True, text=True, cwd=cwd
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

    def tearDown(self):
        self._tmp.cleanup()

    # -- basics (VAL-CLI-001) -------------------------------------------------

    def test_help_lists_all_subcommands_and_flags(self):
        p = self.run_cli("--help")
        self.assertEqual(p.returncode, 0)
        out = p.stdout.lower()
        for needle in (
            "model lint",
            "model map",
            "model distance",
            "model trajectory",
            "model drift",
            "--json",
            "--dry-run",
            "sst-model-v1",
        ):
            self.assertIn(needle, out)

    def test_version_is_dotted_triple(self):
        p = self.run_cli("--version")
        self.assertEqual(p.returncode, 0)
        self.assertRegex(p.stdout.strip(), r"^\d+\.\d+\.\d+$")

    def test_bare_invocation_exits_2_with_usage_on_stderr(self):
        p = self.run_cli()
        self.assertEqual(p.returncode, 2)
        self.assertEqual(p.stdout, "")
        self.assertIn("usage:", p.stderr.lower())
        self.assertNotIn("Traceback", p.stderr)

    # -- lint (VAL-CLI-002/003/013, VAL-CROSS-018) -----------------------------

    def test_valid_yaml_lints_clean_with_coverage(self):
        p = self.run_cli("model", "lint", self.valid_path)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        out = p.stdout.lower()
        self.assertIn("valid", out)
        self.assertIn("cover", out)
        self.assertIn("sst-model-v1", out)

    def test_lint_json_shape(self):
        p = self.run_cli("model", "lint", self.valid_path, "--json")
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        self.assertEqual(
            set(data), {"command", "schema_version", "valid", "errors", "coverage"}
        )
        self.assertIs(data["valid"], True)
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["schema_version"], "sst-model-v1")
        self.assertGreaterEqual(data["coverage"]["nodes"], 1)
        self.assertGreaterEqual(data["coverage"]["edges"], 1)

    def test_invalid_node_type_named_violation(self):
        bad = self.write_tmp(
            "bad-node.yaml",
            VALID_YAML.replace("type: event\n", "type: object\n", 1),
        )
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("report-event", combined)
        self.assertIn("object", combined)
        self.assertIn("event, thing, concept", combined)

    def test_invalid_link_value_named_violation(self):
        bad = self.write_tmp(
            "bad-link.yaml",
            VALID_YAML.replace("link: 1\n", "link: 5\n", 1),
        )
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("5", combined)
        self.assertIn("-3..3", combined)

    def test_dangling_edge_reference_named_violation(self):
        bad = self.write_tmp(
            "dangling-edge.yaml",
            VALID_YAML.replace("from: report-event\n", "from: ghost-node\n", 1),
        )
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("ghost-node", combined)
        self.assertIn("'from'", combined)

    def test_dangling_acceptance_named_violation(self):
        bad = self.write_tmp(
            "dangling-acceptance.yaml",
            VALID_YAML.replace(
                "promise: deliver-report\n", "promise: ghost-promise\n", 1
            ),
        )
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("ghost-promise", combined)

    def test_dangling_trajectory_named_violation(self):
        model = VALID_YAML + "\ntrajectories:\n  - id: t1\n    path: [report-event, ghost]\n"
        bad = self.write_tmp("dangling-trajectory.yaml", model)
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("ghost", combined)

    def test_violations_accumulate_all(self):
        model = VALID_YAML.replace("type: event\n", "type: object\n", 1).replace(
            "link: 1\n", "link: 9\n", 1
        )
        bad = self.write_tmp("multi-error.yaml", model)
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("object", combined)
        self.assertIn("9", combined)

    # -- template contract (VAL-CLI-012, VAL-CROSS-008, VAL-ROUTE-020) ---------

    def test_template_example_block_lints_clean(self):
        block = _extract_template_example()
        path = self.write_tmp("template-example.yaml", block)
        p = self.run_cli("model", "lint", path)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("valid", p.stdout.lower())
        self.assertIn("cover", p.stdout.lower())

    def test_sample_fixture_lints_clean_and_matches_template(self):
        with open(FIXTURE_PATH, encoding="utf-8") as fh:
            fixture_text = fh.read()
        self.assertEqual(fixture_text.strip(), _extract_template_example().strip())
        p = self.run_cli("model", "lint", FIXTURE_PATH)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p2 = self.run_cli("model", "lint", FIXTURE_PATH, "--json")
        data = json.loads(p2.stdout)
        self.assertIs(data["valid"], True)
        self.assertEqual(data["coverage"]["agents"], 2)
        self.assertEqual(data["coverage"]["nodes"], 3)
        self.assertEqual(data["coverage"]["edges"], 3)

    # -- JSON equivalence (VAL-CLI-021) ----------------------------------------

    def test_yaml_json_equivalence_byte_identical(self):
        with open(FIXTURE_PATH, encoding="utf-8") as fh:
            sample = fh.read()
        sample_json = json.dumps(
            {
                "schema_version": 1,
                "agents": [
                    {
                        "id": "operator",
                        "role": "workflow operator",
                        "promises": [
                            {
                                "id": "deliver-report",
                                "body": "Deliver the weekly status report by Friday.",
                                "type": "capability",
                                "target": "reviewer",
                            },
                            {
                                "id": "no-unverified-claims",
                                "body": "Never assert a claim without a measured source.",
                                "type": "constraint",
                                "target": "all",
                            },
                        ],
                    },
                    {
                        "id": "reviewer",
                        "role": "semantic reviewer",
                        "promises": [
                            {
                                "id": "review-report",
                                "body": "Review the report for semantic drift against the agreed vocabulary.",
                                "type": "capability",
                                "target": "operator",
                            }
                        ],
                    },
                ],
                "nodes": [
                    {"id": "report-event", "type": "event"},
                    {"id": "report-thing", "type": "thing"},
                    {"id": "drift-concept", "type": "concept"},
                ],
                "edges": [
                    {"from": "report-event", "to": "report-thing", "link": 1},
                    {"from": "report-thing", "to": "drift-concept", "link": 3},
                    {"from": "drift-concept", "to": "report-thing", "link": 2},
                ],
                "acceptances": [
                    {"promise": "deliver-report", "from": "operator", "to": "reviewer"}
                ],
                "trajectories": [
                    {
                        "id": "report-flow",
                        "path": ["report-event", "report-thing", "drift-concept"],
                        "label": "report moves from event to reviewed thing",
                    }
                ],
                "observations": [
                    {"at": "t1", "event": "report drafted", "changed": "report-event"},
                    {
                        "at": "t2",
                        "event": "reviewer flags drift in vocabulary",
                        "changed": "drift-concept",
                    },
                ],
            }
        )
        yaml_path = self.write_tmp("sample-as-yaml.yaml", sample)
        json_path = self.write_tmp("sample-as-json.json", sample_json)
        py = self.run_cli("model", "lint", yaml_path, "--json")
        pj = self.run_cli("model", "lint", json_path, "--json")
        self.assertEqual(py.returncode, 0)
        self.assertEqual(pj.returncode, 0)
        self.assertEqual(py.stdout, pj.stdout)
        self.assertEqual(json.loads(py.stdout), json.loads(pj.stdout))

    # -- restricted subset (VAL-CLI-021) ---------------------------------------

    def test_out_of_subset_anchor_rejected(self):
        bad = self.write_tmp("anchor.yaml", "schema_version: 1\nagents: &a\n  x: 1\n")
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        self.assertIn(bad, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_out_of_subset_block_scalar_rejected(self):
        bad = self.write_tmp("block.yaml", "schema_version: 1\nagents: |\n  x\n")
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        self.assertIn(bad, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_out_of_subset_multi_document_rejected(self):
        bad = self.write_tmp("multi.yaml", "---\nschema_version: 1\n")
        p = self.run_cli("model", "lint", bad)
        self.assertEqual(p.returncode, 1)
        self.assertIn(bad, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    # -- map (VAL-CLI-004) ------------------------------------------------------

    def test_map_text_names_nodes_and_edges_with_labels(self):
        p = self.run_cli("model", "map", self.valid_path, "--format", "text")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("report-event", p.stdout)
        self.assertIn("report-thing", p.stdout)
        self.assertIn("event", p.stdout)
        self.assertIn("thing", p.stdout)
        self.assertIn("leads-to", p.stdout.lower())
        self.assertIn("expresses", p.stdout.lower())

    def test_map_mermaid_is_graph_block(self):
        p = self.run_cli("model", "map", self.valid_path, "--format", "mermaid")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(p.stdout.startswith("graph"))
        self.assertIn("report-event", p.stdout)
        self.assertIn("report-thing", p.stdout)
        self.assertIn("LEADS TO", p.stdout)

    def test_map_json_is_single_object(self):
        p = self.run_cli("model", "map", self.valid_path, "--format", "json")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = json.loads(p.stdout)
        node_ids = {n["id"] for n in data["nodes"]}
        edge_pairs = {(e["from"], e["to"], e["link"]) for e in data["edges"]}
        self.assertEqual(node_ids, {"report-event", "report-thing"})
        self.assertIn(("report-event", "report-thing", 1), edge_pairs)
        self.assertIn(("report-thing", "report-event", 3), edge_pairs)

    def test_map_invalid_format_exits_2_naming_value(self):
        p = self.run_cli("model", "map", self.valid_path, "--format", "ascii-art")
        self.assertEqual(p.returncode, 2)
        self.assertIn("ascii-art", p.stderr)
        self.assertEqual(p.stdout, "")

    # -- distance (VAL-CLI-005/022) --------------------------------------------

    def test_distance_known_pair_is_deterministic_number(self):
        a = self.run_cli(
            "model", "distance", self.valid_path, "--from", "report-event", "--to", "report-thing"
        )
        b = self.run_cli(
            "model", "distance", self.valid_path, "--from", "report-event", "--to", "report-thing"
        )
        self.assertEqual(a.returncode, 0)
        self.assertEqual(a.stdout, b.stdout)
        match = [tok for tok in a.stdout.split() if tok.replace("-", "").isdigit()]
        self.assertTrue(match)

    def test_distance_json_has_numeric_distance(self):
        p = self.run_cli(
            "model",
            "distance",
            self.valid_path,
            "--from",
            "report-event",
            "--to",
            "report-thing",
            "--json",
        )
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = json.loads(p.stdout)
        self.assertIsInstance(data["distance"], int)
        self.assertEqual(data["path"], ["report-event", "report-thing"])

    def test_distance_missing_id_exits_1_naming_id(self):
        p = self.run_cli(
            "model", "distance", self.valid_path, "--from", "ghost", "--to", "report-thing"
        )
        self.assertEqual(p.returncode, 1)
        self.assertIn("ghost", p.stdout + p.stderr)

    def test_distance_missing_flags_exits_2(self):
        p = self.run_cli("model", "distance", self.valid_path)
        self.assertEqual(p.returncode, 2)
        self.assertIn("--from", p.stderr)

    def test_distance_no_path_exits_1_naming_both_ids(self):
        path = self.write_tmp("disconnected.yaml", DISCONNECTED_YAML)
        p = self.run_cli(
            "model", "distance", path, "--from", "left-a", "--to", "right-x"
        )
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("left-a", combined)
        self.assertIn("right-x", combined)

    # -- trajectory (VAL-CLI-006/023) ------------------------------------------

    def test_trajectory_enumerates_paths_with_link_types(self):
        # the sample fixture chains report-event -[1:leads-to]-> report-thing
        # -[3:expresses]-> drift-concept, so both link types appear on one path
        p = self.run_cli(
            "model", "trajectory", FIXTURE_PATH, "--from", "report-event", "--to", "drift-concept"
        )
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("report-event", p.stdout)
        self.assertIn("drift-concept", p.stdout)
        self.assertIn("leads-to", p.stdout)
        self.assertIn("expresses", p.stdout)

    def test_trajectory_unreachable_exits_1_naming_both(self):
        path = self.write_tmp("disconnected.yaml", DISCONNECTED_YAML)
        p = self.run_cli(
            "model", "trajectory", path, "--from", "left-a", "--to", "right-x"
        )
        self.assertEqual(p.returncode, 1)
        combined = p.stdout + p.stderr
        self.assertIn("left-a", combined)
        self.assertIn("right-x", combined)

    def test_trajectory_simple_paths_no_repeats_cycles_noted_stable(self):
        path = self.write_tmp("cyclic.yaml", CYCLIC_YAML)
        a = self.run_cli(
            "model", "trajectory", path, "--from", "a", "--to", "c"
        )
        b = self.run_cli(
            "model", "trajectory", path, "--from", "a", "--to", "c"
        )
        self.assertEqual(a.returncode, 0, a.stdout + a.stderr)
        self.assertEqual(a.stdout, b.stdout)
        self.assertIn("cycle detected", a.stdout)
        # JSON form: no listed path repeats a node; cycles are present.
        pj = self.run_cli(
            "model", "trajectory", path, "--from", "a", "--to", "c", "--json"
        )
        self.assertEqual(pj.returncode, 0)
        data = json.loads(pj.stdout)
        self.assertGreaterEqual(data["path_count"], 1)
        for entry in data["paths"]:
            nodes = entry["nodes"]
            self.assertEqual(len(nodes), len(set(nodes)), nodes)
            self.assertEqual(nodes[0], "a")
            self.assertEqual(nodes[-1], "c")
        self.assertTrue(data["cycles"])

    # -- drift (VAL-CLI-007) ----------------------------------------------------

    def test_drift_differing_snapshots_categorizes_regions(self):
        # snap-a: only-in-a node present; snap-b: only-in-b node present,
        # report-thing retyped thing -> concept, first edge link 1 -> 2, and
        # observation event changed -> added + removed + changed regions
        snap_a = VALID_YAML.replace(
            "edges:", "  - id: only-in-a\n    type: thing\nedges:", 1
        ) + "\nobservations:\n  - at: t1\n    event: started\n"
        snap_b = (
            VALID_YAML.replace("type: thing\n", "type: concept\n", 1)
            .replace("edges:", "  - id: only-in-b\n    type: event\nedges:", 1)
            .replace("link: 1\n", "link: 2\n", 1)
            + "\nobservations:\n  - at: t1\n    event: finished\n"
        )
        a_path = self.write_tmp("snap-a.yaml", snap_a)
        b_path = self.write_tmp("snap-b.yaml", snap_b)
        p = self.run_cli("model", "drift", a_path, b_path)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        out = p.stdout.lower()
        self.assertIn("added regions", out)
        self.assertIn("removed regions", out)
        self.assertIn("changed regions", out)
        self.assertIn("only-in-a", p.stdout)
        self.assertIn("only-in-b", p.stdout)
        self.assertIn("report-thing", p.stdout)
        self.assertIn("t1", p.stdout)

    def test_drift_identical_snapshots_no_drift(self):
        p = self.run_cli("model", "drift", self.valid_path, self.valid_path)
        self.assertEqual(p.returncode, 0)
        self.assertIn("no drift", p.stdout.lower())

    def test_drift_json_shape(self):
        a_path = self.write_tmp("snap-a.yaml", VALID_YAML)
        b_path = self.write_tmp(
            "snap-b.yaml", VALID_YAML.replace("link: 1\n", "link: 2\n", 1)
        )
        p = self.run_cli("model", "drift", a_path, b_path, "--json")
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        self.assertIn("drift", data)
        self.assertTrue(data["drift"])
        self.assertTrue(data["changed"])

    # -- --json purity (VAL-CLI-008/017) ----------------------------------------

    def test_json_purity_on_content_error(self):
        bad = self.write_tmp("bad.yaml", MALFORMED_YAML)
        p = self.run_cli("model", "lint", bad, "--json")
        self.assertIn(p.returncode, (1, 2))
        data = json.loads(p.stdout)  # must parse: no prose on stdout
        self.assertIs(data["valid"], False)
        self.assertTrue(data["errors"])
        self.assertEqual(p.stderr, "")

    def test_json_purity_on_io_error(self):
        missing = os.path.join(self.tmpdir, "does-not-exist.yaml")
        p = self.run_cli("model", "lint", missing, "--json")
        self.assertEqual(p.returncode, 2)
        data = json.loads(p.stdout)
        self.assertIs(data["valid"], False)
        self.assertTrue(data["errors"])
        self.assertIn("does-not-exist.yaml", data["errors"][0])
        self.assertEqual(p.stderr, "")

    def test_json_never_emitted_for_usage_errors(self):
        cases = [
            ["model", "frobnicate", "--json"],
            ["model", "lint", "--json"],
            ["frobnicate", "--json"],
            ["model", "map", self.valid_path, "--format", "ascii-art", "--json"],
        ]
        for args in cases:
            p = self.run_cli(*args)
            self.assertEqual(p.returncode, 2, args)
            self.assertEqual(p.stdout, "", args)
            self.assertTrue(p.stderr.strip(), args)
            self.assertNotIn("Traceback", p.stderr)

    def test_json_single_object_no_second_value(self):
        p = self.run_cli("model", "lint", self.valid_path, "--json")
        self.assertEqual(p.returncode, 0)
        text = p.stdout.strip()
        self.assertEqual(text.count("{"), text.count("}"))
        self.assertTrue(text.startswith("{"))
        self.assertTrue(text.endswith("}"))

    # -- --dry-run (VAL-CLI-009) ------------------------------------------------

    def test_dry_run_no_writes_and_identical_output(self):
        sentinel = os.path.join(self.tmpdir, "sentinel.txt")
        with open(sentinel, "w") as fh:
            fh.write("sentinel")
        before = sorted(os.listdir(self.tmpdir))
        normal = self.run_cli("model", "lint", self.valid_path)
        dry = self.run_cli("model", "lint", "--dry-run", self.valid_path)
        self.assertEqual(dry.returncode, normal.returncode)
        self.assertEqual(dry.stdout, normal.stdout)
        self.assertEqual(dry.stderr, normal.stderr)
        self.assertEqual(sorted(os.listdir(self.tmpdir)), before)
        with open(sentinel, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "sentinel")
        with open(self.valid_path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), VALID_YAML)
        # every subcommand accepts --dry-run and renders identically
        p = self.run_cli("model", "map", "--dry-run", self.valid_path, "--format", "text")
        self.assertEqual(p.returncode, 0)
        p = self.run_cli(
            "model", "distance", "--dry-run", self.valid_path, "--from", "report-event", "--to", "report-thing"
        )
        self.assertEqual(p.returncode, 0)

    # -- malformed input, never a traceback (VAL-CLI-010/016) -------------------

    def test_malformed_yaml_no_traceback(self):
        path = self.write_tmp("malformed.yaml", MALFORMED_YAML)
        p = self.run_cli("model", "lint", path)
        self.assertIn(p.returncode, (1, 2))
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_blank_file_exits_1_no_traceback(self):
        path = self.write_tmp("blank.yaml", "  \n\n  \n")
        p = self.run_cli("model", "lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("parse", (p.stdout + p.stderr).lower())

    def test_non_utf8_bytes_exits_1_no_traceback(self):
        path = self.write_tmp("bad.bin", b"\xff\xfe" + b"schema_version: 1\n", binary=True)
        p = self.run_cli("model", "lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("UnicodeDecodeError", p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_deep_nesting_no_recursion_traceback(self):
        path = self.write_tmp("deep.json", "[" * 5000 + "0" + "]" * 5000)
        p = self.run_cli("model", "lint", path)
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("RecursionError", p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    # -- IO and grammar taxonomy (VAL-CLI-016) ----------------------------------

    def test_missing_file_exits_2_naming_path(self):
        missing = os.path.join(self.tmpdir, "does-not-exist.yaml")
        p = self.run_cli("model", "lint", missing)
        self.assertEqual(p.returncode, 2)
        self.assertIn("does-not-exist.yaml", p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_unreadable_directory_exits_2(self):
        p = self.run_cli("model", "lint", self.tmpdir)
        self.assertEqual(p.returncode, 2)
        self.assertIn("read", p.stderr.lower())

    def test_usage_errors_exit_2_with_offending_token(self):
        cases = [
            (["model", "frobnicate"], "frobnicate"),
            (["model"], "subcommand"),
            (["lint", self.valid_path], "model"),
            (["model", "lint", "--bogus", self.valid_path], "--bogus"),
            (["model", "lint"], "file argument"),
            (["model", "distance", self.valid_path], "--from"),
            (["model", "lint", self.valid_path, "extra.yaml"], "extra.yaml"),
        ]
        for args, token in cases:
            p = self.run_cli(*args)
            self.assertEqual(p.returncode, 2, args)
            self.assertTrue(p.stderr.strip(), args)
            self.assertIn(token, p.stderr)
            self.assertNotIn("Traceback", p.stderr)

    # -- cwd independence and module import (VAL-CLI-018/019) -------------------

    def test_identical_behavior_from_any_cwd(self):
        fixture = FIXTURE_PATH
        outputs = []
        for cwd in (REPO_ROOT, SKILL_ROOT, self.tmpdir):
            p = self.run_cli("model", "lint", fixture, "--json", cwd=cwd)
            self.assertEqual(p.returncode, 0, p.stderr)
            outputs.append(p.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])

    def test_module_import_no_side_effects(self):
        code = (
            "import importlib.util, pathlib\n"
            f"s = pathlib.Path({SCRIPT!r})\n"
            "spec = importlib.util.spec_from_file_location('sst_cli', s)\n"
            "m = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(m)\n"
            "assert callable(getattr(m, 'main', None))\n"
            "assert getattr(m, 'SCHEMA_VERSION', None) == 'sst-model-v1'\n"
        )
        for cwd in (REPO_ROOT, self.tmpdir):
            p = subprocess.run(
                [sys.executable, "-c", code], capture_output=True, text=True, cwd=cwd
            )
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout, "")
            self.assertEqual(p.stderr, "")

    # -- stdlib-only / venv-independent (VAL-CLI-020) ---------------------------

    def test_stdlib_only_imports(self):
        with open(SCRIPT, encoding="utf-8") as fh:
            source = fh.read()
        tree = ast.parse(source)
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        self.assertTrue(roots)
        self.assertEqual(roots - set(sys.stdlib_module_names), set())

    def test_shebang_is_env_python3(self):
        with open(SCRIPT, encoding="utf-8") as fh:
            first_line = fh.readline().rstrip("\n")
        self.assertEqual(first_line, "#!/usr/bin/env python3")

    def test_runs_under_empty_env(self):
        env = {"HOME": "/tmp", "PATH": os.environ.get("PATH", "")}
        p = subprocess.run(
            ["env", "-i", "HOME=/tmp", f"PATH={env['PATH']}", "python3", SCRIPT, "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("model lint", p.stdout)

    # -- Quick Start walkthrough support (VAL-ROUTE-011/020) --------------------

    def test_quickstart_command_surface_runs_against_sample(self):
        commands = [
            ["model", "lint", FIXTURE_PATH],
            ["model", "map", FIXTURE_PATH, "--format", "text"],
            ["model", "map", FIXTURE_PATH, "--format", "mermaid"],
            ["model", "map", FIXTURE_PATH, "--format", "json"],
            ["model", "distance", FIXTURE_PATH, "--from", "report-event", "--to", "drift-concept"],
            ["model", "trajectory", FIXTURE_PATH, "--from", "report-event", "--to", "drift-concept"],
            ["model", "drift", FIXTURE_PATH, FIXTURE_PATH],
        ]
        for args in commands:
            p = self.run_cli(*args)
            self.assertEqual(p.returncode, 0, f"{args}: {p.stdout + p.stderr}")
            self.assertNotIn("Traceback", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
