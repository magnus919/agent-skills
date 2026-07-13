# Secure Software Engineering

Build security into software decisions before they become expensive defects.

## Why Install This Skill

This skill helps an agent turn "make it secure" into concrete design choices: what must be protected, who may do what, where trust changes, and how a team can verify the result. It covers everyday engineering work such as APIs, credentials, dependencies, multi-tenant services, release artifacts, and AI features without assuming a cloud provider or framework.

Instead of treating a checklist or scanner as a security guarantee, the workflow asks for evidence, assumptions, misuse cases, and accountable residual-risk decisions. It complements an assessment skill: use this one while building and changing software, then assess or scan separately when that is the actual task.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | A five-phase, prevention-oriented workflow and routing guide. |
| `references/source-index.md` | Version-pinned primary sources and the decisions they inform. |
| `references/` | Focused guidance for threat modeling, controls, review, release, incident learning, and AI systems. |
| `templates/` | Adaptable threat-model, acceptance-criteria, and review-checklist starting points. |

## Quick Start

Install or expose this directory through your Agent Skills-compatible client. Then ask, for example:

```text
Threat-model this multi-tenant document API before implementation.
```

The resulting model should name assets, boundaries, assumptions, abuse cases, mitigations, evidence, and residual risk rather than simply declare the API secure.

## Triggers

- Design or implement a feature securely.
- Threat-model a system, API, integration, tenant boundary, or AI capability.
- Define security acceptance criteria or review a security-sensitive change.
- Choose authentication, authorization, secret handling, dependency, logging, or release-evidence practices.

## Requirements

No runtime dependency, API key, or platform-specific tool is required. The included sources are decision aids; adopt the controls that apply to your organization, contract, regulator, and threat model.
