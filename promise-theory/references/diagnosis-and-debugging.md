# Diagnosis and Debugging — Failure Taxonomy, Diagnostic Procedure, and Limits

**Load this file when you are diagnosing a coordination failure** — a multi-agent task that produced the wrong outcome, an agent that acknowledged a constraint and then violated it, a handoff that lost context, or a review loop that never caught a breach — or when you need to know where promise theory itself stops helping. The file gives you (1) the failure taxonomy mapped onto promise-theory breach categories, (2) a stepwise diagnostic procedure you can run against a specific incident, and (3) the theory's limitations and open problems. Definitions of every term used here are in [glossary.md](glossary.md); the concept→practice mapping that motivates the categories is in [agent-coordination.md](agent-coordination.md); the recovery patterns (breach→renegotiation, redundancy, trust calibration) are developed in [patterns.md](patterns.md) and [trust-and-verification.md](trust-and-verification.md).

**Provenance.** The failure taxonomy is Cemri, Pan, Yang, et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025, arXiv:2503.13657 (fourteen failure modes in three classes). The mapping of those classes to promise-theory breach categories, and the four-step diagnostic procedure in Section 2, are this skill's synthesis and are labeled `EXTRAPOLATION`. The limitations section restates documented positions from the cited sources (M12, "From Promises to Contracts," 2026; Zhu et al. 2026; Ye & Tan 2026; Burgess, arXiv:2604.10505, 2026). Claims that could not be verified against a primary source are marked `[UNVERIFIED]`.

---

## 1. The failure taxonomy in promise vocabulary

### 1.1 Where the taxonomy comes from

The empirical record on LLM multi-agent systems is blunt: one agent's incorrect reasoning cascades through the system, coordination overhead grows with agent count, and local optimization conflicts with global goals (Pan et al. 2025; Renney et al. 2026, arXiv:2601.03328). Cemri et al. (NeurIPS 2025) distilled this into a catalog of **fourteen failure modes in three classes**:

- **Specification issues** — the task or prompt is wrong, ambiguous, or overly constrained; the agents were set up to fail before any execution.
- **Inter-agent conflicts** — agents disagree, argue, or produce incompatible outputs; the system spends its effort on unproductive contention.
- **Task verification problems** — the system cannot tell whether it succeeded; success and failure are indistinguishable from the observer's vantage point.

The value of the taxonomy for this skill is that it turns "something went wrong" into instrumentable categories — and each category has a precise counterpart in the promise model (Section 1.2). That mapping is what makes a diagnosis *promise-theory-grounded* rather than a vague "agents misbehaved" story.

### 1.2 The fixed mapping — failure class ↔ promise-theory breach category

| Failure class (Cemri et al. 2025) | Promise-theory breach category | What it means in the model |
|---|---|---|
| **Specification issues** — task ill-posed, ambiguous, overly constrained | **Broken promise bodies** — the promise was never precisely stateable; the co-language was inadequate | The body b of the promise (label Λ, type τ, constraint χ) was empty, contradictory, or written in a language the receiver could not check. "Agents should expect to misunderstand one another's intentions to some level" (Burgess, arXiv:2604.10505). |
| **Inter-agent conflicts** — disagreement loops, incompatible outputs, unproductive arguing | **Failed acceptance / incompatible co-languages** — acceptance was never achieved; internal languages did not overlap | A delegation requires an offer (+b) and a matching acceptance (−b); their overlap b∩ is the only influence that transmits. When two agents' outputs conflict, the acceptance handshake between them never closed — each side kept a different promise. |
| **Task verification problems** — the system cannot tell success from failure | **Missing assessment** — no receiver-side evaluation loop | Trust is accumulated assessment; a system that cannot assess cannot accumulate trust. The most promise-theoretically damning class: the failure is not that a promise was broken but that *no one was watching* whether it was kept. |

**EXTRAPOLATION** — the mapping table is this skill's synthesis: the three classes and fourteen modes are Cemri et al.'s, and the promise machinery (body, acceptance, assessment) is Burgess/Bergstra's; the identity between them is the skill's reading, not a claim made in either source.

### 1.3 A fourth, distinctly promise-theoretic category: withdrawal failure

Cemri's taxonomy is snapshot-shaped: it classifies what happened *during* the task. Promise theory adds a temporal dimension — a promise can be withdrawn at any time, and a withdrawal that is not declared within scope is itself a failure mode (the shadow side of deception: a non-documented change of intention). Concrete forms:

