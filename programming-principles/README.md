# Programming Principles — 14 Classic Software Books

Distilled coding principles from 14 classic software engineering books, organized for agent consumption. Cross-cutting principles by concern, task-to-book mapping, per-book rule sets at two depths, and a structured code-assessment workflow.

## Why Install This Skill

When your agent loads this skill, it gains a **shared vocabulary for code quality** grounded in established literature rather than vibes. That means:

- **Principled code review** — findings cite specific books and principles, not just "this looks wrong"
- **Task-aware loading** — a task-to-book mapping table tells the agent which principles matter for the current work (refactoring? load Refactoring + WELC. architecture? load APoSD + Clean Architecture)
- **Progressive depth** — SKILL.md has enough to change decisions; reference files provide per-book depth on demand
- **Structured assessment** — a reproducible workflow for combining all 14 books against a real repo

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Cross-cutting principles by concern, task-to-book mapping, per-book compressed rule cards, compatibility guide |
| `references/*.mini.md` | 14 per-book mini rule sets with triggers, decision rules, and checklists |
| `references/*.full.md` | 14 complete rule catalogs (11–63 KB each) for deep reference or audits |
| `references/code-assessment-workflow.md` | Structured workflow for combining all books against a real repo |

## Triggers

Load this skill for code review, refactoring, implementation quality assessment, architecture decisions, or any coding task where you want principled guidance rather than ad-hoc judgment. Also load when performing a structured code assessment against a repository.

## Requirements

Platform-agnostic. Works with any agent that supports the Agent Skills directory format. No external dependencies.

## Quick Start

Load SKILL.md for the core principles and task-to-book mapping. When a specific book's guidance is needed, load the corresponding `references/<book>.mini.md`. For deep audits, load the `.full.md` variant.
