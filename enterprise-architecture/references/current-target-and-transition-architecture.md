# Current, Target, and Transition Architecture

Use this reference when a desired enterprise state spans multiple domains or cannot
be reached safely in one change.

## Describe each state

- **Current:** observed capabilities, applications, information, technology,
  dependencies, constraints, pain, and ownership. Mark unknowns instead of filling
  gaps with a preferred future.
- **Target:** the future arrangement tied to outcomes, principles, measurable
  constraints, ownership, and decision rights. It is a hypothesis until adopted and
  funded.
- **Transition:** a stable intermediate arrangement that reduces risk or unlocks the
  next change. It must be useful on its own, not a disguised project phase.

For every target difference, record the dependency, affected capability, change
owner, reversibility, customer or operational impact, and evidence that would permit
the next move.

## Choose transitions

Prefer increments that remove a material constraint, establish missing ownership,
reduce duplicated investment, or create evidence for a disputed target. Compare
options by value, dependency order, disruption, reversibility, coexistence burden,
and ability to stop safely. A transition may retain legacy components deliberately
when replacement would create greater risk.

Do not promise rollback when data, contracts, training, or operating behavior have
irreversibly changed. Name roll-forward, containment, or retirement alternatives and
route execution to `migration-engineering` after the target is approved.

## Transition quality check

Each increment should state:

- entry conditions and the capability/outcome it advances;
- systems, information, roles, and decisions affected;
- dependencies and coexistence assumptions;
- user, operational, cost, and risk consequences;
- exit evidence and a named accountable owner;
- stop, defer, or proceed conditions;
- next transition enabled and residual debt accepted.

Architecture decides the coherent sequence and guardrails. Product owns product
commitments, strategy owns corporate choices, organization design owns people
changes, and delivery/migration owners execute approved work.
