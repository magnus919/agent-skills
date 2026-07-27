# PACE Plan - Keep Emergency Communications Working When Preferred Paths Fail

## Why Install This Skill

A four-column PACE table is easy to write and hard to operate. Teams still need to know who can activate each fallback, when to stop retrying a failed path, whether two supposedly different methods share the same dependency, and what evidence shows a path actually works.

This skill turns Primary, Alternate, Contingency, and Emergency planning into an owner-approved operating cycle. It helps a group document local facts, coordinate authority and handoffs, troubleshoot failures, run bounded exercises, and convert observations into tracked improvements without inventing technical details or granting itself authority.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | The six-stage workflow, safety boundaries, quality gates, and completion criteria. |
| `DELIVERY-SPEC.md` | The acceptance criteria and traceability record used to remediate the initial research and deliver this skill. |
| `VERIFICATION.md` | The per-criterion delivery verdict, evidence, and verified GitHub correction. |
| `EVIDENCE-LEDGER.md` | The neckbeard change record: inspected artifacts, decisions, checks, boundaries, and rollback triggers. |
| `references/plan-design.md` | A method for communication pairs, path selection, dependency checks, and explicit gaps. |
| `references/coordination-and-operation.md` | Ownership, authority, endpoint alignment, check-ins, transitions, and handoffs. |
| `references/troubleshooting.md` | Evidence-led failure diagnosis that avoids unsafe improvisation. |
| `references/exercise-and-improvement.md` | Bounded exercises, after-action review, corrective actions, and change governance. |
| `references/evidence-base.md` | Directly inspected sources, supported claims, and exclusions. |
| `templates/` | A plan worksheet, check-in card, exercise/AAR, and troubleshooting decision log. |
| `evals/evals.json` | Output-quality cases covering gaps, drills, handoffs, troubleshooting, improvement, and unauthorized activation. |

## Quick Start

No setup or API key is required. Load the skill and provide the mission or essential function, participants, authorized communications capabilities, and known decision authority. Start with `templates/pace-plan-worksheet.md`; leave missing local facts marked `UNKNOWN` with an owner and validation action.

## Triggers

- Build or audit a Primary, Alternate, Contingency, and Emergency communications plan.
- Define owners, activation triggers, check-ins, fallback procedures, or communication-path handoffs.
- Diagnose why a planned emergency communications path failed.
- Plan a PACE drill or convert exercise observations into corrective actions.
- Review whether supposedly redundant methods share infrastructure or other dependencies.

## Requirements

No runtime dependencies. Users must supply local operating procedures, authorized communication details, applicable regulations, and decision authority. The skill does not authorize transmission, activation, or live-system testing.
