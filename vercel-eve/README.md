# Vercel Eve skill

Build and operate durable AI agents with Vercel Eve, including the parts that matter when you leave Vercel’s managed platform.

## Why Install This Skill

Eve makes an agent legible: instructions, tools, skills, subagents, integrations, schedules, and sandboxing live in predictable files. That gives an agent project the shape of an application rather than a pile of prompts and callbacks.

The hard part is deployment. This skill keeps the distinction clear between “the Node server started” and “durable agent work survives restart, resumes through the proxy, protects credentials, and produces usable traces.” It covers both Vercel and self-hosted Node deployments.

## What You Get

| Resource | Purpose |
|---|---|
| `SKILL.md` | Development, deployment, security, and verification workflow |
| `references/development-and-architecture.md` | Agent-directory model, tools, skills, subagents, connections, sandboxing, and observability |
| `references/deployment-and-self-hosting.md` | Vercel versus Node hosting, persistent workflow state, reverse proxy, model, auth, scheduling, and validation requirements |
| `references/source-index.md` | Official documentation and repository sources |
| `evals/evals.json` | Representative skill-quality scenarios |

## Quick Start

```sh
npx eve@latest init my-agent
cd my-agent
npm run dev
```

For a self-hosted service:

```sh
eve build
PORT=3000 eve start --host 0.0.0.0
```

Do not expose it until persistent workflow storage, authentication, proxy routes, and a real session have been verified.

## Triggers

Use this skill when building an Eve agent, adding tools or skills, configuring subagents, sandboxes, sessions, schedules, channels, connections, telemetry, Vercel deployment, or self-hosted Eve infrastructure.

## Requirements

Current Eve requires Node.js 24+. An agent needs an LLM provider credential or AI Gateway access. Production self-hosting also needs persistent storage for workflow state, an authentication policy, and an appropriate sandbox backend for any generated command or code execution.