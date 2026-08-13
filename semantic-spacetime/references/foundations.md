# Foundations — The Academic Core of Semantic Spacetime

**Load this file when you need the definitions, the formal model, proper time,
causality, the γ(3,4) formalism, the learning/knowledge formalism, or an honest
assessment of the theory's status.** This is the academic anchor of the skill.
What belongs here: the academic theory of Semantic Spacetime (SST) as developed
by Mark Burgess (2014-2025) — definitions, the formal model, γ(3,4), proper
time, causality, the promise-theory substrate, and adjacent fields. What does
not belong here: quantum-gravity or physics derivation (this is not a physics
theory — see §4), the CFEngine/infrastructure application history, and the
agent-coordination synthesis; those belong to the skill's application and
agent-coordination references, which are added in a later milestone. For
one-line definitions see [glossary.md](glossary.md); for sources see
[bibliography.md](bibliography.md).

**Provenance.** Every definition below is tagged with exactly one marker,
following the research corpus this skill was built from:

- `[VERIFIED]` — confirmed directly in a primary source fetched during the
  research phase (the arXiv papers, markburgess.org pages, and the fetched
  secondary sources listed in [bibliography.md](bibliography.md)).
- `[UNVERIFIED]` — secondary-source or inferred; confirmed only via metadata,
  search index, or an author's own secondary account.
- `EXTRAPOLATION` — original synthesis extending the theory to new domains;
  never presented as a verified fact.

The theory is semi-formal and deliberately unrefereed (§5). This file states
what is defined and verified, what is only informally claimed, and what is this
skill's own synthesis. Do not present unverified claims as fact and do not drop
markers when reusing this content.

---

## 1. Authorship and scope of the term

Semantic Spacetime is the coinage and project of **Mark Burgess** — the
physicist-turned-computer-scientist who created CFEngine — with the exact term
effectively his alone. A full-text search of arXiv for the exact phrase
"semantic spacetime" returns exactly 7 hits, all by Burgess; "semantic
space-time" returns zero hits [VERIFIED — arXiv full-text search performed
2026-08-12]. There is no independent academic school using the term. The
primary series is his arXiv papers 2014-2025:

- *Spacetimes with Semantics* (2014), arXiv:1411.5563 [VERIFIED]
- *Spacetimes with Semantics (II): Scaling of agency, semantics, and tenancy*
  (2015), arXiv:1505.01716 [VERIFIED]
- *Spacetimes with Semantics (III): The Structure of Functional Knowledge
  Representation and Artificial Reasoning* (2016, rev. 2017), arXiv:1608.02193 —
  the most formal document, canonical source for Definitions 1-9 and
  Lemmas 1-3 [VERIFIED]
- *Agent Semantics, Semantic Spacetime, and Graphical Reasoning* (2025),
  arXiv:2506.07756 — the current formal statement, introducing the γ(3,4)
  representation [VERIFIED]

Burgess states the intent directly: *"I have no interest or intention of
seeking to publish any of this work beyond making these notes available seeking
trusted review"* [VERIFIED — markburgess.org/blog_spacetime3.html]. SST is a
conceptual/modeling framework, deliberately not a quantum-gravity theory (§4).

## 2. The formal model

The formal skeleton comes from Part III (arXiv:1608.02193v4), which Burgess
calls "lengthy notes" laying foundations; and from the 2025 γ(3,4) paper.

### Semantic element (Definition 1)

> "A semantic element is a tuple ⟨Aᵢ, {π_scalar j, …}⟩ consisting of a single
> autonomous agent, and an optional number of scalar material promises."
> [VERIFIED — arXiv:1608.02193v4, Definition 1]

An agent "surrounded by a halo of promises that imbue it with semantics"
[VERIFIED — same source]. The promises are scalar/material (the agent's own
capabilities and properties) as distinct from the vector/adjacency promises of
Part II that connect elements into a spacetime [VERIFIED — arXiv:1505.01716].

### Semantic spacetime (Definition 2)

> "A collection of semantic elements, in any phase (gas or solid), for which a
> local change in state, promises or configuration represents a local unit of
> time." [VERIFIED — arXiv:1608.02193v4, Definition 2]

