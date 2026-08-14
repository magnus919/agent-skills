# Patterns — Ten Named SST Patterns for Design and Diagnosis

**Load this file when you need to apply a named pattern** — semantic anchor, semantic trajectory, convergence loop, promise propagation, drift detection, absorbing-state detection, shared semantic manifold, γ(3,4) modeling, semantic distance/divergence metrics, or reconciliation. Each pattern states its when-to-use condition as an observable trigger, its anti-pattern as a concrete misuse, and its SST grounding.

**What belongs here:** the ten patterns as reusable, named design moves, with when-to-use triggers and anti-patterns. What does **not** belong here: the formal definitions behind the patterns (see [foundations.md](foundations.md)); the empirical record of the infrastructure and agentic-AI lines (see [applications-infrastructure.md](applications-infrastructure.md) and [agent-coordination.md](agent-coordination.md)); the bounded diagnosis procedure (see [diagnosis-and-debugging.md](diagnosis-and-debugging.md)). Promise-level machinery (offer/acceptance, assessment, breach, trust calibration) is linked to [promise-theory](../../promise-theory/SKILL.md), never re-taught here.

**Provenance.** `[VERIFIED]` = confirmed in a fetched primary source; `[UNVERIFIED]` = secondary/inferred; `EXTRAPOLATION` = this skill's synthesis, labeled. Patterns grounded in verified research are marked; the pattern *shapes* themselves (when-to-use/anti-pattern framing) are this skill's original synthesis [EXTRAPOLATION] unless a source is named.

---

## 0. Pattern overview

| # | Pattern | Use when (one line) | Key anti-pattern |
|---|---|---|---|
| 1 | Semantic anchor | A term or promise needs a stable, versioned meaning reference | Freezing the anchor forever; anchoring to an internal embedding |
| 2 | Semantic trajectory | You need to record where an agent's meaning is going over time | Treating snapshots as the whole story; no time axis |
| 3 | Convergence loop | State must be measured against a desired meaning and repaired | Confusing convergence with idempotence; expecting exactness |
| 4 | Promise propagation | Delegation chains carry commitments between agents | Modeling promises without acceptance; long unverified chains |
| 5 | Drift detection | Meaning quietly changes between two snapshots or agents | Thresholding on one snapshot; ignoring scale |
| 6 | Absorbing-state detection | Agents dead-end, hallucinate, or stop learning | Treating the symptom as the cause; no boundary injection |
| 7 | Shared semantic manifold | Agents must coordinate on what relations mean | Building a manifold without causality; expecting identical projections |
| 8 | γ(3,4) modeling | You need to type the semantic graph (events/things/concepts × 4 links) | Inventing extra link types; ontology-first modeling |
| 9 | Semantic distance/divergence metrics | You need a number for "how far apart" two meanings are | Using raw coordinate distance as semantic distance |
| 10 | Reconciliation | Two divergent meanings must be brought back into agreement | Forcing agreement by fiat; no acceptance on both sides |

## 1. Semantic anchor

**When to use:** use when you observe that a term, promise, or instruction keeps being interpreted differently by different agents (or by the same agent at different times), and you need a stable reference point against which interpretations can be compared. The observable trigger is a measurable disagreement that re-occurs despite repeated explanation.

**Shape:** a versioned, addressable statement of what a concept or promise *means* in this system — the intended interpretation, its boundaries (what it does not cover), and its revision history. In SST terms the anchor is a concept node with typed edges to the things and events it is anchored to (γ(3,4) typing rule: concepts become realized by anchoring to things or events [VERIFIED — arXiv:2506.07756]); its revision history is the record axis of [applications-infrastructure.md](applications-infrastructure.md) §8.

**Anti-patterns:** freezing the anchor — a semantic anchor that can never be revised becomes a lie as the system changes (knowledge decays geometrically when unconfirmed; [VERIFIED — arXiv:1608.02193, Lemma 1, via foundations.md §9]). Anchoring to an agent's internal embedding rather than to an observable, shared statement — embeddings are "interior spaces" with "inscrutable property models" [VERIFIED — arXiv:2506.07756]. Anchoring to prose that no one versioned — the GitOps lesson is that the contract must be versioned desired state [VERIFIED — CNCF, GitOps 101].

## 2. Semantic trajectory

**When to use:** use when you need to know where an agent's (or a system's) meaning is going over time — whether understanding is converging, drifting, or diverging — and when the artifact you need is a recorded path, not a single snapshot. Trigger: the question "how did we get from interpretation A to interpretation B?" is answerable only from a series of observations, not from the current state.

