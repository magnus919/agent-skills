# AGENTS.md — Agent Guide for agent-skills

This file tells AI agents how to load and use skills from this repository. Skills in this repo follow the [Agent Skills open format](https://agentskills.io) — a standardized way to give agents new capabilities through structured markdown files.

## Format Compliance

Every skill in this repository conforms to the [Agent Skills specification](https://agentskills.io/specification.md):

| Requirement | Rule |
|-------------|------|
| Directory | Each skill in its own directory named by the skill |
| Entry point | `SKILL.md` with YAML frontmatter + markdown body |
| `name` field | Lowercase, hyphens only, matches parent directory name |
| `description` field | Trigger-oriented, starts with an imperative verb, defines both positive and negative trigger boundaries |
| Progressive disclosure | Core instructions in `SKILL.md` (< 500 lines, < 5,000 tokens), supporting material in `references/`, `templates/`, `scripts/` |
| File references | Relative paths from skill root, one level deep |
| **Human-readable README** | **`README.md`** in skill root — required for every skill. See [README Format](#readme-format) below |

## README Format

Every skill directory **MUST** contain a `README.md` written for a **human audience** (not an AI agent). The README explains what the skill does and why someone would want to install it. It is the public face of the skill — the first thing a human sees when browsing the repository.

### Required Sections

| Section | Purpose |
|---------|---------|
| **Title** | Skill name + one-line summary of what it does |
| **Why Install This Skill** | 2-3 paragraph pitch answering "what problem does this solve for me?" and "what can my agent do after installing this?" — written in plain language, not format docs |
| **What You Get** | Table listing directory contents (scripts, references, templates, assets) and what each provides |
| **Quick Start** | Minimal setup: env vars to export, first command to run (omit for reference-only skills) |
| **Triggers** | List of trigger conditions that tell someone when to load this skill |
| **Requirements** | Dependencies, API keys, Python version, system tools |

### Style Guidance

- **Lead with benefit, not implementation.** Answer "what does this do for me?" before "what tech is it built on?"
- **Be concrete.** Show real command examples with expected output. Avoid abstract descriptions.
- **Assume the reader is human.** No agent instructions, no JSON schemas, no progressive disclosure notes. Those go in `SKILL.md`.
- **Keep it scannable.** Use tables, code blocks, and bullet lists. A human should grasp the skill's purpose in 10 seconds.
- **One page or less.** A README that takes more than a minute to read is too long. Save depth for `SKILL.md`.

### Example

See [data-scientist/README.md](data-scientist/README.md) or any skill in this repository for the canonical format.

## State-Modifying Skills

Skills that change external state must say so explicitly and use this gate before the first mutation:

> Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.

Destructive operations still require an explicit user directive; this convention does not authorize deletion, privilege changes, or irreversible cleanup.

## Failure-Mode Routing

For problem-pattern routing, start with [FAILURE-MODE-INDEX.md](FAILURE-MODE-INDEX.md).

## How to Load Skills

Skills are loaded progressively in three stages:

### Stage 1 — Metadata

At session start, read each skill's `name` and `description` from frontmatter. This takes ~100 tokens per skill and lets you know what's available without loading full content.

```yaml
# Example metadata (from cli-builder/SKILL.md)
name: cli-builder
description: >-
  Build or refactor CLI tools designed for AI agent consumption: non-interactive,
  flag-driven, idempotent, with --json output and --dry-run preview.
```

### Stage 2 — Full Instructions

When a user's request matches a skill's description keywords, load the full `SKILL.md`. The body contains step-by-step instructions, examples, and gotchas. Do not load skills preemptively — only load when triggered.

### Stage 3 — Supporting Files

Reference files (`references/`, `templates/`, `scripts/`) are loaded on demand. The `SKILL.md` tells you when to read each one. Do not load all references at activation time — following the triggers preserves context.

## Reading Order

If this is your first session with this repo, read these in order:

1. [agent-skills/SKILL.md](agent-skills/SKILL.md) — The Agent Skills format reference. Read this first to understand the format.
2. [README.md](README.md) — Skill index with descriptions. Use to discover which skill to load.
3. Individual skill `SKILL.md` files as triggered by the user's task.

## Skill Routing

Use each skill's `description` field as the primary routing source. For keyword lookup, see the [skill trigger index](references/skill-triggers.md).

## Use-When Sections

Every skill description must start with an imperative verb and define both when to load it and when not to. Skills with meaningful overlap should also include a `## When not to use` section naming the nearest alternative or prerequisite. Keep these sections trigger-oriented and concise; implementation details belong in references. The repository's quality validator enforces these requirements on changed skills.

## Eval Requirements

Every new skill must include `evals/evals.json` with at least five representative output-quality cases. Each case needs a realistic prompt, an expected outcome, and observable assertions. Trigger-only checks (should-trigger / should-not-trigger probes) are harness-specific and belong in a separate test set, not in `evals/evals.json`.

Existing skills are grandfathered via `scripts/grandfathered-skills.txt`. As overall eval coverage climbs past 25%, modified skills without evals receive a warning; past 50%, they fail CI. The coverage report is available via `python3 scripts/eval-coverage.py`.

## Best Practices

### Do Load by Trigger

The `description` field is the trigger mechanism. If the user's request contains keywords matching a skill's description, load that skill. If multiple skills match, load the most specific one.

### Don't Load Everything at Startup

Loading every skill at session start wastes context. Let the conversation trigger loading. Skills load in ~100 tokens (metadata) and only expand when needed.

### Follow Progressive Disclosure

When a skill body tells you to read a reference file only under specific conditions ("Read this if the API returns a 500"), do not read it proactively. Reference files are for specific edge cases, not general instruction.

### Completion and Exit Conditions

Skills that perform diagnosis, planning, or multi-step work must state when they are complete and when to stop. A valid exit condition is an observable artifact or a bounded escalation, such as: deliver the requested file, confirm the current setup is adequate, or stop after three non-converging diagnostic passes and report the evidence.

## Validate Your Output

When creating or modifying a skill in this repo, validate against the format:
- `name` matches parent directory name
- `description` is 1-1024 chars, non-empty, starts with an imperative verb, and defines a negative boundary
- Body under 500 lines and 5,000 tokens
- All file references use relative paths from skill root
- Frontmatter YAML is valid
- **`README.md` exists in the skill root** with all required sections (see [README Format](#readme-format) above)
- **README is written for humans** — no agent instructions, JSON schemas, or progressive disclosure notes in the README. Those belong in `SKILL.md`.
- **`evals/evals.json` exists** with at least five output-quality cases for new skills (see [Eval Requirements](#eval-requirements))

### Generated Artifacts

This repository tracks generated catalog files (`.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `llms.txt`). CI validates that these are current; it does not regenerate them. If CI reports a stale artifact, regenerate locally:

```sh
ruby scripts/gen-claude-marketplace.rb --write
ruby scripts/gen-codex-plugin.rb --write
ruby scripts/gen-llms-txt.rb --write
```

Each script also runs in check mode (without `--write`) to verify freshness.

### Respect Attribution

Some skills in this repo are adapted from other open-source projects. Attribution is maintained in the source field. Do not remove or modify attribution.

## Troubleshooting

**Skill not loading when expected:** The `description` field may need trigger keyword updates. Check that the user's phrasing overlaps with the skill's description vocabulary.

**Skill body too large:** The agent's context window may be full. The spec recommends under 5,000 tokens per skill. If a skill is exceeding this, its content can be further split into references.

**Reference file not found:** All file references use relative paths from the skill's directory root. If a reference is missing, check that the file exists at the path specified.
