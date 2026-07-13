# Contract Verification

Validate an interface at multiple boundaries. A schema linter, generated document, or
passing mock is useful evidence but is not integration proof.

| Boundary | Evidence to collect |
|---|---|
| Contract | Schema parse/validation, references, examples, negative examples, documented semantics |
| Provider | Conformance tests for success, errors, authorization, limits, concurrency, and side effects |
| Consumer | Consumer expectations, generated-client behavior, tolerant/strict parsing, migration fixtures |
| Compatibility | Consumer-aware diff, enum/default/null/order/pagination and behavioral regression assessment |
| Deployed | Authenticated end-to-end test against the intended deployment, telemetry and rollback evidence |

For an event or webhook interface, test the stated publisher/subscriber perspective,
envelope, signature profile, duplicate/reorder/gap behavior, and delivery failure
handling. For a stream, test reconnect and checkpoint/loss semantics.

## Deployed-Boundary Verification

Use the contract-review template to record evidence, gaps, owners, and a verdict.
Load [verification-methodology](../../verification-methodology/SKILL.md) when a formal
evidence-backed completion assessment is needed, and
[spec-driven-development](../../spec-driven-development/SKILL.md) when contracts must
be connected to delivery specifications and acceptance gates.
