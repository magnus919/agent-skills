# Glossary — Promise-Theory Vocabulary for Hybrid Human + Agent Workforces

**Load this file when you hit an unfamiliar term while applying this skill** — a word in the routing table, a reference, a manifest, a contract template, or a diagnosis you cannot place. Each entry is a heading-led definition with its canonical source; where a term names an agent-coordination practice, the entry points to the reference that develops it. The formal definitions behind every entry are in [foundations.md](foundations.md); the practical mappings are in [agent-coordination.md](agent-coordination.md), [patterns.md](patterns.md), and [trust-and-verification.md](trust-and-verification.md).

**Provenance.** Definitions are cited to the primary sources (Bergstra & Burgess, *Promise Theory: Principles and Applications*, 2nd ed., 2019; Burgess, "Cooperation in Human and Machine Agents," arXiv:2604.10505, 2026; Burgess & Dunbar 2025; Leoveanu-Condrei, arXiv:2508.03665, 2025). The agent-coordination readings — capability manifest, acceptance handshake, P_succ, kinetic mistrust — are this skill's synthesis and are labeled `EXTRAPOLATION`. Claims that could not be verified against a primary source are marked `[UNVERIFIED]`.

---

## Core actors

### Agent
**Agent** — any bounded, causally independent entity with its own state, resources, and behaviour that can make promises about its own future behaviour: a human, an LLM agent, an API, a microservice, a cell, an organization (Bergstra & Burgess 2019, ch. 1; Burgess, arXiv:2604.10505). In this skill's manifest schema, humans are never declared as agents: they appear as acceptors/evaluators via `expectations` entries with `from: human` (see [agent-coordination.md](agent-coordination.md) §3.1).

### Autonomy
**Autonomy** — the a priori modelling assumption that agents cannot be coerced into making promises, and that no agent may make promises on another's behalf ("no agent may make promises on behalf of another" — Bergstra & Burgess 2019, ch. 1). It is a causal/physical property (agents are causally independent), not a moral claim, and it is a modelling postulate chosen to force complete documentation of intended behaviour — not an ideology (book §1.3).

### Promise
**Promise** — "an autonomous declaration of intended, but as yet unverified, behaviour" from a promiser to one or more promisees (Def 1). The body b carries a label Λ, a type τ, and a constraint χ; notation `S ─b→ R` means agent S promises body b to agent R. The promise is "unverified" because the promisee has yet to verify the outcome. Full definitions and notation are in [foundations.md](foundations.md) §3.2.

### Promisee/promiser
**Promisee/promiser** — the promiser is the agent making the promise; the promisee is the receiver to whom it is directed (Def 1). The promisee is not passive: a promise "to give" only takes effect when the promisee makes a complementary promise "to accept" — see Acceptor and Consent. The pair is the two endpoints of every promise edge in the graph.

### Acceptor
**Acceptor** — the agent that receives an offer and voluntarily makes the complementary acceptance promise (−b) that turns the offer into a binding (book §3.5). Only the overlap of offer and acceptance transmits influence. In a hybrid workforce, humans are the highest-value acceptors: they decide which agent offers to rely on, and can refuse (see [agent-coordination.md](agent-coordination.md) §3.1).

### Consent
**Consent** — in promise theory there is no separate act of consent: consent is modeled as the acceptor's own counter-promise to accept, which is what gives an offer its effect (book §3.5). An offer without a matching acceptance is an imposition, not a cooperation.

## The promise machinery

### Imposition
**Imposition** — "a message intended to induce voluntary cooperation in another agent" (Def 5): hints, suggestions, requests, requirements, commands, demands. It is made *without* a prior promise to accept, and it only "works" inside an existing network of promises that disposes the target to accept. Every push-based orchestration command — an Ansible task over SSH, a `kubectl` scale enforced by a scheduler — is an imposition in this vocabulary (see [applications-infrastructure.md](applications-infrastructure.md)).

