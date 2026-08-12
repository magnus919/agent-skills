# Applications in Infrastructure & Code — CFEngine, IaC, and Distributed Systems

**Load this file when you need the empirical record:** what promise theory did
(or failed to do) in real infrastructure — the CFEngine reference
implementation, the IaC generation's borrowing of its vocabulary, the
distributed-systems patterns that look promise-shaped, the adoption history,
and the 2026 argument that LLMs finally supply the reasoning layer the theory
always assumed. This is the practical companion to
[foundations.md](foundations.md), which carries the definitions and citations
for every concept used here; for the application of these lessons to hybrid
human + AI workforces see [agent-coordination.md](agent-coordination.md) and
[patterns.md](patterns.md).

**Provenance.** This file follows the skill's provenance policy: `[UNVERIFIED]`
marks claims that rest on vendor-sourced or secondary accounts, and
`EXTRAPOLATION` marks interpretations that go beyond the cited sources (the
LLM-reasoning-layer synthesis in particular). Case-study figures from CFEngine
and LinkedIn are first-party/vendor materials; they are consistent with the
public record but are flagged where they cannot be independently corroborated.

---

## 1. CFEngine — the reference implementation

### 1.1 From physics to configuration (1993–2008)

CFEngine ("Configuration Engine") began in 1993 as Burgess's personal tool for
managing Unix workstations at the University of Oslo. Two ideas shaped the
later theory:

- **Convergent operators (1995–2003).** Change operations with the character
  of mathematical fixed points: rather than describing steps ("run this
  script"), CFEngine describes the final state and the agent derives the
  steps; running it repeatedly from any initial state converges to a
  predictable result. Key papers: "Cfengine: a site configuration engine"
  (*USENIX Computing Systems* 8(3), 1995) and "On the theory of system
  administration" (*Science of Computer Programming* 49, 2003).
- **Computer Immunology (1998).** The LISA 98 paper "Computer Immunology" was
  a manifesto for self-healing systems — agents in each node continuously try
  to keep their promises and correct deviations — which Wikipedia credits as
  predating IBM's Autonomic Computing manifesto (2001).

By the mid-2000s Burgess concluded that CFEngine 2 was reaching its limits and
spent roughly five years (2004–2008) formulating promise theory specifically
"to help me to rework CFEngine." CFEngine 3 was introduced in 2008 (CFEngine
AS founded June 2008; CFEngine 3 released 2009), rebuilt *around* promise
theory.

### 1.2 CFEngine 3: everything is a promise

CFEngine 3's documentation is explicit: "One concept in CFEngine should stand
out from the rest as being the most important: promises. Everything else is
just an abstraction that allows us to declare promises and model the various
actors in the system" (CFEngine 3.12 docs, "Promises"). The concrete
mechanisms:

1. **Promise types, promisers, promisees, classes.** Promise types define the
   subject — `files`, `packages`, `processes`, `services`, `commands`,
   `methods`, `storage`, `databases`, `reports`, `access`, `classes`, `vars`,
   `defaults`, `roles`, `meta`. Different CFEngine components keep different
   promise types: `cf-serverd` cannot keep `packages` promises; `cf-agent`
   cannot keep `access` promises. The *promiser* is the object that "promises
   that a certain fact will be true" (a file promises permission `0755` and
   owner `root`); the optional *promisee* records who the promise is made to;
   *classes* control the conditions under which a promise is valid (OS type,
   day of week, user-defined contexts).
2. **Bundles and bodies.** Promises are grouped into *bundles* (logical groups
   such as "webserver" or "filesystem"); reusable attribute groups are
   *bodies*. This maps directly to promise theory's "aspects and bundles"
   (Burgess, "Promise You A Rose Garden," 2007).
3. **Normal ordering and fixed-point convergence.** CFEngine maintains a
   default order of promise types "based on a simple logic of what needs to
   come first, e.g. it makes no sense to create something and then delete it,
   but it could make sense to delete and then create (an equilibrium)." Within
   a bundle, promise types execute in round-robin "normal ordering," iterating
   up to three times "converging towards a final state." Explicit ordering is
   available via `depends_on` and class-based conditioning. This is the
   operational embodiment of fixed-point convergence.
