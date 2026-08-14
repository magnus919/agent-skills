# Fairness, Bias, and Accountability

This reference teaches how to reason about and operationalize fairness, bias, and
accountability in AI systems. Its central message is that fairness cannot be collapsed into a
single number: the choice of any one metric embeds a contested moral judgment, and a defensible
program measures the right things, documents the reasoning behind the choice, and assigns someone
who can be held answerable for the outcome. It synthesizes (never reproduces) the ideas in *AI
Fairness*, *Introduction to Responsible AI*, and *Responsible AI: Best Practices*. Read it with
`foundations-and-principles.md` (which frames fairness and accountability as governance
principles), `transparency-and-explainability.md` (which covers the explanation and disclosure
half of accountability), and `ai-lifecycle-governance.md` (which places fairness review at stage
gates). Use the `model-card.md` and `model-risk-assessment.md` templates to record the decisions
this reference describes. It is not legal advice.

## Why Fairness Defies a Single Metric

It is tempting to ask "is our model fair?" and expect a yes-or-no answer backed by one score. The
books that inform this reference converge on a different lesson: fairness is context-dependent,
partly subjective, and measured in several irreducibly different ways, so any attempt to reduce it
to one threshold is an oversimplification that can hide real harm. *Responsible AI: Best Practices*
stresses that fairness is so bound up with context and so many-sided that no small set of numbers
can do it justice, and warns that metric-driven toolkits risk a compliance checklist mentality in
which a check mark stands in for genuine scrutiny. *AI Fairness* makes a related point about so-called "ethics
washing": running a model through a fairness library, picking whichever measurements it happens to
satisfy, and then claiming the model was audited is a way of manufacturing the appearance of
diligence rather than exercising judgment.

The practical consequence is that an organization must be able to say *which* notion of fairness
it is pursuing and *why*. There is no neutral default. Choosing a metric is a value-laden decision
that deserves an explicit ethical justification, not a habit of reaching for the newest or most
popular measurement. *AI Fairness* argues that the choice of metrics should be grounded in an
independent theory of justice rather than in convention, and at minimum the reasoning behind the
choice must be stated and defensible. *Introduction to Responsible AI* reinforces the point that
defining a universally acceptable notion of fairness is unachievable because different contexts
demand different definitions, and the balance between equal treatment and correcting historical
disparities is inherently contested.

## Where Bias Comes From

Before measuring fairness it helps to name the sources of bias, because each has a different
remedy. Drawing on the Barocas-Selbst analysis that *AI Fairness* recounts, a model can absorb
bias in at least three distinct ways:

