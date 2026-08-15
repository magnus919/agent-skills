# Procurement, Third-Party, and Board Oversight of AI

This reference teaches the acquisition-side and governance-top-side of an AI program: how an
organization decides what to buy versus build, how it vets and manages the vendors, models, data, and
open-source assets it brings in from outside, how it keeps that third-party surface safe across the
supply chain, and how it reports the whole picture to the board with meaningful metrics and audit
backing. Its central message is that governance must reach beyond the models built in-house. A large
share of an organization's AI surface arrives through procurement — hosted models, pretrained weights,
data licenses, tooling, and consultants — so the discipline of due diligence and supply-chain
management is what turns board-level intent into working control, and board reporting with metrics is
what keeps leadership honestly informed. Read it alongside `risk-management-and-frameworks.md` (the
tiering and control machinery), `regulatory-landscape.md` (the legal duties that make third-party and
board exposure material), `governance-operating-model.md` (roles, councils, and the decision chain that
reaches the board), `ai-lifecycle-governance.md` (where vendor-built assets enter and leave the
lifecycle), and `llm-and-agent-security.md` (the supply-chain and plugin threats specific to LLM
systems). Use the `third-party-due-diligence.md` template to run a vendor or model intake and the
`board-ai-governance-report.md` template to structure the periodic reporting this reference describes.
This is educational context, not legal advice.

## Why Procurement and Board Oversight Belong Together

Two observations pull third-party risk and board oversight into one discipline. The first is that AI
is increasingly procured rather than invented. Hosted model APIs, pretrained open-source weights,
curated datasets, ML platform tooling, and specialized consultancies supply a large share of the
systems an enterprise actually runs. When an AI system fails — it is biased, it leaks data, it makes
a consequential error — the organization is accountable for that failure even if the flawed component
came from a vendor it did not build. The second is that the board, not the engineering team, carries
the ultimate duty of oversight. Fiduciary expectations and enforcement pressure mean leadership cannot
delegate AI risk away and call it handled; it must be informed, ask pointed questions, and see
reporting that reflects reality.

The two themes reinforce each other. Third-party diligence produces the evidence a board needs to make
acquisition and risk decisions, and board reporting produces the accountability that forces the
procurement function to keep its diligence current. A governance program that treats vendor risk as an
engineering-only concern, or board reporting as a cosmetic slide deck, fails on both sides of the
chain. The practical shape of a working program is a documented accountability chain that runs from a
named owner on a procurement or due-diligence intake, through a governance council or risk committee
that reviews higher-risk acquisitions, up to a board committee that receives a metrics-backed report on
a fixed cadence.

## Third-Party and Vendor Due Diligence

Due diligence is the disciplined practice of investigating a proposed third-party engagement — a
vendor, a model, a dataset, or a consultancy — before you commit to it, so that you accept risk with
your eyes open rather than discover it after signing. The goal is not to refuse every external
dependency; it is to characterize what you are bringing in, what it could harm, and what you need to
protect yourself with in the contract and the controls.

### A due-diligence intake should answer before engagement

- [ ] **What is the component and how is it used?** Classify the engagement: a hosted model API, an
      open-source weight, a licensed dataset, an ML platform, or a professional service. State the use
      case it supports and the tier it lands in under `risk-management-and-frameworks.md`.
- [ ] **Who owns and operates it?** Identify the provider, its location and jurisdiction, its size and
      financial stability, and whether it is subject to any regime relevant to the data you will share
      (see `regulatory-landscape.md`).
- [ ] **What data flows to the vendor?** Enumerate inputs and outputs. Whether data is personal,
      regulated, proprietary, or open determines lawful-basis, transfer, and confidentiality duties.
- [ ] **What does the vendor do with our data and the model?** Ask about training, retention, storage
      location, subprocessors, and whether inputs can be retained or reused in ways you cannot accept.
- [ ] **What controls does the vendor actually operate?** Request evidence of security, privacy, and
      governance controls — certifications, audits, incident-response capability, and model-governance
      practices — rather than accepting assertions at face value.
- [ ] **What happens when things go wrong?** Confirm the vendor's incident-notification commitments,
      uptime and performance commitments, liability and indemnity terms, and the exit path.
- [ ] **Can we verify it?** Build in rights to audit or at least to review evidence, so diligence is not
      a one-time event.

Diligence should be proportional to risk. A low-impact internal productivity tool and a system making
consequential employment or credit decisions are not the same due-diligence job. The proportionality
lens in `risk-management-and-frameworks.md` — inherent risk, impact, and likelihood — should drive how
deep the investigation goes and how many signatures the intake needs.

### Common pitfalls in diligence

