---
name: product-discovery
description: >-
  Discover product requirements from human stakeholders — map who to talk to,
  ask questions that surface hidden assumptions, detect gaps in real time,
  resolve conflicts, and translate conversations into structured SDD specs.
  Phase 0 upstream of Spec-Driven Development.
license: MIT
compatibility: Agent-agnostic — works with any agent supporting a spec-driven or requirements pipeline.
---

# Product Discovery — Stakeholder Map

Pre-discovery work begins before any conversation. Load this reference first when planning discovery:

| Reference | Load when | File |
|-----------|-----------|------|
| Stakeholder Mapping & Sequencing | You need to decide who to interview and in what order | `references/stakeholder-mapping.md` |
| Interview Protocol Design | You're designing a question stack for a specific stakeholder type | `references/question-patterns.md` |
| Gap Detection Techniques | You're preparing to recognize what stakeholders don't say | `references/gap-detection.md` |

## Pipeline: Phase 0 — Discovery

```
RAW NEED → [MAP] → [INTERVIEW] → [SYNTHESIZE] → [DISTILL] → [VALIDATE] → SPEC.md
              |           |              |            |            |
         Who to       What to        Resolve      Convert to   Stakeholder
         talk to      ask            conflicts    structured   review
```

Load the reference for the phase you're entering.

## Trigger Conditions

Load this skill when:
- You're starting product discovery for a new feature or project
- You have a vague idea that needs to become a structured specification
- You need to interview stakeholders but don't have a protocol
- You have raw interview notes that need to become a SPEC.md
- You're about to enter Phase 1 (SPECIFY) of SDD and need upstream input
- You're evaluating whether you've done enough discovery work

## Loading Guide

| Phase | Load When | File |
|-------|-----------|------|
| MAP | You need to identify who to interview, in what order, and how to find the right stakeholders | `references/stakeholder-mapping.md` |
| INTERVIEW | You're about to conduct stakeholder interviews and need question patterns, gap detection, and conflict handling | `references/question-patterns.md` + `references/gap-detection.md` + `references/conflict-resolution.md` |
| SYNTHESIZE | You have raw interview notes and need to identify conflicts, risks, and gaps before distillation | `references/conflict-resolution.md` |
| DISTILL | You need to transform interview notes into structured SPEC.md with ACs, edge cases, and NFRs | `references/transcript-to-spec.md` |
| VALIDATE | You have a draft spec and need to verify interpretations with stakeholders | `references/transcript-to-spec.md` (Interpretation Audit Trail section) |

## Cross-Cutting Concerns

These dimensions apply across all phases. Load when relevant:

| Concern | Load when | File |
|---------|-----------|------|
| AI-conducted discovery | An AI agent is conducting discovery interviews | `references/ai-conducted-discovery.md` |
| Power dynamics | Stakeholders span multiple organizational levels; hierarchy may distort responses | `references/power-dynamics.md` |
| Time constraints | Stakeholder time is limited; need maximum signal extraction | `references/time-constrained-discovery.md` |

## Templates

| Template | Load when | File |
|----------|-----------|------|
| Discovery Plan | You need to structure the full discovery effort — stakeholder map, interview schedule, timeline | `templates/discovery-plan.md` |
| Interview Guide | You need a structured question stack for an interview session | `templates/interview-guide.md` |
| Distillation Worksheet | You're transforming raw notes into structured spec components | `templates/distillation-worksheet.md` |
| Gap Register | You need to track unresolved gaps, deferred decisions, and open questions across interviews | `templates/gap-register.md` |
| Interpretation Log | You need to track every translation from stakeholder language to spec language | `templates/interpretation-log.md` |

## Quick Reference: Is Discovery Complete?

Before handing off to SDD Phase 1 (SPECIFY), check:

- [ ] All stakeholder types interviewed (knowledge holders, authority holders, affected parties, implementation knowers)?
- [ ] At least 3 independent sources for every requirement?
- [ ] Abstract nouns decomposed into measurable thresholds?
- [ ] Conflicts resolved or documented with decision-maker identified?
- [ ] Edge cases extracted from stakeholder anecdotes?
- [ ] Every AC classified: SAID / IMPLIED / INTERPRETED / INFERRED?
- [ ] HIGH-risk interpretations identified and flagged for validation?
- [ ] Gaps, deferred decisions, and avoided topics documented?
- [ ] Stakeholder validation loop completed?
- [ ] Interpretation audit trail preserved for handoff?
