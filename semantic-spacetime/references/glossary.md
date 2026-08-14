# Glossary — Semantic Spacetime Vocabulary

**Load this file when you hit an unfamiliar term while applying this skill** —
a word in the routing table, a reference, a model, or a diagnosis you cannot
place. Each entry is a heading-led definition consistent with
[foundations.md](foundations.md); where a term belongs to promise theory, the
entry links there and keeps its own definition short. Sources are tagged as in
[foundations.md](foundations.md): `[VERIFIED]` (confirmed in a primary source),
`[UNVERIFIED]` (secondary or inferred), `EXTRAPOLATION` (this skill's
synthesis).

---

## Core semantic spacetime terms

### Semantic element
**Semantic element** — "a tuple ⟨Aᵢ, {π_scalar j, …}⟩ consisting of a single
autonomous agent, and an optional number of scalar material promises"
[VERIFIED — arXiv:1608.02193v4 Def 1]. The atomic unit of a semantic spacetime:
an agent "surrounded by a halo of promises that imbue it with semantics."
See [foundations.md](foundations.md) §2.

### Semantic spacetime
**Semantic spacetime (SST)** — "a collection of semantic elements, in any phase
(gas or solid), for which a local change in state, promises or configuration
represents a local unit of time" [VERIFIED — arXiv:1608.02193v4 Def 2]. Mark
Burgess's discrete graph model of meaning over time; the term is effectively his
alone (exactly 7 arXiv hits, all by him) [VERIFIED]. See
[foundations.md](foundations.md) §2.

### Proper time
**Proper time** — time as countable local changes observed by the agent
concerned: "the Aristotelian concept of proper time as countable changes, as
observed by the agent concerned" [VERIFIED — arXiv:2506.07756 §1.3]. Each
semantic element has its own proper time; there is no global clock. See
[foundations.md](foundations.md) §2.

### Cooperative promise causality
**Cooperative promise causality** — the SST account of causation: every
adjacency requires both an offer (+) and an acceptance (−) promise between the
two ends, so "space is made up of cooperating nodes and edges"
[VERIFIED — markburgess.org/semantic_spacetime.html]. Causality is negotiated,
local, and observable; it is never imposed. See
[foundations.md](foundations.md) §2.

### γ(3,4)
**γ(3,4)** — the 2025 typed-graph formalism of Semantic Spacetime (Burgess,
arXiv:2506.07756): exactly three node meta-types — events (e), things (t),
concepts (c) — crossed with exactly four link types — 0 NEAR, ±1 LEADS TO,
±2 CONTAINS, ±3 EXPRESSES [VERIFIED]. Pronounced "gamma three four"; the model
format in this skill encodes it as nodes with a `type` and edges with a `link`
value in {-3..3}. See [foundations.md](foundations.md) §2.

### NEAR
**NEAR** — γ(3,4) link value 0; symmetric; equivalence, similarity, proximity,
correlation. The "semantic symmetrization" link [VERIFIED — arXiv:2506.07756
Table 1]. See [foundations.md](foundations.md) §2.

### LEADS TO
**LEADS TO** — γ(3,4) link value ±1; directed; temporal/causal order — enables,
causes, precedes, depends on. The "follows" gradient link [VERIFIED — arXiv:
2506.07756 Table 1]. See [foundations.md](foundations.md) §2.

### CONTAINS
**CONTAINS** — γ(3,4) link value ±2; directed; containment, membership,
generalization, coarse-graining. The aggregate/membership link [VERIFIED —
arXiv:2506.07756 Table 1]. See [foundations.md](foundations.md) §2.

### EXPRESSES
**EXPRESSES** — γ(3,4) link value ±3; directed; attribute, name/value,
property, distinguishing mark. The distinguishability link [VERIFIED — arXiv:
2506.07756 Table 1]. See [foundations.md](foundations.md) §2.