4. **Promise locking.** When a promise is validated (kept or repaired), it is
   locked for a default interval (`ifelapsed`, 1 minute by default), keyed on
   a hash of promiser + attributes + context. Locks control frequency and
   prevent thrashing.
5. **Idempotence and statistical compliance.** "Promises are idempotent:
   repetition confirms but they don't add up cumulatively" (Rose Garden
   essay). A system never guarantees to be exactly in the ideal state; it
   approaches the fixed point by best effort, at a rate determined by the
   ratio of environmental change frequency to CFEngine execution frequency
   (Wikipedia; "On the theory of system administration," 2003).
6. **The autonomous agent pull model.** The default architecture: a policy
   server publishes policy (the "masterfiles"), and each host's `cf-agent`
   *pulls* the policy it has agreed to apply over an authenticated channel
   (`cf-serverd` access promises), then evaluates it locally. There is no
   central scheduler issuing commands. "All decision-making and information is
   made by each CFEngine agent autonomously... there is no strong coupling
   through the network" (Burgess, InfoQ interview, 2014). The pull model is
   simultaneously a *security* principle: agents dial out, firewalls stay
   closed inbound, and an external actor cannot reach in to push commands —
   "autonomy is deafness to exploitation" (Burgess, 2022).
7. **The agent loop: observe, reason, commit.** Each agent observes its local
   environment (its promises define what it watches), reasons about which
   promises are unkept, and repairs only those.

In Burgess's own account (InfoQ, 2014), the theory shows up in CFEngine 3 in
three places: the language ("Absolutely everything that you express is a
promise, or part of a promise... Each promise is continuously measured — is it
kept or not kept?"); the decentralization of decision-making (routing-protocol-
like autonomy, "no strong coupling through the network"); and conflict and
knowledge tracking (two promises of the same type with different constraints
are broken promises — contradictions detectable by counting promises across the
graph).

### 1.3 Scale: the LinkedIn case study

The public LinkedIn case study (CFEngine AS, Nov 2014 — vendor first-party
material) reports: automation of **40,000+ servers by a six-person operations
team**; 5–10 production changes per day; new machines provisioned "in 15
minutes or less"; user account management across "thousands of machines in
minutes"; phased rollouts using CFEngine *range classes* (assign a change to
0% of machines, expand to 10%, monitor, expand to 100%); and root access
granted broadly to engineers because CFEngine "will immediately restore the
system to its desired system state using its policy engine." The Wikipedia
summary adds: "The largest reported datacenter under management of CFEngine is
above a million servers, while sites as large as 40,000 machines are publicly
reported (LinkedIn)." The million-server figure is a repeated marketing claim
without a public citation — treat as `[UNVERIFIED]`.

### 1.4 The documented gap: promise-keeping was never stored as data

The CFEngine experience is the strongest evidence both for and against the
theory's practical power — and its failure mode is the single most important
lesson for this skill:

- **Scope-bounded observation.** "A cf-agent observes what its promises
  describe. Write a promise about `/etc/ssh/sshd_config` and the agent watches
  that file. Write nothing about the security group in front of the host and
  the agent holds no opinion" (Webframp, "The Promise None of Them Kept,"
  2026). This is a *feature* of the theory (locality of knowledge) and a
  *failure mode* in practice (silent drift outside the declared surface).
- **No retained history.** "It can tell you whether the promise is kept right
  now. Ask what the config looked like last Tuesday... and there is no
  queryable answer, because **promise-keeping was never stored as data**"
  (Webframp, 2026). CFEngine's verdict is a snapshot, not a record.

