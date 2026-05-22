# agent-skills

A collection of AI agent skills — reusable workflows, protocols, and knowledge packs for agentic systems. Skills follow the [Agent Skills open format](https://agentskills.io), making them compatible with any agent framework that supports the standard.

## Skills

### [cli-builder](cli-builder/SKILL.md)

Build and refactor CLI tools for AI agent consumption. 10 universal patterns (non-interactive, `--json`, `--dry-run`, idempotent, lazy auth, progressive help), an agent-compatibility test suite, a Python API client pattern, and a bash scaffold template. Principles grounded in real failures from building 15+ agent-facing CLIs.

### [systematic-debugging](systematic-debugging/SKILL.md)

4-phase root cause debugging protocol: understand bugs before fixing.

### [tmdb-cli](tmdb-cli/SKILL.md)

The Movie Database API from the terminal. Search and discover movies and TV by genre, certification, rating, and date range. Check trending, upcoming, and now playing. Free API key from themoviedb.org.

### [jellyfin-cli](jellyfin-cli/SKILL.md)

Jellyfin media server from the terminal. Check server info, browse recently added, search your library by type, list libraries, and view statistics.

### [ghost-cli](ghost-cli/SKILL.md)

Ghost CMS from the terminal. Manage posts and pages, list tags, and check site info. Admin API key from Ghost Integrations.

### [forgejo-cli](forgejo-cli/SKILL.md)

Forgejo or Gitea self-hosted Git forge from the terminal. List repositories, search repos, manage issues, and view pull requests.

### [openlibrary-cli](openlibrary-cli/SKILL.md)

Open Library book metadata from the terminal. Search books and authors, get work and edition details, lookup by ISBN. No API key required.

### [jira-cli](jira-cli/SKILL.md)

Atlassian Jira from the terminal. Search issues with JQL, view details, create issues, add comments, list projects, and transition status.

### [confluence-cli](confluence-cli/SKILL.md)

Atlassian Confluence from the terminal. List spaces, browse pages, view content with body extraction, search with CQL, and create pages.

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

Skills don't require installation in the traditional sense. They are loaded by your AI agent when triggered. Each agent framework documents its own skill directory path and loading mechanism — follow the links below for the authoritative setup guide for your harness.

| Harness | Setup Guide |
|---------|-------------|
| **Claude Code** | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) |
| **OpenCode** | [opencode.ai/docs/skills](https://opencode.ai/docs/skills) |
| **OpenAI Codex** | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) |
| **GitHub Copilot** | [docs.github.com/en/copilot/concepts/agents/about-agent-skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| **Cursor** | [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills) |
| **Gemini CLI** | [geminicli.com/docs/cli/skills](https://geminicli.com/docs/cli/skills) |
| **Hermes Agent** | See below |

### Hermes Agent

Hermes Agent loads skills from `~/.hermes/skills/`, organized by category subdirectory:

```bash
cp -r cli-builder ~/.hermes/skills/devops/
cp -r systematic-debugging ~/.hermes/skills/software-development/
cp -r tempest-cli ~/.hermes/skills/devops/
```

Hermes loads skill metadata at session start. Use the `/skills` command to list available skills, and `skill_view(name)` to load a specific skill's full instructions. Skills can also be pinned for persistent availability.

### Generic / Other Frameworks

The [agentskills.io clients page](https://agentskills.io/clients) maintains an up-to-date list of every agent framework that supports the Agent Skills format, with links to each one's setup instructions. Any framework listed there can load these skills — follow that framework's specific documentation for the correct directory path and loading mechanism.

For frameworks without built-in skill loading, the format is intentionally simple:

1. Place the skill directory in your agent's accessible file path
2. The agent reads `SKILL.md` when triggered by keywords in the task
3. Supporting files in `references/`, `templates/`, and `scripts/` are loaded on demand

You can also instruct your agent to read specific `SKILL.md` files at session start, or reference skills in your agent's system prompt or CLAUDE.md/AGENTS.md.

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
