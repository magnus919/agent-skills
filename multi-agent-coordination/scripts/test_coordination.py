"""Adverse declaration tests; no service or model calls."""

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("coordination", ROOT / "scripts/coordination.py")
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "templates/team-snapshot.json").read_text())
        self.task = self.data["tasks"][1]

    def codes(self):
        return {row["code"] for row in c.audit(self.data)["findings"]}

    def test_example_is_declaration_only(self):
        report = c.audit(self.data)
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["runtime_acceptance"], "not_assessed")

    def test_expiry_boundary(self):
        self.task["claims"][0]["expires_at"] = self.data["as_of"]
        self.assertIn("expired_claim", self.codes())

    def test_timezone_equivalence(self):
        self.task["claims"][0]["expires_at"] = "2026-11-01T19:00:00-05:00"
        self.assertIn("expired_claim", self.codes())

    def test_stale_intent(self):
        self.task["intent_version"] = "v1"
        self.assertIn("stale_intent", self.codes())

    def test_terminal_history_not_current_claim(self):
        self.task.update(status="accepted", intent_version="v1", claims=[])
        self.assertEqual(self.codes(), set())

    def test_multiple_claims_and_owner_mismatch(self):
        other = copy.deepcopy(self.task["claims"][0])
        other.update(seat="integrator", execution="integration-run-1")
        self.task["claims"].append(other)
        self.assertTrue({"multiple_claims", "claim_owner_mismatch"} <= self.codes())

    def test_old_occupant(self):
        self.task["claims"][0]["execution"] = "build-run-1"
        self.assertIn("obsolete_occupant", self.codes())

    def test_missing_claim(self):
        self.task["claims"] = []
        self.assertIn("missing_claim", self.codes())

    def test_blocked_continuation(self):
        self.task["status"] = "blocked"
        self.assertIn("missing_continuation", self.codes())
        self.task["continuation"] = {
            "blocker": "decision-1",
            "wake": "on owner decision",
            "owner": "integrator",
        }
        self.assertNotIn("missing_continuation", self.codes())

    def test_unaccepted_prerequisite(self):
        self.data["tasks"][0]["status"] = "queued"
        self.assertIn("unaccepted_prerequisite", self.codes())
        self.task["status"] = "blocked"
        self.assertNotIn("unaccepted_prerequisite", self.codes())

    def test_cycle_and_downstream_are_labeled_honestly(self):
        self.data["tasks"][0]["depends_on"] = ["contract"]
        finding = c.audit(self.data)["findings"][0]
        self.assertEqual(finding["code"], "dependency_cycle_or_downstream")
        self.assertEqual(finding["tasks"], ["contract", "export"])

    def test_dangling_reference_rejected(self):
        self.task["depends_on"] = ["missing"]
        with self.assertRaises(c.InputError):
            c.audit(self.data)

    def test_duplicate_ids_rejected(self):
        self.data["seats"].append(copy.deepcopy(self.data["seats"][0]))
        with self.assertRaises(c.InputError):
            c.audit(self.data)

    def test_invalid_types_and_schema(self):
        changes = [
            lambda d: d.update(schema_version=True),
            lambda d: d.update(as_of="2026-11-02T00:00:00"),
            lambda d: d["tasks"][1].update(status="done-ish"),
            lambda d: d["tasks"][1]["claims"][0].update(epoch=True),
            lambda d: d["tasks"][1].update(continuation={"owner": "builder"}),
            lambda d: d.update(extra="unexpected"),
            lambda d: d["tasks"][1].update(depends_on=["contract", "contract"]),
        ]
        for change in changes:
            with self.subTest(change=change):
                data = copy.deepcopy(self.data)
                change(data)
                with self.assertRaises(c.InputError):
                    c.audit(data)

    def test_exposure_transitive_and_unknown(self):
        report = c.exposure(self.data, "lesson-old")
        self.assertEqual(report["reachable"], ["builder-context", "role-recap"])
        self.assertEqual(report["consumers"], ["builder-context"])
        self.assertEqual(report["coverage"], "unknown")

    def test_exposure_cycle_terminates_and_excludes_origin(self):
        self.data["edges"].append({"source": "builder-context", "target": "lesson-old"})
        report = c.exposure(self.data, "lesson-old")
        self.assertNotIn("lesson-old", report["reachable"])
        self.assertEqual(len(report["reachable"]), 2)

    def test_disconnected_and_missing_source(self):
        self.data["edges"] = []
        self.assertEqual(c.exposure(self.data, "lesson-old")["consumers"], [])
        with self.assertRaises(c.InputError):
            c.exposure(self.data, "absent")

    def test_bad_edge(self):
        self.data["edges"][0]["target"] = "absent"
        with self.assertRaises(c.InputError):
            c.exposure(self.data, "lesson-old")

    def invoke(self, payload, *args):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_bytes(payload)
            before = path.read_bytes()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = c.main(["audit", "--file", str(path), "--json", *args])
            self.assertEqual(path.read_bytes(), before)
            return code, json.loads(output.getvalue())

    def test_cli_no_writes_and_exit_codes(self):
        code, report = self.invoke(json.dumps(self.data).encode(), "--dry-run")
        self.assertEqual(code, 0)
        self.task["claims"] = []
        code, report = self.invoke(json.dumps(self.data).encode())
        self.assertEqual(code, 1)
        self.assertTrue(report["findings"])

    def test_cli_malformed_bounded_errors(self):
        for payload in [
            b"{",
            b"[]",
            b'{"x":1,"x":2}',
            b'{"x":NaN}',
            b'{"x":1e999}',
            b"\xff",
            b" " * (c.MAX_BYTES + 1),
        ]:
            with self.subTest(payload=payload[:15]):
                code, report = self.invoke(payload)
                self.assertEqual(code, 2)
                self.assertIn("error", report)

    def test_cli_wrong_source_argument(self):
        code, report = self.invoke(json.dumps(self.data).encode(), "--source", "lesson-old")
        self.assertIn("error", report)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
