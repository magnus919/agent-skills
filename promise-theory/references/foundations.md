# Foundations — The Academic Core of Promise Theory

**Load this file when you need the definitions, the formal model, the history,
or an honest assessment of the theory's status.** This is the academic anchor
of the skill: the practical mappings in
[applications-infrastructure.md](applications-infrastructure.md) (CFEngine,
IaC, distributed systems) and
[agent-coordination.md](agent-coordination.md) (hybrid human + AI workforces)
are built on the vocabulary defined here. For one-line definitions see
[glossary.md](glossary.md); for applying the model to infrastructure practice
see [applications-infrastructure.md](applications-infrastructure.md).

**Provenance.** Every definition below is cited to a primary source: the
Burgess/Bergstra books and papers, the CFEngine documentation, and Burgess's
later arXiv work. Two markers are used consistently across every reference in
this skill:

- `[UNVERIFIED]` — a claim that could not be verified against a primary source
  (vendor-sourced figures, facts attested only in secondary accounts).
- `EXTRAPOLATION` — an interpretation that goes beyond the cited sources. The
  promise-theory → AI-agent synthesis is the main such zone and is labeled
  explicitly.

The theory is "semi-formal" — its own authors' term — and Section 4 states
precisely what is defined, what is proven, and what is only informally claimed.

---

## 1. The theory in one paragraph

Promise theory is a method of analysis for systems of interacting components
developed by the British physicist-turned-computer-scientist Mark Burgess
(creator of CFEngine, formerly professor at Oslo University College / Oslo
Metropolitan University) and, from roughly 2007, jointly with the Dutch
computer scientist Jan A. Bergstra (emeritus professor, University of
Amsterdam). It models every actor — human, machine, process, or organisation —
as an *autonomous agent* that can only make promises about its own behaviour,
and treats coordination as emerging from *voluntary cooperation* (an offer plus
an acceptance) rather than from obligations, commands, or centralised control.
The founding claim is that obligation — the assumption that one agent can
command another and be obeyed — is the wrong primitive for reasoning about
distributed systems: in Burgess's phrase, obligation-based accounts of remote
policy "amounted to wishful thinking" (Burgess, "Promise You A Rose Garden,"
2007, markburgess.org/rosegarden.pdf). The canonical statement of the theory is
Bergstra & Burgess, *Promise Theory: Principles and Applications* (2nd ed.,
χtAxis Press, 2019), which describes itself as a "semi-formal language for
modelling intent and its outcome."

## 2. Origin and history

### 2.1 From CFEngine to a theory (1993–2005)

