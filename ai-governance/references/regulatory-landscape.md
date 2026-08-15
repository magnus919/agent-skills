# AI Regulatory Landscape

This reference teaches the current obligations organizations face across the major AI
jurisdictions, with an eye to what enforcers actually do. Its central message is that AI
compliance is now a *place-based* problem: the same model can be lawful to sell in one country,
illegal to deploy in another, and only lightly regulated in a third. Rather than one global rule,
there are several converging but distinct regimes — the European Union's horizontal AI Act, the
General Data Protection Regulation (GDPR), a fragmented United States patchwork, the United
Kingdom's context-based approach, and China's binding sectoral measures — and a governance program
must map each system to each regime by its risk tier and its geographic footprint. This reference
is authoritative on the current state, built from the mission research note on the regulatory
landscape (research-regulatory.md); the regulatory chapters of the source books are treated here
as historical context only, because the law has moved materially past their 2023–2025 publishing
dates. Read it with `risk-management-and-frameworks.md` (the NIST/ISO machinery a compliance program
applies), `procurement-third-party-and-board-oversight.md` (the board-level obligations that flow
from these laws), and `llm-and-agent-security.md` (where security duties become legal duties). Use
the [model-risk-assessment.md](../templates/model-risk-assessment.md) and [board-ai-governance-report.md](../templates/board-ai-governance-report.md) templates to record the
regulatory mapping this reference describes. It is not legal advice, and the in-flux sections it
flags must be verified against primary sources at use time.

## Why Regulation Is the Fastest-Moving Input to AI Governance

The first practical fact for a governance practitioner is that the regulatory map changes faster
than almost any other input to the discipline. The laws themselves are recent — the EU AI Act was
only adopted in 2024 — and the deadlines, fines, and even the *existence* of a rule have shifted
during the writing window of the source books. *Responsible AI in the Enterprise*, for example,
described a compliance landscape in which the EU was still finalizing its AI regulation and the
United States had no unified federal framework; that general shape is still accurate, but the
specific obligations have since become far more concrete in Europe and remain genuinely unsettled
in the United States. The books are therefore a reliable guide to the *principles* a compliance
program should embody — risk-based tiering, documentation, accountability, human oversight — but
not to the *current* deadlines or penalty levels. Any serious governance program should track
primary regulator sources continuously rather than rely on a static reference like this one.

A second practical fact is that compliance is increasingly a risk-tier exercise. Most AI in use
today sits in a "minimal risk" bucket that no regime newly regulates, while a small set of
highest-risk uses — biometric identification, employment and credit decisions, critical
infrastructure, influence over public life — draws the heaviest duties. The governance skill
overall, and the risk-tiering in `risk-management-and-frameworks.md`, exists precisely to answer
"which tier is this system, and therefore what must we do." Regulation supplies the legal
underpinning for that tiering, but the analytical work is the same everywhere: characterize the
system's data sensitivity, autonomy, and potential for harm, then apply the rules that attach to
that characterization in each jurisdiction where the system is deployed.

## European Union: The AI Act as the Global Baseline

EU Regulation 2024/1689 — the AI Act — is the world's first comprehensive, horizontal AI statute,
and it has effectively become the reference point other jurisdictions either imitate or explicitly
reject. Its reach extends to *providers* (who put an AI system or general-purpose AI (GPAI) model
on the market) and to *deployers* (who use one), whenever they operate in or serve the EU market.
Its organizing idea is a **four-tier risk pyramid**:

| Tier | What it covers | Consequence |
|---|---|---|
| Unacceptable | Prohibited practices (harmful manipulation, social scoring, scraping untargeted facial imagery, emotion recognition in workplaces or schools, and live remote biometric ID in public places) | Banned outright |
| High-risk | AI in sensitive areas (biometrics, critical infrastructure, education or employment, migration and asylum, plus border control) and AI embedded in regulated products | Strict duties before and after market placement |
| Limited / transparency | Generative AI and chatbots that interact with people or produce content | Disclosure and labelling duties |
| Minimal | The large majority of ordinary AI | Largely unregulated by the Act |

