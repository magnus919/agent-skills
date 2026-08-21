# Evidence Method for AI Operating Economics

This reference turns the core skill into a repeatable investigation and decision method. Use it when the user needs more than a short recommendation or when a claim is consequential enough to preserve.

## 1. Scope the decision before gathering numbers

Write a one-sentence decision question:

> Should [accountable owner] [scale, constrain, redesign, hold, retire, or approve an exception for] [AI intervention] in [workflow/population] by [date or trigger], based on [required outcome and guardrails]?

Record the intervention mode:

- Assist: provides information or drafts while a person decides.
- Recommend: proposes a ranked or selected action.
- Route: classifies or directs work.
- Execute: takes an external action.
- Replace or remove: changes staffing, process, or service capacity.

The mode determines what evidence and authority are appropriate. A positive assist result does not automatically justify execution authority.

## 1a. Separate the business case from benefit realization

A forecasted benefit is not a realized benefit. Track four states separately:

1. **Expected benefit:** the hypothesis or business-case estimate.
2. **Enabled capacity:** time, throughput, or capability the intervention appears to make available.
3. **Operational benefit:** a verified change in the target workflow, such as more resolved cases, shorter cycle time without quality loss, or fewer avoidable escalations.
4. **Realized economic or mission benefit:** the operational change is converted into an attributable financial, service, capacity, or mission result under the organization's actual decision and accounting rules.

Record the owner, baseline, realization mechanism, timing, dependencies, and disbenefits for each expected benefit. Do not call time saved “savings” until the organization has a credible mechanism for converting it into reduced spend, additional output, avoided cost, improved service, or another explicitly valued result. If the benefit is capacity released for higher-value work, measure whether that work actually occurred.

Benefits-realization planning can borrow from public-sector benefits-management guidance, but the local owner and accounting treatment remain authoritative. Load the source index when a board or investment claim depends on the distinction.

Build a claim table before writing the conclusion:

| Claim | Evidence class | Source and scope | What it supports | What it does not support | Open challenge |
|---|---|---|---|---|---|
| [claim] | observed / causal / inferred / vendor-reported / asserted / normative | [citation, date, version] | [permitted interpretation] | [boundary] | [test or missing evidence] |

Use the strongest source appropriate to the claim:

- Workflow outcomes: controlled studies, internal experiments, or verified operational data.
- Cost: billing records, usage telemetry, allocation rules, and explicit assumptions.
- Quality and safety: outcome audits, incident records, domain review, and representative samples.
- Worker or user impact: segmented operational data plus worker/user research where relevant.
- Controls: official standards, provider documentation, and observed enforcement behavior.

A research summary is not a substitute for source-level claims. Preserve rejected, inaccessible, redundant, or out-of-scope sources in the research log or evidence record so omission is distinguishable from oversight.

## 3. Build an outcome model

Separate the mechanism from the outcome:

| Layer | Question | Example |
|---|---|---|
| Intervention | What changed? | Agent receives suggested responses |
| Behavior | What did people or systems do differently? | More chats handled; recommendations accepted selectively |
| Immediate outcome | What changed in the workflow? | Resolved cases per hour |
| Quality outcome | Did the result remain correct and acceptable? | Resolution rate, customer sentiment, rework |
| Business or mission outcome | Did the organization get the intended value? | Cost per resolved case, retention, revenue, service access |
| Distributional outcome | Who gained, lost, or carried new burden? | Novices improve; experts see no gain; review work shifts |

Do not jump from intervention to business outcome without observing the intermediate mechanism and its failure modes.

## 4. Design the comparison

Choose the strongest feasible design and name the downgrade if it is weaker:

1. Randomized or staggered assignment.
2. Matched comparison or difference-in-differences with a defensible control and pre-period.
3. Controlled pilot with explicit inclusion, exclusion, baseline, and observation window.
4. Before/after descriptive comparison with seasonality, selection, and concurrent-change caveats.
5. Qualitative or vendor evidence used only for hypothesis formation.

Before interpreting a result, ask:

- Did people self-select into treatment or into using the tool?
- Did task mix, volume, staffing, incentives, or pay change?
- Did the intervention change which tasks were attempted?
- Did quality measurement cover the treated population equally?
- Did learning, novelty, or temporary support affect the result?
- Were concurrent tools, process changes, or policy changes present?
- Is the comparison at the same workflow boundary as the decision?

If these questions cannot be answered, narrow the causal language and classify the result as descriptive or inferred.

## 5. Model the economic boundary

Use three cost layers, then show marginal and fully loaded views within the economic layer:

1. **Billing truth:** provider or infrastructure charges as recorded in source billing data.
2. **Allocated cost:** shared charges assigned to a product, team, tenant, workflow, or business unit under documented allocation rules.
3. **Economic cost:** allocated cost plus material human, engineering, governance, risk, idle-capacity, transition, and opportunity costs needed to operate the intervention.

A common billing schema can improve reconciliation and allocation, but it does not decide the right allocation policy or establish business value.

### Marginal view

What changes when one more meaningful unit of work is served?