**Shape:** a sequence of {position, intent (promise), time} observations — each local change is a unit of proper time for the element concerned [VERIFIED — arXiv:1608.02193, Def. 2, via foundations.md]. Record the trajectory as observations in the skill's model format (see [templates/sst-model.yaml.tmpl](../templates/sst-model.yaml.tmpl)); compute displacement (drift), inter-agent separation (divergence), and approach-to-fixed-point (convergence) from it.

**Anti-patterns:** treating snapshots as the whole story — a single state cannot show drift, because drift is a time-indexed quantity [EXTRAPOLATION — grounded in the definitions of drift in arXiv:2601.04170]. Recording trajectories without a time axis or causal order — wall-clock-less, causality-less traces cannot answer "what can affect what" [VERIFIED — Lamport 1978, via applications-infrastructure §4]. Confusing the agent's reported trajectory with its actual trajectory — the record axis and the world axis must stay separate [VERIFIED — Temporal database Wikipedia, via applications-infrastructure §4].

## 3. Convergence loop

**When to use:** use when you need a system that continuously measures its current state against a desired meaning and repairs toward it — the SST form of a control loop. Trigger: you can state a desired end-state as an observable condition, and you expect the environment to perturb state unpredictably over time.

**Shape:** a loop that (1) measures the current state, (2) compares against the promised state, (3) acts to repair divergence, (4) repeats. This is CFEngine's fixed-point machinery — a convergent operator satisfies `O(q0) = q0` with `O^2 = O`, "like a ball rolling into a potential well" [VERIFIED — Burgess, *A Tiny Overview of CFEngine*] — and MAPE-K's monitor → analyze → plan → execute [VERIFIED — Kephart & Chess 2003]. It is also the drift literature's bounded-equilibrium finding: turn-wise divergence evolves "as a bounded stochastic process with restoring forces" [VERIFIED — arXiv:2510.07777]. For the promise-level convergence mechanics (offer/acceptance and assessment inside the loop), link to [promise-theory](../../promise-theory/references/patterns.md) rather than re-deriving them.

**Anti-patterns:** confusing convergence with idempotence — idempotence requires only O²=O, convergence is relative to a specific policy state q0 [VERIFIED — *A Tiny Overview*]. Expecting exactness — convergence is statistical, never exact, in a stochastic environment: "a complete specification of policy determines an approximate configuration… only approximately over persistent times" [VERIFIED — *A Tiny Overview*]. A loop with no measurement plan — "dynamics always trumps semantics"; without measurement at the right scale, the loop is guessing [VERIFIED — InfoQ, *In Search of Certainty*].

## 4. Promise propagation

**When to use:** use when commitments travel through chains — an orchestrator delegates to a subagent, which delegates further, or a promise must transit intermediate agents — and you need to model how intent propagates and where it attenuates. Trigger: a delegation chain of length ≥ 2, or a promise whose meaning depends on intermediate reinterpretation.

**Shape:** model each delegation as an offer (+b) and acceptance (−b) with overlap `b∩` — the effective propagated content is the overlap, not the full offer [VERIFIED — arXiv:2604.10505]; the Downstream Principle makes the accepting agent responsible for its own use [VERIFIED — same source]. Cost model: fully-promised delivery through N intermediaries costs O(N²); at minimal trust the promise graph must be complete [VERIFIED — same source]. Trace the trajectory of the promise through semantic spacetime and check where the overlap shrinks (each non-unitary translation "agents should expect to misunderstand one another's intentions to some level" [VERIFIED — arXiv:2604.10505]).

**Anti-patterns:** modeling promises without acceptance — a dispatched task with no recorded acceptance is an imposition that looks accepted (the silence-as-acceptance trap) [EXTRAPOLATION — grounded in arXiv:2604.10505 offer/acceptance semantics and promise-theory's acceptance handshake pattern in [promise-theory/references/patterns.md](../../promise-theory/references/patterns.md)]. Long unverified chains — trusting the chain head instead of verifying per hop, which the O(N²) result and handoff-context-loss failures warn against [VERIFIED — arXiv:2604.10505; the handoff-loss reading is this skill's synthesis]. An agent promising on behalf of another — the tenet "no agent may promise anything on behalf of any agent but itself" [VERIFIED — arXiv:2604.10505].

## 5. Drift detection

**When to use:** use when meaning may be changing between snapshots, between agents, or between instruction and implementation, and you need to notice it early. Trigger: you have two or more observations of the same semantic state (or the same promise) at different times or from different agents, and you need a decision rule for "they no longer mean the same thing."

