---
name: agent-skills
description: >-
  Reference for the Agent Skills open format — the directory structure, SKILL.md
  frontmatter schema, naming conventions, progressive disclosure model, and best
  practices for creating skills. Use this whenever creating, reviewing, or editing
  skills in this repository to ensure they follow the standard spec.
license: MIT
compatibility: Compatible with any agent supporting the Agent Skills format (Hermes Agent, Claude Code, GitHub Copilot, OpenCode, Cursor, etc.)
metadata:
  source: https://agentskills.io
  spec-version: "1.0"
---

# Agent Skills Standard Reference

This skill documents the [Agent Skills](https://agentskills.io) open format — a standardized way to give AI agents new capabilities and expertise. **Follow these conventions when creating or editing skills in this repo.**

> Source: [agentskills.io/specification.md](https://agentskills.io/specification.md)

---

## Directory Structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## SKILL.md Format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown body content.

### Frontmatter Fields

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64 chars. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen. **Must match the parent directory name.** |
| `description` | Yes | Max 1024 chars. Non-empty. Describes what the skill does and when to use it. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Indicates environment requirements. |
| `metadata` | No | Arbitrary key-value mapping. |
| `allowed-tools` | No | Space-separated string of pre-approved tools. (Experimental) |

#### `name` field rules
- 1–64 characters
- Only lowercase unicode alphanumeric (`a-z`, `0-9`) and hyphens (`-`)
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

#### `description` field rules
- 1–1024 characters
- Should describe both **what** the skill does and **when** to use it
- Should include specific keywords that help agents identify relevant tasks

### Body Content

The Markdown body has no format restrictions beyond being helpful to the agent. Recommended sections:

- **Step-by-step instructions** — the procedure the agent should follow
- **Examples of inputs and outputs** — what data looks like going in and coming out
- **Common edge cases** — situations the agent might not handle correctly without guidance
- **Gotchas** — environment-specific facts that defy reasonable assumptions

Keep `SKILL.md` under **500 lines and 5000 tokens**. Move detailed reference material to separate files in `references/`.

## Progressive Disclosure

Agents load skills in three stages:

1. **Metadata** (~100 tokens): `name` and `description` loaded at startup for all skills
2. **Instructions** (< 5000 tokens recommended): Full `SKILL.md` loaded when activated
3. **Resources** (as needed): Files in `scripts/`, `references/`, `assets/` loaded on demand

## Optional Directories

### `scripts/`
Executable code agents can run. Scripts should:
- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully
- Use relative paths from the skill root (e.g., `scripts/extract.py`)

### `references/`
Additional documentation loaded on demand. Keep individual files focused — agents load these when instructed, so smaller files save context.

### `assets/`
Static resources: templates, images, data files, schemas.

## File References

Use **relative paths from the skill root** when referencing other files:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

## Writing Effective Descriptions

The `description` field is a skill's only trigger mechanism. Follow these principles:

- **Use imperative phrasing.** "Use this skill when..." rather than "This skill does..."
- **Focus on user intent, not implementation.** Describe what the user is trying to achieve.
- **Err on the side of being pushy.** Explicitly list contexts where the skill applies.
- **Keep it concise.** A few sentences to a short paragraph is right.

## Best Practices

### Start from real expertise
Feed domain-specific context into skill creation. Skills grounded in real project artifacts (runbooks, API specs, code review comments, actual failure cases) outperform ones synthesized from generic knowledge.

### Spend context wisely
Focus on what the agent wouldn't know without the skill: project-specific conventions, domain-specific procedures, non-obvious edge cases. Don't explain general concepts the agent already knows.

### Calibrate control
- **Give freedom** when multiple approaches are valid — describe *why*, not just *what*
- **Be prescriptive** when operations are fragile or a specific sequence must be followed
- **Provide defaults, not menus** — pick one approach, mention alternatives briefly
- **Favor procedures over declarations** — teach *how to approach* a class of problems, not *what to produce* for one instance

### Design coherent units
Scope skills like functions: one coherent unit of work that composes well with other skills. Too narrow → multiple skills needed for one task. Too broad → hard to activate precisely.

### Use gotchas sections
The highest-value content is often environment-specific corrections — things the agent will get wrong unless told otherwise. When an agent makes a mistake, add the correction to the gotchas section.

### Provide output templates
When output needs a specific format, provide a template inline or in `assets/`. Agents pattern-match well against concrete structures.

## Validation

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library to validate skills:

```bash
skills-ref validate ./my-skill
```

This checks that `SKILL.md` frontmatter is valid and follows all naming conventions.
