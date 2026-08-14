# Agent Coordination — The Core Thesis: Promise Theory for Hybrid Human + AI Workforces

**Load this file when you need to design or diagnose coordination between specific humans and agents** — which actor may promise what to whom, how acceptance is recorded, where human oversight sits, how delegation chains stay trustworthy, and when a fleet should behave as a team rather than a swarm. This is the practical heart of the skill. The mapping table in Section 2 pairs every core promise-theory concept with a concrete agent-coordination practice; Section 3 draws the hybrid human + agent boundary; Section 4 positions promise theory inside the multi-agent systems research lineage. The definitions behind every term used here are in [foundations.md](foundations.md); the named, buildable patterns (manifests, handshakes, contracts, evaluation loops, breach→renegotiation, redundancy, trust calibration) are developed with worked examples in [patterns.md](patterns.md); calibrating trust and verification budgets is [trust-and-verification.md](trust-and-verification.md).

**Provenance.** The direct academic literature connecting promise theory to AI/LLM agents is **thin and recent**. As of mid-2026 it consists essentially of Burgess's position paper *Cooperation in Human and Machine Agents: Promise Theory Considerations* (arXiv:2604.10505, 2026), his 2025 twentieth-anniversary review, a handful of essays and interviews (NLnet/NGI, 2024; webframp, 2026), and adjacent applied work on trust measurement (Burgess & Dunbar, *European Economic Review*, 2025). Everything beyond those sources in this file is the author's synthesis mapping promise theory onto LLM-agent engineering practice, and that synthesis is labeled `EXTRAPOLATION` wherever it goes beyond what the cited sources explicitly state. Claims that could not be verified against a primary source are marked `[UNVERIFIED]`.

---

## 1. The thesis

Promise theory is a method of analysis for systems of autonomous agents — humans, LLM agents, deterministic automation, APIs — founded on three axioms: (1) agents are autonomous and cannot be coerced; (2) an agent can only promise its own behaviour; (3) an agent's knowledge is local (Bergstra & Burgess, *Promise Theory: Principles and Applications*, 2nd ed., 2019). From these axioms follow the concepts the agent-engineering industry is independently reinventing: public **promise offers** that others accept or refuse, **assessment** of whether promises are kept, **breach** as an expected event rather than an anomaly, **renegotiation** rather than blame, and a two-component model of **trust** (potential trustworthiness plus kinetic mistrust — the rate at which you verify).

**The thesis of this file is that promise theory supplies the missing organizing vocabulary and design discipline for hybrid human + AI agent workforces** — the coordination layer above the model layer. A single LLM call is a prediction problem; an agentic workforce is an organization problem. The orchestration literature (Zhu et al., *LLM-Based Multi-Agent Orchestration: A Survey*, 2026) defines the core mechanisms as task decomposition and allocation, inter-agent communication and context sharing, state management, control-flow sequencing, and error detection and recovery. All five are, in promise-theoretic terms, problems of *making, accepting, tracking, and repairing promises*. **EXTRAPOLATION** — this one-sentence identity between orchestration mechanisms and promise operations is this skill's synthesis, not a claim made in any single cited source; it follows from reading the survey's mechanism list against the promise machinery in Bergstra & Burgess (2019) and Burgess (arXiv:2604.10505).

Three properties make the mapping more than a metaphor:

1. **It is pessimistic by design.** Promise theory assumes promises will be broken and that guarantees are impossible ("Guarantees are impossible, and it is the autonomous responsibility of the user to allow for that" — Burgess, arXiv:2604.10505). That is exactly the correct prior for stochastic LLM agents, whose promises are "statements about intended future behavior with no binding force" (M12, "From Promises to Contracts," 2026).
2. **It is receiver-centric.** The Downstream Principle — the receiver of a promise holds the ultimate power of decision over the outcome — makes the relying party responsible for its own reliance, which is where evals, guardrails, redundancy, and escape hatches belong.
3. **It treats assessment as a first-class, costly mechanism.** Trust is *accumulated assessment* (webframp, "The Promise None of Them Kept," 2026); the rate and cost of verification are design variables, not afterthoughts. This is precisely the gap the agent industry is filling with evals, observability, and guardrails.

