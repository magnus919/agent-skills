# Patterns — Seven Canonical Coordination Patterns with Worked Examples

**Load this file when you want to apply a named pattern** — promise manifest, acceptance handshake, agent contract (including the M12 "ladder from promise to contract" and the Ye & Tan formal lifecycle), evaluation loop, breach→renegotiation, redundancy & downstream responsibility, or trust calibration. Each pattern below states its promise-theory rationale, its concrete shape, a worked example you can adapt, and design guidance. The definitions and notation used here are in [foundations.md](foundations.md); the concept→practice mapping these patterns operationalize is in [agent-coordination.md](agent-coordination.md); trust calibration and verification budgets are developed in [trust-and-verification.md](trust-and-verification.md).

**Provenance.** Patterns 1, 2, 4, and 5 restate mechanisms directly documented in the cited sources (Burgess's promise machinery, CFEngine's convergence loop, agile renegotiation practice). Patterns 3, 6, and 7 synthesize promise theory with agent-engineering sources (M12 2026; Ye & Tan 2026; Leoveanu-Condrei 2025; Burgess & Dunbar 2025) and are marked `EXTRAPOLATION` where the synthesis goes beyond the cited texts. Unverified vendor or secondary claims are marked `[UNVERIFIED]`.

---

## 0. Pattern overview

| # | Pattern | Promise-theory principle honored | Use when |
|---|---|---|---|
| 1 | Promise manifest | Autonomy + local knowledge: cooperation starts with published offers | You need agents (or humans) to declare what they can and will do, before anything is dispatched |
| 2 | Acceptance handshake | Only the overlap of offer and acceptance transmits influence; the receiver decides | Every delegation that matters: record accept/refuse explicitly |
| 3 | Agent contract | A promise has no binding force; the contract adds enforcement and non-bypassability | The promise is consequential or the promiser is stochastic (an LLM) |
| 4 | Evaluation loop | Trust is accumulated assessment; accumulation needs a place to accumulate | You need to know whether promises are actually being kept, continuously |
| 5 | Breach → renegotiation | Breach is an information event, not a moral event; blame is a useless imposition | A promise was broken; the system must recover and re-converge |
| 6 | Redundancy & downstream responsibility | The downstream party carries greatest causal responsibility; plan for non-keeping | A promise is load-bearing (its failure takes the system down) |
| 7 | Trust calibration schedule | Two-component trust: calibrate potential trust, budget kinetic mistrust | You onboard new agents or need to decide how much to verify |

## 1. Pattern 1 — Promise manifest

**Rationale.** Autonomy plus local knowledge imply that cooperation starts with each agent *publishing what it can and will do* — its acceptance set, in Burgess's notation (the promises `+bi` an agent can make and `−bi` it can accept; Bergstra & Burgess 2019). A receiver can only rely on offers it can see.

**Shape.** A versioned, machine- and human-readable declaration per agent containing: capabilities (tools, skills, domains), constraints (what it will *not* do; resource limits), expectations (what it requires from others to keep its promises), and maintenance/withdrawal semantics (how promises are revoked — "I will stop handling X after date D"). Manifests exist in the wild as `AGENTS.md` (repository-scoped behaviour declarations), MCP tool descriptors and function schemas, worker-enrollment advertisements, and SLOs.

**Worked example — a 3-agent research team with human oversight.** Three agents and one human acceptors/evaluators.

- `research-agent` (literature summarizer): capabilities `lit-review` ("survey and summarize literature on X, limit 20 sources"), `evidence-tables` ("produce evidence tables with citations"). Constraint: "I will not fabricate citations; if I cannot verify a source I will mark it `[UNVERIFIED]`." Withdrawal: "I stop handling X when the coordinator withdraws direction."
- `reviewer`: capability `fact-check` ("verify claims against cited sources"), constraint "review only within my declared domain."
- `coordinator` (the human): commitment "provide research direction and review summaries by the agreed cadence."

The manifest is versioned (`v1`, `v2`, …); each version is a reviewable artifact, not prose. When the human adds a new expected capability, the manifest is revised and re-published *before* work starts — never silently appended mid-task. This is the promise-theory *admission rule*: "nothing lets the orchestrator reach a machine that never advertised the capability" (webframp 2026).

**Design guidance.** Declare less, promise more precisely; version manifests; make withdrawal explicit; treat the manifest as a contract surface for the acceptance handshake (pattern 2), not as documentation.

## 2. Pattern 2 — Acceptance handshake

