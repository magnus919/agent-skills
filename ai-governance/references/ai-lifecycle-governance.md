# AI Lifecycle Governance

This reference explains how to keep an AI system accountable across its full lifetime, from
the moment someone proposes an idea or decides to buy a model, through the data, build,
evaluation, deployment, and monitoring phases, and finally into orderly retirement. The
backbone is the **stage gate**: a fixed checkpoint with a named decision-maker and a
published set of criteria that a use case or model must satisfy before it is allowed into
the next phase. Around those gates sit the controls that make the whole sequence visible
and auditable — a **model inventory** that lists every system the organization runs,
**lineage** that shows where data and models originated and how they were transformed,
**drift detection** that flags degradation once a model is live, and **incident response**
for when something goes wrong despite the gates.

The content below is an original synthesis of the ideas in *Platform and Model Design for
Responsible AI*, *Designing Data Governance from the Ground Up*, and the *Data Governance
Handbook*, refreshed against current research on technical governance controls (see
`research-technical-controls.md`). Read it alongside `risk-management-and-frameworks.md`,
which supplies the risk tiers and registers the gates feed into, and
`governance-operating-model.md`, which names the owners and councils who operate the gates.
Nothing here is legal advice.

## Why Governance Must Cover the Entire Lifetime

A model is not a thing you construct once and forget. *Platform and Model Design for
Responsible AI* argues that responsible AI is a continuing practice that runs from an early
prototype all the way to a production system that may be decommissioned years afterward,
and it warns that each step in the development life cycle brings hazards of its own. Risk
does not begin at the training run: an ill-chosen use case, a biased or outdated dataset, a
build nobody validated, a launch with no monitoring, a model that drifts silently, or a
decommissioned system still making decisions can each do damage independently.

Because the failure modes differ from phase to phase, oversight has to be spread across the
whole sequence rather than concentrated at a single approval moment. Current research on
technical controls echoes this: the NIST AI RMF and ISO/IEC 42001 both treat governance as
an activity that extends throughout the AI life cycle, and the EU AI Act — which took
effect on 2 August 2026 — makes logging, technical documentation, and post-market
surveillance explicit duties for high-risk systems precisely because obligations do not end
at launch.

Three commitments hold the sequence together:

- **Every phase has a named owner and a documented gate.** Someone is accountable for each
  transition, and the bar for passing is written down in advance.
- **Every phase is recorded.** The inventory, the lineage, and the logs let anyone
  reconstruct what happened, which is what makes the process auditable.
- **Every phase can feed back.** Monitoring and incidents push lessons back into earlier
  phases so the next model starts from a smarter place.

## Stage Gates as the Spine of Lifecycle Governance

A stage gate is a defined point between phases where a model or use case is checked against
fixed criteria and either cleared to continue, sent back for rework, or stopped. Gates earn
their keep three ways: they force a review before expensive work is committed; they leave an
auditable trail of who approved what and on what evidence; and they stop teams from quietly
skipping a required control.

*Platform and Model Design for Responsible AI* catalogues the recurring questions a model
practice should be able to answer at each gate — whether the applicable regulatory tools
have been identified, whether inventorying and classification happens during development,
how model naming and version control are handled, whether formal policies and audit
checklists exist for development, validation, use, monitoring, and retirement, whether
compliance checklists are maintained, and whether models are properly documented. These
questions are the substance of a gate.

A well-defined gate records four things:

| Gate element | What it captures |
|---|---|
| Entry criteria | What must already be true before work on the next phase begins |
| Review artifacts | The evidence the owner must present (cards, assessments, logs) |
| Decision rights | Who approves, who is consulted, who must be told (see the RACI material in `governance-operating-model.md`) |
| Exit criteria | The concrete, verifiable conditions that clear the gate |

How heavy a gate should be depends on the model's risk tier (see
`risk-management-and-frameworks.md`). A low-risk internal utility might clear a light gate
with a one-page intake; a high-impact system warrants the full assessment, validation, and
oversight chain. Calibrating gate depth to tier keeps the gate from being either a rubber
stamp or an unusable bottleneck.

The `use-case-intake-form.md` template turns the earliest gate into a fillable form, and
`model-risk-assessment.md` records the tiering decision that sets how demanding every later
gate must be.

## The Ideation and Procurement Stage

Oversight starts before any model exists, at the point where someone floats an AI idea or
decides to bring in a vendor-built model. The ideation gate exists to force one question
first: is this a sound AI use case at all, and is the risk worth it?

At this stage the organization should record:

- The business problem the AI is meant to solve and why AI — as opposed to a rule or a human
  process — is the right answer.
