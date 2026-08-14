# semantic-spacetime — trigger probes

Harness-specific activation tests for the `semantic-spacetime` skill. These
probes evaluate whether a client should load the skill from its frontmatter
`description` alone (no `SKILL.md` body, no references). They live **only**
here, separate from `evals/evals.json`, which carries output-quality cases with
machine-parseable assertions.

This file also commits the two behavioral routing tables that VAL-ROUTE-009 /
015 / 016 are measured against: the Load By Need routing table (each of the
seven representative needs mapped to its expected reference) and the
anti-trigger refusal table (each of the five anti-triggers mapped to its
expected decision). Both carry a Results / observed-outcome column recording
the reference a fresh agent actually picked or the decision it actually
produced.

## How to run

Give a fresh agent (with no prior semantic-spacetime knowledge) **only** the
frontmatter `description` below plus the probe prompt, and ask it to decide
whether to load the skill and — for the routing probes — which reference it
would open. Record the decision; it must match the expected decision stated for
the probe. The expected decisions are grounded in the description's trigger
vocabulary and its negative boundary.

The skill `description` the probes are evaluated against (verbatim from
`SKILL.md` frontmatter):

> Model and diagnose shared semantic ground between agents with Semantic Spacetime (Mark Burgess, 2014-2025): a discrete graph model of meaning over time, where local proper time replaces global clocks, causality is cooperative promises, and gamma(3,4) graphs expose semantic drift, world model divergence, and absorbing states. Use for designing convergent self-healing coordination, modeling intent and trajectories over time, mapping promises onto spacetime, diagnosing semantic drift or dead-ends, and analyzing temporal blindness in agents. Do not use for physics or relativity, pure vector embeddings or RAG without temporal-causal structure, enforceable centralized control, simple single-agent prompting, or tool manuals — route those to the appropriate skill.

## Should-trigger probes

Prompts that must activate the skill. Each is an in-boundary task whose
vocabulary matches the description's triggers (shared semantic ground,
semantic drift / world model divergence, mapping promises onto spacetime,
temporal blindness).

### Probe ST-1 — shared semantic ground design (should trigger)

- **Prompt:** "Design shared semantic ground for a two-agent team that keeps misaligning on what 'done' means; produce a map of their interpretations."
- **Expected decision:** activate. The task asks to design shared semantic ground between agents, which the description names first ("Model and diagnose shared semantic ground between agents").

### Probe ST-2 — semantic drift / world model divergence (should trigger)

- **Prompt:** "Diagnose semantic drift between my agents' world models — they started aligned and diverged over time; find where they dead-end."
- **Expected decision:** activate. The description's trigger vocabulary covers "semantic drift", "world model divergence", and "diagnosing semantic drift or dead-ends".

### Probe ST-3 — mapping promises onto spacetime (should trigger)

- **Prompt:** "Map our promises and acceptances onto spacetime and trace how intent propagates between the agents over time."
- **Expected decision:** activate. "mapping promises onto spacetime" is a named trigger in the description.

### Probe ST-4 — temporal blindness analysis (should trigger)

- **Prompt:** "Analyze why my agent cannot tell what happened before what — it seems temporally blind and misorders events."
- **Expected decision:** activate. "analyzing temporal blindness in agents" is a named trigger in the description.

## Should-not-trigger probes (near-misses)

Prompts adjacent to the skill's territory that must **not** activate it. The
set collectively exercises the description's negative boundary: physics /
relativity, pure embeddings / RAG without temporal-causal structure,
enforceable centralized control, simple single-agent prompting, and tool
manuals.

### Probe SN-1 — physics near-miss (should not trigger)

- **Prompt:** "Derive the time dilation factor for a satellite in a Schwarzschild metric, including the gravitational redshift term."
- **Expected decision:** do not activate. This is spacetime physics, which the description explicitly excludes ("Do not use for physics or relativity"); it belongs to a physics domain.

### Probe SN-2 — static embeddings near-miss (should not trigger)

- **Prompt:** "Build semantic search over our static vector embeddings — there are no timestamps and no causal structure, just similarity scores."
- **Expected decision:** do not activate. A static embedding index is "pure vector embeddings or RAG without temporal-causal structure", an explicit anti-trigger; route to the embedding or semantic-search tool's own skill.

### Probe SN-3 — enforceable control near-miss (should not trigger)

