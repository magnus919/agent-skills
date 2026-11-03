# Infinity research brief

Research question: what architectural choices in the Infinity runtime are reusable
in harness engineering, and what evidence supports them? Deep technical source
review, commissioned for catalog enrichment; checked 2026-11-03.

## Findings

**Open source — high confidence.** The supplied [video](https://youtu.be/os5eNeAVRpc),
“Amazon built a new AI agent runtime in Rust” (Let's Get Rusty, published
2026-11-02), links the AWS Infinity announcement in its public description.
[Infinity](https://github.com/hydro-project/infinity) is the Hydro project's
Rust runtime, RAP protocol, and Infinity Code application. The pinned
[license](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/LICENSE.txt) is Apache 2.0. These are separate layers, not three
names for one coding-agent UI. No code is vendored or installed by this enrichment.

**The transferable choice is the continuation boundary — high confidence in the
source design.** Treat durable conversation plus runtime metadata as resumable
state; dispatch slow work through a callback protocol and release the execution
slice. Serialize a conversation while scheduling different conversations
concurrently. This fits long waits and event-driven work; it does not require
converting every small synchronous harness to serverless.

**The implementation qualifies the headline — high confidence in static inspection,
no runtime reproduction.** Fast synchronous tools can loop through multiple
completions within a slice. The local router directly owns driver futures rather
than spawning an OS thread per conversation. Deferrable events may wait behind an
active tool; the deferral adapter changes semantics across deployments. History,
processed IDs, callback delivery, and tool effects are separate durability domains.
The code review does not establish an atomic end-to-end exactly-once protocol.

**Capacity is a narrow result — medium confidence in reported numbers.** The AWS
author reports an 80,000-agent benchmark with a simulated model and in-memory
stores on one AMD EPYC 9R14 thread. Its approximately 100 KB per idle agent supports
a projection of about 75,000 histories in 8 GB. The benchmark source samples RSS
after waves become idle. This does not establish a measured Raspberry Pi run,
75,000 simultaneous model calls, useful task throughput, or agent quality. We did
not reproduce the Linux-specific benchmark on this macOS research host.

**Research context exists; an Infinity paper was not located.** Targeted searches
and [Hydro's publication index](https://hydro.run/research/) found related work,
not a publication formally evaluating this runtime. Flo (POPL 2025) distinguishes
bounded from unbounded streams and studies progress/eager execution. The SIGMOD
2024 protocol-rewrite work studies when decoupling and partitioning preserve
semantics. These are useful lenses for reasoning about waiting and ordering;
they neither prove Infinity's correctness nor transfer guarantees to LLM decisions.
Laddad's 2025 dissertation supplies broader Hydro context. See source records for
reading depth and scope. The [follow-up findings](infinity-design-findings.md)
now extend that initial reading to selected paper sections and the runtime
extension, provider, client and workspace contracts.

## Evidence and limits

| Finding | Evidence | Qualification |
|---|---|---|
| Identity/license | Video metadata/description, repository LICENSE.txt | Captions returned empty; no audiovisual claims |
| Scheduling and persistence | Pinned core, local router, store and tool code | Static inspection; upstream tests inspected, not run |
| Protocol | Pinned RAP invocation, result, subscription and cancellation specs | Normative requirements are distinct from adapter behavior |
| Scale | Author's announcement and scripted benchmark source | Reported result; no independent repetition |
| Literature | Primary abstracts, publication index, dissertation abstract/contents | Related foundations; no Infinity-specific paper found in this search |

Most direct sources share project authorship: agreement is not independent
validation. The pin stabilizes source claims; release maturity, paper availability,
and operational behavior may change. Open questions include crash-window recovery,
callback authenticity, long-lived subscription cleanup, event-flood control,
scheduler fairness, and model decisions under interleaved events.

## Catalog changes and further candidates

| Owner | Enrichment | Boundary |
|---|---|---|
| harness-engineering | Continuation design, event ordering, commit/dispatch limits, compaction and recovery drills | Owns runtime design, not a new Infinity installation manual |
| agent-production-operations | Wake-up admission, revocation, pending effects and backlog accounting | Owns control decisions; platform/SRE own infrastructure |
| agent-evals-and-observability | Idle capacity versus active load, interleaving cases and causal event traces | Owns evidence; capacity is not semantic success |
| api-design-and-evolution | Candidate: acknowledgement versus eventual result, cancellation contracts | Existing tool/event guidance already covers much of this; no broad rewrite here |
| multi-agent-coordination | Candidate: spawn snapshots, stale reports and context inheritance | Runtime mechanics stay with harness-engineering |
| secure-software-engineering | Candidate: callback injection, confused deputy, callback-URL misuse | Requires a dedicated threat-model review before tool-specific prescriptions |
| capacity-and-cost-engineering | Candidate: resident/active/queued counts and total waiting cost | No independently reproduced cost data to justify new numerical rules |

## Durable inventory and closure

- [Source records](infinity-sources.md): identities, pinned source paths, extracted
  claims, disagreements, literature boundaries and provenance.
- [Research log](infinity-research-log.md): searches, retained/excluded sources,
  failed caption retrieval, coverage and unexecuted experiments.
- [Runtime procedure](event-driven-continuations.md): reusable design steps.
- [Decision template](../templates/event-runtime-decision.md): a reviewable design
  and failure drill record, without installing a runtime.
- [Rubric challenges](../evals/infinity-challenges.md): satisfying, contradictory
  and missing-evidence examples for new semantic assertions across three skills.

The [worked coding journey](event-runtime-worked-example.md) composes architecture
selection, durable configuration, CI waiting, restore, reconnect and integration.
See the research log for closure of the follow-up gaps.

Every retained source group is represented in the source records and log. Material
claims are connected to either pinned implementation, documented contract,
reported benchmark, or explicitly labeled design inference. No efficacy, live
cloud, independent benchmark, or audiovisual verification is claimed.
