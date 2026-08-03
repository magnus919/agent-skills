---
name: release-engineering
description: >-
  Design, automate, and operate end-to-end software releases: release process
  models and pipelines (trunk-based development, CD stages, release trains),
  progressive delivery and feature flags, versioning and artifact management
  (SemVer, conventional commits, changelogs, SBOM/provenance), readiness and
  quality gates, rollback and recovery planning, change-management and audit
  compliance (SOC 2, SOX, PCI), DORA metrics, and multi-team release
  coordination. Do not use for application feature implementation
  (backend-engineering/frontend-engineering), production incident root-cause
  debugging or on-call/SLO operations (systematic-debugging /
  site-reliability-engineering), security implementation or threat modeling
  (secure-software-engineering), or internal developer platform construction
  (platform-engineering).
license: MIT
compatibility: >-
  Platform-agnostic methodology. Scripts require Python 3.8+ (stdlib only).
  No CI platform, deployment tool, or version control mandate.
metadata:
  source_repo: https://github.com/magnus919/agent-skills
  skill_version: "1.0.0"
  tags: release-engineering, releases, ci-cd, continuous-delivery, progressive-delivery,
    feature-flags, semver, changelog, rollback, release-trains, dora, sbom, change-management,
    deployment, artifacts, release-coordination
---

# Release Engineering

Senior-to-principal release engineering methodology: designing and operating the pipelines, processes, artifacts, gates, compliance evidence, and metrics that move software from commit to customer safely, predictably, and fast.

## Ownership

| You own | You don't own |
|---------|--------------|
| Release process design — branch strategy, process model, release cadence | Application feature implementation — route to [backend-engineering](../backend-engineering/SKILL.md) / [frontend-engineering](../frontend-engineering/SKILL.md) |
| CD pipeline architecture — build-once promotion stages, gates, push-on-green | Production incident root-cause debugging — route to [systematic-debugging](../systematic-debugging/SKILL.md) |
| Progressive delivery — canaries, rings, percentage rollouts, feature flags | On-call and SLO operations — route to [site-reliability-engineering](../site-reliability-engineering/SKILL.md) |
| Versioning and artifacts — SemVer, conventional commits, changelogs, immutability, provenance | Security implementation and threat modeling — route to [secure-software-engineering](../secure-software-engineering/SKILL.md) |
| Readiness and quality gates — release candidates, go/no-go, sign-off | Internal developer platform construction — route to [platform-engineering](../platform-engineering/SKILL.md) |
| Rollback and recovery planning — runbooks, rehearsals, recovery targets | Data pipeline operations and schema migration engineering — route to [data-engineering](../data-engineering/SKILL.md) |
| Change governance and audit compliance — SOC 2 / SOX / PCI evidence chains | Spec authoring and SDD gate mechanics — route to [spec-driven-development](../spec-driven-development/SKILL.md) |
| DORA metrics — definitions, computation, thresholds | API contract design and versioning policy — route to [api-design-and-evolution](../api-design-and-evolution/SKILL.md) |
| Multi-team release coordination — trains, calendars, stabilization | Evidence collection and verdicts against explicit criteria — route to [verification-methodology](../verification-methodology/SKILL.md) |
| Release operations — branch cuts, pipeline triage, emergency releases | Runtime monitoring and alerting — that's SRE |

## Core Principles

**Build once, promote many.** The artifact that passed every gate is the only artifact that ships. Rebuilding per environment reintroduces risk and invalidates what was verified.

**Small batches ship faster and safer.** Trunk-based development with frequent small merges outperforms long-lived branches on every DORA metric — deployment frequency, lead time, change failure rate, and recovery time.

**Decouple deploy from release.** Deploying code to production is not the same as exposing it to users. Feature flags and progressive rollout separate the two so each can happen on its own timeline and either can be reversed independently.

**Automated safety beats approval bureaucracy.** Evidence-based controls and pipeline gates outperform change-advisory-board sign-off, which research correlates with slower, less stable delivery. Automate the checks; reserve human approval for genuinely exceptional change.

**Rehearse rollback.** A rollback you haven't practiced will fail under pressure. Rollback is a first-class release artifact with its own runbook, trigger thresholds, and rehearsal log.

**Verify in production.** Staging parity helps, but production canaries, smoke tests, and observability gates are where readiness is actually proven. Real traffic, real telemetry, real decision points.

**Protect the supply chain.** Sign every artifact, record provenance and SBOM data, and treat registries as a security boundary. Integrity is part of the release, not an add-on.

**DORA is a system outcome.** Speed and stability emerge from how the process is designed — batch size, architecture, automation, safety culture — not from chasing metric targets.