### Obligation
**Obligation** — a derived, non-autonomous construct: an imposition that implies a cost or penalty for non-compliance (book §1.4, §3.7). "Autonomous agents are, by definition, never obliged to do anything they have not decided for themselves." Obligations can be modeled only through a standing voluntary promise to accept another's directives — the basis of authority (Burgess, "Authority (I): A Promise Theoretic Formalization," SSRN 3855352, 2021). Promise and obligation are independent concepts (Bergstra & Burgess, arXiv:0810.3294).

### Bindings
**Bindings** — a pair of back-to-back promises of opposite polarity that mutually connect two agents; the primitive of cooperative structure (book ch. 3). "A promise binding defines a voluntary constraint on agents. The perceived strength of that binding is an individual value judgement made by each individual agent." In a manifest, bindings are the cross-agent `accepts` pairs.

### Polarity
**Polarity** — the sign of a promise: +b is a promise to give, −b is a promise to accept (book §3.5). Cooperation requires both signs: influence passes only through the overlap of an offer (+b) and an acceptance (−b). The book draws the analogy to positive and negative electric charge.

### Valence
**Valence** — the number of distinct bindings an agent can sustain (Def 15), an analogy from chemistry; net valence and utilization of a promise graph are defined from its ± counts (Defs 15–17). An agent that promises more than its valence allows is *overcommitting* — a structural fragility visible in the graph before any execution fails.

### Intent
**Intent** — "a subject or type of possible behaviour … something that can be interpreted to have significance" (book §1.4). Intentions exist before and independently of communication, and their selection is deliberately left unexplained. Because the interior of an agent is unobservable (tenet 5), intent is accessible only through the expressed promise and the assessed outcome. **EXTRAPOLATION** — for LLM agents, whose "intentions" are not stable objects, this tenet is methodologically convenient: judge the promise and the outcome, not the claimed interior.

### Expectation
**Expectation** — the consequence of a promise within its scope: a promise "drives expectations" only among agents who know about it (Def 4). Expectation is scoped knowledge plus belief; an agent cannot form an expectation about a promise it has never learned of, and a promise directed outside its scope creates nothing.

## Knowledge and evaluation

### Belief
**Belief** — β(π, t_i, t_f, I): a prior, Bayesian-flavoured assessment of the likelihood that a promise π will be kept within the stated interval, based on a set of impressions I (Def 22). Belief in a promise about a promise is discounted — see Trust (as discounting).

### Evidence
**Evidence** — ε(π, t_i, t_f, E): a posterior, frequentist/evidential assessment that π was kept, based on partial evidence E (Def 23). An assessment without provenance — who assessed, when, against what observation — is an opinion, not evidence.

### Assessment
**Assessment** — αO(π): a decision by a single agent O about whether a promise π has been kept (Def 21), written more fully αA(π; t_i, t_f; I). Assessment is relativistic (Lemma 5: agent-specific, context-dependent, non-repeatable), is itself a promise, and is the mechanism by which trust accumulates. "A promise that nobody assesses" is operationally meaningless (see [trust-and-verification.md](trust-and-verification.md)).

## Trust, breach, and coordination

### Trust (as discounting)
**Trust (as discounting)** — the trust-as-discounting model of nested promises: belief in a promise about a promise is discounted relative to belief in a direct promise, β(π(n)(b)) = δ(n)β(π(b)) with discounting factor δ ≤ 1 (book §3.12.5). Local trust is the expectation that a promise will be kept; global/community trust is a weighted eigenvector-centrality function on the promise graph (Bergstra & Burgess, "Local and Global Trust Based on the Concept of Promises," arXiv:0912.4637, 2009). Burgess's later refinement splits trust into two components — potential trustworthiness and kinetic mistrust (arXiv:2604.10505; Burgess & Dunbar 2025).

### Deception
**Deception** — "A deception consists of two intentions: a documented intention (i.e. a promise) and a non-documented intention, which are incompatible" (Def 10). A lie is a promise made about something the agent knows it cannot accomplish or does not intend to keep; only the lying agent can generally detect its own lie. The "I promise X if I can" dodge is an evasion equivalent to an empty promise.