- Diligence that happens *after* the contract is signed, when leverage is gone.
- Accepting vendor claims without independent verification or the right to inspect evidence.
- Ignoring the full chain — the vendor's own suppliers and subprocessors — rather than just the direct
  counterparty.
- Treating diligence as a static document instead of a living file that is revisited when the system,
  the vendor, or the risk profile changes.
- Failing to record the outcome so a board or audit can see how a decision was reached.

## Supply Chain Risk

Supply chain risk is the modern, expanded form of third-party risk. Traditional manufacturing tracked
every part and its source through a bill of materials; software and AI face the same problem with far
more moving pieces and far fewer guarantees. For AI systems the supply chain includes not only hosted
services and licensed data but pretrained model weights, model registries, open-source libraries,
training data of uncertain provenance, and LLM plugin extensions. A vulnerability in any of these can
infect the finished system, introduce bias, leak data, or make the model behave unpredictably in
production.

### Why AI supply chains are fragile

- **Pretrained and open-source models are reused at scale.** Model registries host thousands of models
  that teams fine-tune or embed without always knowing their origin, training data, or weaknesses.
  Their convenience and low cost hide genuine uncertainty about integrity and lineage.
- **Dependencies multiply silently.** The software libraries, plugins, and packages that surround a
  model often have weak version tracking and can carry their own vulnerabilities.
- **Data provenance is hard to guarantee.** Training or operational data gathered from external or
  crowd-sourced sources can be tampered with, biased, out of date, or drawn from material you have no
  right to use.
- **Models go stale and unsupported.** A model that served well can hit end-of-support, leaving no
  security updates and creating drift and exposure over time.

### BOMs for AI

Just as a software bill of materials (SBOM) lists every component in an application, an **AI bill of
materials (AI BOM)** records, component by component, what an AI system is assembled from: the model
and its architecture, the data
sources used for training, the libraries and dependencies, how the model is used or deployed, and the
assumptions and attestations behind it. Maintaining an AI BOM delivers several practical benefits:

- **Transparency and traceability** of what is really inside a system, so developers, auditors, and
  stakeholders can assess quality, reliability, and security.
- **Faster root-cause work** when a system fails, shows bias, or is breached — you can identify the
  problematic component quickly instead of hunting through an undocumented stack.
- **Due-diligence and compliance evidence** that the organization can show to auditors, regulators, and
  the board.
- **Contingency planning** for high-risk third-party AI systems: knowing what the system depends on lets
  you plan for failure or incident response.

SBOMs are increasingly expected in regulated environments and are being mandated for software sold to
governments, so AI governance programs should treat component-level transparency as a baseline
expectation rather than a nice-to-have.

### Supply-chain threats to monitor

- Outdated or vulnerable third-party packages and dependencies.
- Reliance on a vulnerable or untrusted pretrained model for fine-tuning.
- Training on tampered crowd-sourced or external data.
- Using end-of-support models or libraries with no security updates.
- Ambiguous terms and privacy policies that allow misuse of sensitive or copyrighted data.

Because LLM systems amplify these threats — model manipulation, data poisoning, and malicious plugin
behavior all travel through the supply chain — read this section together with `llm-and-agent-security.md`
for the specific attack surface.

## Managing the Vendor Lifecycle

Due diligence is the entry point, but third-party risk is a lifecycle, not a form. A working vendor
management program covers onboarding, continuous monitoring, and exit.

### Onboarding

Onboarding is where diligence becomes an enforceable relationship. The contract should encode the
commitments identified during diligence: data-handling and retention rules, subprocessor disclosure,
incident notification windows, performance and uptime targets, liability and indemnification, and the
right to verify compliance. Roles and responsibilities should be explicit — who inside the organization
owns the relationship, who monitors the vendor, and who gets escalated to. Without a written onboarding
record, the diligence that justified the relationship is lost and cannot be reviewed or audited later.

### Continuous monitoring

The relationship is not a one-time deal. Recurring review should track the vendor's actual performance
against commitments, watch for changes in the vendor's controls, ownership, or financial health, and
recheck the system as it or the surrounding risk profile evolves. How you observe the vendor can range
from automatically collected system telemetry to scheduled reviews, structured surveys, and interviews,
supplemented by the incident and violation reports the contract requires them to surface. When a
materially risky third-party AI system is involved, this monitoring should be explicit and documented
— a gap that surfaces only at incident time is a governance failure.

### Exit

Exiting a vendor should be planned before you need it. What happens to the data the vendor holds when
the contract ends? What is the migration path for the models or services that depended on it? Building
exit terms into the contract at onboarding — data return or deletion, transition assistance, and
notice periods — prevents a procurement decision from becoming a lock-in liability later. The
board-reporting cadence should surface material dependency concentrations so the organization is not
surprised by its own reliance on a single vendor.

