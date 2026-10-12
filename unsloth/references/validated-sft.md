# Observed GPU text-SFT recipe

Read this for a runnable, bounded text-only SFT baseline. It was executed on
2026-10-12 on Ubuntu 24.04.5, Python 3.11.16, RTX 5070 Ti (16,303 MiB), NVIDIA
580.178.04, compute capability 12.0. The existing GLiNER service remained running
with 2,270 MiB resident and idle. Other GPUs, UI products, quantized training,
vision/audio, RL, and multi-GPU paths have not been validated by this run.

## Pinned compatibility baseline

| Component | Observed version/revision |
|---|---|
| Unsloth / Zoo | 2026.10.3 / 2026.10.3 |
| Torch / compiled CUDA | 2.14.0+cu130 / 13.0 |
| Triton / Xformers | 3.8.0 / 0.0.35 |
| Transformers / TRL | 5.17.0 / 1.13.0 |
| PEFT / datasets / bitsandbytes | 0.21.2 / 4.8.5 / 0.50.2 |
| Model | `unsloth/Qwen3-0.6B` |
| Model revision | `db4e90b8359f816f09bf5c944797ce116f26da3c` |
| Official Qwen3 notebook revision | `87c1e89e973562a5fa94aaffe523e2da84f75785` |
| llama.cpp converter/libraries | `1acee6bf8939948f9bcbf4b14034e4b475f06069` |

The full resolved stack is in `assets/requirements-gpuslut01.lock`. This is an
observed version freeze, not a minimal dependency set or a hash-locked wheel
archive. It includes packages inherited from a previous local experiment. The
new environment was separate; cached wheels used hardlinks. Never modify linked
package files in place. Two offline attempts failed (missing CUDA index, then a
missing Pillow wheel); online installation with the explicit cu130 index passed.
`uv pip check`, Unsloth import, and a CUDA matrix multiply all passed. Do not
individually upgrade Triton against Torch's pinned dependency.

