# Consumer review contract: customer resolution, event reads, export

## Task and boundary

The consumer’s outcome is an export of the intended customer’s events for a stated scope and period, with evidence that the export completed and can be retrieved by the authorized requester. The customer service owns customer identity and event records; the export service owns export operation state and artifact lifecycle. The API must identify the authenticated principal, tenant/account context, permitted actions, and relevant object scope. A name is a search/display value, not a stable identifier or authorization credential.

## Consumer path

1. **Resolve the customer.** Search using the supplied name with explicit matching rules and bounded results. Return service-scoped customer IDs, display labels, and only safe disambiguating attributes. If multiple plausible candidates remain, return `ambiguous` with candidates the caller is authorized to see and require a human or caller decision. Never choose the first candidate by default. No match, denied access, missing connection, and transient failure need distinct outcomes.
2. **Read events.** Pass the selected opaque customer ID in its declared namespace and tenant scope. Require a time range or documented default, deterministic ordering and tie-breaker, maximum page size, and an opaque cursor. The response reports whether it is complete, has a next cursor, and whether the cursor is snapshot-stable. Define behavior if records change during pagination; callers must not infer completeness from a short page. Reauthorize each page and make denied distinct from empty.
3. **Request export.** Before the consequential request, validate target, event range, fields, destination/visibility, and authority. If review is required, show a clear preview and obtain approval tied to the final normalized operation and payload. Create an operation ID and idempotency scope that binds equivalent request parameters; define retention, duplicate concurrency behavior, replay/result lookup, and key-reuse conflict. Return accepted/pending separately from terminal completion. Expose status, partial outcomes, cancellation semantics, and a retrieval reference limited to the authorized principal, with content type, size, expiry, and access rules.

## Timeout and recovery

A timeout after export submission means outcome unknown, not failure. The client first queries by operation/idempotency identity and reconciles the server-side state before retry. It must not issue a new export blindly. If the operation completed, return its existing result; if still pending, continue bounded polling or use the documented notification/status mechanism; if failed, report the operation-level code and whether a retry is safe; if partial, identify completed and incomplete parts and the recovery action. Cancellation means a request to stop future work until the service confirms terminal cancellation; already-created files or dispatched data may require separate cleanup or compensation.

## Acceptance evidence

Exercise the deployed client/server boundary with unique, ambiguous, and nonexistent names; wrong-tenant ID; event pagination with changes between pages; empty versus denied; invalid range; export permission denial; timeout before and after effect; duplicate request; key conflict; expired artifact; and partial export. Verify calls, arguments, authorization, event counts, final operation state, and actual retrievability. The consumer review is conditional until domain owners define name matching and snapshot guarantees, export sensitivity/retention, approval policy, and downstream artifact access. Schema validation alone cannot establish these behaviors.
