# agent-skills

A collection of AI agent skills — reusable workflows, protocols, and knowledge packs for agentic systems.

This repo is being built incrementally. Skills will be added over time as they're curated, refined, and tested.

## What is a skill?

Each skill lives in its own directory with a `SKILL.md` as the entry point, optionally backed by `references/`, `templates/`, and `scripts/` for supporting material. Skills are designed to be loaded by AI agents (Hermes Agent, Claude Code, OpenCode, etc.) as procedural memory — giving them structured domain knowledge and proven approaches for specific tasks.

## Skills

### [cli-builder](cli-builder/SKILL.md)

Design and build CLI tools for AI agent consumption. 10 universal patterns (non-interactive, `--json`, `--dry-run`, idempotent, lazy auth, progressive help), an agent-compatibility test suite, and a bash scaffold template. Principles grounded in real failures from building 15+ agent-facing CLIs.

### [agent-skills](agent-skills/SKILL.md)

Reference for the Agent Skills open format itself — directory structure, frontmatter schema, naming conventions, and progressive disclosure model. Use this meta-skill when creating or reviewing any other skill in this repository.

## License

MIT
