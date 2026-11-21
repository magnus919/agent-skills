# Harness for multimodal RAG

Start with the [harness contract](../../harness-engineering/templates/harness-contract.md).
The runtime owns identity, resource limits, state transitions, and acceptance.
The model can interpret intent, propose a bounded plan, and synthesize a reply.
Use a fixed chain for stable paths, such as straightforward text Q&A. Use a
stateful workflow such as LangGraph when branching, fan-out, approval, or
resumption needs explicit control. The workflow graph manages execution; the
knowledge graph stores retrievable entities and relationships.

## Contracts at the boundaries

| Boundary | Required contract |
|---|---|
| Request intake | Server-authenticated user and tenant, question, requested evidence scope, time cutoff, allowed media types, budget, and optional thread reference |
| Router | Typed branch choices, allowed arguments, max hops, max cost, time limits, policy context supplied by runtime |
| Retriever adapters | Validated per-modality arguments and typed results with immutable evidence references, locator, version, policy reference, coverage, and source time where applicable |
| Evidence admission | Trusted service scopes candidates, reauthorizes hydration, validates versions/units/locators, deduplicates, and assembles only the minimum approved payloads |
| Answer | Claims with evidence IDs, observed versus forecast labels, citation references, coverage, and status such as answered, partial, unavailable, or insufficient evidence |
| Memory proposal | Typed action, tenant, destination, expected revision, source lineage, and scope. A separate worker validates, stages, and publishes |

Expose purpose-specific text, graph, media, and metric adapters. Keep secrets
and policy out of model-writable state. Validate requested branches and their
arguments server-side. Give each branch a deadline and enforce an overall
budget. Keep per-branch evidence and failure outcomes when reducing parallel
results. Fuse text ranks only where meaningful. Join measured series with
dated documents by entity and time. Preserve each evidence kind through
serialization and generation. On failure allow a scoped fallback where it can
still establish a claim. Block claims that require the missing evidence.

## LangGraph-shaped workflow

```text
authenticate and validate -> plan within scope
  -> bounded text / graph / visual / time-series branches
  -> authorize, normalize and assemble evidence
  -> generate structured claims
  -> validate references, evidence coverage and output policy
  -> respond, show partial coverage, or abstain

separate source event or explicit proposal
  -> validate write authority -> stage and project
  -> check source versions, policy and lineage -> publish or quarantine
```

Use LangChain retriever or tool interfaces as adapters where their contracts fit.
Use LangGraph typed state and explicit conditional edges for routing, branch
reducers keyed by immutable evidence IDs to merge results, and checkpoints only
where resume needs them. Version state, adapters, policy decisions and routing.
Persist scoped references and statuses where possible, with tenant-bound thread
ownership. Keep checkpoints distinct from the source of truth and long-term
memory. On resume, derive identity again, invalidate stale evidence, and
recheck before hydration, model calls and release. Use idempotency keys and
atomic version checks for retried side effects and decide whether a branch can
use a fresh snapshot when its old version is unavailable.

Complete the workflow only when citations resolve to currently authorized
evidence and the claim types agree with their inputs. Check numeric claims
against structured values. Check meaning and completeness with rubric or
qualified review as appropriate. Trace branch choice, source IDs and
versions, cache and checkpoint hits, status, timings, and spend with minimized
payload logging. Test timeout, malformed output, revocation during pause,
tenant/thread mismatch, duplicate worker commits, and the loss of a modality.
Measure task success and recovery compared with a fixed pipeline.
