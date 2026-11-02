# Learn from tools without inheriting their opinions

Accessed 2026-11-02. These are documented designs, not locally deployed trials.
Read source records for immutable README revisions and evidence limits. A tool's
feature list is not a benchmark, security assessment or recommendation to install.

| Tool | Distinctive surface | Portable lesson | What must be independently tested |
|---|---|---|---|
| [HERDR](https://github.com/herdrdev/herdr/blob/ee5bfb5041bb3e4a49d591c72308aae3c81ecdde/README.md) | Background terminals, multiple machines, working/blocked/idle indicators, CLI/socket operation | Separate session visibility and liveness from durable work ownership and accepted outcomes | State signal accuracy, actual wait completion, reconnect versus process restart, message delivery |
| [Block/Buzz](https://github.com/metroncorp/blockbuzz/blob/074561233eef71df9690ec22c2a9c5e798c297a7/README.md) | Self-hosted workspace with signed events and identity/community-scoped participation | Correlate conversation, artifacts and decisions with authenticated provenance and workspace boundaries | Replay/deduplication, membership enforcement, approval scope, cross-community isolation, compromised identities |
| [OpenRig](https://github.com/mvschwarz/openrig/blob/f3f8319d1ca6e7af3c7a2634603ffbf80be5ea90/README.md) | Stable seats, context, owned queues and work hierarchy across harnesses | Keep role continuity, task transfer, intent lineage and acceptance distinguishable | Claim/handoff atomicity, stale occupant fencing, context adoption, crash recovery, actual integrated delivery |

## Different layers can compose

HERDR can provide terminal/session management while another system owns work
coordination. The supplied video explicitly says its author uses HERDR as a
wrapper and OpenRig for coordination. Buzz's workspace/event model and its ACP
agent/MCP tool components are distinct layers too. Avoid comparing all three as
identical products or copying their full architectures into a methodology.

For each mechanism ask: what failure motivates it; what guarantee is documented;
what layer implements it; what evidence exists; what does it cost; what simpler
alternative exists; how does it fail? Use the tool-assessment template. Check
current release-matched documentation before issuing commands. This skill
intentionally does not include vendor installation or operational runbooks.

## Invariants to carry across tools

- Stable address is distinct from occupant identity and current permission.
- Message delivery, claim, execution, artifact delivery and acceptance are separate.
- Session restoration is distinct from survival of a process or external operation.
- Context assembly is distinct from retrieval, adoption and correct application.
- Authenticated authorship is distinct from trustworthy content and authority.
- A queue, graph or event log needs an owner for integration and unknown effects.

These are our synthesis and test obligations, not promises made collectively by
the three projects. No side-by-side runtime, performance or reliability ranking
was performed. Preserve that boundary when adding another tool to this comparison.
