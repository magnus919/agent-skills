# Diagnosis and Debugging — A Bounded Procedure for Semantic Drift, Divergence, Dead-Ends, and Meaning Gaps

**Load this file when you are diagnosing a semantic failure in an agent or system** — two agents disagree about what a word means, an agent's behavior drifts from its instructions, a task dead-ends and nothing the agent tries helps, or a term that used to mean something now means nothing to anyone. This file gives a bounded, checkable procedure that terminates: after three non-converging diagnostic passes you stop and report the evidence.

**What belongs here:** the diagnosis procedure — inputs, the four named conditions (drift, divergence, dead-end/absorbing state, meaning gap), the stepwise diagnosis, the three-pass bounded exit, and the exit artifacts. What does **not** belong here: the definitions and formal model behind the vocabulary (see [foundations.md](foundations.md)); the drift literature and metrics in depth (see [agent-coordination.md](agent-coordination.md) §5); the named patterns the procedure applies (see [patterns.md](patterns.md)); the empirical infrastructure record (see [applications-infrastructure.md](applications-infrastructure.md)). Promise-level assessment (whether a promise is kept, breach, trust calibration) is linked to [promise-theory](../../promise-theory/SKILL.md) — this file covers the *semantic* side, not the promise-accounting side.

**Provenance.** `[VERIFIED]` = confirmed in a fetched primary source; `[UNVERIFIED]` = secondary/inferred; `EXTRAPOLATION` = this skill's synthesis, labeled. The procedure's structure (steps, four conditions, three-pass exit) is this skill's original synthesis, grounded in the verified definitions it cites.

---

## 1. When to use this procedure (and when not to)

Use this procedure when the symptom is **semantic**: the outputs, decisions, or coordinated behavior diverge from a stated meaning, and you can point at a concept, promise, instruction, or shared term as the thing that "meant" something. The four target conditions:

1. **Semantic drift** — a meaning changes over time away from its promised/recorded meaning (the agent or system quietly re-interprets). Empirically: "progressive degradation of agent behavior, decision quality, and inter-agent coherence over extended interaction sequences" with semantic drift as "deviation from original intent" [VERIFIED — arXiv:2601.04170].
2. **Divergence** — two or more agents (or an agent and its instruction) end up with *different* meanings for the same term or state; the gap grows with time. Empirically: "the divergence of internal knowledge states between concurrent agents" [VERIFIED — arXiv:2606.21666].
3. **Dead-end (absorbing state)** — a node or process stops propagating information; the same failure recurs and interior changes do not help. Formally: "the ubiquitous appearance of absorbing states in any partial graph means that certain graph processes leak information and represent entropy changing processes"; an absorbing state "can only be replaced with new boundary data from outside the graph" [VERIFIED — arXiv:2506.07756].
4. **Meaning gap** — a term or promise has no working interpretation at all in the current system: the co-language between the agents that must use it has no overlap on that term ("agents should expect to misunderstand one another's intentions to some level" [VERIFIED — arXiv:2604.10505]).

Do **not** use this procedure when the failure is purely mechanical (a crashed service, a malformed message, a wrong API call with no meaning dimension) — route to the tool's own skill. Do **not** use it when the question is whether a promise was *kept* (assessment, breach, trust calibration) — that is [promise-theory's diagnosis-and-debugging reference](../../promise-theory/references/diagnosis-and-debugging.md), which this file links to rather than restates.

## 2. Inputs — what to collect before starting

Gather these before pass 1; every step consumes them:

- **The instruction / promised state** — the text or artifact that stated the intended meaning (the "instruction trajectory" of [agent-coordination.md](agent-coordination.md) §8.5). If it is not versioned, version it now as an observation.
- **Observed implementations** — agent outputs, decisions, tool calls, or system states at known times; at least two points in time to make drift/divergence measurable (drift is a time-indexed quantity).
- **Reality observations** — measurements of the external world state the meanings are supposed to track (SLO-style measurements; see [applications-infrastructure.md](applications-infrastructure.md) §7).
- **The shared vocabulary in play** — the terms, promises, or concepts that are in dispute, with any prior anchor definitions ([patterns.md](patterns.md) Pattern 1).
- **The causal/time structure** — event ordering where it matters ("there is only a partial order in which an event e1 precedes an event e2 iff e1 can causally affect e2" [VERIFIED — Lamport 1978]); reconstruct causality, not timestamps, first.

