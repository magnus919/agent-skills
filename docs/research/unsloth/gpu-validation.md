# GPU validation and local delivery

2026-10-12. Recovered the uncommitted `feat/unsloth-skill` draft from wanker01
without changing its workspace. Imported `unsloth/`, `docs/research/unsloth/` and
human catalog changes into an independent local clone. Regenerated package
catalogs rather than trusting copied generated files. Fetched origin/main twice;
both resolved to `fb3253335cdb1156522901ef52f9897212b2e4b5`.

Local checkout: `/private/tmp/agent-skills-unsloth-20261012`.
Local branch: `work/unsloth-gpu-validation`. No push, upload, PR, publication or
merge. The original Mac checkout and wanker01 working changes are preserved.
Model weights remain on gpuslut01 at
`/home/magnus/experiments/unsloth-skill-20261012`.

## Result

| Stage | Status | Measured evidence |
|---|---|---|
| Isolated installation | PASS | 107 pinned packages; `uv pip check`, Unsloth import, CUDA matrix result 8.0 |
| Token/template and collated labels | PASS | 40 rows, 32–33 tokens, 3 supervised tokens each, no lost targets; actual SFTTrainer batch checked |
| Base evaluation | PASS | Fixed greedy prompts scored 0/8 exact uppercase answers |
| Initial 20-step training | PASS | Finite loss; 7.522 s trainer / 26.612 s stage |
| Finalized code, same 20-step settings | PASS | 7.078 s trainer / 16.684 s stage; same losses and outcomes |
| Candidate evaluation | PASS | 8/8 exact matches; all terminate |
| Fresh adapter/tokenizer reload | PASS | Exact token parity on all eight prompts |
| Stateful checkpoint resume | PASS | Full step-20 state restored; two more steps; final trainer time 1.600 s |
| 16-bit merge and fresh GPU reload | PASS | Eight prompt/output token matches; reload 4.432 s |
| F16 GGUF conversion | PASS | 1.2 GB local artifact; checksum retained |
| GPU GGUF inference parity | PASS | 29/29 offloaded layers; prompt/output token parity and EOS on all eight; 9.281 s for eight processes |
| CPU GGUF attempt | FAIL | Unbounded Python capture OOM-killed, exit 137; not part of the successful workflow |
| Bounded GPU llama-cli attempt | FAIL | CLI rejects noninteractive mode; output limit stopped its child |
| QLoRA, Q4/Q8, GUI, RL, multimodal, multi-GPU | NOT RUN | Broader guidance is explicitly unverified by this run |
| Generated catalog behavioral evals | NOT RUN | Manifest/schema validity does not prove semantic performance |

Training peak Torch allocation was **1,419,094,016 bytes (1.322 GiB)**; peak
reservation **1,465,909,248 bytes (1.365 GiB)** in both initial/final runs.
A training-time nvidia-smi sample showed 3,829 MiB total GPU memory including the
pre-existing 2,270 MiB GLiNER service. Native GGUF logs show a 1,137 MiB CUDA model
buffer plus kernel buffers; this is not a claimed measured total-process peak.
Stage timings exclude installation and Unsloth import. Final training stage
includes load, audits, baseline/candidate inference and artifact saves.

The task is a small synthetic color-formatting test. Similar training and held-out
examples test the pipeline; they do not establish broad generalization or real
workload quality. Resume extends max_steps from 20 to 22, altering the scheduler
horizon. This is restoration evidence, not a proof of equivalence to uninterrupted
22-step training. No tuning was performed to manufacture an improvement.

## Hardware and dependencies

Ubuntu 24.04.5 LTS, Python 3.11.16, RTX 5070 Ti, 16,303 MiB VRAM, driver
580.178.04, SM 12.0, 31 GiB system RAM. At discovery about 16 GiB RAM was available
and the root filesystem had 6.5 GiB free. Cached hardlinks made a new environment
possible; no prior installations were modified. Later user-authorized Docker
cache/image reclamation raised free disk to about 144 GiB. Existing containers,
volumes, models, services and training workspaces were preserved.

