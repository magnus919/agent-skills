# agent-production-operations — runtime control plane for AI agents

Take an evaluated agent from "passes tests" to "safe in production" with
versioning, staged rollout, fallback, cost and latency monitoring, escalation,
and disablement — all feeding back into better evaluations.

## Why Install This Skill

You have an AI agent that passes your evaluation suite. The evals are solid, the
observability is in place, and the agent looks ready. But between "passes evals"
and "safe at scale" there is an operational gap no single specialist skill fills:
how do you version the model, prompt, and tools together? How do you roll out
gradually instead of flipping a switch? What happens when the model regresses,
a tool goes down, the cost budget blows up, or the agent tries something it
shouldn't?

This bundle gives you a runtime control plane purpose-built for AI agents. It
does not replace your release pipeline, your SRE practices, your security
reviews, or your eval framework — it sits between them, coordinating the
decisions that are specific to operating an agent with tools and authority in
production. It distinguishes read-only agents from side-effect-capable agents
and customer-facing agents from internal ones, because a search bot and a
support bot that can modify accounts have fundamentally different operational
risk profiles.

After installing this skill, your agent can answer: what authority do I have,
what happens when I'm uncertain, when do I escalate to a human, how do I fall
back safely, and when should I be disabled entirely. Your team can answer: how
do production incidents feed back into better evaluations, and how do eval
results gate the next release.

## What You Get

| Path | What it provides |
|---|---|
| [SKILL.md](SKILL.md) | Umbrella entry point — runtime control plane routing table, concrete authority/escalation/fallback/disablement parameters, and specialist-skill orchestration |
| [README.md](README.md) | This file — human-facing overview |
| [AGENTS.md](AGENTS.md) | Agent loading and nested-skill discovery notes |
| [references/discovery-brief.md](references/discovery-brief.md) | Bounded discovery brief defining boundaries with agent-evals, release, SRE, security, and platform skills |
| [references/agent-production-contract.md](references/agent-production-contract.md) | Production contract template — capability, authority, uncertainty, escalation, and side-effect contracts with production-readiness and incident-learning inputs |
| [references/runtime-control-plan.md](references/runtime-control-plan.md) | Versioning (model, prompt, tool, policy, evaluator), four-stage rollout plan, and fallback paths with concrete triggers |
| [references/tool-authority-health.md](references/tool-authority-health.md) | Health record schema for tracking tool availability, tool failure, authority usage, authority breaches, cost, and latency over time |
| [references/trace-to-eval-feedback.md](references/trace-to-eval-feedback.md) | Production-to-evaluation feedback loop — how traces and incidents become eval cases and gate releases |
| [evals/evals.json](evals/evals.json) | Integrated eval cases covering read-only agents, side-effect agents, model regression, tool outages, cost breaches, and human escalation |
| [manifest.yaml](manifest.yaml) | Machine-readable bundle manifest (schema v1): purpose, audience, stages, included skills, prerequisites, outputs, handoffs, conflicts, and eval suite |

## Quick Start

1. Start with an agent that has passed evaluation (use
   [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md)).

2. Define the agent's production contract using
   [references/agent-production-contract.md](references/agent-production-contract.md).
   Fill in capability, authority, uncertainty, escalation, and side-effect fields.

3. Consume the most recent production-readiness review outcome for the agent's
   host service from
   [production-readiness](../../production-readiness/SKILL.md) and any open
   incident-learning records from
   [incident-learning](../../incident-learning/SKILL.md). Record both in the
   contract.

4. Plan versioning, staged rollout, and fallback using
   [references/runtime-control-plan.md](references/runtime-control-plan.md).

5. Begin Stage 1 rollout (shadow/dry-run). Record tool and authority health in
   [references/tool-authority-health.md](references/tool-authority-health.md).

6. Advance through stages as exit criteria are met. At each stage boundary,
   review the health record for authority breaches, tool degradation, cost
   trends, and latency patterns.

7. When escalation or fallback triggers fire, follow the concrete procedures in
   [SKILL.md](SKILL.md).

8. Feed production traces and incidents back into evaluation cases using
   [references/trace-to-eval-feedback.md](references/trace-to-eval-feedback.md).

## Triggers

Load this bundle when:
- You are operating an agent that has passed evaluation and is being promoted to production.
- You need to define a staged rollout with progressive authority expansion.
- You need versioning across model, prompt, tools, policy, and evaluator.
- You need fallback, escalation, and disablement procedures for an agent.
- You need a production-to-evaluation feedback loop.
- You see terms like "agent authority," "tool health," "agent cost budget," "agent latency SLO," or "agent disablement."

Do NOT load this bundle for:
- Building an agent from scratch — use your agent framework skill.
- Designing evaluations or observability — use `agent-evals-and-observability`.
- General release engineering — use `release-engineering`.
- General SRE or incident response — use `site-reliability-engineering`.
- General security engineering — use `secure-software-engineering`.
- Platform infrastructure — use `platform-engineering`.

## Requirements

- An agent that has passed evaluation (observability and eval infrastructure
  must exist — see `agent-evals-and-observability`).
- A designated escalation channel (human operator or team).
- A cost budget and attribution mechanism for the agent.
- Production-readiness review process in place (see `production-readiness`).
- Incident-learning process in place (see `incident-learning`).
- No additional API keys, services, or runtime dependencies beyond what the
  agent already requires.
