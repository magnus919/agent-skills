# Background workers for agent memory

Use background memory processing when later requests can benefit from work
that can finish asynchronously. Use established terms such as memory
consolidation, reflection, asynchronous enrichment, or sleep-time compute.
These mechanisms differ in what they do, when they run, and what they can
change. See the [research log](research-log.md) for academic and product evidence.

| Work | Trigger and output | Failure to test |
|---|---|---|
| Index projection | Source or policy event produces chunks, embeddings, or time buckets | Old retry republishes stale data, or acknowledgement is mistaken for readiness |
| Candidate links and facts | Ingestion batch proposes typed assertions with original evidence | Wrong entity merge, visible private relationship, or unsupported inference |
| Contradiction and expiry | Event or schedule marks superseded facts or proposes resolution | Conflicting records collapsed without authority, or expiration treated as erasure |
| Consolidation or reflection | Idle, periodic, or volume-based job produces a reviewable summary or memory version | Lost qualification, recurrence of old facts, or agent-derived claims reinforcing each other |
| Trend/forecast enrichment | Data watermark triggers a series analysis with inputs and cutoff | Dashboards leak restricted series, probabilities drift, or stale forecasts persist |

## Publish in stages

Keep low-latency serving separate from optional enrichment. Capture source
material or a memory proposal under a named principal and scope. On durable
commit emit a versioned job, and show pending/ready/failed where the state
matters. Use a database transaction with an outbox or equivalent mechanism
when persistence and enqueue must agree.

Bind every job to a tenant, explicit read scope, output scope, service
identity, input versions, and an idempotency key. Bound time, tokens, fan-out,
depth, and retries. Persist job state and quarantine terminal failures.
At execution and again before publication, revalidate tenant, policy,
source versions, deletion status, and write authority. A source may change
while a worker is running. Publish a staged version only if its preconditions
still hold, using an atomic version check or equivalent. Readers should see
the last eligible version or an explicit unavailable state after revocation.

For a personal assistant, let explicit user preferences update a scoped
profile and show inferred changes in a reviewable log. In organizations,
an automated worker can have authority to project a source while a steward
owns publication of inferred policy or organization-wide claims. Keep sources
and derived statements distinguishable. Preserve contrary evidence and
supersession lineage. Give consolidation a rollback path and remove or rebuild
derived outputs when their sources are revoked or deleted.

## Decide when the pattern earns its cost

Compare deterministic jobs, scoped LLM enrichment, and query-time processing
using later questions plus correction and deletion tests. Measure critical
path latency, total compute including unused precomputation, publication
lag, stale content, lost or invented claims, and review burden. Test retries,
overlapping runs, access changes mid-job, and reverting a promoted output.
Scope-based workers and staged publication are concrete product patterns.
The value of autonomous graph maintenance or reflection cascades depends on
the corpus, error costs, and evaluation evidence.
