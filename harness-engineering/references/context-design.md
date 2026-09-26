# Design context as a measured information path

## Diagnose the context problem

Separate missing information, irrelevant information, stale information, poor
retrieval affordances, and coherence loss. More tokens fix only some of these.
Inspect what the agent actually loaded and used, not just what files exist.

Measure per phase: input/output tokens (from provider usage when available),
retrieval/tool bytes, repeated reads, startup latency, correction attempts,
compactions/resets, and accepted task outcomes. Character counts are size proxies,
not tokenizer measurements. Record unavailable usage rather than inventing it.

## Choose the operation

| Operation | Use when | Failure to challenge |
|---|---|---|
| Select/JIT retrieve | Large information space, sparse task relevance | Critical source never discovered |
| Write durable notes | Decisions/work must outlive a context | Stale summary mistaken for current fact |
| Compress/compact | Coherent session but growing repeated history | Acceptance/authority lost in summary |
| Reset with structured handoff | Measured loss of coherence persists after compaction | Missing state or expensive rediscovery |
| Isolate work contexts | Independent exploration pollutes parent context | Worker misses required constraints |
| Cache/memoize | Stable context construction repeats | Revision changes without invalidation |

Start with a hybrid: small authoritative map plus on-demand sources. Do not
force resets on a newer model because they helped a previous one. Run long-task
and interruption cases on the actual model/runtime before adopting that cost.

## Budget design

Set reserves for tool results, acceptance verification, final reporting, and
recovery. Prefer compaction before the reserve is exhausted. Thresholds come from
observed task demands and host behavior; percentages such as 80% are candidate
settings, not standards.

Each bounded block needs: source ID/version, purpose, size, inclusion condition,
priority, truncation flag, and recovery pointer. Never silently truncate authority,
acceptance, or unresolved side effects. Emit an explicit insufficient-context
status when a decisive source cannot fit or cannot be retrieved.

Compress low-value repetition before lossy summarization. Keep decisions,
rejected alternatives that constrain the next step, blockers, source pointers,
candidate revision, and check evidence. Exclude secrets and avoid retaining full
intermediate reasoning by default. Test compaction with questions whose answers
must survive; a fluent summary is not a fidelity check.

## Retrieval and memory

Let metadata narrow the search, then retrieve relevant excerpts with source
pointers. Distinguish no match, access denied, stale index, and conflicting facts.
Use stable identities and versioned memory; derived facts can often be reread from
source. Long-term user preferences need scope and an explicit override path.

Invalidate cached assembled context when policy, files, tools, model settings,
authority, task selection, or relevant state changes. Include these dependencies
in the cache key where possible; a global manual invalidation convention is easy
to forget. Background extraction must not race with current writes; define lease,
version check, and conflict handling rather than assuming extraction always wins.

## Worker handoff

Send goal, accepted contract, necessary sources, authority, ownership, budget,
expected artifact, and escalation conditions. Return conclusions and evidence
references instead of a whole exploration transcript. Isolation has a cost:
missing assumptions and integration work; measure both.

Use [templates/context-budget.md](../templates/context-budget.md). Primary source:
[Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
for JIT retrieval and long-horizon techniques; its examples motivate design choices,
not a universal threshold or a guarantee for this skill.