- The intended users and everyone the system could affect, including any group that might be
  harmed.
- The decision impact, meaning the consequential outcome the model will influence or
  automate.
- The data involved and how sensitive it is.
- The owner, the sponsor, and the decision rights for the use case.
- A first risk-tiering so the depth of later review is set up front.

For procured and third-party models, the ideation gate merges with procurement diligence:
the organization is choosing to host an external model, so it must establish who is
accountable for it, what documentation and assurances the vendor will provide, and how it
will be watched after adoption. That supply-chain thread is developed in
`procurement-third-party-and-board-oversight.md`. The governing rule, consistent with the
*Data Governance Handbook*'s point that a governed asset has clear ownership, is that no
model — whether built in-house or bought — enters the portfolio without a named owner and a
stated purpose.

A practical intake gate is a checklist rather than a blank approval:

- [ ] Problem statement and intended use recorded
- [ ] Affected population and decision impact assessed
- [ ] Data sensitivity and sourcing identified
- [ ] Named owner and sponsor assigned
- [ ] Initial risk tier proposed and recorded
- [ ] Applicable laws, policies, and standards identified

## The Data Stage

A model is only as sound as the data it learns from, which is why the data phase is where
many failures take root. *Designing Data Governance from the Ground Up* contends that data
oversight must persist through the life cycle and that a plan ignoring drift and end-of-life
phases will come up short. The *Data Governance Handbook* frames data ownership and data
quality as foundational: governed data has a clear owner, is fit for its purpose, and can be
traced.

The data gate should confirm:

- **Ownership.** A named steward is accountable for the dataset and its quality (see the
  steward roles in `governance-operating-model.md`).
- **Provenance and lineage.** Where the data came from and how it was transformed is
  recorded, so the model's inputs can be followed back (see `Lineage` below).
- **Quality.** The data is profiled and checked for completeness, accuracy, consistency, and
  timeliness against defined rules, with a plan for any material gaps.
- **Suitability.** The data reflects the intended use and population, and known gaps, biases,
  or proxies — for instance, a sensitive attribute correlated with an innocuous-looking one —
  are surfaced rather than buried.
- **Consent and rights.** The data was lawfully obtained and its use respects privacy and
  licensing constraints, in line with `privacy-and-data-governance.md`.

The *Data Governance Handbook* describes data quality as fitness for use, delivered through
defined rules, profiling resources, dashboards that report current quality openly, and plans
to resolve material issues. Those four steps map directly onto the data gate: set the rules,
measure against them, surface the results, and act before the model builds on shaky data.

## The Build Stage

The build phase turns data and a use case into a working model. Oversight here is less a
single approval point and more a set of habits woven into how the team works: reproducible
experiments, versioned code and data, documented choices, and acknowledged limits.

*Platform and Model Design for Responsible AI* treats governance as an engineering
discipline: reproducible pipelines, clear naming and versioning of models, documented
assumptions and limitations, and sharing so features and models are reused rather than
reinvented in isolation. The build gate confirms that a model's development is traceable —
that the code, data, and configuration behind any given version can be reproduced and
examined later. Current research on MLOps governance tooling backs this up: before a model
can advance from build to evaluation it must have its documentation finished, its risk tier
accepted, and a clear connection to its data lineage, because those artifacts are what make
the build auditable after the fact.

Build-phase practices worth enforcing:

- Reproducible training runs with recorded code, data versions, and configuration.
- A clear, documented naming and versioning scheme for models and their artifacts.
- Recorded assumptions, limitations, and design decisions.
- Registration in a model registry or inventory so the versioned artifact is tracked from
  the start.
- Bias and robustness checks at the model level, guided by
  `fairness-bias-accountability.md`.

## The Evaluation Stage

Evaluation is where the organization decides whether the model is actually good enough and
safe enough to ship. Good governance demands that evaluation be planned, not improvised:
the metrics, the datasets, and the acceptance thresholds are agreed before the run, and the
results are written down against a model card.

The evaluation gate should confirm:

- **Performance.** The model meets the agreed accuracy, reliability, and quality thresholds
  on appropriate test data, including performance broken out by relevant subgroups so
  the spread across groups is apparent instead of buried in one aggregate — the model-card
  discipline described in current research.
- **Fairness.** Bias is measured against relevant metrics, and trade-offs are explicit and
  defensible (see `fairness-bias-accountability.md`).
- **Explainability.** Where needed, the model's behavior can be explained and the disclosure
  a user will see is defined (see `transparency-and-explainability.md`).
- **Robustness and security.** The model holds up under expected variation and known
  adversarial cases (see `llm-and-agent-security.md`).