Companion one-liner from the project hub: *"A semantic spacetime is a discrete
graph, which evolves, and whose properties vary from point to point."*
[VERIFIED — markburgess.org/spacetime.html]. The definition makes time a
property of local change within the graph, not an external axis.

### Proper time and the absence of a global clock

Time in SST is *proper time*: *"Time in this sense is the Aristotelian concept
of proper time as countable changes, as observed by the agent concerned."*
[VERIFIED — arXiv:2506.07756 §1.3]. There is no global clock: *"The view of
time as a relative transition system goes back to the work of Leslie Lamport…
Lamport rediscovered the idea that time can at best be understood as a
precedence relation, in a discrete spacetime context."* [VERIFIED —
markburgess.org/semantic_spacetime.html]. Lamport, "Time, Clocks, and the
Ordering of Events in a Distributed System," *CACM* 21(7):558-565, 1978, is the
credited origin of this precedence view [VERIFIED — same page; bibliography].
Practically: two agents cannot share a wall-clock ordering of events; each
element's sequence of local changes is its own time.

### Causality as cooperative promises

Causality in SST is constituted by cooperative promises, not by imposed links.
Each adjacency requires both an offer (+) and an acceptance (−) promise between
the two ends: *"each node must both emit and absorb adjacency relations,
cooperatively… Thus space is made up of cooperating nodes and edges."*
[VERIFIED — markburgess.org/semantic_spacetime.html]. In the notation of the
papers, `S →(+π) R` means sender S offers promise π to receiver R, which
accepts with the complementary −π promise; influence passes only through the
overlap of offer and acceptance [VERIFIED — arXiv:1608.02193]. This is the
promise-theoretic spine that makes SST an agent model rather than a global
network model: every edge is a negotiated, observable relation.

### The γ(3,4) formalism

The 2025 paper (arXiv:2506.07756) refines the earlier four irreducible
associations (aggregation, causation, cooperation, similarity — [VERIFIED —
arXiv:1608.02193]) into a typed graph formalism called γ(3,4): **three node
meta-types × four link types** [VERIFIED — arXiv:2506.07756, Table 1].

The three node meta-types [VERIFIED — arXiv:2506.07756 §2.3]:

| Meta-type | Symbol | Nature |
|---|---|---|
| Events | e | Temporary/ephemeral; timelike (process) agents; persist or change via "leads to" |
| Things | t | Persistent, physical/realized agents; "behave like matter"; spacelike (snapshot) |
| Concepts | c | Invariant notions that cannot be created or destroyed; virtual space of "unrealized" potential; materialized only by attaching to physical agents |

The four link types, exactly [VERIFIED — arXiv:2506.07756, Table 1]:

| Value | Label | Direction | Semantics |
|---|---|---|---|
| 0 | NEAR | symmetric | equivalence, similarity, proximity, correlation |
| ±1 | LEADS TO | directed | temporal/causal order: enables, causes, precedes, depends on |
| ±2 | CONTAINS | directed | containment, membership, generalization, coarse-graining |
| ±3 | EXPRESSES | directed | attribute, name/value, property, distinguishing mark |

Burgess frames the four-link hypothesis itself as a hypothesis: *"This remains
a hypothesis for now, but it is not a particularly original one. Various
authors have suggested that spacetime concepts underpin natural language."*
[VERIFIED — arXiv:2506.07756 §2.2]. No additional link types exist in the
formalism; adding one would leave γ(3,4).

### The nine typing design rules

The node typing rules from arXiv:2506.07756 §2.3, exactly as verified
[VERIFIED — arXiv:2506.07756 §2.3]:

1. Things may be contained but not expressed.
2. Concepts may be expressed but not contained.
3. Concepts become realized by anchoring them to things or events.
4. Verbs are dangling concepts without a subject or object to instantiate them.
5. Verbs anchored to subjects/objects (things) are events.
6. A realized state of being is an event.
7. An unrealized state of being is a concept.
8. A realized type of thing is a thing.
9. An unrealized type of thing is a concept.

