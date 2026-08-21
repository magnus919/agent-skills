# Coupling, Modularity, and Decomposition

Use this reference when the question is whether architecture boundaries contain change, failure, ownership, or deployment consequences. A boundary is not justified by a component name or by a preference for services.

## Six coupling lenses

Inspect the same candidate boundary through these lenses and keep the evidence separate:

| Lens | Questions and evidence |
|---|---|
| Static | Which modules import, call, inherit from, or directly reach into one another? Are there cycles, shared utilities with business meaning, or hidden side doors? |
| Dynamic | Which runtime calls, messages, callbacks, retries, and fan-out paths cross the boundary? What happens on timeout, duplication, or partial completion? |
| Data | Which tables, records, files, caches, indexes, and schemas are read or written by each part? Who defines invariants and can safely change the data? |
| Temporal | Which steps must occur in order, within one request, within a time window, or after an earlier event? Does a shared clock or sequence create a hidden dependency? |
| Deployment | Which parts must be released, scaled, configured, rolled back, or restored together? Do they share a process, image, database, secret, or maintenance window? |
| Organizational | Which team owns the code, data, on-call burden, and decision rights? Do team boundaries align with the proposed boundary or create a coordination tax? |

Also inspect change coupling: use version history, incident fixes, and release notes to see whether files or capabilities change together. A low import count does not prove low change coupling.

## Modularity signals

Positive signals include a coherent reason to change, explicit inputs and outputs, owned invariants, replaceable dependencies, failure containment, independent verification, and an owner able to operate the unit. Negative signals include cycles, shared mutable state, cross-boundary transactions, synchronous fan-out, duplicated policy, coordination-heavy releases, and an interface that exposes internal data shape.

Classify each signal as observed, reported, inferred, or unknown. Do not use a numeric score as a substitute for judgment; a single cross-boundary invariant can outweigh many clean imports.

## Decomposition readiness

Assess readiness in this order:

1. State the reason for considering a split: change isolation, scaling asymmetry, fault containment, team ownership, regulatory isolation, or another evidenced pressure.
2. Identify the smallest capability and its invariants, data authority, inbound/outbound dependencies, and operational responsibilities.
3. Test whether the boundary can tolerate asynchronous or independently deployed behavior. Name the consistency and recovery consequences rather than assuming a message solves them.
4. Estimate the new coordination surface: contracts, observability, deployment, access, testing, support, data migration, and reconciliation.
5. Compare alternatives: retain a modular monolith, isolate a process without a service boundary, extract a library/package, use a queue, or split a deployable unit. Select “not ready” when evidence does not support the added cost.

The output should state a readiness verdict such as `ready for a bounded experiment`, `needs seam work`, `retain current boundary`, or `insufficient evidence`. It should list reversible probes and a stop condition. A decomposition recommendation is outside this skill's execution scope; route an approved migration to `migration-engineering`.

## Boundary report

For each candidate boundary, report: purpose, six-lens evidence, change coupling, data ownership, consistency model, failure containment, team/operator fit, coordination cost, alternatives rejected, confidence, and the next reversible probe.
