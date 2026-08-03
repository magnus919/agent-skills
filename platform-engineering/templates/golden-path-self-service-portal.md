---
title: "Golden Path / Self-Service Portal: [Capability Name]"
doc_id: GP-[CAPABILITY-CODE]-[VERSION]
status: draft | proposed | approved | superseded
created: [YYYY-MM-DD]
last_modified: [YYYY-MM-DD]
owner: "[Platform Team / Individual]"
approver: "[Platform Lead]"
---

# Golden Path / Self-Service Portal — [Capability Name]

## 1. Purpose and Scope

| Field | Value |
|---|---|
| **Capability** | [What developers can obtain, e.g., a new service with CI pipeline, namespace, and database] |
| **Developer need** | [The workflow this removes from a ticket queue, e.g., provision a Postgres database for a new microservice] |
| **In scope** | [List what the portal provisions automatically] |
| **Out of scope** | [List what still requires a ticket or manual review, e.g., production firewall changes] |
| **Request frequency** | [e.g., 12 requests/week — evidence that this is the highest-friction path] |
| **Current cycle time** | [e.g., 3 days from ticket to working environment] |

## 2. Developer Journey

| Step | Actor | Action | System Response | Time |
|---|---|---|---|---|
| 1 | [Developer] | [Submit request with service name, team, environment] | [Validate naming and quota] | _[fill: seconds]_ |
| 2 | [System] | [Run scaffold from template] | [Create repo, pipeline, namespace, DB via IaC] | _[fill: minutes]_ |
| 3 | [Developer] | [Approve generated PR] | [Apply to Git, reconcile via GitOps] | _[fill: minutes]_ |
| 4 | [Developer] | [First deploy] | [Verify observability baseline is live] | _[fill: minutes]_ |

- **Time-to-first-deploy target:** _[fill: e.g., under 30 minutes from request]_
- **Cognitive load target:** _[fill: e.g., no more than N decisions required from the developer]_

## 3. Template Design

### 3.1 Provisioning Template

- **IaC module used:** _[fill: e.g., terraform module for service scaffolding, version pinned]_
- **Resources created:** _[fill: repository, CI workflow, namespace, database, secrets placeholder, dashboards]_
- **Input parameters:** _[fill: name, team, environment, size limits — every input validated]_
- **Default values:** _[fill: what the template assumes when the developer leaves a field blank]_

### 3.2 Pipeline Template

- **Stages:** _[fill: build, test, artifact, deploy — mirror the platform CI/CD reference]_
- **Gates:** _[fill: where approvals sit and who can override]_
- **Artifact handling:** _[fill: registry, signing, provenance, versioning scheme]_

## 4. Guardrails and Policies

| Guardrail | Enforcement Mechanism | Escalation / Override |
|---|---|---|
| Least-privilege IAM | _[fill: generated from request scope, not admin defaults]_ | _[fill: role/person with authority]_ |
| Budget and quota limits | _[fill: tag-based budget alert, quota per namespace]_ | _[fill: cost owner approval]_ |
| Observability baseline | _[fill: mandatory dashboard + alert rules on scaffold]_ | _[fill: SRE review]_ |
| Security baseline | _[fill: secret scanning, image scanning, network policy default deny]_ | _[fill: security review]_ |
| Naming and ownership | _[fill: validated naming convention, required owner field]_ | _[fill: platform team]_ |

- **Policy-as-code location:** _[fill: where policies live in Git, e.g., OPA/kyverno rules, Terraform guardrail module]_

## 5. Escape Hatch

- **Escape hatch path:** _[fill: what a developer does when the golden path does not fit — e.g., exception request, custom module review]_
- **Exception review criteria:** _[fill: what justifies leaving the paved road and who reviews]_
- **Bounded by:** _[fill: golden paths are paved roads, not cages — the exception keeps the platform from blocking delivery]_

## 6. API-First Design

- **Portal entry points:** _[fill: CLI command, web UI, API endpoint — each invokes the same scaffold service]_
- **Request/response contract:** _[fill: schema of the request and the status response]_
- **Audit trail:** _[fill: every provisioned change is a Git commit/PR with actor and timestamp]_
- **Idempotency:** _[fill: what happens when the same request is submitted twice]_

## 7. Success Metrics

| Metric | Target | Measurement Source |
|---|---|---|
| Time-to-first-deploy | _[fill: target]_ | _[fill: portal telemetry]_ |
| Ticket volume for this capability | _[fill: target decrease]_ | _[fill: ticketing system]_ |
| Developer satisfaction / cognitive load | _[fill: survey score]_ | _[fill: survey]_ |
| Guardrail violations | _[fill: target]_ | _[fill: policy engine logs]_ |

## 8. Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | [YYYY-MM-DD] | [Author] | Initial golden path design |
| 1.1 | [YYYY-MM-DD] | [Author] | [Summary of changes] |

*Keep this record in Git next to the portal implementation so the design and the code stay in sync.*