Note on the paper's abstract: it states that "The Semantic Spacetime postulates
bring predictability when reasoning," but the research phase could not verify an
enumerated postulate list in the fetched text (it would require a full read of
the paper's later sections). Treat the nine design rules above as the verified
typing content; do not present them as a numbered list of "the Semantic
Spacetime postulates" [UNVERIFIED — exact postulate set not verified].

### Location agents and signal agents

Two auxiliary agent types complete the model's ontology [VERIFIED —
arXiv:1608.02193v4]:

- **Location agents** (Definition 6): "irreducible sites that take up space and
  can emit and absorb signal agents. They may not overlap."
- **Signal agents** (Definition 7): "They may be created and destroyed,
  subsequently emitted and absorbed, by location agents. They can occupy the
  same space, since they end up and accumulate at end points."

## 3. Absorbing states and information leaks

Absorbing states are a central diagnostic concept in SST: *"The ubiquitous
appearance of absorbing states in any partial graph means that a graph process
leaks information."* [VERIFIED — arXiv:2506.07756 abstract]. They are
"non-conserving of information" [VERIFIED — same source]. Burgess ties the
phenomenon to division by zero: the leak is *"closely associated with the issue
of division by zero, which signals a loss of closure and the need for manual
injection of remedial information"* — and the boundary where the graph leaks is
*"boundary information where intentionality can enter"* [VERIFIED — arXiv:
2506.07756 §1.3]. Practically: a dead-end node (an event or thing with no
outgoing LEADS TO/EXPRESSES edges that matter) accumulates meaning and stops
propagating it; intent or policy must be injected manually at that boundary.
For a bounded diagnosis procedure using this concept, see the skill's
diagnosis-and-debugging reference (added in a later milestone).

## 4. The "not physics" boundary

SST is explicitly **not** a theory of physics: *"Semantic spacetime is a
discrete model of spacetime, but it is not intended as a theory of quantum
gravity, in spite of some affinity with quantum systems."* [VERIFIED —
markburgess.org/semantic_spacetime.html]. Three consequences worth stating
[VERIFIED — markburgess.org/semantic_spacetime.html]:

- No manifold structure is assumed: space is constituted by relationships
  between objects, not by a background geometry.
- There is no concept of variable velocity, nor momentum: "a discrete spacetime
  with finite number of states is not obviously a canonical system."
- The connection with canonical systems remains unknown.

When a task is physics (general relativity, quantum gravity, kinematics), SST
is the wrong tool; route away at the SKILL.md "When not to use" boundary.

## 5. Status: semi-formal and unrefereed

The core series is a set of self-published notes, deliberately not submitted
for refereed publication: *"I have no interest or intention of seeking to
publish any of this work beyond making these notes available seeking trusted
review"* [VERIFIED — markburgess.org/blog_spacetime3.html]. Burgess also warns
of the scope: *"I have improvised with an eye on practical applications. It is
probably too ambitious in scope and detail, but bridges may serve a purpose even
with gaps,"* and *"Although not a complete theory, it lays out guidance on the
formulation of the basic issues of information propagation, with some proofs
left to the reader."* [VERIFIED — arXiv:1608.02193 preamble; markburgess.org/
semantic_spacetime.html]. Use the formalism as a reasoning aid, not a proof
system. What is formal: the graph definitions (Definitions 1-9), the γ(3,4)
type system and its nine design rules, the learning/knowledge formalism with
its Nyquist bound and decay lemmas (§9), and the association-decomposition
algebra. What is semi-formal or metaphorical: the scaling/tenancy results of
Part II, and the physics parallels (Feynman/Schwinger readings, quantum-field
analogies, "logic emerges from reasoning") [VERIFIED — arXiv:1608.02193;
markburgess.org].

## 6. Promise theory as the substrate

SST is formally built from Promise Theory: *"The chosen language here is
Promise Theory (2004-2014)"* [VERIFIED — markburgess.org/spacetime.html] and
*"the idea of semantic spacetime is based on an idea called Promise Theory"*
[VERIFIED — markburgess.org/blog_spacetime3.html]. Promise Theory is the joint
work of Mark Burgess and Jan A. Bergstra; its canonical statement is *Promise
Theory: Principles and Applications* (χtAxis Press, 2014; 2nd ed. 2019), which
describes itself as a "semi-formal language for modelling intent and its
outcome" [VERIFIED — markburgess.org/promises.html].