- an agent **silently drops a task** mid-flight and starts something else;
- a capability is **revoked without notice** while downstream agents still rely on it;
- a promise **expires** (its `expires` bound passes, the agent contract enters EXPIRED or TERMINATED) and nobody renegotiates;
- a manifest is **revised and re-published** while old acceptances are still being honored.

The classic CFEngine-era lesson is that intentions drift as promises are forgotten, changed, or deprecated; if some agents change while others do not, reliance fails (promise drift, per the Promise Theory FAQ). **EXTRAPOLATION** — classifying withdrawal failure as a fourth coordination-failure category is this skill's reading; the withdrawal/revocability machinery and the drift warning are Burgess/Bergstra's.

### 1.4 Symptom → category triage

When you have a symptom but not yet a category, start here. Each row names the likely category and the first place to look.

| Symptom | Likely category | First place to look |
|---|---|---|
| Agent produced a plausible but wrong deliverable | Specification (broken body) **or** Verification (missing assessment) | The task text vs. the deliverable; whether any independent check ran |
| Agents argued, looped, or produced incompatible outputs | Inter-agent conflict (failed acceptance) | Handoff records; each agent's recorded acceptance of the other's output |
| The system reported success but the outcome was wrong | Verification (missing assessment) | The assessment loop: what "success" was measured against, and by whom |
| A task silently vanished or stopped | Withdrawal failure | The withdrawal/expiry log; the manifest versions |
| Agent acknowledged a constraint, then violated it | Specification + enforcement gap | The contract ladder: where the boundary lived, and whether it was enforced outside the model |
| Two outputs conflict but no one noticed | Verification (missing assessment) + failed acceptance | Whether any receiver-side check compares outputs |

## 2. The diagnostic procedure

**EXTRAPOLATION** — this four-step procedure is this skill's synthesis: it applies the promise machinery (graph, bindings, evaluation loop, withdrawal) as a debugging discipline. The procedure is a disciplined walk over the coordination state; do the steps in order. Each step either locates the failure or rules out a whole category. Apply the completion discipline from `SKILL.md`'s Exit Conditions: **stop after three non-converging passes and report the evidence** rather than re-litigating the same promises.

### Step 1 — Walk the promise graph

**Goal.** Reconstruct who promised what to whom, and find structural impossibilities before looking at execution.

1. **Inventory the actors** — every human, agent, API, and deterministic process that touched the outcome. Decide which are agents (they can promise) and which are acceptors/evaluators (they can only accept and assess).
2. **Rebuild the promise set** — from the manifest, the contracts, and the prompts: for each delegation, what body was promised (capability or intent), to whom, with what constraint and withdrawal clause?
3. **Check every edge** — is each delegation backed by a declared promise? The *admission rule*: nothing should reach an agent that never advertised the capability (webframp 2026). An edge with no declared promise is an imposition masquerading as delegation.
4. **Look for structural contradictions** — two promises of the same type with incompatible constraints; an empty promise (acceptance criteria unstated); over-promising (a valence exceeded, one agent bound beyond its capacity).
5. **Trace the chains** — for each handoff (research → review → write, orchestrator → worker, agent → tool), is there a record of what was passed and in what form?

**What a finding means.** An edge with no declared promise → the failure started at design time, not execution (imposition). A broken or contradictory body → specification class. A chain whose handoffs have no records → you cannot yet distinguish inter-agent conflict from verification failure; proceed to Step 2 with the handoff records as your target.

### Step 2 — Check bindings (acceptance)

**Goal.** Verify that every delegation was actually accepted, and that the offer/acceptance overlap existed.

1. **Record check** — for each delegation, is there a logged accept or refuse? Silence is the worst case: an *imposition that looks accepted* (the LLM-era signature: fluent acknowledgment without enrollment).
2. **Overlap check** — did the acceptor's counter-promise overlap the offer (b∩)? The executor may have accepted a *different* task than the requester offered — the classic co-language failure.
3. **Cross-agent check** — do the recorded acceptances reference promises declared by *other* agents (no self-acceptance, no dangling accepts)? In the skill's manifest schema these are the `agents.accepts` bindings.
4. **Refusal signal** — was any refusal recorded? Refusal is a coordination signal, not a failure; a rising refusal rate means manifest/task mismatch, and a refusal that is not recorded becomes an invisible conflict.

**What a finding means.** No recorded acceptance → the task was an imposition; the "agent failure" is an acceptance gap upstream of any execution error. Non-overlapping bodies → co-language failure: each side kept a different promise, so both sides are "right" and the contract is wrong. This is the inter-agent-conflict class made legible.

### Step 3 — Check the evaluation loop (assessment)

**Goal.** Determine whether the system *could* have detected the breach — and whether it did.