- **Limitations.** The situations where the model is likely to underperform are documented
  so it is not applied somewhere it is unsuited to.

The evaluation gate is also where the **model card** is finalized. As the mission's
technical-controls research records, model cards began as a proposal to standardize model
documentation — intended use, benchmarked results by subgroup, evaluation method, and
limitations — and have since become the standard artifact attached to a registry entry. A
finished model card is both the evidence that clears the evaluation gate and the reference
that the monitoring and incident-response phases consult later. The fillable `model-card.md`
template ships with this skill.

## The Deployment Stage

Deployment is the moment a model starts influencing real decisions, which makes this the
highest-stakes gate before launch. Its purpose is to confirm that a model enters production
only with the controls it needs to run safely and to be pulled back if it misbehaves.

*Platform and Model Design for Responsible AI* stresses that oversight continues after
launch and that live systems need monitoring and a fast way to respond. Current research
adds that monitoring must be set up in advance — with defined owners, thresholds, and
runbooks for responding — rather than thrown together after a problem appears, and that the
EU AI Act turns post-market monitoring and incident reporting into legal duties for
high-risk systems.

A deployment gate should confirm:

- A completed model card and approved risk tier on record.
- A monitoring configuration with defined metrics, alert thresholds, owners, and a runbook
  for drift and quality issues.
- A rollback plan, so the team can revert to the previous version or take the model offline
  quickly.
- Access controls and logging, so who can invoke or change the model is controlled and
  recorded (see `llm-and-agent-security.md`).
- Human oversight arrangements where the decision calls for them (see
  `foundations-and-principles.md`).
- A named operator or steward who owns the live system.

Current research describes the desired end state as one where deployment is gated
automatically: the pipeline blocks a model from reaching production until its documentation
is complete, its risk tier is accepted, and its monitoring is configured, enforcing those
checks mechanically instead of trusting someone to remember them.

## The Monitoring Stage

Monitoring is the runtime control that catches a deployed model when it stops performing as
expected. It is increasingly treated as a required part of responsible deployment rather
than an add-on, and it is what changes "we shipped it" into "we keep watching it."
*Designing Data Governance from the Ground Up* makes the parallel case for data: oversight
is not done at launch, and a plan that does not think about what happens to data in
production will fall short.

Monitoring generally tracks two things at once:

- **Operational health** — latency, throughput, error rates, and availability.
- **Model behavior** — prediction distributions, output quality, and whether the outputs
  still look like the ones the model was evaluated on.

The specific hazard monitoring exists to catch is **drift**, covered in depth in `Drift
Detection and Response` below. The key governance principle is that monitoring is
pre-configured and owned: someone is responsible for the metrics, the thresholds, and the
escalation path, and the setup is recorded before launch rather than bolted on after an
incident. Current research notes that monitoring is well developed for ordinary predictive models but
weaker for generative and agentic ones, whose outputs are not predetermined and are hard to
grade against a ground truth, so those systems call for proxy signals and staged human
review rather than a single accuracy figure.

## The Retirement Stage

Every model eventually reaches the end of its useful life. Retirement, or decommissioning,
is the governed end-of-life phase where the organization confirms a model is no longer
serving its purpose, shuts it down cleanly, records the fact, and disposes of the related
data responsibly.

*Platform and Model Design for Responsible AI* treats retirement as part of the inventory
life cycle: the inventory notes each model's development stage, including whether it is in
use, under development, or recently retired. *Designing Data Governance from the Ground Up*
applies the same discipline to data, holding that a governance plan must cover the
end-of-life phases — data usage, archiving, and destruction — and that governed teams decide
retention, storage, and deletion in advance rather than hoarding everything.

A retirement gate should confirm:

- **A reason and an owner.** Someone documents why the model is being retired and answers
  for the call.
- **A clean handoff.** Any models or systems that depended on this one are re-pointed or
  validated first, because retiring a model others rely on can cascade.
- **Access removal.** The model is taken offline and its entry points are disabled.
- **Data disposition.** Training and operational data is archived or destroyed according to
  retention policy, balancing compliance obligations against the cost and risk of holding
  data indefinitely.
- **Records.** The retirement is logged in the inventory and lineage so the system's history
  stays reconstructable for audit.

The *Data Governance Handbook*'s ownership principle applies at the end as much as the
start: even retirement needs a named accountable owner, or the model lingers unmanaged and
keeps making decisions nobody watches.

## Model Inventory

