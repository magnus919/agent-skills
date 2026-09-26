# Source coverage and adaptation decisions

Source snapshot: WalkingLabs commit 77e7a3e21469dcbece2558086c8d91657abeaa40.
This map is an extraction/review ledger, not a claim that translations, every app
component, all external links, or all vendor internals were exhaustively audited.
English curriculum concepts, project contracts, four product breakdowns, bundled
skill patterns and selected scripts were reviewed. The separate source inventory
records content hashes and review scope; an inventory/hash is not proof of reading.

## Fourteen lectures

| Lecture | Knowledge extracted | New skill home (relative to skill root) | Adaptation/caveat |
|---|---|---|---|
| 01 | Failure taxonomy and diagnostic loop | references/diagnosis.md | Anonymous outcome percentages and benchmark extrapolation are not adopted |
| 02 | Instructions/tools/environment/state/feedback; component ablation | references/runtime-design.md | Ablation ranks contribution, not causality; avoid duplicate taxonomy |
| 03 | Fresh-session questions; knowledge proximity; ACID analogy | references/instructions-and-knowledge.md, references/initialization-and-session-lifecycle.md | Repo is not universally sole/highest authority; connectors and durable stores can be legitimate |
| 04 | Entry map; progressive disclosure; contradictory rules; instruction debt | references/context-design.md, references/instructions-and-knowledge.md | No universal 100-line or token-percentage rule; measure fidelity |
| 05 | Context lifetime, handoffs, external decisions and progress | references/context-and-state.md, references/context-design.md | Compaction and reset are distinct interventions; test actual model behavior |
| 06 | Initializer versus coding worker; readiness and startup contract | references/initialization-and-session-lifecycle.md | One standard readiness path need not reinstall dependencies every session |
| 07 | Scope surface, dependencies, WIP, verified completion | references/context-and-state.md, references/loops-and-coordination.md | WIP=1 is a default; never infer acceptance from mutable tracker status |
| 08 | Task state, verification/evidence, transition gates | references/context-and-state.md, scripts/contracts.py | Passing evidence becomes stale after changes; JSON does not enforce itself |
| 09 | Externalized completion; layered checks; maker/checker | references/verification-and-improvement.md, templates/acceptance-contract.md | Risk-appropriate checks; separate model review is not truth or permission |
| 10 | Full-path verification; architecture boundaries; review-to-rule promotion | references/instructions-and-knowledge.md, references/observability-and-feedback.md | Toy e2e runner simulates outcomes; grep screens are not full semantic enforcement |
| 11 | Runtime observability; sprint contract; evaluator criteria | references/observability-and-feedback.md, templates/acceptance-contract.md | Minimize sensitive traces; ordinal scores are not release evidence |
| 12 | Restartability; immediate/periodic upkeep; harness simplification | references/initialization-and-session-lifecycle.md, references/verification-and-improvement.md | No automatic reset/delete/commit; benchmark examples are simulations |
| 13 | Goal/timer/event loops; six primitives; four silent costs | references/loops-and-coordination.md, templates/loop-contract.md | No infinite task loop; explicit scheduling/delegation authority; complete costs |
| 14 | Nodes/edges/state/routing; conflicts; anchors; orchestration tax | references/loops-and-coordination.md, templates/graph.json, scripts/contracts.py | Graph shape alone cannot fix bad metrics/authority; persistent checkpoints and real checks |

## Eight projects

| Project | Practice extracted | How it informs this skill | Evidence limit |
|---|---|---|---|
| 01 | Prompt-only versus explicit minimal harness | Same task/model/config; task outcomes not artifact score | Starter/solution product state differs; reconstruct comparable initial state before causal comparison |
| 02 | Agent-readable workspace and import/persistence continuity | Fresh-session source discovery and restart exercise | Documentation presence is weaker than actual recovery |
| 03 | Scope control through indexing and grounded QA sessions | Task/evidence/dependencies and interruption handoff | Citation presence is not grounding correctness |
| 04 | Seeded large-document chunking defect; logging/boundaries | Reproduce → trace → first divergence → repair → same workload | Must exercise actual services/UI, not only scanner strings |
| 05 | Single role versus generator/evaluator versus three-role setup | Acceptance contract and separate checking, fixed feature | Checked-in rubric scores are examples, not our measurements |
| 06 | Capstone observability, cleanup and benchmark | Golden journey, restartability, maintenance experiment | Shell benchmark simulates operations; does not benchmark agent behavior |
| 07 | Goal, timer, maker/checker experiments | Entry-mode selection, authority, stop/no-progress/cost bounds | Scheduling primitive does not guarantee correctness |
| 08 | Explicit graph, fan-out/fan-in, rollback and approval | Shared-state/routing/ownership and terminal-path checks | Graph skeleton stubs verification/model calls and uses in-memory state |

Project source directories and descriptions are teaching resources. We did not
install all Electron applications or claim their reference solutions are production
ready. Supporting code was inspected selectively at the verification, benchmark,
and runtime boundaries that affect the proposed skill.

## Four design breakdowns

| Breakdown | Portable design idea | Verification boundary |
|---|---|---|
| Pi | Small kernel, programmable extension, on-demand context | Course interpretation; no independent source audit of current Pi runtime |
| Claude Code | Scoped memory, hooks, context isolation and session state | Official hook/context docs checked; community internals/caps not generalized |
| Codex | Discoverable source map, executable invariants, isolated work | OpenAI engineering case study checked; team's setup is not universal product behavior |
| DeepSeek | Model/provider/tool/plugin seams and explicit event pipeline | Course architecture interpretation; no claim every plugin configuration enforces policy |

The initial draft incorrectly said the English Claude Code and Codex breakdowns
were missing. They exist in the pinned snapshot; this review corrects the finding.

## Resource and Harness Creator extraction

- Repo template/SOPs: domain ownership, source routes, architecture constraints,
  observable journey, encode invisible decisions, query→repair→restart→rerun.
  The course's particular layer ordering is an example, not a universal architecture.
- Harness Creator: scaffold/audit/report entry points, state/handoff templates,
  memory/context/tool/lifecycle patterns, and declarative cases.
- Rejected as universal rules: local overrides always beat organization policy;
  all hooks share one trust/failure policy; all forks must be single-level;
  fixed memory caps; erase terminal output before recoverable acknowledgement.
- Creator structural score/self-check: replaced by observations and unknowns;
  no readiness score or unsupported causal bottleneck.
- Upstream cases: topic coverage informs new schema-v1 cases, not imported
  expectations/numeric IDs or a claim that those cases executed.
- Upstream graph: model calls stubbed; a test substring and approved substring
  are placeholders; attempts are not incremented; merge prints only; MemorySaver
  is not process-durable. New contracts challenge those exact failure classes.
- Upstream lecture e2e and benchmark code includes simulated outcomes. The
  capstone shell benchmark uses simulated operations and floating timestamps in
  shell integer arithmetic. Treat this as code-review evidence of an example's
  limitations, not a measured execution failure or benchmark result.

## What the new skill adds

Explicit entry and exit artifacts; specialist round-trip contracts; protected
acceptance and revision-bound evidence; task/graph/run declaration validators;
comparison refusal for confounded records; bounded check execution with atomic
progress reports; partial-effect reconciliation; fidelity probes; event criticality;
worked use cases; near-miss tests; and honest separation of validation from outcome
quality. These additions are our synthesis, not upstream claims of proved efficacy.
