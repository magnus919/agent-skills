# C4 Diagramming

Make system boundaries, responsibilities, and relationships legible at the architectural level appropriate to the reader.

## Why Install This Skill

Make system boundaries, responsibilities, and relationships legible at the architectural level appropriate to the reader. It preserves a practical method, local reference material, and reusable templates so an agent can do more than produce a generic answer.

Use it when the work needs a repeatable process and an inspectable result. It is portable across Agent Skills-compatible clients and does not require a profile system or a particular task orchestrator.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, workflow, and guidance for loading deeper resources. |
| `references/` | Reference material for C4 levels, architecture-as-code tooling, CI, and communication review, including `technical-diagram-communication.md`. |

## Quick Start

Choose the C4 level and authoring format in `SKILL.md`, load the matching reference before drawing, and review the rendered artifact for the audience's job rather than syntax alone.

Install or expose this directory using your agent's standard Agent Skills loading mechanism, then ask for work that matches the triggers below.

## Triggers

- Create C4 software-architecture diagrams using Mermaid or Structurizr. Use when teams need clear system context, container, component, or code-level views.
- Requests involving the method, deliverables, or review process described in `SKILL.md`.
- Requests to make a C4 diagram understandable to a particular audience or to review its hierarchy, narrative, labels, uncertainty, or accessible fallback.
- Work where a reusable template or reference from this skill would reduce avoidable mistakes.

## Requirements

Mermaid or Structurizr tooling is optional and only needed to render or validate diagrams.

## Source and maintenance

This skill was extracted from [`magnus919/hermes-profiles`](https://github.com/magnus919/hermes-profiles) at commit [`867a555`](https://github.com/magnus919/hermes-profiles/commit/867a555). The portable methodology was retained; Hermes-specific profile, orchestration, and memory assumptions were removed.
