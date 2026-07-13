# Authentication And Authorization

## Make The Decision Now

Separate identity proof from permission to act. Select an authentication protocol only after defining the relying parties, token holders, browser or service trust, phishing resistance needs, session lifetime, and recovery path. OAuth or OpenID Connect can fit delegated access; they are not universal answers for service-to-service or local trust models.

## Design For Enforcement

- Define a server-side authorization decision for every protected action and object: subject, action, resource, tenant, and contextual constraints.
- Derive identity and tenant context from validated credentials or trusted server-side bindings. Never grant authority from a client request field, prompt, retrieved document, or tool output.
- Enforce object-level checks on reads, writes, exports, and indirect references. Apply least privilege to people, services, jobs, and AI tools.
- Make session issuance, renewal, revocation, logout, recovery, and privilege changes explicit. Bind tokens to intended audience and purpose where the protocol supports it.
- Give automation narrowly scoped, short-lived credentials and independently authorize each material tool action.

## Evidence And Verification

Keep an authorization matrix and tests that exercise allowed and denied cases across roles, objects, tenants, direct endpoints, bulk endpoints, jobs, and tool calls. Inspect middleware and downstream services to prove a gateway check is not bypassed. Test expired, revoked, wrong-audience, and confused-deputy credentials.

## Misuse To Avoid

- Authentication-only APIs that expose any object named by an identifier.
- Frontend-only role checks, broad administrator tokens, or authorization performed only at routing.
- Letting an LLM decide whether a tool action is authorized; use it to propose intent, then enforce policy server-side.

Use OWASP ASVS stable 5.0.0 and the OWASP API Security Top 10 2023 edition as control-selection and risk-awareness guidance where adopted. See [source-index.md](source-index.md) for exact sources.
