# Software factory source records

Accessed 2026-10-31. Scores are author assessments (currency, relevance, authority, accuracy, purpose), not empirical confidence probabilities. Source IDs are stable. Each extraction is limited to what was actually read; official docs establish documented semantics, not executed behavior. See the brief for synthesis and the log for exclusions.

## S1: Matt Maher, How the Pros Actually Work With AI Now

- Source: [Matt Maher, How the Pros Actually Work With AI Now](https://www.youtube.com/watch?v=KbuSHtTeyEA)
- Retrieved surface: https://moderncreator.app/2026-10-23-matt-maher-how-the-pros-actually-work-with-ai-now
- Date/type: 2026-10-23; third-party timestamped transcript
- Assessment: C4 R5 A3 A2 P3 = 17/25
- Retained extraction: The author describes a conversational director, durable domains of responsibility, model allocation, live steering and hierarchical coordination. Repeated corrections can motivate new role definitions.
- Limits: Mediated account; original captions rate-limited. Evidence of the described method, not proof of implementation correctness, scalability or output quality.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S2: Justin McCarthy / StrongDM, Software Factories And The Agentic Moment

- Source: [Justin McCarthy / StrongDM, Software Factories And The Agentic Moment](https://factory.strongdm.ai/)
- Retrieved surface: https://factory.strongdm.ai/
- Date/type: 2026-02-06; primary practitioner account
- Assessment: C5 R5 A4 A3 P2 = 19/25
- Retained extraction: Describes specification/scenario-driven code production and service twins. Highlights tests being changed or trivially satisfied and moves user scenarios outside the implementation boundary.
- Limits: Commercial self-report. No independent reproduction here; no-human-review and token-spend prescriptions are not adopted.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S3: StrongDM, The Principles

- Source: [StrongDM, The Principles](https://factory.strongdm.ai/principles)
- Retrieved surface: https://factory.strongdm.ai/principles
- Date/type: undated living page; primary practitioner guidance
- Assessment: C4 R5 A4 A3 P2 = 18/25
- Retained extraction: Connects seed, end-to-end validation and feedback in a repeated production loop. Validation should include integrations and economics.
- Limits: Same organization as S2, not independent corroboration. Unbounded looping is not adopted.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S4: Anthropic, Building effective agents

- Source: [Anthropic, Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- Retrieved surface: https://www.anthropic.com/research/building-effective-agents
- Date/type: 2024-12-19; primary engineering guidance
- Assessment: C3 R5 A5 A4 P3 = 20/25
- Retained extraction: Distinguishes predefined workflows from dynamic agents. Orchestrator-workers decomposes and synthesizes work. Recommends beginning with simple systems and evaluating complexity against latency and cost.
- Limits: Historical architecture guidance; page explicitly notes tooling has changed. Not a universal benchmark or client API contract.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S5: Anthropic, How we built our multi-agent research system

- Source: [Anthropic, How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system)
- Retrieved surface: https://www.anthropic.com/research/multi-agent-research-system
- Date/type: 2025-06-13; primary production account
- Assessment: C4 R5 A5 A4 P3 = 21/25
- Retained extraction: Reports lead/worker research architecture, bounded delegation descriptions and context separation. Notes duplicated exploration, excessive agents and communication overhead. Warns that tightly dependent coding work can be a poor parallelization fit.
- Limits: Research-system experience and internal evaluation; do not transfer its performance or token ratios to a software factory.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S6: Temporal, Workflow message passing

- Source: [Temporal, Workflow message passing](https://docs.temporal.io/encyclopedia/workflow-message-passing)
- Retrieved surface: https://docs.temporal.io/encyclopedia/workflow-message-passing
- Date/type: living official documentation
- Assessment: C5 R5 A5 A4 P3 = 22/25
- Retained extraction: Separates read queries, asynchronous signals and tracked updates with responses. Provides a concrete documented distinction between sending a change and observing its processing.
- Limits: Temporal-specific semantics; portable acknowledgement protocol is our synthesis. No Temporal deployment or handler behavior reproduced.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S7: Cemri et al., Why Do Multi-Agent LLM Systems Fail?

- Source: [Cemri et al., Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657v3)
- Retrieved surface: https://arxiv.org/abs/2503.13657
- Date/type: 2025-10-26 v3; primary research abstract
- Assessment: C4 R5 A5 A4 P4 = 22/25
- Retained extraction: The revised abstract describes MAST categories spanning system design, inter-agent misalignment and task verification, derived through annotated traces.
- Limits: Abstract-level extraction; no dataset or judge reproduction. Search snippets described an older version, so older sample counts were excluded.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S8: Ong et al., RouteLLM

- Source: [Ong et al., RouteLLM](https://arxiv.org/abs/2406.18665v4)
- Retrieved surface: https://arxiv.org/abs/2406.18665
- Date/type: 2025-02-23 v4; primary research abstract
- Assessment: C3 R4 A5 A4 P4 = 20/25
- Retained extraction: Studies routing between stronger and weaker models using preference data to trade response quality against cost.
- Limits: Abstract-level finding; benchmark response routing is not evidence of task-level routing quality for tool-using workers. No savings percentage imported.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S9: DORA, State of AI-assisted Software Development 2025

- Source: [DORA, State of AI-assisted Software Development 2025](https://dora.dev/research/2025/dora-report/)
- Retrieved surface: https://dora.dev/research/2025/dora-report/
- Date/type: 2025; official report landing-page summary
- Assessment: C4 R4 A5 A4 P3 = 20/25
- Retained extraction: The official summary frames AI as amplifying existing organizational strengths and weaknesses and emphasizes the organizational system.
- Limits: Landing-page extraction, not full-report analysis or causal proof of factory effectiveness. Older 2024 throughput estimates are not treated as current results.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S10: Anthropic, Create custom subagents

- Source: [Anthropic, Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- Retrieved surface: https://code.claude.com/docs/en/sub-agents
- Date/type: living official documentation
- Assessment: C5 R5 A5 A4 P3 = 22/25
- Retained extraction: Documents separate model and effort fields, explicit skill loading and configurable background execution.
- Limits: Client-specific documentation, not tested locally or portable permission enforcement. Refresh version-sensitive settings before implementation.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.

## S11: StrongDM, Digital Twin Universe

- Source: [StrongDM, Digital Twin Universe](https://factory.strongdm.ai/techniques/dtu)
- Retrieved surface: https://factory.strongdm.ai/techniques/dtu
- Date/type: undated primary practitioner description
- Assessment: C4 R4 A4 A3 P2 = 17/25
- Retained extraction: Describes service-boundary behavioral clones and comparison against real dependencies to find differences.
- Limits: Same source family as S2/S3. Reported scale and fidelity not independently measured; a twin cannot establish live acceptance by itself.
- Destination: factory procedure, concept ledger and related templates; S6 additionally informs steering, S8/S10 model allocation, S11 assurance follow-up.
