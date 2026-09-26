# Bounded loop or graph contract

- Goal, task eligibility, and business owner:
- Discovery source/cursor; deduplication/run key:
- Trigger and explicit scheduling authorization:
- Accepted behavior and checker evidence source:
- Maker/checker criteria integrity and context separation:
- Authority; prohibited side effects; approval owner:
- Node responsibilities, inputs/outputs, resource ownership:
- Routing: pass / fail / unknown / denied / timeout / exhausted:
- Maximum attempts, elapsed time, cost, no-progress cycles:
- Work lease/fencing and durable checkpoint store:
- Operation reconciliation/idempotency before replay:
- Cancellation and owned-resource teardown:
- Human/business anchor for goal review:
- Integration/release boundary and rollback:
- Expected evidence on each terminal path:
- Measured orchestration/review overhead:

A graph must not convert unknown to success or allow a worker to authorize its own
merge. Use a simple execution when coordination benefits do not exceed costs.