An inventory, or registry, is the foundation the other lifecycle controls rest on, because
an organization cannot govern systems it cannot list. As the mission's technical-controls
research emphasizes, a dependable inventory is usually the highest-value governance artifact
there is: it converts broad policy into a tangible, queryable register that audit,
monitoring, and incident-response teams can use, and it tends to be the first deficiency
surfaced when an organization measures its maturity, since most firms struggle to enumerate
every model running in their systems.

*Platform and Model Design for Responsible AI* describes the model inventory as holding all
the models running in production, along with the terms stakeholders need to see what each
model does and where its limits are. Crucially, the inventory makes it possible to build a
**dependency tree** showing how models interact, which reveals which models carry the most
inherent risk because a failure in one could ripple into others. A typical inventory entry
records:

- The model's identity, name, and version.
- Its development stage (in use, under development, or retired).
- Its owner and business sponsor.
- A high-level risk assessment and tier.
- Its intended use, goals, assumptions, and limitations.
- Its volume and context of use, plus its financial or customer impact.
- Its data lineage plus pointers to its documentation and monitoring setup.

The book also flags a practical trap: inventories tend to go stale. Its remedy is to hand
explicit responsibility for upkeep to a designated owner who works closely with model owners
to keep each entry current. The *Data Governance Handbook* makes the parallel point for
data — that governed assets have clear owners and that stewards keep them current — which
carries over directly to a model registry.

Current research treats the inventory as the scaffolding for all the other controls: a
governance-focused MLOps stack is built around a model registry that keeps model cards and
versioned artifacts, and ISO/IEC 42001 assumes the organization can name the AI systems
within its management system's scope. If the organization cannot produce a complete,
current list of its models on request, that is the first control to build.

## Lineage

Lineage is the record of where data and models came from and how they changed over time. It
is what makes the whole sequence reconstructable, and therefore auditable. *Platform and
Model Design for Responsible AI* insists that data and model lineage be captured across the
development phases so that, at any moment, the team can see how a model evolved. *Designing
Data Governance from the Ground Up* defines data lineage as confirming the origin of data,
recording the path it follows over time, and showing its flow from one system to another,
and it argues that lineage underpins transparency and root-cause analysis.

The book demonstrates the value with a hiring-algorithm example: when a bias concern is
raised about a deployed model, lineage lets the team trace back to the data and discover
that an indirect bias — a sensitive attribute tracking a non-sensitive one such as a zip
code — had been baked into the training set. With lineage in place, the fix is to roll back
to a version before the biased data and retrain, rather than guessing at the cause.

Lineage is not free; it depends on solid metadata management. The *Data Governance Handbook*
treats lineage as a capability built on metadata: to trace data, the organization must first
define the metadata that matters and assign stewards who keep it current. Two views are
commonly useful:

- **End-to-end lineage**, which shows the complete path of an asset from its source inputs
  to its final uses.
- **Vertical, or granular, lineage**, which focuses on a single asset or feature to reveal
  its details.

A **feature store** is one concrete lineage mechanism in practice: it catalogues features in
a single place, tracks how each feature was generated and used across projects, and gives
teams one location to answer questions about compliance, accuracy, and use. Lineage serves
several masters at once — finding errors, meeting privacy obligations, migrating systems,
and supporting bias investigations — which is why the mission's research calls it a core
technical control rather than a nice-to-have.

## Drift Detection and Response

Drift is the slow erosion of a model's validity after it goes live. It is the reason
monitoring exists, and it is the failure mode that most often catches teams off guard.
*Designing Data Governance from the Ground Up* is direct: drift is unavoidable, and a
governance plan that ignores it will fall short — but a model losing predictive power is not
fatal if the team detects it in time and has a plan.

The book defines data drift as unexpected, undocumented shifts in data structure, semantics,
or infrastructure that hurt quality, and it observes that environmental change alters how
the data a model is exposed to interacts with the training process. The mission's
technical-controls research narrows this to the two standard forms:

- **Data drift** — the input features no longer resemble the distribution they had during
  training.
- **Concept drift** — the connection between inputs and the predicted outcome shifts as
  circumstances change.

Detection usually works by running statistical tests and distribution-comparison measures
across sliding windows of live data, with warning levels and escalation points that prompt an
investigation, a retrain, or a revert. Because fresh labels for production output are
frequently missing or arrive late, *Designing Data Governance from the Ground Up* recommends
proxies: train a model on
data from six months ago and compare its outcomes with a model trained on current data, or
build pipelines whose features carry quality expectations and correct errors by updating part
of the pipeline. *Platform and Model Design for Responsible AI* describes the remediation
loop the same way — detect the drift, set a threshold for how much is tolerable, and trigger
model replacement or calibration once the threshold is crossed.

