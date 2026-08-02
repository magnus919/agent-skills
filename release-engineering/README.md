# Release Engineering

Senior-to-principal release engineering methodology: pipelines, process, artifacts, gates, compliance, and metrics that move software from commit to customer safely.

## Why Install This Skill

Releasing software is where engineering risk becomes customer impact. This skill gives your agent the working methodology of a senior release engineer: designing CD pipelines that promote one immutable artifact through every environment, planning rollbacks before you need them, choosing between canary, blue-green, and feature-flag rollouts, and computing DORA metrics from real events instead of guesses.

It also covers the parts of release work that quietly break teams: versioning and changelog discipline, audit-ready change records for SOC 2 / SOX / PCI, supply-chain integrity (SBOM, signing, provenance), and the ceremony of multi-team release trains. Install once and your agent can draft a release plan, compute the next SemVer from commit history, validate a changelog, build a rollback runbook, and report the five DORA metrics — without you hand-writing a single template.

## What You Get

| Directory | Contents |
|-----------|----------|
| `references/` | 15 dense topic files: role-and-career, skills-competency-model, release-process-models, cd-and-pipeline-stages, progressive-delivery, change-governance-and-compliance, readiness-and-quality-gates, rollback-and-recovery, versioning-and-artifacts, feature-flag-lifecycle, monorepo-polyrepo-release, toolchain-landscape, supply-chain-security, metrics-and-dora, release-operations-and-triage |
| `templates/` | 6 fillable templates: release-plan, release-readiness-checklist, rollback-runbook, release-notes, change-governance-record, hotfix-emergency-release-plan |
| `assets/` | 4 quick-reference files: dora-metrics-reference, versioning-decision-table, deployment-strategy-matrix, release-toolchain-cheatsheet |
| `scripts/` | 5 Python CLIs: version_bump (next-SemVer from conventional commits), semver_check (validate/compare/sort), changelog_check (Keep a Changelog validator), dora_metrics (five-metric computation), release_plan_scaffold (plan generator) |
| `evals/` | Schema-v1 output-quality eval manifest (8 cases) |

## Quick Start

Compute the next version from the commits since the last tag:

```bash
python3 release-engineering/scripts/version_bump.py --current-version 1.4.0 --git-range v1.4.0..HEAD
```

Validate a changelog before it ships:

```bash
python3 release-engineering/scripts/changelog_check.py CHANGELOG.md
```

Compute the five DORA metrics from deployment and commit event data:

```bash
python3 release-engineering/scripts/dora_metrics.py --events deploy-events.json --environment prod
```

## Triggers

- Release planning, timelines, and rollout strategy
- CD pipeline design and promotion-stage reviews
- Version bumps, SemVer validation, and conventional-commit classification
- Changelog authoring and validation
- Go/no-go readiness reviews and release candidates
- Rollback runbook writing and rehearsal
- Canary, blue-green, ring, and feature-flag rollouts
- Feature flag lifecycle and cleanup
- Release trains, branch cuts, and stabilization windows
- DORA metric definitions and computation
- Change-control and audit evidence (SOC 2, SOX, PCI)
- SBOM, signing, provenance, and registry hygiene
- Hotfixes, break-glass changes, and emergency releases
- Multi-team release coordination

## Requirements

- Python 3.8+ for scripts (standard library only, no third-party packages)
- No specific CI platform, deployment tool, or version control mandate
- Works with any stack; examples reference GitHub Actions, GitLab, Argo CD, LaunchDarkly, and others as illustrations