The consequence is exactly what the theory itself says trust requires but never
delivered: without a retained, versioned, queryable record of assessments you
cannot do trend analysis, rollback planning, breach→renegotiation, or trust
accumulation. **The evaluation loop was incomplete** — observe → assess → act
existed, but the *assessment* was not persisted as data, so the loop could not
learn across time. Any promise-theoretic system built today — including
AI-agent coordination — must store assessments as versioned data (a promise
ledger). This is the gap the skill's "evaluation loop" pattern and the
`promise-review` template close (see [patterns.md](patterns.md) and
[trust-and-verification.md](trust-and-verification.md)).

---

## 2. The IaC landscape — vocabulary without the mechanism

Burgess has said he is "surprised and a little humbled by how much of promise
theory has been taken on board by the industry" (InfoQ, 2014). The industry,
however, took the *words* (declarative, convergence, idempotency, desired
state) and mostly not the *mechanics* (autonomous agents, local reasoning,
voluntary acceptance, observation by the acting agent).

### 2.1 The three-property test

The following analysis uses a three-property test derived from promise theory's
axioms, following Webframp's 2026 framework (itself an interpretation of the
theory — `EXTRAPOLATION` in the sense that the axioms are the authors', the
operational test is the essayist's):

1. **Observation** — does the agent perceive its environment itself, or diff
   against a snapshot?
2. **Local reasoning** — does the agent decide, or merely execute precomputed
   instructions?
3. **Voluntary commitment** — is the behaviour a promise about the agent's own
   state, or an imposition on a remote party?

### 2.2 Comparison table

| System | Control model | Desired-state mechanism | Continuous convergence? | Agent on target? | Verdict |
|---|---|---|---|---|---|
| **CFEngine 3+** | Pull; agent autonomy | Promise language; fixed-point convergence | Yes (scheduled loop, ~5-min default) | Yes (`cf-agent`) | Reference implementation: observe, reason, commit |
| **Puppet** | Pull; master + agent | Declarative resource DSL; convergence per run | Yes on schedule | Yes | Partial: pull agent + desired state, but reasoning centralized in the master; catalog = obligations imposed |
| **Chef** | Pull; server + client | Recipes/attributes; "convergent" resources | Yes on schedule (~30 min) | Yes (`chef-client`) | Partial: local convergence, but "observation scoped to the declaration" |
| **Ansible** | Push; control node via SSH | Playbooks; module-level idempotency | No between runs; no resume after mid-run failure | No (agentless by default) | Imposition model; `ansible-pull` is the honest exception |
| **Terraform** | CLI plan/apply | HCL declarations; plan = diff vs last-known state file | No (inert between applies; `refresh` opt-in) | No | Fails all three properties: a batch script with a diffing preamble |
| **Nix / NixOS** | Apply-time build (pull from store) | Pure functional derivation; reproducibility | No repair loop (rebuild/switch is atomic) | No | Different axis: functional purity, not convergence; no observing agent |
| **Kubernetes** | Controller reconciliation (control plane + kubelet) | Declarative spec vs status; controllers drive actual → desired | Yes (continuous, level-triggered) | Yes (`kubelet` per node) | Closest mass-adopted cousin: the loop without the theory |
| **OPA / Kyverno** | Decision service / admission webhook | Rego/Kyverno rules; allow/deny/violation | No (evaluated per request) | No | Obligation-based gates → best fit as the *assessment* layer of promises |
| **Rudder** | CFEngine agent + UI | CFEngine promises + compliance reporting | Yes | Yes | Direct descendant: promise theory + continuous compliance |

### 2.3 Verdicts in detail

- **Terraform fails the three-axiom test.** Its state file "records
  Terraform's own last write, the one piece of evidence an agent assessing its
  own promise-keeping cannot use" (Webframp). It executes; it does not decide —
  the reasoning was precomputed by the human who wrote the HCL. And it
  "imposes changes on remote resources through API calls. The resources
  promise nothing back, and Terraform promises nothing about ongoing
  maintenance." Drift is only detected when a human runs `plan`; the
  "terraform apply every 5 minutes" pattern is a manual reconstruction of the
  loop the theory makes automatic.
