# Security Requirements And Threat Modeling

## Make The Decision Now

Decide what harm the feature must prevent, which assets and actions matter, and where the system changes trust. Create a short model before implementation and revise it when flows or assumptions change. Use the per-component STRIDE questions in [security-audit-methodology](../../security-audit-methodology/references/threat-modeling.md) when they reveal useful threats; do not force every category onto every component.

## Work From Evidence

1. Inventory assets, including credentials, tenant data, money-moving actions, audit records, model inputs, retrieved documents, and tool capabilities.
2. Name actors and their current versus required authority. Include services, administrators, background jobs, support staff, external providers, and AI agents.
3. Draw data flows and mark crossings such as browser-to-service, service-to-store, tenant-to-shared worker, model-to-tool, and build-to-release.
4. Write assumptions that can be disproved: identity issuer validation, tenant context propagation, queue visibility, retrieval corpus curation, or build isolation.
5. Turn plausible abuse into mitigations and measurable acceptance criteria. Record likelihood, impact, owner, and residual risk.

Evidence is the reviewed model, data-flow diagram, design decision, and tests or configuration proving each mitigation. The model is incomplete if it omits failure paths, administrative paths, data export, asynchronous work, or AI tool calls.

## Hypothetical Abuse Cases

Use scenarios like these as prompts, then replace them with cases grounded in the actual design:

| Boundary | Hypothetical abuse | Design question | Verification idea |
|---|---|---|---|
| User to object API | An authenticated user requests an object owned by another user or tenant. | Where is object-level authorization enforced? | Exercise allowed and denied object/tenant combinations through direct and bulk paths. |
| External sender to webhook | An attacker forges or replays a message. | How are origin, integrity, freshness, and idempotency established for this protocol? | Submit forged, modified, duplicate, and stale messages. |
| API to background worker | A job carries a client-supplied tenant identifier into shared processing. | How does the worker derive and independently enforce tenant context? | Attempt cross-tenant job, cache, search, and storage access. |
| Retrieved document to AI tool | Retrieved text instructs the model to disclose data or invoke a privileged tool. | Why can untrusted content not grant authority or expand retrieval scope? | Inject conflicting instructions and verify server-side policy still denies the action. |
| Model to external side effect | Model output proposes a material or irreversible action without valid approval. | Which capability, validation, authorization, and human gate apply? | Manipulate tool arguments and approval state; confirm no side effect occurs. |

## Misuse To Avoid

- Treating a diagram as a threat model while leaving assets, assumptions, and mitigations unstated.
- Trusting client-supplied roles, tenant identifiers, prompt instructions, or callback claims.
- Limiting the model to request/response paths and missing caches, jobs, backups, telemetry, search, and release automation.

## Verify

For each material boundary, show where authentication, authorization, input handling, failure behavior, logging, and resource limits are enforced. Confirm an abuse case fails safely in a test or review the explicit reason it cannot be tested. Use OWASP ASVS 5.0.0 control objectives and OWASP Top 10:2025 only as adopted context, not as proof of coverage.
