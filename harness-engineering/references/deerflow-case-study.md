# DeerFlow: choose the execution loop, not the label

Use this case when choosing between a workflow-specific graph and a
general-purpose agent with a specialist skill. Both can use LangGraph. The
important difference is **who controls the next step and who accepts the result**.

## Research brief and evidence boundary

Question: What changed between DeerFlow's original research workflow and 2.x,
which pieces transfer to a custom harness, and what must a new implementation
prove independently? Inspected November 20, 2026. The comparison uses the legacy
`main-1.x` snapshot at `2ab28765803d4d9582aaa8f2f3355137d154e273` and
[v2.2.0](https://github.com/bytedance/deer-flow/releases/tag/v2.2.0) at
`58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a`. The 2.x architecture describes a rewrite,
not an incremental upgrade of the same research graph. Claims below are from
upstream docs and static source inspection, not live runs, independent quality
measurements, or proof that these controls cover every deployment.

| Subsystem | Mechanism inspected | Design choice to carry forward |
|---|---|---|
| Instructions | [1.x graph builder](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/graph/builder.py) defines coordinator, planner, human feedback, research roles, and reporter. Code routes an unfinished plan step by its type; planning and research still require judgment. In 2.x the [deep-research skill](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/skills/public/deep-research/SKILL.md) guides a general lead agent. | Put required transitions in code. Keep flexible query and synthesis choices with the model. A checklist in a skill is not a required node or gate. |
| Tools | The [2.x architecture](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/docs/ARCHITECTURE.md) separates built-in, configured, and MCP tools. The [lead-agent assembly](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/agents/lead_agent/agent.py) narrows and checks its assembled tool view. | Give research workers retrieval and artifact-writing tools appropriate to their role; verify actual grants at dispatch rather than relying on the role name. |
| Environment | The [sample config](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/config.example.yaml#L1709-L1812) defaults to the local provider with host Bash disabled and lists isolated alternatives. The app container and a worker's execution boundary are different controls. | Record the real provider and boundaries for each deployment. Do not infer per-task isolation from Docker or a virtual workspace path. |
| State | The [1.x graph builder](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/graph/builder.py) exports an uncheckpointed graph and separately offers an in-memory checkpointer. The [2.x checkpoint provider](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/runtime/checkpointer/provider.py) supports memory, SQLite, and Postgres; the [retention contract](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/docs/checkpoint-retention-contract.md) describes replay and lineage. | Persist an accepted brief, source ledger, stage and pending effects. Prove restart and reconciliation against the chosen backend. Chat history, memory, and resumable execution are not interchangeable. |
| Feedback | The [2.x terminal-response middleware](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/agents/middlewares/terminal_response_middleware.py) rejects a silent empty post-tool finish. [Batch acceptance](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/subagents/batch_acceptance.py) runs declared checks when supplied. | A nonempty reply or a successful worker run is not a verified deliverable. A file/schema check also does not establish that a citation supports a claim. |

## Two execution loops

### 1.x: a research graph with explicit routing

The graph starts at the coordinator; it can clarify intent, end a simple
interaction, or route substantive work to the planner, optionally through
background investigation. The planner emits structured steps. The research
team routes the first unfinished research, analysis, or processing step to its
corresponding worker, then returns to the planner when results exist. The
reporter is the final graph node. This is more constrained than giving a
generalist a research playbook, but the model still chooses the plan,
interpretation, and report.

Three details change what the graph actually guarantees:

- Human review is conditional: the feedback node interrupts unless
  `auto_accepted_plan` is set. The HTTP path uses an in-memory checkpointer and
  a LangGraph resume command; the bundled CLI workflow sets auto-accept true.
  Even without auto-accept, the planner can go straight to the reporter when
  it judges the context sufficient or reaches the iteration cap.
- The research-team router tests whether `execution_res` is populated. A worker
  error can populate that field and the observation list. The graph can
  therefore advance with an error observation, not only usable evidence.
- Reporter completion says the graph ended. It does not establish source
  sufficiency, factual support, or persistence across process loss.

See the [pinned source ledger](deerflow-source-ledger.md) for the exact branches
and evidence limits.

### 2.2.0: a general runtime with a research policy

The Gateway admits a run with task context; the lead assembly combines model,
instructions, authorized tools, and middleware. The deep-research skill guides broad discovery, deeper reads,
source diversity and validation, and a synthesis check. Delegation is a
separate conditional runtime capability, not a required research stage.
Neither is a mandatory research graph for every run. The
[v2.2.0 release notes](https://github.com/bytedance/deer-flow/releases/tag/v2.2.0)
also distinguish skill `allowed-tools` compatibility metadata from actual tool
authorization, and describe an optional, default-disabled script workflow
extension. An explicit workflow can therefore be built on the general runtime
without assuming one is enforced by ordinary research prompts. Compare the checked-in instructions
with actual runtime records: did the run load the skill, invoke only approved
tools, preserve evidence, and return an accepted artifact?

The general runtime gives an operator reusable execution and state controls,
but a specialist still needs an acceptance contract. Conversely, a separate
research graph is worth the additional state and maintenance when missing a
review, source class, or escalation is consequential enough to require a hard
transition. For exploratory work, a generalist with a research skill, bounded
retrieval, and independent checks may be enough.

## Delegation: completion is not acceptance

The [worker executor](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/subagents/executor.py#L1982-L2046) can represent a budget-capped worker as completed with a separate cap reason. Preserve that reason on handoff. [Receipt verification](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/agents/middlewares/receipt_verification.py#L79) is evidence for a reported action, not proof that the resulting report is correct. Keep worker termination, observed effects, and parent acceptance separate.

The sample config declares three running slots and 64 queued, with a
300-second queue timeout, shared by ordinary tasks and durable batches. It
also documents a distinct default of six delegations per lead run. These are
configuration examples, not measured throughput. The optional acceptance judge
is off in the sample; a runtime with receipts is not automatically a semantic
reviewer.

## Apply it: a bounded research specialist

For a concrete screening contract, see the [evidence sufficiency checkpoint](research-evidence-checkpoint.md).

Start with one assignment type and one acceptance contract, not a general
workflow engine. An outer coordinator can own assignment, budget, approvals, and
the final disposition. A specialist can own graph transitions and report
checkpoints without making the coordinator reimplement its loop.

1. Accept a question, scope, source requirements, and the time/tool budget.
2. Let a model generate queries and identify conflicts. Record retrieved source
   identities, provenance, and evidence spans; deduplicate and enforce the
   required source classes in code.
3. Let the model draft and map consequential claims to evidence. Deterministically
   validate artifact shape and evidence references; separately review whether the
   cited evidence actually supports the claim. Escalate consequential conflicts
   that the verifier cannot resolve.
4. Retry evidence gaps only within a declared bound. Return an evidence bundle and
   explicit disposition (accepted, insufficient evidence, or needs review).
   Never turn budget exhaustion, a convincing draft, or a successful model call
   into verified completion.

To compare against a generalist baseline, hold the question set, model and
retrieval budget constant. Score independently reviewed claim support, unsupported
claims wrongly accepted, abstentions, cost, and interventions. Include conflicting
sources, a valid URL that does not support the claim, and interruption after
retrieval. Check that resume does not duplicate external effects and that a
missing artifact fails acceptance. These are proposed tests, not reported
DeerFlow benchmark results.

For a concrete fixture, use two dated source snapshots that disagree and one
source that is retrievable but irrelevant. Require a delivered report and a
ledger mapping each material claim to a source and excerpt. Interrupt after
one source result is stored, resume, and confirm that the durable record and
final report agree. Then remove one necessary source or force a worker budget
stop. An acceptable result explicitly identifies the gap and holds delivery
rather than treating a citation, terminal response, or graph transition as
success.