The governance discipline is to make the drift response pre-planned and owned:

- Define the drift metrics and the acceptable thresholds before deployment.
- Assign a named owner who answers for acting when an alert fires.
- Pre-write the response runbook: investigate, re-evaluate against fresh labeled data,
  retrain, or roll back.
- Log the decision so the response is auditable.

Current research adds that drift detection is routine for predictive models yet still
developing for generative and agentic systems, which rely on proxy signals and human
oversight; do not treat a plain accuracy metric as enough there.

## Incident Response

Even with good gates, incidents happen — a biased outcome surfaces, a model leaks data, a
security flaw is exploited, a system misfires in a way that harms someone. Incident response
is the controlled way the organization reacts: recognize the problem, stop the harm,
investigate the cause, fix it, and learn so it does not recur.

*Platform and Model Design for Responsible AI* includes real incident cases — data leaks and
breaches at major companies, with resulting fines and settlements — to show that incidents
are genuine, costly, and often the product of avoidable mistakes such as misconfigured
storage or weak access control. The mission's technical-controls research stresses that the
evidence base for any incident review is the **audit trail**: a log of what the system did
and when, the inputs it acted on, and who signed off on or launched each operation. The EU
AI Act treats such logging as a core obligation for high-risk systems so outcomes can be
reconstructed, and that same logging is what lets an assessor tell whether a decision
followed the intended procedure.

A workable incident-response posture for AI follows the operating model's escalation path
(see `governance-operating-model.md`):

1. **Detect.** Monitoring, lineage, user reports, or audits surface a problem.
2. **Triage.** Assess severity and impact, and decide whether to pause, roll back, or take
   the model offline.
3. **Contain.** Stop further harm — restrict access, disable the model, or roll back to a
   known-good version.
4. **Investigate.** Use the inventory, lineage, and audit logs to reconstruct what happened
   and find the root cause.
5. **Remediate.** Fix the model, the data, the process, or the control that failed, and
   validate the fix.
6. **Report and learn.** Escalate to the right body (including the board for material
   incidents), record the lessons, and feed them back into earlier stage gates so the next
   model starts smarter.

Two principles keep incident response trustworthy rather than reactive. First, **predefine
the escalation path**: know in advance whom to call and who is accountable, so the response
is not improvised when the incident strikes. Second, **keep the logs that make
reconstruction possible**: if the organization cannot reconstruct what a system did, it
cannot credibly investigate an incident, defend a decision, or show a regulator or auditor
that it governed the system correctly. Log design should balance completeness against
privacy and storage cost, with defined retention periods, access controls, and immutability
so the records cannot be quietly rewritten later.

## Running Lifecycle Governance with the Rest of the Skill

Lifecycle governance schedules every other control in this skill across time:

- **Principles** set the values the gates are protecting (`foundations-and-principles.md`).
- **The operating model** names the owners, councils, and escalation paths that run the gates
  (`governance-operating-model.md`).
- **Risk frameworks and tiering** decide how heavy each gate must be and feed the register
  (`risk-management-and-frameworks.md`).
- **Fairness, transparency, privacy, and security** each contribute specific checks to the
  data, build, evaluation, and deployment gates (`fairness-bias-accountability.md`,
  `transparency-and-explainability.md`, `privacy-and-data-governance.md`,
  `llm-and-agent-security.md`).
- **Procurement and board oversight** cover the third-party models entering at the ideation
  gate and the aggregate lifecycle picture reported upward
  (`procurement-third-party-and-board-oversight.md`).

Use `use-case-intake-form.md` to open the lifecycle with a governed intake,
`model-risk-assessment.md` to set the tier that calibrates every later gate, and
`model-card.md` to produce the documentation that carries the model through evaluation,
monitoring, and incident response.

## Where to Go Next

- **`governance-operating-model.md`** — who owns and runs each gate.
- **`risk-management-and-frameworks.md`** — the tiers and registers the gates route through.
- **`privacy-and-data-governance.md`** — the data ownership and quality underpinning the data
  and retirement stages.
- **`procurement-third-party-and-board-oversight.md`** — the supply-chain and board tiers of
  the lifecycle.

---

### Synthesized from

This reference synthesizes (never reproduces) ideas from *Platform and Model Design for
Responsible AI*, *Designing Data Governance from the Ground Up*, and the *Data Governance
Handbook*. Current context on model and data cards, model inventories, monitoring and drift,
audit trails, and MLOps governance tooling is drawn from the mission research note
`research-technical-controls.md`. All prose is an original paraphrase and synthesis of the
ideas in these sources; idea-level attribution is consolidated in `source-index.md`. It is
not legal advice.
