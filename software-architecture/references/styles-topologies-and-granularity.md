# Styles, Topologies, And Granularity

Choose a shape because it fits the scenarios and ownership, not because the label is fashionable.

## Style comparison

Compare a modular monolith, separately deployed services, event-oriented collaboration, batch or workflow-oriented integration, and managed platform capabilities by the same questions: where policy lives, where data is authoritative, how callers coordinate, how failures surface, how teams deploy and operate, and how the shape changes later.

## Deployment topology

Describe runtime placement and trust boundaries separately from logical boundaries. Include process and network hops, regions or zones, data stores, queues, ingress and egress, and operator paths. Show which parts are managed by the application team and which are substrate responsibilities. Route concrete cloud resource selection or provisioning to `platform-engineering`.

## Granularity test

A boundary is promising when it has a coherent policy, an owner who can change and operate it, a stable interaction surface, data authority that can be stated, and a failure behavior that callers can tolerate. A boundary is premature when it exists only to reduce file size, mirrors team names without ownership, requires frequent distributed transactions, or adds a hop without a scenario that benefits.

## Cloud topology questions

For a cloud design, document regional assumptions, availability zones, state placement, network admission, identity boundaries, dependency failure, deployment blast radius, data movement, and recovery. Do not claim provider resilience from a service name alone. Load `platform-engineering` for substrate implementation and `capacity-and-cost-engineering` for measured capacity or spend.

## Diagram handoff

Use `c4-diagramming` for context, container, component, or code views. A diagram supports the decision; it does not replace ownership, runtime behavior, or evidence.