Recipe sources: [official Blackwell guide](https://unsloth.ai/docs/blog/fine-tuning-llms-with-blackwell-rtx-50-series-and-unsloth),
[Qwen3 notebook](https://github.com/unslothai/notebooks/blob/87c1e89e973562a5fa94aaffe523e2da84f75785/nb/Qwen3_%2814B%29-Reasoning-Conversational.ipynb),
and [public model revision](https://huggingface.co/unsloth/Qwen3-0.6B/tree/db4e90b8359f816f09bf5c944797ce116f26da3c).
This adaptation uses the smaller dense model, BF16 LoRA (not QLoRA), rank 8,
seven projection targets, alpha 16, batch 2, accumulation 2, AdamW Torch,
learning rate 2e-4, warmup 2, seed 3407, context 256, no packing, and 20 steps.

## Reproduce in an authorized isolated directory

Run from the skill root on the **GPU host**. Use a new user-owned directory;
never reuse a completed training directory or upgrade another environment.
Confirm target, scope and rollback before mutation using existing authorization.
Rollback is stopping only this experiment's process and retaining its artifacts.
Inventory first; allow only observed idle GPU service PIDs. Stop on new GPU
processes, activity from existing services, low disk reserve, or nonfinite loss.
The initial fixture config records PID 26174 from this run; review that field on
another host or date. Do not allowlist an unknown job to make a guard pass.

```bash
RUN="$HOME/experiments/unsloth-smoke-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN"
cp assets/smoke-config.json assets/train.jsonl assets/heldout.jsonl "$RUN/"
uv venv "$RUN/.venv" --python 3.11.16
uv pip install --python "$RUN/.venv/bin/python" --torch-backend=cu130 \
  -r assets/requirements-gpuslut01.lock
uv pip check --python "$RUN/.venv/bin/python"
uv pip freeze --python "$RUN/.venv/bin/python" > "$RUN/resolved.txt"
python3 scripts/unsloth_preflight.py dataset "$RUN/train.jsonl" \
  --eval-file "$RUN/heldout.jsonl" --json
"$RUN/.venv/bin/python" scripts/sft_smoke.py train \
  --run-dir "$RUN" --config "$RUN/smoke-config.json"
"$RUN/.venv/bin/python" scripts/sft_smoke.py reload \
  --run-dir "$RUN" --config "$RUN/smoke-config.json"
"$RUN/.venv/bin/python" scripts/sft_smoke.py resume \
  --run-dir "$RUN" --config "$RUN/smoke-config.json"
```

Prerequisites: NVIDIA driver/GPU, user-installed uv, nvidia-smi (including pmon),
Python 3.11, and public download access. No token, service, upload, or paid endpoint
is needed. Torch's CUDA wheels supply runtime libraries; the driver capability
string alone does not select an appropriate package stack. The successful path
used system CUDA capability 13.0 with Torch cu130; this is not a driver-upgrade
instruction. A new uncached installation needs more disk than a hardlinked one.
Budget at least 25 GiB free for a cold environment, model, checkpoints and export;
retain at least 2 GiB free during execution.

## What the scripts prove

- `sft_audit.py` renders the actual tokenizer template with thinking disabled.
  Training token IDs must start with the exact inference generation-prefix IDs.
  Prefix tokens receive -100 labels; answer, EOS and trailing template tokens are
  supervised. This recipe intentionally supports exactly one user/assistant turn.
- Full untruncated tokenization records lengths and supervised-token counts.
  Any partial or complete target truncation aborts. The actual collator output is
  compared against expected IDs, attention masks, label masks and ignored padding.
  A real SFTTrainer dataloader batch is matched back to audited examples and checked.
- The fixture has 40 synthetic training records and eight distinct held-out
  prompts. It checks exact prompt overlap; the preflight also checks content
  duplicates. These similar toy examples do not establish semantic independence
  or domain generalization. Reports deliberately expose only this synthetic text;
  review privacy before adapting the reporting to real user data.
- Greedy decoding, a 16-token completion budget and identical prompts are fixed.
  Exact match strips only surrounding whitespace. All raw outputs, token IDs,
  expected answers, scores and termination flags are retained. Baseline is captured
  before applying LoRA; candidate is captured after saving.
- Checkpoints at steps 10 and 20 contain adapter, optimizer, scheduler, trainer and
  RNG state. Adapter/tokenizer delivery is saved separately. Fresh reload checks
  missing/unexpected adapter keys, saved tokenizer prompts and token parity.
- Resume restores step 20 and runs to 22. Input hashes reject changed config/data.
  Extending max_steps changes the learning-rate horizon; this demonstrates stateful
  restoration, not equivalence to an uninterrupted run planned for 22 steps.
- Timings include model load, audits, generation and saving, excluding package
  installation and Unsloth import. Torch peak allocation/reservation measure this
  process, not total host VRAM. Trainer runtime is reported separately.

## GPU export and inference parity

Do not use CPU fallback when the user requires GPU-only inference. First merge:

```bash
"$RUN/.venv/bin/python" scripts/sft_smoke.py merge \
  --run-dir "$RUN" --config "$RUN/smoke-config.json"
"$RUN/.venv/bin/python" scripts/verify_export.py hf --run-dir "$RUN"
```

Use a pinned, clean llama.cpp source checkout and matching CUDA-enabled libraries.
On the validation host these already existed at `/home/magnus/llama.cpp`; they were
read without modifying them. On a different host prepare them in an authorized
isolated directory. Set the following paths to that matching installation:

```bash
LLAMA_SRC=/home/magnus/llama.cpp
LLAMA_LIB="$LLAMA_SRC/build/bin"
"$RUN/.venv/bin/python" "$LLAMA_SRC/convert_hf_to_gguf.py" "$RUN/merged" \
  --outfile "$RUN/candidate-f16.gguf" --outtype f16
g++ -O2 -std=c++17 scripts/gpu_completion.cpp \
  -I"$LLAMA_SRC/include" -I"$LLAMA_SRC/ggml/include" -L"$LLAMA_LIB" \
  -Wl,-rpath,"$LLAMA_LIB" -lllama -lggml -lggml-base -o "$RUN/gpu-completion"
"$RUN/.venv/bin/python" scripts/verify_export.py llama --run-dir "$RUN" \
  --gpu-completion "$RUN/gpu-completion"
```

The small public-API harness uses greedy sampling, no additional BOS, explicit
EOG detection, and 99 requested GPU layers. It refuses inference unless the
backend is GPU-capable and the loader reports full offload. The Python verifier
checks prompt tokenization, output token IDs, exact-match answers and termination.
Native GPU kernel execution is confirmed in retained CUDA backend logs. Process
output goes to files with a 1 MiB cap and 60-second deadline; stdin is EOF. On a
limit/failure only that child process group is stopped. Repeated CLI output must
never be accumulated by an unbounded `capture_output=True` call.

The installed `llama-cli` rejected `--no-conversation` and instructed use of
`llama-completion`, which was not built on this host. An initial CPU attempt's
unbounded Python capture was OOM-killed at about 20 GiB RSS; the bounded GPU CLI
attempt stopped at its output cap. Both failures are retained. The GPU-only
harness was the third and final diagnostic attempt and passed. No CPU inference
is part of the reproducible successful recipe. F16 GGUF is tested; Q4/Q8
quantization, UI/server-template behavior and other runtimes remain unverified.

## Observed results and completion

Initial training: 7.522 seconds trainer time, 26.612 seconds stage time;
1.322 GiB peak Torch allocation and 1.365 GiB reservation. The finalized script
verification repeated the same frozen settings: 7.078 seconds trainer time,
16.684 seconds stage time, identical peak memory and held-out outcomes.
The base scored 0/8 exact uppercase answers; the adapter scored 8/8. Fresh reload,
merged Transformers and GPU F16 GGUF matched all eight candidate outputs. GGUF
also matched prompt and generated token IDs; its eight-process test took 9.281
seconds, and each load reported 29/29 offloaded layers with a 1,137 MiB CUDA
model buffer. This is a formatting smoke task, not a general quality benchmark.

Complete when label audits pass, bounded training has finite loss and saved state,
fresh reload and resume are evidenced, and the requested export passes its target
runtime checks. Otherwise retain failure logs and report fail/not-run. Stop at
three nonconverging diagnostic attempts, new contention, nonfinite training or a
failed data audit; do not repair by changing system drivers/packages/services.