### Discovery
**Discovery** — how agents in a world with no global registry find one another's promises: "a kind of Monte Carlo search" — random-walk encounters followed by binding (book §3.16). Communication is the act of binding to discovered agents. Modern service discovery (DNS, Consul, CoreDNS) is the industrial form (see [applications-infrastructure.md](applications-infrastructure.md)).

### Downstream Principle
**Downstream Principle** — in a chain of promises, dependencies are upstream and benefactors downstream; the most downstream agent has both access and opportunity to correct or absorb faults, and hence carries the greatest causal responsibility for the outcome (book §13.6.3; Burgess, arXiv:2604.10505, Def. 1). It is a pragmatic observation about cause and effect, "not a moral assessment": the receiver of a promise holds the ultimate power of decision over the outcome, and designs its own redundancy and escape hatches.

### Evaluation loop
**Evaluation loop** — the feedback cycle by which promises are kept: observe → assess → act, converging on the promised state (book fig. 1.2, §3.18). Agents continuously assess (α, β, ε) and re-enforce promises, repairing drift toward the promised fixed point. The practical expression is the CFEngine and Kubernetes reconciliation loop (see [applications-infrastructure.md](applications-infrastructure.md) and [patterns.md](patterns.md) pattern 4).

### Breach
**Breach** — an unkept promise, detected by assessment; an expected event, not an anomaly (Burgess, arXiv:2604.10505 §VI-F). Breach is an information event that triggers renegotiation or redundancy — never blame ("an autonomous agent cannot impose blame"; blaming an upstream provider "is a useless imposition and a waste of trust/energy"). In a diagnosis, a breach is classified against the failure taxonomy in [diagnosis-and-debugging.md](diagnosis-and-debugging.md).

### Renegotiation
**Renegotiation** — updating the promise set after a breach or a change of context: revise the contract, change acceptance criteria, add verification, replace the provider, or down-rank the trust estimate (see [patterns.md](patterns.md) pattern 5). Escalation is bounded and named: escalate only when renegotiation fails to converge.

## Agent-coordination practice

### Capability manifest
**Capability manifest** — a versioned declaration of an agent's capabilities, constraints, expectations, and withdrawal semantics; the agent-coordination practice corresponding to the promise offer. Concrete forms: an MCP tool descriptor or function schema, a repository `AGENTS.md`, a system prompt with explicit constraints, an SLO. **EXTRAPOLATION** — the manifest-as-promise-offer mapping is this skill's synthesis (see [agent-coordination.md](agent-coordination.md) row 1 and [patterns.md](patterns.md) pattern 1).

### Acceptance handshake
**Acceptance handshake** — the recorded accept/refuse decision on every delegation: the two-way handshake / approval gate that operationalizes the acceptance promise (−b). Refusal is a coordination signal, not a failure; silence is treated as refusal-by-default, because an unaccepted delegation is an imposition that looks accepted. **EXTRAPOLATION** — the handshake pattern is this skill's synthesis (see [patterns.md](patterns.md) pattern 2).

### P_succ
**P_succ** — the empirically estimated probability that an agent satisfies a given contract, estimated over repeated assessed runs (Leoveanu-Condrei, "A DbC Inspired Neurosymbolic Layer for Trustworthy Agent Design," arXiv:2508.03665, 2025). The operational face of potential trust: it is what makes two agents that satisfy the same contract interchangeable except for their P_succ and cost (see [trust-and-verification.md](trust-and-verification.md) §3).

### Kinetic mistrust
**Kinetic mistrust** — the rate at which a receiver checks on a promiser: how often you run evals, ping health checks, re-audit outputs, or re-review work; the attention/energy component of two-component trust (Burgess, arXiv:2604.10505; Burgess & Dunbar 2025). It is spent attention and must be budgeted explicitly — "mistrust is the prerequisite for learning," and "if you trust something too much, you're not paying attention."

## Related terms

The following vocabulary appears across the references and templates; these are supplementary, not part of the core twenty-seven.

