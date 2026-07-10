# Workflow Architect — Discover and Encode Your Actual Workflow

A meta-skill that helps you understand how you actually work, then generates a loadable skills bundle encoding your workflow as agent-triggerable skills. Turns implicit process into explicit, reusable capability.

## Why Install This Skill

When your agent loads this skill, it becomes a **process discovery specialist** who can:

- **Discover your workflow** — through active interview (8-15 guided questions) or passive observation (analyzing what you actually do)
- **Generate a skills bundle** — loadable skills with trigger conditions that encode each phase of your workflow
- **Create a decision map** — Mermaid flowchart visualizing your workflow as your agent sees it
- **Optionally set up a kanban board** — if your workflow has a predictable linear path
- **Make it permanent** — generated bundle is registered in your agent's skill system for future sessions

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Bundle umbrella — two modes: active interrogation or passive observation |
| `skills/` | 3 sub-skills: interviewer (active mode), observer (passive mode), bundle-builder (generation engine) |
| `references/` | Workflow archetypes library, trigger condition patterns, kanban decision criteria |
| `templates/` | 4 templates: skill skeleton, manifest, kanban setup, decision map |
| `references/example-output/` | Two worked examples: developer pipeline, developer triage |

## Two Modes

- **Active Interrogation** — guided interview that asks structured questions and branches based on your answers.
- **Passive Observation** — watches what you do in a session and infers your workflow patterns without interrupting.

Both modes feed into the bundle-builder, which generates the final skills bundle.

## Triggers

Load this when you want to understand your own process, formalize a workflow, share it with collaborators, or give structure to a session that feels aimless.

## Requirements

Hermes Agent (uses skill_view, memory, session context scanning, write_file for bundle generation). Output bundles are standard Agent Skills format.
