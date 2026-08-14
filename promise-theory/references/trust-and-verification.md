# Trust and Verification — The Two-Component Model in Practice

**Load this file when you need to decide how much to verify an agent, set a starting trust level, budget verification cost, or wire assessment into evals and observability.** This file develops the skill's trust model — two-component trust (potential trustworthiness + kinetic mistrust), belief/evidence, the measured promise P_succ, verification rates as an attention budget (including Dunbar budgets), gameable assessment, and measurement guidance for semantic promises — and connects it to the assessment layer. The formal definitions (assessment α, belief β, evidence ε, trust as discounting δ) are in [foundations.md](foundations.md); the trust calibration schedule as a named pattern is in [patterns.md](patterns.md); the concept mapping that motivates all of this is in [agent-coordination.md](agent-coordination.md).

**Provenance.** The two-component model, the 50-50 default, and the Dunbar-budget discussion are Burgess's (arXiv:2604.10505, 2026; SSRN 4252501, 2022; Burgess & Dunbar 2025). The measured promise P_succ and bounded remediation are Leoveanu-Condrei's Design-by-Contract for LLMs (arXiv:2508.03665, 2025). The connection of all of this to agent evals and observability practice is this skill's synthesis and is labeled `EXTRAPOLATION` where it goes beyond the cited texts. Claims resting on vendor or secondary accounts are marked `[UNVERIFIED]`.

---

## 1. The two-component trust model

Burgess's model separates trust into two components that move independently and are almost always conflated:

1. **Potential trustworthiness** — the receiver's *accumulated estimate* that the promiser will keep its word: `V_S = α_R(π_S)` — the assessment value α that receiver R has built up about promiser S from the promise record π (Burgess, SSRN 4252501; arXiv:2604.10505). This is a *stock*: it changes slowly, with evidence.
2. **Kinetic mistrust** — the *rate* at which the receiver checks on the promiser: how often you run evals, ping health checks, re-audit outputs, or re-review work. This is a *flow*: attention and energy spent in the present.

The two are not opposites. **High potential trust + low kinetic mistrust** = a well-calibrated relationship. **Low potential trust + low kinetic mistrust** = recklessness ("if you trust something too much, you're not paying attention" — Burgess). The industry phrase "zero trust" correctly refers to the *second* component — pay attention continuously — not to eliminating reliance, which would be impossible: "you have to trust technology if it's going to take over the job of mistrusting or monitoring something else. So you don't escape trust. It's trust all the way down" (NLnet/NGI interview, 2024). Every delegating layer — human to orchestrator, orchestrator to agent, agent to tool — must itself be assessed.

Burgess & Dunbar (2025) model kinetic mistrust as an *energy/attention budget*: human groups are bounded by cognitive trust budgets (Dunbar-scale limits on how many relationships any individual can meaningfully maintain and verify). For machine societies the budget is inverted — "there is no upper limit on the amount of energy an artificial autonomous system may choose to invest in surveillance of its neighbours" (arXiv:2604.10505) — which is precisely why agent fleets need *explicit* verification budgets: the constraint is no longer natural, so it must be imposed by governance. **EXTRAPOLATION** — the design rule "budget verification explicitly because machine surveillance is effectively limitless" is this skill's synthesis; the limitless-capacity observation and the Dunbar model are Burgess & Dunbar's.

## 2. Belief and evidence

Promise theory's epistemic vocabulary: an agent holds **belief β** about whether a promise will be kept, based on **evidence ε** gathered through **assessment α** — where assessment is *relativistic*: it is always from a particular receiver's vantage point, never a global verdict (Bergstra & Burgess 2019). Three consequences for agent coordination:

- **Assessment is local to the receiver.** A controller's aggregate metric is not the receiver's assessment. This is why "the service returned 200" can wrap a confidently wrong answer, and why an agent that loops can look healthy from the controller's vantage point: the receiver's signal is what matters, and a source is "only as good as its signal can be heard downstream" (Burgess).
- **Trust is not transitive.** Because belief is receiver-local, you cannot inherit trust through a chain: every delegating layer must be assessed on its own evidence. "Trust all the way down."
- **Belief updates on evidence, not on confidence.** An agent's self-prediction is a poor predictor of its own future outputs (there is no causal mechanism connecting the acknowledgment to the compliance — M12 2026). Calibrate belief from *observed outcomes*, never from the promiser's fluency.

