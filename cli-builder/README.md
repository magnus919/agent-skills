# CLI Builder — Design Agent-Friendly CLI Tools

A comprehensive design guide and scaffold for building CLI tools that **AI agents can actually use**. 10 universal design patterns grounded in real failures from building 15+ agent-facing CLIs.

## Why Install This Skill

When your agent loads this skill, it can **design, build, and refactor CLI tools** that agents can discover and use without human help. That means:

- **Every `--help` output becomes a contract** the agent parses to understand your tool
- **Every command supports `--json`** for machine-readable output the agent consumes
- **Every operation is idempotent** — `--dry-run` previews changes before they happen
- **Authentication is lazy** — help and dry-run work without credentials
- **Errors are structured** — different exit codes for different failure modes

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | 500+ line reference: 10 design patterns, 3-phase build workflow, agent-compatibility test suite |
| `templates/` | Python API client scaffold and bash CLI scaffold |
| `references/` | Agent-compatibility test suite, Python API client pattern |

## Triggers

Load this when building a new CLI tool, refactoring an existing tool that causes agent friction, or debugging why your agent keeps failing to use a CLI properly.

## Requirements

Bash, Python 3.8+, jq, and a standard Unix CLI environment.


## Quick Start

Start with the setup and first workflow in SKILL.md, then use the linked resources for the specific task you need to complete.
