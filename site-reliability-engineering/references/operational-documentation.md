# Operational Documentation Lifecycle

Use this reference when runbooks, alerts, service maps, configuration guidance, or incident procedures are stale, hard to find, or not trusted by responders.

## Source anchors

Synthesized from *Seeking SRE*, “Do Docs Better: Integrating Documentation into the Engineering Workflow,” “Active Teaching and Learning,” “SRE Cognitive Work,” and “Psychological Safety in SRE.”

## Functional quality

A document is good when it helps its intended reader complete a real task safely. Check more than spelling and structure:

- Can the reader identify the symptom and scope?
- Does the document state prerequisites, access, and assumptions?
- Are the first actions safe, bounded, and reversible?
- Does every consequential action have an observable verification?
- Does it say when to stop, escalate, or hand off?
- Are dashboards, configuration, owners, and dependencies linked to authoritative sources?
- Can a new responder follow it without relying on private memory?

## Lifecycle

1. Create the smallest document for a named task and audience.
2. Store it beside the service or in a discoverable source-controlled location.
3. Link alerts and service reviews to it.
4. Test it during onboarding, game days, and real incidents.
5. Update it when the service, alert, configuration, dependency, or recovery path changes.
6. Record owner and review trigger, not only a calendar date.
7. Prune documents that no longer describe a supported path.

Documentation work belongs in the engineering workflow. A stale runbook is an operational defect that can prolong an incident.

## Coverage signals

Useful signals include alert-to-playbook coverage, broken-link count, age of last successful exercise, time for a new responder to complete a task, and incidents where missing or misleading documentation delayed mitigation. Do not optimize for document count or word count.

## Agent procedure

Use this reference with `templates/runbook-template.md`, `monitoring-alerting.md`, and `human-systems-and-learning.md`. When editing a runbook, verify every command's scope, prerequisite, expected result, and rollback. If the source of truth is unavailable, mark the link and assumption instead of fabricating it.