**Rationale.** Only `b∩ = bi ∩ bj` transmits influence; the Downstream Principle says the receiver decides. A task that is never accepted is an imposition (Burgess, arXiv:2604.10505; Bergstra & Burgess 2019).

**Shape.** Every delegation has an explicit accept/refuse decision, recorded: explicit task acceptance by the executing agent; approval gates by humans; refusal signals (an agent says "out of scope" instead of hallucinating compliance); capability-matching before dispatch. Burgess's historical implementation was the Voluntary RPC (vRPC) — pull-based interaction "in which each side could completely control the conditions under which it interacted with the other."

**Worked example — guarded dispatch with refusal logging.** A coordinator proposes a task to `research-agent`: "Summarize these 20 papers by 17:00." The handshake has three recorded outcomes:

1. **Accept** — `research-agent` replies with a concrete re-promise: "I will deliver a summary with an evidence table, 20 sources max, by 17:00, provided the PDFs are accessible." The coordinator accepts *that* (the overlap `b∩` is now the binding promise).
2. **Refuse** — "Out of scope: this requires access to a paywalled database I am not enrolled for." The refusal is logged, not punished; the coordinator re-delegates or adjusts the manifest. **Refusal is a coordination signal**: a rising refusal rate means manifest/task mismatch, not a failing agent.
3. **Silence** — the worst case, because it is an *imposition that looks accepted*. The system treats a delegation with no recorded acceptance as not delegated, and surfaces it.

Human approval checkpoints (LangGraph breakpoints / HITL nodes) are the same pattern with a human acceptor: the agent proposes, the guard disposes, the human approves consequential steps (M12 2026).

**Design guidance.** Make refusal cheap and non-punitive for both humans and agents; log accept/refuse; measure the refusal rate as a coordination signal; treat silence as refusal-by-default.

## 3. Pattern 3 — Agent contract

**Rationale.** A promise has no binding force by itself. "A contract is a promise *plus* a mechanism that makes deviation either impossible or costly" (M12, "From Promises to Contracts," 2026). Promise theory supplies the acceptance half; the contract supplies the enforcement half. This pattern matters most for LLM agents, whose promises are "statements about intended future behavior with no binding force" that can be overridden by later context (prompt injection is the clean proof).

**Shape A — the M12 ladder from promise to contract.** The canonical spectrum of enforcement, from pure promise to hard guarantee:

1. **Soft prompting (pure promise)** — system prompts, constitutions. Steering only; no guarantee.
2. **Self-checking / reflection** — the model critiques itself; it shares the failure modes of what it checks (same blind spots, same randomness).
3. **Output validation / constrained decoding** — JSON schema, grammar constraints, type-checked tool arguments: a genuine contract on the *form* of output.
4. **External validators / action guards** — a separate deterministic process checks every proposed action against policy *before* execution.
5. **Capability restriction / sandboxing** — "don't ask the agent not to do the thing; remove its ability to do it": read-only mounts, no egress, microVM isolation, least-privilege identity. Converts "I promise I won't" into "the model cannot."
6. **Formal methods / typed effects** — provably bounded behaviour spaces; highest assurance, narrowest applicability.

The governing principle, stated at rung 5: **"confine, don't convince" — treat the model as an untrusted planner inside a sandbox of hard guarantees; "won't" becomes "can't."**

**Shape B — the formal tuple and lifecycle (Ye & Tan 2026).** Ye & Tan's Agent Contract is a 7-tuple `C = (I, O, S, R, T, Φ, Ψ)`: input spec; output spec with minimum quality threshold `Qmin`; skill set; multi-dimensional resource bounds (tokens, API calls, iterations, cost); temporal bounds; weighted success criteria; and termination conditions. Lifecycle:

```
DRAFTED → ACTIVE → {FULFILLED, VIOLATED, EXPIRED, TERMINATED}
```

with guard conditions such as `ACTIVE → VIOLATED` when any resource bound `ci ≥ bi` is exceeded. **Conservation laws**: delegated sub-contracts cannot exceed the parent's budget, enabling hierarchical, composable coordination. Empirically claimed by the authors (self-reported): 90% token reduction with 525× lower variance in iterative workflows, and zero conservation violations in delegation tests. `[UNVERIFIED]` independently.

**Shape C — degradation/exception semantics.** Because "guarantees are impossible, and it is the autonomous responsibility of the user to allow for that" (Burgess, arXiv:2604.10505), every contract names its exception behaviour *before* the breach:

