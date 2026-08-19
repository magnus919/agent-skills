---
name: digital-twin
description: >-
  Design, build, evaluate, govern, monitor, evolve, and retire digital twins
  and federated twin universes for software systems, engineering processes,
  agentic software factories, infrastructure, and cyber-physical operations.
  Use when a task involves digital-twin architecture, digital thread, simulation,
  predictive maintenance, twin health, agent authority, or dark-factory design.
  Do not use for ordinary observability dashboards, static dependency graphs,
  generic AI governance, or operating one named infrastructure tool without a
  twin-specific representation and feedback loop.
license: MIT
---

# Digital Twin

Use this skill to design and operate a trustworthy digital twin, especially a twin of a software product, engineering process, delivery system, infrastructure estate, or agentic factory.

## Core position

A digital twin is not automatically a dashboard, 3D view, dependency graph, emulator, test fixture, or LLM wrapper. Establish the represented original, synchronization contract, models/services, intended decision, uncertainty, and action boundary before using the term.

For this skill, use these working distinctions:

- **Digital model:** representation without a required live synchronization loop.
- **Digital shadow:** observable flow from original to representation without a governed return path.
- **Digital twin:** a versioned representation of a named entity or process, synchronized at an explicit frequency and fidelity, with models/services that support a declared decision or action.
- **Digital thread:** provenance and lifecycle linkage across systems, artifacts, decisions, and outcomes. A thread is necessary for many twins but is not itself a twin.
- **Twin universe:** a federation or composition of purpose-bounded twins with explicit identity, time, provenance, semantics, ownership, and authority boundaries.

These are operational definitions, not claims of universal standards consensus. NIST IR 8356 explicitly notes that no single definition is agreed, while allowing abstract entities and processes as twin subjects.

## Operating workflow

1. **Frame the use case.** Name the original, decision, desired outcome, authoritative sources, update/fidelity requirement, operating domain, owner, risk tier, forbidden actions, and simpler alternatives.
2. **Classify the representation.** Decide whether the artifact is a model, shadow, twin, emulator, simulator, or composite universe. Do not upgrade the label without evidence of synchronization, model credibility, and a governed feedback path.
3. **Design the contracts.** Define stable identities, event envelopes, timestamps, schema versions, provenance, freshness, uncertainty, validity intervals, permissions, and action semantics.
4. **Build evidence first.** Capture immutable source events and artifacts, then create replayable temporal projections. Preserve raw evidence separately from claims and disposable views.
5. **Add models and scenarios.** Register model purpose, assumptions, domain, parameters, version, calibration, uncertainty, tests, and prohibited use. Pin scenario inputs, model digests, seeds, clocks, fixtures, and outputs.
6. **Run read-only and shadow modes.** Compare reconstructed state and recommendations with independently captured reality before allowing side effects. Treat missing, stale, contradictory, or unauthenticated evidence as `unknown` or `hold`, not pass.
7. **Govern the action path.** Separate observe, simulate, recommend, approve, execute, rollback, and stop. Put authorization in deterministic policy enforcement, not model prose. Require idempotency, scoped credentials, preconditions, expiry, rollback, and reconciliation.
8. **Evaluate independently.** Keep represented-system health, synchronization/data health, model credibility, platform health, and agent/action quality as separate planes. The twin must not grade itself.
9. **Operate and evolve.** Monitor freshness, loss, ordering, schema/topology drift, residuals, calibration, uncertainty, scenario gaps, platform SLOs, agent trajectories, authority, and outcome value. Revalidate after material changes.
10. **Retire deliberately.** Revoke action authority, drain and migrate consumers, preserve required lineage, remove secrets and sensitive data under policy, mark endpoints retired, detect orphan calls, and verify no live workflow still depends on the twin.

## Choose the right reference

| Need | Read |
|---|---|
| Architecture and federation | `references/architecture.md` |
| Data, identity, event, graph, model, and simulation implementation | `references/implementation.md` |
| VVUQ, health planes, SLOs, drift, agent evaluation, and chaos tests | `references/evaluation.md` |
| Security, privacy, decision rights, and earned autonomy | `references/governance.md` |
| Growth, change, incident recovery, and decommissioning | `references/lifecycle.md` |
| Standards, source boundaries, and further reading | `references/source-index.md` |

## Agentic software factory boundary

A software factory analogue maps repositories, revisions, requirements, builds, artifacts, dependencies, services, environments, deployments, incidents, humans, agents, policies, and runtime observations to twin entities and events. Executable repository environments, service emulators, traffic mirrors, IaC sandboxes, and learned world models are useful components, but each has a simulator-reality boundary. Real execution remains the release oracle for consequential code and infrastructure changes.

A dark factory is an authority state, not a twin type. More automation requires stronger independent validation, provenance, staged rollout, rollback, and accountable escalation. Do not equate high model confidence with authority.

## Minimum release packet

Before granting non-read-only authority, preserve:

- intended-use, risk, and authority contract;
- source and identity map;
- event/schema/provenance contract;
- assumptions, validity limits, and uncertainty budget;
- verification and independent validation results;
- synchronization/data-quality benchmark;
- scenario and replay manifest;
- agent task and trajectory evaluation;
- security, privacy, and supply-chain review;
- shadow/canary and rollback evidence;
- health SLOs and alert ownership;
- signed `approve`, `conditional approve`, `hold`, or `block` decision.

## When not to use

Do not load this skill for ordinary dashboard construction, static asset inventory, generic dependency mapping, generic AI governance, generic DevOps design, or routine operation of a named tool. Route those tasks to the relevant observability, AI-governance, platform, data, or tool-specific skill. In this repository, use `agent-evals-and-observability` for generic agent eval/telemetry, `ai-governance` for organization-wide AI governance, `data-architect` for general data-platform design, and the relevant tool skill for operating a named platform. Load this skill when the representation itself, its synchronization, simulation/prediction, composition, authority, or lifecycle is the problem.

## Exit criteria

Stop when the requested twin design or decision artifact exists, claims are separated into evidence and inference, the relevant evaluation/governance gates are explicit, and unresolved gaps have owners or bounded escalation. Never claim a twin is trustworthy, autonomous, production-ready, or safe solely because its schema, graph, dashboard, or component tests pass.
