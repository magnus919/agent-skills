#!/usr/bin/env python3
"""Plan or run bounded GPU-only raw completion with llama-completion (POSIX)."""

import argparse
import contextlib
import hashlib
import json
import os
import re
import selectors
import signal
import subprocess
import time
from pathlib import Path


class LaunchError(RuntimeError):
    pass


def environment():
    # Caller defaults must not enable interactive mode, downloads, or hide logs.
    return {k: v for k, v in os.environ.items() if not k.startswith("LLAMA_") and k != "HF_TOKEN"}


def bounded_process(argv, timeout, byte_limit, stdout_file=None, stderr_file=None):
    """Cap combined pipe bytes before accumulating or writing; clean child group."""
    process = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment(),
        start_new_session=True,
    )
    outputs = [bytearray(), bytearray()]
    count = 0
    start = time.monotonic()
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ, 0)
        selector.register(process.stderr, selectors.EVENT_READ, 1)
        try:
            while selector.get_map() or process.poll() is None:
                if time.monotonic() - start > timeout:
                    raise LaunchError("runtime deadline exceeded")
                for key, _ in selector.select(timeout=min(0.05, timeout)):
                    chunk = os.read(key.fileobj.fileno(), 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    remaining = byte_limit - count
                    keep = chunk[: max(0, remaining)]
                    count += len(keep)
                    index = key.data
                    target = stdout_file if index == 0 else stderr_file
                    if target is None:
                        outputs[index].extend(keep)
                    else:
                        target.write(keep)
                        target.flush()
                    if len(chunk) > len(keep):
                        raise LaunchError("combined runtime output limit exceeded")
            if process.returncode:
                raise LaunchError(f"runtime exited {process.returncode}")
        finally:
            # Parent may exit while a descendant retains a pipe. Kill only our group.
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGTERM)
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=2)
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            process.stdout.close()
            process.stderr.close()
    return [bytes(output).decode("utf-8", errors="replace") for output in outputs]


def command_plan(bin_dir, model, prompt, max_tokens, context):
    if os.name != "posix":
        raise LaunchError("bounded launcher requires POSIX process groups")
    binary = bin_dir / "llama-completion"
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise LaunchError(
            "llama-completion is missing; build/install the pinned completion target. Interactive llama-cli is not a fallback."
        )
    if not model.is_file() or model.open("rb").read(4) != b"GGUF":
        raise LaunchError("a local GGUF model is required; downloads are not performed")
    if not prompt.is_file() or prompt.stat().st_size > 1024 * 1024:
        raise LaunchError("a local prompt file of at most 1 MiB is required")
    help_text = "\n".join(bounded_process([str(binary), "--help"], 5, 256 * 1024))
    required = [
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
        "--verbose",
    ]
    missing = [flag for flag in required if flag not in help_text]
    if missing:
        raise LaunchError("installed completion help lacks required flags: " + ", ".join(missing))
    devices = "\n".join(bounded_process([str(binary), "--list-devices"], 5, 256 * 1024))
    if not re.search(r"\bCUDA0\b", devices):
        raise LaunchError("CUDA0 not listed; GPU-only launch refused")
    version = "\n".join(bounded_process([str(binary), "--version"], 5, 256 * 1024)).strip()
    argv = [
        str(binary),
        "-m",
        str(model),
        "-f",
        str(prompt),
        "--no-conversation",
        "--no-display-prompt",
        "--no-escape",
        "--no-warmup",
        "--verbose",
        "-n",
        str(max_tokens),
        "-c",
        str(context),
        "--temp",
        "0",
        "--seed",
        "3407",
        "--repeat-penalty",
        "1",
        "--device",
        "CUDA0",
        "--gpu-layers",
        "99",
        "-t",
        "2",
        "-tb",
        "2",
    ]
    if "--fit" in help_text:
        argv.extend(["--fit", "off"])
    return {
        "schema_version": 1,
        "status": "ready",
        "version": version,
        "binary": str(binary),
        "argv": argv,
        "gpu_evidence": "not_run",
        "sampling": {"greedy": True, "max_tokens": max_tokens},
        "help_sha256": hashlib.sha256(help_text.encode()).hexdigest(),
    }


def verify_gpu(stderr):
    layers = re.search(r"offloaded (\d+)/(\d+) layers to GPU", stderr)
    buffer = re.search(r"CUDA0\s+model buffer size\s*=\s*([\d.]+)\s*MiB", stderr)
    if (
        not layers
        or not buffer
        or int(layers[1]) <= 0
        or layers[1] != layers[2]
        or float(buffer[1]) <= 0
    ):
        raise LaunchError("full CUDA0 model placement not observed; do not claim GPU success")
    return {
        "offloaded_layers": int(layers[1]),
        "total_layers": int(layers[2]),
        "model_buffer_mib": float(buffer[1]),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["plan", "run"])
    p.add_argument("--bin-dir", type=Path, required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--output-dir", type=Path)
    p.add_argument("--max-tokens", type=int, default=16)
    p.add_argument("--context", type=int, default=256)
    p.add_argument("--timeout", type=float, default=60)
    p.add_argument("--output-bytes", type=int, default=1024 * 1024)
    args = p.parse_args(argv)
    if not (
        1 <= args.max_tokens <= 1024
        and args.max_tokens < args.context <= 32768
        and 0 < args.timeout <= 600
        and 1024 <= args.output_bytes <= 16 * 1024 * 1024
    ):
        p.error("invalid bounded token/context/time/output budget")
    report = {}
    output = None
    created = False
    try:
        report = command_plan(
            args.bin_dir.resolve(),
            args.model.resolve(),
            args.prompt_file.resolve(),
            args.max_tokens,
            args.context,
        )
        if args.command == "run":
            if args.output_dir is None:
                p.error("--output-dir is required for run")
            output = args.output_dir.resolve()
            output.mkdir(mode=0o700, parents=True, exist_ok=False)
            created = True
            report.update(
                status="running",
                deadline_seconds=args.timeout,
                combined_output_byte_limit=args.output_bytes,
            )
            started = time.monotonic()
            with (
                (output / "stdout.txt").open("xb") as out,
                (output / "stderr.txt").open("xb") as err,
            ):
                bounded_process(report["argv"], args.timeout, args.output_bytes, out, err)
            report["gpu_evidence"] = verify_gpu((output / "stderr.txt").read_text(errors="replace"))
            report.update(
                status="completed",
                seconds=time.monotonic() - started,
                semantic_quality="not_assessed",
            )
    except (LaunchError, OSError) as error:
        report.update(status="failed", error=str(error))
        print(json.dumps(report, indent=2))
        if created:
            (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        return 1
    if output is not None:
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