1. **Coverage** — for each load-bearing promise, is there an assessment: who assesses, when, against what criterion? A promise that nobody assesses is operationally meaningless.
2. **Independence** — is the assessment made by a receiver or an independent verifier, or does it track the promiser's self-report? An agent that controls the evidence stream about itself (its own traces, its own "all checks passed") controls the record its reliability is computed from — assessment capture.
3. **Data** — are assessments stored as versioned data (a promise ledger) with provenance, or are they ephemeral? An assessment without provenance is an opinion, not evidence.
4. **Language** — is the acceptance criterion written in the receiver's language? An eval is a formalized acceptance criterion; if the criterion is unstated or written only in the promiser's vocabulary, the loop has nothing to compare against.
5. **Actuation** — does the loop *act* (repair, renegotiate, escalate) or only observe? A loop that observes but never actuates is a log, not an evaluation loop.

**What a finding means.** No assessment → verification-class failure: the system was blind by design; the fix is to build the loop, not to blame an agent. Assessment that tracks the promiser's self-report → the assessment itself is the vulnerability (see gameable assessment in [trust-and-verification.md](trust-and-verification.md)).

### Step 4 — Check withdrawal semantics

**Goal.** Find promises that were revoked, expired, or silently changed — the temporal failures that snapshot taxonomies miss.

1. **Withdrawal log** — was any promise withdrawn? Was the withdrawal declared within scope, *before* downstream agents relied on it?
2. **Expiry** — did any promise expire mid-task (`expires` bound passed; the agent contract entered EXPIRED or TERMINATED) without renegotiation?
3. **Version drift** — did a manifest or contract version change while old acceptances were still being honored? Was the revision accepted, or just published?
4. **Reliance after revocation** — did any party keep relying on a promise after its withdrawal? That reliance is now *unbacked* — downstream responsibility belongs to the receiver, who should have had redundancy or an escape hatch (Downstream Principle).

**What a finding means.** Silent withdrawal → downstream agents kept relying on a non-promise; the failure is the un-declared revocation, and the fix is scoped-withdrawal discipline plus redundancy for load-bearing promises. Expiry without renegotiation → the contract lifecycle was not observed; the fix is lifecycle monitoring (DRAFTED → ACTIVE → {FULFILLED, VIOLATED, EXPIRED, TERMINATED}).

### 2.1 Worked example — the fabricated-citation report

**Scenario.** A three-agent research pipeline — `research-agent` → `reviewer` → `writer` — produces a final report for a human acceptor. The report contains two fabricated citations. Logs show `research-agent` and `reviewer` spent 40 minutes in a disagreement loop, and `writer` "summarized reviewer's notes." The human approved on the strength of a "all checks passed" summary line. Run the procedure:

1. **Walk the promise graph.** `research-agent` promised `lit-review` ("survey and summarize literature on X, limit 20 sources"); `reviewer` promised `fact-check` ("verify claims against cited sources"); `writer` promised "report from reviewed notes." Nothing declared what "reviewed" meant. Structural contradiction: `reviewer`'s `fact-check` covered claims in the *summary*; `writer`'s output reintroduced claims from `research-agent`'s *raw notes* that `reviewer` never saw. The writer's promise body was inexact — an empty-ish promise with unstated acceptance criteria.
2. **Check bindings.** `research-agent` never accepted `reviewer`'s output format: `reviewer`'s re-promise ("send me a claims list, not prose") was refused and logged out-of-scope. `writer` accepted "reviewed notes," but the accepted body did not specify which artifacts counted as "reviewed." The acceptance overlap b∩ on the research → review → write chain was empty at the critical handoff — the disagreement loop was this gap expressing itself.
3. **Check the evaluation loop.** The only assessment was `writer`'s self-check ("all checks passed") plus a human approval of a one-line summary. No citation-level check ran against the final report; the loop's observation step stopped at the promiser's own last write — assessment capture, by construction.
4. **Check withdrawal semantics.** `reviewer`'s fact-check coverage was effectively withdrawn when it refused the format, but nothing recorded the withdrawal or re-scoped `writer`'s promise; `writer` kept relying on "reviewed notes" that no longer existed as an object.

**Diagnosis in promise vocabulary — a multi-class breach:** (a) **broken promise body** — `writer`'s promise never specified which source artifacts were in scope (specification class); (b) **failed acceptance** — no overlap on the review handoff (inter-agent conflict class); (c) **missing assessment** — no independent citation check on the final artifact (verification class); (d) **withdrawal failure** — fact-check coverage was dropped without record.