- **Termination conditions** (`Ψ`): resource exhaustion, duration expiry, explicit cancellation, unrecoverable error. Every contract reaches exactly one terminal state — unambiguous resource release and audit.
- **Degradation tiers** (from Leoveanu-Condrei's Design-by-Contract for LLMs, 2025): verified → best-effort → safe default. Fail-open when liveness matters; fail-closed when safety matters. Name the tier in the contract. The telling compromise: a contract violation *degrades gracefully* (returns best-effort) rather than halting — preserving liveness at the cost of the guarantee.
- **Budget-aware behaviour**: injecting remaining budget into prompts, control tokens, satisficing instead of maximizing (Simon, via Ye & Tan 2026).
- **Runaway protection**: stop conditions, loop detection, cost ceilings — the operational controls that the $47,000 eleven-day recursive-clarification incident showed are missing when contracts are absent (Ye & Tan 2026, citing a Nov 2025 trade article; `[UNVERIFIED]` at primary-source level).

**Worked example — a coding agent with a workspace contract.** A coding agent is delegated "implement the retry logic in `src/retry.py`." The contract:

- **I**: input spec (repo path, function signature); **O**: output spec (diff against `src/`, must pass `pytest` and the repo's lint, `Qmin` = tests green); **S**: skills (`python`, repo conventions); **R**: resource bounds (≤ 200k tokens, ≤ 20 tool calls, ≤ 1h); **T**: temporal bound (due 17:00); **Φ**: weighted success criteria (correctness 0.6, style 0.2, test coverage 0.2); **Ψ**: terminate on budget exhaustion, on timeout, or on explicit cancel.
- The enforcement ladder is applied top-down: soft prompt states the boundary ("edit only `src/`"); the agent self-checks; an output validator enforces the diff scope; an action guard rejects file writes outside `src/`; the agent runs with a read-only mount on everything except `src/` (rung 5 — "won't becomes can't").
- **Degradation tier**: fail-closed. If `pytest` fails at the deadline, the contract enters VIOLATED, the partial diff is preserved, and the outcome is reported to the human acceptor rather than silently merged.
- **Lifecycle trace**: DRAFTED (contract written) → ACTIVE (accepted by the agent via the acceptance handshake) → FULFILLED (tests green, diff accepted) or VIOLATED (guard tripped / budget exhausted). **EXTRAPOLATION** — the full worked example is this skill's application of the cited formal machinery; the tuple, ladder, and lifecycle are from Ye & Tan (2026) and M12 (2026).

**Design guidance.** Specify contracts at the operational level where you can enforce; use measured promises (P_succ) at the semantic level where you cannot; give every handoff its own guard ("a chain of agents is only as bound as its least-enforced boundary"); make enforcement live *outside* the model.

## 4. Pattern 4 — Evaluation loop

**Rationale.** The promise-theory control loop (observe, reason locally, commit) plus assessment is what makes promises meaningful; trust is "accumulated assessment," and accumulation needs a place to accumulate (webframp 2026). CFEngine's convergence loop is the archetype: a continuous, iteratively safe map to a fixed point, not a one-shot push (see [applications-infrastructure.md](applications-infrastructure.md)).

**Shape.** Every agent relationship has an explicit evaluation loop: (1) define the accepted outcome (fixed point / acceptance criteria); (2) observe reality (agent observability: tool calls, reasoning, state, memory); (3) assess (evals, checks, human review); (4) act (repair, escalate, renegotiate, or record breach).

**Worked example — observation-first, with idempotency in the guard.** A configuration-coordination workflow observes live state rather than trusting last-write state: `discover_all` against live APIs → store versioned, schema-validated observations → diff reality-at-T vs. reality-at-T−1 → decide whether to act in a workflow → act only when warranted. Idempotency moves up from per-resource code to a workflow *guard* — a predicate ("has this already been done?") evaluated by the judgment layer, not re-implemented by every resource (webframp 2026). The promise-theory reading of why: a state file records "the one piece of evidence an agent assessing its own promise-keeping cannot use" — the agent's own last write — and push-based controllers "impose obligations and the target makes no promise."

**Assessments stored as versioned data.** The loop's output — each assessment ("promise `lit-review` KEPT on 2026-08-11 by human review", "promise `fact-check` BREACHED on 2026-08-12 by guard trip") — is written to a **promise ledger**: an append-only, queryable record of promises made (manifest versions), acceptances, assessments, breaches, renegotiations, and trust deltas, per agent and per relationship. The ledger is the coordination-layer counterpart of a trace store: traces capture *what happened*; the ledger captures *what was promised vs. what was kept*. CFEngine's documented gap is the warning: promise-keeping was never stored as data, so the evaluation loop was incomplete. **EXTRAPOLATION** — "promise ledger as a named artifact" is this skill's synthesis; the components (versioned assessments, trace stores, audit logs) are documented in the sources.

**Design guidance.** Make observation the primary operation, not an opt-in refresh; store assessments as versioned data with provenance; separate observation from action; treat idempotency as a decision, not a module-level implementation detail.

## 5. Pattern 5 — Breach → renegotiation, not blame

**Rationale.** "An autonomous agent cannot impose blame" (Burgess, arXiv:2604.10505 §VI-F); blaming an upstream provider "is a useless imposition and a waste of trust/energy." Breach is an information event that triggers reassessment — the retrospective, not the punishment.

**Shape.** On detected breach: (1) record it (trace → eval case; promise ledger entry); (2) assess the cause against the failure taxonomy (specification error vs. inter-agent conflict vs. verification gap — the three classes of Cemri et al. 2025); (3) renegotiate: update the prompt/contract/manifest, change acceptance criteria, add verification, or replace the provider; (4) adjust the trust estimate (down-rank P_succ; increase the verification rate); (5) apply redundancy if the dependency is load-bearing. Escalate only when renegotiation fails to converge.

**Named escalation trigger.** In this skill's contracts the escalation condition is named and written into the contract before any breach: **`ESCALATE-2`** — escalate to the human supervisor (or the next acceptance authority) when renegotiation fails to converge after two full renegotiation cycles, where a cycle is one breach → one contract revision → one verification window. After two non-converging cycles, further renegotiation is unbounded kinetic mistrust spent on a non-learning system; the evidence is reported instead. This follows the bounded-escalation completion discipline this skill applies to all diagnosis work.

**Worked example — the boundary-violating coding agent.** A coding agent repeatedly violates "touch nothing outside /workspace." Breach detected by the action guard (rung 4 of the ladder). Renegotiation options in order of increasing force:

1. **Clarify the contract** (soft): rewrite the boundary clause in the receiver's language.
2. **Add an output validator** (structural): reject diffs touching paths outside /workspace.
3. **Add an action guard** (external): deterministic pre-execution policy check.
4. **Move to a sandbox** (capability restriction): read-only mount on everything else — "won't" becomes "can't."
5. **Replace the agent** (redundancy): swap in an alternate provider.

Each is a renegotiation of the promise set, not a scolding. The breach is recorded in the ledger with its cause class (here: specification — the original boundary was stated in the system prompt but never enforced structurally). If the renegotiated contract (guard added) still breaches in the next verification window, and a second renegotiation cycle (sandbox) fails to converge, `ESCALATE-2` fires: the case goes to the human supervisor with the evidence trail, and the human decides sandbox hardening vs. provider replacement vs. task redesign.

**Design guidance.** Run retrospectives like agile teams do — a retro *is* renegotiation of the team's promise set; make the renegotiation trail visible; escalate only when renegotiation fails to converge; write the escalation trigger into the contract *before* the breach.

## 6. Pattern 6 — Redundancy & downstream responsibility

**Rationale.** Downstream Principle: "If a provider fails to keep a promise, the downstream agent only has its own policy to blame... It could or should have sourced more than one provider, planned for the promise not being kept, and sought out redundancy from multiple sources" (Burgess, arXiv:2604.10505). Composition of promises follows fault-dependency algebra: **parallel redundant sources give a dependent promise resilience; independent unique serial inputs make an aggregating promise fragile.**

**Shape.** For every load-bearing promise: multiple potential providers (alternate agents, alternate models, a human fallback), failover on breach, and an explicit plan for non-keeping. Redundant parallel sources make the system resilient; a promise that depends on a unique serial chain of inputs is a single point of failure.

**Worked example — the single-answer research pipeline.** A research pipeline must produce one answer. Fragile design: one agent run, one model, one shot. Resilient design: run two independent models on the same question, or one model plus a human reviewer, and require agreement before the answer is accepted (ensemble assessment). If the answer is load-bearing for a downstream decision, the consumer also keeps a human fallback ("if neither run converges by 16:00, the human produces the answer"). The classic LLM-engineering "verify with a second opinion / LLM-as-judge with checks" pattern is a redundancy pattern for *assessments*, not just for answers.

**Design guidance.** Identify load-bearing promises (failure takes the system down); give each at least one alternate provider; make failover a tested path, not a theory; treat unique serial inputs (a single upstream agent whose output feeds everything) as fragility to be broken up.

## 7. Pattern 7 — Trust calibration schedule

**Rationale.** Trust has two components — potential trustworthiness (accumulated assessment) and kinetic mistrust (the rate of checking). Verification is a sampling/energy problem: for inexpensive sampling, the checking rate can scale as a square root of trust, and agents budget verification against risk (Burgess & Dunbar 2025). "Mistrust is the prerequisite for learning" — you cannot learn reliability without checking.

**Shape.** Per-relationship verification schedule: new agents start at **50-50** (Burgess's default for agents that can't be assessed in advance: "often have no option but to start with a 50-50 guess about trustworthiness, which might be upgraded or downgraded later" — arXiv:2604.10505); high measured P_succ → cheap sampling; low P_succ or high risk → continuous monitoring + human review. Verification costs (tokens, human attention) are budgeted like any resource.

**Worked example — onboarding a new summarizer.** A new `research-agent` joins the team with no track record. Day 1: start at 50-50; verify every output — full human review of the first 10 deliverables (kinetic mistrust high, because risk is high: fabricated citations are costly). As the ledger accumulates 50 verified outputs with P_succ rising to 0.95, the schedule relaxes: sample 1-in-10 outputs with a rule-based citation check plus spot human review; escalate back to full review if a breach is detected (the trust estimate drops and the verification rate rises — the two move in opposite directions). The verification budget itself is declared: "≤ 2 human review hours/day on this agent, ≤ 5% of total token budget on evaluation." **EXTRAPOLATION** — the concrete schedule is this skill's synthesis of Burgess's 50-50 default, the square-root sampling model, and the Dunbar budget warning that machine fleets need explicit verification budgets because datacenter-hosted agents have "effectively limitless" surveillance capacity (arXiv:2604.10505).

**Design guidance.** Make the verification rate an explicit, adjustable parameter; tie it to risk appetite; measure the cost of assessment itself; state the starting trust level with its justification — a justified deviation from 50-50 (a stated prior with reasoning) is acceptable, an unstated one is not.

## 8. Choosing patterns and routing

- **Start with a promise manifest** (pattern 1) whenever you add agents to a workforce — it makes everything else possible.
- **Handshake before you delegate** (pattern 2): acceptance is the boundary between coordination and imposition.
- **Contract the consequential** (pattern 3): enforce what you can, measure what you cannot (see [trust-and-verification.md](trust-and-verification.md)).
- **Evaluate on a cadence** (pattern 4): the loop is what makes promises real.
- **Plan breach as a recovery path** (pattern 5) and **redundancy for what must survive** (pattern 6).
- **Calibrate trust deliberately** (pattern 7): the schedule is the operational face of the two-component model.
- **Designing a whole workflow as a chain of promises?** Route to [workflow-architect](../../workflow-architect/SKILL.md) — its guided workflow discovery and synthesis turn a sequence of phases, branching signals, and handoffs into a structured bundle; promise theory supplies the semantics of each handoff (offer → acceptance → assessment), workflow-architect supplies the workflow-building machinery. **EXTRAPOLATION** — the semantic mapping between the two skills is this skill's synthesis; both the promise model and the workflow-architect process are documented in their own sources.

Also relevant: [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md) for the assessment layer that pattern 4's loop calls on, and [artifact-pyramids](../artifact-pyramids/SKILL.md) for structuring the evidence the ledger accumulates.

## 9. Sources

**Promise theory.** Bergstra & Burgess, *Promise Theory: Principles and Applications*, 2nd ed., χtAxis Press, 2019. Burgess, "Cooperation in Human and Machine Agents: Promise Theory Considerations," arXiv:2604.10505 (2026). Burgess, "Notes on Trust as a Causal Basis for Social Science," SSRN 4252501 (2022). Burgess & Dunbar, "A quantitative model of trust...", *European Economic Review* (2025). Burgess, *In Search of Certainty*, O'Reilly, 2015.

**Agent contracts and enforcement.** Ye & Tan, "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems," arXiv:2601.08815 (2026). Leoveanu-Condrei, "A DbC Inspired Neurosymbolic Layer for Trustworthy Agent Design," arXiv:2508.03665 (2025). M12/Todd Graham, "From Promises to Contracts: Enforceable Behavior in LLM Agents" (2026). Cemri, Pan, Yang, et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025, arXiv:2503.13657.

**Practice.** webframp, "The Promise None of Them Kept" (2026). Zhu, Liu, Yu & Zhang, "LLM-Based Multi-Agent Orchestration: A Survey," *Future Internet* 18(6), 2026. Braintrust, "Agent observability: The complete guide for 2026." Full bibliographic details are in the mission research report; the repository standard is to cite the named work inline, as above.