| Package | Version |
|---|---|
| Unsloth / Zoo | 2026.10.3 / 2026.10.3 |
| Torch / compiled CUDA | 2.14.0+cu130 / 13.0 |
| Triton / Xformers | 3.8.0 / 0.0.35 |
| Transformers / TRL | 5.17.0 / 1.13.0 |
| PEFT / datasets / bitsandbytes | 0.21.2 / 4.8.5 / 0.50.2 |

Full version freeze: `unsloth/assets/requirements-gpuslut01.lock`.
Base model: `unsloth/Qwen3-0.6B`, immutable revision
`db4e90b8359f816f09bf5c944797ce116f26da3c`, public and ungated at discovery.
Official notebook revision: `87c1e89e973562a5fa94aaffe523e2da84f75785`.
llama.cpp source/converter/libraries: `1acee6bf8939948f9bcbf4b14034e4b475f06069`.
Known-host ED25519 fingerprint matched the user-verified value; existing SSH
identities were used in place. No credentials were transferred.

## Reproduction and retained evidence

Full cold-install, GPU SFT/reload/resume/merge and GPU GGUF commands are in
`unsloth/references/validated-sft.md`. To reproduce only the finalized saved
experiment's resume evidence, inspect its stage reports first; scripts reject
rerunning a completed stage or changed configuration/data. For a new run use a
new directory and the same frozen fixtures. Review existing GPU PID allowances
against live inventory before execution.

Small records are in `docs/research/unsloth/evidence/`:

- `stage-status.json` provides pass/fail/not-run per stage and evidence paths.
- `source-record.json` pins model/source revisions and recovery/notebook hashes.
- `final-run/` retains tokenizer, trainer batch, baseline/candidate, reload and
  resume reports for the finalized SFT code.
- Initial reports and `executed-initial-*.py.txt` preserve the first executed
  code versions. Final source lives in the skill scripts, with host hashes in
  `artifact-hashes.txt`. No inference/optimizer algorithm changed between runs;
  final changes tightened auditing, input consistency and resource guards.
- Install logs preserve both failed offline hypotheses and the successful third
  attempt. Export logs preserve failures and the successful third diagnostic.
  The second CLI stdout is preserved as a tool-output excerpt; its full stream
  was replaced on the next attempt. Kernel OOM evidence is in `export-diagnosis.txt`.
- Model, optimizer/scheduler/RNG and final source hashes identify retained host
  artifacts. Per-prompt native logs verify CUDA offload, prompt IDs, token IDs
  and termination. Final host GPU/RAM/disk snapshots are included.

Local native-log copies normalize trailing whitespace; original byte hashes are
in `evidence/raw-log-hashes.txt`, and original files remain on the GPU host.

No complete environment dump, private dataset or weights is returned. The helper
reports intentionally include only this synthetic text. Do not blindly use its
content-logging policy for sensitive training data.

## Skill improvements and validation

The skill now ships executable SFT and actual token/collator audits, an observed
version freeze, synthetic separate holdouts, stateful checkpoint and fresh-process
reload checks, merged GPU inference, and GPU-only F16 GGUF verification. A small
native harness avoids the installed interactive CLI's incompatibility. Output
capture is file-backed, capped and timed; failures stop only the child group.

Eleven v1 output-quality eval cases are present. Five existing IDs were retained
while their rubric was revised to demand artifacts; a reproducible-package case
was added. Artifact-existence assertions use the repository's recognized prefix;
semantic claims require readable artifact content and remain manual review.
The v2 challenge tables include satisfying, contradictory and missing-evidence
examples. No generated evals or Jev pass is claimed.

The root dependency scanner excludes the Unsloth skill, following other named-tool
skills, because its separate GPU dependencies are frozen in the skill assets.
This does not exclude it from skill-local tests, schema validation or catalog checks.
Final check results are recorded in `final-verification.md`.
