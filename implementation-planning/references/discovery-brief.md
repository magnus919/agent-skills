# Discovery Brief — Implementation Planning

## Purpose

This brief surveys existing planning-related material in the agent-skills
catalog, identifies overlaps and gaps, and defines the ownership boundary for
the implementation-planning skill. It answers: **what does this skill own, and
what does it deliberately hand off to others?**

## Existing planning material in the catalog

### spec-driven-development — task plans

SDD produces a `TASK-PLAN.md` as part of its phase-4 decomposition step. That
task plan is **specification-local**: it decomposes a single spec into tasks
within the spec's own scope, primarily for a single agent or team following the
SDD pipeline. It is designed for the SDD factory model — spec in, code out.

**What implementation-planning adds:** SDD task plans do not address cross-team
coordination, multi-repository dependency mapping, data migration staging,
rollout strategy design, or the handoff between separately-owned workstreams.
Implementation planning operates at the level **above** a single spec's task
plan — it coordinates multiple workstreams, each of which may be driven by its
own SDD pipeline or specialist skill.

### release-engineering — rollout plans

Release engineering covers promotion gates, canary mechanics, progressive
delivery, feature flags, and release-train coordination. Its rollout plans are
**pipeline-oriented**: how the release system moves artifacts through stages.

**What implementation-planning adds:** Release engineering assumes a single
release artifact or coordinated train. It does not produce the cross-workstream
dependency map, the ownership assignment, or the verification-traceability
matrix from requirement to workstream. Implementation planning hands the rollout
**design** to release-engineering for pipeline mechanics, but owns the rollout
**strategy** — which stages, what each stage gates on, what triggers rollback,
and how the rollout fits the broader plan.

### site-reliability-engineering — change plans

SRE covers change-management practices: change windows, SLO-based gradual
rollout, error budgets, and operational readiness. Its change plans are
**operations-oriented**: what the on-call responder needs to know.

**What implementation-planning adds:** SRE change plans assume an operations
perspective on a single change. They do not design the work breakdown, critical
path, or handoff contracts between teams. Implementation planning produces the
plan that feeds into SRE change management — the SRE change plan is a consumer
of the rollout stage definition, not its author.

### product-discovery — requirements gathering

Product discovery interviews stakeholders, surfaces hidden assumptions, detects
gaps, resolves conflicts, and translates conversations into structured SDD
specs. It is **upstream** of implementation planning.

**What implementation-planning adds:** No plan content. The boundary is
clear: product-discovery produces the **input** to an SDD spec; SDD produces the
**approved spec**; implementation-planning consumes the approved spec and
produces the **delivery plan**. Implementation planning never performs
discovery.

### product-methodology — prioritization (RICE, MoSCoW)

Product-methodology owns tactical prioritization frameworks. Implementation
planning may **cite** a prioritization output (e.g., "these three workstreams
are priority-1 per the product methodology RICE assessment") but never
re-derives RICE, MoSCoW, or other prioritization mechanics.

### Other relevant skills (no ownership conflict)

| Skill | Relationship |
|---|---|
| `qa-methodology` | Consumes the verification section of the plan; designs the test strategy for each workstream |
| `platform-engineering` | Consumes infrastructure or CI/CD requirements surfaced in the plan |
| `secure-software-engineering` | Consumes security requirements; the plan identifies security-sensitive workstreams and routes them |
| `data-engineering` | Consumes data migration staging; the plan defines the stages, cutover, and reconciliation |
| `api-design-and-evolution` | Consumes API contract dependencies identified in the plan |
| `adr-authoring` | The plan may identify architecture decisions that need formal ADRs |
| `backend-engineering` / `frontend-engineering` | Consume individual workstreams from the plan for implementation |
| `neckbeard` | The plan is an input to a neckbeard change-request journey, but this skill does not execute the journey itself |

## Ownership boundary

### What implementation-planning OWNS

1. **End-to-end delivery planning** for approved requirements spanning one or
   more teams, repositories, or systems.
2. **Work decomposition** into vertical slices, workstreams, and completion
   criteria.
3. **Dependency mapping** — hard and soft dependencies, critical path, and
   coordination interfaces.
4. **Ownership assignment** — who is accountable for each workstream and each
   dependency.
5. **Sequencing and parallelism** — which workstreams run concurrently, which
   are sequential, and where they synchronize.
6. **Rollout strategy design** — stages, gates, observability signals, and
   rollback triggers. (Pipeline mechanics are handed to release-engineering.)
7. **Rollback and recovery path design** — per-stage rollback procedures,
   including data rollback.
8. **Verification traceability** — mapping every workstream back to the approved
   requirement.
9. **Unresolved decision and risk tracking** — capturing what could not be
   resolved during planning, with owners and deadlines.
10. **Entry-gate enforcement** — rejecting unapproved inputs.

### What implementation-planning HANDS OFF

1. **Discovery and requirements elicitation** → product-discovery.
2. **Specification authoring and phase gates** → spec-driven-development.
3. **Implementation (coding, debugging, architecture design)** → backend-engineering, frontend-engineering, software-architecture-analysis.
4. **Release pipeline mechanics (canary config, feature flags, promotion automation)** → release-engineering.
5. **SLO definition, error budgets, incident response procedure** → site-reliability-engineering.
6. **Threat modeling, security requirements authoring** → secure-software-engineering.
7. **QA test strategy and verification plan authoring** → qa-methodology.
8. **Platform infrastructure provisioning** → platform-engineering.
9. **API contract design** → api-design-and-evolution.
10. **The neckbeard issue-to-PR delivery lifecycle** — phase gates, delivery-packet sequencing, and orchestration are separate concerns.