Burgess himself made the connection to agent systems explicit: *Cooperation in Human and Machine Agents* (arXiv:2604.10505, April 2026) opens with "Agent based systems are more common than we may think" and argues that promise theory "offers a unified perspective on organization and functional design with semi-automated efforts." The paper supplies the boundary concepts used throughout this file: the Downstream Principle, the three-languages problem, two-component trust, proxy/delegation chains, swarms vs. teams, Dunbar trust budgets, and the "cooperative manifesto."

## 2. The fixed mapping table

The table below is the fixed concept→practice mapping of this skill: the left column is a promise-theory concept with its canonical source; the right column is a concrete agent-coordination practice — something you can actually do with or for agents. All eleven rows are populated; the rows marked **EXTRAPOLATION** are this skill's synthesis where the source literature does not itself make the connection. Each right-hand cell names a practice, not a restatement of the concept.

| # | Promise-theory concept (source) | Concrete agent-coordination practice |
|---|---|---|
| 1 | **Promise offer** — an agent's public declaration of its own intended behaviour (`Ai →+b Aj`; Bergstra & Burgess 2019) | Publish a **versioned capability manifest**: an MCP tool descriptor or function schema ("I can search the web"), a repository `AGENTS.md` ("I will only edit files under /workspace"), a system prompt with explicit constraints, a human's commitment ("I will review PRs by EOD"), or an SLO. Declare capabilities, constraints (what the agent will *not* do), resource limits, and withdrawal semantics before any task is dispatched. |
| 2 | **Acceptance promise** — the receiver's voluntary agreement to rely on an offer (`Aj →−b Ai`); only the overlap of offer and acceptance transmits influence | Run a **two-way handshake / approval gate** on every delegation: the executing agent explicitly accepts or refuses the task; a human clicks "approve" at consequential checkpoints; a guard checks "is this worker enrolled for this capability?" before dispatch. Log accept/refuse and measure the refusal rate as a coordination signal. |
| 3 | **Imposition** — an attempt to induce acceptance by force, without the receiver's promise | Detect and eliminate **push-based commands without consent**: dispatching to an agent that never accepted, a central controller that assumes compliance, a human ordered to execute without opt-in. LLM-era impositions fail distinctively: they *look* accepted (fluent acknowledgment) and are not — so audit for "acknowledged but not enrolled" paths. |
| 4 | **Assessment α** — each agent evaluates whether the promises it relies on are kept; the load-bearing concept ("the principal area for exploiting and misdirecting agents" — Burgess) | Build the **assessment layer**: evals (offline benchmarks + online scorers), guardrails, observability traces, code review, fact-checking, human review. Treat "a promise that nobody assesses" as operationally meaningless. |
| 5 | **Measured promise / P_succ** — an empirically estimated probability of success; the receiver's accumulated estimate of reliability (`V_S = α_R(π_S)`) | Track **potential trust as data**: maintain a per-agent P_succ over repeated runs (Leoveanu-Condrei's Design-by-Contract for LLMs); compare providers by P_succ and cost; treat two agents satisfying the same contract as interchangeable except for those two numbers. |
| 6 | **Verification rate / kinetic mistrust** — the rate at which the receiver checks on the promiser; an attention/energy budget (Burgess & Dunbar 2025) | Run a **verification sampling schedule**: how often you run evals, ping health checks, re-audit outputs, or re-review an agent's work. Start new agents at 50-50 and calibrate; scale checking rate with risk and inversely with measured P_succ; budget the verification cost explicitly (tokens + human attention). |
| 7 | **Breach** — an unkept promise, detected by assessment; expected, not exceptional | Classify breaches against the **multi-agent failure taxonomy** (Cemri et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025): a failed eval, guardrail trip, violated SLO, wrong tool call, or reviewer-caught hallucination maps to specification / inter-agent conflict / verification failure. Instrument each class. |
| 8 | **Downstream Principle** — the receiver holds ultimate decision power and carries greatest causal responsibility for the outcome (Burgess, arXiv:2604.10505, Def. 1) | Practice **receiver-owned reliance risk**: the consumer of an agent's output decides its value, so give every downstream party redundancy, verification tools, and escape hatches ("the downstream agent only has its own policy to blame" — Burgess). Design for the promise *not* being kept. |
| 9 | **Proxy / delegation chains** — conditional promises through middlemen are unreliable; agents are not reliable relays (Burgess, arXiv:2604.10505) | Treat **every handoff as a logged boundary**: record inputs, outputs, and timing at each agent-to-agent transfer the way you would log a remote procedure call; verify per-hop rather than trusting the chain head; watch for handoff-context-loss failures in multi-agent traces. |
| 10 | **Swarms vs. teams** — "a swarm is a role associated with flying, not an identity"; role-differentiated, contract-bearing collaboration is a team (Burgess, arXiv:2604.10505 §VI-E) | Choose **team semantics for production agent systems**: assign differentiated roles with explicit promises and contracts (microservices are a team structure applied to IT); use true swarm semantics (emergent, homogeneous) only where role differentiation is genuinely absent. |
| 11 | **Dunbar trust budgets** — human groups are bounded by cognitive trust budgets; machine limits are unknown (Burgess & Dunbar 2025) | Set **team-size and span-of-control limits**: keep human-oversight groups inside Dunbar-scale budgets, batch and group agent fleets to respect attention limits, and treat "how many agents can one human meaningfully verify?" as a first-order design question. **EXTRAPOLATION** — applying the numbers to agent fleets is this skill's reading; the trust-budget model itself is Burgess & Dunbar's. |