## 3. The measured promise: P_succ

A **measured promise** is a commitment whose satisfaction is *estimated* rather than assumed — the bridge between an ungoverned natural-language promise and a hard guarantee. Leoveanu-Condrei's Design-by-Contract for LLMs (arXiv:2508.03665, 2025) lifts the Hoare triple `{P}C{Q}` into the probabilistic domain: pre/post-condition predicates on typed inputs and outputs, a bounded remediation loop (a validation error becomes a corrective prompt; failure history accumulates in context to prevent re-looping), and a **measured success probability P_succ** estimated over repeated runs.

P_succ is the operational face of potential trust: it is what makes two agents that satisfy the same contract interchangeable except for their P_succ and cost. Practical implications:

- **Estimate it empirically, per contract.** One run proves nothing for a stochastic promiser; P_succ is a statistic over a recorded sample of assessed outcomes.
- **Update it from the ledger.** Each kept or breached promise (see Section 8) is an evidence point; the estimate moves with the record, not with the model's self-report.
- **Use it where you cannot enforce.** At the semantic level ("the summary is accurate") you cannot build a hard guarantee; P_succ is the honest substitute. At the operational level, enforce instead (Section 7).
- **Bound the remediation loop.** The Design-by-Contract remediation is *bounded* — failure history accumulates to prevent re-looping, and contract violation *degrades gracefully* (fail-open to best-effort) rather than halting, preserving liveness at the cost of the guarantee.

**EXTRAPOLATION** — "P_succ as the tradable unit of potential trust, and the ledger as its evidence base" is this skill's synthesis of Leoveanu-Condrei's measured promise with Burgess's `V_S = α_R(π_S)`; each half is documented in its own source.

## 4. Verification rates as an attention budget

The rate at which you check is kinetic mistrust, and it is spent attention. Burgess models verification as a sampling/energy problem: for inexpensive sampling verification, the checking rate can scale as the square root of trust — the more trust has accumulated, the cheaper the sampling can be (Burgess & Dunbar 2025). Calibration guidance:

- **Start unknown agents at 50-50.** Agents "often have no option but to start with a 50-50 guess about trustworthiness, which might be upgraded or downgraded later" (arXiv:2604.10505). A justified deviation (a stated prior with reasoning) is acceptable; an unstated one is not.
- **Verify proportional to risk, inversely to measured trust.** High P_succ + low stakes → cheap sampling; low P_succ or high stakes → continuous monitoring and human review. When a breach drops the estimate, the verification rate rises — the two components move in opposite directions.
- **Budget the verification cost explicitly.** For machine fleets the natural bound is absent (Section 1), so the budget is a governance artifact: tokens spent on evaluation, human review hours, eval runs per release. Without a declared budget, verification expands without limit or collapses without notice — and humans, whose attention is Dunbar-bounded, get alert fatigue and start rubber-stamping.
- **Respect the human budget.** Wikipedia edit wars taught Burgess that conflict consumes attention; Dunbar-scale trust budgets bound human tolerance (NLnet interview, 2024). Agent fleets must not impose unbounded human monitoring loads.

**"Mistrust is the prerequisite for learning."** You cannot learn whether a promise is being kept without checking; every verified outcome is the evidence that updates belief. A system that stops checking — out of complacency ("high trust, why bother") or exhaustion — stops learning, and its trust estimate silently decays into an assumption.

## 5. Trust calibration in practice

The trust calibration schedule (pattern 7 of [patterns.md](patterns.md)) operationalizes this: onboarding an agent starts at 50-50 with full verification; the verification rate relaxes as the ledger accumulates assessed outcomes and P_succ rises; any breach drops the estimate and raises the rate. The schedule is itself a promise: "I will verify X at rate Y" is the supervisor's promise to the organization, and the organization accepts it. Trust decisions should be *written down as data* — the starting level, the evidence, the adjustment — never left as an unstated vibe. The three most common calibration errors are: starting from trust instead of 50-50; letting the verification rate track the *promiser's* confidence instead of the *assessed* record; and failing to price the assessment itself (Section 6).

