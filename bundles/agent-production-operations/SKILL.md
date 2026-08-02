---
name: agent-production-operations
description: >-
  Operate an evaluated agent with tools and authority in production through a
  runtime control plane covering versioning, staged rollout, fallback, cost and
  latency budgets, tool health, human escalation, disablement, and trace-to-eval
  feedback. Do not use for building agents, designing evals, or general release,
  SRE, security, or platform engineering — those methods stay with their
  specialist skills.
license: MIT
compatibility: Agent harness with file read/write and terminal access. No network or runtime dependency required by the bundle itself.
metadata:
  spec-version: "1.0"
  tags: agent, production, operations, runtime, control-plane, rollout, fallback, disablement
---

# agent-production-operations

A runtime control plane for taking an evaluated agent with tools and authority
into controlled production operation. This bundle bridges the gap between
passing evaluations and safe production use: it defines how an agent is
versioned, rolled out, monitored, constrained, escalated, and disabled — and
how production evidence feeds back into evaluation and release decisions.

The bundle does **not** build agents, design evaluations, run release pipelines,
or own infrastructure. It composes those concerns from existing specialist
skills and owns only the runtime control decisions between them.

## When to load this

Load this bundle when you are operating an agent that:
- Has passed evaluation and is cleared for production consideration.
- Has tools with side effects and delegated authority that must be gated.
- Needs a staged rollout with progressive authority expansion.
- Must be monitored for cost, latency, tool health, and authority usage in
  production.
- Requires a defined fallback, escalation, and disablement path.
- Should feed production traces and incidents back into evaluation cases and
  release-gate updates.

## When not to use

Do **not** load this bundle for:
- Building or designing an agent from scratch — route to the appropriate
  framework skill (LangGraph, CrewAI, AutoGen, etc.).
- Designing agent evaluations or observability — route to
  [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md).
- General release engineering (CI/CD pipelines, artifact promotion) — route to
  [release-engineering](../../release-engineering/SKILL.md).
- General site reliability engineering (incident response, SLO definition,
  error budgets) — route to
  [site-reliability-engineering](../../site-reliability-engineering/SKILL.md).
- General security engineering (threat modeling, vulnerability assessment) —
  route to [secure-software-engineering](../../secure-software-engineering/SKILL.md).
- General platform infrastructure (compute, networking, storage) — route to
  [platform-engineering](../../platform-engineering/SKILL.md).
- Performing a production-readiness review — route to
  [production-readiness](../../production-readiness/SKILL.md); this bundle
  **consumes** readiness outcomes, it does not produce them.
- Conducting an incident postmortem — route to
  [incident-learning](../../incident-learning/SKILL.md); this bundle
  **consumes** incident records as escalation and feedback inputs.

## Autonomy is not assumed uniform

This bundle explicitly does **not** assume all agents share the same autonomy,
user population, or side-effect profile. Agent profiles are distinguished by
capability class and side-effect surface:

| Profile | Example | Authority | Escalation trigger | Fallback |
|---|---|---|---|---|
| **Read-only** | Internal search agent | Query-only; no mutation, no user-data access | Uncertainty above threshold; result quality degradation | Return cached/static results |
| **Side-effect-capable, internal** | CI triage bot | Issue/PR comments, label management, branch creation | Tool failure > 5% in window; authority breach attempt | Disable tool, escalate to human |
| **Side-effect-capable, customer-facing** | Support agent with account access | Read PII, suggest actions, no mutation without confirmation | Any PII access without explicit consent; cost breach > 10% of budget | Degrade to read-only, escalate immediately |

Every control-plan decision (authority, escalation, fallback, disablement) in
this bundle is parameterized by the agent's autonomy profile. A read-only agent
and a side-effect-capable agent operating on customer data receive different
thresholds and different escalation paths.

## Runtime control plane routing

The bundle composes the following specialist skills. Load them when their
domain is the active concern; the bundle owns the cross-domain coordination.

