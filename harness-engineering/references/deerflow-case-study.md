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

## Delegation: completion is not acceptance

The [worker executor](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/subagents/executor.py#L1982-L2046) can represent a budget-capped worker as completed with a separate cap reason. Preserve that reason on handoff. [Receipt verification](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/agents/middlewares/receipt_verification.py#L79) is evidence for a reported action, not proof that the resulting report is correct. Keep worker termination, observed effects, and parent acceptance separate.

## Apply it: a bounded research specialist

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