**Shape:** compute a divergence metric between the observations (see Pattern 9), threshold it against a risk budget, and alert. The empirical metrics to draw on: the Context Divergence Score over spatial/temporal/task dimensions [VERIFIED — arXiv:2606.21666]; the Agent Stability Index over twelve dimensions [VERIFIED — arXiv:2601.04170]; turn-wise KL divergence with restoring forces [VERIFIED — arXiv:2510.07777]. The SST framing: drift is displacement from the promised trajectory; the three-trajectory version (instruction, implementation, reality) is Pattern 5's strongest form and is developed in [diagnosis-and-debugging.md](diagnosis-and-debugging.md) and [agent-coordination.md](agent-coordination.md) §8.5.

**Anti-patterns:** thresholding on a single snapshot — drift is a time-indexed quantity; one measurement cannot detect it [EXTRAPOLATION]. Ignoring scale — different scales yield contradictory conclusions; "the ability to distinguish and separate scales is closely allied with our notions of simplicity" [VERIFIED — InfoQ, *In Search of Certainty*]. Full-broadcast "sync" as a fix — naive full-broadcast synchronization *increases* hallucination by 34%; selective sync reduces it [VERIFIED — arXiv:2606.21666].

## 6. Absorbing-state detection

**When to use:** use when agents or systems dead-end — repeat the same failure, hallucinate, stop learning, or stop responding to new information — and you need to recognize the dead-end as a structural property rather than a one-off bug. Trigger: the same divergent outcome recurs despite intervention, or information stops propagating from some node.

**Shape:** identify the absorbing state in the γ(3,4) graph: "the ubiquitous appearance of absorbing states in any partial graph means that certain graph processes leak information and represent entropy changing processes"; absorbing states erase interior information and "can only be replaced with new boundary data from outside the graph, such as outside policy choices"; this is "closely associated with the issue of division by zero, which signals a loss of closure and the need for manual injection of remedial information" — "boundary information where intentionality can enter" [VERIFIED — arXiv:2506.07756]. The SST remedy is boundary injection: a new promise, a human input, or outside policy data, not more iterations of the same loop [VERIFIED — same source]. See [foundations.md](foundations.md) §3 for the formal treatment.

**Anti-patterns:** treating the symptom as the cause — e.g., "more context" for a task that has collapsed into an absorbing state where no amount of interior information helps [EXTRAPOLATION — grounded in the absorbing-states doctrine]. Never injecting boundary data — an absorbing state "can only be replaced with new boundary data from outside the graph" [VERIFIED — arXiv:2506.07756]. Confusing an absorbing state with convergence — an absorbing state is a leak (entropy-increasing); a convergent fixed point is a desired attractor [VERIFIED — arXiv:2506.07756; *A Tiny Overview*].

## 7. Shared semantic manifold

**When to use:** use when multiple agents must coordinate on what relations mean — when "near", "causes", "contains", and "expresses" must mean the same thing to every participant — and raw token contexts or opaque agent cards are insufficient. Trigger: you observe coordination failures that trace to relation-type ambiguity ("we disagreed about whether X causes Y or merely correlates with Y").

**Shape:** a shared γ(3,4)-structured representation (typed nodes and links) that each agent projects onto, with its own interior state kept separate; coordination happens by comparing projections. This is the coordination-substrate synthesis of [agent-coordination.md](agent-coordination.md) §8.1, grounded in the intentionality-preservation claim — "graphs preserve the intentionality of the source even under data fractionation" [VERIFIED — arXiv:2512.19084] — and the Tolman-Eichenbaum finding that spatial and relational memory share machinery [VERIFIED — Whittington et al., Cell 2020].