If the inputs are unavailable (no recorded instruction, no observations, no shared terms), the diagnosis cannot converge — that finding itself goes into the evidence report (§6) as a meaning gap.

## 3. The four conditions — diagnosis checks

For each candidate condition, run its check. A condition is *confirmed* only when the check's evidence is present; otherwise record it as ruled out.

| Condition | Diagnosis check | Ruled out when |
|---|---|---|
| **Drift** | Compute the divergence between the promised/recorded meaning and the observed implementation at two or more times (semantic distance; [patterns.md](patterns.md) Patterns 5 and 9). Is the pairwise distance growing, or consistently nonzero in one direction? | Distances are stable and near zero at every pair of times |
| **Divergence** | Compare the same term or state across two agents (or agent vs. instruction) at the same time. Is the inter-agent semantic distance above your risk threshold? Is the gap widening? | All agents agree within threshold at all sampled times |
| **Dead-end (absorbing state)** | Trace the graph from the failing node. Do information flows stop at it? Does it re-absorb every intervention (same outcome, more input)? Is the node's interior data being erased (no learning)? | Interventions produce new, different outcomes; information passes through |
| **Meaning gap** | For the disputed term, does any agent have a working interpretation (a defined anchor, or an observed consistent use)? Does the exchange co-language contain the term at all? | At least one agent demonstrates a stable, observable interpretation of the term |

Each check consumes the inputs of §2 and produces a verdict plus the evidence that supports it. Do not skip the measurement step in any check: "it is not possible to reason about semantics without taking into account the underlying dynamics" [VERIFIED — InfoQ, *In Search of Certainty*].

## 4. The procedure — bounded, stepped

**EXTRAPOLATION** — this five-step procedure is this skill's synthesis: it applies the verified SST machinery (γ(3,4) typing, semantic distance, absorbing states, promise overlap) as a debugging discipline. Run the steps in order; each step either locates the failure or rules out a whole class.

**Pass structure.** One *pass* = running steps 1–4 in order. You may run up to **three passes**; a pass that does not converge must change something (a new observation, a new hypothesis, a re-typed edge) rather than repeat the same loop. After three non-converging passes, stop and write the evidence report (§5). This bounded exit mirrors the skill's Exit Conditions and prevents the re-litigation trap.

### Step 1 — Reconstruct the semantic spacetime

Build (or update) the γ(3,4) model of the failing system from the inputs: nodes typed as events (timelike process agents), things (persistent, realized), or concepts (virtual, unrealized); edges typed 0 = NEAR, ±1 = LEADS TO, ±2 = CONTAINS, ±3 = EXPRESSES [VERIFIED — arXiv:2506.07756; formal definition in [foundations.md](foundations.md) §2]. Record promises and acceptances as edges with their overlap `b∩` [VERIFIED — arXiv:2604.10505]. If the model cannot be built (no node type fits, edges cannot be typed), record that as evidence of a meaning gap and continue.

### Step 2 — Locate the divergence

Compute pairwise semantic distances between the instruction trajectory, the implementation trajectory, and the reality observations ([agent-coordination.md](agent-coordination.md) §8.5). Answer: which pair diverges, and along which dimension (spatial/temporal/task for the context-divergence framing [VERIFIED — arXiv:2606.21666]; semantic/coordination/behavioral for the agent-drift framing [VERIFIED — arXiv:2601.04170])? Identify the earliest observation at which the divergence exceeded threshold — that is the candidate *onset*.

### Step 3 — Classify the condition

Run the §3 checks for the four conditions against the divergence locus. The most common misreads to guard against: drift and divergence both show distance, but drift is time-local (one trajectory vs. its promise) while divergence is inter-agent (two trajectories vs. each other); a dead-end is not drift — it is structural, and only boundary data helps ("can only be replaced with new boundary data from outside the graph" [VERIFIED — arXiv:2506.07756]); a meaning gap is not divergence — it is the absence of a working interpretation, not two different ones.