## Loading Guide

| File | Load when |
|------|-----------|
| `references/role-and-career.md` | Understanding the release engineering role — org placement, day-to-day, Senior/Staff/Principal leveling, and evidence separating levels |
| `references/skills-competency-model.md` | Mapping the technical and professional skills release engineers master, and which ones differentiate at senior and above |
| `references/release-process-models.md` | Choosing a process model — trunk-based, GitFlow, GitHub Flow, release branches, release trains — and matching cadence to the org |
| `references/cd-and-pipeline-stages.md` | Designing CD pipelines — build-once promotion, stage gates, push-on-green, pipeline-as-code, hermetic builds, environment parity |
| `references/progressive-delivery.md` | Planning canary, blue/green, ring, or percentage rollouts; metric and error-budget gates; auto-rollback triggers |
| `references/change-governance-and-compliance.md` | Building audit-ready change control — SOC 2 CC8.1, SOX ITGC, PCI back-out, evidence chains, separation of duties, emergency change |
| `references/readiness-and-quality-gates.md` | Defining readiness dimensions, release candidates, go/no-go structure, error-budget release policy, definition of done |
| `references/rollback-and-recovery.md` | Planning rollback vs roll-forward vs flag recovery per system type; rehearsed rollbacks; time-boxed decisions; quarantine |
| `references/versioning-and-artifacts.md` | Setting SemVer/CalVer policy, conventional commits, changelog conventions, artifact immutability and provenance |
| `references/feature-flag-lifecycle.md` | Running flags through their full lifecycle — create, guard, rollout, verify, remove, expire — and avoiding flag debt |
| `references/monorepo-polyrepo-release.md` | Choosing mono vs polyrepo release strategy, affected-build detection, topological publish order, release tooling |
| `references/toolchain-landscape.md` | Selecting tools by category — CI/CD, release automation, artifact repos, GitOps, feature flags (2025-2026 status) |
| `references/supply-chain-security.md` | Hardening the supply chain — SLSA, SBOM, sigstore keyless signing, dependency updates, provenance attestations |
| `references/metrics-and-dora.md` | Defining and computing the five DORA metrics, thresholds, vendor divergence, and measurement pitfalls |
| `references/release-operations-and-triage.md` | Running release trains end-to-end — branch cuts, stabilization, go/no-go, pipeline triage, release infra reliability, agentic automation |
| `templates/release-plan.md` | Producing a release plan — scope, milestones, owners, risks, rollout, rollback contingency, comms |
| `templates/release-readiness-checklist.md` | Running a readiness review — checkbox table by dimension with owner + evidence, go/no-go block |
| `templates/rollback-runbook.md` | Writing a rollback runbook — triggers, per-layer steps, verification, ordering, comms, rehearsal log |
| `templates/release-notes.md` | Drafting release notes — version, date, change-type sections, breaking changes, migration steps |
| `templates/change-governance-record.md` | Recording an audit-ready change — ticket, PR, CI runs, artifact digest, deploy timestamp, verification, emergency flag |
| `templates/hotfix-emergency-release-plan.md` | Planning an emergency release — severity, break-glass approvals, expedited path, post-implementation review |
| `assets/dora-metrics-reference.md` | Looking up the five DORA metrics — formulas, units, data sources, thresholds, pitfalls — in one page |
| `assets/versioning-decision-table.md` | Choosing a versioning scheme — SemVer vs CalVer vs independent vs one-version, bump rules |
| `assets/deployment-strategy-matrix.md` | Comparing deployment strategies — rolling, blue-green, canary, ring, flag, shadow — on speed, safety, rollback |
| `assets/release-toolchain-cheatsheet.md` | Quick tool lookup by category — one-liner and when-to-pick per tool |
| `scripts/version_bump.py` | Computing the next SemVer from conventional commits or a git range |
| `scripts/semver_check.py` | Validating, comparing, or sorting strict SemVer versions |
| `scripts/changelog_check.py` | Validating Keep a Changelog or Release Please CHANGELOG.md files |
| `scripts/dora_metrics.py` | Computing the five DORA metrics from deployment and commit event data |
| `scripts/release_plan_scaffold.py` | Scaffolding a release plan document from flags or a git range |
| `evals/evals.json` | Running output-quality evals for this skill (schema v1, 8 cases) |

## Adjacent Skills

- Use [qa-methodology](../qa-methodology/SKILL.md) to define test strategy, regression scope, flake policy, and quality-gate semantics. This skill combines the resulting evidence with operational and governance evidence for a release decision.
- For AI-agent releases, use [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md) to design and interpret behavioral, trajectory, and model-regression evidence before incorporating it into a release gate.