- **Ansible is push/imposition.** "A control node connects to targets via SSH
  and pushes tasks. It runs what it was told" (Webframp). In Burgess's terms
  that is an *imposition model*: targets are obliged by the controller's
  assumption of compliance. **`ansible-pull` is the honest exception** — it
  "run[s] from cron on the target... gets a local agent that clones a playbook
  repository, evaluates conditions locally, and converges on a schedule with no
  controller involved. That is the promise-theoretic mode, shipped in the box,
  and almost nobody deploys it" (Webframp).
- **Chef/Puppet are partial.** Both deploy pull agents that converge toward a
  declared state, which is genuinely promise-like — but the reasoning is
  centralized (the master builds the catalog; the server computes the
  recipes), so the agent observes facts without deciding policy, and the
  resources are obligations the master imposes via catalog rather than
  promises the node accepted.
- **Nix is a different axis.** NixOS is "declarative" in a functional-
  programming sense, not a convergence sense: the whole OS "is built by the Nix
  package manager from a description in a purely functional build language...
  building a new configuration cannot overwrite previous configurations"
  (nixos.org, "How Nix Works"). Properties are reproducibility, atomic
  upgrades, and rollback — there is **no continuous repair loop and no
  observing agent**; convergence is replaced by determinism. Burgess has
  publicly dismissed the immutability framing ("This nonsense about
  immutability is a complete red herring, in my view," InfoQ 2014), while
  conceding disposable-computing redundancy is the correct scaling strategy.
- **OPA/Kyverno are obligation gates.** The Open Policy Agent "provides a
  high-level declarative language that lets you specify policy as code and
  simple APIs to offload policy decision-making from your software" (OPA docs).
  A Rego policy answers a query about input ("allow", "violation", "deny") and
  the caller enforces the verdict. In promise-theoretic terms these are
  **impositions evaluated at the gate**, not promises kept by agents: the
  requestor does not promise to behave; it is (or is not) admitted. There is a
  nuance: OPA is *consultative* — the caller promises to ask, the enforcement
  point promises to check — but in practice the pattern is obligation layered
  on the admission path. **The constructive reading: an operator building a
  promise-theoretic system uses OPA/Kyverno as the *assessment* layer of
  promises** — "I will not expose telnet" can be verified by evaluating Rego
  against live config — which is exactly the assessment-layer role this skill
  routes to [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md)
  (also routed from [trust-and-verification.md](trust-and-verification.md)).

### 2.4 Honest exceptions and the residual need for declarations

Imposition is legitimate where an agent cannot be installed (network switches,
locked-down appliances) — "imposition is the only available mode" (Webframp).
Declared intent still matters in three cases: *provisioning* (you cannot
observe what does not exist), *compliance baselines* ("all S3 buckets must
have encryption enabled" is intent, not observation), and *rollback targets*.
The lesson is scope, not abolition: keep declarations where intent is real,
and shrink the surface of state you pretend to manage by declaration.

---

## 3. Distributed systems — promise-shaped ideas at scale

Burgess has argued that the networking world "has pretty much always been
designed in a promise-compatible way" (InfoQ, 2014). A map of where
promise-theoretic ideas already appear:

### 3.1 BGP peering and DNS

- **BGP peering** is the canonical example of voluntary cooperation at scale:
  providers exchange *mutual promises to transport packets*, and the value is
  in the promise itself — "a matter of being seen to be connected to the right
  people" (Rose Garden essay, citing Norton's peering work). Routing protocols
  are decentralized, self-healing, convergent systems.
- **DNS** is the essay's worked example: name servers promise answers;
  resolvers promise to accept requests, forward them, and *use* replies;
  masters promise zone data to slaves, who promise to use it. Every promise is
  a potential failure mode and a place to plan redundancy.

### 3.2 Gossip / epidemic protocols

Gossip protocols were introduced by **Demers et al., "Epidemic algorithms for
replicated database maintenance," PODC 1987**: each node periodically exchanges
state with a randomly chosen peer (anti-entropy and rumor mongering), so
information spreads epidemically with no central coordinator. This is
coordination *by voluntary peer exchange* — structurally the same
"bottom-up, many-to-many, no central controller" stance as promise theory,
though gossip propagates state, not intentions. The relationship: gossip gives
you *eventual consistency of information*; promises give you *stated
intentions that agents assess*. A promise-theoretic distributed system would
use gossip- or DNS-like discovery as the substrate for communicating promises
and local assessment for keeping them.

### 3.3 Consensus vs promise-based coordination

Strongly consistent consensus — Lamport's Paxos (1989/1998); Ongaro &
Ousterhout's Raft (USENIX ATC 2014) — is the opposite end of the spectrum: a
quorum agrees on a total order of operations. Promise-based coordination makes
no such guarantee; correctness is a property of the promise graph
(contradiction-freedom) rather than of a single ordered log. These are
complementary: Raft/etcd gives the few things that must be exactly agreed (who
is leader, what is the config version); promises give the many things that only
need approximate consistency (host configuration, drift repair). Kubernetes'
design is exactly this split — etcd (Raft) for the API store, per-resource
controllers for continuous reconciliation.

### 3.4 Service discovery

Burgess's DNS analysis generalizes: a discovery service is a set of agents
promising answers about where things are, and consumers promise to *use* those
answers. Modern equivalents (CoreDNS, Consul, etcd-based discovery, mDNS)
implement promise-shaped contracts: the registry promises freshness, the client
promises to re-resolve, and health checks are assessments of the "service is
running" promise.

### 3.5 MAPE-K and autonomic computing

IBM's Autonomic Computing initiative (2001; canonical statement **Kephart &
Chess, "The Vision of Autonomic Computing," *IEEE Computer* 36(1):41–50,
2003**) defined the MAPE-K control loop — Monitor, Analyze, Plan, Execute,
shared Knowledge — and the self-* properties. The connection to promise theory
is direct: Burgess's "Computer Immunology" (1998) predates the initiative, and
the bridge paper is **Burgess & Couch, "Autonomic Computing Approximated by
Fixed-Point Promises," MACE 2006**: MAPE-K loops are implementations of
promise-keeping, with convergence semantics giving stability guarantees. The
difference is again the unit of interaction: MAPE-K's manager commands
effectors; promise theory's agents promise.

### 3.6 Cisco ACI / OpFlex — the one major vendor build

Cisco ACI (2012–2014) is the only major vendor product built *explicitly* on
promise theory: "APIC policy use an object-oriented approach based on promise
theory. Promise theory is based on declarative, scalable control of intelligent
objects, in comparison to legacy imperative models" (Cisco Community, "Cisco
ACI Architecture – Simplified"). The southbound protocol **OpFlex** was
designed to "exhibit the same promise theory information model as ACI"
(Network World, 2014), and the promise-theoretic analysis of SDN is in
**Borrill, Burgess, Craw & Dvorkin, "A Promise Theory Perspective on Data
Networks," arXiv:1405.2627 (2014)**. In ACI, the endpoint group (EPG) and
contracts are the promise objects rendered by intelligent fabric devices rather
than dumb flow tables. (The ACI/OpFlex promise-theory basis is vendor + trade-
press attested; treat detail beyond the arXiv paper and Cisco's own
documentation as secondary `[UNVERIFIED]`.) OpFlex did not win the SDN
southbound debate — OpenFlow/OVSDB and vendor models did.

### 3.7 Intent-based networking

Cisco's IBN: "The goal is for the network to continuously monitor and adjust
network performance to help assure desired business outcomes" (cisco.com). The
closed loop has three blocks — **Translation** (intent → policy),
**Activation** (policy installation), **Assurance** (analytics/ML verifying
the intent is achieved). IBN is promise-shaped at the level of *intent and
assurance*; its mechanism, however, is controller-led policy push (obligation),
not autonomous device promises.

### 3.8 Kubernetes — "the loop without the theory"

Kubernetes is the most important real-world instance of promise-shaped control,
and its own documentation reads like a promise-theory summary:

> "Kubernetes is not a mere orchestration system. In fact, it eliminates the
> need for orchestration... Kubernetes comprises a set of independent,
> composable control processes that continuously drive the current state
> towards the provided desired state. It shouldn't matter how you get from A to
> C. Centralized control is also not required." (kubernetes.io/docs/concepts/
> overview)