Two of these rows deserve a short expansion because they are the least obvious in practice.

**Row 9 — proxy/delegation chains.** Burgess's warning that conditional promises through middlemen are unreliable (arXiv:2604.10505) predicts the handoff-context-loss failures documented in multi-agent traces (Zhu et al. 2026; Braintrust 2026). The operational consequence is that *a chain of agents is only as bound as its least-enforced boundary*: verify at each hop, propagate context explicitly, and treat the handoff record as part of the assessment data. **EXTRAPOLATION** — the mapping of "conditional promise through a middleman" to "multi-agent handoff" is this skill's synthesis; the conditional-promise mechanics are Burgess's.

**Row 10 — swarms vs. teams.** Most production agent systems need team semantics, not swarm semantics: roles, contracts, acceptance, and assessment. A "swarm" of undifferentiated agents that emerges into coordination without declared promises is, in promise-theoretic terms, a system in which promises are being made and broken without record — exactly the *EmergentBehavior* risk dimension the Zhu et al. (2026) six-dimension framework measures (messages outside the declared interaction graph). **EXTRAPOLATION** — the equation "undifferentiated swarm ≈ unrecorded promises" is this skill's synthesis.

## 3. The hybrid human + agent boundary

The hardest coordination problem is the boundary between humans and agents — not because agents are complex, but because the boundary carries the theory's two asymmetric responsibilities: **acceptance** (who chooses to rely) and **assessment** (who verifies), plus the accountability question of who is *responsible* when a promise is broken. Burgess's 2026 paper supplies the frame; the operational reading below is this skill's synthesis and is labeled where it extrapolates.

### 3.1 Humans are acceptors and evaluators, never agents in the manifest

In promise theory every actor is both a promiser and an assessor; for humans in a hybrid workforce this means:

- **Humans accept agent promises.** A human decides which agent offers to rely on, and can refuse (the acceptance handshake pattern in [patterns.md](patterns.md)). Acceptance is the mechanism by which agents acquire *legitimate* influence over human work.
- **Humans evaluate agent promises.** Human review is the highest-bandwidth assessment available for *semantic* promises ("the summary is accurate," "this code has no backdoor") that deterministic checks cannot yet verify (M12, 2026: "we cannot yet cheaply enforce 'the summary is accurate'"). Human review is promise evaluation, and its cost is a first-order budget item.
- **The Downstream Principle makes the relying human responsible for their own reliance** — "one takes on the risk of an agent's promise not being kept when choosing to engage with it" (Burgess, arXiv:2604.10505). This is not victim-blaming; it is a design directive: give the human the redundancy, verification tools, and escape hatches that make downstream responsibility actionable.

**Manifest modeling consequence:** in this skill's contract schema, humans are never declared as agents in a manifest. Human acceptance of a promise is modeled as an `expectations` entry with `from: human`; humans accept and evaluate, they do not declare promises inside the agent graph. This keeps the model's causal bookkeeping honest: the only actors that can promise are the ones whose behaviour can be observed and assessed. **EXTRAPOLATION** — the schema consequence is this skill's design choice; the underlying claim (humans as acceptors/evaluators) is Burgess's and the schema's `from: human` modeling is pinned in the skill's contract.

