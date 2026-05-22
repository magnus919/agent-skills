# agent-skills

A curated collection of AI agent skills — reusable workflows, protocols, and knowledge packs for agentic systems.

## What this is

This repo collects skills designed to be loaded by AI agents (Hermes Agent, Claude Code, OpenCode, or compatible frameworks) to give them structured domain knowledge and proven approaches for recurring tasks. Each skill is self-contained, versioned, and designed to slot into an agent's procedural memory.

## Structure

```
agent-skills/
├── research/           # Web research, article capture, knowledge extraction
├── content/            # Blog writing, image generation, creative workflows
├── devops/             # Infrastructure management, deployment, CI/CD
├── software-development/  # Coding patterns, debugging, code review
├── thinking/           # Multi-agent debate (council), structured reasoning
├── note-taking/        # Vault operations, knowledge graphs, session memory
├── mlops/              # Model serving, training, evaluation
├── data-science/       # Analysis, visualization, notebooks
├── productivity/       # Email, calendar, task management
├── creative/           # ASCII art, p5.js, diagrams, video
├── social-media/       # Platform interaction workflows
├── consulting/         # Domain-specific advisory skills
├── media/              # Audio/video processing, music generation
├── github/             # GitHub workflow skills (PRs, issues, code review)
├── red-teaming/        # Security audit, jailbreak testing
├── smart-home/         # Home automation skills
├── gaming/             # Game server management
├── leisure/            # Hobby-adjacent skills
└── templates/          # Skill templates for creating new skills
```

## Skill format

Each skill is a directory containing:

```
skill-name/
├── SKILL.md           # The skill itself (YAML frontmatter + markdown body)
├── references/        # Supporting documentation, research notes
├── templates/         # Config templates, example files
└── scripts/          # CLI tools and automation scripts
```

## License

MIT — use freely, adapt openly, share back if you improve something.
