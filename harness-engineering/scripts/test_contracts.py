"""Challenge declaration validity and comparable-record boundaries."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("contracts.py")
SPEC = importlib.util.spec_from_file_location("contracts", SCRIPT)
contracts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contracts)
TEMPLATES = SCRIPT.parents[1] / "templates"


def template(name):
    return json.loads((TEMPLATES / name).read_text())


def verified_state():
    d = template("state.json")
    d["candidate_revision"] = "rev-a"
    d["tasks"][0].update(
        status="verified",
        revision="rev-a",
        verification=[{"id": "a1", "claim": "search returns bounded page"}],
        evidence=[
            {
                "criterion_id": "a1",
                "revision": "rev-a",
                "outcome": "pass",
                "reference": "run/check-a",
            }
        ],
    )
    return d


class ContractTests(unittest.TestCase):
    def test_pending_template_is_not_verified(self):
        result = contracts.validate("state", template("state.json"))
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["details"]["verified_claims"], 0)
        self.assertEqual(result["behavior"], "not_assessed")

    def test_complete_declaration_valid_but_not_behavior(self):
        result = contracts.validate("state", verified_state())
        self.assertEqual(result["details"]["verified_claims"], 1)
        self.assertEqual(result["behavior"], "not_assessed")

    def test_missing_evidence_rejected(self):
        d = verified_state()
        d["tasks"][0]["evidence"] = []
        with self.assertRaisesRegex(ValueError, "passing evidence"):
            contracts.validate("state", d)

    def test_wrong_revision_rejected(self):
        d = verified_state()
        d["candidate_revision"] = "rev-b"
        with self.assertRaisesRegex(ValueError, "candidate revision"):
            contracts.validate("state", d)

    def test_unknown_and_failed_evidence_not_pass(self):
        for outcome in ["unknown", "fail"]:
            d = verified_state()
            d["tasks"][0]["evidence"][0]["outcome"] = outcome
            with self.assertRaises(ValueError):
                contracts.validate("state", d)

    def test_duplicate_task_rejected(self):
        d = verified_state()
        d["tasks"].append(copy.deepcopy(d["tasks"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            contracts.validate("state", d)

    def test_dependency_cycle_rejected(self):
        d = template("state.json")
        other = copy.deepcopy(d["tasks"][0])
        other["id"] = "task-2"
        other["dependencies"] = ["task-1"]
        d["tasks"][0]["dependencies"] = ["task-2"]
        d["tasks"].append(other)
        with self.assertRaisesRegex(ValueError, "cycle"):
            contracts.validate("state", d)

    def test_active_needs_owner(self):
        d = template("state.json")
        d["tasks"][0]["status"] = "active"
        with self.assertRaisesRegex(ValueError, "owner"):
            contracts.validate("state", d)

    def test_unverified_dependency_rejected(self):
        d = verified_state()
        other = copy.deepcopy(d["tasks"][0])
        other.update(id="task-2", status="pending", evidence=[])
        d["tasks"][0]["dependencies"] = ["task-2"]
        d["tasks"].append(other)
        with self.assertRaisesRegex(ValueError, "dependency"):
            contracts.validate("state", d)

    def test_duplicate_current_evidence_rejected(self):
        d = verified_state()
        other = copy.deepcopy(d["tasks"][0]["evidence"][0])
        other["outcome"] = "fail"
        d["tasks"][0]["evidence"].append(other)
        with self.assertRaisesRegex(ValueError, "duplicate current"):
            contracts.validate("state", d)

    def test_graph_template_valid_declaration(self):
        result = contracts.validate("graph", template("graph.json"))
        self.assertEqual(result["behavior"], "not_assessed")

    def test_unknown_cannot_take_pass_route(self):
        d = template("graph.json")
        d["nodes"][1]["routes"]["unknown"] = "complete"
        with self.assertRaisesRegex(ValueError, "pass route"):
            contracts.validate("graph", d)

    def test_in_memory_not_durable(self):
        d = template("graph.json")
        d["checkpoint_store"] = "in_memory"
        with self.assertRaisesRegex(ValueError, "durable"):
            contracts.validate("graph", d)

    def test_unbounded_loop_rejected(self):
        d = template("graph.json")
        del d["limits"]["max_attempts"]
        with self.assertRaisesRegex(ValueError, "max_attempts"):
            contracts.validate("graph", d)

    def test_unknown_node_rejected(self):
        d = template("graph.json")
        d["nodes"][0]["routes"]["blocked"] = "missing"
        with self.assertRaisesRegex(ValueError, "destinations"):
            contracts.validate("graph", d)

    def test_side_effect_requires_authority_and_reconciliation(self):
        d = template("graph.json")
        d["nodes"][0]["side_effects"] = True
        with self.assertRaisesRegex(ValueError, "authorization"):
            contracts.validate("graph", d)
        d["nodes"][0]["requires_authorization"] = True
        with self.assertRaisesRegex(ValueError, "reconciliation"):
            contracts.validate("graph", d)

    def test_comparison_refuses_changed_fingerprint(self):
        a, b = template("run-record.json"), template("run-record.json")
        b["fingerprints"]["model_config"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "fingerprints"):
            contracts.compare(a, b)

    def test_comparison_refuses_missing_case(self):
        a, b = template("run-record.json"), template("run-record.json")
        extra = copy.deepcopy(a["cases"][0])
        extra["id"] = "extra"
        a["cases"].append(extra)
        with self.assertRaisesRegex(ValueError, "case IDs"):
            contracts.compare(a, b)

    def test_comparison_refuses_changed_input(self):
        a, b = template("run-record.json"), template("run-record.json")
        b["cases"][0]["input_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "inputs"):
            contracts.compare(a, b)

    def test_comparison_flags_acceptance_regression(self):
        a, b = template("run-record.json"), template("run-record.json")
        a["cases"][0]["outcome"] = "accepted"
        b["cases"][0].update(outcome="unknown", elapsed_seconds=1)
        r = contracts.compare(a, b)
        self.assertTrue(r["rows"][0]["acceptance_regression"])
        self.assertEqual(r["release_approval"], "not_assessed")
        self.assertEqual(r["observed_candidate_accepted"], 0)

    def test_nonfinite_and_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            for payload in ['{"x": NaN}', '{"x":1,"x":2}']:
                p.write_text(payload)
                with self.assertRaises(ValueError):
                    contracts.load(p)

    def test_accepted_run_requires_reference(self):
        d = template("run-record.json")
        d["cases"][0].update(outcome="accepted", evidence_reference="")
        with self.assertRaisesRegex(ValueError, "evidence reference"):
            contracts.validate("run", d)

    def test_negative_cost_rejected(self):
        d = template("run-record.json")
        d["cases"][0]["cost"] = -1
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            contracts.validate("run", d)

    def test_cli_invalid_shape_reports_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text("[]")
            r = subprocess.run(
                [sys.executable, str(SCRIPT), "validate", "--kind", "state", "--file", str(p)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["contract_valid"])


class InterventionDetailTests(unittest.TestCase):
    def record(self):
        return template("run-record-with-interventions.json")

    def test_default_and_legacy_comparison_remain_unchanged(self):
        record = template("run-record.json")
        self.assertNotIn("intervention_detail", record["cases"][0])
        self.assertTrue(contracts.validate("run", record)["contract_valid"])
        before = contracts.compare(record, record)
        with_detail = copy.deepcopy(record)
        with_detail["cases"][0]["intervention_detail"] = {
            "coverage": "not_collected", "events": []
        }
        self.assertEqual(before, contracts.compare(record, with_detail))

    def test_example_counts_mixed_purposes_once_and_excludes_automation(self):
        record = self.record()
        self.assertTrue(contracts.validate("run", record)["contract_valid"])
        case = record["cases"][0]
        self.assertEqual(case["human_interventions"], 1)
        self.assertEqual(len(case["intervention_detail"]["events"]), 2)
        for count in (0, 2, 3):
            with self.subTest(count=count), self.assertRaises(ValueError):
                case["human_interventions"] = count
                contracts.validate("run", record)

    def test_partial_detail_requires_independently_known_total(self):
        record = self.record()
        case = record["cases"][0]
        case["human_interventions"] = 5
        case["intervention_detail"]["coverage"] = "partial"
        contracts.validate("run", record)
        case["human_interventions"] = 0
        with self.assertRaisesRegex(ValueError, "exceed"):
            contracts.validate("run", record)
        del case["human_interventions"]
        with self.assertRaises(ValueError):
            contracts.validate("run", record)

    def test_empty_detail_states_do_not_imply_zero_total(self):
        for coverage in ("not_collected", "partial"):
            record = self.record()
            case = record["cases"][0]
            case["human_interventions"] = 4
            case["intervention_detail"] = {"coverage": coverage, "events": []}
            contracts.validate("run", record)
        case["intervention_detail"]["coverage"] = "complete"
        with self.assertRaisesRegex(ValueError, "match"):
            contracts.validate("run", record)
        case["human_interventions"] = 0
        contracts.validate("run", record)

    def test_not_collected_rejects_events(self):
        record = self.record()
        record["cases"][0]["intervention_detail"]["coverage"] = "not_collected"
        with self.assertRaises(ValueError):
            contracts.validate("run", record)

    def test_extensible_kinds_and_unknown_changes_are_valid(self):
        record = self.record()
        event = record["cases"][0]["intervention_detail"]["events"][0]
        event["kinds"] = ["local:clarification"]
        event["changes"] = {"goal": None, "constraints": None, "authority": None}
        del event["target"]["workstream_id"]
        contracts.validate("run", record)

    def test_orchestrator_step_in_does_not_count_as_human(self):
        record = self.record()
        case = record["cases"][0]
        case["intervention_detail"]["events"][0]["actor"] = "orchestrator"
        case["human_interventions"] = 0
        contracts.validate("run", record)

    def test_duplicate_event_within_run_is_rejected_across_cases(self):
        record = self.record()
        second = copy.deepcopy(record["cases"][0])
        second["id"] = "other-case"
        record["cases"].append(second)
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            contracts.validate("run", record)
        for event in second["intervention_detail"]["events"]:
            event["target"]["run_id"] = "different-run"
        contracts.validate("run", record)

    def test_malformed_event_fields_fail_without_echoing_payloads(self):
        bad_fields = {
            "id": [None, "", "x" * 65, "raw human message"],
            "actor": [None, {}, "unknown"],
            "kinds": [[], "steering", [None], ["steering", "steering"]],
            "target": [None, {}, {"run_id": "r"}, {"run_id": "r", "task_id": " "}],
            "boundary_reference": [None, "", "x" * 257, "raw human message"],
            "changes": [None, {}, {"goal": 1, "constraints": False, "authority": False}],
            "outcome": [None, {}, "free form outcome"],
            "evidence_reference": [None, "", "line\nbreak", "control\x00character"],
        }
        for field, values in bad_fields.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    record = self.record()
                    record["cases"][0]["intervention_detail"]["events"][0][field] = value
                    with self.assertRaises(ValueError) as error:
                        contracts.validate("run", record)
                    self.assertNotIn("raw human message", str(error.exception))

    def test_raw_payload_and_undeclared_fields_are_rejected(self):
        for field in ("raw_message", "prompt", "hidden_reasoning", "comment"):
            record = self.record()
            detail = record["cases"][0]["intervention_detail"]
            for container in (detail, detail["events"][0], detail["events"][0]["target"], detail["events"][0]["changes"]):
                with self.subTest(field=field, container=list(container)):
                    container[field] = "sensitive message"
                    with self.assertRaises(ValueError):
                        contracts.validate("run", record)
                    del container[field]

    def test_invalid_detail_shapes_are_refused(self):
        for value in (None, [], {}, {"coverage": {}, "events": []},
                      {"coverage": "complete", "events": [None]},
                      {"coverage": "partial", "events": "text"}):
            with self.subTest(value=value):
                record = self.record()
                record["cases"][0]["intervention_detail"] = value
                with self.assertRaises(ValueError):
                    contracts.validate("run", record)

    def test_cli_validates_opt_in_example_and_refuses_inconsistent_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            record = self.record()
            for count, exit_code in ((1, 0), (2, 2)):
                record["cases"][0]["human_interventions"] = count
                path.write_text(json.dumps(record))
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "validate", "--kind", "run", "--file", str(path)],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["contract_valid"], exit_code == 0)


if __name__ == "__main__":
    unittest.main()
