# Decompose decisions before choosing a topology

## Model the work

List decisions, inputs, outputs, shared resources and acceptance boundaries.
Draw three different relationships: task dependency, communication, and authority.
A peer messaging edge does not imply a task prerequisite or permission to approve.
Annotate which decisions can proceed under stable inputs and which continually
invalidate each other. Keep tightly coupled decisions together until an interface
can preserve their constraints. Good decomposition preserves what the consumer
needs while removing irrelevant exploration.

Default to one lead plus bounded independent workers only where justified. A
single-agent result is a valid outcome of this skill. If independent searches
can be batched as tools, another agent may add no useful context boundary.

## Choose by failure surface

| Shape | Choose when | Challenge before adopting |
|---|---|---|
| Single agent / sequential pipeline | Decisions depend heavily on common context or ordered effects | Context limits and total latency |
| Independent fan-out + integration | Disjoint evidence gathering or implementations behind stable interfaces | Duplicate work, conflicting assumptions, unverified aggregation |
| Central lead and specialists | Adaptive task division and one integrated decision owner | Lead bottleneck, lossy summaries, unavailable lead |
| Hierarchical teams | Subsystems have coherent contracts and measured coordination load exceeds one lead | Escalation delay, nested authority/budget drift, hidden failures |
| Peer collaboration | Local discoveries genuinely change peers' next steps | Broadcast noise, groupthink, circular waiting, no accountable integrator |
| Hybrid | A specific boundary needs peer exchange within bounded subteams | Complexity that neither single shape requires |

Declare maximum depth, active workers and message/repair bounds from workload
and host capacity. These are experiment parameters, not recommended universal
numbers. Keep a minimal fallback topology if a coordinator or communication
service is unavailable.

## Research and transfer limits

[Kim et al., v3](https://arxiv.org/abs/2512.08296v3) compares five architectures
under controlled configurations and finds task-dependent benefits and harms.
This supports measuring decomposition and tool overhead; it does not supply a
universal team-size threshold. Earlier summaries describe a smaller experiment;
use the pinned revision's conditions. [MASS, v2](https://arxiv.org/abs/2502.02533v2)
optimizes prompts and topology together. Synthesis: preserve both revisions in
comparisons, and do not attribute gains to topology after silently changing prompts.

## A worked split

Request: export invoices with currency grouping. Define invoice/payment/currency
semantics before splitting implementation. One worker can implement export and
another document the accepted format once the interface is fixed. Two workers
independently inventing payment semantics are not independent subtasks. An
integration owner checks actual invoice → export behavior on the combined
revision. If semantics change, invalidate dependent outputs and acceptance
receipts; do not average their green checks.

## When to recombine

Measure clarification loops, repeated interface edits, integration time and
accepted results against the baseline. Recombine tasks when coordination costs
exceed useful independence or critical context cannot be compressed faithfully.
Add hierarchy only after locating a real bottleneck. Retain dissenting evidence
and failed attempts; a successful demo does not establish repeatable advantage.
