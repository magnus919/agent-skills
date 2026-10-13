import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import audit_sequence_windows as audit


def fixture():
    windows = []
    for i, split in enumerate(("train", "development", "test")):
        date = ["2025-12-01", "2026-02-01", "2026-03-01"][i]
        windows.append(
            {
                "id": split,
                "target_id": split + "target",
                "entity_id": "customer",
                "split": split,
                "prediction_time": date + "T00:00:00Z",
                "label_available_time": date + "T01:00:00Z",
                "events": [
                    {
                        "id": "shared-past",
                        "entity_id": "customer",
                        "event_time": "2025-11-01T00:00:00Z",
                        "available_time": "2025-11-01T01:00:00Z",
                        "contains_outcome": False,
                    }
                ],
            }
        )
    return {
        "schema_version": 1,
        "split_mode": "forward",
        "training_cutoff": "2026-01-01T00:00:00Z",
        "evaluation_cutoff": "2026-04-01T00:00:00Z",
        "windows": windows,
    }


class Tests(unittest.TestCase):
    def test_shared_past_context_is_not_automatic_leakage(self):
        r = audit.audit(fixture())
        self.assertTrue(r["checks_clear"])
        self.assertEqual(r["semantic_feature_leakage"], "not_assessed")

    def test_future_outcome_and_target(self):
        r = fixture()
        e = r["windows"][0]["events"][0]
        e.update(id="traintarget", available_time="2026-01-01T00:00:00Z", contains_outcome=True)
        self.assertTrue(
            {"future_context", "outcome_in_context_or_unreviewed", "self_in_history"}
            <= {f["code"] for f in audit.audit(r)["findings"]}
        )

    def test_holdout_groups(self):
        r = fixture()
        r["split_mode"] = "entity_holdout"
        self.assertIn("entity_leakage", {f["code"] for f in audit.audit(r)["findings"]})

    def test_boundaries_and_maturity(self):
        r = fixture()
        r["windows"][1]["prediction_time"] = "2026-03-02T00:00:00Z"
        r["windows"][0]["label_available_time"] = "2026-04-02T00:00:00Z"
        self.assertTrue(
            {"fold_boundary_overlap", "immature_label"}
            <= {f["code"] for f in audit.audit(r)["findings"]}
        )

    def test_identity_and_empty_or_naive_time(self):
        for change in (
            lambda r: r["windows"][0].update(events=[]),
            lambda r: r.update(training_cutoff="2026-01-01"),
            lambda r: r.update(schema_version=True),
        ):
            r = fixture()
            change(r)
            with self.assertRaises(ValueError):
                audit.audit(r)
        r = fixture()
        r["windows"][1]["events"][0]["entity_id"] = "wrong"
        self.assertIn("event_identity_changed", {f["code"] for f in audit.audit(r)["findings"]})

    def test_private_identifiers_not_printed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "windows.json"
            r = fixture()
            r["windows"][0]["id"] = "secret-id"
            r["windows"][0]["events"][0]["contains_outcome"] = True
            p.write_text(json.dumps(r))
            x = subprocess.run(
                [sys.executable, "-O", audit.__file__, str(p)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(x.returncode, 1)
            self.assertNotIn("secret-id", x.stdout)


if __name__ == "__main__":
    unittest.main()