Mechanics: users declare desired state in API objects (`spec`); controllers
watch `spec` vs `status`, level-triggered, and take idempotent actions;
`kubelet` on each node is the local agent that keeps node-level promises
(containers running, health probes). Self-healing — "restarts containers that
fail, replaces containers, kills containers that don't respond to health
checks" — is the fixed-point loop. The divergences from the theory are equally
instructive: the API server + etcd is a *central source of truth*
(consensus-backed), and scheduling is *imposition* (a Pod does not promise to
run; the scheduler decides and the kubelet obeys). Kubernetes is thus "the
loop without the theory": it delivers observe–compare–repair at industrial
scale while keeping a centralized control spine. A fair claim is that
Kubernetes made the promise-theoretic control loop the default mental model of
infrastructure for a generation — while dropping the theory's stronger claims
about autonomy, locality, and voluntary acceptance.

---

## 4. Adoption history — why it never dominated

### 4.1 Timeline (abridged)

| Year | Event |
|---|---|
| 1993 | CFEngine 1 ships (Burgess, Oslo) |
| 1998 | "Computer Immunology" (LISA 98): self-healing manifesto; CFEngine 2 |
| 2001 | IBM launches Autonomic Computing initiative (Kephart & Chess, 2003) |
| 2004 | Promise theory first proposed by Burgess (policy-based management context) |
| 2005 | DSOM 2005 paper introduces the name "Promise Theory"; informal best-paper recognition |
| 2005–2006 | Bergstra collaboration begins; impositions concept |
| 2007 | "Promise You A Rose Garden" essay |
| 2008–2009 | CFEngine 3 rebuilt on promise theory; CFEngine AS founded |
| 2012 | Cisco begins using promise theory in SDN/ACI initiatives |
| 2013–2014 | Tech media wave (Network World, NoJitter, Linux Journal); LinkedIn case study; first book edition |
| 2015 | *In Search of Certainty* and *Thinking in Promises* (O'Reilly) |
| 2016 | Chef Habitat unveiled; Wired profiles it with Burgess; Tim O'Reilly's *WTF* discusses promise theory |
| 2017 | CFEngine company renamed Northern.tech |
| 2019 | *Promise Theory: Principles and Applications*, 2nd ed. |
| 2023 | ~2,700 companies reported using CFEngine (Enlyft — vendor-ecosystem metric, `[UNVERIFIED]`) |
| 2025 | Ecma publishes NLIP, a natural-language agent-communication standard |
| 2026 | CFEngine 3.28.0 released (July 2026); Webframp's "The Promise None of Them Kept" |

### 4.2 The two industry moments

**Cisco ACI (2012–2014)** was the explicit, high-profile industrial adoption
(§3.6); it generated the famous tech-press moment but OpFlex lost the SDN
southbound race. **Chef Habitat (2016)** — "the automation travels with the
application"; supervisors as autonomous cells — was framed by Burgess in Wired
as an application of promise theory ("humans and autonomous agents work
together... You share your intentions with Habitat, and its autonomous agents
work to realize them"). It never achieved mainstream adoption, and Chef itself
was later acquired.

### 4.3 Why academic traction outpaced industry dominance

1. **The theory is analytic, not prescriptive.** "Promise theory is not a
   technology or design methodology. It doesn't advocate any position or
   design principle, except as a method of analysis" (Wikipedia). Enterprises
   buy solutions, not analysis frameworks.
2. **Self-referential literature.** Most peer-reviewed output is
   Burgess–Bergstra co-authored; Wikipedia flags the article's reliance on
   sources "too closely associated with the subject." Independent validation
   is thin (see [foundations.md](foundations.md) §6).
3. **The DSL and the cultural misfit.** CFEngine's promise language and the
   "academization" agenda alienated practitioners, while Puppet/Chef/Ansible
   courted developers with Ruby/Python/YAML and GitHub-style workflows.
4. **Timing and the container wave.** The 2010s moved from config management
   to immutable images, containers, and orchestrators — a world Burgess has
   criticized ("immutability... a complete red herring... I call that politics,
   not science," InfoQ 2014). Disposable computing took the "numbers game"
   redundancy he had predicted, but via images rather than promises.
5. **The market.** RedMonk's 2015 analysis documented Ansible's explosive
   growth and minimal CFEngine community activity; Enlyft's 2023 data showed
   CFEngine at 0.04% of IT management software market share.
6. **The company.** CFEngine AS → Northern.tech pivoted toward device lifecycle
   management and compliance-heavy regulated industries — a defensible niche,
   not the mainstream.

### 4.4 Lessons for applying it now

1. **Use it as a vocabulary and audit discipline, not a runtime.** The durable
   asset is the questions: *Who is the agent? What does it observe, and can it
   observe that directly? What may it promise, and about whom? Where does an
   imposition happen, and did anything on the receiving end agree to accept
   it?* (Webframp's formulation.)
2. **Design for the loop plus memory.** CFEngine proved the loop but could not
   answer "what did last Tuesday look like?" Retained, versioned, queryable
   observation records are the missing third leg; any modern promise-theoretic
   system should store assessments as data (§1.4).
3. **Watch the imposition-to-promise ratio.** Push tools work, but they give
   you neither autonomy nor convergence nor verification; when you cannot
   install an agent, say so explicitly rather than pretending.
4. **Adopt the fixed-point discipline regardless of tool.** Desired state +
   continuous reconciliation + idempotency is the one promise-theory idea that
   demonstrably won (Kubernetes). It is safe to bet on.
5. **Expect the "hardwired centralization" reflex.** Burgess: "centralised
   control is always the first idea people come back to when they need to
   manage something. It's like it's hardwired into our culture" (InfoQ, 2014).

---

## 5. The LLM-reasoning-layer argument

### 5.1 The missing piece was never the agent

CFEngine built the *agent* side of the theory completely: a real
promise-keeping engine with observation, local reasoning, voluntary pull, and
fixed-point convergence. What it never built — and what the IaC generation that
followed did not build either — was the *reasoning layer*: an actor that can
look at a live system, interpret what it sees, decide what matters, and commit
to a repair, at a semantic altitude above declarative diffs. Configuration
agents are bounded by their declarations; a promise about
`/etc/ssh/sshd_config` is watched, and everything else is ignored (§1.4).
That scope-boundedness is exactly what makes the evaluation loop incomplete.

### 5.2 What LLMs supply — and what must still be built

`EXTRAPOLATION` — this synthesis goes beyond the cited sources. Burgess's own
2026 work ("Cooperation in Human and Machine Agents," arXiv:2604.10505)
reframes promise theory for human–machine cooperation, and Webframp's 2026
essay ("The Promise None of Them Kept") makes the direct claim: **large
language models supply the reasoning layer promise theory always assumed** —
an agent that can observe a live system, reason about what it sees (the
three-property test's "reason" step), and commit to action in natural language,
without a prewritten DSL describing every promise in advance.

Three properties make LLMs a qualitatively different substrate than CFEngine
or Terraform:

1. **Semantic observation.** An LLM can interpret unstructured observations
   (logs, tickets, conversations, status pages) and map them to promises,
   where a config agent can only see its declared surface.
2. **Local reasoning about intent.** An LLM can compare what a promise says
   against what actually happened and *explain* the gap — turning the
   assessment step (α, β, ε in [foundations.md](foundations.md)) from a
   boolean verdict into a negotiable finding.
3. **Natural-language commitment.** LLMs make promises (capability
   declarations, contracts, acceptance criteria) in the same language humans
   use, closing the semantic gap that sank KQML/FIPA-ACL and The Coordinator
   (agents no longer need a shared ontology — the model translates between
   local ontologies, as Ecma's NLIP, standardized December 2025, begins to
   formalize).

The 2026 essay's title — "The Promise None of Them Kept" — cuts both ways: the
IaC generation *claimed* the promise lineage without the mechanism ("Chef
called its resources 'convergent.' Puppet called its catalogs 'desired state.'
Terraform called its plans 'declarative.' Ansible called its playbooks
'idempotent.' None of those four kept the promise. Burgess's own tool did, and
ran into a different limit" — the un-stored assessment history). LLMs may
finally supply the reasoning layer — but they inherit the same two failure
modes unless the loop is completed: **promise-keeping must be stored as data**,
and **assessments need provenance** (who assessed, when, against what
observation).

### 5.3 Why this matters for a hybrid workforce

`EXTRAPOLATION` — the application to human + AI coordination is the core thesis
of this skill and is developed in
[agent-coordination.md](agent-coordination.md). The infrastructure record
justifies the transfer: the theory's vocabulary (autonomous agents, promises,
impositions, assessment, the Downstream Principle) was forged in systems where
nobody could command anyone; a workforce containing humans (unformalizable),
LLMs (probabilistic), and machines (deterministic) has exactly that property.
The CFEngine lesson — *the loop is only as good as its stored assessments* —
and the Kubernetes lesson — *the loop is mass-adoptable when the reasoning is
centralized* — define the design space: run the loop, store the assessments,
and let each party promise only what it can observe.

---

## 6. Sources (works cited above)

**Primary (Burgess/Bergstra):** Burgess, "Cfengine: a site configuration
engine," *USENIX Computing Systems* 8(3), 1995; Burgess, "On the theory of
system administration," *Science of Computer Programming* 49, 2003; Burgess,
"Computer Immunology," LISA 98; Burgess, "Promise You A Rose Garden" (2007);
Burgess, DSOM 2005 (LNCS 3775, pp. 97–108); Bergstra & Burgess, *Promise
Theory: Principles and Applications* 2nd ed., χtAxis, 2019; Burgess, *In
Search of Certainty* (O'Reilly, 2015); Burgess, *Thinking in Promises*
(O'Reilly, 2015); Borrill, Burgess, Craw & Dvorkin, "A Promise Theory
Perspective on Data Networks," arXiv:1405.2627 (2014); Burgess & Couch,
"Autonomic Computing Approximated by Fixed-Point Promises," MACE 2006;
Burgess, "Cooperation in Human and Machine Agents," arXiv:2604.10505 (2026).

**CFEngine and case materials:** CFEngine 3.12 documentation ("Promises",
"Normal Ordering"); CFEngine documentation (LTS), "What is CFEngine and why?";
LinkedIn Infrastructure and Operations Automation at WebScale (CFEngine AS
case study, Nov 2014); Wikipedia: "CFEngine", "Promise theory" (index only).

**Industry and IaC:** InfoQ interview with Burgess (2014); Network World,
"Promise Theory" (2014); Cisco Community, "Cisco ACI Architecture – Simplified"
(2014); Cisco, "Intent-Based Networking" (2024); Kubernetes documentation
("Overview"); nixos.org, "How Nix Works"; Open Policy Agent documentation;
Webframp, "The Promise None of Them Kept" (2026); RedMonk (2015); Enlyft
(2023); Wired, "The Quest to Make Code Work Like Biology Just Took A Big Step"
(2016); O'Reilly, *WTF* (2017).

**Distributed systems and precedents:** Demers et al., "Epidemic algorithms
for replicated database maintenance," PODC 1987; Lamport, Paxos (1989/1998);
Ongaro & Ousterhout, Raft (USENIX ATC 2014); Kephart & Chess, "The Vision of
Autonomic Computing," *IEEE Computer* 36(1), 2003; Ecma TC56, NLIP (2025).
Full bibliographic details are in the mission research report
(applications-infrastructure.md); the repository standard is to cite the named
work inline, as above.
