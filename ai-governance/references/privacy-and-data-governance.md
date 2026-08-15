# Privacy and Data Governance

This reference teaches how to govern the data that feeds and runs AI systems, and how to protect
the individuals whose information flows through those systems. Its central message is that privacy
and data governance are two halves of the same discipline: data governance supplies the ownership,
lineage, and quality that make data trustworthy and auditable, while privacy supplies the limits —
consent, minimization, retention, and protective techniques — that keep that data from causing
harm. It synthesizes (never reproduces) ideas from *Designing Data Governance from the Ground Up*,
*Data Governance Handbook*, and *Platform and Model Design for Responsible AI*, and it marks
"current research" where the 2023–2025 books are de-staled by recent regulation. Read it with
`foundations-and-principles.md` (which names privacy as a governing principle),
`ai-lifecycle-governance.md` (where data and model lineage surface at stage gates), and
`llm-and-agent-security.md` (the security half of data protection). Use the [model-card.md](../templates/model-card.md) and
[model-risk-assessment.md](../templates/model-risk-assessment.md) templates to record the data practices this reference describes. It is
not legal advice; data-protection duties should be confirmed against current law at use time.

## Data Governance Is the Foundation

*Data Governance Handbook* describes data governance as the deliberate alignment of people,
processes, and technology so that an organization delivers the correct data, to the right place,
under appropriate safeguards, and thus enables effective and safe use. The book treats governance as
an ongoing activity carried through several cooperating capabilities rather than one standing rule:
managing metadata, tracing lineage, assuring data quality, shaping data architecture, mastering core
reference data, and running data operations. Each capability
answers a concrete question — where data came from, how trustworthy it is, how it is classified,
who may use it — and together they turn a collection of scattered files into a governed, queryable
asset.

A useful mental model from the same book is to treat data as both asset and liability. Data is an
asset when it creates measurable value — a curated, well-owned dataset that many teams can rely on,
or a model that drives revenue. Data becomes a liability when it introduces risk, for example
records that were never catalogued, were never classified and secured, or have leaked. The goal of a governance
program is to grow the asset side and shrink the liability side, which the book calls creating
"data equity." This framing matters for AI because model quality and privacy risk both trace back
to how well the underlying data is owned and controlled; a model is only as trustworthy as the data
that trained it, and only as safe as the controls around the data it uses.

For AI specifically, the discipline splits into two regimes that this reference keeps distinct:

| Regime | What it governs | Typical questions |
|---|---|---|
| Training-data governance | The datasets used to fit and validate a model | Who owns this corpus? Where did it come from? Is its use authorized? |
| Operational-data governance | The data a deployed model ingests and produces | What PII flows in and out? Who may see it? How long is it kept? |

The two share the same toolkit — ownership, lineage, quality, and retention — but pose different
risks, so a governance program should treat them separately rather than folding them into one
bucket.

## Ownership and Accountability

Data governance begins with answering "who owns this data?" Both *Data Governance Handbook* and
*Designing Data Governance from the Ground Up* make ownership the first building block, because
accountability is impossible without a named owner. *Designing Data Governance from the Ground Up*
argues that data stewards are the human heart of governance: they own the strategic and tactical
decisions about data within their domains, act as trusted advisors on its meaning and limits, and
provide the context that data engineers and scientists need to use it correctly. Stewards can come
from business or technical roles; a sales director who knows the customer dataset is often a better
owner than an engineer who merely processes it, because ownership is about understanding and being
answerable, not just about touching the data.

The book distinguishes two stewardship flavors that should both be populated:

- **Business stewards** are accountable for the data used across business processes and workflows —
  the classification scheme, the business definitions, the quality expectations — and write the
  documentation that makes data usable across departments.
- **Technical stewards** own data for systems and pipelines — the metadata parameters, the marts and
  warehouses, the models and algorithms, the access limits that decide who can see and change data.

The same split appears in *Data Governance Handbook*, which assigns data-domain executives and data
stewards per functional area and pairs them with technical stewards who carry out the mechanics.
Both books stress a common failure: stewards may be experts in their data yet lack the authority to
enforce decisions. A governance program must give owners real decision rights, visibility, and
recognition, or ownership becomes an empty title. In AI terms, every training dataset and every
production data feed should have a named accountable owner who can answer for its provenance, its
authorized use, and its quality.

## Data Lineage and Provenance

Ownership is only useful if you can trace what a piece of data actually is and where it has been.
*Data Governance Handbook* treats data lineage as one of the core capabilities, and *Designing Data
Governance from the Ground Up* defines lineage as confirming the origin of data and the path it took
to reach its current state. Lineage underpins transparency and root-cause analysis: when a model
produces a wrong or harmful output, lineage is what lets you walk the trail backward from the result
to the source dataset and the transformation that introduced the problem. *Platform and Model Design
for Responsible AI* extends the idea to the model itself, arguing that data and model lineage should
be captured across the pipeline so that any deployment can be reproduced from its inputs.

