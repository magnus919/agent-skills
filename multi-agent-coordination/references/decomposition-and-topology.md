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

## Worked example: choose session lifetime by work shape

| Work | Starting shape | Where continuity lives |
|---|---|---|
| Diagnose one failure where each next step depends on the previous finding | One harness session, with a checkpoint if interrupted | Task and evidence record |
| Coordinate a migration with recurring decisions, stakeholders and open dependencies | Persistent role with replaceable sessions | Role remit, authorized inbox and durable project record |
| Classify independent support cases under a stable policy | Fresh worker per case, with bounded case-specific context | Case record and current policy at the host |

For a returning role, provide the current remit and revision, active work ID
and claim, latest accepted decision, unresolved question, stop conditions and
links to authorized evidence. Retrieve details as needed. Bind effects to the
current principal and claim at the tool boundary. A predecessor’s note may
explain a decision. Only the current authority can enable the action.

Challenge a replaced worker’s late output, a revoked grant, a contradictory
handoff note, and similar-looking case IDs belonging to different customers.
The case worker should receive only its assigned case fields. A mismatch must
be resolved through the current record before work continues. Compare accepted
outcomes, first correct decision, boot and idle-wake cost, retry and review
effort, and any leakage or unauthorized effect. Charge human interruptions and
review to the same comparison window. Route cost comparisons to
[AI operating economics](../../ai-operating-economics/SKILL.md).

The contrast between [Wheelhouse and Counting House](https://videos.itrevolution.com/watch/1233771796/)
motivates the examples. The [controlled topology study](https://arxiv.org/abs/2512.08296v3)
also supports comparing against a single agent for sequential work.