The primitives SST inherits, stated here in one line each and developed in
depth by the promise-theory skill, are:

- **Promise** — an autonomous declaration of intended behavior, with a body
  (label Λ), a type (τ), and a constraint (χ); written `S →(+π) R` for an offer
  from promiser S to promisee R [VERIFIED — promise-theory foundations;
  arXiv:1608.02193].
- **Offer (+) and acceptance (−)** — every interaction requires both directions
  to be promised independently; this is the semantic spine of adjacency in SST
  (§2, Causality) [VERIFIED].
- **Autonomy and locality** — agents are autonomous and inert except for the
  promises they make; a strong form of locality, and the reason SST is an agent
  model rather than a global network model [VERIFIED].
- **Downstream Principle** — the most downstream party in a promise chain
  carries the greatest causal responsibility for the outcome [VERIFIED —
  promise-theory foundations].
- **Convergence** — repeated local assessment toward a desired state; the
  dynamic meaning of "convergent coordination" in SST [VERIFIED — promise-theory
  foundations].

Do not re-derive promise definitions here. When you need the promise vocabulary
(promises, acceptances, bindings, assessment, trust, the Downstream Principle),
load [promise-theory](../../promise-theory/SKILL.md) or its
[foundations reference](../../promise-theory/references/foundations.md). This
skill's territory is the space/time of meaning built on top of those promises:
γ(3,4), trajectories, drift, semantic distance, shared semantic ground.

## 7. Measurement: the spacelike/timelike duality

SST distinguishes two inequivalent ways to stabilize observation, which Burgess
maps onto the Feynman (path-integral) vs. Schwinger (source) readings of
quantum theory [VERIFIED — markburgess.org/semantic_spacetime.html;
markburgess.org/spacetime.html]:

1. **Spacelike / ensemble measurement** — *repeated trials with constant state
   and semantics, in which time plays no role*; objective/frequentist. You
   sample the same configuration many times and average.
2. **Timelike / "cognitive" measurement** — *continuously adapting accumulation
   of state, whose semantics define change in real time*; subjective/Bayesian.
   You update a running assessment as the system changes.

The two modes can disagree because they answer different questions, and the
practitioner consequence is the skill's core measurement rule: **semantics
requires measurement** — meaning cannot be asserted before the dynamics are
measured at the right scale. Different scales yield different conclusions; a
measurement that is stable at one scale can be wrong at another. This duality
is the theory-level ground for the "dynamics always trumps semantics" lesson of
the infrastructure lineage (covered in the application reference, added in a
later milestone) and for Gotcha 4 in SKILL.md.

## 8. Distance: metric vs semantic

Part III defines two kinds of distance [VERIFIED — arXiv:1608.02193v4]:

- **Metric (quantitative) distance** (Definition 8): *"a measure of
  coordinate-similarity in position."* Coordinates, embeddings, positions.
- **Semantic (qualitative) distance** (Definition 9): *"a measure of similarity
  in interpretation."* Worked examples in the paper: Hamming distance; hop
  counts in an associative network; semantic hashing; sparse distributed
  representations [VERIFIED — same source].

The distinction is operational: two concepts can be close in coordinates yet
far in interpretation, and vice versa. A weighted hop count over a γ(3,4) graph
is a semantic-distance instance of the hop-count family — the family this
skill's model tooling will implement for measuring drift between two snapshots
of a system's meaning.

## 9. Learning and knowledge

SST formalizes learning and knowledge as processes with explicit timescales
[VERIFIED — arXiv:1608.02193v4]:

- **Learning about a promise π** (Definition 3): "the sampling, equilibration,
  and summarization of observational assessments concerning a promise π made by
  another agent, repeated over a timescale T_learn > 2·T_sample." The observer
  applies a learning function E(α(π)_{t+1}) = L(α(π)_t, E(α(π)_t)); learning
  defines a clock ticking at rate T_sample.
