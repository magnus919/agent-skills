# Spec Quality Gates

Seven gates every SPEC.md must pass before entering the code generation pipeline. These are validation checks, not editorial preferences — a failing gate means the spec is not executable by an AI agent.

## Gate 1: Testability

Every acceptance criterion must produce a CLEAR PASS or CLEAR FAIL.

**Test:** Read each AC aloud. Can you check "yes or no" against it? If the check requires interpretation ("what counts as responsive?" "what counts as efficient?"), the AC fails.

**Wrong:** "The system should handle errors gracefully"
**Right:** "When the payment API returns HTTP 503, the system displays 'Service temporarily unavailable' and retries automatically after 5 seconds"

## Gate 2: Edge Case Completeness

Edge cases must be explicitly enumerated, not implied by "normal case" examples.

**Test:** For each user story, list five things that could go wrong. If the spec doesn't address at least three, edge cases are underspecified.

**Wrong:** "User uploads a profile photo" — no mention of what happens with empty files, wrong formats, oversized images
**Right:** "User uploads a profile photo" with explicit ACs for: empty/corrupt file, wrong format, >5MB, non-image file

Common edge case categories:
- Empty/null inputs
- Maximum/minimum boundary values
- Invalid formats (wrong type, wrong encoding)
- Concurrent access / race conditions
- Network failures / timeouts
- Authorization failures
- Data that no longer exists (tombstones, soft deletes)

## Gate 3: Scope Boundary Clarity

Out-of-scope must be as explicit as in-scope. Ambiguous scope boundaries are the most common source of drift — the implementation agent cannot distinguish "out of scope" from "the spec forgot to mention this."

**Test:** Read the in-scope list. For each item, ask: "Could someone reasonably include broader functionality under this description?" If yes, the scope boundary is not tight enough.

**Wrong:** "In scope: user authentication" — does this include password reset? social login? MFA? session management? API tokens?
**Right:** "In scope: email/password authentication, password reset flow, session token management. Out of scope: social login (Google/GitHub OAuth), MFA/TOTP, API key authentication"

## Gate 4: Non-Functional Requirement Measurability

NFRs must state a specific, measurable threshold and a verification method.

**Test:** For each NFR, ask: "Can I write a test that fails if this threshold is not met?" If no, the NFR is not measurable.

**Wrong:** "The system should be fast"
**Right:** "Search responses must complete within 200ms at P95 under 1000 concurrent requests, verified by k6 load test with 95th percentile assertion"

| NFR Type | Measurable Format | Verification Method |
|----------|------------------|-------------------|
| Performance | X units under Y load at Z percentile | Load test (k6, Locust) |
| Availability | X% uptime over Y period | Monitoring + SLO |
| Security | X controls, Y compliance standard | SAST scan, pen test |
| Observability | X metrics + Y logging + Z tracing | Integration test |

## Gate 5: Data Contract Sufficiency

Any interface between components must be specified at a level of detail enabling independent implementation of both sides.

**Test:** Could two implementation agents build the producer and consumer independently using only this spec and their shared contracts? If they'd need to coordinate in real time, the data contracts are insufficient.

**Wrong:** "API endpoint: POST /orders"
**Right:** "POST /orders accepts JSON body {customerId, items[], shippingAddress}. Returns 201 with {orderId, status}. Error responses: 400 for validation failures, 422 for out-of-stock items."

Data contract minimum:
- All request/response schemas (field names, types, required/optional, constraints)
- Status codes and error formats for every endpoint
- Event/stream schemas if applicable
- Auth requirements (method, scopes, token format)

## Gate 6: Assumption Inventory

Every assumption made during specification must be documented with an impact assessment.

**Test:** Count the undocumented assumptions. If you can find any not in the Assumptions section, the inventory is incomplete. Ask "what would have to be true for this spec to be wrong?" for each section.

**Wrong:** No Assumptions section at all
**Right:** "Assumption: Users have stable internet connectivity. Impact if wrong: offline mode is not specified, retry logic may be insufficient."

Common undocumented assumptions:
- Network reliability assumptions
- User behavior assumptions (will users follow the happy path?)
- Data quality assumptions (will input data be clean?)
- Environment assumptions (hardware, OS, dependencies)
- Third-party service assumptions (availability, latency, rate limits)

## Gate 7: AI Agent Readiness

The spec must be consumable by an AI coding agent without requiring clarification.

**Test:** Read the spec as if you cannot ask a single follow-up question. Mark every phrase that could be interpreted in more than one way. Each marked phrase is a spec defect.

**Wrong:** "The system should handle common file formats" — the agent must guess what "common" means
**Right:** "The system must accept CSV (RFC 4180), JSON, and XML files. Reject all other formats with error code 400 and message 'Unsupported format: {format}'"