For AI governance, lineage should cover at least three layers:

- **Data lineage.** Where each training or operational dataset originated, how it was collected or
  acquired, what transformations it passed through, and which version is in use.
- **Feature lineage.** Which engineered features were derived from which source columns, and with
  what definitions — important because a seemingly innocent feature can encode sensitive or biased
  information.
- **Model lineage.** Which model version was trained on which data snapshot, with which
  hyperparameters, feeding which deployed artifact.

Lineage is what converts "we used some data" into "we can reconstruct exactly what the system
ingested and why," which is essential for audits, incident response, and compliance inquiries. In
practice it is delivered through a data catalog and metadata management layer that records business
and technical metadata for every critical data element (the *Data Governance Handbook* lists
descriptions, schemas, business definitions, and data classification among the required catalog
fields).

## Data Quality

Data that is not trustworthy cannot be governed safely, so quality is a prerequisite for both
privacy and model reliability. *Data Governance Handbook* defines data quality simply as ensuring
data is "fit for use": the data meets the standards of accuracy, completeness, and timeliness needed
for the analytical or operational purpose at hand. The book recommends establishing data quality
rules for each critical data element, enabling monitoring on those elements, publishing transparent
quality dashboards, and creating remediation plans for material issues. *Designing Data Governance
from the Ground Up* ties quality to the cost side of the ledger, noting that poor-quality data costs
organizations heavily and that stewards are responsible for defining and conducting quality
assessments against agreed business metrics.

Quality work in AI is doubly important because defects compound: a small error in a training
dataset can become a systematic bias in a model, and a stale production feed can silently degrade
predictions. Governance should therefore treat data quality not as a one-time clean-up but as an
ongoing, monitored property with named owners, explicit rules, and visible measurement — the same
discipline that `ai-lifecycle-governance.md` applies to the model itself. Where quality gaps cannot
be fixed, they should at least be disclosed so that users and reviewers know the limits of what the
data can support.

## Consent and Lawful Basis

Privacy law, above all the GDPR, governs when personal data may be collected and used at all.
Because the primary AI books predate much of the current enforcement picture, this section marks
"current research." Under the GDPR (Regulation (EU) 2016/679), every use of personal data must rest
on a lawful basis, and "consent" is only one of several; others include contractual necessity,
legal obligation, and legitimate interest. **Consent** is a specific, informed, freely-given, and
revocable indication of agreement — not a passive default and not buried in terms the individual
cannot meaningfully decline. The European Data Protection Board's guidance on AI and personal data
(such as Opinion 28/2024) clarifies that the GDPR continues to govern AI models and that the
data-protection duties attached to lawful basis, transparency, and accountability persist in AI
processing. The EU AI Act does not displace the GDPR: an AI system that handles personal data must
comply with data protection law in addition to AI-specific rules.

For governance practice, this means:

- **Document a lawful basis per use.** Do not assume that scraping or accumulating data implies
  permission to train on it. Record, per training and operational dataset, the legal ground relied
  on and the reasoning behind it.
- **Treat consent as a living consent.** Consent that is opt-in, specific, and withdrawable must be
  revocable; if individuals later withdraw, the system must honor that withdrawal, which has
  implications for retention and retraining.
- **Reconcile AI Act and GDPR duties.** They are complementary, not interchangeable; a compliance
  mapping must satisfy both where personal data is involved.

Consent is one piece of a broader transparency duty: individuals should be told what data is
processed, for what purpose, and how the system reaches decisions that affect them (see
`transparency-and-explainability.md`).

## Minimization and Retention

Two data-protection principles constrain how much data an AI system may hold and for how long.
**Minimization** is the principle that you collect and keep only the personal data necessary for the
declared purpose — no more. For AI this is in tension with the common instinct to hoard every
available record, but it is directly protective: the less sensitive data you hold, the less there is
to leak, misattribute, or misuse. **Retention** is the related limit on time: personal data should
not be kept longer than needed for the purpose, after which it should be deleted or de-identified.
The EU AI Act's "high-quality datasets" requirement (which pushes providers to design training data
to minimize discriminatory outcomes) reinforces the spirit of minimization by tying the *content* of
data to the system's actual purpose rather than to convenience.

Practical controls a governance program can adopt:

- **Purpose-bound acquisition.** Collect data for a stated purpose and refuse scope creep — do not
  quietly repurpose a dataset collected for one use into training a model for an unrelated one.
