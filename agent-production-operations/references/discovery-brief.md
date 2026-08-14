# Discovery Brief — agent-production-operations Bundle

## Survey scope

This brief surveys the existing repository at base SHA `8226bcc` to define the
boundary between the `agent-production-operations` bundle and five specialist
skills it composes, plus two production-skill artifacts it consumes.

### Surveyed specialist skills

| Skill | Directory | What it owns | What the bundle must NOT duplicate |
|---|---|---|---|
| agent-evals-and-observability | `../../agent-evals-and-observability/SKILL.md` | Agent evaluation design, observability instrumentation, trajectory analysis, regression detection, release-gate eval suites | General eval methodology, observability pipeline architecture, eval harness design |
| release-engineering | `../../release-engineering/SKILL.md` | Release planning, versioning, pipeline promotion, rollout/rollback design, release readiness | General release mechanics, CI/CD pipeline design, artifact management |
| site-reliability-engineering | `../../site-reliability-engineering/SKILL.md` | Reliability engineering, incident response, operational recovery, SLO/SLI definition, error budgets | General SRE methods, incident command, infrastructure reliability |
| secure-software-engineering | `../../secure-software-engineering/SKILL.md` | Security design, threat modeling, secure coding, trust-boundary validation | General security engineering, vulnerability management, access-control architecture |
| platform-engineering | `../../platform-engineering/SKILL.md` | Platform capabilities, infrastructure provisioning, service mesh, compute/storage/networking | General platform design, infrastructure-as-code, capacity planning |

### Consumed production artifacts

| Skill | What the bundle consumes | How it is used |
|---|---|---|
| production-readiness | `../../production-readiness/SKILL.md` | Go/no-go/defer/exception outcomes from production-readiness reviews feed agent authority-gating and disablement decisions. An agent whose service or tools have not passed a readiness review is restricted to a reduced authority profile. |
| incident-learning | `../../incident-learning/SKILL.md` | Verified-closure records and follow-up work maps from incident-learning feed escalation thresholds and trace-to-eval feedback. An unresolved incident with agent-attributed root cause triggers an authority downgrade. |

## What the bundle owns

This bundle owns the **runtime control plane** between a passing evaluation and
safe production use:

- **Versioning**: model, prompt, tool, policy, and evaluator versioning and
  compatibility contracts.
- **Rollout**: staged rollout with progressive authority expansion, gated by
  production-readiness evidence and real-world observation windows.
- **Fallback**: defined fallback paths when an agent, model, or tool degrades
  below an operational threshold.
- **Cost and latency budgets**: budget allocation, breach detection, and
  automatic constraint responses (throttling, degraded modes, disablement).
- **Tool health**: tool availability monitoring, failure-rate thresholds, and
  degradation responses.
- **Escalation**: human-handoff triggers based on uncertainty, authority
  boundary, tool failure, or cost/latency breach.
- **Disablement**: conditions and procedures for disabling an agent or tool
  safely without cascading failures.
- **Trace-to-eval feedback**: production traces and incident records feeding
  back into evaluation case generation and release-gate updates.

## What the bundle does NOT own (boundary statement)

- It does **not** replace general release-engineering methods. Release pipelines,
  artifact promotion, and CI/CD mechanics stay with `release-engineering`.
- It does **not** replace general SRE methods. Incident response, SLO
  definition, error budgets, and operational recovery stay with
  `site-reliability-engineering`.
- It does **not** replace general security engineering. Threat modeling,
  vulnerability assessment, and secure design stay with
  `secure-software-engineering`.
- It does **not** replace general agent-evaluation methods. Eval design,
  observability instrumentation, and regression detection stay with
  `agent-evals-and-observability`.
- It does **not** replace general platform engineering. Infrastructure,
  compute, networking, and service capabilities stay with
  `platform-engineering`.
- It does **not** perform production-readiness reviews or incident learning.
  It **consumes** their artifacts as decision inputs.

## Routing table

| Concern | Route to |
|---|---|
| Agent evaluation design, observability, regression detection | [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md) |
| Release pipelines, artifact promotion, CI/CD | [release-engineering](../../release-engineering/SKILL.md) |
| Incident response, SLO/SLI, error budgets, operational recovery | [site-reliability-engineering](../../site-reliability-engineering/SKILL.md) |
| Security design, threat modeling, trust boundaries | [secure-software-engineering](../../secure-software-engineering/SKILL.md) |
| Platform infrastructure, compute, networking | [platform-engineering](../../platform-engineering/SKILL.md) |
| Production-readiness go/no-go/defer/exception outcomes | [production-readiness](../../production-readiness/SKILL.md) |
| Incident records, verified closure, follow-up work | [incident-learning](../../incident-learning/SKILL.md) |

## Autonomy assumption

The bundle explicitly does **not** assume uniform agent autonomy, user
population, or side-effect profile. Read-only agents, tool-using agents with
side effects, internal-facing agents, and customer-facing agents receive
different authority, escalation, and fallback treatment. Every contract and
control-plan artifact in this bundle distinguishes agent profiles by
capability class and side-effect surface.