- **Prompt:** "I fully control the fleet; just push the config to every server and verify compliance directly — no consent model needed."
- **Expected decision:** do not activate. Direct command-and-verify authority is "enforceable centralized control", an explicit anti-trigger; the control-vs-cooperation discussion, if wanted, routes to promise-theory.

### Probe SN-4 — single-agent prompting near-miss (should not trigger)

- **Prompt:** "Write me a single prompt for one LLM to summarize this meeting transcript."
- **Expected decision:** do not activate. This is "simple single-agent prompting" with no delegation or meaning space to model, an explicit anti-trigger.

### Probe SN-5 — tool-manual near-miss (should not trigger)

- **Prompt:** "Show me the kubectl commands and flags to deploy this chart, with examples."
- **Expected decision:** do not activate. The user needs a tool manual, which the description routes away ("tool manuals — route those to the appropriate skill"); the correct target is the kubernetes tooling skill.

## Boundary coverage checklist

| Anti-trigger boundary | Probes exercising it |
|-----------------------|----------------------|
| Physics / relativity | SN-1 |
| Pure vector embeddings / RAG without temporal-causal structure | SN-2 |
| Enforceable centralized control | SN-3 |
| Simple single-agent prompting | SN-4 |
| Tool manuals | SN-5 |

Counts: 4 should-trigger probes (≥3 required) and 5 should-not-trigger
near-misses (≥2 required), each with an explicit expected decision.

## Committed routing tables (VAL-ROUTE-009 / 015 / 016)

The tables below are the committed, mechanically checkable record that
VAL-ROUTE-009 (Load By Need row mapping), VAL-ROUTE-015 (behavioral routing of
seven needs), and VAL-ROUTE-016 (behavioral anti-trigger refusal) are measured
against. The Results columns record the observed outcome of a fresh-agent run
given the probe prompt and only the `SKILL.md` router (frontmatter description
plus the Load By Need / When not to use sections).

### Load By Need routing table

| Need (VAL-ROUTE-015 probe) | Expected reference | Results (observed) |
|---|---|---|
| "Re-derive the formal model: proper time, γ(3,4), semantic element — what does it all mean formally?" | `references/foundations.md` | Picked `foundations.md` — the formal-model row of Load By Need. Matches. |
| "Learn from CFEngine and the IaC/Kubernetes/GitOps lineage before designing a convergent system." | `references/applications-infrastructure.md` | Picked `applications-infrastructure.md` — the CFEngine/infrastructure row. Matches. |
| "Model this specific agent team in SST terms and design their coordination." | `references/agent-coordination.md` | Picked `agent-coordination.md` — the agent-team/coordination row. Matches. |
| "Apply the drift-detection pattern (or another named pattern) to my system." | `references/patterns.md` | Picked `patterns.md` — the named-patterns row. Matches. |
| "My agents keep disagreeing about what a word means — diagnose the drift." | `references/diagnosis-and-debugging.md` | Picked `diagnosis-and-debugging.md` — the drift/divergence/dead-end diagnosis row. Matches. |
| "I hit an unfamiliar term while modeling." | `references/glossary.md` | Picked `glossary.md` — the unfamiliar-term row. Matches. |
| "Find the primary sources — which paper says X?" | `references/bibliography.md` | Picked `bibliography.md` — the primary-sources row. Matches. |

Verdict: 7/7 needs routed to the expected reference; no row sends a need to a
semantically wrong file (VAL-ROUTE-009 and VAL-ROUTE-015 pass).

### Anti-trigger refusal table

| Anti-trigger (VAL-ROUTE-016 probe) | Expected decision | Results (observed) |
|---|---|---|
| General relativity / spacetime physics | Decline; no SST modeling — a physics domain owns this. | Declined, no reference loaded. Matches. |
| Pure vector embeddings / RAG / semantic search without temporal-causal structure | Decline; route to the embedding or semantic-search tool's own skill. | Declined and routed to the embedding/search tool skill. Matches. |
| Enforceable centralized control (direct command-and-verify) | Decline; SST machinery is overhead; route to promise-theory for the control-vs-cooperation discussion. | Declined; noted promise-theory as the routing target for the control discussion. Matches. |
| Simple single-agent prompting | Decline; no delegation or meaning space to model. | Declined, no reference loaded. Matches. |
| Tool manuals / framework documentation | Decline; route to the tool's own skill. | Declined and routed to the tool's own skill. Matches. |

Verdict: 5/5 anti-trigger probes produced a decline or the stated routing
destination, consistent with the `## When not to use` section (VAL-ROUTE-016
passes).
