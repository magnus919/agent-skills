# agent-skills

A collection of AI agent skills — reusable workflows, protocols, and knowledge packs for agentic systems. Skills follow the [Agent Skills open format](https://agentskills.io), making them compatible with any agent framework that supports the standard.

## Skills

### [cli-builder](cli-builder/SKILL.md)

Build and refactor CLI tools for AI agent consumption. 10 universal patterns (non-interactive, `--json`, `--dry-run`, idempotent, lazy auth, progressive help), an agent-compatibility test suite, a Python API client pattern, and a bash scaffold template. Principles grounded in real failures from building 15+ agent-facing CLIs.

### [systematic-debugging](systematic-debugging/SKILL.md)

4-phase root cause debugging protocol: understand bugs before fixing. Covers schema/environment divergence, exception type specificity in fallback chains, progressive characterization grids for API/retrieval failures, dependency source detection (editable dev forks), macOS sandboxed application debugging, and the Rule of Three for recognizing architectural problems. Adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT) with significant expansion from real-world use.

### [tempest-cli](tempest-cli/SKILL.md)

Hyper-local weather from a WeatherFlow Tempest station. Query current conditions, 7-day forecast, historical observations, and real-time UDP broadcasts. A complete reference implementation of the cli-builder patterns in a working, testable project — including the CLI binary and full API field layout reference.

### [software-architecture-analysis](software-architecture-analysis/SKILL.md)

Reverse-engineer a software codebase to understand its architecture, data flow, privacy posture, and feature surface — then produce a clean-room design document, PRD, or migration plan under new constraints (local-first, privacy-first, self-hosted). Includes an interface extraction pattern for designing swappable storage provider abstractions.

### [data-architect](data-architect/SKILL.md)

Act as a virtual data architect. Discover data assets, assess maturity, evaluate platforms, design architectures, establish governance, and create migration plans. Covers modern data patterns (data mesh, data lakehouse, streaming, real-time analytics) with vendor evaluation frameworks and maturity models.

### [agent-skills](agent-skills/SKILL.md)

Reference for the Agent Skills open format itself — directory structure, frontmatter schema, naming conventions, and progressive disclosure model. Use this meta-skill when creating or reviewing any other skill in this repository.

---

## Installation

Skills don't require installation in the traditional sense. They are loaded by your AI agent when triggered. The setup differs slightly by harness.

### Claude Code

Claude Code supports Agent Skills natively. Place skills in your project's `.claude/skills/` directory or in `~/.claude/skills/` for global access:

```bash
# Per-project (recommended)
mkdir -p .claude/skills
cp -r cli-builder .claude/skills/

# Or global for all projects
mkdir -p ~/.claude/skills
cp -r cli-builder ~/.claude/skills/
```

Claude Code automatically indexes skills at startup and loads them based on their `description` field matching the current task.

### OpenCode

OpenCode loads skills from the `skills/` directory in your project or from `~/.opencode/skills/`. Skills must follow the Agent Skills format with valid YAML frontmatter:

```bash
# Project-level
mkdir -p skills
cp -r cli-builder skills/

# Or global
mkdir -p ~/.opencode/skills
cp -r cli-builder ~/.opencode/skills/
```

OpenCode uses the `name` and `description` frontmatter fields for skill discovery. Ensure descriptions include trigger keywords matching your use cases.

### Hermes Agent

Hermes Agent loads skills from `~/.hermes/skills/`. Skills are organized by category subdirectory:

```bash
cp -r cli-builder ~/.hermes/skills/devops/
cp -r systematic-debugging ~/.hermes/skills/software-development/
cp -r tempest-cli ~/.hermes/skills/devops/
```

Hermes loads skill metadata at session start. Use the `/skills` command to list available skills, and `skill_view(name)` to load a specific skill's full instructions. Skills can also be pinned for persistent availability.

### Codex (OpenAI Codex CLI)

Codex CLI supports the Agent Skills format. Consult the [Codex documentation](https://github.com/openai/codex) for the current skill directory path and loading mechanism. The format is the same — valid `SKILL.md` with frontmatter — regardless of the specific directory.

### GitHub Copilot

GitHub Copilot supports Agent Skills in editor and CLI modes. Place skills in `.github/skills/` in your repository root:

```bash
mkdir -p .github/skills
cp -r cli-builder .github/skills/
```

Copilot indexes skills from the repository and loads them based on task context. Skills can be version-controlled alongside your project code.

### Generic / Other Frameworks

Any agent framework that supports reading markdown files can use these skills. The format is intentionally simple:

1. Place the skill directory in your agent's accessible file path
2. The agent reads `SKILL.md` when triggered by keywords in the task
3. Supporting files in `references/`, `templates/`, and `scripts/` are loaded on demand

If your framework doesn't have built-in skill loading, you can:
- Instruct your agent to read specific `SKILL.md` files at session start
- Reference skills in your agent's system prompt or CLAUDE.md/AGENTS.md
- Use a startup script that pre-loads skill content into context

---

## Contributing

Skills follow the [Agent Skills specification](https://agentskills.io/specification.md). See the [agent-skills](agent-skills/SKILL.md) reference skill for format details, and `AGENTS.md` in this repo for agent-specific loading and compliance guidance.

Before submitting a new skill:
1. Ensure `SKILL.md` has valid YAML frontmatter (required: `name`, `description`)
2. The `name` field must match the parent directory name
3. Keep `SKILL.md` under 500 lines and 5,000 tokens
4. Move detailed reference material to `references/` for progressive disclosure
5. Validate with `skills-ref validate ./my-skill` if available

---

## License

MIT — see [LICENSE.md](LICENSE.md) for full terms.
