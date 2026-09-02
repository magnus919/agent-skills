# react — Build and diagnose React applications

## Why Install This Skill

React projects accumulate framework-specific failure modes: hooks that resynchronize unnecessarily, stale requests that overwrite newer data, routes that break under a subpath, and Vite environment values accidentally shipped to browsers. This skill gives your agent a focused operating loop for those problems.

After installation, your agent can inspect a React/Vite project safely, make component and state changes that fit its existing conventions, protect accessible interaction states, and verify the result with the project's own checks. It also includes a read-only doctor for quick diagnostics without installing dependencies or exposing environment values.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | React-specific implementation workflow, guardrails, handoffs, and verification steps |
| `references/component-and-state.md` | Component boundaries, hooks, effects, async state, and forms |
| `references/vite-diagnostics.md` | Vite environment, build, asset-base, and deployment diagnostics |
| `scripts/react-doctor.py` | Bounded Python diagnostic with human-readable or JSON output |
| `scripts/test_react_doctor.py` | Offline tests for diagnostic behavior and safety guarantees |
| `evals/evals.json` | Six substantive output-quality cases for React and Vite work |

## Quick Start

```bash
python3 scripts/react-doctor.py --json .
python3 scripts/react-doctor.py .
```

The doctor reads project files only. It does not install packages, run scripts, contact the network, or print environment values.

## Triggers

Load this skill when working with React, JSX/TSX, hooks, React Router, Vite React configuration, React component/state implementation, or React build failures. Use it for a focused project diagnosis before editing.

## Requirements

- Python 3.8+ for the bundled diagnostic and tests.
- Node.js and the project's package manager for application builds and tests.
- Existing React/Vite project files; no API key is required.
- Use `frontend-engineering` for framework-agnostic frontend architecture, `playwright` for browser automation, and `web-accessibility` for dedicated accessibility audits.
