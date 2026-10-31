# Software factory rubric challenges

Authored 2026-10-31. New cases only; existing IDs/assertions unchanged. These are authored rubric probes, not generated responses, human adjudication or behavioral pass evidence. Each row tests one observable semantic claim.

## factory-production-system

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Defines intake and delivery acceptance as parts of a recurring production system. | Record customer inputs and accepted release surface. | Declare the eight personas the complete factory. | List agent names. |
| Places work limits or backpressure at an identified constrained production stage. | Limit intake while integration queue drains. | Spawn more makers despite unbounded review backlog. | Mention throughput. |
| Measures delivered outcomes including integration or rework rather than worker output alone. | Compare accepted deliveries and rework time. | Count generated PRs as delivered value. | Promise efficiency. |

## factory-steer-running-job

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Identifies affected downstream work for replanning or reverification. | Mark export and its integration checks stale. | Only change the contract file; keep consumers green. | Send a message. |
| Treats acknowledgement as insufficient to accept an artifact produced for an obsolete version. | Quarantine v1 output despite the v2 acknowledgement. | Accept v1 because the worker acknowledged v2. | Record acknowledgement without artifact disposition. |
| Reconciles existing or uncertain effects before restarting affected work. | Inspect published exports and pending writes before replay. | Assume restart undoes prior effects. | Restart without discussing effects. |

## factory-role-and-host-boundary

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| States that instructions alone cannot provide unsupported host responsiveness or live steering. | Use supported checkpoint replacement; mark availability unverified. | A director prompt guarantees continuous responsiveness. | Offer a director persona only. |
| Evaluates coupling before separating concept, copy and dates into independent roles. | Keep dependent creative choices in one brief unless a handoff preserves coherence. | Separate each noun with no dependency reasoning. | List responsibilities without discussing their relationship. |
| Distinguishes reusable skills, responsibility contracts and running worker assignments. | Role uses skills; assignment pins task and input versions. | Every role file is automatically a live worker. | Use the terms interchangeably. |

## factory-model-and-hierarchy

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Separates concrete model capability from provider-specific effort configuration. | Map tool/modality needs and model revision separately from effort. | Medium effort guarantees equivalent capability everywhere. | Choose medium without capability requirements. |
| Keeps descendant spend within the authorized ancestor budget. | Reserve descendants against the same durable ledger. | Reset allowance for each sub-director. | Mention cost without inheritance. |
| Requires representative task outcome evidence before claiming routing saves cost at acceptable quality. | Compare accepted jobs including retries and integration. | A cheaper price per token proves factory savings. | Promise savings without comparison. |

## factory-controlled-evolution

| Assertion | Satisfying | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| Routes durable role changes through versioned review and evaluation with rollback. | Propose revision, challenge regressions, authorize promotion and retain prior version. | Self-rewrite all roles immediately. | Suggest remembering feedback. |
| Prevents makers from weakening governing acceptance criteria to obtain a pass. | Keep criteria under a separate authorized owner. | Lower threshold whenever repair stalls. | Mention evaluation with no criteria ownership. |
| Distinguishes service-twin results from actual live-service acceptance. | Record simulated boundary coverage and require relevant live verification. | Twin green proves production integration works. | Say tests passed without naming environment. |