- **Knowledge of π** (Definition 4): "a stable summary of the iterated
  assessment α(π)_{T_know}, of one or more promises π, formed by equilibration
  of the samples over a timescale T_know ≫ 2·T_sample." Crucially, "because
  knowledge defines a process with a timescale, the failure to confirm it
  relative to other changes leads to its decay."
- **Lemma 1 (knowledge decay):** uncertainty of knowledge grows geometrically
  with time since learning, with attenuation ℓ^r, ℓ < 1.
- **Lemma 2 (fidelity / learning rate):** "Learning can only represent source
  values faithfully if the rate of sampling is greater than twice that of the
  fastest rate of change in the data, i.e. 2/T_sample < ∂π/∂t" — the Nyquist
  bound.

Practitioner consequence: **staleness is a first-class quantity.** Memory and
retrieval designs must budget refresh; a knowledge summary that is never
re-confirmed decays geometrically no matter how accurate it was when formed.
This directly supports drift diagnosis: a stale shared interpretation is a
predictable source of semantic divergence.

## 10. The empirical arm: the Quantitative Spacetime Hypothesis

Two 2020 papers operationalize SST as a *testable hypothesis* rather than pure
formalism [VERIFIED — arXiv:2010.08126; arXiv:2010.08125]:

- **arXiv:2010.08126** — *Testing the Quantitative Spacetime Hypothesis using
  Artificial Narrative Comprehension (I): Bootstrapping Meaning from Episodic
  Narrative viewed as a Feature Landscape.* Parses narrative streams "without
  knowledge of semantics, using only measurable patterns (size and time)… as an
  event 'landscape'"; concepts are extracted "as process invariants." Results
  claim simple spacetime process cues, not higher reasoning, drive what is
  important about sensory experience [VERIFIED — arXiv:2010.08126].
- **arXiv:2010.08125** — *…(II): Establishing the Geometry of Invariant
  Concepts, Themes, and Namespaces.* Reconstructs concepts and themes via
  "multiscale interferometry" and a "chemistry of association and pattern
  reconstruction, based only on the four fundamental spacetime relationships,"
  drawing a bioinformatic analogy (n-grams, micro/meso/macro scales)
  [VERIFIED — arXiv:2010.08125].

Honest caveat: these are proof-of-concept experiments on narrative corpora with
single-CPU methods; the research phase found **no independent replication and no
benchmark against distributional baselines** [UNVERIFIED — no independent
replication found]. Treat the Quantitative Spacetime Hypothesis as an active,
incompletely validated empirical program — not established validation of SST.

## 11. Spacetime-Entangled Networks: consensus as entanglement

*Spacetime-Entangled Networks (I): Relativity and Observability of Stepwise
Consensus* is a four-author paper — Paul Borrill, Mark Burgess, Alan Karp,
Atsushi Kasuya (arXiv:1807.08549, 2018, rev. 2020) — that instantiates the
SST/promise line at the distributed-consensus layer [VERIFIED — arXiv:
1807.08549]: *"Entanglement describes co-dependent evolution of state. Networks
formed by entanglement of agents keep certain promises: they deliver sequential
messages, end-to-end, in order, and with atomic confirmation of delivery to
both ends of the link."* The "relativity of consensus" reading — observers at
different points in the network reach consensus stepwise, in their own local
order — is the SST no-global-clock doctrine applied to agreement
[VERIFIED — arXiv:1807.08549; the mapping onto the cooperative-promise
causality doctrine of §2 is this skill's synthesis and is labeled
EXTRAPOLATION]. Note this paper is not one of the seven "semantic spacetime"
phrase hits; it does not use the exact term [VERIFIED — arXiv search].

## 12. Motion of the Third Kind

