# High-throughput merges on a shared main branch

Research brief · 2026-11-28 · Moderate depth

**Research question.** How do teams merging rapidly into one codebase minimize rebases, isolate conflicts, and sustain safe throughput? [Research log and source evidence](evidence.md) · [Related factory handoff research](../factory-handoffs-and-review/README.md) · [Existing software factory guidance](../../../harness-engineering/references/software-factory.md)

## Summary

Use one protected merge path per target branch. Authors work and get reviewed in parallel. The queue combines each ready change with main and queued predecessors, runs required checks on that candidate, and controls the order in which main advances. This removes routine author rebases just to keep up with main. Actual conflicts still go back to an owner, and a CI result is usable only while its candidate remains valid. [Queue mechanics](evidence.md#queue-mechanics)

## Findings

### Separate review from integration validation

Review and early checks establish that a specific change is ready to join the queue. Integration checks establish that it works in the proposed combined code. With main at **M** and queue order **A → B → C**, CI can check **M+A**, **M+A+B**, and **M+A+B+C** concurrently. If B fails, A can continue and C needs a candidate without B. If C actually requires B, hold C on B or test and land them as an explicit group. A clean Git merge can still break compilation, configuration, or behavior. [Queue mechanics](evidence.md#queue-mechanics) · [Shopify case study](evidence.md#engineering-case-studies)

### Match queue design to CI cost and the state you need to validate

| Design | What runs | When it fits |
|---|---|---|
| Serial validation | One candidate at a time. Main advances after it passes. | Low arrival rate, fast CI, or a first rollout. A 20-minute gate caps a busy serial lane at three PRs per hour before overhead and failures. |
| Speculative merge train | Several ordered candidate prefixes run at once. Removing or reordering an entry invalidates affected later candidates. | Reliable checks and spare runner capacity. Tune concurrency against discarded CI and tail latency. |
| Tested batch or rollup | One combined candidate is tested for several PRs. A failed batch needs isolation or splitting. | Expensive fixed CI costs and independently reviewable, low-risk changes. Evidence covers the combined state. For intermediate states that must be independently usable, require evidence for each prefix. |
| Dependency-aware speculation | The scheduler tests alternative candidate states and uses explicit rules to allow safe out-of-order landing. | Persistent head-of-line delays at scale and a reliable dependency model. Uber requires positive evidence about alternate states to bypass an unresolved change. |

GitHub's **Build concurrency** controls how many candidate builds it dispatches. Its **Merge limits** control how many already-validated PRs land together. Raising merge limits alone leaves the number of merge-group builds unchanged. Rust's bors rollups show how several PRs can share a test run. [Queue mechanics](evidence.md#queue-mechanics) · [Uber case studies](evidence.md#engineering-case-studies)

### Reduce conflicts before work enters the queue

Tell workers which issue or outcome they own, which interfaces they share, and which PRs they depend on. Assign one owner to a shared schema, manifest, generated surface, or API migration when concurrent edits repeatedly collide. Land a backwards-compatible contract change first, migrate consumers in parallel, then remove the old contract. Use a short stack for real dependencies and land usable prefixes or a verified group. On eligible GitHub.com repositories, a native stack can enter the queue as one merge group. [Change structure and ownership](evidence.md#change-structure-and-ownership)

Shopify's 2026 app rebuild was the closest public example found of agents raising PR volume. The team reports bottlenecks in CI, review, merging, and duplicate work. Agents helped with CI triage and conflict repair, and small pods owned app areas. The account gives no comparative merge-throughput figures. [Shopify app rebuild](evidence.md#change-structure-and-ownership)

### Optimize the current bottleneck

| Observation | First adjustment to test |
|---|---|
| Long review wait, short queue wait | Reduce work in progress, split by reviewable behavior, and route review to the appropriate owner. |
| Idle runners while ready PRs wait on the front candidate | Increase speculative concurrency in small steps. |
| Long runner waits or queue CI starving branch feedback | Reserve integration capacity, shorten setup, and reuse correctly keyed build artifacts. |
| Many ejections or invalidated downstream builds | Fix flaky checks, bound retries for classified infrastructure failures, reduce hotspot overlap, and reduce speculative depth if wasted runs are saturating CI. |
| A few large PRs dominate tail latency | Split by compatibility where possible. Consider out-of-order landing only where the system can validate the relevant combined states. |
| Green main with a growing backlog of undeployed changes | Apply deployment backpressure or increase release capacity. Track the two queues independently. |

GitHub reported a 33% reduction in **average wait to ship** in its own deployment workflow alongside about 2,500 PRs per month in its large monorepo. Uber reported a 74% lower **p95 wait to land** for its Go monorepo from April to June 2023 after a speculation change. These are historical, first-party comparisons with different baselines and outcomes. [Engineering case studies](evidence.md#engineering-case-studies)

## A starting configuration for a software factory

1. **Protect main.** Use an enforced queue or a single protected integration lane. Admit eligible PRs only. Bind review and policy results to the proposed change, run required checks on the combined candidate, and record the observed merge. If building a lane, atomically advance main only from a base covered by the evidence, or rebuild.
2. **Keep the gate fast and meaningful.** Run cheap feedback on the branch, required cross-change checks on the candidate, and broader checks after merge or at release with an owner and recovery path. Select affected tests from dependency information with a broad fallback for shared tooling, unknown impact, and cross-cutting changes.
3. **Start shallow.** Wire up one candidate at a time, then try two concurrent candidates if integration is the bottleneck and runners have room. On GitHub, start with **Only merge non-failing pull requests** enabled and a minimum merge size of one. Frequent queue jumps invalidate in-flight work. Reserve them for urgent fixes and retain required checks. Define who can pause the queue and how to recover a red main.
4. **Return failures to an owner.** Report the candidate and failing check or conflict. Rebuild affected successors when queue inputs change. Agents can diagnose and repair within their assigned scope. Bound transient retries and retain their evidence. A late result on a superseded candidate cannot authorize a merge.
5. **Measure landed work.** Track review-ready → approved, approved → enqueued, and enqueued → merged at p50 and p95. Include time across removals and requeues. Track PRs landed per working hour, runner wait, CI minutes per landed PR, superseded CI minutes, author conflict fixes, failed or abandoned PRs, time main is red, reverts, and merge-to-deploy lag. Change one setting at a time against the repository's throughput, cost, and reliability targets.

**GitHub Actions detail.** Required checks for the native queue must run on the `merge_group` event and report against the candidate. Keep the required workflow runnable and put selective checks inside it. Verify that failed or cancelled prerequisites propagate to the required result and that concurrency groups distinguish simultaneous candidates. Before relying on the gate, exercise a passing PR, two PRs that pass individually but fail in combination, and an upstream removal during later CI. Confirm the queue uses only the rebuilt result for the surviving candidate. [GitHub configuration evidence](evidence.md#queue-mechanics)

## Catalog application

PR #899 applied the research to the catalog. Verified Delivery follows the current candidate and verifies the landing. Release Engineering explains how to select and measure a queue design. Harness Engineering shows how a factory handles independent and dependent work after an ejection. [PR #899](https://github.com/magnus919/agent-skills/pull/899) · [Merge queue delivery](../../../verified-delivery/references/merge-queue-delivery.md) · [Release process models](../../../release-engineering/references/release-process-models.md#merge-queues) · [Software factory](../../../harness-engineering/references/software-factory.md#worked-queue-failure-with-dependent-work)

## Confidence and open questions

High confidence in protecting one merge path, validating combined candidates, and avoiding routine freshness rebases. The starting configuration is a proposal. Optimal concurrency, batch size, and required versus post-merge test coverage depend on local data. The reported case-study gains give no portable target. This research involved no live queue pilot.