**Remediation (breach → renegotiation, not blame):** pin the writer's acceptance criteria (which artifacts count as "reviewed"), record accept/refuse per handoff, add an independent citation verifier as the acceptance criterion, and log withdrawals explicitly (see the breach→renegotiation pattern in [patterns.md](patterns.md), and the assessment wiring in [trust-and-verification.md](trust-and-verification.md)). Then renegotiate the promise set with all three agents and re-run the loop — the human acceptor re-approves only the *new* contract, not the old one.

## 3. Diagnosis by category — what a finding means and what to do

### 3.1 Broken promise body (specification class)

Sub-modes: ambiguity (co-language mismatch), over-constraint (the body demands the impossible), empty promise (acceptance criteria unstated), over-promising (valence exceeded — more bindings than resources). Evidence to collect: the task text, the manifest, the contract tuple, and both sides' interpretations of the body. Fixes: rewrite the body in the receiver's language; make acceptance criteria exact; where enforcement matters, climb the contract ladder (soft prompt → validation → guards → sandbox → formal methods) — see pattern 3 in [patterns.md](patterns.md).

### 3.2 Failed acceptance (inter-agent conflict class)

Sub-modes: disagreement loops, incompatible outputs, unproductive arguing, refusal without record, silence-as-acceptance. Evidence to collect: handoff logs, accept/refuse records, traces at each agent-to-agent boundary. Fixes: run the acceptance handshake on every delegation (pattern 2 in [patterns.md](patterns.md)); make refusal cheap and non-punitive; log every handoff like an RPC; verify per hop rather than trusting the chain head (proxy-chain lesson, [agent-coordination.md](agent-coordination.md) row 9).

### 3.3 Missing assessment (verification class)

Sub-modes: no eval at all, self-assessment only, stale or contaminated evals, assessment capture (the agent controls its own evidence stream). Evidence to collect: eval coverage per promise, the ledger, the guardrail configuration. Fixes: build the evaluation loop (pattern 4); use independent verifiers (deterministic checks + human review + a judge model, cross-checked); store assessments as versioned data by a mechanism the assessed agent cannot write; treat assessment as an attack surface (Section 6 of [trust-and-verification.md](trust-and-verification.md)).

### 3.4 Withdrawal failure

Sub-modes: silent task drop, unannounced capability revocation, expiry without renegotiation, manifest version drift. Evidence to collect: the withdrawal/expiry log, manifest version history, the contract lifecycle states. Fixes: declare withdrawals within scope and before reliance; monitor contract lifecycles; give load-bearing promises redundancy so a withdrawal degrades rather than breaks (pattern 6 in [patterns.md](patterns.md)).

## 4. Limitations and open problems

These are the places where promise theory, applied to LLM agents, strains. Knowing them keeps a diagnosis honest: some "failures" are the theory's open problems, not your implementation's bugs.

### 4.1 No benchmark for coordination quality

There is "no widely adopted benchmark specifically targeting multi-agent orchestration" (Zhu et al. 2026, *Future Internet* 18(6)). The six-dimension evaluation framework in that survey — task performance, coordination efficiency, scalability, robustness, cost efficiency, emergent behavior — is a *proposal*, not a standard. Consequence for diagnosis: you cannot yet score "how good is this promise graph" objectively; classification and remediation stay qualitative, and vendor-reported coordination numbers should be treated as `[UNVERIFIED]` until independently replicated.

### 4.2 Guarantees don't compose across handoffs

Ye & Tan's contract conservation laws hold *within* one contract — delegated sub-contracts cannot exceed the parent's resource bounds, which makes hierarchical coordination composable in budget terms (arXiv:2601.08815, 2026). But **conservation of verification coverage across handoffs does not exist**: a verified upstream promise says nothing about whether the downstream handoff was verified. Each handoff reopens the trust question; "a chain of agents is only as bound as its least-enforced boundary." Consequence for diagnosis: a clean upstream result does not clear the downstream pipeline; check each hop's own loop.

### 4.3 LLM promises lack causal teeth

An LLM's promise is "a statement about intended future behavior with no binding force"; "the promise and the action are the same kind of object" (M12 2026). There is no mechanism connecting the acknowledgment to the compliance: prompt-level promises are weak conditioning and can be overridden by later context — prompt injection is the clean proof. Consequence for diagnosis: for LLM promisers, "the promise was broken" must be paired with "and it was never enforceably bound." The fix is the contract ladder (enforcement and non-bypassability), not more trust or more pleading.

### 4.4 Stochasticity is irreducible

