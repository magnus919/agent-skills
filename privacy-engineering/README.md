# Privacy Engineering

Turn privacy principles and legal requirements into engineering artifacts that are observable, testable, and verifiable — data-lifecycle records, privacy acceptance criteria, data-flow maps, retention/deletion verification plans, and privacy change reviews.

## Why Install This Skill

Most privacy work stops at policy documents. A privacy policy says "we delete your data after 90 days." Privacy engineering asks: how do you know? Has anyone verified that the deletion actually happened across all stores, backups, caches, and derived datasets? This skill provides a structured method for translating privacy requirements — whether from GDPR, CCPA, internal policy, or contractual obligations — into engineering artifacts that can be tested, verified, and evidenced.

Install this skill when your agent needs to help teams move from "we have a privacy policy" to "we verified deletion within the SLA, here is the evidence, and here is the change review for the new feature that touches PII." It defines the engineering ownership boundary: privacy engineering translates requirements into artifacts; legal interpretation stays with legal counsel; security implementation stays with security engineering; data infrastructure stays with data engineering.

The skill covers seven privacy dimensions (purpose, lifecycle/retention, access, deletion, tenant/isolation, residency, consent) as structured concerns in every artifact. It addresses agent traces (LLM conversation logs, tool-call history) and product analytics telemetry with privacy-specific guidance. It routes jurisdictional questions to legal counsel — it never provides legal advice.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Core methodology: seven privacy dimensions, working method, agent-traces and analytics-telemetry guidance, routing boundaries, core principles, and progressive-disclosure loading guide |
| `references/discovery-brief.md` | Bounded discovery brief comparing legal-strategy, secure-software-engineering, security-audit-methodology, data-engineering, production-readiness, product-analytics-and-measurement, and agent-evals-and-observability with ownership boundaries and routing decisions |
| `templates/data-lifecycle-record.md` | Structured template for tracing each data category from collection through processing, storage, access, archival, and deletion across all stores |
| `templates/privacy-acceptance-criteria.md` | Template for defining verifiable, testable privacy acceptance criteria with criterion description, verification method, and pass/fail condition fields |
| `templates/data-flow-and-access-map.md` | Template for mapping data flows across services, tenants, and geographic regions with access-pattern documentation |
| `templates/retention-deletion-verification-plan.md` | Template for designing a retention/deletion verification plan with measurable success conditions and exercise evidence |
| `templates/privacy-change-review.md` | Template for reviewing a feature, schema, integration, or AI pipeline change for privacy impact |
| `evals/evals.json` | Six output-quality eval cases covering analytics telemetry, agent traces, multi-tenant data, deletion/revocation, residency constraints, and jurisdiction-escalation |

## Quick Start

Start with the seven privacy dimensions in `SKILL.md` to scope the engagement, then use the discovery brief if you need to understand ownership boundaries with adjacent skills. Produce a data-lifecycle record for the data categories in scope, define verifiable acceptance criteria using the template, and design a retention/deletion verification plan that can be exercised.

Ask your agent to "map the data lifecycle for <system>" or "define privacy acceptance criteria for <feature>" and the skill's triggers will route the work.

## Triggers

- Engineering privacy into a system, feature, or data flow: data classification, purpose mapping, data-lifecycle tracing, retention/deletion design, residency constraints, consent flows, tenant isolation, privacy acceptance criteria, privacy change review.
- Work where privacy requirements must be translated into verifiable, testable engineering artifacts rather than policy prose alone.
- Addressing privacy implications of agent traces (LLM conversation logs, tool-call history) or product analytics telemetry.
- Designing multi-tenant data isolation or cross-region data residency at the engineering level.

## Requirements

No runtime dependencies. The methodology is host-neutral and requires no specific tools, platforms, or API keys. Privacy engineering consumes legal requirements as input (from legal counsel or [legal-strategy](../legal-strategy/SKILL.md)) and produces engineering artifacts; it does not provide legal advice or interpret regulatory scope.
