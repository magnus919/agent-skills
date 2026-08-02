# Resilience and Recovery

Design, exercise, and evidence resilience and recovery behavior across systems and dependencies — producing exercise-backed resilience plans, not only design documents.

## Why Install This Skill

Most teams have recovery plans. Few have tested them. This skill provides a structured method for designing resilience into systems — graceful degradation, restore-based recovery, dependency analysis, RTO/RPO decision records, game days, failover drills, data integrity verification, and recovery communication. It treats exercise evidence as the standard of proof: a recovery plan that has never been exercised is not a recovery capability.

Install this skill when your agent needs to help teams move from "we have a DR plan somewhere" to "we exercised our restore last quarter and here is the evidence." It composes specialist capabilities from SRE, platform, data, security, and release engineering without duplicating their methodology, and it feeds resilience evidence into the production-excellence bundle for go/no-go readiness decisions.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, resilience patterns (graceful degradation and restore-based recovery), resilience plan template fields, core principles, routing table, and progressive-disclosure loading guide |
| `references/discovery-brief.md` | Survey of adjacent skills (SRE, platform, data, security, release, incident-learning) with ownership boundaries and routing decisions |
| `references/failure-modes-and-dependencies.md` | Method for mapping failure modes, analyzing dependency behavior under failure, and designing degradation paths with tier-based feature shedding |
| `references/recovery-plan-template.md` | Structured resilience/recovery plan template with all required fields: system boundary, failure modes, dependency map, degradation choices, RTO/RPO, data integrity, recovery procedure, communication plan, exercise schedule, follow-up ledger |
| `references/exercise-design-and-evidence.md` | Game-day, restore-test, and failover-drill design; scenario definition; evidence recording; exercise-finding classification |
| `references/rto-rpo-decision-record.md` | Context-specific RTO/RPO decision-record template with tradeoff analysis and per-system examples |
| `references/data-integrity-verification.md` | Post-restore data validation: checksums, row counts, application-level consistency checks, reconciliation protocol |
| `references/recovery-communication.md` | Stakeholder notification planning: templates, channels, escalation paths, timing |
| `references/follow-up-work-ledger.md` | Converting exercise findings into owned implementation, test, and operational follow-up work with verification gates |
| `evals/evals.json` | Five output-quality eval cases covering dependency outage, restore test, regional failure, degraded-but-available path, and recovery exercise exposing an unowned gap |

## Quick Start

Start with the failure-modes reference to map your system's failure surface, then use the recovery-plan template to produce a structured plan. The RTO/RPO decision record and exercise-design reference turn the plan into testable evidence.

Ask your agent to "design a resilience plan for <system>" or "prepare a game day for <scenario>" and the skill's triggers will route the work.

## Triggers

- Design, exercise, and evidence resilience and recovery behavior across systems: failure-mode analysis, graceful degradation, restore-based recovery, RTO/RPO decision records, game days, failover drills, restore testing, data integrity verification, and recovery communication.
- Requests to assess disaster recovery readiness, plan a failover drill, verify data integrity after a restore, or convert exercise findings into follow-up work.
- Work where a system's resilience must be proven through exercise evidence rather than design documentation alone.

## Requirements

No runtime dependencies. The methodology is host-neutral and requires no specific tools, platforms, or API keys. Exercise execution may require access to the target system and its recovery tooling; the skill provides the method, not the execution environment.
