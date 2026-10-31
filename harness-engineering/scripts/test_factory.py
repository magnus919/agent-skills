"""Adversarial declaration and CLI checks, not agent effectiveness tests."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("factory.py")
spec = importlib.util.spec_from_file_location("factory_screen", SCRIPT)
factory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(factory)


class FactoryTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(
            (SCRIPT.parent.parent / "templates/factory-snapshot.json").read_text()
        )

    def test_transitive_impact_preserves_unaffected_candidate(self):
        report = factory.reconcile(self.data)
        self.assertEqual(report["affected_tasks"], ["contract", "export", "verify"])
        self.assertEqual(report["completed_candidates_for_review"], ["docs"])
        self.assertEqual(report["behavior"], "not_assessed")
        self.assertEqual(report["release_acceptance"], "not_assessed")

    def test_late_artifact_not_cured_by_new_ack(self):
        task = self.data["tasks"][0]
        task.update(worker_revision="v2", ack_revision="v2")
        self.data["changed_tasks"] = []
        report = factory.reconcile(self.data)
        self.assertIn(
            "artifact_revision_mismatch", report["tasks_requiring_disposition"]["contract"]
        )
        self.assertNotIn("verify", report["completed_candidates_for_review"])

    def test_missing_ack_and_expired_lease(self):
        task = self.data["tasks"][3]
        task.update(status="running", ack_revision=None, lease_expires_at=100)
        reasons = factory.reconcile(self.data)["tasks_requiring_disposition"]["docs"]
        self.assertIn("current_revision_not_acknowledged", reasons)
        self.assertIn("lease_expired_reconcile_effects_before_reassignment", reasons)

    def test_cancelled_upstream_blocks_consumer(self):
        self.data["tasks"][1]["status"] = "cancelled"
        report = factory.reconcile(self.data)
        self.assertIn(
            "dependency_unresolved:export", report["tasks_requiring_disposition"]["verify"]
        )

    def test_budget_reservations_and_exhaustion(self):
        self.data["budget"]["reserved"] = 6
        self.assertFalse(factory.reconcile(self.data)["new_dispatch_budget_available"])
        self.data["budget"]["reserved"] = 7
        self.assertTrue(factory.reconcile(self.data)["budget_reconciliation_required"])

    def test_extreme_budget_values_fail_cleanly(self):
        for limit, spent, reserved in [(10**1000, 0, 0), (1, 1e308, 1e308)]:
            self.data["budget"] = {"limit": limit, "spent": spent, "reserved": reserved}
            with self.subTest(limit=limit), self.assertRaises(factory.InvalidSnapshot):
                factory.reconcile(self.data)

    def test_multiple_node_cycle_and_duplicate_change_rejected(self):
        self.data["tasks"][0]["dependency_versions"] = {"verify": "v1"}
        with self.assertRaises(factory.InvalidSnapshot):
            factory.reconcile(self.data)
        self.setUp()
        self.data["changed_tasks"] = ["contract", "contract"]
        with self.assertRaises(factory.InvalidSnapshot):
            factory.reconcile(self.data)

    def test_no_input_mutation(self):
        original = copy.deepcopy(self.data)
        factory.reconcile(self.data)
        self.assertEqual(self.data, original)

    def test_bad_shapes_and_cycles_rejected(self):
        variants = []
        for key, value in [
            ("tasks", []),
            ("schema_version", True),
            ("as_of", float("nan")),
            ("changed_tasks", ["missing"]),
        ]:
            data = copy.deepcopy(self.data)
            data[key] = value
            variants.append(data)
        for key, value in [
            ("status", "done"),
            ("id", ""),
            ("dependency_versions", {"missing": "v1"}),
            ("dependency_versions", {"contract": "v1"}),
        ]:
            data = copy.deepcopy(self.data)
            data["tasks"][0][key] = value
            variants.append(data)
        data = copy.deepcopy(self.data)
        data["tasks"].append(copy.deepcopy(data["tasks"][0]))
        variants.append(data)
        data = copy.deepcopy(self.data)
        data["budget"]["limit"] = True
        variants.append(data)
        for data in variants:
            with self.subTest(data=data), self.assertRaises(factory.InvalidSnapshot):
                factory.reconcile(data)

    def test_cli_json_and_malformed_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(self.data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--snapshot", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                json.loads(result.stdout)["affected_tasks"], ["contract", "export", "verify"]
            )
            self.assertEqual(json.loads(path.read_text()), self.data)
            path.write_text('{"tasks":')
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--snapshot", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("error", json.loads(result.stderr))
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