Promise theory grew out of practical failure. CFEngine ("Configuration
Engine") began in 1993 as Burgess's personal tool for managing Unix
workstations at the University of Oslo (Burgess, "Cfengine: a site
configuration engine," *USENIX Computing Systems* 8(3):309–337, 1995). Its
core design idea was *convergence*: rather than executing imperative scripts
once, agents repeatedly enforce a desired state (a mathematical fixed point),
repairing drift on every pass. Burgess developed the theory of this approach in
"On the theory of system administration" (*Science of Computer Programming*
49(1–3):1–46, 2003) and framed configuration management through an "immunity
model" in "Configurable immunity for evolving human-computer systems"
(*Science of Computer Programming* 51(3):197–213, 2004).

The direct precursor of promise theory is Burgess's observation, which he
dates to around 2002 (per his Semantic Spacetime project page: "puzzles that
have bugged me since I started thinking about promises around 2002"), that
obligation- and command-based models of distributed policy were wrong for
autonomous, physically independent machines: an operator cannot *cause* a
remote host to comply; it can only create conditions under which the host's own
agents choose to comply. The popular essay "Promise You A Rose Garden" (2007)
called existing obligation-based theories "wishful thinking." This is the
theory's origin story — Burgess's own account, repeated in the FAQ and in the
2025 twentieth-anniversary retrospective.

### 2.2 DSOM 2005 — the founding paper

The first formal academic statement is:

> **M. Burgess, "An Approach to Understanding Policy Based on Autonomy and
> Voluntary Cooperation."** In: Schönwälder, J., Serrat, J. (eds), *Ambient
> Networks*, DSOM 2005, LNCS 3775, pp. 97–108, Springer, 2005.
> DOI 10.1007/11568285_9. Copyright © 2005 IFIP.

The paper proposes "a theory of atomic policy units called 'promises'" and
argues that "a global authority is not required to build conventional
management abstractions, but work is needed to bind peers into a traditional
authoritative structure." Many citations render the year as 2004 because the
paper was written in 2004; DBLP and Springer record the proceedings year as
2005. Burgess's own 2025 retrospective states that promise theory "was first
presented to an academic audience at the DSOM" workshop.

### 2.3 The Bergstra collaboration and mathematisation (2007–2014)

Bergstra — best known for process algebra (ACP, with J. W. Klop) and program
algebra — collaborated with Burgess from around 2007 and deepened the formal
apparatus:

- **Bergstra, Bethke & Burgess, "A process algebra based framework for promise
  theory," arXiv:0707.0744 (2007)** — promises as process-algebra terms,
  cooperation as synchronisation, conflict resolution handled algebraically,
  with a transportation-planning example.
- **Bergstra & Burgess, "A static theory of promises," arXiv:0810.3294
  (submitted 2008; revised through v5, January 2014)** — the canonical
  reference for the promise-vs-obligation distinction: "We compare promises to
  the more established notion of obligations and find promises to be both
  simpler and more effective at reducing uncertainty in behavioural outcomes."
- **Bergstra & Burgess, "Local and Global Trust Based on the Concept of
  Promises," arXiv:0912.4637 (2009)** — local trust as the expectation that a
  promise will be kept; global trust as a weighted eigenvector-centrality
  ("voting") function over the promise graph.
- **Bergstra & Burgess, "Promises, Impositions, and other Directionals,"
  arXiv:1401.3381 (2014)** — refines the taxonomy of promise-like constructs
  and their directionality.

### 2.4 The books

- **Bergstra & Burgess, *Promise Theory: Principles and Applications*, χtAxis
  Press, 1st ed. February 2014 (ISBN 9781495437779); 2nd ed. 2019 (ISBN
  9781696578554).** The formal reference text; all numbered Definitions (Defs
  1–23) cited below are from the 2nd edition. Free PDF at markburgess.org.
- **Mark Burgess, *In Search of Certainty: Ruling the Machines That Rule the
  World*, 2nd ed. O'Reilly, April 2015 (ISBN 9781491923337; first edition
  self-published 2012 — first-edition date not independently confirmed
  `[UNVERIFIED]`).** A broad science-of-infrastructure book in which promise
  theory is the "semantic measuring stick."
- **Mark Burgess, *Thinking in Promises: Designing Systems for Cooperation*,
  O'Reilly, June 2015 (ISBN 9781491917879).** The popular, non-technical
  introduction — the best starting point for a newcomer.

### 2.5 Recent and ongoing work (2024–2026)

- **Burgess & Dunbar, "Causal evidence for social group sizes from Wikipedia
  editing data," *Royal Society Open Science* 11:240514 (2024), DOI
  10.1098/rsos.240514** — the most prominent peer-reviewed empirical
  application; derives a scaling law from a "promise theory model of bipartite
  trust."
- **Burgess, "Cooperation in Human and Machine Agents: Promise Theory
  Considerations," arXiv:2604.10505 (2026)** — directly relevant to hybrid
  human–AI coordination: "Promise Theory represents the fundamentals of
  signalling, comprehension, trust, risk, and feedback between agents, and
  offers some lessons about success and failure."
- **Burgess, "Quantitative Promise Theory: Intentionality and Inference in
  Autonomous Agents," arXiv:2606.08552 (2026)** — incorporates Bayesian
  probability, information-theoretic optimisation, and Active Inference into
  promise semantics.
- **Burgess, "Legal Responsibilities Using Autonomous Agents For Artificial
  Intelligence," arXiv:2608.08022 (2026)** — applies the Downstream Principle
  to assign legal responsibility in AI-agent incidents.

---

## 3. The core model — definitions with citations

### 3.1 Agents and autonomy

The active entities in promise theory are *agents*: persons, animals, plants,
machines, or any other entity that exhibits behaviour whose observation leads
to the perception of behaviour and intentions in others. *Autonomy* is the a
priori assumption that agents cannot be coerced into making promises and that
"no agent may make promises on behalf of another" (Bergstra & Burgess,
*Promise Theory* 2nd ed., ch. 1). Each agent lives in its own private world
with incomplete information.

The five tenets of promise theory (book §1.3):

1. Agents are autonomous; they can only make promises about their own
   behaviour; no other agent can impose a promise upon them.
2. Making a promise involves passing information to an observer, but not
   necessarily an explicit linguistic message.
3. Assessment of whether a promise is kept may be made independently by any
   agent in its scope.
4. Interpretation of a promise's intent may be made independently by any agent
   in its scope.
5. The internal workings of agents are unknown; knowledge of them is assessed
   from the promises they make and keep, and the agent boundary may be drawn
   arbitrarily.

The autonomy assumption is explicitly **not** an ideological commitment to
decentralisation (the book warns against this misreading); it is a modelling
postulate chosen because it forces complete documentation of intended behaviour
and exposes failure modes. The promise-theory notion of autonomy is
causal/physical (agents are causally independent), not moral.

### 3.2 The promise (Def 1) and its notation

**Def 1 (Promise or µ-promise).** "A promise is an autonomous declaration of
intended, but as yet unverified, behaviour from one agent (the promiser) to
one or more others (called promisees). Each promise contains a body b that
explains what is being promised."

Notation (book eq. 3.1):

```
    b
As ──→ Ar          (promise from As to Ar with body b)
```

The shorthand `S ─b→ R` says the same thing: agent S promises to agent R a
body of behaviour b. The promise is "unverified" because one does not promise a
state of affairs already known; the promisee has yet to verify the outcome. A
promise may refer to past or future events.

The **body b** of a promise contains:

- a **name or label** Λ(b) uniquely identifying the promise;
- a **type** τ(b) describing the nature of the promise;
- an explicit **constraint** χ(b) on the affected state of the agent.

The body is often written as a pair b ~ (τ(b), χ(b)). Negation: for each body
b there is a body ¬b with ¬¬b = b, τ(¬b) = τ(b), and ¬χ(b) = χ(¬b) — negation
applies to the constraint, not the type. The full description of a promise is
the tuple def(π) = ⟨A, b, A′, σ⟩ (promiser, body, promisee, scope).

### 3.3 Promise proposals (Def 2)

**Def 2 (Promise proposals).** "The statement of a promise that is posited for
consideration by one or more parties, prior to keeping or discarding the
promise." A proposal is a complete description of a possible promise that is
not yet intended — the book analogises to treaty negotiation and un-signed
contracts. Burgess's *In Search of Certainty* summary: "A promise proposal is
not yet promised — like a testament/will that hasn't yet been signed." In a
hybrid workforce, a *draft* capability manifest or a contract template before
acceptance is a promise proposal (`EXTRAPOLATION`: the mapping of proposals to
agent-workforce artifacts is this skill's synthesis, not a claim in the cited
sources; developed in [agent-coordination.md](agent-coordination.md)).

### 3.4 Scope and knowledge (Defs 3–4)

**Def 3.** The description of a promise π is denoted def(π); def(def(π)) =
def(π) (idempotent). Knowledge of a promise may itself be the content of a
promise ("I promise that X told me about her promise…").

**Def 4 (Scope).** "We denote the scope of a promise by a set of agents σ,
with whom information def(π) is shared." Only agents in scope can form
expectations. A promise directed to "any agent" is written to A?; to all
agents, to ∗. Scope is why a promise is not a global broadcast: expectations
are local — an agent cannot form an expectation about a promise it has never
learned of.

### 3.5 Promisees, acceptors, consent, and ± polarity

The promisee (recipient) is not passive. Because agents are autonomous, a
promise "to give" only has effect if the promisee makes a complementary
promise "to accept." The book introduces **signed (polarised) promises**:

```
    +b
A1 ──→ A2     ("I will give b")
    −b
A1 ──→ A2     ("I will accept b")
```

Pairs of back-to-back promises of opposite polarity form a **binding** (a
handshake). This is the formal content of "voluntary cooperation": cooperation
requires both *offer* and *acceptance*, and *consent* is modelled as the
promisee's own counter-promise. The book notes the analogy between ± promise
polarity and positive/negative electric charge. **Lemma 1** establishes the
inequivalence of "promise to accept" and "imposition to give": accepting is
not the same as being obliged to offer. (In human contexts empathy can blur
this — the book's "I promise to receive you at my wedding" example — but in
formal terms the distinction is preserved.)

### 3.6 Impositions (Def 5)

**Def 5 (Imposition).** "A message intended to induce voluntary cooperation in
another agent" — an attempt to implant an intention in an external agent,
*without* a prior promise to accept. Degrees include hints, suggestions,
requests, requirements, specifications, commands, and demands.

Impositions are not promises (they cannot be kept by the one who makes them)
and are not obligations (no penalty semantics). An imposition only "works"
inside an existing network of promises that makes the target disposed to
accept. In notation, an imposition from A1 to A2 with body b is drawn with a
distinctive arrow (the book suggests "imagine a fist"). Every push-based
orchestration command — an Ansible task over SSH, a `kubectl` scale that the
scheduler enforces — is, in this vocabulary, an imposition (see
[applications-infrastructure.md](applications-infrastructure.md)).

### 3.7 Obligation — a derived, non-autonomous construct

*Obligation* (book §1.4, §3.7): "An imposition that implies a cost or penalty
for non-compliance." Obligations are imposed from outside and hence violate
(or at best suspend) autonomy: "Autonomous agents are, by definition, never
obliged to do anything they have not decided for themselves. To accept an
obligation, an autonomous agent must sacrifice some of its autonomy."

The theory's central polemical move: in philosophy and law a promise is
usually taken to generate an obligation; promise theory rejects this and treats
promise and obligation as *independent* concepts (Bergstra & Burgess, "A
static theory of promises," arXiv:0810.3294). Obligations can be *modelled* in
promise theory only as derived structures: an agent voluntarily promising to
accept another's directives — the basis of *authority* (Burgess, "Authority
(I): A Promise Theoretic Formalization," SSRN 3855352, 2021). This is also the
theory's account of why command-and-control is not contradicted by autonomy:
"Since a promise can always be withdrawn, there is no contradiction between
voluntary cooperation and command and control" (Wikipedia, citing the static
theory). So the derived chain is: **obligation = imposition + penalty**, kept
alive only by a standing voluntary promise to accept.

### 3.8 Self-promises

An agent may promise to itself — the book's µ-promise of the first kind is
precisely S → R with S = R for self-promises. Self-promises are the formal
representation of *goals, policies and desired states* that an agent undertakes
to maintain (e.g., CFEngine's desired configuration state). Because promiser
and promisee coincide, assessment and verification are internal but still
deferred ("unverified" until assessed). The modern capability-manifest pattern
for AI agents — an agent's self-commitment to its own operating rules — is a
self-promise (`EXTRAPOLATION`: the mapping to AI capability manifests is this
skill's synthesis; developed in [agent-coordination.md](agent-coordination.md)).

### 3.9 Bindings, promise chains, and valence

*Acceptance* is a counter-promise (the −b promise of §3.5). A *binding* is a
pair of promises of opposite polarity that mutually connect two agents
("back-to-back"). Bindings are the primitive of all cooperative structure: "A
promise binding defines a voluntary constraint on agents. The perceived
strength of that binding is an individual value judgement made by each
individual agent" (book, ch. 3). The concept of *valence* (Def 15) measures
how many bindings an agent can sustain — an analogy drawn from the
valency/oxidation-number concept in chemistry; an agent that promises more than
its valence allows is *overcommitting*.

A *promise chain* is a sequence of promises linking an upstream source to a
downstream recipient through intermediaries (each link typically itself a
binding). Chains are the unit of analysis for service delivery, supply chains,
and workflows; conditional promises allow redundant/alternative paths. The
book (fig. 13.14) illustrates a "+s1 → +s2 → +s3" chain with ownership resting
at the most downstream interior agent.

### 3.10 Trust as discounting

Trust in promise theory is defined relative to promises:

- *Local trust* (Bergstra & Burgess, "Local and Global Trust Based on the
  Concept of Promises," arXiv:0912.4637, 2009): "An agent is trustworthy if it
  is expected that it will keep a promise." Reputation is the propagation of
  such expectations from agent to agent. The 2009 paper argues trust is
  fundamentally *heuristic* — promise-based information is insufficient for
  rational judgement — and defines *global/community trust* as a weighted
  eigenvector-centrality (self-consistent voting) function on the promise
  graph.
- *Trust discounting* (book §3.12.5): a promise to keep a promise is believed
  less than a direct promise. If β(π(b)) is belief in direct promise π, then
  belief in π(n)(b) (an n-fold promise about a promise) satisfies
  β(π(n)(b)) = δ(n)β(π(b)), with discounting factor δ ≤ 1.

The FAQ adds: "Trust is a human judgement, informed by experience of
reliability, and how well agents keep their promises… Trustworthiness is an
assessment. It can also be promised about oneself or another agent." The book
also distinguishes this from the different technical meaning of "trust" in
computer security.

### 3.11 Assessment α, belief β, and evidence ε

**Def 21 (Assessment).** "A 'decision' by a single agent O about whether a
promise π has been kept or not," written αO(π); more fully
αA(π; t_i, t_f; I) — assessment by agent A of promise π over the time interval
[t_i, t_f] on the basis of a set of impressions I (measured data, hearsay,
etc.). The assessment function is itself a promise (to supply a
determination), so assessment is not a new kind of object in the theory.

**Def 22 (Belief).** β(π, t_i, t_f, I): a *prior* (Bayesian-flavoured)
assessment of the likelihood that π will be kept within the stated interval.

**Def 23 (Evidence).** ε(π, t_i, t_f, E): a *posterior* (frequentist /
evidential) assessment that π was kept, based on partial evidence E.

**Lemma 5 (Assessments are relativistic non-invariants):** assessments result
from contextual observation and are in general non-repeatable and
agent-specific; observations at different places/times have the status of
random variables. Outcomes are either T(X) (true), F(X) (false), or
indeterminate. This is why the theory insists every assessment record must
carry *who assessed, when, and against what observation* — an assessment
without provenance is an opinion, not evidence (see
[applications-infrastructure.md](applications-infrastructure.md) and
[trust-and-verification.md](trust-and-verification.md)).

### 3.12 Promise matrices and adjacency graphs

**Def 6 (Promise matrix).** For a collection of n agents {A_i}, the promise
matrix π_ij collects all promises between A_i and A_j with agent labels
implicit; the union/sum over all pairs denotes the complete set of promises.

**Def 7 (Promise adjacency matrix).** Π_ij = 1 iff A_i promises anything to
A_j (b_ij ≠ ∅), else 0. The matrix admits a rank decomposition
Π_ij = Σ_r Π_ij^(r) into matrices of promises of rank r.

Promise graphs are directed graphs whose edges are promises; since each edge
requires a counter-promise to be *effective*, "a link requires the mutual
consent of two autonomous agents," making promise graphs more primitive than
ordinary graph adjacency — and the foundation for Burgess's notion of *semantic
spacetime* (Burgess, "Spacetimes with Semantics (I)," arXiv:1411.5563, 2014).
Graph-inspection is where broken promises show up: two promises of the same
type with different constraints are a contradiction (Burgess, "Promise You A
Rose Garden," 2007).

### 3.13 Exact, inexact, and empty promises

- **Exact vs inexact (Def 8):** a promise is *exact* if its constraint χ(b)
  leaves no residual degrees of freedom, otherwise *inexact* (e.g., "q = 5"
  exact vs "1 < q < 5" inexact; a 100 Ω ±5% resistor is an inexact promise).
- **Empty/superfluous promise (Def 9):** a promise whose body contains no type
  or constraint ("I promise something or other"); it is trivially kept.
  Promises about inevitable outcomes are superfluous.

The empty promise is the formal limit of vacuous agreements — a contract whose
acceptance criteria are unstated satisfies nothing. This is why the skill's
manifest schema makes empty promises structurally impossible to declare
meaningfully (see [glossary.md](glossary.md) and `SKILL.md`'s Quick Start).

### 3.14 Deception

**Def 10 (Deception).** "A deception consists of two intentions: a documented
intention (i.e. a promise) and a non-documented intention, which are
incompatible." A lie is a promise made about something the agent knows it
cannot accomplish or does not intend to keep. Only the lying agent can
generally detect its own lie. The "I promise X if I can" dodge is an evasion
equivalent to an empty promise. Relatedly, *promise drift* (FAQ): intentions
drift as promises are forgotten, changed, or deprecated; if some agents change
while others do not, reliance fails.

### 3.15 Bundles, valence, and roles

**Bundles (Defs 12–14):** *promise bundles* aggregate promises between sets of
agents S, R ⊆ A (homogeneous and parameterised variants) — the origin of
CFEngine's bundle mechanism. **Valence (Defs 15–17):** the number of distinct
bindings an agent can sustain, with *net valence* of a graph and *utilization*
defined from the ± counts — the graph-theoretic quantity controlling saturation
and overcommitment. **Roles (Defs 18–20):** equivalence classes of agents —
roles *by association* (promisers making the same promise), *by appointment*
(promisees receiving the same promise), and *by cooperation* (coordinated
roles) — turning a promise graph into a compact organisational description.
Roles-by-association is exactly what a "role" in a multi-agent team manifests:
agents that promise the same capability.

### 3.16 Discovery

In a world of autonomous agents with no global registry, agents must find one
another. The book describes *discovery* as "a kind of Monte Carlo search":
agents become aware of one another's promises by random-walk encounters and
then bind to one another; communication is the act of binding to discovered
agents. The book also distinguishes *dispatch* (point-to-point delivery) from
*distribution/flooding* (broadcast to superagent binding sites) as
dissemination strategies. Modern service discovery (DNS, Consul, CoreDNS) is
the industrial form of this (see [applications-infrastructure.md](applications-infrastructure.md)).

### 3.17 The Downstream Principle

**Downstream principle** (book §13.6.3): in a chain of promises, dependencies
are *upstream* and benefactors are *downstream*; "the assurance of the final
promise outcome follows a 'downstream principal' [sic] that the most downstream
agent has both access and opportunity to correct or absorb faults, and hence
the greatest causal responsibility for an assessment of a promise not being
kept." The principle is explicitly a pragmatic observation about cause and
effect, "not a moral assessment," and it inverts conventional
hierarchy/Root-Cause-Analysis assumptions: influence propagates bidirectionally
through bindings while the final user retains ultimate causal responsibility
for securing the outcome. This principle is the load-bearing idea in Burgess's
2026 AI-legal-responsibility paper (arXiv:2608.08022) and in the skill's
"redundancy and downstream responsibility" pattern.

### 3.18 Evaluation and convergence loops

Keeping a promise is a process of *convergence*: agents continuously assess
(α, β, ε) and re-enforce promises, repairing drift toward the promised fixed
point. The book's conceptual graph is "Autonomy → Promise → Cooperation →
Assessment → …" — a feedback loop (fig. 1.2). Burgess's *In Search of Certainty*
summaries add that convergence goes beyond idempotence: a promise is kept when
the system ends in the correct state (a mathematical fixed point), and
"detailed balance" of opposing promises is how semantics are stabilised on top
of flawed dynamics. The 2019 "Locality, Statefulness, and Causality" paper
(arXiv:1909.09357) argues that feedback loops and recursion, which appear
acausal to external observers, make statefulness/statelessness an artifact of
observational scale. The practical expression of the loop — observe → assess →
act — is the mechanism behind CFEngine and Kubernetes (see
[applications-infrastructure.md](applications-infrastructure.md)).

---

## 4. Formal status — what is actually defined, proven, and claimed

The authors themselves describe the framework as a **semi-formal language**
(Bergstra & Burgess, *Promise Theory* 2nd ed., preface). Concretely:

**What exists:** a defined notation; numbered Definitions (1–23 in chs. 3 and
5, more later); Rules (e.g., Rule 1 "Separate events have separate types";
Rule 2 "Idempotence of promises"); Lemmas (Lemma 1: inequivalence of − promise
and + imposition; Lemma 5: assessments are non-invariants); Examples; and a
small algebra (idempotence, negation involution, def-idempotence, ± polarity,
δ-discounting).

**What does not exist:** there is **no complete axiomatisation** — no closed
set of axioms with rules of inference, no sound-and-complete equational theory
(the "algebra" is a list of properties, not a calculus with meta-theorems) —
and **no model-theoretic semantics** in the mainstream sense (no truth
conditions over structures, no completeness results). The process-algebra
paper (arXiv:0707.0744, 2007) is the closest thing to a mainstream-formal
statement and it is short (9 pp.) and example-driven. There is also no
standalone publication titled "promise algebra"; the algebra lives inside the
book and its process-algebra companion.

**What is rigorously proven:** essentially nothing beyond the algebraic
identities above, which follow directly from the definitions. The strongest
empirical validation is the 2024 Burgess–Dunbar *Royal Society Open Science*
paper, but its "proof" is a statistical fit to a scaling law, not a derivation
from axioms.

**What is informally claimed:** that promises "reduce uncertainty" better than
obligations; that promise theory subsumes game theory and information theory
("games can always be expressed in promise language, but not vice versa"; "an
information model can always be represented as promises, but not vice versa" —
FAQ; arXiv:2004.12661); that any system of interacting components can be
analysed this way (universality). Most importantly for honesty:

> **The ≤50% vs ≤100% claim is an informal heuristic.** The FAQ states that
> "the chance of an imposition being honoured within its expected time is at
> best 50/50, but that may increase up to 100% for promises." As stated it has
> **no derivation** and is **not a proven result**; it is an unfalsifiable-in-
> this-form heuristic about the relative reliability of voluntary promises over
> imposed commands. Use it as a mnemonic for why promises beat impositions, not
> as a quantitative law.

Treat the formalism as a **reasoning aid, not a proof system**: it gives you a
vocabulary and a consistency check (contradiction detection on promise graphs),
not soundness guarantees. This is the honest boundary of the theory — and it is
a deliberate design choice to remain a *language* rather than a model of
everything with a canonical semantics.

---

## 5. Adjacent frameworks — comparison with citations

### 5.1 Social commitments in multi-agent systems (the closest relative)

- **M. P. Singh, "An ontology for commitments in multiagent systems,"
  *Artificial Intelligence and Law* 7:97–113, 1999** — commitments as social,
  directed, normative relations with operations (create, discharge, cancel,
  delegate, assign, violate).
- **P. Yolum & M. P. Singh, "Commitment Machines," ATAL 2001 / *Intelligent
  Agents VIII*, LNCS 2333, pp. 235–247, 2002** — protocols as commitment
  machines compiled to finite-state machines with proven soundness/completeness.

**Comparison.** Both traditions treat coordination as emerging from directed,
publicly observable social relations rather than from individual mental states.
Differences: (i) the MAS tradition keeps *obligations and violations* as
first-class (a violated commitment triggers normative consequences), while
promise theory removes penalty semantics; (ii) the MAS tradition has rigorous
temporal-logic semantics and verification (model checking of commitment
protocols), which promise theory largely lacks; (iii) promise theory adds the
physical/autonomy grounding (agents are causally independent, promises are
always revocable); (iv) promise theory's *assessment* is intentionally
relativistic (each agent judges), whereas commitment logic is objective and
global. The literatures barely cite each other — cross-citation is almost nil
(report interpretation). *Relationship in one line:* a commitment "to which
one is committed" is a special case of a promise (book §3.12.1).

### 5.2 Deontic logic

- **G. H. von Wright, "Deontic logic," *Mind* 60(237):1–15, 1951**; standard
  deontic logic (O/P/F) and its paradoxes; dyadic / contrary-to-duty logic
  (**Prakken & Sergot, 1997**).

Promise theory is deliberately **antagonistic** to deontic logic. The DSOM 2005
paper cites Chellas's *Modal Logic* and Prakken & Sergot — Burgess knew the
literature. The critique is pragmatic: obligation logic assumes an external
norm that an autonomous agent will follow, which in distributed systems is
precisely what cannot be assumed; obligations "amount to wishful thinking."
Promise theory therefore replaces the normative primitive (obligation) with a
descriptive one (declaration of intent) and derives obligation-like behaviour
as voluntary acceptance. **Consequence:** promise theory deliberately forgoes
the expressiveness of normative reasoning — permissions, prohibitions,
contrary-to-duty obligations — which matters when modelling *regulation* rather
than *coordination*. For compliance-driven AI governance, you may need both
(see also the OPA/Kyverno discussion in
[applications-infrastructure.md](applications-infrastructure.md)).

### 5.3 Design by Contract

- **B. Meyer, "Applying 'Design by Contract'," *IEEE Computer* 25(10):40–51,
  1992** — preconditions, postconditions, and invariants attached to software
  modules, checked at runtime.

**Comparison.** The structural parallel is strong: a service's promises are its
postconditions/invariants; a use-promise is the caller's precondition;
assessment is runtime assertion checking; convergence to fixed points is
invariant maintenance. The philosophical upgrade: DbC obligations are
enforced by the compiler/runtime (the system is not autonomous), while promise
theory insists both sides are autonomous and must *choose* to participate —
the *client* also promises to use the service correctly, making DbC a special,
one-sided case of a symmetric promise contract (report interpretation;
grounded in book §3.12.1 and the FAQ's "invariants" language). For an agent
workforce: DbC is the right tool *inside* a single program or agent;
promise theory is the right tool *between* agents (human or machine) that
cannot assume obedience.

### 5.4 Control theory

- **M. Burgess, "A control theory perspective on configuration management and
  Cfengine," *ACM SIGBED Review* 3(2):12–16, 2006**; **Burgess & Couch,
  "Autonomic Computing Approximated by Fixed-Point Promises," MACE 2006,
  pp. 197–222**; the canonical autonomic-computing statement is **Kephart &
  Chess, "The Vision of Autonomic Computing," *IEEE Computer* 36(1):41–50,
  2003** (MAPE loop).

**Comparison.** Burgess explicitly connects CFEngine/promise theory to feedback
control: convergence to fixed points is tracking a reference signal; assessment
is error measurement; promises are reference/constraint signals. Promise theory
adds *semantic* (not just dynamic) stability — meaning and intent on top of
performance — and its control-theoretic reading is the most scientifically
conventional justification for its convergence claims. The skill's "evaluation
loop" pattern (observe → assess → act) is a MAPE loop in promise vocabulary.

### 5.5 (Brief) Policy-based management, game/information theory, sociology of trust

- **Policy-based management** is the theory's immediate intellectual context:
  Sloman & Moffett's policy hierarchies (1993), Lupu & Sloman's role-based
  frameworks (1996/1997), and Ponder (Damianou et al., 2000) modelled policy as
  obligations and authorisations imposed from above. The DSOM 2005 paper argues
  this fails for autonomous networks and proposes promises as "atomic policy
  units."
- **Game theory:** the "Voluntary Economic Cooperation in Policy Based
  Management" paper (2004, archived) introduced the economic reading — promises
  as strategies, cooperation as a repeated game, "detailed balance" as an
  equilibrium condition. The FAQ claims strategic-form games arise from
  collections of bi-directional ± promises and extensive-form games from
  conditional-promise graphs. This is a claimed (not proven) subsumption.
- **Information theory:** Burgess, "Information and Causality in Promise
  Theory," arXiv:2004.12661 (2020) — a Shannon channel as two promises (+b)
  and (−b); the claim that information models embed in promises but not vice
  versa. Again a claimed subsumption.
- **Sociology of trust:** promise theory aims to give trust a definable,
  computable substrate (arXiv:0912.4637; "Notes on Trust as a Causal Basis for
  Social Science," SSRN 4252501, 2022), formalising what Gambetta (1988) and
  the trust literature treat qualitatively. The 2024 Burgess–Dunbar paper is
  the first quantitative validation.

---

## 6. Critiques and limitations

1. **No axiomatisation, no model theory** (detailed in §4). The "algebra" is a
   list of properties; the process-algebra paper is an outline, not a calculus
   with meta-theorems.
2. **Vague primitive semantics.** The promise *body* b is deliberately
   underspecified — "up to each agent… to decide" — and the theory "does little
   to formalize the promise bodies it refers to" (FAQ, category-theory
   answer). This makes promise theory more a *metalanguage* than a domain
   model.
3. **Dependence on the originator and venue concentration.** Most formal
   statements appear in Burgess's and Bergstra's own books/preprints, in
   Bergstra's own journal (Transmathematica), or in self-published χtAxis
   volumes; the Wikipedia article flags over-reliance on sources "too closely
   associated with the subject" and possible "original research." Citation
   count in the mainstream multi-agent and formal-methods literatures is low.
4. **Testability is hampered by relativistic assessment.** Lemma 5 makes each
   agent's assessment agent-relative, which complicates inter-observer
   falsification; most claimed predictions are structural ("commands do not
   work without invitations"), not quantitative.
5. **The "not even wrong" challenge.** The FAQ devotes a section to this
   Popperian challenge. The honest assessment: promise theory has
   *explanatory* power (retrospective case studies: Boeing 737 MAX,
   arXiv:2001.01543; Brexit; money) but a thin, mostly qualitative *predictive*
   record; the one strong quantitative test is the 2024 Dunbar collaboration,
   which is real but narrow.
6. **The "model of everything" risk.** If any behaviour can be represented as
   a promise, promises risk carrying no information. The theory's defence —
   scope, exact/inexact constraints, assessment, valence — narrows this but
   does not close it; the burden of a canonical semantics remains open.

**Open problems** (from the research report's future-work list): a complete
axiomatisation and model theory; proven embeddings into CTL-style commitment
logics, deontic logic, or linear logic; quantitative calibration of β, ε, δ,
and valence from real telemetry (arXiv:2606.08552 begins this); agent-AI
applications (arXiv:2604.10505; arXiv:2608.08022); an empirical validation
programme beyond the Dunbar collaboration; and a schema/ontology for promise
bodies that would make promises machine-verifiable.

---

## 7. Sources (works cited above)

**Books.** Bergstra & Burgess, *Promise Theory: Principles and Applications*,
2nd ed., χtAxis Press, 2019 (Defs 1–23, tenets, rules, lemmas). Burgess, *In
Search of Certainty*, 2nd ed., O'Reilly, 2015. Burgess, *Thinking in Promises*,
O'Reilly, 2015. Bergstra & Burgess, *Money, Ownership and Agency*, χtAxis,
2019. Burgess, *A Treatise on Systems*, vols. 1–2, 2020.

**Papers.** Burgess, DSOM 2005, LNCS 3775, pp. 97–108. Bergstra, Bethke &
Burgess, arXiv:0707.0744 (2007). Bergstra & Burgess, arXiv:0810.3294 (2008,
rev. 2014). Bergstra & Burgess, arXiv:0912.4637 (2009). Bergstra & Burgess,
arXiv:1401.3381 (2014). Burgess & Dunbar, *Royal Society Open Science*
11:240514 (2024). Burgess, arXiv:2604.10505; arXiv:2606.08552; arXiv:2608.08022
(2026). Burgess, arXiv:1411.5563 (2014); arXiv:1909.09357 (2019); arXiv:
2004.12661 (2020). Burgess, SSRN 3855352 (2021); SSRN 4252501 (2022). Burgess,
"Promise You A Rose Garden" (2007); Promise Theory FAQ (markburgess.org/
promiseFAQ.html).

**Adjacent frameworks.** Singh (1999); Yolum & Singh (2002); von Wright (1951);
Prakken & Sergot (1997); Meyer (1992); Sloman & Moffett (1993); Damianou et al.
(2000); Kephart & Chess (2003); Gambetta (1988). Full bibliographic details are
in the mission research report (academic-foundations.md); the repository
standard is to cite the named work inline, as above.