| Source of bias | What it looks like | How hard it is to address |
|---|---|---|
| Sample inequality | The training set under-represents a group (for example, far more resumes from men than women) | Easiest; collect a larger, balanced sample |
| Label inequality | The outcomes used to train the model are themselves skewed by biased human judgments (for example, managers rated women's performance lower) | Manageable; rework or reweigh the labels |
| Underlying social inequality | Historical oppression means a group genuinely has fewer qualifying features, so even "true" labels encode disadvantage | Hardest; this may be injustice rather than a fixable data flaw |

*Introduction to Responsible AI* frames bias as a human tendency that seeps into AI through the
data it learns from, and it documents well-known real-world failures to illustrate the stakes:
recruiting tools that downgraded resumes containing female-coded terms, recidivism risk scores
that overestimated reoffense for minority groups, photo auto-tagging that mislabeled people, and
facial recognition that misidentifies darker-skinned faces. The book notes that eliminating all
bias is unfeasible, so the realistic goal is to mitigate the biases that produce unjust or harmful
consequences. Bias can enter at collection, at labeling, through proxy features that stand in for
protected attributes, and through the choice of target variable itself.

## Fairness Metrics and Their Limits

Fairness metrics divide broadly into individual and group measures. *AI Fairness* catalogs the
families, and *Responsible AI: Best Practices* adds the practitioner vocabulary. The important
distinction is between *equal treatment* (whether the same rule is applied to everyone) and *equal
impact* (whether outcomes balance across groups); the two are in mathematical tension with one
another and with overall accuracy.

| Metric | Kind | What it requires | Caveat |
|---|---|---|---|
| Blindness | Individual | No protected attributes (or proxies) in the data | Being blind to a feature does not mean being blind to its proxies |
| Counterfactual tests | Individual | Changing an irrelevant feature should not change the outcome; changing a relevant one should | Needs a defensible notion of "relevant" and "similar" |
| Demographic parity | Group | Positive-selection rates are equal across groups | Can conflict with actual qualification rates; resembles quotas |
| Equalized odds | Group | True-positive and false-positive rates are equal across groups | Trades off against selection parity; needs a clear decision threshold |
| Equal opportunity | Group | True-positive rates (recall) are equal across groups | Widely endorsed, relatively minimal; respects actual qualifications |
| Calibration | Group | A given predicted score means the same likelihood of the outcome in every group | Not always satisfiable alongside other parity notions |

The most consequential limit is formal: *AI Fairness* describes the "impossibility" results of
2017, showing that in realistic conditions no single model can satisfy all of the reasonable
fairness requirements at once. Equalized odds, equal opportunity, calibration, and demographic
parity pull against one another. Practitioners must therefore decide priorities rather than chase
every parity at once. The book also flags the shallowness of a field that produces many metrics
with little underlying moral content, urging that metric selection be anchored in ethical argument.

### Choosing and Reporting the Metric Set

Because the metrics conflict, the defensible move is to state a priority order. *AI Fairness*
proposes a hierarchical approach: a model must meet a minimally acceptable accuracy bar; it must
expose its most significant causal features so that irrelevant (especially protected) features can
be ruled out; it should equalize recall for qualified candidates across protected groups; and it
should equalize selection rates unless doing so would push accuracy below the minimum standard or
below default human practice. Whatever ordering an organization adopts, the reasoning should be
recorded in the model's documentation, where it becomes auditable. This is the substance behind the
fairness section of the `model-card.md` template: not a single number but an explicit statement of
which metrics were computed, what they showed, and why those metrics were the right ones.

## Algorithmic Justice and the Trade-offs of Enforcing Fairness

Correcting a model to improve group parity is not free. *AI Fairness* documents that enforcing
selection parity almost always reduces overall accuracy, and often reduces accuracy and precision
most sharply for the very groups the mitigation is meant to help. There are also "losses in
fairness": a mitigated model can create reverse-discrimination cases where someone from a majority
group can truthfully claim that they would have been approved under the original model but were
rejected after the correction. These are genuine costs that must be weighed, not dismissed.

Because demographic parity, equalized odds, equal opportunity, and calibration make incompatible
demands, an organization that enforces one parity notion necessarily gives ground on the others
and on raw accuracy. Fairness also has to be reconciled with the other trustworthiness
properties. A purely accuracy-maximizing model can be blatantly unfair, but a heavily constrained
one can be so degraded that it fails its purpose. The discipline this reference recommends is to treat fairness
as one dimension of a risk assessment rather than an absolute override: surface the trade-offs,
quantify what is given up, and let the governance process decide whether the residual outcome is
acceptable. This is why fairness review belongs in the same workflow as the `model-risk-assessment.md`
template and the tiering logic in `risk-management-and-frameworks.md`.

## Disparate Treatment Versus Disparate Impact

The legal vocabulary for discrimination usefully frames the fairness problem. As *AI Fairness*
explains, US anti-discrimination law recognizes disparate treatment (using a protected attribute in
a decision that harms an individual) and disparate impact (a practice that produces unequal outcomes
across protected groups even without intent). Algorithms complicate this picture because they have
no intent, so the traditional "intent to discriminate" test does not map cleanly onto them. Yet the
law has long recognized that discrimination need not be intentional, and regulators such as the
Consumer Financial Protection Bureau have applied an "effects test" to practices that are neutral on
their face but disproportionately harmful, unless a legitimate business need justifies them.

This matters for accountability because many unfair AI outcomes are unintentional and driven by
proxy features rather than explicit protected attributes. A model that never sees race can still
produce racially disparate results through correlated proxies such as income, geography, or
residence. *Responsible AI: Best Practices* makes the same point at the level of the system: a
company can assert that it never collects protected attributes, yet the model perpetuates historical
bias through the data it was trained on. Consequently, "we are blind to protected attributes" is not
an accountability claim; it is a reason to test whether the model is nonetheless reproducing
disparate outcomes. Notable policy responses, such as New York City's Local Law 144 requiring
public bias audits of automated hiring tools, show the direction of travel toward mandatory
disparate-impact reporting.

## Accountability: Assigning Answerability

Accountability turns the analysis of bias into an obligation with an owner. *Responsible AI: Best
Practices* frames it as a principle that the people responsible for each phase of the AI lifecycle
should be identifiable and answerable for outcomes, and it offers the *role-level accountability
contract* as the concrete mechanism: a document describing the specific roles and responsibilities
of every individual or organization involved in the system's development and use, sometimes
formalized as a signed contract. The intent is that when a system misbehaves, there is a clear,
accessible answer to the question of who is accountable at each stage, rather than a diffuse
organizational fog. The book acknowledges the tension between this clarity and the loss of
flexibility that rigid role boundaries can create, and it pairs role-level accountability with
related controls such as a code of ethics and oversight structures.

*Introduction to Responsible AI* links accountability to transparency: a system that is explainable
and documented is one whose developers can be held responsible for failures, and one that can be
audited for compliance. Accountability is therefore not a separate tool but a property that the rest
of the governance stack produces — clear ownership, recorded decisions, audit trails, and disclosure
make answerability possible. The `governance-operating-model.md` reference assigns these roles and
decision rights; this reference supplies the fairness-specific content those roles are accountable
for.

## Model Cards as the Accountability Record

Model cards are the canonical documentation artifact that makes fairness and accountability
verifiable after the fact. Originating in the 2019 model-cards paper (current research, see
`research-technical-controls.md`), a model card is a short document accompanying a released model
that records its intended use, the evaluation procedure, and benchmarked performance *disaggregated
by subgroup* — so that accuracy variation across demographic and other groups is visible rather than
hidden inside a single average. The disaggregation is the point for fairness: an overall accuracy
figure can mask a model that performs well for the majority and poorly for a minority. The card
also documents limitations, so the model is not applied in contexts for which it is unsuited.

*Responsible AI: Best Practices* treats model cards and data sheets as the checklist-and-template
layer of a responsible-AI program, with the caveat that such artifacts only work when high-quality,
standardized practices sit behind each check box; otherwise they become superficial compliance
theater. For governance purposes, a completed model card records the fairness metrics that were
chosen, why, what they showed across groups, and which decisions were made in response — turning the
discussions in this reference into a durable, audit-ready record. The `model-card.md` template in
this skill implements exactly that, and `research-technical-controls.md` documents the current
state of model and data cards as a widely adopted control.

## Running Fairness, Bias, and Accountability with the Rest of the Skill

Fairness work is not a standalone activity; it threads through every other governance surface:

- **Principles** define what the organization values about fairness and accountability
  (`foundations-and-principles.md`).
- **Risk frameworks** host fairness measures alongside accuracy, safety, and robustness metrics,
  and route fair models through the same tiering and register as any other risk
  (`risk-management-and-frameworks.md`).
- **Lifecycle gates** schedule when fairness is assessed — from ideation through post-deployment
  monitoring for drift that reintroduces bias (`ai-lifecycle-governance.md`).
- **Transparency and explainability** provide the disclosure and explanation that make
  accountability meaningful (`transparency-and-explainability.md`).
- **Board and third-party oversight** consume the fairness findings as part of the aggregate risk
  picture and hold the accountable owners to account
  (`procurement-third-party-and-board-oversight.md`).

Use the `model-card.md` template to record metric choice, subgroup results, and limitations; the
`model-risk-assessment.md` template to weigh fairness against other risk dimensions; and the
`use-case-intake-form.md` template to flag high-stakes, fairness-sensitive use cases early.

## Where to Go Next

- **`foundations-and-principles.md`** — fairness and accountability as governing principles.
- **`transparency-and-explainability.md`** — the explanation and disclosure that enable
  accountability.
- **`ai-lifecycle-governance.md`** — where fairness review and monitoring happen across the
  lifecycle.
- **`research-technical-controls.md`** — current state of model cards, data cards, and monitoring.

---

### Synthesized from

This reference synthesizes (never reproduces) ideas from *AI Fairness*, *Introduction to
Responsible AI*, and *Responsible AI: Best Practices*. Current context on model cards and
monitoring is drawn from the mission research note `research-technical-controls.md`. All prose is
an original paraphrase and synthesis of the ideas in these sources; idea-level attribution is
consolidated in `source-index.md`. The legal discussion is educational context, not legal advice,
and specific laws and enforcement should be confirmed against current sources at use time.
