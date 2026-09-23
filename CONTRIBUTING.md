# Contributing to agent-skills

Thanks for helping improve agent-skills. Contributions should make a skill more useful, more portable, or easier for humans and agents to discover.

## Before you start

- Read `AGENTS.md` for repository-wide conventions.
- Read the target skill's `SKILL.md` and `README.md` before changing it.
- For a new skill or a substantial change, open an issue first so the scope can be discussed.
- Do not include credentials, private infrastructure details, or deployment-specific paths.

## Skill requirements

Each skill must:

- Live in its own directory with a matching lowercase, hyphenated name.
- Include `SKILL.md` with valid YAML frontmatter.
- Include a human-facing `README.md` with the required sections described in `AGENTS.md`.
- Keep core instructions concise and put deeper material in `references/`, `templates/`, or `scripts/`.
- Use relative links that work from a fresh clone.
- Use an imperative-verb description that defines both positive and negative trigger boundaries.
- Describe when the skill should be loaded, and identify the nearest alternative when overlap matters.
- Include `evals/evals.json` with explicit `schema_version: 1` and at least five representative output-quality cases for every new skill. This is a repository-owned contract, not part of the normative Agent Skills specification; see [`schemas/evals-v1.schema.json`](schemas/evals-v1.schema.json). Use canonical `assertions`, not `expectations`. Existing skills are grandfathered via `scripts/grandfathered-skills.txt`; the ratchet tightens as schema-valid manifest coverage climbs. The ratchet runs in CI on every pull request via `python3 scripts/eval-coverage.py --modified-from <base-sha>`. A skill counts as modified when any tracked file under its directory changes. Schema-valid manifest coverage must not decrease between the base revision and the candidate.

The coverage report keeps claims separate. `manifest_present` means only that a file exists. Per skill, `schema_valid` is `not_applicable` when `evals/evals.json` is missing, `false` when a present manifest fails parsing/schema/semantic validation, and `true` only when the manifest passes repository v1 validation. Aggregate schema-valid coverage counts only skills where `schema_valid` is `true`. The remaining states are named but intentionally `not_assessed` in v1: `executable_grader_bindings_present`, `recent_run_evidence_present`, and `release_gated_evidence_present`. Those require separate versioned contracts for grader bindings, provenance/freshness, and release-gate evidence.

### Writing useful eval assertions

Our default-branch CI can ask Jev for an **advisory** second opinion on prose assertions in paired skill evals. Design the eval to describe the behavior you want, not to flatter the model. The v1 manifest format has not changed: keep stable case IDs, realistic prompts, a case-level `expected_output`, and observable `assertions`.

Avoid a broad assertion such as “Covers private hosting, authentication, readiness, and rollback.” A response can cover three of those and omit the fourth. Write separately checkable claims instead:

```json
{
  "assertions": [
    "Limits the service to private network access",
    "Authenticates requests before inference",
    "Reports readiness only after the model, tokenizer, and inference device load",
    "Defines a rollback path for a checkpoint upgrade"
  ]
}
```

For structural API requirements, name the invariant. For example, a reranking eval should require a distinct Score or Noul question ID **for each candidate** and separately require sorting or fusion in code. Batching those distinct questions in one request is valid; a single question returning an array of candidate scores is not. Do not require one request per candidate or otherwise exclude a valid design just to simplify grading.

Before submitting a changed manifest, try to identify a satisfying response, a plausible contradiction, and an answer that simply lacks evidence for each semantic assertion. If the three cannot be distinguished, sharpen the assertion or choose a more appropriate evidence source. Use `eval_runner/grader.py`'s existing prefixes for exact checks; a keyword check does not verify meaning. Claims about actual files, execution, or side effects need executable/environment evidence, not just a response saying they happened. Do not add Jev-specific fields to `evals/evals.json` or silently rename an eval ID.

The current grader reports prose as `manual_review`, and its overall `passed=true` is **not** a verified semantic pass. Jev's `met`/`not_met`/`not_shown` suggestions help reviewers prioritize inspection; they do not change required CI or approve release. Our pilot found a high-confidence false positive on a real API-shape mistake, so do not tune wording to maximize Jev's score or set a gating probability from the synthetic fixture. See [`docs/jev-ci-reference-runlog.md`](docs/jev-ci-reference-runlog.md) for the experiments and remaining calibration work. In a PR, explain any material change to what an assertion accepts and include the relevant validation results.

For low-toil iteration, the optional main-branch model-teacher screen can blind a separate inference model to Jev's predictions and report disagreements on real outputs. Its labels are **pseudo-labels**, not human-verified outcomes: use them to find ambiguous assertions and candidate failure cases, not to claim accuracy or set a CI gate. Keep generated responses and teacher rationales out of public artifacts, and do not use Jev outputs to train an imitation model.

Improving this CI integration means changing **our Jev API inputs**, not training Jev: the assertion, trusted question instructions and Choice criteria, relevant state, or grouping of independent questions. Record the input revision and the specific error it is meant to address. Compare it against the current request on the same labeled examples, then check a frozen held-out set; report `met` false accepts and `not_shown`/abstention behavior, not just overall agreement. The synthetic benchmark is a contract check, and an inference-model teacher is a disagreement screen. Neither alone authorizes a CI gate or a probability cutoff.

