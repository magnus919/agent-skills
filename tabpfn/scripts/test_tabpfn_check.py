import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import tabpfn_check as check


def fixture():
    r = {
        "schema_version": 1,
        "task": "classification",
        "checkpoint": {
            "version": "explicit-version",
            "revision": "immutable-revision",
            "license_decision": "reviewed-example",
            "package_version": "pinned-example",
        },
        "capacity": {"max_train_rows": 10, "max_features": 2},
        "training_cutoff": "2026-01-01T00:00:00Z",
        "evaluation_cutoff": "2026-04-01T00:00:00Z",
        "splits": {},
    }
    for n, s in enumerate(("train", "calibration", "test")):
        r["splits"][s] = [
            {
                "id": s + str(i),
                "group_id": s + str(i),
                "features": [n * 10 + i, None],
                "target": i,
                "prediction_time": "2025-12-01T00:00:00Z"
                if s == "train"
                else "2026-02-01T00:00:00Z",
                "feature_available_time": "2025-11-01T00:00:00Z",
                "label_available_time": "2025-12-20T00:00:00Z"
                if s == "train"
                else "2026-03-01T00:00:00Z",
            }
            for i in (0, 1)
        ]
    return r


class Tests(unittest.TestCase):
    def test_clear_is_not_runtime_or_license_verification(self):
        r = check.audit(fixture())
        self.assertTrue(r["checks_clear"])
        self.assertEqual(r["runtime"], "not_run")
        self.assertEqual(r["license"], "not_verified")

    def test_leakage(self):
        r = fixture()
        r["splits"]["test"][0].update(id="train0", group_id="train0", features=[0, None])
        codes = {f["code"] for f in check.audit(r)["findings"]}
        self.assertTrue({"duplicate_id", "group_leakage", "exact_feature_overlap"} <= codes)

    def test_future_and_immature(self):
        r = fixture()
        r["splits"]["train"][0].update(
            feature_available_time="2026-02-01T00:00:00Z",
            label_available_time="2026-05-01T00:00:00Z",
        )
        codes = {f["code"] for f in check.audit(r)["findings"]}
        self.assertTrue({"future_feature", "immature_label"} <= codes)

    def test_limits_and_unknown_class(self):
        r = fixture()
        r["capacity"]["max_train_rows"] = 1
        r["capacity"]["max_features"] = 1
        r["splits"]["test"][0]["target"] = "unknown"
        codes = {f["code"] for f in check.audit(r)["findings"]}
        self.assertTrue({"row_capacity", "feature_capacity", "unseen_class"} <= codes)

    def test_invalid_contract_and_time(self):
        for change in (
            lambda r: r.update(schema_version=True),
            lambda r: r["splits"].update(test=[]),
            lambda r: r.update(training_cutoff="2026-01-01"),
            lambda r: r["splits"]["test"][0].update(features=[float("nan"), 0]),
        ):
            r = fixture()
            change(r)
            with self.assertRaises(ValueError):
                check.audit(r)

    def test_cli_privacy_and_python_optimized(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "input.json"
            r = fixture()
            r["splits"]["test"][0]["group_id"] = "private-name"
            r["splits"]["test"][0]["target"] = "unseen"
            p.write_text(json.dumps(r))
            x = subprocess.run(
                [sys.executable, "-O", check.__file__, "audit", str(p)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(x.returncode, 1)
            self.assertNotIn("private-name", x.stdout + x.stderr)


if __name__ == "__main__":
    unittest.main()