The AI Act does not switch on all at once; its obligations arrive in phases. The bans on prohibited
practices and the AI-literacy duties have been live since February 2025. From 2 August 2025, makers
of general-purpose models took on duties covering transparency, copyright, and, for the most
capable models, systemic-risk management. Commission guidance published in 2025 sets out when a
model qualifies as general-purpose, adopts a pragmatic view that only providers making substantial
changes are caught, and describes the open-source carve-outs. Then, in August 2026, fresh
transparency duties arrived for those who build or run generative systems: telling users when they
are conversing with a machine, and labelling AI-made images, audio, deepfakes, and public-facing
text.

### EU high-risk timing: verify against current state

> **Currency flag.** The most consequential recent change is the deferral of the high-risk
> obligations. Under the original schedule, the central high-risk duties would have started on
> 2 August 2026. The AI Omnibus — floated by the Commission in November 2025, politically agreed in
> May 2026, and effective from 27 July 2026 — pushed those dates out. High-risk systems in areas
> like biometrics, critical infrastructure, education and employment, migration and asylum, and
> border control now face strict rules from 2 December 2027, while high-risk systems embedded in
> regulated products like lifts and toys follow from 2 August 2028. **Because this timeline is in active flux
> and subject to litigation and further amendments, verify the effective dates against the European
> Commission's current publications at the time you rely on them.** The deferral buys organizations
> a window, but it also leaves real uncertainty about the final scope once the supporting standards
> mature.

When the high-risk rules do bite, they are heavy and practical. Owners must carry out risk
assessment and mitigation, feed models with datasets curated to reduce discrimination, log activity
for traceability, keep documentation examinable by authorities, give deployers clear instructions,
build in human oversight, and hit exacting targets for robustness, security, and accuracy.
Deployers owe duties of their own for oversight, monitoring, and notifying serious incidents.
Compliance machinery should be built to these duties *now*, even where the hard deadline has
slipped, because the obligation set is not going away — only its start date.

## Enforcement and Penalties in the EU

Enforcement is split between the AI Office at the European Commission and the authorities of the member states. The
AI Office took charge of general-purpose models in August 2026, with authority to demand technical
docs, run evaluations, order corrective measures, and impose penalties; that same day the
Commission's broader enforcement and the new transparency rules also went live. Behind all this sit
the AI Board, plus a Scientific Panel and an Advisory Forum, along with practical fixtures such as a service
desk, a channel for whistleblowers, and a complaints mechanism.

The penalty ceiling is what makes the AI Act a board-level concern. Fines can reach **EUR 35
million or 7% of global annual turnover** for the gravest breaches, with violations tied to
general-purpose models capped at EUR 15 million or 3% of turnover. These figures mirror the scale
of GDPR penalties and make AI compliance an enterprise-risk matter, not an engineering checkbox.
The compliance angle is to treat the AI Act as carrying roughly the same organizational weight as
GDPR, with the same need for accountability, audit trail, and senior ownership.

### GDPR and the AI Act as complementary duties

The AI Act does not displace the GDPR; systems touching personal data stay squarely within
data-protection law. The two regimes overlap rather than collapse into one another: the AI Act
governs a system's design and risk profile, while the GDPR governs the data flowing through it —
lawful basis, transparency, minimization, data-subject rights, and accountability. The European
Data Protection Board's Opinion 28/2024 is the key EU data-protection gloss on AI: it explains when
a model counts as processing under the GDPR and how duties like lawful basis, transparency, and
accountability flow into AI workloads. Governance practitioners should treat the two as
complementary — a compliant AI system satisfies both its AI-Act risk-tier duties and its GDPR data
duties, and a compliance plan should document each separately rather than assume one implies the
other.

## United States: Federal and State Patchwork

