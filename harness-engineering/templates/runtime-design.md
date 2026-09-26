# Runtime design decision

- User outcome and repository/custom-runtime boundary:
- Model/provider adapter and portability assumptions:
- Context assembly sources/versioning/budgets:
- Tool registry, authority enforcement, sandbox boundary:
- Event ordering and critical hook failure policies:
- Durable state owner, transaction/lease/fencing model:
- Proposed action → validation → authorization → execute → observe → checkpoint:
- Partial-effect reconciliation and replay policy:
- Acceptance/evaluator integrity, pass/fail/unknown routing:
- Task and global attempt/time/cost limits:
- Cancellation/child-process/drain semantics:
- Environment readiness and secrets handling:
- Failure/interrupt/resume exercises:
- Minimal telemetry, access and retention:
- Framework implementation handoff and owner:
- Alternatives/tradeoffs, rollback, unverified assumptions:
