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

## Example: fixture maintenance with scoped landing

A synthetic instance of the fields above for
[earned-autonomy decision M-17](../../ai-governance/references/earned-autonomy.md#worked-decision-a-bounded-maintenance-merge-class):

| Contract field | Example value |
|---|---|
| Goal, owner, eligibility | Release owner maintains only export fixture files on the approved repository. Scope and allowed paths come from the effective grant. |
| Trigger, identity and queue | An explicitly authorized scheduled queue reads the approved issue source from its durable cursor. A key joins issue, accepted revision and attempt lease. The [intake example](../references/software-factory.md#worked-intake-preserve-distinct-reports-before-dispatch) governs report replay and urgency. |
| Acceptance, checker, authority | Expected parser output and required current CI on the candidate. A checker controlled outside the maker verifies the target using [evidence standards](../../verification-methodology/references/evidence-standards.md#worked-example-a-disposable-settings-to-export-driver). The grant excludes deployment, policy changes, and customer data access. |
| Responsibility and outcomes | Coordinator assigns bounded work, maker prepares change, independent checker reports, controller validates authority before any permitted landing. A failed behavior routes to repair within budget. Unknown or stale evidence holds. Denied authority stops the effect. Timeout and exhaustion preserve a checkpoint and escalate. |
| Bounds, ownership and reconciliation | For illustration, one worker, two attempts and 30 minutes per item. Lease and checkpoint bind the exact candidate. Reconcile branch and landing state before retrying. On revocation stop the affected action, cancel or drain as policy provides, reconcile in flight, and clean only owned resources. |
| Handoff and review | Retain result and decision links for each terminal path. The release owner reviews sample coverage, incidents, accepted outcomes and total review burden. Keep release/promotion and rollback in their authorized path. |
