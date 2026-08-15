# LLM and Agent Security

This reference teaches how to secure systems built around large language models (LLMs) and the
autonomous agents that act on their output. Its central message is that LLM security is not a
single bug to patch but a set of trust-boundary decisions layered across the whole system: what you
let a model read, what you let it do, what you trust its output to be, and what it can reach when an
input turns adversarial. The same discipline extends to agents, where autonomy multiplies every
risk because a model that merely talks can be re-pointed to call tools, move files, and change real
state. This reference synthesizes (never reproduces) ideas from *The Developer's Playbook for LLM Security* and *Beyond the Algorithm*, and it marks "current research" where the
fast-moving 2025-era OWASP and agentic guidance de-stales the books. Read it with
`foundations-and-principles.md` (which names safety and human oversight as governing principles),
`privacy-and-data-governance.md` (the data-protection half that security protects), and
`ai-lifecycle-governance.md` (where security gates sit in the model lifecycle). Use the
`model-risk-assessment.md` and `model-card.md` templates to record the threat model and controls
this reference describes. It is not legal advice, and specific controls should be re-verified
against current OWASP and government guidance at use time.

## Why LLM Security Is Different

A conventional application separates code from data: the attacker can try to inject into the code
path, but the two are distinguishable. An LLM blurs that line because its instructions and its data
are the same natural-language tokens, processed together in one pass. *The Developer's Playbook for
LLM Security* makes this the heart of the threat model: an LLM cannot always tell
developer-authored guidance from user-supplied or retrieved content, which is why so many of its
risks are really about confusion between "instructions" and "data." *Beyond the Algorithm* frames
the same idea as a trust-boundary problem — a line that separates components worth trusting from
those treated as untrusted — and stresses that sanitizing and validating inputs before they reach
the model is the protective habit that keeps a boundary meaningful.

The practical consequence is that most LLM defenses are not about making the model immune; they are
about constraining what a compromised model can reach and what its outputs can do. Security teams
should assume injection may succeed and engineer the surrounding system so that a failure is
contained. This is the pessimistic trust boundary: treat every output the model produces, and every
action it initiates, as potentially harmful until validated.

## Trust Boundaries in an LLM Application

A trust boundary is the point where data or control moves from one trust level to another — user
input entering the model, model output returning to the user, data leaving for an external API, or
an agent reaching a database. *The Developer's Playbook* walks through each boundary an LLM
application crosses and what to secure there:

| Boundary | What crosses it | What to secure |
|---|---|---|
| User interaction | Inputs and outputs between person and model | Validate and sanitize inputs; filter and monitor outputs for toxic, inaccurate, or sensitive content |
| In-the-wild training data | Public/internet-sourced training and retrieval content | Treat as untrusted; watch for bias, toxicity, poisoning, and indirect injection |
| Internal data | Proprietary fine-tuning data, corporate documents | Protect confidentiality; beware leakage of sensitive or personally identifiable content |
| Live external sources | Web pages, third-party APIs, tool outputs read at runtime | Treat as untrusted; validate and scope what the model may ingest |
| Internal services | Databases, internal APIs, backend systems the model or agent can reach | Apply least privilege; prevent unauthorized access and lateral movement |

Two hosting choices shift the risk profile. Calling a third-party model API is convenient and
cheap, but the data crosses a boundary into an external system, raising exposure risk. Hosting a
model privately keeps data inside your network and tightens control over the boundary, but shifts
the burden to maintenance, patching, and verifying that an open-source model is genuine and
uncompromised. Neither choice is safe by default; each just moves where the boundary is drawn.

## Prompt Injection

Prompt injection is the manipulation of an LLM or agent through crafted inputs so that it ignores
its instructions, leaks data, bypasses policy, or takes actions the operator never intended. It is
the single most consistently ranked risk in OWASP's taxonomy and is widely described as the most
common AI exploit. *The Developer's Playbook* distinguishes the two delivery classes:

- **Direct injection** ("jailbreaking"): the attacker controls the input channel, crafting a prompt
  to override the system prompt or reveal hidden instructions. *Beyond the Algorithm* notes that
  this can let an attacker target backend systems the LLM can reach.
- **Indirect injection**: malicious instructions are planted in content the model reads as part of
  its task — a retrieved document, a web page, a tool's output. This is the more dangerous variant
  for agents, because the untrusted material often arrives through a channel the system trusts, and
  it can be invisible to humans when only the model processes the text.

Prompt injection is hard because there is no solid, universal patch the way there is for SQL
injection. The books characterize mitigation as defense-in-depth, more like anti-phishing than like
parameterized queries. Layered controls include:

- **Rate limiting** (by IP, user, or session) to slow automated probing and concentrated attacks.
- **Input filtering** as a first line, though simple regex blocklists are brittle and degrade
  capability (blocking words like "bomb" also blocks legitimate discussion).