### Step 4 — Check the promise plumbing (link, don't restate)

If the failure touches whether a promise was kept, whether acceptance was recorded, or how trust was calibrated, route that part of the diagnosis to [promise-theory's diagnosis-and-debugging reference](../../promise-theory/references/diagnosis-and-debugging.md) and run its assessment steps there. This procedure covers the semantic side only; do not re-derive promise-accounting here. Record which promises/acceptances the semantic failure involves (their overlap `b∩` [VERIFIED — arXiv:2604.10505]) as evidence, then return to Step 5.

### Step 5 — Hypothesize the fix and verify it in the model

For the classified condition, propose the SST-typed intervention and test it in the model before applying it to the system:

- **Drift** → re-anchor the drifting term (Pattern 1) and re-apply the convergence loop (Pattern 3): re-affirm the promised meaning, re-record it as versioned data [EXTRAPOLATION — grounded in the fixed-point convergence of arXiv:2604.10505 and the versioned-coordinate machinery of arXiv:2204.00470].
- **Divergence** → reconcile (Pattern 10): expose both projections, expand the co-language, re-anchor shared terms, re-measure [EXTRAPOLATION — grounded in the offer/acceptance overlap and three-languages framing of arXiv:2604.10505].
- **Dead-end** → inject boundary data: a new promise, a human input, outside policy — then verify the absorbing state re-opens [VERIFIED — arXiv:2506.07756].
- **Meaning gap** → define and anchor the missing term in the exchange co-language, or refuse to proceed on it until both sides accept a definition [EXTRAPOLATION — grounded in the co-language/non-unitary-translation framing of arXiv:2604.10505].

Verify the fix by re-running Step 2 on the model with the fix applied: the divergence metric must move toward zero (or stay within the risk threshold). If it does not, the fix was wrong — this is a non-converging pass; change the hypothesis and go again (up to three passes).

## 5. The bounded exit — after three non-converging passes

If after **three passes** the divergence metric is still above threshold, the absorbing state still absorbs, or the meaning gap persists, **stop diagnosing and report**. Do not iterate a fourth time, do not re-litigate the same model, do not silently widen the scope. The purpose of the bound is to convert an unbounded hunt into an evidence artifact — the diagnosis is itself a finding.

## 6. Exit artifacts — what the evidence report must contain

Write the report with at least these sections (this is the report contract of [templates/sst-analysis.md.tmpl](../templates/sst-analysis.md.tmpl)):

1. **System description** — the model built in Step 1 (or the reason it could not be built).
2. **Semantic spacetime map** — the γ(3,4) graph with node types, link types, and the divergence locus marked.
3. **Findings** — for each of the four conditions: confirmed or ruled out, with the check evidence; the onset observation for drift/divergence; the leaking boundary for dead-ends; the unanchored term for meaning gaps.
4. **Interventions** — the fixes tried in Steps 5, with their modeled outcomes (converged / non-converging per pass).
5. **Verification/measurement plan** — the specific re-measurement (what to observe, at what scale, how often) that would confirm the fix in the real system, per the "dynamics always trumps semantics" measurement rule [VERIFIED — InfoQ, *In Search of Certainty*].
6. **Pass ledger** — what changed between pass 1, 2, and 3, so a future diagnoser can see the evidence trail and pick up where this one stopped.

A completed report is a legitimate termination: the exit condition is an observable artifact (the report exists and states findings + bounded escalation), not an admission of failure.

## Routing

For the metrics and literature behind Steps 2–3: [agent-coordination.md](agent-coordination.md) §5. For the patterns the interventions apply: [patterns.md](patterns.md). For the formal model and γ(3,4) definitions: [foundations.md](foundations.md). For the empirical infrastructure record behind the measurement rule: [applications-infrastructure.md](applications-infrastructure.md). For promise-accounting diagnosis (assessment, breach, trust): [promise-theory](../../promise-theory/SKILL.md) and its [diagnosis-and-debugging reference](../../promise-theory/references/diagnosis-and-debugging.md).