- **Promise proposal** — a promise posited for consideration prior to keeping or discarding (Def 2); a draft capability manifest before acceptance.
- **Scope** — the set of agents σ with whom a promise's description is shared (Def 4); only agents in scope can form expectations.
- **Exact / empty promise** — *exact*: the constraint leaves no residual degrees of freedom (Def 8); *empty/superfluous*: the body has no type or constraint and is trivially kept (Def 9).
- **Promise matrix / adjacency graph** — the collection of all promises between agent pairs (Def 6) and its 0/1 adjacency form (Def 7); graph inspection is where broken promises show up.
- **Role** — an equivalence class of agents: by association (same promise), by appointment (same promisee), or by cooperation (Defs 18–20).
- **Self-promise** — a promise an agent makes to itself: the formal representation of goals, policies, and desired states.
- **Promise chain** — a sequence of promises linking an upstream source to a downstream recipient through intermediaries; each link is typically a binding.
- **Conditional promise** — a promise contingent on a received signal; delegations through middlemen are conditionals, and are unreliable (Burgess, arXiv:2604.10505).
- **Promise ledger** — an append-only, versioned record of promises, acceptances, assessments, breaches, and renegotiations. **EXTRAPOLATION** (see [trust-and-verification.md](trust-and-verification.md) §8).
- **Agent contract** — a formal governance artifact: the tuple C=(I,O,S,R,T,Φ,Ψ) with lifecycle DRAFTED → ACTIVE → {FULFILLED, VIOLATED, EXPIRED, TERMINATED} (Ye & Tan, arXiv:2601.08815, 2026).
- **Eval** — a formalized acceptance criterion: a stated rule by which a receiver decides a promise is kept; offline (benchmarks, golden sets) or online (production scoring).
- **Dunbar trust budget** — the cognitive limit on meaningful social relationships, modeled as an attention/trust-energy budget (Burgess & Dunbar 2025); the machine equivalent is unknown.
- **Three-languages problem** — sender language, receiver language, and co-language; no authority calibrates two agents' internal languages to be the same, so shared meaning is negotiated, never guaranteed (Burgess, arXiv:2604.10505).
- **Authority** — calibrated subordination: followers voluntarily promise to follow a leader, and the leader is a trusted calibration point (SSRN 3855352, 2021).
- **Swarm vs. team** — an emergent, homogeneous flock vs. a role-differentiated, contract-bearing collaboration; production agent systems mostly need team semantics (Burgess, arXiv:2604.10505 §VI-E).

## Notation summary

The formal notation used across the references: `S ─b→ R` (promise of body b from S to R); `+b` (promise to give) and `−b` (promise to accept); a binding is `+b` paired with `−b` between the same two agents; def(π) is the description of a promise; scope σ is the set of agents that know it; assessment αO(π), belief β(π), and evidence ε(π) are written with their interval and information arguments in [foundations.md](foundations.md) §3.11. Full definitions, lemmas, and the honest statement of the theory's formal status are in [foundations.md](foundations.md).

## Sources

**Promise theory.** Bergstra & Burgess, *Promise Theory: Principles and Applications*, 2nd ed., χtAxis Press, 2019 (Defs 1–23). Bergstra & Burgess, "A static theory of promises," arXiv:0810.3294. Bergstra & Burgess, "Local and Global Trust Based on the Concept of Promises," arXiv:0912.4637 (2009). Burgess, "Authority (I): A Promise Theoretic Formalization," SSRN 3855352 (2021). Burgess & Dunbar, "A quantitative model of trust...", *European Economic Review* (2025). Burgess, "Cooperation in Human and Machine Agents: Promise Theory Considerations," arXiv:2604.10505 (2026). Promise Theory FAQ, markburgess.org.

**Agent contracts and practice.** Ye & Tan, "Agent Contracts...," arXiv:2601.08815 (2026). Leoveanu-Condrei, "A DbC Inspired Neurosymbolic Layer...," arXiv:2508.03665 (2025). Cemri et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025, arXiv:2503.13657. webframp, "The Promise None of Them Kept" (2026). Full bibliographic details are in the mission research report; the repository standard is to cite the named work inline, as above.
