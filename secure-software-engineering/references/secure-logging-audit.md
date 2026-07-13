# Secure Logging And Audit

## Make The Decision Now

Choose which security-relevant events need accountability, detection, or investigation, then define their minimal fields, access controls, retention, integrity expectations, and response owner. Log a decision and its evidence, not every sensitive input.

## Design For Useful Evidence

- Capture identity or workload, action, target, authorization result, time, request or correlation identifier, and policy or configuration version when they are needed to reconstruct a material event.
- Redact or avoid credentials, raw tokens, sensitive payloads, personal data, prompts, retrieved documents, and model context unless a documented investigation need outweighs exposure risk.
- Protect log transport, storage, query access, and deletion. Separate operational logs from high-value audit events when their access and retention needs differ.
- Preserve ordering and integrity signals appropriate to the threat model; alerting and immutable storage are design choices, not automatic guarantees.
- Log server-side tool authorization, execution outcome, user approval, and data destination for AI actions. Do not log private model context by default.

## Evidence And Verification

Review event schemas and run representative actions, denied attempts, privilege changes, tenant-bound operations, secret exposure responses, and AI tool requests. Verify that authorized investigators can answer the intended question without seeing prohibited data. CISA Secure by Design joint guidance supports transparency and ownership; it does not require indiscriminate collection.

## Misuse To Avoid

- Calling application debug output an audit trail.
- Making logs so complete that they become an unprotected copy of customer or secret data.
- Recording a successful request without the authorization decision, resource, or actor needed to investigate it.
