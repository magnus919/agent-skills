"""Resource guard tests never call nvidia-smi or touch a GPU."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from sft_smoke import resource_gate


class GuardTests(unittest.TestCase):
    def gate(self, outputs, free=10 * 1024**3):
        with (
            patch("sft_smoke.shutil.disk_usage", return_value=SimpleNamespace(free=free)),
            patch("sft_smoke.subprocess.check_output", side_effect=outputs),
        ):
            return resource_gate(".", {123})

    def test_idle_existing_service_allowed(self):
        self.assertEqual(self.gate(["123\n", "# pmon\n0 123 C - - python\n", "0\n"]), 0)

    def test_active_existing_service_stops(self):
        with self.assertRaisesRegex(RuntimeError, "became active"):
            self.gate(["123\n", "0 123 C 12 2 python\n"])

    def test_new_job_stops(self):
        with self.assertRaisesRegex(RuntimeError, "new GPU process"):
            self.gate(["123\n999\n"])

    def test_own_job_is_allowed(self):
        self.assertEqual(self.gate([f"123\n{os.getpid()}\n", "0 123 C - - python\n", "80\n"]), 80)

    def test_disk_reserve_stops_before_gpu_queries(self):
        with self.assertRaisesRegex(RuntimeError, "disk reserve"):
            self.gate([], free=1024)


if __name__ == "__main__":
    unittest.main()