> **Currency flag.** The U.S. position is the least settled of the major jurisdictions. There is no
> comprehensive federal AI statute as of the date of this reference; rule-making proceeds through
> executive action and existing agency authority (above all the Federal Trade Commission), and
> a rapidly growing and actively litigated body of state law. **Because federal policy can change
> with each administration and state laws are being enacted, amended, challenged, and enjoined
> month to month, verify the current federal and state position against primary sources at the time
> you rely on it.**

At the federal level, policy has swung with the executive. An executive order from January 2025,
EO 14179, scrapped the prior administration's AI directive and ordered an AI Action Plan, which
appeared that July. A White House order in December 2025 championed one national policy and
criticized what it called "onerous and excessive" state rules, and a 2026 national AI framework then
called on Congress to unify the field federally. What this means in practice is that federal
*guidance* can shift direction quickly even while the underlying agency powers (especially FTC
authority over unfair and deceptive practices) remain available to police harmful AI conduct.

At the state level the picture is a genuine patchwork. Colorado's SB 24-205 was America's first
broad consumer-protection AI statute, yet its rollout was delayed and a Colorado court in 2026
temporarily stopped the state attorney general from applying it, following legal challenges.
California, Texas, Illinois, Connecticut, and Utah are among the states that have passed or are
progressing their own measures on algorithmic bias, deepfakes, and AI in hiring; more than a
thousand AI bills surfaced in statehouses in a single recent year. For governance practitioners,
this means the practical compliance surface is both broad and shifting: a national deployer must
track a growing set of state-specific duties, monitor which are actually in force versus enjoined,
and treat the federal pre-emption question as genuinely open.

## United Kingdom: Context-Based and Sectoral

The UK has not enacted its own AI law; it governs AI by the context of use, leaning on current
regulators and legal regimes. That stance, set out in a March 2023 white paper that framed AI
regulation as a pro-innovation exercise, has been kept by the Labour government, which argues that
most AI should
be overseen where it is used and that sector specialists are the right overseers. Oversight is
spread among bodies like the ICO (for data protection), the FCA, the CMA, and Ofcom, which polices
online services including AI chatbots under the 2023 Online Safety Act. A promised statutory scheme
for the most advanced frontier models has still not been passed into law, so frontier-model
governance in the UK today rests more on the voluntary and safety-research side, including the UK
AI Safety Institute, than on statute.

The compliance angle for the UK is that obligations are *sector- and context-specific* rather than
a single horizontal law: the same system may face data-protection duties from the ICO if it touches
personal data, consumer-protection and competition duties if it reaches consumers, and
platform-safety duties if it operates as an online service — but there is no one UK AI statute to
map against. Governance programs with UK exposure should therefore map each use case to the
relevant sectoral regulator and treat "is this AI subject to UK rules" as a question answered per
context.

## China: Binding Sectoral Measures

China lacks one overarching AI statute yet runs what many consider the world's densest set of
binding, sector-specific AI rules, largely administered by a single body, the Cyberspace
Administration of China (CAC). The cornerstone instruments are the recommendation-algorithm and deep-synthesis regulations
plus the August 2023 Interim Measures for generative-AI services, which load providers with
content, safety, and data duties. Draft rules on anthropomorphic AI chat services, covering
chatbots and virtual companions, were released by China in 2026. Beijing's regime pairs innovation
goals with tight curbs on content, data security, and national interest, and the "AI+" program
within the current five-year plan signals continued growth.

For multinationals, the compliance takeaway is that China adds a substantial, *distinct* compliance
surface on top of the EU, US, and UK frameworks — content controls and data-security duties that
have no direct EU or US analogue and that apply to providers operating within or serving the
Chinese market. A governance program cannot assume that a system compliant in the EU or US is
compliant in China; the obligations are qualitatively different and require separate mapping.

## Sectoral Rules: Where Horizontal and Vertical Law Meet

