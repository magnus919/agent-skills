# Final verification

2026-10-12. Local branch `work/unsloth-gpu-validation`, independent clone
`/private/tmp/agent-skills-unsloth-20261012`, based on freshly fetched origin/main
`fb3253335cdb1156522901ef52f9897212b2e4b5`. No push or merge.

## Passed

- `make validate`: Ruff lint/format, mypy, complexity, dependency scan, dependency
  release-age check and core tests. **389 tests and 31 subtests** passed;
  core coverage **72.33%**, above the required 60%.
- Skill-local tests: `python3 -m unittest discover -s unsloth/scripts -p 'test_*.py'`
  passed **35 tests**. Pytest with scoped addopts passed those same 35 tests and
  three subtests; these are two runners for the same suite, not independent quality evidence.
- `python3 unsloth/scripts/unsloth_preflight.py dataset unsloth/assets/train.jsonl
  --eval-file unsloth/assets/heldout.jsonl --json`: 40/8 valid rows, zero exact
  duplicates/overlap. This offline preflight does not assess tokenization or
  semantic leakage; the separate GPU label reports do assess actual tokens/labels.
- Integration suite: **14 tests** passed.
- Canonical skill format/link/README validation: **184 skills** accepted.
- Changed-skill quality: **one skill, zero errors/warnings**.
- Eval schema/semantic validation: **184 manifests** accepted. Eval validator and
  coverage-validator tests each passed **27 tests**. Coverage ratchet stays at
  **100% schema-valid manifests**; generated semantic performance is not assessed.
- Script-test naming and all **10 registered shell suites** passed using the
  development environment on PATH. EPUB dependencies are already present there.
- Required tracked artifact sweep passed with local mock-server socket access.
  New tracked Python compiles and JSON parses were included in that sweep.
- Reference-scan validator tests: **25 runs / 72 assertions**; changed-skill
  validator tests: **19 runs / 159 assertions**; llms generator tests:
  **5 runs / 41 assertions**, all without failures.
- Claude marketplace, Codex/agent marketplace and llms catalog regenerated and
  current: **174 top-level skills**. Bundle validation: **8 bundles**. Lifecycle
  matrix, curated-case register and AGENTS consistency checks passed.
- Bandit high-severity check completed successfully. Existing lower-severity
  repository findings are not claimed absent.
- Duplicate-code check (`jscpd@5.4.1`) passed configured 15% threshold:
  **3.20% duplicated lines**, 2.26% duplicated tokens repository-wide.
- Technical-debt scan completed: five existing markers reported; no new source
  markers were introduced by the Unsloth scripts.
- `git diff --check` passed after trailing whitespace was normalized only in
  local native-log review copies; raw host log hashes are retained.

## Environment failures preserved and resolved

The sandboxed artifact sweep failed because mock HTTP servers could not bind
local sockets, with PermissionError. The same required sweep passed with local
socket access; no production endpoints or GPU inference were used by that suite.
An initial registered-shell run omitted the development environment from PATH
and failed EPUB dependency checks. Using the existing development environment
on PATH passed all ten suites; no unrelated skill was changed to accommodate it.
The npm duplicate-code checker was not cached; its pinned public release was
run with npm config/cache confined to `/private/tmp`.

`skills-ref` was not installed; no successful reference-library validation is
claimed. The repository's validator checked format, references and README rules.
No generated model behavioral evals or Jev semantic grading was run, and none is
claimed from manifest or deterministic helper test success.

## GPU evidence

All requested successful model stages ran on the RTX 5070 Ti. See
`gpu-validation.md` and `evidence/stage-status.json` for per-stage statuses,
model/package/source revisions, memory/timing, preserved failed attempts and
remaining unverified paths. The successful F16 GGUF path requires observed
29/29 GPU layer offload and compares prompt IDs, generated IDs and termination.
Model weights, checkpoint binaries and native executable remain on the GPU host;
only code, synthetic fixtures and small evidence records are in the local branch.