| Concern | Specialist skill | When to load | What the bundle adds |
|---|---|---|---|
| Agent evaluation and observability | [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md) | Designing evals, instrumenting observability, detecting regression | Trace-to-eval feedback loop; eval-case generation from production incidents |
| Release engineering | [release-engineering](../../release-engineering/SKILL.md) | Release pipeline design, artifact promotion, CI/CD | Agent-specific staged rollout with authority gating; rollback triggers tied to agent health |
| Site reliability engineering | [site-reliability-engineering](../../site-reliability-engineering/SKILL.md) | Incident response, SLO/SLI definition, error budgets | Agent-specific latency/cost budgets; tool-health SLOs; escalation handoff to incident command |
| Security engineering | [secure-software-engineering](../../secure-software-engineering/SKILL.md) | Threat modeling, trust-boundary validation, secure design | Agent authority contracts with side-effect boundaries; disablement security (revoke, not just stop) |
| Platform engineering | [platform-engineering](../../platform-engineering/SKILL.md) | Compute, networking, storage, service infrastructure | Agent sandboxing requirements; tool-execution isolation preferences |
| Production readiness | [production-readiness](../../production-readiness/SKILL.md) | Readiness reviews, go/no-go/defer/exception decisions | Consumed as input: readiness outcomes gate agent authority expansion |
| Incident learning | [incident-learning](../../incident-learning/SKILL.md) | Post-incident analysis, verified closure, follow-up work | Consumed as input: incident records feed escalation thresholds and eval-case generation |

## Loading protocol

This SKILL.md is the discoverable umbrella entry point. Nested skills are not
used in this bundle. Reference files are loaded on trigger:

| Reference | Loaded when |
|---|---|
| [references/discovery-brief.md](references/discovery-brief.md) | Reviewing the bundle's boundary decisions against specialist skills |
| [references/agent-production-contract.md](references/agent-production-contract.md) | Defining capability, authority, uncertainty, escalation, and side-effect contracts for an agent |
| [references/runtime-control-plan.md](references/runtime-control-plan.md) | Planning versioning, staged rollout, or fallback for an agent in production |
| [references/tool-authority-health.md](references/tool-authority-health.md) | Recording or reviewing tool availability, failure, and authority usage/breach state over time |
| [references/trace-to-eval-feedback.md](references/trace-to-eval-feedback.md) | Connecting production traces and incidents back to evaluation cases and release gates |

## Concrete operational parameters

### Authority

- **Definition**: the set of actions an agent is permitted to perform, scoped by
  target (which resources), operation (read/write/delete), and user-context
  (whose data).
- **Trigger to review**: any new tool registration, model update, or prompt
  change that expands the agent's reachable action surface.
- **Threshold**: authority is binary per action class. No action may be
  performed that is not explicitly listed in the production contract. An
  attempt to perform an unauthorized action is an **authority breach** and
  triggers immediate escalation.
- **Action on breach**: log the attempt, block the action, increment the
  authority-breach counter, and escalate. If breach count exceeds 3 in a
  rolling 24-hour window, disable the agent.

### Escalation

- **Definition**: transfer of a decision or action from the agent to a
  designated human operator.
- **Triggers** (any one triggers escalation):
  - Authority breach (attempted unauthorized action).
  - Uncertainty above threshold: agent confidence < 0.7 on a
    side-effect-capable action (configurable per profile).
  - Tool failure rate > 5% in a 5-minute sliding window.
  - Cost budget breach > 10% of allocated budget in a billing period.
  - Latency p95 > 2x baseline for > 5 minutes.
  - Human-handoff keyword or explicit user escalation request.
- **Action**: suspend the agent's side-effect authority, log the escalation
  context (trigger, state snapshot, pending actions), notify the designated
  escalation channel, and await human disposition (resume / reduced-authority /
  disable).

### Fallback

- **Definition**: a predetermined safe behavior when the agent, model, or a
  tool cannot operate at its normal capability level.
- **Triggers**:
  - Model endpoint returns 5xx for > 30 seconds.
  - A critical tool is unavailable (health-check failure for > 2 minutes).
  - Cost budget exhausted (100% consumed).
  - Latency p95 > 5x baseline for > 2 minutes.
- **Actions per profile**:
  - Read-only: return a static/cached response with a "results may be stale"
    disclaimer.
  - Side-effect-capable, internal: degrade to read-only, queue pending
    mutations, notify operator.
  - Side-effect-capable, customer-facing: degrade to read-only, surface a
    "temporarily unavailable" message to the user, escalate immediately.

### Disablement

- **Definition**: complete revocation of the agent's ability to act, including
  read-only access. Distinct from fallback (which preserves reduced capability).
- **Triggers**:
  - 3 or more authority breaches in a 24-hour window.
  - Production-readiness review outcome is "no-go" or "defer" for the current
    agent version.
  - Incident-learning record attributes a severity-1 or severity-2 incident to
    agent action, and verified closure is not yet complete.
  - Human operator issues an explicit disable directive.
  - Tool compromise or credential leak detected (route through
    [secure-software-engineering](../../secure-software-engineering/SKILL.md)).