## Board Oversight and Fiduciary Duty

Board oversight of AI is no longer a forward-looking nicety; it has become a recognized director
responsibility. The legal anchor, especially in the United States, is the fiduciary duty of oversight
rooted in the 1996 Delaware *Caremark* decision. Under that standard, directors act improperly if
they knowingly let the corporation run without a sound information and reporting apparatus, or if
they neglect to track management and thus stay in the dark about risks that called for their
attention. Recent cases have tested whether that duty reaches "mission critical" risks — the same
kind of exposure courts already attach to cybersecurity, and one that commentators expect to extend
to high-impact AI shaping consequential outcomes such as hiring, lending, health, and similar
decisions.

### Applying a fiduciary mindset to AI

- **Treat AI as strategy and risk, not just technology.** Boards should understand which AI systems are
  mission critical, how they affect employees, customers, stakeholders, and the environment, and how
  they create or destroy value.
- **Oversee compliance.** Directors should ensure management has assigned clear responsibility for
  AI-related legal and regulatory compliance and risk mitigation, and that there are AI-specific
  policies and guidance in place.
- **Stay informed without operating.** The governing discipline is often summarized as "noses in,
  fingers out": a board should observe enough to direct well but never slip into hands-on management.
  The failure mode is the reverse — ignoring mission-critical AI risk by failing to hand monitoring
  responsibility for a safety- or compliance-critical AI system to any committee.
- **Assign committee responsibility.** AI risk should be mapped to a specific board committee (audit,
  risk, or a dedicated technology or AI committee) so it has a defined owner, not an ambiguous
  "everyone and no one."
- **Demand director education.** When directors across the board lack AI expertise, that gap is itself
  a governance risk; boards should invest in their own learning so their questions are substantive
  rather than perfunctory.

The arrangement the leading guidance keeps converging on is a documented accountability chain: the
board or a named committee holds oversight, an internal AI ethics or governance council weighs policy
and clears the higher-risk use cases, and named owners or stewards at the operating level handle the
day-to-day controls. That chain is exactly the operating model described in
`governance-operating-model.md`.

### When oversight becomes exposure

Enforcement is making AI governance material to directors. Regulators are pursuing "AI washing" —
marketing claims that overstate AI capability or responsibility — and taking action on AI-related
misconduct, while Delaware-style oversight doctrine continues to be tested for mission-critical AI. The
practical consequence is that boards cannot treat AI as a technical or compliance matter that is fully
delegated away. Being able to show an informed, recurring review process with named responsibility is
itself a governance control that reduces both legal exposure and the chance of being blindsided by an
AI failure.

## Board Reporting with Metrics

Board reporting is how oversight becomes real rather than nominal. Reporting turns the noisy detail of
day-to-day governance into a compact, decision-useful picture that directors can actually evaluate, and
it forces management to define what good looks like. Without metrics, a board report is an opinion;
with the right metrics, it is a state of the system.

### What a reporting cadence should cover

- [ ] **Inventory and tiering:** how many AI systems exist, their risk tiers, and how the portfolio is
      shifting.
- [ ] **Material risks and incidents:** the highest-risk systems, their residual risk, and any material
      incidents or near-misses since the last report, including briefings on those that need prompt
      attention.
- [ ] **Compliance and regulatory exposure:** open obligations, audit findings, and any enforcement or
      investigation activity (see `regulatory-landscape.md`).
- [ ] **Third-party and supply-chain posture:** concentration on critical vendors, outstanding
      diligence, and material supply-chain or model events.
- [ ] **Governance operations:** status of policies, council decisions, approvals, and the state of the
      control environment.
- [ ] **Progress against goals:** how the program is advancing against the board-approved objectives and
      any identified gaps.

### Choosing metrics that actually inform

Metrics should be chosen to tell directors whether the system is safe, compliant, and being governed —
not to flatter the program. Good candidates include:

| Type | Example indicators |
|---|---|
| Exposure | Count of systems by risk tier; coverage of systems with a named owner; material-vendor concentration |
| Control | Percentage of high-risk systems with completed risk assessments, model cards, or monitoring; audit findings open versus closed |
| Performance | Drift alerts, accuracy or fairness metric regressions, system availability, mean time to resolve incidents |
| Compliance | Number of open compliance obligations, incidents reported to regulators, outstanding audit recommendations |
| Third-party | Vendors with current vs overdue diligence, data flows that lack a documented lawful basis, open supply-chain findings |
| Incidents | Number and severity of AI incidents in the period, time to detect and to remediate |

The metric set will differ by organization, but it should be **stable enough to trend over time**,
**comparable across periods**, and **honest** — a metric that never changes or never shows a problem is
a signal the wrong thing is being measured. This reporting structure is implemented concretely in the
`board-ai-governance-report.md` template.