Paired-eval CI has a five-skill resource cap. Changes anywhere in a skill directory—including references, templates, assets, and README—make that skill eligible if it has an eval manifest. When a change touches more than five eligible skills, CI fails selection rather than silently evaluating a subset. Split the PR or propose an explicit cap change. The model job freezes the selected case IDs before generation; Jev compares that list with the received reports. Read both the expected-versus-observed case count and the assertion coverage before interpreting a green Jev audit. A missing case report, skipped model job, or missing selection evidence is incomplete coverage even if Jev judged every assertion it saw. None of these counts establishes semantic correctness or release approval.

## Skill catalog structure

The catalog is two-layered by design. Keep your change in the layer that matches the job, and prefer beefing up an existing skill over creating a near-duplicate:

- **Methodology skills** teach judgment for a discipline (frameworks, decision models, ownership boundaries): `backend-engineering`, `platform-engineering`, `qa-methodology`, the product family, and friends.
- **Operational tool skills** own a named tool or system agents actually run: `kubernetes`, `docker-compose`, `traefik`, `grafana`, `supabase`, `restic`, and the `*-cli` wrappers.

Decision guide:

| Situation | Do |
|---|---|
| An existing skill's description already claims the topic | Thicken it — add references, templates, scripts, and evals. Don't split. |
| A named tool has no owner skill | New operational tool skill — one skill per tool, with a script, `README.md`, and `evals/evals.json`. |
| A judgment discipline has no owner skill | New methodology skill — keep runbooks out; patterns go in `references/`. |
| Formats/tools share one workflow and one trigger (PDF/Word/Excel/PowerPoint; EPUB) | One family skill with per-format references, like `epub`. Promote to a bundle with sub-skills only when reference depth outgrows it. |
| Routing references | Must point at real skills in this repository. Fix dead links (`docker-management`, `technical-architect`, `reviewer`, ...) when you touch a skill. |
| A new `*-cli` wrapper | Ship a script that adds depth beyond a thin wrapper, plus `README.md` and evals. Thicken existing wrappers before adding siblings. |
| Any change to an existing skill | Add or update its eval manifest in the same change so the coverage ratchet never decreases. |

See `AGENTS.md` ("Catalog Structure: Methodology vs. Operational Tooling") for the full statement of the split.

## Development

Clone the repository and run the validators from its root:

```sh
git clone https://github.com/magnus919/agent-skills.git
cd agent-skills
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
ruby scripts/validate-skills.rb
ruby scripts/validate-skill-quality.rb --base origin/main
python3 scripts/test-eval-validation.py
python3 scripts/validate-evals.py
python3 scripts/test-eval-coverage.py
python3 scripts/eval-coverage.py
```

The structural validator checks the whole repository. The quality validator checks only added, renamed, modified, or uncommitted `SKILL.md` files relative to the supplied base. Changed descriptions must begin with an imperative verb and define a negative boundary in the description or a `When not to use` section. Generic no-op instructions are reported as warnings. The same validation runs in GitHub Actions for pushes and pull requests.

This repository also tracks generated catalog files. CI validates their freshness but does not regenerate them. If a check reports a stale artifact, regenerate locally:

```sh
ruby scripts/gen-claude-marketplace.rb --write
ruby scripts/gen-codex-plugin.rb --write
ruby scripts/gen-llms-txt.rb --write
```

Each generator also runs in check mode (without `--write`) to verify freshness.

If a skill includes executable scripts or a package, run its documented checks as well and include the commands and results in your pull request.

### Skill script tests

Every skill that ships executable scripts must name its script tests `scripts/test_*.py`; pytest auto-discovers and runs them in CI for every skill's `scripts/` directory, so Python test files must use the exact `test_*.py` name. Shell-based tests are the exception: register them in `scripts/check-skill-tests.py` as a `run` entry (executed in CI with `bash`) or a `manual` entry (documented only, when the test needs network access, credentials, or external tooling). CI enforces the naming convention: a file under any skill `scripts/` directory whose name matches the test conventions (`test_*.py`, `test*.sh`, `*_test.*`, `*-test.*`, or `.bats`) must be a Python `test_*.py` (auto-run) or be registered in `scripts/check-skill-tests.py`; `python3 scripts/check-skill-tests.py --check` fails otherwise.

## Deprecating a skill

When replacing a skill, preserve its old directory as a routing stub. Prefix its description with `Deprecated: use <replacement>`, explain the migration in the stub, and remove it only after compatibility is no longer required.

## Pull requests

- Create a branch from `main`: `feat/short-description`, `fix/short-description`, or `docs/short-description`.
- Keep each pull request focused on one logical change.
- Use a clear Conventional Commit subject, such as `feat(skill): add ...` or `fix(skill): ...`.
- Add or update documentation with the behavior it describes.
- Do not force-push after review unless a maintainer asks you to.
- Complete the pull request checklist and disclose meaningful AI assistance.

A maintainer may ask for an issue before reviewing a large design change. Small documentation fixes and clear bug fixes can go directly to a pull request.

## License

By contributing, you agree that your contribution is released under the MIT License in this repository.
