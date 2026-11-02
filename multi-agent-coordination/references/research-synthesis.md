# Research synthesis and claim closure

Question, scope and stopping criteria were declared in research-brief.md. Source
records S01–S27 contain source-level extraction and limits; research-log.md records
searches and exclusions. Accessed 2026-11-02 UTC.

## Findings

| Finding | Evidence and counterevidence | Confidence and implementation |
|---|---|---|
| Coordination is an independent design discipline across harnesses | S02–S09 expose different runtime/workspace/team layers; S10 identifies cross-agent failures | High confidence in the ownership boundary; new SKILL.md and catalog-boundaries.md |
| Topology must fit task, resources and information coupling | S11/S12/S13 support task-dependent design; S24/S25 challenge automatic benefits of communication or coordinator titles | Moderate confidence in transferable selection procedure, no universal best shape; decomposition-and-topology.md |
| Context and authority must meet at the decision boundary | S01/S04 motivate intent recovery; S21 shows multiple contributing causes beyond missing context | High confidence in keeping grants separate; reminder efficacy unverified; communication-and-context.md and harness enrichment |
| Persistent owned work needs effect-aware handoff and recovery | S03/S06 document lifecycle distinctions; S18/S19 ground causality and partial-work handling | High confidence in explicit contracts; actual host guarantees unverified; ownership-and-flow.md, recovery templates |
| Shared knowledge can propagate error across sessions | S01 reports recurrence; S15 demonstrates adversarial propagation under its conditions | Moderate confidence in source/consumer tracing as a recovery method; no eradication-rate claim; shared-knowledge.md |
| Delivery and conduct need team-level evaluation | S17/S22/S24 distinguish milestones, constraint survival and synthesis; S26 demonstrates grading confounds | High confidence in separate evidence dimensions and matched suites; effectiveness of this skill unassessed; evaluation.md |
| Coordination overhead requires diagnosis, not automatic removal | S01 motivates ceremony monitoring; S11/S16/S25 show limited/task-dependent costs and harms | Moderate confidence in diagnostic signals, unknown detector thresholds; collective-failures.md |

## Contradictions preserved

The video emphasizes context engineering; S24 shows sufficient information can
still be combined incorrectly, while S21 identifies additional misalignment and
control failures. The skill requires evidence sufficiency, reasoning/integration
checks and runtime boundaries together. It does not repeat a context-only cure.

S11's revised paper describes 260 configurations and six benchmarks, whereas its
earlier Google blog describes 180. Retain v3 for current claims and reject the
older quantitative summary as a basis for current thresholds. S26 finds high
failure on constructed tasks and little interference on mined reviewed changes;
these are different populations, not competing estimates of field prevalence.
S25's sealed replication limits conclusions from earlier uncontained runs.

## Confidence and missing evidence

Primary papers, official docs and first-party incident/engineering accounts are
appropriate for source-grounded design, but their independence and experimental
conditions differ. Tool docs establish documented mechanisms, not tested service
behavior. Research includes peer-reviewed work and recent preprints; venue status
does not validate local transfer. This is a bounded deep review, not an exhaustive
systematic literature search or a meta-analysis.

No live HERDR, Block/Buzz or OpenRig deployment was installed, and no fleet cleanup,
message, paid model experiment or benchmark replication was run. The offline
helper's tests observe its code only. Portable semantic evals and author rubric
challenges are not independently adjudicated model-quality/release evidence.

## Durable inventory and completion audit

- Source-level claims, contradictions and limits: source-records.md, all S01–S27.
- Video extraction: video-ledger.md, complete caption interval accounted for.
- Discovery/fallback/exclusion decisions: research-log.md.
- Retrieval digests: retrieval-receipts.json, not substitutes for source text.
- Portable procedures: topic references and SKILL.md, linked to evidence records.
- Reusable artifacts: nine Markdown templates and the fictional snapshot.
- Executable bounded mechanism: coordination.py plus test_coordination.py.
- Behavioral contracts and challenge examples: evals/evals.json and assertion-challenges.md.
- Verification/publication boundaries: evals/validation.md.

All retained sources have an extraction/disposition record. Remaining research
questions are preserved in emerging-research.md. Broad discovery stopped after
coverage of every scope dimension, primary counterevidence and recent 2026 work;
additional source count alone would not establish completeness or effectiveness.
