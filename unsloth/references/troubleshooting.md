# Troubleshooting by failing layer

Preserve a minimal input, first traceback, environment inventory and attempted
change for each pass. Work on a disposable environment or new run directory.
Stop after three passes without new evidence and report the missing prerequisite.

| Symptom | First discriminating check | Next bounded action |
|---|---|---|
| Import/kernel/ABI error | Does a tiny backend operation work without Unsloth? | If not, fix driver/Torch/backend pairing first; otherwise test a fresh Unsloth-first import. |
| Package upgrade did nothing | Which interpreter/kernel loaded the package? | Compare metadata in that interpreter and restart the kernel. |
| OOM while loading | Model weights, quantization, free device memory | Use a smaller supported model or valid quantization; do not start a long training retry. |
| OOM during training | Peak context and batch, activation/optimizer state | Start batch 1, shorter context, supported checkpointing; remeasure before altering rank. |
| OOM during evaluation | Eval batch, retained predictions/logits | Reduce evaluation batch/retention using the installed trainer's options. |
| OOM during merge/export | Temporary high-precision weights and disk/RAM | Preserve adapter; use supported lower export memory budget or another adequately sized host. |
| Zero/NaN loss | Actual labels, mask coverage, answer truncation | Decode supervised positions before changing optimizer settings. |
| Loss improves; task worsens | Same held-out prompts and decoding? | Audit leakage, objective, target quality and overfitting; retain the failed candidate. |
| Export loops or repeats | Prompt/template/special tokens in target runtime | Compare rendered tokens and termination configuration before blaming quantization. |
| RL reward flat or perfect | Known correct/incorrect/malformed reward probes | Inspect component scores, parsing and reward hacking; don't blindly extend training. |
| Slow first steps | Compilation, download and warmup versus steady state | Measure after warmup with identical token workload; inspect CPU/data stalls. |
| Stalled distributed run | Per-rank logs, device assignment and collective state | Reproduce on one rank, then two; stop the exact job, not all host processes. |

The official [FAQ](https://unsloth.ai/docs/basics/troubleshooting-and-faqs.md)
contains version and export diagnostics. It suggests broad upgrades and remote
code in some cases; this skill deliberately narrows those actions: first capture
versions, prove the failing layer, and review model-specific code before enabling
`trust_remote_code`. Do not use it as a generic compatibility switch.

For export memory errors, official guidance exposes `maximum_memory_usage` on
supported save paths; verify the installed method accepts it before setting a
lower value. Memory freed by unrelated process termination is not an authorized
fix unless that process is within the task scope.

## Evidence for an upstream report

Include OS, accelerator and driver, exact package versions/commits, source
notebook revision, model revision, minimal synthetic data, command, first complete
traceback, and whether the failure survives a fresh environment. Exclude tokens,
private training examples and unrelated machine information. Draft the report;
publishing it requires the user's instruction to communicate externally.
