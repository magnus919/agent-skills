# Evidence Ledger

## Intent

Add the source-grounded llama.cpp operations skill requested by issue #143, covering installation, GGUF/model handling, verified inference and serving, tuning, benchmarking, and diagnosis without freezing volatile interfaces in the core skill.

## Authority

The user granted modify, publish, and merge authority for this repository and requested commit, push, PR, green CI, and merge.

## Inspected artifacts

- Issue `magnus919/agent-skills#143` and repository `AGENTS.md`, validators, eval schema, CI workflows, catalogs, and recent merged PR conventions.
- Existing `agent-skills`, `research-methodology`, `spec-driven-development`, `neckbeard`, `ml-engineering`, `restic`, `supabase`, and `esp32-development` guidance.
- llama.cpp commit `555881ebc8b0fc0402b30e09258a32a7bfd13c52`, release `b10107`, official build/install/server/CLI/GGUF/quantization/benchmark/multi-GPU sources, and REST changelog.

## Assumptions

- The repository's current schema-version-1 eval contract remains authoritative for this change.
- Source-backed command examples are useful without a bundled wrapper CLI.
- Runtime behavior must be refreshed against the installed binary because upstream interfaces are volatile.

## Alternatives rejected

- Expanding `ml-engineering/references/quantization-inference.md`: too broad for the llama.cpp lifecycle and operational failure modes.
- Separate GGUF/server/benchmark skills: fragments one operational workflow.
- Bundled preflight wrapper: native `--version`, `--help`, `--list-devices`, logs, and templates cover the first version without another maintenance surface.
- One known-good launch command: hardware/model-specific and rapidly stale.

## Files changed