- **Action**: revoke all credentials and tokens; remove from routing/load-balancing;
  record disablement reason, timestamp, and authorizing evidence; notify
  escalation channel; prevent automatic restart until a new
  production-readiness review passes.

### Cost

- **Definition**: the financial cost of operating the agent, attributed to a
  budget owner.
- **Budget**: allocated per agent per billing period (e.g., $500/day for a
  customer-facing support agent). Budget is set at production-contract time and
  reviewed at each production-readiness cycle.
- **Thresholds**:
  - 50% consumed: notification to budget owner.
  - 80% consumed: warning; cost-optimization review triggered.
  - 100% consumed: fallback to degraded mode (read-only or cached).
  - 110% consumed: disablement (hard stop, no further cost accrual).
- **Measurement**: per-request model cost + per-call tool cost (where
  applicable), attributed to the agent instance. Cost data is appended to the
  tool-authority-health record.

### Latency

- **Definition**: end-to-end response time from user request to agent response,
  measured at p50 and p95 over 5-minute windows.
- **Baseline**: established during staged rollout observation window (phase 1
  of rollout). Recorded in the agent production contract.
- **Thresholds**:
  - p95 > 2x baseline for > 5 minutes: escalation trigger.
  - p95 > 5x baseline for > 2 minutes: fallback trigger.
  - p50 > 3x baseline for > 10 minutes while cost budget is > 80% consumed:
    disablement consideration.
- **Action**: latency breaches feed the trace-to-eval feedback loop: the
  latency-impacted requests are sampled and reviewed for eval-case generation.

### Privacy

- **Definition**: constraints on agent access to, processing of, and retention
  of user data (PII, usage patterns, conversation content).
- **Concrete rules**:
  - An agent must not access PII without an explicit user-data-access grant in
    its authority contract.
  - Agent traces and conversation logs must be scrubbed of PII before entering
    the trace-to-eval feedback pipeline (route scrubbing design to
    [privacy-engineering](../../privacy-engineering/SKILL.md)).
  - Data retention for agent traces defaults to 30 days unless a shorter period
    is specified in the production contract.
  - Any PII access by a read-only agent triggers immediate escalation (the
    read-only profile should never touch PII).
- **Privacy breach**: any PII access outside the granted scope triggers
  escalation and a mandatory security review via
  [secure-software-engineering](../../secure-software-engineering/SKILL.md).

## Core workflow

1. **Contract**: define the agent's capability, authority, uncertainty,
   escalation, and side-effect contracts using
   [references/agent-production-contract.md](references/agent-production-contract.md).
   Consume production-readiness outcomes and incident-learning records as
   decision inputs.

2. **Version and plan**: version the model, prompt, tools, policy, and
   evaluator; plan the staged rollout and fallback path using
   [references/runtime-control-plan.md](references/runtime-control-plan.md).

3. **Roll out**: execute staged rollout with progressive authority expansion,
   monitoring tool health and authority usage at each stage using
   [references/tool-authority-health.md](references/tool-authority-health.md).

4. **Monitor**: track cost, latency, tool health, authority breaches, and
   escalation events. Apply threshold-based actions (notify, degrade, escalate,
   disable) per the concrete parameters above.

5. **Feed back**: connect production traces and incidents to evaluation cases
   and release-gate updates using
   [references/trace-to-eval-feedback.md](references/trace-to-eval-feedback.md).

6. **Learn**: consume incident-learning verified-closure records and
   production-readiness review outcomes to update agent authority, escalation
   thresholds, and disablement conditions.

## File map

| Path | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Umbrella entry point (this file) |
| [README.md](README.md) | Human-facing overview and quick start |
| [AGENTS.md](AGENTS.md) | Agent loading and discovery notes |
| [references/discovery-brief.md](references/discovery-brief.md) | Boundary analysis against specialist skills |
| [references/agent-production-contract.md](references/agent-production-contract.md) | Capability, authority, uncertainty, escalation, and side-effect contracts |
| [references/runtime-control-plan.md](references/runtime-control-plan.md) | Versioning, staged rollout, and fallback plan |
| [references/tool-authority-health.md](references/tool-authority-health.md) | Tool availability/failure and authority usage/breach record |
| [references/trace-to-eval-feedback.md](references/trace-to-eval-feedback.md) | Production-to-evaluation feedback loop |
| [evals/evals.json](evals/evals.json) | Integrated output-quality evaluation cases |
| [manifest.yaml](manifest.yaml) | Machine-readable composition contract (schema v1): purpose, audience, stages, included skills, prerequisites, outputs, handoffs, conflicts, and eval suite; consumed by the lifecycle capability matrix |