### 3.2 Authority as calibrated subordination — voluntary and withdrawable

Burgess formalizes authority as **calibrated subordination**: followers voluntarily promise to follow a leader, and the leader is a trusted calibration point (Burgess, "Authority (I): A Promise Theoretic Formalization," SSRN 3855352, 2021; arXiv:2604.10505). Hierarchy "cannot be imposed onto autonomous agents, yet hierarchies can be formed by voluntary cooperation." Organizational implications for human oversight of agents:

- A **supervisor** (human or orchestrator) is not an authority by position but by *accepted promises to follow*. When agents and humans stop accepting direction, authority has evaporated — regardless of job titles.
- **Leadership as a calibration role** explains why centralized orchestrators are attractive (a single calibration point) and fragile (a single point of trust — if the calibration is wrong, everything downstream is wrong).
- **Oversight design should treat the human supervisor as an assessor with calibrated authority**: the supervisor's promise to the organization is "I will verify X at rate Y," and the organization accepts it. **EXTRAPOLATION** — the supervisor-promise formulation is this skill's synthesis; the calibrated-subordination model is Burgess's.

### 3.3 Causal vs. moral responsibility

Burgess (arXiv:2604.10505, Definition 2) distinguishes:

- **Causal responsibility** — "the freedom to obtain a promised service elsewhere" (redundancy). An agent that had alternatives and did not use them bears causal responsibility for relying on a broken promise. This is formalizable and auditable.
- **Moral responsibility (culpability)** — "a human assessment about whether agent outcomes stem from good or bad intent; hence it cannot be formalized except as a norm or in law."

For hybrid workforces this distinction is the accountability skeleton: **machines can be causally responsible (and audited); only humans can be morally responsible (and regulated).** This aligns with current governance practice — e.g., the EU AI Act's human-oversight provisions and accountability resting with deployers — and with the industry pattern of "human responsibility for AI outcomes." **EXTRAPOLATION** — the alignment with regulation is this skill's reading; the causal/moral distinction is Burgess's. The operational consequence for a coordination design: audit trails, redundancy choices, and verification records make causal responsibility legible; they do not, and cannot, settle moral responsibility, which belongs to the humans who deployed and relied.

### 3.4 Human-in-the-loop escalation

HITL is promise evaluation by the most capable assessor, triggered at agreed boundaries:

- **Approval gates** (LangGraph breakpoints, human-in-the-loop nodes): the human is the *final acceptance promise* for consequential actions (money-moving, identity-affecting, externally visible).
- **Escalation on uncertainty**: when assessment is inconclusive (low confidence, contested semantics), the promise escalates to a higher-capability assessor — a human or a stronger model.
- **Escalation on breach**: the agent contract enters VIOLATED/EXPIRED; termination conditions trigger; a human decides renegotiation vs. redundancy vs. shutdown (see the breach→renegotiation pattern in [patterns.md](patterns.md)).
- **Bounded escalation**: stop after a named number of non-converging remediation passes and report the evidence (this skill's completion discipline applied to kinetic mistrust).

Burgess's warnings carry the design constraints: mistrust is draining — conflict consumes attention (Wikipedia edit wars), and Dunbar-scale trust budgets bound human tolerance (NLnet interview, 2024). Agent fleets must not impose unbounded human monitoring loads; that is how alert fatigue and rubber-stamping set in. And "if you trust something too much, you're not paying attention" — humans who delegate all verification to agents are the Eloi; the agents (and those who control them) are the Morlocks (arXiv:2604.10505).

### 3.5 The three-languages problem

Burgess's three-languages analysis (arXiv:2604.10505) — **sender language, receiver language, co-language** — explains why mentalistic semantics cannot work between autonomous agents: there is "no authority that calibrates" two agents' internal languages to be the same, and "agents can never know when they have reached the optimum without an actual (promise) dialogue and mutual assessment." **Autonomous agents are never certain.**

For LLM agents this is structural, not incidental: sharing a base model or a protocol vocabulary does not guarantee shared meaning, because "each picks a selection based on its own context (which is autonomous and independent)." Capability schemas (MCP, A2A) are structural, not intentional — they standardize the *form* of capability declaration, not the *meaning* of the outcomes. Practical consequences:

- **Expect misunderstanding.** "Agents should expect to misunderstand one another's intentions to some level" (arXiv:2604.10505); the Cemri et al. (2025) inter-agent-conflict class is this phenomenon at scale.
- **Negotiate meaning through dialogue and assessment**, not through shared ontologies — ontologies "trade expressibility for false precision" and need versioned calibration (Burgess).
- **Write acceptance criteria in the receiver's language**, the co-language the receiver can actually check (this is what an eval formalizes — see [trust-and-verification.md](trust-and-verification.md)).

### 3.6 Swarms vs. teams at the human boundary

The swarm/team distinction (row 10 of the mapping table) has a human-organizational reading: Burgess's "swarm is a role associated with flying, not an identity" (arXiv:2604.10505 §VI-E) means a human group can *behave* swarm-like without being a swarm, and a fleet of agents can *behave* team-like if roles and promises are declared. For hybrid workforces: add agents to the team as **promise-holders with the same instruments as humans** — a working agreement (the team's promise set), a Definition of Done (acceptance criteria), a cadence (assessment rhythm), and a retrospective (renegotiation). An agent with a versioned manifest, acceptance criteria, and a retro loop is governable; an agent dropped into a team with none of these is an imposition. **EXTRAPOLATION** — the direct agent-inclusion extension is this skill's synthesis; the agile-to-promise mapping is documented in Burgess's management materials (Open Leadership Network / Open Space Technology collaborations with Mezick and Sheffield, 2019–2020).