"As long as the model samples its outputs with any randomness at all, the forbidden action keeps a nonzero probability" (M12 2026). Training lowers but never zeroes the breach probability. Consequence for diagnosis: a single breach is not, by itself, evidence of a design bug; distinguish a one-off stochastic miss from a distributional failure, and estimate P_succ over repeated assessed runs rather than from one incident ([trust-and-verification.md](trust-and-verification.md) Section 3).

### 4.5 Ambiguity is structural

Natural-language promises inherit the three-languages problem at scale: sharing a model or a protocol vocabulary does not guarantee shared meaning; "autonomous agents are never certain" (Burgess, arXiv:2604.10505). Ontologies don't fix this — they "trade expressibility for false precision" and need versioned calibration. Consequence for diagnosis: some "broken promises" are not fixable by better wording; they require negotiated co-languages, mutual assessment, and acceptance criteria written in the receiver's language.

### 4.6 Further limits (brief)

- **Assessment is gameable.** Burgess: "the manipulation of assessments remains the chief area for gaming and manipulating agents" (arXiv:2604.10505) — the principal exploit surface; harden every assessment mechanism adversarially.
- **Semantic promises are measurable, not enforceable.** "You can only enforce what you can specify"; accuracy, non-harm, and intent alignment can be measured, not guaranteed (M12 2026).
- **Trust is not transitive.** Belief is receiver-local; you cannot inherit trust through a chain, and every delegating layer must be assessed on its own evidence.
- **Machine Dunbar limits are unknown.** "We do not yet know the Dunbar limits for machine societies" (Burgess, arXiv:2604.10505); explicit verification budgets replace the natural human bound.

### 4.7 The honest position

Promise theory does not guarantee coordination; it makes the conditions for coordination — promise, acceptance, assessment, redundancy, renegotiation — visible and engineerable. Its classical determinism must be updated for stochastic agents, but its core axioms (autonomy, local knowledge, receiver-decides) are *more* true of LLM agents than of CFEngine hosts, not less: an LLM agent is genuinely non-coercible, genuinely locally-knowledged, and genuinely unpredictable. When the theory strains, the right move is measurement (P_succ) where you cannot enforce, enforcement where you can, and renegotiation when the promise set no longer matches reality.

## 5. Routing to sibling skills

- **Assessment layer** → [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md). Once you have classified a breach as verification-class, that skill supplies the machinery: task and trajectory contracts, datasets and graders, regression analysis, release gates, incident-to-case learning. Promise theory names *what* to assess; that skill supplies *how*.
- **Root-cause discipline** → [systematic-debugging](../systematic-debugging/SKILL.md). Promise theory names what to look for in coordination failures; systematic-debugging supplies the generic four-phase root-cause protocol for investigating any technical issue rigorously before fixing. Use the taxonomy here to form the hypothesis, and that discipline to verify it.
- **Evidence structure** → [artifact-pyramids](../artifact-pyramids/SKILL.md). When a diagnosis produces a body of evidence (traces, ledger entries, eval results), structure it as summaries → analysis → evidence dossiers so the diagnosis is auditable.
- **Recovery** → [patterns.md](patterns.md) for breach→renegotiation (pattern 5) and redundancy (pattern 6); [trust-and-verification.md](trust-and-verification.md) for recalibrating the trust estimate after a breach.

## 6. Sources

**Failure taxonomy and agent systems.** Cemri, Pan, Yang, et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025, arXiv:2503.13657 (fourteen modes, three classes). Zhu, Liu, Yu & Zhang, "LLM-Based Multi-Agent Orchestration: A Survey," *Future Internet* 18(6), 2026 (six-dimension framework; benchmark gap). Renney et al., "LLM-Enabled Multi-Agent Systems: Empirical Evaluation...," arXiv:2601.03328 (2026). Pan et al. (2025) on error propagation.

**Promise theory.** Bergstra & Burgess, *Promise Theory: Principles and Applications*, 2nd ed., χtAxis Press, 2019 (Defs 1–23; body, binding, assessment, withdrawal, promise drift). Burgess, "Cooperation in Human and Machine Agents: Promise Theory Considerations," arXiv:2604.10505 (2026). Burgess, "Authority (I): A Promise Theoretic Formalization," SSRN 3855352 (2021).

**Contracts and enforcement.** Ye & Tan, "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems," arXiv:2601.08815 (2026). M12/Todd Graham, "From Promises to Contracts: Enforceable Behavior in LLM Agents" (2026). Leoveanu-Condrei, "A DbC Inspired Neurosymbolic Layer for Trustworthy Agent Design," arXiv:2508.03665 (2025).

**Practice.** webframp, "The Promise None of Them Kept" (2026) (the admission rule; observation-first design). Full bibliographic details are in the mission research report; the repository standard is to cite the named work inline, as above.
