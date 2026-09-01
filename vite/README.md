# Vite Skill - Operate Vite projects safely

## Why Install This Skill

Vite is fast, but small configuration mistakes can produce broken asset URLs, leaked client variables, inaccessible dev servers, or builds that only work from the repository root. This skill gives your agent a practical inspect, change, build, and verify workflow for Vite projects.

After installation, your agent can identify the real Vite and Node toolchain, reason about modes and `import.meta.env`, diagnose plugins and module resolution, validate `base` paths and output directories, and check the built artifact instead of treating an exit code as the whole result.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Vite operating contract, boundaries, workflow, and routing |
| `references/config-and-environments.md` | Config, plugins, modes, env files, aliases, and public assets |
| `references/build-and-deploy.md` | Production builds, asset paths, SPA hosting, and dependency failures |
| `references/dev-server-and-diagnostics.md` | Dev server, proxy, preview, host safety, and troubleshooting |
| `scripts/vite-doctor` | Bounded JSON diagnostic for Node, package manager, Vite, config, and env names |
| `scripts/test_vite_doctor.py` | Deterministic tests for the diagnostic script |
| `evals/evals.json` | Five output-quality evaluation cases |

## Quick Start

From a Vite project, run the diagnostic without exposing environment values:

```sh
/path/to/vite/scripts/vite-doctor --project . --json
```

Then use the package manager script already declared by the project:

```sh
npm run build
npm run preview
```

## Triggers

Load this skill when a task involves:

- `vite`, `vite.config.*`, Vite plugins, or a Vite migration
- `import.meta.env`, modes, `.env` loading, or public assets
- Vite dev server, proxy, preview, or host/port behavior
- Production build failures, chunk output, `base`, or static deployment
- Checking the installed Node, package manager, or Vite version

## Requirements

- Python 3.8+ for `scripts/vite-doctor`
- Node.js and the project's package manager for Vite commands
- A supported Vite version and framework plugin as declared by the project
- Network access only when installing approved dependencies or consulting documentation
