# Fixture and Source Notes — Lifecycle Evaluation Corpus

This document records every fixture/source input used by corpus cases and its provenance,
per VAL-CRP-025.

## Corpus cases are self-contained

All 98 corpus cases across the 17 manifests are **self-contained**: every input needed to
evaluate the case is inlined in the case `prompt` (scenario facts, metrics, thresholds,
constraints, and expectations are embedded in the prompt text). There are no external
datasets, no URLs fetched at run time, and no case uses the `files` field.

Consequence: the **union of `files` entries across the corpus is empty**, so there are no
fixture paths to resolve, and the repository fixture-resolution validator
(`scripts/validate-evals.py`, which rejects missing, untracked, escaping, or symlinked
fixture paths) has nothing to check beyond its normal manifest validation. Every per-trial
manifest records `case.prompt_hash` (SHA-256 prefix of the prompt) so the exact inline input
under test is pinned; `case.fixture_hashes` is empty for every case.

Provenance for the inline inputs is the case content itself — see the per-case IDs in
[`coverage-matrix.md`](coverage-matrix.md) and the manifest sources below.

## Manifest sources

| Manifest | Cases | Provenance / notes |
|---|---|---|
| `implementation-planning/evals/evals.json` | 6 | Milestone-4 skill #186. Scenarios derived from the issue's mandatory case types (ambiguous requirements, cross-repo dependencies, data migration, risky rollout, unapproved-prerequisite rejection). |
| `product-analytics-and-measurement/evals/evals.json` | 6 | #188. New feature, internal product, public service, conflicting metrics, unmeasurable North Star, privacy-boundary measurement. |
| `product-roadmapping-and-portfolio/evals/evals.json` | 5 | #189. Competing bets, dependency invalidation, low-confidence opportunity, capacity shortfall, justified stop. |
| `product-experimentation/evals/evals.json` | 5 | #190. Method selection, feature-flag rollout, underpowered experiment, guardrail omission, no-ship boundary. |
| `product-adoption/evals/evals.json` | 7 | #191. Internal tool, public service, discovery failure, enterprise cohorts, pause expansion, two anti-triggers. |
| `conditional-customer-success/evals/evals.json` | 5 | #192. Subscription plan, internal-tool decline, public-service routing, renewal risk, conflicting health evidence. |
| `product-operations-and-governance/evals/evals.json` | 6 | #193. Lightweight model, high-assurance model, contested decision, exception, missing-evidence escalation, anti-universal-org-chart. |
| `product-lifecycle-learning/evals/evals.json` | 7 | #194. Success, non-adoption, ambiguity, justified retirement, retirement migration, two anti-patterns. |
| `production-readiness/evals/evals.json` | 5 | #196. Low-risk release, user-facing launch, migration-dependent release, missing-owner block, human-approval exception. |
| `migration-engineering/evals/evals.json` | 5 | #197. Additive schema, backfill+reconciliation, API version, irreversible cutover, reconciliation failure. |
| `resilience-and-recovery/evals/evals.json` | 5 | #198. Dependency outage, restore test, regional DR, degraded path, unowned-gap exercise. |
| `capacity-and-cost-engineering/evals/evals.json` | 5 | #199. Growth forecast, peak event, SLO/cost conflict, quota decision, misleading unit cost. |
| `incident-learning/evals/evals.json` | 5 | #200. Noisy report, monitoring gap, process failure, agent authority failure, non-actionable follow-up rejection. |
| `privacy-engineering/evals/evals.json` | 6 | #202. Analytics telemetry, agent traces, tenant isolation, deletion/revocation, residency, jurisdiction escalation. |
| `bundles/product-lifecycle/evals/evals.json` | 6 | #187. Integrated trajectories incl. product launch and failed experiment; phase routing + lifecycle evidence ledger. |
| `bundles/production-excellence/evals/evals.json` | 6 | #195. Integrated trajectories incl. blocked readiness review and migration-reconciliation failure; production evidence packet + operational handoff. |
| `bundles/agent-production-operations/evals/evals.json` | 8 | #201. Integrated trajectories incl. agent tool failure and privacy-boundary escalation; runtime control plan + tool-authority-health + trace-to-eval feedback. |

## No credentials, no external sources

Corpus prompts, expected outputs, and assertions contain no API keys, tokens, or other
credentials, and no case requires network access or a real model. All corpus runs use the
fake adapter only (`--adapter fake`), consistent with VAL-CRP-030. Before committing, the
corpus layer and manifests are grepped for credential patterns (see the PR validation
checklist).