Beyond the horizontal regimes, AI is increasingly caught by sectoral law that was not written for
AI but applies to it. Financial services, health care, employment, and consumer protection each
carry existing duties that an AI system inherits when it operates in that sector. Two patterns
matter for governance:

- **AI Act as a coordinating layer:** in the EU, the AI Act explicitly clarifies its relationship
  with sectoral product-safety legislation (such as the Machinery Regulation) to avoid duplicating
  rules, so a system already governed by a sectoral regime must still satisfy its AI-Act risk-tier
  duties where applicable.
- **Sectoral duties as independent obligations:** in the US and UK especially, AI deployed in a
  regulated sector is bound by that sector's existing rules — fair-lending and employment law, for
  example, apply to an AI that makes or informs credit and hiring decisions regardless of whether
  a dedicated AI statute exists.

The governance implication is a **mapping discipline**: for each AI system, record the horizontal
regimes (AI Act, GDPR, and any applicable US/UK/China law) *and* the sectoral rules that the system
inherits from the domain it operates in. `risk-management-and-frameworks.md` and the
[model-risk-assessment.md](../templates/model-risk-assessment.md) template provide the structure for recording this mapping.

## A Practitioner's Compliance Workflow

- [ ] **Inventory:** maintain a model/system inventory (see `ai-lifecycle-governance.md`) with the
      jurisdictions where each system is offered or deployed.
- [ ] **Tier:** characterize each system's risk tier per the EU AI Act's categories and any local
      analogues (see `risk-management-and-frameworks.md`).
- [ ] **Map:** for each system, list the horizontal regimes (AI Act, GDPR, US federal/state, UK
      sectoral, China sectoral) that apply in each deployment location.
- [ ] **Assign duties:** translate each applicable rule into concrete obligations — documentation,
      logging, human oversight, transparency, data minimization — and record them.
- [ ] **Track currency:** subscribe to primary regulator sources (European Commission, EDPB, FTC,
      relevant state AGs, UK ICO, CAC) and re-verify the in-flux sections flagged in this reference
      on a fixed cadence.
- [ ] **Report:** surface material obligations and penalty exposure to the board (see
      [board-ai-governance-report.md](../templates/board-ai-governance-report.md)).

## Horizon Scanning: What to Watch

- **EU:** the final scope of the high-risk obligations once the deferred deadlines arrive and the
  supporting standards mature; how the AI Act, GDPR, and sectoral rules interact in enforcement
  practice.
- **US:** whether a federal pre-emption framework is enacted; the outcome of litigation over state
  laws like Colorado's; how the FTC exercises existing authority over AI.
- **UK:** whether the planned binding regulation of frontier models is enacted, and how the
  sectoral regulators coordinate on cross-cutting risks.
- **China:** the scope of the draft chatbot/virtual-companion rules and continued expansion of
  generative-AI content and data duties.

## Where to Go Next

- **`risk-management-and-frameworks.md`** — the NIST AI RMF and ISO/IEC 42001 machinery a
  compliance program applies to meet these legal duties.
- **`procurement-third-party-and-board-oversight.md`** — how regulatory obligations surface in
  third-party due diligence and board reporting.
- **`ai-lifecycle-governance.md`** — where regulatory checks and documentation sit in the model
  lifecycle.
- **`llm-and-agent-security.md`** — security duties that become legal duties under these regimes.

---

### Synthesized from

This reference is authoritative on the current state, built from the mission research note on the
regulatory landscape (research-regulatory.md, current to August 2026). The regulatory chapters of
the source books — primarily *Responsible AI in the Enterprise* and *Beyond the Algorithm* — are
treated as historical context only, because the obligations described there have moved materially
past their publication dates. All prose is an original paraphrase and synthesis of the ideas in
these sources; idea-level attribution is consolidated in `source-index.md`. Because the EU AI Act
high-risk timeline and the entire US federal/state landscape are in active flux, those sections are
explicitly flagged for verification against primary sources at use time. This reference is
educational context, not legal advice.