- **Retention schedules.** Define, per dataset, how long it is retained, who may extend that period
  and why, and when deletion or anonymization is triggered. Record the schedule in the catalog.
- **Deletion and de-identification paths.** Ensure that when a retention period ends, or an
  individual exercises a right to erasure, the data is actually removed from training corpora,
  feature stores, and backups, not merely hidden.
- **Reasonable, not minimal-to-zero.** Minimization does not mean stripping data until a model
  cannot function; it means the amount of data is justified by and proportionate to the purpose.

## Privacy-Enhancing Techniques

Privacy-enhancing techniques (PETs) are the technical tools that let organizations extract value
from data while reducing the exposure of the underlying individuals. *Platform and Model Design for
Responsible AI* treats these as a set of "privacy by design" defaults built into the model pipeline
rather than bolt-on afterthoughts. The book's model-level view distinguishes privacy across several
surfaces: the training data (an adversary should not be able to reverse-engineer it from the model),
the model inputs (protected from view during training), the model outputs (visible only to the
intended recipient), and model storage and access (restricted to authorized staff). Protecting each
surface requires different controls.

The core PETs the book and current practice converge on include:

| Technique | What it does | Typical use |
|---|---|---|
| Differential privacy (DP) | Adds calibrated noise so that including or excluding any one record barely changes outputs, bounding what an adversary can infer | Training and query-time privacy; measured by epsilon (ε) |
| K-anonymity | Groups records so each is indistinguishable from at least k−1 others on identifying attributes | Publishing or sharing structured data |
| Anonymization / pseudonymization | Removes or replaces identifiers; pseudonymization is reversible with a key, anonymization is not | Pre-processing before sharing or analysis |
| Encryption / access control | Protects data and model weights in storage and transit; restricts who can reach them | Model storage and access privacy |
| Federated learning | Trains on distributed data without centralizing raw records, exchanging only model updates | Keeping data local while still learning |

A recurring caution in the book is that overly flexible models can *memorize* training data, so an
overfitted model can leak private information even when the source data is secured. This is why
governance pairs PETs with monitoring and with careful feature selection: the protection has to hold
at the model output, not just at the dataset boundary. The book also notes that DP's epsilon metric
quantifies how much privacy loss a query or training run incurs, so practitioners can set a budget
for how much noise a system is willing to pay in exchange for how much utility.

## Privacy by Design Across the Model Pipeline

The lesson across all three sources is that privacy cannot be a last-minute audit step; it has to be
built into the design and every stage of the pipeline. *Platform and Model Design for Responsible AI*
lists the characteristics of privacy-aware AI as: being proactive and preventive rather than
reactive; making privacy the default; designing privacy in rather than bolting it on after the fact;
refusing to trade away essential functionality; protecting the model end to end across its lifecycle;
maintaining visibility and transparency; and putting the individual's interests first. These map
cleanly onto the governance controls this reference describes:

- **At intake**, classify each dataset and decide lawful basis, purpose, and owner before any
  modeling begins.
- **At build**, apply PETs, minimize sensitive features, and record lineage and quality so the model
  is auditable.
- **At deploy**, restrict access, monitor for drift and for leakage of sensitive outputs, and bind
  retention schedules to the operational data.
- **At retirement**, decommission data per its retention schedule and record the deletion.

Wiring these into the lifecycle gates (see `ai-lifecycle-governance.md`) and recording them in the
model card is what turns "privacy is important to us" into an enforced, verifiable practice.

## Where to Go Next

- **`foundations-and-principles.md`** — privacy as a governing principle and how training vs.
  operational data governance fit the principles.
- **`ai-lifecycle-governance.md`** — where ownership, lineage, quality, and retention are enforced
  across stage gates.
- **`llm-and-agent-security.md`** — the security controls (access, exposure, trust boundaries) that
  protect data in deployed systems.
- **`transparency-and-explainability.md`** — how disclosure of data practices supports consent and
  individual control.
- **`regulatory-landscape.md`** — GDPR and AI Act obligations that set the legal floor for the
  practices above.

---

### Synthesized from

This reference synthesizes (never reproduces) ideas from *Designing Data Governance from the Ground
Up*, *Data Governance Handbook*, and *Platform and Model Design for Responsible AI*, and it is
de-staled against the current state by the mission research notes on the regulatory landscape
(GDPR lawful basis, EDPB AI guidance) and technical controls (data cards, lineage, monitoring). All
prose is an original paraphrase and synthesis of the ideas in these sources; idea-level attribution
is consolidated in `source-index.md`. The discussion of consent, retention, and minimization is
educational context, not legal advice, and specific requirements should be confirmed against current
regulation at use time.