- Input and output tokens
- Model and routing charges
- Data acquisition, preparation, licensing, and retention
- Tool and API calls
- Retrieval and data transfer
- Human review, correction, escalation, and rework
- Incremental compute or capacity

### Fully loaded view

What must exist for the intervention to operate responsibly?

- Engineering and integration
- Evaluation and test data
- Red-teaming and monitoring
- Observability and retention
- Security, privacy, and governance
- Training, change management, and support
- Incident response and recovery
- Committed or idle capacity
- Model/provider migration, retraining, deprecation, and exit costs

Classify each cost as fixed, variable, step-function, avoided, transferred, or uncertain. State the allocation method for shared resources. Keep token attribution separate from realized value: tokens are a computation unit, not a value unit.

The denominator must represent meaningful work. Possible denominators include completed workflow, resolved case, accepted decision, active user-month, or customer outcome. Use separate denominators for materially different task classes rather than hiding them in an average.

## 6. Inspect worker, user, and task heterogeneity

At minimum, slice by the variables that could reverse the decision:

- Experience, skill, role, and training status
- Task complexity, risk, and exception rate
- Customer or user segment
- Language, geography, accessibility, or demographic group where appropriate and lawful
- Human-review burden and escalation frequency
- Quality, error severity, and rework
- Adoption intensity and non-user comparison

A heterogeneous result may require differentiated deployment: assistance for novices, review support for experts, a higher-quality model for high-risk tasks, or no deployment in a harmed segment. Do not “solve” heterogeneity by reporting only the mean.

Worker-impact evidence should include more than productivity. Consider autonomy, workload, learning, skill development, job quality, schedule, stress, discretion, and who absorbs monitoring or correction work. Route formal labor, legal, or collective-bargaining questions to qualified specialists.

## 7. Separate evidence from decision language

Use calibrated verbs:

- **Observed:** “The treated group resolved more cases per hour in this deployment.”
- **Causal:** “The staggered comparison estimates an increase within this population and period.”
- **Inferred:** “The pattern is consistent with knowledge transfer, but does not establish it.”
- **Vendor-reported:** “The provider reports that customers experienced…”
- **Normative:** “The framework recommends monitoring and assigned responsibility.”
- **Unknown:** “The available evidence does not establish…”

Never use “proves,” “guarantees,” “will save,” or “safe” unless the evidence and scope truly support that strength.

## 7a. Require a governance evidence packet for authority expansion

Before moving from a bounded pilot to a materially broader population, higher-risk task, or side-effect authority, require a compact governance packet:

- Accountable owner, intended use, risk tier, and affected population
- System, model, prompt/policy, tool, provider, and version inventory
- Acceptable-use, refusal, escalation, and human-oversight rules
- Pre-deployment evaluation results and the release threshold used
- Third-party/provider assessment and relevant contractual evidence
- Incident, override, and near-miss record with after-action ownership
- Change and revalidation trigger for model, prompt, tool, data, or workflow changes
- Retention, dependency, leakage, user-impact, and decommissioning plan

These are governance inputs, not proof that the system is safe or valuable. Include the cost of producing and operating these controls in the economic boundary. Route detailed risk, privacy, security, and runtime control work to their owning skills.

## 8. Apply a decision rule without pretending to score everything

Use a structured disposition rather than a universal numeric score:

| Disposition | Minimum basis | Required next control |
|---|---|---|
| Scale | Outcome improvement, countermetrics within bounds, cost boundary understood, no disqualifying slice | Define next population and authority slice |
| Constrain | Plausible value with unresolved cost, quality, distributional, or authority risk | Set quota, population, task, or human-review boundary |
| Redesign | Mechanism or workflow creates avoidable failure or burden | Change workflow/model/control and rerun comparison |
| Hold | Required evidence is missing or conflicting | Name evidence owner, method, and review trigger |
| Retire | Value absent or countermetrics exceed bounds after review | Protect users/workers, migrate, and record learning |
| Exception | Material gap accepted temporarily | Named human approver, expiry, containment, and revisit |

A positive average cannot override a hard safety, privacy, authorization, or material quality failure. Conversely, a single weak metric should not automatically kill an intervention if the decision record explains the tradeoff and names the accountable owner.

## 9. Close the loop

At the review trigger, compare:

- Expected versus observed outcome
- Expected versus observed cost
- Countermetrics and subgroup effects
- Adoption, substitution, and new human work
- Incidents, near misses, overrides, and escalations
- Model, prompt, tool, policy, or population changes

Classify the hypothesis as supported, weakened, refuted, or unresolved. Preserve the result and link it to the next decision. A value-realization process that never changes authority, scope, or investment is measurement theater.

## Research thin spots to keep visible

The foundational evidence is strongest for workflow-level productivity, measurement caution, cost/usage controls, telemetry, and lifecycle governance. It is thinner for:

- Realized financial returns after implementation and change-management cost
- Long-term worker learning, job quality, and distributional effects
- Agentic workflows with multiple tools and autonomous side effects
- Comparable cross-vendor or cross-model economic benchmarks
- Enterprise counterfactuals where adoption is voluntary and task mix changes

Treat these as active evidence gaps. Do not fill them with vendor case studies or invented benchmarks.