### Event
**Event** — γ(3,4) node meta-type e: temporary/ephemeral, timelike (process)
agents that persist or change via "leads to" [VERIFIED — arXiv:2506.07756
§2.3]. A realized state of being is an event; verbs anchored to things are
events. See [foundations.md](foundations.md) §2.

### Thing
**Thing** — γ(3,4) node meta-type t: persistent, physical/realized agents that
"behave like matter"; spacelike snapshot [VERIFIED — arXiv:2506.07756 §2.3].
Things may be contained but not expressed. See [foundations.md](foundations.md)
§2.

### Concept
**Concept** — γ(3,4) node meta-type c: invariant notions that cannot be created
or destroyed; the virtual space of "unrealized" potential, materialized only by
anchoring to things or events [VERIFIED — arXiv:2506.07756 §2.3]. Concepts may
be expressed but not contained. See [foundations.md](foundations.md) §2.

### Absorbing state
**Absorbing state** — a state in a partial graph where information stops
flowing; "absorbing states are non-conserving of information" and "a graph
process leaks information" at them [VERIFIED — arXiv:2506.07756]. Burgess ties
the leak to division by zero: "loss of closure and the need for manual
injection of remedial information"; the leaking boundary is "boundary
information where intentionality can enter" [VERIFIED]. In diagnosis, a
dead-end node that accumulates meaning without propagating it. See
[foundations.md](foundations.md) §3.

### Metric distance
**Metric (quantitative) distance** — "a measure of coordinate-similarity in
position" [VERIFIED — arXiv:1608.02193v4 Def 8]. Coordinates, embeddings,
positions. Contrast with semantic distance. See [foundations.md](foundations.md)
§8.

### Semantic distance
**Semantic (qualitative) distance** — "a measure of similarity in
interpretation" [VERIFIED — arXiv:1608.02193v4 Def 9]; worked examples include
Hamming distance, hop counts in an associative network, semantic hashing, and
sparse distributed representations. Two concepts can be close in coordinates
yet far in interpretation. See [foundations.md](foundations.md) §8.

### Semantic drift
**Semantic drift** — this skill's term for the divergence of shared semantic
ground over time: two agents (or an agent and its instructions) start with the
same meaning for a term and their interpretations move apart as their local
proper times advance. The diagnosis treats drift as an observable — measure the
semantic distance between the interpretations at successive observations.
**EXTRAPOLATION** — the drift concept is the skill's application of SST's
trajectory and semantic-distance machinery; the term itself is standard in the
agent-drift literature the research corpus reviewed, while the SST framing is
synthesis.

### Trajectory
**Trajectory** — the path an agent or a concept takes through semantic
spacetime: the sequence of node states a semantic element occupies as its
proper time advances, recorded as observations. Reasoning is "constrained
spacetime trajectories" through the association network [VERIFIED — arXiv:
1608.02193 §1, §5]. In the model format, a trajectory is a declared `path` of
node ids.

### Shared semantic ground
**Shared semantic ground** — the overlap of interpretation between two or more
agents: the set of terms and promises that both sides mean the same way,
measurable as low semantic distance between their concepts. SST models it as a
region of the semantic spacetime where NEAR/EXPRESSES edges agree across
agents. **EXTRAPOLATION** — synthesis term for this skill, grounded in the
cooperative-promise account of adjacency and the definition of semantic
distance.

### Temporal blindness
**Temporal blindness** — an agent's failure to track event ordering, state
change, or causality — effectively lacking a proper-time record of its own
semantic element. SST's local-time account (no global clock) makes such
blindness structural unless observations are recorded; the fix is a recorded
observation log per element. The research corpus documents the LLM literature
on this ("LLMs are temporally blind," arXiv:2510.23853) [VERIFIED — citation in
the research corpus; the SST framing is EXTRAPOLATION].

