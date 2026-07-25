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