## 4. Multi-agent systems lineage — what promise theory adds

Promise theory sits inside a long lineage of agent-coordination research. Knowing the lineage positions the skill and states precisely what promise theory adds (and what it deliberately rejects):

| Classic approach | Central mechanism | What promise theory changes |
|---|---|---|
| Deontic logic / policy-based management | Obligation, command | Autonomy as base state; obligations are derived, voluntary agreements (Bergstra & Burgess, arXiv:0810.3294) |
| FIPA-ACL (speech acts, mentalistic semantics) | Request/inform/promise performatives with BDI semantics | Three-languages problem; meaning is negotiated, never guaranteed (Singh 1998 made the social-semantics critique; Burgess's co-language argument supplies the mechanism) |
| BDI architectures (Bratman; Rao & Georgeff) | Interior beliefs/desires → intention | Interior is unobservable; only the expressed promise and the assessed outcome matter — methodologically convenient for LLM agents whose "beliefs" are not stable objects **EXTRAPOLATION** |
| Social commitments (Yolum & Singh 2002; Jennings 1993) | Public, socially held obligations between agents | Promises bind only the promiser; no obligation is entailed ("No agent may promise anything on behalf of any agent but itself" — Bergstra & Burgess 2019). The two schools converge on design (track, verify, repair) but diverge on the primitive |
| Norms and institutions (Dignum et al.; Boella, van der Torre) | Enforced norms and institutional mechanisms | Norms hold only when voluntarily accepted; authority = calibrated subordination (SSRN 3855352) |
| Contract Net Protocol (Smith 1980) / agent contracts | Task allocation by announcement, bidding, award | Full lifecycle with resource bounds, measured success, and promise-theoretic acceptance (Ye & Tan 2026 extend it — see [patterns.md](patterns.md)) |
| Control theory / cybernetic feedback | Feedback on a measurable plant | The "plant" is autonomous and may ignore the controller; the downstream party decides |

**The single most important addition:** promise theory makes *assessment* — and its cost — a first-class citizen. Every classic school treats verification as an engineering afterthought; promise theory treats it as the mechanism by which trust, the "common currency" of coordination, is created and spent. That is precisely the gap the LLM-agent industry is now filling with evals, observability, and guardrails.

## 5. Designing the promise graph — a practical procedure

Under the reframing in Section 1, the manager's job is not to command but to **design the promise graph**: who may promise what to whom, what the acceptance criteria are, how breaches are detected, and who absorbs the risk when a promise is broken. A working procedure, synthesized from the patterns in [patterns.md](patterns.md):

1. **Inventory the actors** — every human, agent, API, and deterministic process that touches the outcome. Decide which are agents (they can promise) and which are acceptors/evaluators (they can only accept and assess — including all humans).
2. **Declare capabilities** — each agent publishes a versioned manifest: capabilities, constraints, resource limits, withdrawal semantics (promise offer).
3. **Negotiate acceptance** — for each delegation, record an explicit accept/refuse; refusal is a coordination signal, not a failure (acceptance promise).
4. **Pin acceptance criteria** — for every promise that matters, state in the receiver's language how "kept" will be determined (assessment; an eval is a formalized acceptance criterion).
5. **Instrument assessment** — attach evals, guardrails, observability, and human review at the risk-appropriate rate (kinetic mistrust); store assessments as versioned data (see [trust-and-verification.md](trust-and-verification.md)).
6. **Plan for breach** — every load-bearing promise gets redundancy or a renegotiation path; escalation is named and bounded (breach→renegotiation pattern).
7. **Review on a cadence** — a regular assessment rhythm (standup-like) and a periodic renegotiation of the promise set (retro-like).

This procedure is this skill's synthesis — **EXTRAPOLATION** — of the sources cited throughout this file; each individual step is grounded in the mapping table's rows.

## 6. Routing to sibling skills

- **Multi-agent debate and convergence** → [agent-council](../agent-council/SKILL.md). When you want to *run* structured multi-agent debate, agent-council is the operational tool: its panel debate is a promise exchange (each panelist offers positions, the moderator accepts/assesses, synthesis converges), and its convergence-aware iteration is an evaluation loop over the panel's promises. Use promise theory to *design* the exchange; use agent-council to *execute* it.
- **Assessment layer** → [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md) (also routed from `references/trust-and-verification.md`): verifying promises are kept via evals, traces, and guardrails.
- **Workflow design as promise chains** → [workflow-architect](../../workflow-architect/SKILL.md) (also routed from `references/patterns.md`): designing a workflow is designing a chain of promises.
- **Promise-keeping evidence** → [artifact-pyramids](../artifact-pyramids/SKILL.md) (also routed from `references/trust-and-verification.md`): structure evidence as summaries → analysis → evidence dossiers.
- **The skill format itself** → [agent-skills](../agent-skills/SKILL.md); **script conventions** → [cli-builder](../cli-builder/SKILL.md).

## 7. Sources

**Primary promise theory.** Burgess, "Cooperation in Human and Machine Agents: Promise Theory Considerations," arXiv:2604.10505 (2026) — the key paper for this file: Downstream Principle, three-languages problem, two-component trust, proxy chains, swarms vs. teams, Dunbar limits, causal vs. moral responsibility, the cooperative manifesto. Bergstra & Burgess, *Promise Theory: Principles and Applications*, 2nd ed., χtAxis Press, 2019. Bergstra & Burgess, "A static theory of promises," arXiv:0810.3294. Burgess, "Authority (I): A Promise Theoretic Formalization," SSRN 3855352 (2021). Burgess & Dunbar, "A quantitative model of trust as a predictor of social group sizes and its implications for technology," *European Economic Review* (2025). Burgess, "Notes on Trust as a Causal Basis for Social Science," SSRN 4252501 (2022).

**Promise theory + agents (direct, recent).** Burgess, arXiv:2604.10505 (above). NLnet/NGI Assure interview with Burgess, "Promise Theory," 2024 (nlnet.nl/project/TrustSemanticLearning/interview.html). webframp, "The Promise None of Them Kept," 2026. M12/Todd Graham, "From Promises to Contracts: Enforceable Behavior in LLM Agents," 2026.

**Agent systems lineage.** Jennings, "Commitments and conventions," 1993; Yolum & Singh, "Commitment Machines," 2002; Singh, "A Social Semantics for Agent Communication Languages," 1998; Smith, "The Contract Net Protocol," 1980; Dignum et al., normative MAS; Boella, van der Torre, Verhagen.

**LLM multi-agent systems.** Cemri, Pan, Yang, et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025, arXiv:2503.13657 (14 failure modes in three classes). Zhu, Liu, Yu & Zhang, "LLM-Based Multi-Agent Orchestration: A Survey," *Future Internet* 18(6), 2026. Ye & Tan, "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems," arXiv:2601.08815 (2026). Leoveanu-Condrei, "A DbC Inspired Neurosymbolic Layer for Trustworthy Agent Design," arXiv:2508.03665 (2025). Shavit et al., "Practices for Governing Agentic AI Systems," OpenAI, 2023. Full bibliographic details are in the mission research report; the repository standard is to cite the named work inline, as above.
