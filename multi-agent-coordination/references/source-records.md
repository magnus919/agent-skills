# Primary-source evidence records

Accessed 2026-11-02 UTC. Records separate source claims from our synthesis. No fleet or research benchmark was reproduced. See research-log.md for retrieval/exclusion decisions and research-synthesis.md for claim closure. Full copyrighted sources are linked rather than republished.

## S01 — OpenRig agent civilizations video
- Source: [OpenRig agent civilizations video](https://www.youtube.com/watch?v=AL-PQuB2wy0)
- Revision/date: English captions, 00:00–24:47; full transcript read.
- Evidence class: Author-reported experience.
- Retained claims: Stable seats, intent hierarchy, recursive checking, scope expansion, uninformed approval, shared-practice propagation and outcome-relative activity monitoring.
- Limit/counterevidence: No controlled prevention trial; analogies and the incident interpretation are hypotheses. Transcript does not establish audiovisual or deployed behavior.
- Disposition: retained → video-ledger.md and the relevant procedure references.

## S02 — OpenRig README
- Source: [OpenRig README](https://github.com/mvschwarz/openrig/blob/f3f8319d1ca6e7af3c7a2634603ffbf80be5ea90/README.md)
- Revision/date: f3f8319d1ca6e7af3c7a2634603ffbf80be5ea90.
- Evidence class: Documented design.
- Retained claims: Persistent teams, roles, shared context and owned work connect multiple existing harnesses.
- Limit/counterevidence: Feature documentation is not runtime verification.
- Disposition: retained → tool-lessons.md; ownership-and-flow.md.

## S03 — OpenRig coordination
- Source: [OpenRig coordination](https://openrig.dev/docs/coordination)
- Revision/date: Documentation declares 0.6.6.
- Evidence class: Documented semantics.
- Retained claims: Durable queue rows have owners and transition history; handoff is documented as transactional; closure records delivery rather than downstream acceptance. Blocked work needs continuation/wake.
- Limit/counterevidence: Mutable docs; no crash or atomicity trial performed here.
- Disposition: retained → ownership-and-flow.md; handoff template.

## S04 — OpenRig context
- Source: [OpenRig context](https://openrig.dev/docs/context)
- Revision/date: Documentation declares 0.6.6.
- Evidence class: Documented semantics.
- Retained claims: Context can be retrieved by reference and composed by situation. Serving context does not prove it was read; updates and synchronization are explicit.
- Limit/counterevidence: No proof of comprehension or live adoption.
- Disposition: retained → communication-and-context.md; context packet.

## S05 — OpenRig continuity
- Source: [OpenRig continuity](https://openrig.dev/docs/continuity)
- Revision/date: Documentation declares 0.6.6.
- Evidence class: Documented design.
- Retained claims: Stable seats carry recap/restore context across sessions.
- Limit/counterevidence: Identity continuity does not establish immortal execution or restored grants.
- Disposition: retained → ownership-and-flow.md.

## S06 — HERDR README
- Source: [HERDR README](https://github.com/herdrdev/herdr/blob/ee5bfb5041bb3e4a49d591c72308aae3c81ecdde/README.md)
- Revision/date: ee5bfb5041bb3e4a49d591c72308aae3c81ecdde.
- Evidence class: Documented design.
- Retained claims: Terminal background persistence, remote-machine visibility, status indicators and CLI/socket interaction. Restart restores layout and supported sessions; original processes do not survive.
- Limit/counterevidence: No local status accuracy, restart or remote-delivery experiment.
- Disposition: retained → tool-lessons.md; recovery drill.

## S07 — HERDR agent skill documentation
- Source: [HERDR agent skill documentation](https://herdr.dev/tui/docs/agent-skill/)
- Revision/date: Page references release v0.9.5.
- Evidence class: Documented interface scope.
- Retained claims: Distinguishes an agent operating HERDR from a guide teaching a human; release-matched skill discovery is available.
- Limit/counterevidence: External operational instructions were read as source data, not activated or executed.
- Disposition: retained → tool-lessons.md; tool assessment.

## S08 — Block/Buzz README
- Source: [Block/Buzz README](https://github.com/metroncorp/blockbuzz/blob/074561233eef71df9690ec22c2a9c5e798c297a7/README.md)
- Revision/date: 074561233eef71df9690ec22c2a9c5e798c297a7.
- Evidence class: Documented design.
- Retained claims: Workspace uses signed events to connect human/agent conversation, workflows, code events and approvals; community URL defines workspace scope.
- Limit/counterevidence: Authenticated authorship does not establish truth, authority or tested isolation.
- Disposition: retained → tool-lessons.md; decision packet.

## S09 — Buzz agent vision
- Source: [Buzz agent vision](https://github.com/metroncorp/blockbuzz/blob/main/VISION_AGENT.md)
- Revision/date: Mutable main, accessed date below.
- Evidence class: Author architecture description.
- Retained claims: ACP agent and MCP tool server are separate components; sessions have separate histories/tools and community-local agent state.
- Limit/counterevidence: Vision/design language and claimed isolation are not independent security evidence.
- Disposition: retained → tool-lessons.md; protocol-layer distinction.

## S10 — Why Do Multi-Agent LLM Systems Fail?
- Source: [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657v3)
- Revision/date: Cemri et al.; v3, 2025-10-26.
- Evidence class: Empirical taxonomy.
- Retained claims: MAST classifies design, inter-agent alignment and verification failures from annotated traces.
- Limit/counterevidence: Taxonomy is not a causal attribution or calibrated detector for this fleet. GroktoCrawl extraction favored appendix/code; abstract and selected full text checked separately.
- Disposition: retained → collective-failures.md.

## S11 — Towards a Science of Scaling Agent Systems
- Source: [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296v3)
- Revision/date: Kim et al.; v3, 2026-04-08.
- Evidence class: Controlled benchmark study.
- Retained claims: Five architectures across 260 configurations and six benchmarks show task-dependent gains and harms under controlled tools/prompts/compute.
- Limit/counterevidence: Earlier blog reports 180 configurations; do not mix revisions or universalize saturation cutoffs. No reproduction here.
- Disposition: retained → decomposition-and-topology.md; evaluation.md.

## S12 — Multi-Agent Design / MASS
- Source: [Multi-Agent Design / MASS](https://arxiv.org/abs/2502.02533v2)
- Revision/date: Zhou et al.; v2, 2026-01-31.
- Evidence class: Optimization study.
- Retained claims: Interleaves local prompt, topology and global prompt optimization.
- Limit/counterevidence: Optimized systems and search costs depend on its task/model space; no portable best topology follows.
- Disposition: retained → decomposition-and-topology.md.

## S13 — Anthropic multi-agent research system
- Source: [Anthropic multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system)
- Revision/date: 2025-06-13.
- Evidence class: First-party engineering report.
- Retained claims: Independent context windows and clear objective/output/tool/task boundaries help broad research; reports duplication without clear delegation and costly multi-agent operation.
- Limit/counterevidence: Internal evaluation, model mix and budget differ; reported gains do not isolate topology or establish coding transfer.
- Disposition: retained → assignment template; decomposition and evaluation procedures.

## S14 — Building effective agents
- Source: [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- Revision/date: 2024-12-19; page flags tooling changes.
- Evidence class: First-party design guidance.
- Retained claims: Recommends simple composable workflows and increasing complexity only when warranted; distinguishes predefined workflows and dynamic agents.
- Limit/counterevidence: Historical operational examples need current documentation; retained only for design rationale.
- Disposition: retained → baseline and complexity decision in SKILL.md.

## S15 — Prompt Infection
- Source: [Prompt Infection](https://arxiv.org/abs/2410.07283v1)
- Revision/date: Lee and Tiwari; 2024-10-09.
- Evidence class: Security experiments.
- Retained claims: Demonstrates self-replicating agent-to-agent injection and examines combinations of source tagging and prompt defenses.
- Limit/counterevidence: Tagging alone is insufficient; tested models/attacks do not prove general immunity. Distinguish malicious injection from accidental bad conventions.
- Disposition: retained → shared-knowledge.md.

## S16 — The Cost of Consensus
- Source: [The Cost of Consensus](https://arxiv.org/abs/2605.00914v1)
- Revision/date: Bertalanič and Fortuna; 2026-04-29.
- Evidence class: Controlled debate study.
- Retained claims: Homogeneous small-model debate can underperform isolated self-correction and consume more tokens; identifies conformity and discarded correct answers.
- Limit/counterevidence: Specific 7–8B models, two reasoning benchmarks and fixed debate setup; no claim all debate fails.
- Disposition: retained → collective-failures.md.

## S17 — MultiAgentBench
- Source: [MultiAgentBench](https://aclanthology.org/2025.acl-long.421/)
- Revision/date: Zhu et al.; ACL 2025.
- Evidence class: Benchmark paper.
- Retained claims: Evaluates task completion plus milestone collaboration measures and multiple topology/protocol choices.
- Limit/counterevidence: Scenario-specific best architecture does not establish universal superiority.
- Disposition: retained → evaluation.md.

## S18 — Time, Clocks and the Ordering of Events
- Source: [Time, Clocks and the Ordering of Events](https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/)
- Revision/date: Lamport; 1978; author retrospective.
- Evidence class: Distributed-systems foundation.
- Retained claims: Explains causal ordering and distributed state-machine coordination.
- Limit/counterevidence: Foundation, not LLM-agent effectiveness evidence; proposed envelope is our synthesis.
- Disposition: retained → communication-and-context.md.

## S19 — Sagas
- Source: [Sagas](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf)
- Revision/date: Garcia-Molina and Salem; 1987.
- Evidence class: Transaction design foundation.
- Retained claims: Compensating transactions address partial long-lived sequences without one long atomic transaction.
- Limit/counterevidence: Compensation does not imply reversal of arbitrary real-world effects or disclosures.
- Disposition: retained → authority-and-recovery.md.

## S20 — A2A specification
- Source: [A2A specification](https://a2a-protocol.org/latest/specification/)
- Revision/date: Mutable latest; access-dated, no implementation pin.
- Evidence class: Official protocol.
- Retained claims: Defines interoperable task/message/artifact concepts and lifecycle.
- Limit/counterevidence: Read via web after GroktoCrawl failed. Version/transport support must be negotiated; protocol compliance is not coordination correctness.
- Disposition: retained → communication-and-context.md.

## S21 — OpenAI Hugging Face incident report summary
- Source: [OpenAI Hugging Face incident report summary](https://openai.com/index/hugging-face-incident-and-the-road-ahead/)
- Revision/date: 2026-08-26.
- Evidence class: First-party incident investigation.
- Retained claims: Documents reward hacking, unsafe persistence, unauthorized communication and agents adopting goals from peers.
- Limit/counterevidence: Video context-only interpretation is incomplete; neither source proves reminders would have prevented the incident.
- Disposition: retained → authority-and-recovery.md; video-ledger.md.

## S22 — AgentCollabBench
- Source: [AgentCollabBench](https://arxiv.org/abs/2605.08647v1)
- Revision/date: Mazumder et al.; 2026-05-09.
- Evidence class: Diagnostic benchmark/preprint.
- Retained claims: Tests instruction decay, false-belief spread, cross-task leakage and tracer survival; converging branches can lose minority constraints.
- Limit/counterevidence: Synthetic diagnostic probes and model/judge conditions; trace survival is not comprehension, and authors qualitative causal claims need bounded transfer.
- Disposition: retained → emerging-research.md; synthesis-boundary eval proposal.

## S23 — MAScope: Know the Shape, Find the Fault
- Source: [MAScope: Know the Shape, Find the Fault](https://arxiv.org/abs/2610.10126v1)
- Revision/date: Liu et al.; 2026-10-07.
- Evidence class: Diagnosis study/preprint.
- Retained claims: Topology-conditioned diagnosis uses message-grounded graph extraction and reports improved classification on its corpora.
- Limit/counterevidence: Association is not proof of cause; judge output and projected costs are not this host runtime evidence.
- Disposition: retained → emerging-research.md; incident topology record.

## S24 — Silo-Bench
- Source: [Silo-Bench](https://arxiv.org/abs/2603.01045v2)
- Revision/date: Zhang et al.; v2, 2026-04-13.
- Evidence class: Distributed reasoning benchmark.
- Retained claims: Finds active communication and plausible topology can coexist with incorrect synthesis of distributed information.
- Limit/counterevidence: Algorithmic tasks, limited protocols and homogeneous models; communication activity is not accepted work.
- Disposition: retained → emerging-research.md; integration/sufficiency challenges.

## S25 — When Agents Coordinate
- Source: [When Agents Coordinate](https://arxiv.org/abs/2608.16801v1)
- Revision/date: Destefanis and Aste; 2026-08-17.
- Evidence class: Coding experiment/preprint.
- Retained claims: Temporal agent/file networks reveal task-dependent channels; naming a coordinator alone does not ensure a hub or reliable benefit.
- Limit/counterevidence: Synthetic Python tasks; shell file activity undercounted, token attribution approximate, uncontained findings challenged by sealed replication.
- Disposition: retained → emerging-research.md; outcome/telemetry limits.

## S26 — Passes Alone, Fails Together / STALE
- Source: [Passes Alone, Fails Together / STALE](https://arxiv.org/abs/2609.25396v1)
- Revision/date: Xia, Wu and Park; 2026-09-21.
- Evidence class: Semantic coordination benchmark.
- Retained claims: Tests the same suite on solo and combined patches. Controlled tasks show interference while corrected grading finds little in mined reviewed Django PR pairs.
- Limit/counterevidence: Constructed failure prevalence must not be treated as field prevalence; different solo/merged suites can manufacture interference.
- Disposition: retained → emerging-research.md; matched integration testing.

## S27 — DPBench
- Source: [DPBench](https://arxiv.org/abs/2602.13255v2)
- Revision/date: Hasan and BusiReddyGari; v2, 2026-06-03.
- Evidence class: Controlled resource-contention benchmark.
- Retained claims: Varies action protocol, communication and group size; resource ordering and symmetry breaking change deadlock behavior in its testbed.
- Limit/counterevidence: Dining Philosophers is a controlled mechanism probe, not a fleet-wide reliability or team-size prescription.
- Disposition: retained → emerging-research.md; resource-ordering recovery drill.