## Scripts

| Script | Invocation | Purpose |
|--------|-----------|---------|
| version_bump | `python3 scripts/version_bump.py --current-version 1.4.0 --git-range v1.4.0..HEAD` | Computes the next SemVer from Conventional Commits — breaking → major (minor in 0.x), feat → minor, fix → patch; optional prerelease tag |
| semver_check | `python3 scripts/semver_check.py --check 1.2.3-beta.1` | Validates strict SemVer 2.0.0, compares two versions, or sorts a list |
| changelog_check | `python3 scripts/changelog_check.py CHANGELOG.md [--format auto|keep-a-changelog|release-please]` | Validates supported changelog headers, dates, sections, bullets, and links; reports selected/detected format |
| dora_metrics | `python3 scripts/dora_metrics.py --events events.json` | Computes all five DORA metrics from deployment and commit event data |
| release_plan_scaffold | `python3 scripts/release_plan_scaffold.py --version 2.0.0 --owner alice --output plan.md` | Scaffolds a release plan document with filled placeholders from flags or a git range |

## Triggers

Load this skill when the task involves:

- **Release planning** — designing a release plan, timeline, milestones, or rollout strategy
- **Pipeline design** — architecting or reviewing CD pipelines, promotion stages, or push-on-green
- **Version bumps** — computing the next version, SemVer validation, conventional-commit classification
- **Changelogs** — authoring or validating a changelog
- **Readiness review** — go/no-go calls, release candidates, readiness checklists
- **Rollback planning** — writing or rehearsing rollback runbooks and recovery plans
- **Progressive delivery** — canaries, rings, percentage rollouts, traffic shadowing
- **Feature flags** — flag rollout, lifecycle, and cleanup
- **Release trains** — calendar releases, branch cuts, stabilization windows
- **DORA metrics** — defining, computing, or reporting the five DORA metrics
- **Compliance evidence** — SOC 2 / SOX / PCI change records, audit trails, separation of duties
- **Artifacts and supply chain** — SBOM, provenance, signing, registry hygiene
- **Emergency releases** — hotfixes, break-glass changes, expedited release paths
- **Multi-team coordination** — cross-team release calendars and integration stabilization

## When not to use

Route to the named sibling skill instead:

- [backend-engineering](../backend-engineering/SKILL.md) / [frontend-engineering](../frontend-engineering/SKILL.md) — implementing application features. Release engineering designs the pipeline that ships code; it does not implement the code itself.
- [systematic-debugging](../systematic-debugging/SKILL.md) — root-cause analysis of production incidents, fault localization, bug reproduction. Release engineering plans recovery; debugging finds the cause.
- [site-reliability-engineering](../site-reliability-engineering/SKILL.md) — on-call operations, SLO/error-budget management, capacity planning, and day-to-day incident response.
- [secure-software-engineering](../secure-software-engineering/SKILL.md) — security implementation and threat modeling. Release engineering consumes security controls (SBOM, signing, dependency scanning) but does not design them.
- [platform-engineering](../platform-engineering/SKILL.md) — building the internal developer platform: CI infrastructure, GitOps controllers, self-service tooling, and golden paths.
- [data-engineering](../data-engineering/SKILL.md) — data pipeline operations, schema migration engineering, and data quality monitoring.
- [spec-driven-development](../spec-driven-development/SKILL.md) — writing specifications and running SDD pipeline gates and verdicts.
- [api-design-and-evolution](../api-design-and-evolution/SKILL.md) — API contract design and versioning policy. Release engineering version-bumps artifacts; it does not set API evolution rules.
- [verification-methodology](../verification-methodology/SKILL.md) — collecting evidence and rendering verdicts against explicit pass/fail criteria.

## Stop and Exit Conditions

- **Release plan complete when:** the plan names version, target date, milestones and branch cut, owners (RACI), scope items, risks with mitigations, rollout plan, rollback contingency, comms plan, and sign-offs.
- **Readiness checklist complete when:** every item in each dimension (functional, non-functional, operational, governance) has an owner and evidence, and a go/no-go decision is recorded.
- **Rollback runbook complete when:** trigger thresholds, impact assessment, decision criteria, per-layer rollback steps, verification SLIs, rollback ordering, comms, and a rehearsal log are all in place.
- **Version bump complete when:** the next version is computed from actual commit history (or an explicit file), validated against strict SemVer, and the bump rule is justified by the conventional-commit types.
- **Compliance record complete when:** the change chain — ticket → PR review → CI → approval → deploy log → verification — is complete, sampled, and retained per policy, with separation of duties respected.
- **Bounded escalation:** stop after three non-converging diagnostic passes and report the evidence collected so far.