- **Adding prompt structure** — tagging data separately from instructions so the model treats
  injected text as data rather than as a high-priority command.
- **A special-purpose filtering LLM** trained to flag injection attempts, treated as one layer, not
  a silver bullet.
- **Adversarial training**, seeding malicious examples into the training set so the model learns to
  recognize them, with continuous updating as attacks evolve.
- **Pessimistic trust boundary and least privilege**, treating every output as untrusted, filtering
  it, restricting backend access, and requiring human approval for destructive actions.

## Sensitive Data Exposure

LLM applications can leak data through several routes: the model regurgitating memorized training
material, drawing on confidential internal data it was given access to, or being steered by
injection into revealing information. *The Developer's Playbook* connects exposure to the "know too
much" problem — an overfitted or too-broadly-accessed model can emit private information even when
the underlying data is secured. Controls include treating externally visible prompts and outputs as
a disclosure surface, restricting which internal corpora a model may draw on, sanitizing outputs,
monitoring for data exfiltration, and keeping sensitive and non-sensitive functions on separate
boundaries. For agentic systems this extends to what a tool can return and what an agent may send
out, so that a compromised agent cannot quietly exfiltrate data through a channel the operator
doesn't watch.

## Hallucination, Overreliance, and Misinformation

Hallucination is the model confidently generating plausible-sounding content that is not true or
grounded in its inputs. Alone it is an accuracy problem, but it becomes a security and governance
problem through **overreliance** — when people or downstream systems trust erroneous output and act
on it. *Beyond the Algorithm* and the playbook both treat overreliance as a top-ten-class risk
because fluent, confident output that drives a decision turns a wrong answer into a wrong outcome.
Mitigations pair technical controls (grounding via retrieval, validation of outputs) with
organizational ones (designing the human–AI interface so people know when to double-check, and
building automatic checkpoints before output becomes action). "current research": the OWASP GenAI
LLM Top 10 2026 has moved misinformation materially up the rankings because incident evidence
showed how often bad output produced real-world harm in systems that acted without checking.

## Excessive Agency and Agentic Risk

Excessive agency is granting an LLM-based system more capability, permission, or autonomy than it
safely should have. *The Developer's Playbook* treats it as a structural design vulnerability rather
than an output bug, and breaks it into three forms:

- **Excessive permissions**: the model or agent holds broader access than needed (e.g., write and
  delete rights where read-only would do), which a confused-deputy attack can exploit to modify
  records it should only view.
- **Excessive autonomy**: the system takes consequential actions without review (e.g., auto-trading
  a portfolio), so a single injected instruction can drive real financial or operational damage.
- **Excessive functionality**: features that sound attractive but expand the attack surface beyond
  what the application requires.

The mitigations center on **least agency**, the agentic counterpart to least privilege: scope each
agent's tools and permissions narrowly, require human approval for high-impact actions, isolate
agents so a compromised one cannot move laterally, and log and monitor decisions and tool calls so
misuse is detectable. "current research": the OWASP GenAI LLM Top 10 2026 ranks excessive agency
third, and in May 2026 a Five Eyes group of national cybersecurity agencies (CISA, NSA, and allied
cyber bodies) issued their first joint guidance on adopting agentic AI, recommending cautious
adoption with identity, access, and monitoring controls.

## Denial of Service and Unbounded Consumption

LLM systems are vulnerable to attacks that exhaust their resources. A denial-of-service (DoS)
attack floods the model with requests to degrade performance or make it unavailable. The playbook
highlights a financially distinct variant, denial-of-wallet (DoW): because cloud models bill
per-token or per-operation, an adversary can drive an unsustainable cost by issuing excessive or
pathologically expensive requests, harming the operator's economics even without a service outage.
A related class is model cloning or theft, where an attacker floods the model with queries, records
the answers, and uses them to train a competing model, draining value from the operator's
intellectual property. Many of the same defenses apply because all three depend on repeated query
volume: rate limiting, quotas, request cost caps, anomaly monitoring, and access controls that
distinguish trusted users from automated abuse. "current research": the OWASP GenAI LLM Top 10 2026
introduces unbounded consumption, noting that per-token costs mean request-per-second limits alone
do not protect against expensive reasoning chains or repeated tool calls.

## Supply Chain Security

The LLM supply chain reaches well beyond conventional software dependencies. It includes the
foundation model itself, the datasets used to train or fine-tune it, the retrieval stores and
external services it calls, and any plugins or tools an agent invokes. *The Developer's Playbook*
warns that open-source model distribution is immature: in 2023, leaked API tokens and account
takeovers on model registries raised the real possibility that a trusted model could be swapped for
a malicious one, and a tainted model file can act as a back door. Training-data poisoning can
inject false information or bias for very little cost, and even accidental exposure to unsafe
training data can cause a deployed model to generate harmful content. Insecure plugins broaden the
surface further, letting a third-party component become a vector for malicious code or data
collection.