SST distinguishes three ways to understand motion in a graph; the third,
"virtual motion" (Motion of the Third Kind), treats processes and properties —
for example cloud workloads and data records — as *promises moving from host to
host* [VERIFIED — markburgess.org/spacetime.html]. This is the basis of
Burgess's "cloud computing as virtual physics" framing: relocating a workload
is not matter moving through space, it is a promise being re-anchored. The
ResearchGate papers *Motion of the Third Kind I & II* (2021-22) exist but their
full texts were not fetched during research; details beyond the moving-promises
framing are [UNVERIFIED]. See [glossary.md](glossary.md) for the one-line entry.

## 13. Adjacent fields

SST sits next to — but is distinct from — these fields. Correct attribution and
a one-line framing for each [VERIFIED — citations verified in the research
phase; see bibliography]:

- **Cognitive maps** — Tolman, "Cognitive maps in rats and men" (1948). The
  brain demonstrably organizes knowledge spatially; SST is a candidate formal
  language for concept space-times, not a neuroscience claim.
- **Conceptual spaces** — Gärdenfors, *Conceptual Spaces: The Geometry of
  Thought* (MIT Press, 2000). Concepts as convex regions in metric spaces with
  quality dimensions; Gärdenfors-style spaces have **no time dimension** — SST
  adds process and temporality.
- **Distributional / vector-space semantics** — Harris (1954), LSA (Landauer &
  Dumais 1997), word2vec-style embeddings (Mikolov et al. 2013). The dominant
  statistical competitor; SST explicitly contrasts itself ("graphs preserve the
  intentionality of the source even under data fractionation" vs. vectorized
  probabilistic estimation [VERIFIED — arXiv:2506.07756; arXiv:2512.19084]).
- **Event calculus** — Kowalski & Sergot (1986). Logic-based reasoning about
  events where "the notion of event is taken to be more primitive than that of
  time"; SST instead claims spacetime structure generates the semantics.
- **Situation calculus** — McCarthy & Hayes (1969). Logic-based reasoning about
  actions and change; the same logic-first framing distinguishes it from SST.
- **Causal sets** — Myrheim (1978), Sorkin (2003), Surya (2019). The discrete-
  spacetime program Burgess flags as the closest physics analogue: "in this
  regard, a semantic spacetime is akin to causal sets" [VERIFIED — arXiv:
  2506.07756 §2]. Difference: SST's nodes are autonomous agents with semantics,
  not passive points, and SST assumes no manifold structure or symmetries.
- **Logical clocks / virtual time** — Lamport (1978), Mattern (1988/89). The
  distributed-systems backbone for "no global clock"; SST generalizes logical
  clocks into full semantic spacetimes [VERIFIED].

## 14. Applying this reference

When you have modeled a system with this vocabulary, materialize it in the
skill's model format — see [templates/sst-model.yaml.tmpl](../templates/sst-model.yaml.tmpl)
(the versioned `sst-model-v1` contract: agents, nodes, edges, acceptances,
trajectories, observations) — and write the analysis in
[templates/sst-analysis.md.tmpl](../templates/sst-analysis.md.tmpl). For
unfamiliar terms while reading, load [glossary.md](glossary.md). For the
promise-theory substrate vocabulary, load
[promise-theory](../../promise-theory/SKILL.md) — do not re-derive promises
here. For measurement and verification practice (turning assessed meaning into
evals and traces), the
[agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md)
skill is the assessment-layer partner.

## Sources

Primary sources and adjacent works are listed with URLs in
[bibliography.md](bibliography.md). The key items cited in this file: Burgess,
*Spacetimes with Semantics* I-III (arXiv:1411.5563, 1505.01716, 1608.02193);
Burgess, *Agent Semantics, Semantic Spacetime, and Graphical Reasoning*
(arXiv:2506.07756); Burgess, *Testing the Quantitative Spacetime Hypothesis*
I-II (arXiv:2010.08126, 2010.08125); Borrill, Burgess, Karp & Kasuya,
*Spacetime-Entangled Networks (I)* (arXiv:1807.08549); Lamport, *Time, Clocks,
and the Ordering of Events in a Distributed System* (CACM 1978); Burgess's
project pages (markburgess.org/spacetime.html, /semantic_spacetime.html,
/blog_spacetime3.html); Bergstra & Burgess, *Promise Theory: Principles and
Applications* (2014/2019).
