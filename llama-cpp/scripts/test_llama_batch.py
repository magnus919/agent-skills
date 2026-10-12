"""No model or GPU is required; fixtures reproduce bad frontends and pipe floods."""

import contextlib
import io
import os
import signal
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from llama_batch import LaunchError, bounded_process, command_plan, environment, main, verify_gpu

HELP = " ".join(
    [
        "--no-conversation",
        "--no-display-prompt",
        "--no-escape",
        "--n-predict",
        "--ctx-size",
        "--gpu-layers",
        "--device",
        "--temp",
        "--seed",
        "--repeat-penalty",
        "--file",
        "--no-warmup",
        "--fit",
        "--verbose",
    ]
)


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.model = self.root / "model.gguf"
        self.model.write_bytes(b"GGUFfixture")
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_text("Reply RED")
        self.binary = self.root / "llama-completion"
        self.binary.write_text("#!/bin/sh\nexit 0\n")
        self.binary.chmod(0o700)

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_completion_never_loads_interactive_cli(self):
        self.binary.unlink()
        (self.root / "llama-cli").write_text("never execute me")
        with patch("llama_batch.bounded_process") as run:
            with self.assertRaisesRegex(LaunchError, "not a fallback"):
                command_plan(self.root, self.model, self.prompt, 16, 256)
            run.assert_not_called()

    def test_help_missing_required_option_stops_before_model(self):
        with (
            patch("llama_batch.bounded_process", return_value=["--gpu-layers", ""]),
            self.assertRaisesRegex(LaunchError, "lacks required"),
        ):
            command_plan(self.root, self.model, self.prompt, 16, 256)

    def test_gpu_absent_refuses_cpu_fallback(self):
        with (
            patch("llama_batch.bounded_process", side_effect=[[HELP, ""], ["CPU only", ""]]),
            self.assertRaisesRegex(LaunchError, "GPU-only"),
        ):
            command_plan(self.root, self.model, self.prompt, 16, 256)

    def test_plan_fixed_gpu_raw_completion(self):
        with patch(
            "llama_batch.bounded_process",
            side_effect=[[HELP, ""], ["CUDA0: RTX", ""], ["version pinned", ""]],
        ):
            plan = command_plan(self.root, self.model, self.prompt, 16, 256)
        self.assertEqual(plan["gpu_evidence"], "not_run")
        self.assertIn("--no-conversation", plan["argv"])
        self.assertIn("CUDA0", plan["argv"])
        self.assertIn("99", plan["argv"])

    def test_false_offload_is_not_gpu_success(self):
        for log in [
            "CUDA0 exists",
            "offloaded 0/29 layers to GPU",
            "offloaded 28/29 layers to GPU\nCUDA0 model buffer size = 1137 MiB",
        ]:
            with self.assertRaises(LaunchError):
                verify_gpu(log)

    def test_full_offload_and_buffer_evidence(self):
        self.assertEqual(
            verify_gpu("offloaded 29/29 layers to GPU\nCUDA0 model buffer size = 1137 MiB")[
                "offloaded_layers"
            ],
            29,
        )

    def test_environment_cannot_force_interactive_or_downloads(self):
        with patch.dict(
            os.environ,
            {
                "LLAMA_ARG_INTERACTIVE": "1",
                "LLAMA_ARG_HF_REPO": "secret/model",
                "LLAMA_LOG_DISABLE": "1",
                "HF_TOKEN": "secret",
                "CUDA_VISIBLE_DEVICES": "0",
            },
        ):
            env = environment()
            self.assertNotIn("HF_TOKEN", env)
            self.assertFalse(any(k.startswith("LLAMA_") for k in env))
            self.assertEqual(env["CUDA_VISIBLE_DEVICES"], "0")

    def test_output_flood_is_capped_before_accumulating(self):
        with self.assertRaisesRegex(LaunchError, "output limit"):
            bounded_process(
                [sys.executable, "-c", "import sys; sys.stdout.write('x'*1000000)"], 5, 1024
            )

    def test_saved_output_never_exceeds_combined_cap(self):
        with (
            (self.root / "out").open("wb") as out,
            (self.root / "err").open("wb") as err,
            self.assertRaisesRegex(LaunchError, "output limit"),
        ):
            bounded_process(
                [sys.executable, "-c", "import sys; sys.stderr.write('x'*1000000)"],
                5,
                1024,
                out,
                err,
            )
        self.assertLessEqual(
            (self.root / "out").stat().st_size + (self.root / "err").stat().st_size, 1024
        )

    def test_timeout_terminates_own_group(self):
        with patch("llama_batch.os.killpg", wraps=os.killpg) as kill:
            with self.assertRaisesRegex(LaunchError, "deadline"):
                bounded_process([sys.executable, "-c", "import time; time.sleep(30)"], 0.1, 1024)
            self.assertTrue(any(c.args[1] == signal.SIGKILL for c in kill.call_args_list))

    def test_stdin_eof(self):
        out, _ = bounded_process(
            [sys.executable, "-c", "import sys; print(len(sys.stdin.read()))"], 5, 1024
        )
        self.assertEqual(out, "0\n")

    def test_existing_output_is_never_overwritten(self):
        output = self.root / "existing"
        output.mkdir()
        (output / "report.json").write_text("original")
        args = [
            "run",
            "--bin-dir",
            str(self.root),
            "--model",
            str(self.model),
            "--prompt-file",
            str(self.prompt),
            "--output-dir",
            str(output),
        ]
        with (
            patch("llama_batch.command_plan", return_value={"argv": ["not run"]}),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(main(args), 1)
        self.assertEqual((output / "report.json").read_text(), "original")

    def test_nonzero_status(self):
        with self.assertRaisesRegex(LaunchError, "exited 3"):
            bounded_process([sys.executable, "-c", "raise SystemExit(3)"], 5, 1024)


if __name__ == "__main__":
    unittest.main()
