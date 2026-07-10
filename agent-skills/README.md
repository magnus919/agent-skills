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
| `SKILL.md` | Complete format reference: frontmatter schema, name constraints, description patterns, directory structure, and progressive disclosure model |
| `references/` | Referenced in the body for format best practices |

## When to Load This Skill

- You're creating a new skill and need to know the correct format
- You're reviewing an existing skill for format compliance
- You want your agent to generate a valid SKILL.md scaffold
- You're setting up conventions for a shared skill repository

## Requirements

None — this is a documentation skill. No scripts, no API keys, no dependencies.