### Cadence and escalation

Recurring review should be on a fixed cadence — commonly at least quarterly, with a standing
board-level agenda item — so AI risk is not buried until an incident forces attention. Beyond the
recurring report, there should be a defined escalation path for material AI incidents so the board or
its committee is briefed promptly when something rises to that threshold, rather than at the next
scheduled meeting. Management should prepare, own, and be accountable for the report's accuracy; the
board should ask questions and challenge the answers, which is the entire point of the exercise.

## Audit

Audit is the independent check that the controls and reporting described above actually exist and work.
It is what converts a self-reported governance program into one that can withstand scrutiny from
regulators, customers, and the board itself. Audit sits alongside monitoring: monitoring is continuous
and operational, while audit is a structured, independent examination against stated criteria.

### The role of audit in AI governance

- **Independent verification:** an auditor (internal audit, or an external third party) evaluates
  whether the program's controls — diligence records, model cards, monitoring, tiering — are in place
  and effective, rather than taking management's word for it.
- **Evidence for the board:** a clean audit gives the board confidence that reported metrics reflect
  reality; findings give it a concrete list of what to fix.
- **Finding what monitoring misses:** because monitoring is designed by the same people who run it,
  audit offers an outside view that can surface gaps, exceptions, and weaknesses that daily operations
  overlook.
- **Due-diligence credibility:** the right to audit, or to receive audit evidence from a vendor, is a
  powerful procurement tool — it forces suppliers to demonstrate the controls they claim.

### What a program should be able to show an auditor

- The inventory and tiering of all AI systems, including those procured from third parties.
- Completed due-diligence records and an AI BOM or equivalent component-level transparency for each
  material system.
- Risk assessments, model cards, and monitoring evidence tied to each system (see
  `risk-management-and-frameworks.md` and the `model-card.md` template).
- A documented accountability chain from named owners up through a council to a board committee.
- The metric set and reporting cadence used for the board, with a track record of actual reports.
- Incident logs and evidence that material incidents were escalated and remediated.
- Exception registers and the process for approving and tracking waivers.

An audit is most valuable when it is genuinely independent and when its findings are acted on. A
governance program should treat audit findings as a feedback loop that feeds back into diligence,
monitoring, and reporting, so the system improves rather than merely passing the next check.

## A Practitioner's Workflow

- [ ] **Classify and tier** every external AI engagement on intake, and route higher-risk ones for
      deeper diligence and sign-off (see `risk-management-and-frameworks.md`).
- [ ] **Run due diligence** before contract, proportional to risk, and record the outcome.
- [ ] **Maintain an AI BOM** for each material system so the supply chain is transparent and auditable.
- [ ] **Encode commitments in the contract** at onboarding, including the right to verify, and assign a
      named owner.
- [ ] **Monitor continuously** and revisit diligence when the system, vendor, or risk profile changes.
- [ ] **Plan the exit** before you need it.
- [ ] **Report on a fixed cadence** with stable, honest metrics and a defined incident-escalation path.
- [ ] **Audit independently** and feed findings back into the program.

## Where to Go Next

- **`risk-management-and-frameworks.md`** — the tiering and risk-assessment machinery that determines
  how deep diligence and reporting must go.
- **`governance-operating-model.md`** — the councils, stewards, and accountability chain that run from
  the board down to named owners.
- **`regulatory-landscape.md`** — the legal duties that make third-party and board exposure material.
- **`llm-and-agent-security.md`** — the supply-chain, plugin, and model-specific threats for LLM
  systems.
- **`ai-lifecycle-governance.md`** — where vendor-built assets enter and leave the model lifecycle.
- Use the **`third-party-due-diligence.md`** template to run a vendor or model intake and the
  **`board-ai-governance-report.md`** template to structure board reporting.

---

### Synthesized from

This reference synthesizes the acquisition, supply-chain, vendor-management, reporting, and audit
material from *The AI Product Manager's Handbook* and from *Developing Cybersecurity Programs and
Policies* (the fourth edition, written for an AI-driven world), together with the mission research note
on organizational and board governance (`research-org-board-governance.md`, current to August 2026). The
research note supplies the current
fiduciary, board-oversight, and third-party expectations; the two books supply the procurement,
vendor-lifecycle, supply-chain, BOM, reporting-metric, and audit mechanics. All prose is an original
paraphrase and synthesis of the ideas in these sources; no passage is reproduced verbatim, and
idea-level attribution is consolidated in `source-index.md`. This reference is educational context, not
legal advice, and the in-flux regulatory and case-law elements it touches should be verified against
primary sources at use time.