## 6. Gameable assessment — the principal exploit area

Burgess's warning is blunt: "the manipulation of assessments remains the chief area for gaming and manipulating agents" (arXiv:2604.10505). Assessment is the load-bearing concept of the whole theory — "the principal area for exploiting and misdirecting agents" — which makes it the principal attack surface. Concrete failure modes, all documented in the agent-engineering record:

- **LLM-as-judge can be fooled** — rating indeterminacy research shows evaluator models are susceptible to phrasing, ordering, and sycophancy effects; the judge is itself an assessor that can be gamed.
- **Goodhart dynamics** — agents optimize for the eval score rather than the underlying promise; if the eval is the acceptance criterion, the eval becomes the target.
- **Eval contamination and staleness** — benchmark figures go stale quickly and can be memorized; vendor-reported adoption numbers dominate (independent replications are essentially absent, `[UNVERIFIED]` by nature of the gap).
- **Assessment capture** — an agent that controls the evidence stream (its own traces, its own self-reports) controls the record its P_succ is computed from. This is why assessments must be stored as versioned data by an independent mechanism (Section 8), and why guardrails must be *outside* the model (the "confine, don't convince" principle, Section 7).

**Design guidance.** Treat every assessment mechanism as a target: use diverse, independent verifiers (deterministic checks + human review + a judge model, cross-checked); keep the eval cases out of the training distribution where possible; monitor the assessment mechanism itself for drift; and harden trust metrics adversarially. **EXTRAPOLATION** — the "assessment as attack surface" framing is this skill's synthesis; the underlying observation is Burgess's, and the failure modes are documented in the cited agent-engineering sources.

## 7. Measurement guidance for semantic promises

Promise theory's honest limit: **semantic promises can only be measured, not enforced.** "You can only enforce what you can specify" (M12 2026). Two promise classes:

- **Operational class** (format, scope, sandbox, network): enforceable. A diff scope can be rejected; a file system can be read-only; a network egress can be blocked. "The intersection of explicit framing + hard guarantee on semantic commitments is empty" — semantic commitments are *not* enforceable by framing alone.
- **Semantic class** (accuracy, non-harm, intent alignment): measurable, not enforceable. "The summary is accurate" cannot yet be cheaply enforced; it can only be assessed — by checks, by judges, by human review.

The governing principle that turns measurement into control is **"confine, don't convince"**: don't ask the model not to do the thing; remove its ability to do it. "Won't" becomes "can't." This is the difference between a *promise* (a declaration of intent, always breakable) and a *constraint* (a structural fact of the environment, not breakable by intent). The measurement guidance in one line: **enforce the operational, measure the semantic, and never mistake a measurement for an enforcement** — a P_succ of 0.97 on semantic promises is an honest estimate, not a guarantee, and the downstream design (redundancy, renegotiation, escalation) must assume the 3% happens.

## 8. Assessments stored as versioned data — the promise ledger

Trust is accumulated assessment, and **accumulation needs somewhere to accumulate** (webframp 2026). CFEngine's documented gap is the negative example: promise-keeping was never stored as data in the reference implementation, so the evaluation loop was incomplete (see [applications-infrastructure.md](applications-infrastructure.md)). The fix is a **promise ledger**: an append-only, versioned, queryable record of promises made (manifest versions), acceptances, assessments (eval scores, review outcomes, who assessed and when, against what observation), breaches, renegotiations, and trust deltas — per agent and per relationship.

Ledger hygiene rules:

- **Versioned, not overwritten.** An assessment is an evidence point; rewriting it destroys the record that belief updates depend on. Assessments are data with provenance (who assessed, when, against what criterion).
- **Append-only and independently writable.** The mechanism that writes assessments must not be the agent being assessed — otherwise assessment capture (Section 6) is structural.
- **Legible as evidence.** Each entry supports a later question: "was promise X kept, and how do we know?" This is what makes causal responsibility auditable (Section 3.3 of [agent-coordination.md](agent-coordination.md)): the audit trail is the promise ledger.

