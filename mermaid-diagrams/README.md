# Mermaid Diagrams

Create maintainable diagrams that render reliably in the documentation surfaces where readers actually encounter them.

## Why Install This Skill

Create maintainable diagrams that render reliably in the documentation surfaces where readers actually encounter them. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material: `c4-mermaid.md`, `c4-to-flowchart.md`, `flowchart.md`, `mmdc-spacing-config.md`, `pdf-rendering-pipeline.md`, `portrait-layout.md`, `sequence.md` |
| `scripts/` | Scripts: `validate-mermaid.sh` |

## Quick Start

Choose the diagram type in `SKILL.md`, author the smallest useful diagram, and render it with the documented verification path.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Author, render, and troubleshoot Mermaid diagrams for documentation, architecture, processes, and technical communication. Use when a text-based diagram needs to stay versionable.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

Mermaid rendering requires a compatible renderer. The optional CLI examples use Mermaid CLI and its documented Node.js runtime.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
