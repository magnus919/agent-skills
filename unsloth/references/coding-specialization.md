# Coding specialization: data, SFT and real-task acceptance

Use for preparing a local code model, repository-repair assistant, or structured
code generator. This guide is researched, not a new GPU-validated training recipe.
The existing `references/validated-sft.md` proves a small single-turn formatting
run only. The operational handoff begins after `ml-engineering` determines that
adaptation is preferable to a prompt, retrieval, classifier or rules baseline.

Task-specific hosted inference products may be useful baselines, but API
availability does not establish open weights, local training or GPU-only execution.
Route classifier/extractor/summarizer selection and CDM claim review to
`ml-engineering`; do not present them as Unsloth-compatible checkpoints.

## Identify the unit of work

Distinguish function synthesis, completion, repository patch generation and a
multi-turn agent. A function model receives a specification and emits code; an
agent receives tool observations, emits actions and produces a patch. An agent's
success depends on its tools, history truncation, permissions and environment,
not just the language-model weights. Training only final patches does not teach
an agent to navigate a repository. Teacher trajectories can teach tool behavior,
but failed, fabricated or secretly solution-informed trajectories contaminate
that signal.

[SWE-Gym](https://arxiv.org/abs/2412.21139) demonstrates training on runnable
repository tasks and agent trajectories. [SWE-smith](https://arxiv.org/abs/2504.21798)
shows scalable task generation by introducing changes that break existing tests.
These are task/data infrastructure examples, not evidence that their 32B agent
recipe fits a consumer GPU or that all synthetic failures resemble real issues.
Use their author code to inspect preparation and scoring. Pin the actual source
revision before executing; a repository landing-page snapshot is not a code audit.

## Construct the dataset before touching the trainer

Keep one immutable source manifest per experiment. For each record preserve:

- stable task/trajectory ID, repository or source-group ID, source URI, commit or
  immutable dataset revision, collection date and permission/license decision;
- issue text and the code snapshot available before the repair, including tests
  legitimately visible to the agent;
- teacher/model/prompt revision and tool schema when trajectories are generated;
- reference solution and independently executed correctness receipt, separate
  from the prompt; never place sealed answers or hidden tests in observations;
- filtering decisions: incomplete traces, nonreproducible environments, invalid
  tests, source forks, duplicate problem families and solution-contaminated rows.

Split source groups **before** deriving variants, chunking or synthesizing.
Choose group IDs that join repository forks, renamed repositories, related issues
and descendants of one seed when those imply leakage. A commit hash does not make
another version of the same task independent. Use a later-time test slice where
maintenance drift matters. Keep development examples for choices and a sealed
final test roster for acceptance. Hash the actual files, not their directory names.

Route permission, annotation quality and teacher provenance to
`training-data-annotation`; route ingestion/deduplication architecture to
`data-engineering`. Exact hashes are one screen: paraphrases, shared solutions,
pretraining contamination and semantically equivalent bugs require additional
review. Public benchmark overlap remains a limitation even if fine-tune splits
are clean.

## Offline provenance and leakage screen

`scripts/specialization_audit.py data` accepts three JSONL files with the contract:

```json
{"id":"repair-001","group_id":"repository-family-a","source":{"uri":"local:reviewed-corpus","revision":"immutable-source-revision","rights":"reviewed internal training use"},"messages":[{"role":"user","content":"Repair this supplied function."},{"role":"assistant","content":"Reviewed solution text"}]}
```

`source.rights` records a decision; nonempty text does not verify legal permission.
`source.revision` must be immutable in the source system; the helper checks presence,
not external resolution. Do not use `main` or `latest`. Messages accept text-only
system/user/assistant roles with exact role/content keys. Tool-call, preference and
multimodal formats fail explicitly; preserve those in a separate processor-aware
pipeline rather than flattening them into this contract.

```bash
python3 scripts/specialization_audit.py data --train train.jsonl \
  --development development.jsonl --test test.jsonl
```

The helper checks required provenance fields, globally duplicate IDs, exact
content duplicates, cross-split prompt overlap even with different answers, and
cross-split source groups. It scans bounded lines/bytes/rows, fails incomplete or
empty scans, and emits codes/counts/line numbers without private text or source
URLs. Exit 0 clears **these checks only**; 1 is findings/incomplete; 2 is bad CLI
arguments. It neither creates splits nor tokenizes, runs code or grants permission.

## SFT implementation sequence

1. Select a supported instruction/code model and pin weights/tokenizer/notebook
   revisions. Select LoRA/QLoRA from measured capacity, not model-download size.
   For GPU-only work review optimizer paging and CPU offload explicitly.
2. Use a new authorized run directory and isolated resolved environment. Capture
   free VRAM, existing processes, disk reserve and version compatibility. The
   validated smoke's old allowlisted PID is not permission to share a current job.
3. Render genuine long examples with the exact inference template. Record token
   length and target retention. Decode non-ignored labels from an actual collator
   batch, including code indentation, EOS and tool delimiters when applicable.
   Reject dropped/partial targets; silently clipping a patch can teach broken code.
4. Pin the installed [TRL SFT](https://huggingface.co/docs/trl/sft_trainer) API.
   Assistant-only loss depends on template masks; completion-only and full-sequence
   objectives are different. Do not label training prompt/tool observations as
   supervised assistant actions accidentally. Validate packing boundaries and
   attention/masking again if enabling packing.
5. Begin with a short finite-loss run and reload; then run the registered budget.
   Sweep learning rate/rank/module targets on development data, not the final set.
   Retain checkpoints and rejected runs. The existing single-turn smoke cannot
   silently become a multi-turn agent trainer by adding more messages.
6. Compare the base and adapter on executable held-out tasks with identical
   prompts/context, maximum attempts, token/tool budgets and scoring. Include
   a tuned prompt/retrieval control where appropriate. Loss improvement is not
   functional correctness. Correctness checks must cover new functionality and
   preservation of existing tests, plus independent critical-failure review.

[LoRA Learns Less and Forgets Less](https://arxiv.org/abs/2405.09673) reports a
learning/retention tradeoff and sensitivity to rank, target modules and learning
rate. It does not support a default promise that LoRA preserves every capability.
Keep out-of-domain and multi-turn regression slices as well as the target tasks.

## Deliver the whole contract

Use `templates/specialization-plan.md` and `templates/reward-contract.md`, plus the
existing run record. Save base revision, adapter/config, tokenizer/template,
training code/data hashes, optimizer checkpoints, held-out outputs and verifier
receipts. Distinguish fresh adapter continuation from stateful optimizer resume.

Use [PEFT merge guidance](https://huggingface.co/docs/peft/developer_guides/lora)
for the chosen adapter configuration. `merge_and_unload` creates a merged model
and removes PEFT operations; it is not a reversible active-adapter switch.
Quantized merges have backend limitations and possible numeric differences.
Test the merged artifact in a fresh process, then the actual `llama-cpp` or `vllm`
runtime with pinned template, termination and context settings. Compare functional
outcomes after lossy quantization; exact token identity is not a universal lossy
acceptance rule. Preserve rollback to the accepted artifact/config pair.

Complete when provenance/label audits, the bounded run, fresh reload and fixed-task
comparison are evidenced and requested export is validated. If hardware is absent,
deliver a runnable prepared package and mark stages not run. Do not claim a coding
specialist from a smoke fixture or a reference-only guide.
