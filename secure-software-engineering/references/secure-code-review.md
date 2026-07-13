# Secure Code Review

## Make The Decision Now

Review the change against its trust boundaries and acceptance criteria, not a generic list alone. Identify what authority, data flow, dependency, deployment capability, or AI tool behavior the change adds or alters; request a threat-model update when the answer is unclear.

## Review Method

1. Read the intended behavior, security criteria, architecture change, and tests.
2. Trace untrusted inputs to privileged sinks, including queries, shell or process calls, URLs, files, templates, logs, queues, model prompts, retrieval, and tools.
3. Trace identity and tenant context from verification through every object, background path, and downstream service.
4. Inspect error, retry, timeout, exceptional, and rollback paths; OWASP Top 10:2025 includes mishandling exceptional conditions as a risk category.
5. Review dependency, configuration, CI, infrastructure, and release-artifact changes alongside code.
6. State each finding as evidence, impact, exploit precondition, remediation, and verification. Separate observed facts from assumptions.

## Evidence And Verification

Require tests for denied authorization, malformed input, cross-tenant access, secret redaction, dependency integrity decisions, and relevant AI action approvals. Use a second reviewer or focused security review for material boundary changes. A passing review checklist is evidence that questions were asked, not proof that no vulnerability remains.

## Misuse To Avoid

- Reviewing only changed lines when a new endpoint or dependency changes a system-wide boundary.
- Accepting tests that prove an allowed path but never exercise denial, revocation, or failure.
- Treating model output as reviewed code or allowing it to introduce uninspected dependencies and privileged operations.

Use [templates/secure-code-review-checklist.md](../templates/secure-code-review-checklist.md) to structure review prompts.
