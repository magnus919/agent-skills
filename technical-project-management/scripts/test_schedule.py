"""Hand-calculated networks, malformed-input boundaries, and CLI behavior."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("schedule.py")
spec = importlib.util.spec_from_file_location("tpm_schedule", SCRIPT)
schedule = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schedule)


def task(key, duration, deps=(), **extra):
    return {"id": key, "duration": duration, "depends_on": list(deps), **extra}


def network(tasks, **extra):
    return {"schema_version": 1, "unit": "working_days", "tasks": tasks, **extra}


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.data = network(
            [task("A", 2), task("B", 3, ["A"]), task("C", 1, ["A"]), task("D", 1, ["B", "C"])]
        )

    def test_diamond_float_and_deadline(self):
        self.data["deadline"] = 5
        result = schedule.analyze(self.data)
        self.assertEqual(result["finish"], 6)
        self.assertEqual(result["deadline_gap"], 1)
        self.assertEqual(result["critical_tasks"], ["A", "B", "D"])
        timings = {t["id"]: t for t in result["tasks"]}
        self.assertEqual(timings["C"]["total_float"], 2)
        self.assertEqual(timings["D"]["early_start"], 5)

    def test_tied_paths_and_disconnected_task(self):
        result = schedule.analyze(
            network([task("A", 2), task("B", 2), task("join", 0, ["A", "B"]), task("C", 1)])
        )
        self.assertEqual(result["critical_tasks"], ["A", "B", "join"])
        self.assertEqual(result["finish"], 2)
        self.assertIsNone(result["deadline_gap"])

    def test_resource_conflict_not_silently_leveled(self):
        result = schedule.analyze(
            network([task("A", 2, resource="engineer"), task("B", 3, resource="engineer")])
        )
        self.assertEqual(result["finish"], 3)
        self.assertEqual(result["resource_conflicts"][0]["overlap_finish"], 2)
        self.assertIn("not resource-leveled", result["warnings"][0])

    def test_conflict_output_is_bounded(self):
        result = schedule.analyze(network([task(str(i), 1, resource="r") for i in range(20)]))
        self.assertEqual(result["resource_conflict_count"], 190)
        self.assertEqual(len(result["resource_conflicts"]), 100)
        self.assertTrue(result["resource_conflicts_truncated"])

    def test_adjacent_and_zero_duration_do_not_conflict(self):
        result = schedule.analyze(
            network(
                [
                    task("A", 2, resource="r"),
                    task("B", 1, ["A"], resource="r"),
                    task("M", 0, resource="r"),
                ]
            )
        )
        self.assertEqual(result["resource_conflicts"], [])

    def test_order_independence_and_no_input_mutation(self):
        original = copy.deepcopy(self.data)
        first = schedule.analyze(self.data)
        self.assertEqual(self.data, original)
        self.data["tasks"].reverse()
        self.assertEqual(first, schedule.analyze(self.data))

    def test_float_durations(self):
        result = schedule.analyze(network([task("A", 0.1), task("B", 0.2, ["A"])]))
        self.assertAlmostEqual(result["finish"], 0.3)
        self.assertEqual(result["critical_tasks"], ["A", "B"])

    def test_invalid_durations(self):
        for value in [-1, True, "2", None, float("nan"), float("inf"), 10**400]:
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                schedule.analyze(network([task("A", value)]))

    def test_graph_errors(self):
        for tasks in [
            [],
            [task("A", 1), task("A", 2)],
            [task("A", 1, ["missing"])],
            [task("A", 1, ["A"])],
            [task("A", 1, ["B"]), task("B", 1, ["A"])],
            [task("A", 1), task("B", 1, ["A", "A"])],
        ]:
            with self.subTest(tasks=tasks), self.assertRaises(ValueError):
                schedule.analyze(network(tasks))

    def test_unknown_fields_and_malformed_types(self):
        samples = [
            None,
            [],
            network([None]),
            network([task("", 1)]),
            network([task("A", 1)], unit="days"),
            network([task("A", 1)], schema_version=True),
            network([task("A", 1)], deadline=True),
            network([task("A", 1)], calendar="holiday"),
            network([task("A", 1, lag=2)]),
            network([task("A", 1, resource="")]),
        ]
        for data in samples:
            with self.subTest(data=data), self.assertRaises(ValueError):
                schedule.analyze(data)

    def test_bounds(self):
        for data in [
            network([task(str(i), 1) for i in range(501)]),
            network([task("A", 600000), task("B", 600000)]),
        ]:
            with self.assertRaises(ValueError):
                schedule.analyze(data)

    def test_cycle_dependent_on_valid_root(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            schedule.analyze(
                network([task("root", 1), task("A", 1, ["root", "B"]), task("B", 1, ["A"])])
            )

    def test_cli_success_errors_and_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            for content, code in [
                (json.dumps(self.data), 0),
                ('{"tasks":[],"tasks":[]}', 2),
                ('{"x": NaN}', 2),
                ("not json", 2),
                ("[" * 1500, 2),
                (" " * (schedule.MAX_BYTES + 1), 2),
            ]:
                path.write_text(content)
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--input", str(path), "--json"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(path.read_text(), content)
                self.assertEqual(list(Path(folder).iterdir()), [path])
                if code == 0:
                    self.assertEqual(json.loads(result.stdout)["finish"], 6)
                    self.assertEqual(result.stderr, "")
                else:
                    self.assertEqual(result.stdout, "")
                    self.assertIn("error:", result.stderr)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(Path(folder) / "absent")],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