- Added `llama-cpp/SKILL.md`, human `README.md`, this ledger, six focused references, two operation templates, and a six-case eval manifest.
- Updated root `README.md` and `references/skill-triggers.md` for discovery.
- Regenerated `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, and `llms.txt`; `.agents/plugins/marketplace.json` remained unchanged.

## Commands / checks run

- `ruby scripts/validate-skills.rb`
- `ruby scripts/validate-skill-quality.rb --base origin/main`
- `python3 scripts/test-eval-validation.py`
- `python3 scripts/validate-evals.py`
- `python3 scripts/test-eval-coverage.py`
- `python3 scripts/eval-coverage.py --modified-from origin/main`
- `python3 scripts/check-artifacts.py`
- `ruby scripts/test-validate-skill-quality.rb`
- Claude, Codex, and `llms.txt` generator check modes plus the `llms.txt` generator tests
- Paired, release, and existing eval-runner test suites
- Independent final-diff review against issue #143, Agent Skills rules, research fidelity, and neckbeard boundaries

## Observed outputs

- Worktree began clean on `main` at `1f5cd6a`.
- Upstream llama.cpp reviewed at `555881eb`; latest reviewed release was `b10107`.
- No `llama-cli` executable was present on the authoring host.
- Skill validation found 108 canonical skills with no format/link failure.
- Changed-skill quality checked one new skill with 0 errors and 0 warnings.
- All 9 present eval manifests passed schema-v1 and semantic validation; eval validation and coverage tests passed.
- Artifact checks and their repository test suites passed.
- Generated catalogs were current at 98 public skills/plugins.
- Paired, release, and existing eval-runner tests passed.
- Independent review found no skill-content, trigger, safety, eval, catalog, or issue-scope defect after this ledger/README correction.

## Verification boundary

- Research: source and repository boundary.
- Component: Agent Skills structure, links, README sections, eval schema, line budget, and generated catalogs.
- Integration: whole-repository artifact and validator suites plus fake-adapter eval-runner plumbing.
- Delivery: GitHub PR checks and final-head review remain pending until publication.

## Unverified boundaries

- Live llama.cpp build, model load, inference, accelerator, and server behavior are not locally exercised because no binary/model is installed and host installation/model download is outside repository scope.
- Real-model output-quality grading is not established by the schema-v1 manifest or fake-adapter CI smoke; repository policy reports executable grader bindings, recent run evidence, and release-gated evidence as not assessed.

## Rollback / follow-up triggers

- Revert if repository validation or CI cannot pass without weakening required quality gates.
- Refresh when upstream command help, backends, GGUF metadata, REST behavior, or benchmark boundaries change materially.
- Add a script only if repeated eval traces show agents independently reimplementing the same error-prone inspection.

## Status

Local implementation and integration verification passed. Delivery is pending publication, final-head CI, and merge; live llama.cpp runtime behavior remains an explicitly disclosed gap.

## Batch frontend and output containment, 2026-10-12

The follow-up user directive authorized fixing this repository's llama.cpp
workflow and merging it through GitHub. The separate Unsloth draft remains on
its unpublished local branch; no model weights are included in this change.

Observed on gpuslut01: Ubuntu 24.04.5, Python 3.12.3, RTX 5070 Ti, driver
580.178.04; installed CLI/source revision `1acee6bf8939948f9bcbf4b14034e4b475f06069`.
The native interactive frontend advertises a shared flag, warns that
`--no-conversation` is unsupported, and continues initialization. Our former
unbounded Python capture amplified repeated EOF/UI output into an OOM. The
repository's stale smoke recipe did not distinguish that frontend from batch
completion. Upstream C++ code lives in ggml-org/llama.cpp and is not modified here.

The new `scripts/llama_batch.py` refuses a missing completion frontend before
weights load, does bounded capability discovery, supplies EOF stdin, caps bytes
before buffering/writing, imposes a wall deadline, isolates/cleans its child group,
and requires positive full CUDA placement. Caller defaults cannot inject chat,
remote model selection or log suppression through LLAMA_* or HF_TOKEN.
A new output-quality case and challenge table cover these boundaries.

Validation:

- Missing target in the existing binary directory was rejected before inference:
  `evidence/missing-completion.json`.
- The completion frontend was built in a new user-owned directory against the
  installed libraries without changing that installation. First compilation
  lacked the vendored nlohmann include path; the second succeeded. Reproduction
  for this matching installation:

```sh
g++ -O2 -std=c++17 /home/magnus/llama.cpp/tools/completion/main.cpp \
  /home/magnus/llama.cpp/tools/completion/completion.cpp \
  -I/home/magnus/llama.cpp/tools/completion -I/home/magnus/llama.cpp/common \
  -I/home/magnus/llama.cpp/include -I/home/magnus/llama.cpp/ggml/include \
  -I/home/magnus/llama.cpp/vendor -L/home/magnus/llama.cpp/build/bin \
  -Wl,-rpath,/home/magnus/llama.cpp/build/bin \
  -lllama-common -lllama -lggml -lggml-base -pthread -o llama-completion
```

- Initial logging checks did not expose placement. Numeric thresholds 2 and 3
  still hid backend INFO in the installed library. Those runs remained failed
  rather than being promoted on CUDA visibility. A metadata-only C++ callback
  probe confirmed threshold 3 suppressed INFO while INT_MAX emitted it; using the
  supported `--verbose` flag then produced explicit placement under the byte cap.
  All failed/build/probe evidence remains under
  `/home/magnus/experiments/llama-completion-fix-20261012`.
- Final GPU run passed: **29/29 layers** and **1,137 MiB CUDA0 model buffer**;
  **0.520 seconds** for process execution, excluding preflight. Greedy output
  was `RED` followed by the native EOG marker, matching the synthetic target.
  `evidence/gpu-run.json` retains command, version, limits and evidence. This is
  one compatibility smoke, not a general quality or performance benchmark.
- The script's report keeps semantic quality `not_assessed`; the separate
  reviewed expected-answer result is limited to that smoke input.
- **13 offline regression tests** passed, including output floods, saved-byte
  caps, EOF stdin, timeouts/group cleanup, missing completion, partial/absent GPU
  evidence, injected defaults and existing-directory preservation.
- `make validate`: **389 core tests and 31 subtests** passed, with all root lint,
  format, type, dependency and coverage gates. Skill format/quality, eval schema,
  script-test naming and generated catalog checks passed. GitHub CI must pass on
  the exact PR head before merge; local evidence alone is not that gate.

Windows and non-CUDA helper execution are not validated. The broader July
reference guidance retains its original research date. No CPU model inference,
paid/model-provider calls, public service or model upload was used in this fix.
