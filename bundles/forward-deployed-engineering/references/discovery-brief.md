# Discovery Brief — Forward-Deployed Engineering

## Scope and design decision

The requested capability is designed as a public, business-agnostic continuity
bundle for embedded technical engagements. Portability is a normative design
objective, not a conclusion established by the employer-authored sources. Its
normative synthesis is the lifecycle
`Discover → Frame → Hypothesize → Build → Evaluate → Deploy → Adopt → Measure →
Generalize`, plus shared artifacts, authority gates, evidence labels, and a
generalization decision. This sequence is bundle design, not an externally
standardized methodology.

## Overlap audit

| Existing owner | Already owns | FDE bundle boundary |
|---|---|---|
| [product-discovery](../../../product-discovery/SKILL.md) | Stakeholder mapping, workflow walkthroughs, hidden assumptions, validation, and interpretation handoff | Routes discovery and carries its evidence forward; does not duplicate discovery method |
| [agent-evals-and-observability](../../../agent-evals-and-observability/SKILL.md) | Decision/risk contracts, datasets, baselines, graders, trajectory review, release gates, telemetry, and incident learning | Routes evaluation evidence and applies it to engagement continuity; does not restate eval method |
| [production-readiness](../../../production-readiness/SKILL.md) | Risk-scaled evidence, ownership, SLOs, observability, support, security, data, rollback, capacity, cost, and verdicts | Routes readiness at the deployment boundary; does not invent a customer-site readiness method |
| [remote-systems-administration](../../../remote-systems-administration/SKILL.md) | Access routes, privilege, bastions, sessions, recovery, rollback, canaries, bounded rollout, and external verification | Routes constrained-environment discovery before action; does not create a second remote-operations runbook |
| [product-lifecycle](../../product-lifecycle/SKILL.md) | Product investment and lifecycle governance | FDE owns embedded delivery continuity, not portfolio choice or product lifecycle governance |
| [production-excellence](../../production-excellence/SKILL.md) | Cross-domain production gate and handoff | FDE prepares engagement continuity and routes evidence; production-excellence owns its launch gate |
| [neckbeard](../../neckbeard/SKILL.md) | Bounded software change journey | FDE stops routing and sends a well-specified repository change directly to neckbeard |

The four audited class-level skills are not modified by this bundle. The
manifest routes to them where their existing methods are needed.

## Themes across the source set

The three sources do not establish one common role contract. Palantir supports
embedded implementation, engineering review and operation, and return of field
configurations and expertise. OpenAI supports discovery through rollout,
adoption and workflow-impact measurement, eval-driven feedback, and pattern
codification. The limited Databricks extract supports customer-facing
productionization and cross-functional work. Together they orient the bundle,
but no source proves the full nine-stage lifecycle or every artifact. They also
do not establish a universal title, staffing model, technology stack, travel
pattern, or lifecycle sequence. See [source-index.md](source-index.md).

## Design risks and mitigations

The following are risks this normative design is intended to guard against;
the source set does not establish their frequency or prevalence.

| Design risk | Continuity mitigation |
|---|---|
| Bespoke-service sprawl | Record reuse boundary and generalization decision for every local solution |
| Hero culture | Name authority, review, support, and receiving owners; make escalation normal |
| Prototype-to-production collapse | Require baseline, representative/adversarial evaluation, readiness evidence, rollback, and a release decision |
| Product bypass | Preserve field-learning and productization records; route patterns to an accountable receiving owner |
| Weak decision authority | Charter decision rights and stop conditions before action; escalate out-of-charter decisions |
| Customer capture | Define exit, transfer, adoption owner, support path, and measurable completion conditions |
| Technical success with adoption failure | Diagnose workflow, trust, education, activation, support, and ownership before more build work |