The controls are inventory and provenance. Teams should track the origin and version of every
model, dataset, and plugin they rely on, mirroring the software-bill-of-materials discipline.
Artifacts include the SBOM (software bill of materials), the model card (documenting intended use,
data, performance, and limitations), and emerging ML-BOMs for machine-learning components. *Beyond
the Algorithm* likewise calls for secure model development and deployment practices that treat
models and datasets as first-class supply-chain components. "current research": the OWASP GenAI LLM
Top 10 2026 broadens supply chain risk to include name-squatting in public model registries and
configuration-file attacks that alter model behavior without touching the model itself.

## Red-Teaming LLM and Agentic Systems

Red-teaming is a structured, adversarial evaluation that probes an AI system for failures —
prompt injection, jailbreaks, data leaks, unsafe outputs, bias, and unintended tool use — before an
attacker finds them. *Beyond the Algorithm* describes it as crafting prompts that trigger harmful
or revealing behavior and notes it is creative and resource-intensive. The playbook adds that a red
team simulates realistic attacks and drives improvements, and it is complementary to traditional
penetration testing: a pen test is a point-in-time assessment of exploitable weaknesses, while red
teaming is an ongoing, creative effort to probe AI-specific behaviors that automated scans miss. A
red team exercises areas like hallucination triggers, bias, excessive agency, and injection with an
external, adversarial perspective that internal teams focused on functionality often lack.

Practitioners caution that red-teaming is necessary but not sufficient: because it tends to find
known vulnerability classes, it can create a false sense of security against novel attacks,
especially as models and agent architectures change quickly. Effective programs combine red-teaming
with layered prompt-injection defenses, least-agency design, monitoring and incident response, and
continuous re-evaluation rather than treating a single pass as a safety certification. "current
research": government bodies have institutionalized this practice — the U.K. AI Security Institute
and the U.S. AI Safety Institute (now NIST's Center for AI Standards and Innovation, or CAISI) both
perform technical adversarial evaluation of models and agents, and OWASP maintains a red-teaming
taxonomy as a companion to its Top 10.

## The Current OWASP Top 10 (verified)

OWASP's Top 10 for LLM Applications is the default risk checklist for the field, but its ranking is
volatile between editions — the research note and the books both stress that treating any published
list as a fixed checklist is unsafe. This section is "current research" verified against the OWASP
GenAI Security Project's release, which moved from expert-vote-only ranking to blending expert
judgment with thousands of documented incidents. The ordering below is the OWASP GenAI LLM Top 10
2026 and should be re-checked before it is asserted as current; earlier editions differed, and later
ones will again.

1. Prompt Injection
2. Sensitive Information Disclosure
3. Excessive Agency
4. Supply Chain
5. Data and Model Poisoning
6. Unbounded Consumption
7. Misinformation
8. Hidden Context Exposure (formerly system prompt leakage)
9. Vector and Embedding Weaknesses
10. Improper Output Handling

The governance takeaway is not to memorize the order but to see the categories it normalizes and to
map them onto the controls in this reference: trust boundaries and least privilege answer the top
three; inventory and provenance answer supply chain and poisoning; monitoring, quotas, and cost caps
answer unbounded consumption; output validation and human-in-the-loop answer misinformation and
improper output handling.

## Where to Go Next

- **`foundations-and-principles.md`** — safety and human oversight as the principles security
  operationalizes.
- **`privacy-and-data-governance.md`** — the data-protection controls (exposure, retention,
  PETs) that security defends.
- **`ai-lifecycle-governance.md`** — where security reviews and red-teaming sit in the stage gates.
- **`risk-management-and-frameworks.md`** — NIST AI RMF and its Generative AI Profile, into which
  the OWASP categories map.
- **`regulatory-landscape.md`** — current law that turns some of these risks into legal duties.

---

### Synthesized from

This reference synthesizes (never reproduces) ideas from *The Developer's Playbook for LLM Security* and *Beyond the Algorithm*, and it is de-staled against the current state
by the mission research note on LLM/agent security (`research-llm-agent-security.md`) and a
verification of the OWASP GenAI LLM Top 10 2026 against the OWASP GenAI Security Project's published
release. All prose is an original paraphrase and synthesis of the ideas in these sources;
idea-level attribution is consolidated in `source-index.md`. Because the LLM/agent security
landscape changes quickly, the OWASP ranking and agentic guidance should be re-verified against
primary sources at use time. The security recommendations here are educational context, not legal
advice.
