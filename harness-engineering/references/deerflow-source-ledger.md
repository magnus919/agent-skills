# DeerFlow case study: evidence ledger

Accessed November 20, 2026. The legacy `main-1.x` snapshot is
`2ab28765803d4d9582aaa8f2f3355137d154e273`; the v2.2.0 tag resolves to
`58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a`. This ledger supports the
[case study](deerflow-case-study.md). Source inspection establishes code and
documented configuration at these revisions, not live behavior.

| Question | Primary evidence and observation | What it cannot establish |
|---|---|---|
| What is fixed in 1.x? | [Graph builder](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/graph/builder.py#L28-L77) registers named nodes and routes unfinished steps by type. It exports an uncheckpointed graph plus a separate MemorySaver constructor. | The quality of its plans or research. |
| Does a person always approve the plan? | [Planner exits](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/graph/nodes.py#L306-L397) allow report routing at the iteration bound or when the model judges the context sufficient. [Feedback node](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/graph/nodes.py#L458-L497) conditionally interrupts. [HTTP entry](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/server/app.py#L825-L850) can submit a resume command; the [CLI](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/workflow.py#L62-L78) auto-accepts. | An always-on approval gate or restart durability. |
| Is a completed step evidence? | [Worker failure handling](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/graph/nodes.py#L1246-L1277) stores an error observation in fields the [router](https://github.com/bytedance/deer-flow/blob/2ab28765803d4d9582aaa8f2f3355137d154e273/src/graph/builder.py#L28-L48) uses to identify finished steps. | Successful collection or factual validation. |
| What does 2.x run? | [Architecture](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/docs/ARCHITECTURE.md#L94-L154) describes pinned project context and the general lead; [assembly](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/agents/lead_agent/agent.py#L1196-L1255) builds and verifies the tool view. | That a particular run selected its research skill or exercised every control. |
| What makes a run research-oriented? | The [deep-research skill](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/skills/public/deep-research/SKILL.md), retrieved through authenticated Groktocrawl, lays out exploration, deeper retrieval, source diversity and validation, and a synthesis check. | Execution of those stages or a deterministic requirement to delegate. |
| Which containment and state are configured? | [Sample config](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/config.example.yaml#L1709-L1812) documents local and isolated providers; [Compose overlay](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/docker/docker-compose.dood.yaml) shows opt-in Docker host socket access. [Storage config](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/config.example.yaml#L2620-L2658) and [retention contract](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/docs/checkpoint-retention-contract.md) distinguish backends and replay targets. | Actual mount/network isolation, crash recovery, or exactly-once effects. |
| What qualifies a worker result? | [Receipts](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/agents/middlewares/receipt_verification.py#L79), [batch checks](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/subagents/batch_acceptance.py#L24), and [executor stop reasons](https://github.com/bytedance/deer-flow/blob/58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a/backend/packages/harness/deerflow/subagents/executor.py#L1982-L2046) separate claim provenance, bounded checks, and execution status. | Universal or independent semantic acceptance. |

The authenticated Groktocrawl deep run reported 120 retrieval attempts, 111
successful source captures, and evidence gaps. It surfaced the
[v2.2.0 release notes](https://github.com/bytedance/deer-flow/releases/tag/v2.2.0),
which document metadata-only `allowed-tools` and opt-in script workflows.
Its results also included unpinned and secondary material, so its synthesis
was not sufficient to attribute implementation details to the pinned release. Third-party summaries and generated research synthesis are
navigation aids, not independent corroboration. Unpinned pages were superseded
by pinned code or docs for mechanism claims. No DeerFlow code or test suite
was run for this case study.
