#!/usr/bin/env python3
"""Compare fresh merged-HF or llama.cpp GGUF outputs to the saved candidate."""

import argparse
import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path

from sft_audit import score
from sft_smoke import resource_gate


def bounded_command(command, stdout_path, stderr_path, timeout=60, max_bytes=1024 * 1024):
    """File-backed output, EOF stdin, process-group cleanup, bounded wall time."""
    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True
        )
        deadline = time.monotonic() + timeout
        try:
            while process.poll() is None:
                if stdout_path.stat().st_size + stderr_path.stat().st_size > max_bytes:
                    raise RuntimeError("runtime output limit exceeded; inspect retained files")
                if time.monotonic() > deadline:
                    raise TimeoutError("runtime deadline exceeded")
                time.sleep(0.05)
            if process.returncode:
                raise RuntimeError(f"runtime exited {process.returncode}; inspect retained stderr")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
    if stdout_path.stat().st_size + stderr_path.stat().st_size > max_bytes:
        raise RuntimeError("runtime output limit exceeded")
    return stdout_path.read_text(errors="replace")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("runtime", choices=["hf", "llama"])
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument(
        "--gpu-completion", type=Path, help="GPU-only harness built from scripts/gpu_completion.cpp"
    )
    args = p.parse_args()
    root = args.run_dir.resolve()
    config = json.loads((root / "smoke-config.json").read_text())
    allowed = set(config["existing_gpu_pids"])
    if resource_gate(root, allowed) > 5:
        raise RuntimeError("existing GPU workload active")
    candidate = json.loads((root / "candidate.json").read_text())
    start = time.monotonic()
    cases = []
    if args.runtime == "hf":
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(root / "merged", local_files_only=True)
        model = (
            AutoModelForCausalLM.from_pretrained(
                root / "merged", local_files_only=True, dtype=torch.bfloat16
            )
            .to("cuda")
            .eval()
        )
    for row in candidate["cases"]:
        resource_gate(root, allowed)
        if args.runtime == "hf":
            inputs = tokenizer(row["prompt"], add_special_tokens=False, return_tensors="pt").to(
                "cuda"
            )
            with torch.inference_mode():
                output = model.generate(
                    **inputs, **candidate["decoding"], pad_token_id=tokenizer.pad_token_id
                )
            ids = output[0, inputs["input_ids"].shape[1] :].tolist()
            text = tokenizer.decode(ids, skip_special_tokens=True)
            terminated = ids[-1] == tokenizer.eos_token_id
            raw = text
        else:
            if not args.gpu_completion:
                p.error("--gpu-completion is required for llama")
            promptfile = root / f"{row['id']}-prompt.txt"
            promptfile.write_text(row["prompt"])
            command = [
                str(args.gpu_completion),
                str(root / "candidate-f16.gguf"),
                str(promptfile),
                str(candidate["decoding"]["max_new_tokens"]),
            ]
            raw = bounded_command(
                command,
                root / f"{row['id']}-llama-stdout.txt",
                root / f"{row['id']}-llama-stderr.txt",
            )
            stderr = (root / f"{row['id']}-llama-stderr.txt").read_text()
            offload = re.search(r"offloaded (\d+)/(\d+) layers to GPU", stderr)
            if not offload or int(offload[1]) <= 0 or offload[1] != offload[2]:
                raise RuntimeError("full GPU offload not observed")
            terminated = "smoke_eog:" in stderr
            text = raw.strip()
            ids = [int(token) for token in re.findall(r"smoke_token: (\d+)", stderr)]
            from transformers import AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(root / "merged", local_files_only=True)
            expected_prompt_ids = tokenizer(row["prompt"], add_special_tokens=False)["input_ids"]
            prompt_ids = [
                int(token) for token in re.search(r"smoke_prompt_ids:([^\n]+)", stderr)[1].split()
            ]
            if prompt_ids != expected_prompt_ids:
                raise RuntimeError("GGUF prompt tokenization differs from saved tokenizer")
        cases.append(
            {
                "id": row["id"],
                "output": text,
                "raw_output": raw,
                "expected": row["expected"],
                "exact_match": score(text, row["expected"]),
                "candidate_text_parity": text.strip() == row["output"].strip(),
                "token_parity": ids == row["generated_ids"] if ids is not None else None,
                "terminated": terminated,
            }
        )
    report = {
        "runtime": args.runtime,
        "seconds": time.monotonic() - start,
        "cases": cases,
        "exact_match": sum(r["exact_match"] for r in cases),
        "total": len(cases),
        "all_text_parity": all(r["candidate_text_parity"] for r in cases),
        "all_terminated": all(r["terminated"] for r in cases),
        "gpu_only": True,
        "all_token_parity": all(r["token_parity"] for r in cases),
    }
    (root / f"export-{args.runtime}.json").write_text(json.dumps(report, indent=2) + "\n")
    if not report["all_text_parity"] or not report["all_terminated"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