### Spacelike measurement
**Spacelike (ensemble) measurement** — repeated trials with constant state and
semantics, in which time plays no role; objective/frequentist [VERIFIED —
markburgess.org/semantic_spacetime.html]. See [foundations.md](foundations.md)
§7.

### Timelike measurement
**Timelike ("cognitive") measurement** — continuously adapting accumulation of
state whose semantics define change in real time; subjective/Bayesian
[VERIFIED — markburgess.org/semantic_spacetime.html]. See
[foundations.md](foundations.md) §7.

### Learning
**Learning (about a promise π)** — "the sampling, equilibration, and
summarization of observational assessments concerning a promise π made by
another agent, repeated over a timescale T_learn > 2·T_sample" [VERIFIED —
arXiv:1608.02193v4 Def 3]. Learning defines a clock ticking at rate T_sample.
See [foundations.md](foundations.md) §9.

### Knowledge
**Knowledge (of a promise π)** — "a stable summary of the iterated assessment
α(π)_{T_know}, of one or more promises π, formed by equilibration of the samples
over a timescale T_know ≫ 2·T_sample"; it decays geometrically without refresh
(attenuation ℓ^r, ℓ < 1) [VERIFIED — arXiv:1608.02193v4 Def 4, Lemma 1].
Staleness is a first-class quantity. See [foundations.md](foundations.md) §9.

### Location agent
**Location agent** — "irreducible sites that take up space and can emit and
absorb signal agents. They may not overlap" [VERIFIED — arXiv:1608.02193v4
Def 6]. See [foundations.md](foundations.md) §2.

### Signal agent
**Signal agent** — agents that "may be created and destroyed, subsequently
emitted and absorbed, by location agents. They can occupy the same space, since
they end up and accumulate at end points" [VERIFIED — arXiv:1608.02193v4
Def 7]. See [foundations.md](foundations.md) §2.

### Super-agent
**Super-agent** — the coarse-grained agent formed by scaling agency up via the
Part II rules: replacing a group of individual agents with one "super-agent"
(sub-space), scaling agency both dynamically and semantically [VERIFIED — arXiv:
1505.01716]. The renormalization analogue; see
[foundations.md](foundations.md) §1 for the series map.

### Motion of the Third Kind
**Motion of the Third Kind** — "virtual motion": processes and properties (e.g.,
cloud workloads, data records) treated as promises moving from host to host,
the basis of Burgess's "cloud computing as virtual physics" framing [VERIFIED —
markburgess.org/spacetime.html]. The ResearchGate papers of that name (2021-22)
exist; their details are [UNVERIFIED]. See [foundations.md](foundations.md) §12.

## Promise-theory-owned terms (deferred)

### Promise
**Promise** — an autonomous declaration of intended, as yet unverified,
behavior made by one agent to another; the primitive every SST adjacency builds
on (offer polarity +π). Full definition, notation, and body/type/constraint
machinery live in [promise-theory](../../promise-theory/SKILL.md) — load it
there rather than re-deriving it. See [foundations.md](foundations.md) §6.

### Acceptance
**Acceptance** — the complementary counter-promise (−π) that turns an offer
into a binding: influence passes only through the overlap of offer and
acceptance. SST's cooperative-promise causality is built from it. Full
treatment: [promise-theory](../../promise-theory/SKILL.md). See
[foundations.md](foundations.md) §2 and §6.

### Convergence
**Convergence** — repeated local assessment toward a desired state (a fixed
point), the dynamic meaning of "convergent coordination" in SST; statistical,
never exact. Full treatment (including the distinction from idempotence):
[promise-theory](../../promise-theory/SKILL.md) and its applications reference.
See [foundations.md](foundations.md) §6.

### Downstream Principle
**Downstream Principle** — the most downstream party in a promise chain carries
the greatest causal responsibility for the outcome. Promise-theory-owned;
[promise-theory](../../promise-theory/SKILL.md) has the full statement. See
[foundations.md](foundations.md) §6.