**Structuring the evidence.** When the ledger accumulates, organize its contents as multi-layer research artifacts: [artifact-pyramids](../artifact-pyramids/SKILL.md) provides the canonical structure for promise-keeping evidence as **summaries → analysis → evidence dossiers** — the summary layer for decisions, the analysis layer for interpretation, the evidence layer for the raw assessed records. Route evidence-heavy coordination work there when the record grows beyond a single relationship. **EXTRAPOLATION** — the ledger structure is this skill's synthesis of the accumulation principle (webframp) with the promise-keeping-as-data lesson (CFEngine); the artifact-pyramid structure is that skill's own methodology.

## 9. Wiring assessment into evals and observability

Promise theory's core operational claim — **assessment is what makes coordination possible, and its cost and rate are first-order design variables** — is exactly what the agent-engineering industry has built as the assessment layer. The wiring:

- **An eval is a formalized acceptance promise**: a stated criterion by which a receiver will decide a promise is kept. Offline evals (benchmarks, golden sets) assess against a fixed corpus; online evals score production traces. Production failures convert into eval cases; CI gates block merges that degrade quality — institutionalized assessment: no acceptance without evaluation.
- **Observability is the assessment record.** Agent traces (tool calls, reasoning, state transitions, memory operations — the four trace pillars) are precisely the record a downstream observer needs to decide whether a promise was kept. Multi-agent handoffs get logged at every boundary, the same way you would log an RPC between two services.
- **Guardrails are automated acceptance.** An action guard is an imposition (an agent action) landing only against a matching acceptance (policy allows it); sandboxing makes breach impossible ("won't" → "can't", Section 7).
- **The trace-to-eval loop is trust accumulation in production**: every assessed outcome updates the empirical reliability record — the ledger (Section 8) is the memory, the eval loop is the learning rate.

**Routing statement:** for designing, running, and reviewing the assessment layer itself — evals, datasets, graders, trajectory review, regression analysis, release gates, production traces — route to **[agent-evals-and-observability](../agent-evals-and-observability/SKILL.md)**: promise theory supplies *what* to assess (whether a promise was kept, at what rate, at what cost); that skill supplies *how* — task and trajectory contracts, dataset and grader design, statistical comparison of runs, incident-to-case learning. **EXTRAPOLATION** — the identity "traces = assessment records; evals = formalized acceptance criteria; guardrails = automated acceptance" is this skill's synthesis; each half is documented in its own source line (Burgess's assessment machinery; the observability/evals literature cited below).

## 10. Sources

**Trust model.** Burgess, "Notes on Trust as a Causal Basis for Social Science," SSRN 4252501 (2022). Burgess & Dunbar, "A quantitative model of trust as a predictor of social group sizes and its implications for technology," *European Economic Review* (2025). Burgess, "Cooperation in Human and Machine Agents: Promise Theory Considerations," arXiv:2604.10505 (2026). NLnet/NGI Assure interview with Burgess, "Promise Theory," 2024.

**Formal model.** Bergstra & Burgess, *Promise Theory: Principles and Applications*, 2nd ed., χtAxis Press, 2019.

**Measured promises and enforcement.** Leoveanu-Condrei, "A DbC Inspired Neurosymbolic Layer for Trustworthy Agent Design," arXiv:2508.03665 (2025). M12/Todd Graham, "From Promises to Contracts: Enforceable Behavior in LLM Agents" (2026). Ye & Tan, "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems," arXiv:2601.08815 (2026).

**Assessment practice.** Braintrust, "Agent observability: The complete guide for 2026." Langfuse, "AI Agent Observability, Tracing & Evaluation" (2024–2026). Confident AI, "Top 8 AI Agent Observability Platforms for 2026." Zhu, Liu, Yu & Zhang, "LLM-Based Multi-Agent Orchestration: A Survey," *Future Internet* 18(6), 2026. Cemri et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025, arXiv:2503.13657. webframp, "The Promise None of Them Kept" (2026). Full bibliographic details are in the mission research report; the repository standard is to cite the named work inline, as above.
