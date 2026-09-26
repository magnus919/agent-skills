# Source assessment and evolution

Reviewed source: WalkingLabs `learn-harness-engineering`, commit
`77e7a3e21469dcbece2558086c8d91657abeaa40`. This skill synthesizes its course and
Harness Creator rather than importing product claims wholesale. See
[upstream repository](https://github.com/walkinglabs/learn-harness-engineering/tree/77e7a3e21469dcbece2558086c8d91657abeaa40).

## Knowledge inventory

- Lectures 1–4: failure patterns, five subsystems, repository as system of record,
  instruction routing instead of an encyclopedia.
- Lectures 5–8: session continuity, initialization, scope/WIP, machine-readable
  feature state with acceptance and evidence.
- Lectures 9–12: termination, full-path verification, observability, handoff,
  cleanup, architectural invariants, feedback promoted into executable checks.
- Lectures 13–14: goals, schedules, maker/checker, external state, loop costs,
  graph nodes/edges/state/routing, rollback, approvals, orchestration overhead.
- Eight project descriptions: six checked-in Electron/TypeScript knowledge-base
  starter/solution exercises, then loop and graph experiments. These are useful
  teaching tasks, not an independent production benchmark corpus.
- Resources: root instructions, initialization, progress, feature tracking,
  evaluator rubrics, quality documents, architecture and observability SOPs.
- Product breakdowns: all four English pages (Pi, Claude Code, Codex, DeepSeek)
  are present. The initial assessment incorrectly reported two absent; this
  deeper review corrects that finding. Product internals are not universal rules.
- Harness Creator: scripts for scaffolding, structural scoring, JSON/HTML reports,
  and self-checking; seven references; ten declarative output-quality cases.

## What changed in this evolution

Preserved creation, audits, handoffs, memory/context/tool patterns, and shareable
reports. Expanded the operating procedure to diagnosis, custom runtime design,
bounded orchestration, recovery, experiments, and maintenance. The catalog already
owns evaluation and production operations; this skill routes to those owners.

The course uses instructions/tools/environment/state/feedback; upstream's skill
scores instructions/state/verification/scope/lifecycle. Use one five-subsystem
model here and treat scope/lifecycle as cross-cutting requirements.

The upstream audit scans a fixed set of root filenames and text patterns. Its
self-check scaffolds and scores its own templates; it does not run agent tasks or
project verification. Replace numeric readiness/bottleneck implications with
explicit structural findings and unassessed behavioral evidence.

Upstream graph code deliberately stubs model calls, checks `"def test" in code`,
accepts `"approved" in review`, and prints a merge. It uses MemorySaver and does
not increment its attempts counter. Those examples are not a durable, bounded,
verified runtime. The new references require real checks and persisted recovery.

The course calls passing feature state irreversible; this skill binds evidence
to a revision and allows invalidation after changes. The upstream Python scaffold
tolerates pytest collecting zero tests; that cannot establish verified behavior.
Do not copy its empirical percentages or anonymous team stories as validated
results; consult original sources before using specific product or outcome claims.

Upstream evals use numeric IDs and `expectations` without our schema version.
These are replaced with repository-v1 cases; IDs are new because this is a new
catalog manifest, not a silent rename of an existing catalog suite. There was no
Harness Creator in this catalog at the time of review, so no routing stub is
introduced for a nonexistent directory. Existing installations can migrate by
installing this skill and retaining their project files, then disabling the old
skill's duplicate trigger. Script CLI migration is documented separately.

## Attribution and primary sources

Substantive ideas and template structure adapted from WalkingLabs under MIT;
see the bundled LICENSE. The Python tooling is a new implementation.

- [OpenAI harness engineering](https://openai.com/index/harness-engineering/)
- [Anthropic effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic long-running application harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)

The deeper review checked these primary engineering articles plus Anthropic
context/tool guidance and hook documentation. Their observations remain scoped
to their reported systems/tasks. Recheck installed-product semantics when they
affect implementation; no complete vendor-internals audit is claimed.