**Anti-patterns:** building the manifold without causal-temporal structure — an undirected similarity space has no "leads-to" and cannot express the relation-type ambiguity that matters [EXTRAPOLATION — grounded in the four γ(3,4) link types]. Expecting identical projections — each agent is autonomous with local knowledge; the manifold coordinates *overlaps*, not identities [VERIFIED — arXiv:2604.10505 autonomy + local knowledge; the overlap framing is the paper's b∩]. Replacing the manifold with a giant shared context — full-broadcast context sharing increases hallucination [VERIFIED — arXiv:2606.21666].

## 8. γ(3,4) modeling

**When to use:** use when you need to type a semantic graph — to classify nodes as events (timelike process agents), things (spacelike snapshot agents), or concepts (virtual role/intention agents), and links as 0 = NEAR, ±1 = LEADS TO, ±2 = CONTAINS, ±3 = EXPRESSES [VERIFIED — arXiv:2506.07756]. Trigger: you have a knowledge or coordination graph and you need a principled, ontology-free typing of what each edge claims.

**Shape:** apply the nine typing design rules (things may be contained but not expressed; concepts may be expressed but not contained; concepts become realized by anchoring to things or events; verbs are dangling concepts without subject/object; a realized state of being is an event; an unrealized state of being is a concept; a realized type of thing is a thing; an unrealized type of thing is a concept) [VERIFIED — arXiv:2506.07756 §2.3]. **The formal definition belongs to [foundations.md](foundations.md) §2 — load it before applying this pattern.** Note the honest limit: the claim that four link types suffice "remains a hypothesis for now" [VERIFIED — arXiv:2506.07756].

**Anti-patterns:** inventing extra link types — the four types (0, ±1, ±2, ±3) are the γ(3,4) contract; adding ad-hoc edge semantics re-introduces the ontology tax the formalism avoids [EXTRAPOLATION — grounded in the "four basic arrows… sufficient" hypothesis and the anti-ontology framing of arXiv:2506.07756]. Ontology-first modeling — "ontologies do not employ principles rooted in the processes of the world"; SST "is not a taxonomy or an ontology" [VERIFIED — arXiv:2506.07756]. Using vector similarity as the edge semantics — vectors are for probabilistic estimation; graphs preserve intentionality [VERIFIED — arXiv:2512.19084].

## 9. Semantic distance/divergence metrics

**When to use:** use when you need a number for "how far apart" two meanings are — for routing, delegation, drift alerting, or reconciliation priority. Trigger: you must decide between two interpretations, two agents, or two snapshots based on how close they are semantically.

**Shape:** distinguish **metric distance** ("a measure of coordinate-similarity in position") from **semantic distance** ("a measure of similarity in interpretation") [VERIFIED — arXiv:1608.02193, Definitions 8–9, via foundations.md §8]. Semantic distance instances include Hamming distance, hop counts in an associative network, semantic hashing, and sparse distributed representations [VERIFIED — same source]. On a γ(3,4) graph, a weighted hop count over typed links is a semantic-distance instance — weight by link type (causal links farther than similarity links, etc.) [EXTRAPOLATION — the weighting scheme is this skill's design; the hop-count family is verified]. The empirical drift metrics (CDS, ASI, KL) are divergence instances to reuse [VERIFIED — arXiv:2606.21666, 2601.04170, 2510.07777].

**Anti-patterns:** using raw coordinate distance as semantic distance — "two concepts can be close in coordinates yet far in interpretation, and vice versa" [VERIFIED — arXiv:1608.02193, via foundations.md §8]. Unweighted hop counts that treat a causal edge like a similarity edge [EXTRAPOLATION]. Declaring a divergence metric without a measurement plan — metrics without observations at the right scale are ungrounded ("dynamics always trumps semantics") [VERIFIED — InfoQ, *In Search of Certainty*].

## 10. Reconciliation

**When to use:** use when two divergent meanings must be brought back into agreement — after drift detection, after a breached promise, or after a merge of two agent teams' interpretations. Trigger: you have identified pairwise semantic distance above a threshold and you need a bounded process to close it.

**Shape:** a bounded negotiation: (1) expose each side's interpretation as a projection onto the shared manifold (Pattern 7); (2) identify the overlap `b∩` that already exists and the disagreement region [VERIFIED — arXiv:2604.10505 offer/acceptance overlap]; (3) expand the co-language — "agents may have to talk their way to a calibration of meaning" [VERIFIED — arXiv:2604.10505, three-languages framing]; (4) re-anchor the shared terms (Pattern 1) and re-record them as versioned data (the record axis of applications-infrastructure §8); (5) verify by re-measuring the divergence after the reconciliation. The drift literature's empirical anchor: reminder interventions reliably reduce divergence [VERIFIED — arXiv:2510.07777].

**Anti-patterns:** forcing agreement by fiat — an imposition "without the receiver's promise" is generally ineffective and looks accepted without being so [VERIFIED — arXiv:2604.10505]. No acceptance on both sides — reconciliation without both sides' acceptance is not convergence, it is coercion [EXTRAPOLATION — grounded in the offer/acceptance machinery]. Reconciling once and never re-checking — knowledge decays without confirmation; reconciliation must be re-measured [VERIFIED — arXiv:1608.02193, Lemma 1, via foundations.md §9]. Iterating reconciliation indefinitely — the bounded-exit rule of [diagnosis-and-debugging.md](diagnosis-and-debugging.md) applies: three non-converging passes → stop and report evidence.

## Routing

For the formal model behind these patterns: [foundations.md](foundations.md). For the empirical record: [applications-infrastructure.md](applications-infrastructure.md) and [agent-coordination.md](agent-coordination.md). For the bounded diagnosis procedure that uses Patterns 2, 5, 6, 9, and 10: [diagnosis-and-debugging.md](diagnosis-and-debugging.md). For promise-level machinery (acceptance handshakes, evaluation loops, breach → renegotiation, trust calibration): [promise-theory](../../promise-theory/SKILL.md) and its [patterns reference](../../promise-theory/references/patterns.md).
