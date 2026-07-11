# Agent Skills — The Standard Itself

This skill is the **meta-skill**: it documents the [Agent Skills](https://agentskills.io) open format itself. Every other skill in this repository follows the conventions defined here.

## Why Install This Skill

When your agent loads this skill, it gains the ability to **create, review, and edit valid Agent Skills-format skills**. That means:

- **Your agent can build new skills on demand.** Describe a workflow you want encoded, and your agent can scaffold a valid SKILL.md with correct frontmatter, progressive disclosure structure, and agent-friendly descriptions.
- **Existing skills stay valid.** When your agent edits a skill, it checks against the format standard — no broken frontmatter, no missing required fields.
- **Consistency across your skill library.** Every skill in your repository follows the same conventions, making them loadable by any Agent Skills-compatible harness.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | A create-and-review workflow, the core format rules, and a completion checklist |
| `references/specification.md` | A bundled snapshot of the official format specification |
| `references/best-practices.md` | Guidance for useful, well-scoped instructions |
| `references/optimizing-descriptions.md` | How to design and test reliable automatic triggers |
| `references/using-scripts.md` | How to bundle safe, agent-friendly executable helpers |
| `references/evaluating-skills.md` | A practical evaluation loop for testing skill quality |
| `references/client-implementation.md` | Guidance for products that discover and load skills |

## Quick Start

Ask your agent to create or review a skill, then load this skill first. For a structural check, run:

```bash
skills-ref validate path/to/skill
```

If the reference validator is not installed, your agent should report that clearly and complete the equivalent manual checks.

## Triggers

- You're creating a new skill and need to know the correct format
- You're reviewing an existing skill for format compliance
- You want your agent to generate a valid SKILL.md scaffold
- You're setting up conventions for a shared skill repository

## Requirements

The documentation itself has no runtime dependencies. Optional validation uses the `skills-ref` reference library; install it in an isolated environment when you want to run its CLI.
