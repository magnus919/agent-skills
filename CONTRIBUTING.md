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
