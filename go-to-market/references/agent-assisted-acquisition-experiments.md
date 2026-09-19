# Agent-Assisted Acquisition Experiments

Use this method when AI or automation may research accounts, recommend segments, draft
messages, classify replies, or tune an acquisition experiment. It turns an ICP and message
idea into a bounded learning loop. It does **not** authorize contact, operate a campaign,
interpret law, or treat tool access as permission.

## 1. Write the experiment contract

Do not start from a website URL and silently infer permission to contact people. Record the
contract first; mark unknowns instead of filling them with plausible guesses.

```text
Acquisition experiment
Decision owner / operator / review date:
Offer and painful job:
Target account / target person:
Positive selection evidence:
Explicit exclusions:
Why-now signal: observed | enriched | model-inferred
Message hypothesis:
Permitted proof / prohibited or unsubstantiated claims:
Channel / audience / geography:
Data source, provenance, and minimum fields:
Authority granted by capability:
Volume / spend / duration / frequency caps:
Success / pause / termination thresholds:
Suppression / complaint / incident path:
Evidence location / unresolved questions:
```

Treat positive criteria as a hypothesis, not a verdict about a person. Record negative
criteria with equal care: existing customers, competitors, students, unsupported regions,
regulated or vulnerable audiences, prior opt-outs, bad-fit firmographics, and other groups
the experiment must not contact. Distinguish directly observed intent from enrichment and
model inference; personalization does not turn an inference into consent or truth.

## 2. Gate readiness before live exposure

Research, simulation, and drafting may continue while readiness is incomplete. Live contact
is not ready until the owner has recorded all applicable decisions below.

| Decision | Minimum evidence | If missing |
|---|---|---|
| Jurisdiction and recipient type | Named geographies and audience classification | Draft/research only; route legal interpretation to `legal-strategy` or qualified counsel |
| Responsibility | Accountable business owner plus legal/privacy/compliance owner where applicable | Do not recommend launch |
| Sender and claims | Truthful identity, substantiated claims, permitted proof | Revise message; do not send |
| Data handling | Source/provenance, purpose, minimum fields, access, retention, rights path | Do not acquire or activate the data |
| Opt-out and suppression | Clear opt-out plus organization-wide suppression checked immediately before every action | Block live execution |
| Reputation and harm | Deliverability/brand owner, complaint and adverse-impact thresholds | Draft/research only |
| Escalation and containment | Ambiguous-reply, rights-request, complaint, incident, and manual pause/kill paths | Block live execution |

Do not declare a campaign lawful or compliant. Requirements vary by jurisdiction and recipient.
For example, UK guidance distinguishes corporate subscribers from sole traders, while US
CAN-SPAM duties also cover business-to-business commercial email. Re-verify current primary
sources for the actual audience and channel:

- [ICO business-to-business marketing guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/business-to-business-marketing/)
- [FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)

## 3. Grant authority per capability

"Autopilot" is not one permission. Assign the narrowest useful authority separately for
research, recommendation, drafting, external communication, optimization, and conversation.

| Level | Allowed behavior | Evidence required to enter | Mandatory boundary |
|---|---|---|---|
| **Observe** | Research accounts and analyze prior results | Approved sources and data boundary | No external action |
| **Recommend** | Propose ICPs, messages, tests, and allocation changes | Traceable rationale and uncertainty | Human decides |
| **Draft** | Prepare targeting and content for review | Claims tied to approved proof | Nothing is sent or published |
| **Execute bounded** | Run an approved audience/message inside caps | Readiness gate complete; preview approved | Fixed audience, message, time, volume, spend, and frequency |
| **Optimize bounded** | Adjust pre-approved reversible parameters | Reliable downstream evidence and change log | No new audience, claim, channel, or budget ceiling |
| **Converse bounded** | Handle explicitly enumerated low-risk reply classes | Tested reply policy and monitored escalation | Escalate pricing, commitments, objections, complaints, rights requests, sensitive content, and ambiguity |

Record for each granted capability: owner, scope, evidence, expiry/review date, audit location,
and pause/reversal path. Authority expands only after predeclared evidence thresholds; it
narrows after regressions, complaints, unexpected affected groups, data-quality failures, or
control failures. Tool availability and one successful pilot never grant broader authority.
The manual stop path remains available at every level.

## 4. Measure signal quality, not activity alone

Preserve the funnel through the furthest reliable downstream outcome:

```text
selected -> contacted -> delivered -> replied -> positive reply -> accepted meeting
         -> qualified opportunity -> proposal -> revenue -> retained gross margin
```

For every step retain its denominator, time window, cohort, source, exclusions, and definition.
Also record negative replies, opt-outs, complaints, exclusions discovered after selection,
qualitative objections, and data or classification errors.

Delivery, reply rate, a vendor-defined "hot lead," meeting count, and cost per lead are proxy
signals. They are not interchangeable with qualified pipeline or retained economics. Use the
furthest trustworthy signal available and state the lag or missing data. Never scale budget or
authority from a proxy alone. If later-stage evidence is not mature, hold the decision or run a
bounded follow-up rather than inventing conversion assumptions.

## 5. Run the decision loop

1. **Frame:** complete the experiment contract and tag assumptions by confidence.
2. **Gate:** choose the highest authority level supported now; use simulation or draft review
   when live readiness is incomplete.
3. **Expose:** run the smallest capped slice that can falsify the segment, message, channel, or
   control hypothesis.
4. **Classify:** review fit, positive and negative responses, objections, exclusions, harms,
   complaints, and control failures—not only favorable activity.
5. **Evaluate:** compare the furthest reliable downstream quality and economics with the
   predeclared success, pause, and termination thresholds.
6. **Decide:** **scale, revise, hold, narrow authority, or stop**. Scaling must name what changes
   and what remains capped; a message win does not automatically authorize a new audience.
7. **Preserve:** store the inputs, versions, outcomes, rationale, exceptions, unresolved
   uncertainty, owner, and next review date.

### Decision record

```text
Experiment / version / dates:
Authority actually exercised:
Exposure and spend:
Outcomes by signal stage:
Negative evidence and affected parties:
Guardrail or control events:
Decision: scale | revise | hold | narrow authority | stop
Rationale and evidence:
Next bounded change / unchanged caps:
Owner / next review date:
```

## Routing and stop conditions

- Route positioning, segment choice, channel economics, and experiment design through this
  skill.
- Route CRM reads or confirmed record changes to the appropriate CRM tool skill.
- Route external messaging and campaign operation to the named vendor/tool skill, whose
  mutation gates still apply. A strategy recommendation is not permission to send.
- Route AI-system risk tiering and organizational control design to `ai-governance`.
- Route legal interpretation to `legal-strategy` or qualified counsel.

Stop and report the evidence when the contract lacks an owner, the readiness gate blocks live
exposure, suppression cannot be enforced, a cap or kill path is absent, or the available metric
cannot support the requested scale decision. The useful result may be a research-only or
draft-only experiment; do not convert a missing decision into assumed authorization.
