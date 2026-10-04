# Agent Interface Enrichment Comparisons

Use this protocol when a change alters how an agent discovers tools or context, receives large results, delegates work, or resumes across sessions. It supplements the general paired-comparison guidance in [metrics-and-statistics.md](metrics-and-statistics.md); it does not prescribe a particular interface or promise that enrichment improves outcomes.

## Isolate the mechanism

Write a failure hypothesis before running trials. Name the mechanism, predicted benefit, and plausible harm. Examples include task-relevant discovery reducing irrelevant definitions while preserving prerequisite correctness, or an external artifact keeping bulk data out of model context while remaining usable by its intended consumer.

Compare baseline and candidate on the same realistic tasks, starting state, identity and permissions, model/runtime, tool and service versions, resource policies, task/result semantics, completeness criteria, and grading. Declare the changed discovery or result-transport mechanism as the treatment rather than requiring that mechanism itself to stay identical. Pair by task and preserve repeated runs where stochasticity matters. Change one mechanism at a time when possible. If discovery and artifact transport change together, use separate ablations or describe the result as a bundled change; do not attribute the outcome to one component.

Include task-relevant discovery and irrelevant/ambiguous requests. Test whether the agent finds the right capability, retrieves prerequisites before acting, and avoids loading irrelevant tools. Compare external bulk artifacts with inline delivery on consumers that need the result, including a different service or delegated agent when that is a claimed use. Test fresh sessions and repeated tasks to measure whether useful results recur without relying on accidental conversational state.

## Grade outcomes and costs

Use task outcome and environment state for completion and side effects; inspect traces for discovery, prerequisite ordering, tool selection, authorization, artifact creation and retrieval, delegation, retries, and recovery. Keep graders tied to observable evidence: a response claiming that another service consumed an artifact does not prove that it did.

Report per-task and per-slice success, incorrect or unnecessary calls, denied/unauthorized actions, partial results, duplicates, timeouts, retries, and recovery. Measure context or tokens, latency distributions, monetary cost, and orchestration, storage, transfer, and cleanup overhead only from sources that actually expose those quantities. Mark unavailable measures as unavailable; do not substitute token counts for cost or invent missing data. Report failed, denied, incomplete, expired, and timed-out runs in the denominator.

Challenge artifact flows with missing or expired references, wrong identity or tenant, revoked permissions, partial pagination, duplicate delivery, stale content, consumer incompatibility, and a recipient that cannot access the source. Check that the agent verifies provenance and permissions, detects incompleteness, and recovers or escalates without exposing data or claiming success. Test discovery with missing prerequisites, near-duplicate tools, empty/ambiguous search results, and permission-filtered capabilities.

Interpret quality, reliability, safety, context use, latency, and total cost as separate dimensions. Context savings do not establish task improvement; task success does not excuse authorization failure. A vendor's reported benchmark is motivation for a local hypothesis, not evidence for this system. Synthetic design responses, static fixtures, adapter mocks, and prose-only claims can test a contract but cannot establish production uplift. Treat unresolved evidence as inconclusive and state what live integration or user evidence is still needed.

## Suggested case families

Build paired cases that include:

- discovery succeeds on a task-relevant request, while a near-miss returns the wrong capability or omits a required prerequisite;
- bulk results are delivered through an artifact and consumed by a different authorized service, with a paired inline baseline;
- artifact failures include missing, expired, partial, duplicate, inaccessible, or permission-changed data, and the agent does not claim complete success;
- a later fresh session repeats a task and locates the correct result using explicit durable identifiers, while ambiguous or stale matches are rejected;
- delegated work returns a verifiable result and provenance to the requester, while denial or partial failure is surfaced instead of silently lost.
