# Runbooks

This document references incident response procedures for the agent-skills repository.

## When Something Goes Wrong

### CI Validation Failure

1. Check the [GitHub Actions validate workflow](https://github.com/magnus919/agent-skills/actions/workflows/validate.yml)
2. Review the failing step output for specific error messages
3. Common failures and resolutions:

| Failure | Likely Cause | Resolution |
|---------|-------------|------------|
| `ruff check` fails | Code style violation | Run `make format` locally, then `make lint` |
| `mypy` fails | Type annotation error | Fix type annotations per mypy output |
| `radon` fails | Complexity threshold exceeded | Refactor complex function into smaller units |
| `pytest` fails | Test regression | Reproduce locally with `make test` |
| `deptry` fails | Unused or missing dependency | Run `make deps` and update requirements-dev.txt |
| `validate-skills.rb` fails | Invalid SKILL.md format | Check frontmatter YAML, relative links |
| `eval-coverage` ratchet fails | Schema-valid manifest coverage decreased | Add evals/evals.json to modified/new skills |

### Generated Artifact Staleness

If CI reports stale catalog artifacts:

```sh
ruby scripts/gen-claude-marketplace.rb --write
ruby scripts/gen-codex-plugin.rb --write
ruby scripts/gen-llms-txt.rb --write
git add .claude-plugin/ .codex-plugin/ llms.txt
git commit -m "chore: refresh generated artifacts"
```

### Security Vulnerability in Dependency

1. Review the bandit or Dependabot alert
2. Update the affected dependency in `requirements-dev.txt`
3. Run `make validate` to confirm no regressions
4. Review the changelog of the updated dependency for breaking changes

### Pre-commit Hook Issues

If pre-commit hooks are blocking commits:

```sh
# Run all hooks manually to see errors
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

## Deployment

This repository has no deployment step. All changes are validated in CI and merged to `main`. Catalog artifacts (`llms.txt`, marketplace.json, plugin.json) are tracked in the repository and refreshed on each change.

## Monitoring

### Dashboards
- [GitHub Actions dashboard](https://github.com/magnus919/agent-skills/actions) — CI pipeline health and deploy status
- [GitHub Actions validate workflow](https://github.com/magnus919/agent-skills/actions/workflows/validate.yml) — Primary validation pipeline
- [GitHub Security Advisories](https://github.com/magnus919/agent-skills/security) — Vulnerability alerts and advisory history
- [Dependabot alerts](https://github.com/magnus919/agent-skills/security/dependabot) — Dependency update PRs and security notifications

### Deploy Impact Visibility
- All changes flow through the validate workflow on each push and PR
- CI status is visible in PR checks and on the [Actions tab](https://github.com/magnus919/agent-skills/actions)
- Release notes are auto-generated in [CHANGELOG.md](https://github.com/magnus919/agent-skills/blob/main/CHANGELOG.md)
- Release history is tracked in [GitHub Releases](https://github.com/magnus919/agent-skills/releases)
- CI failures on `main` automatically create tracking issues (via `ci-failure-to-issue.yml` workflow)
