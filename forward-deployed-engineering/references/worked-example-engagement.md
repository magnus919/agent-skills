# Worked Example — Claims-Processing Cycle-Time Reduction

A synthetic engagement that calibrates the expected depth and evidence
labeling of the continuity artifacts. All people, numbers, and workflows are
illustrative; none reference a real customer, system, or deployment. Use this
to calibrate depth, not as a template substitute.

## Engagement charter (excerpt)

- **Engagement:** Claims-processing cycle-time reduction
- **Accountable technical lead:** Assigned engagement lead
- **Sponsor and decision authority:** Operations sponsor; privacy and security
  owners gate data access; service owner approves production change
- **Stakeholders and intended users:** Claims processors, workflow
  supervisors, downstream payment roles
- **Workflow and problem statement:** Elapsed time from claim submission to
  decision is the target workflow. The bottleneck is unvalidated; no
  particular stage is assumed to be the cause.
- **Desired outcome and baseline:** Reduce median cycle time by at least 10%
  against a recorded 30-day baseline, without breaching agreed quality,
  privacy, or compliance guardrails.
- **In scope:** Read-only workflow observation; baseline measurement; one
  bounded intervention with a tested hypothesis.
- **Out of scope:** Claims policy changes; unapproved production changes;
  external commitments.
- **Constraints:** Least-privilege access; approved change windows; retention
  and deletion rules for claims data.
- **Success measure and decision rule:** Proceed to the next stage only when
  the sponsor approves the metric definition, baseline, target, and guardrails
  with named evidence.
- **Stop conditions:** No recognizable problem; no workflow access; authority
  or constraints cannot be named; evidence fails; next action exceeds charter.
- **Sharing classification:** Private by default; reviewer and review date
  recorded before any external sharing.

## Ledger entries (excerpt)

| ID | Type | Statement | Evidence / source | Confidence | Owner | Due / review | Status |
|---|---|---|---|---|---|---|---|
| A-001 | Assumption | Median cycle time is a material outcome for the engagement. | Source fact: engagement request names cycle-time reduction as the objective | High | Sponsor | Before solution design | Open |
| D-001 | Decision | No solution design until the charter establishes problem, users, workflow, outcome, scope, authority, constraints, success measure, and stop conditions. | Decision: engagement design gate | High | Sponsor and lead | Ratified | Active |
| R-001 | Risk | Optimizing cycle time could degrade claim quality if guardrails are not explicit. | Inference: guardrails not yet defined | Medium | Operational risk owner | Before hypothesis approval | Open |

## Stage handoff — Build to Evaluate (excerpt)

- **Entry evidence:** Approved requirement; thin-slice implementation plan with
  owner; charter and ledger current.
- **Work performed:** Thin slice built and tested against acceptance criteria.
- **Source / evidence labels:** Each test result labeled engagement observation;
  design choices labeled decisions.
- **Observed result:** Slice passes technical acceptance; no production claim.
- **Unknowns:** Production data behavior; operator workflow interaction.
- **Decision rule:** Advance to Evaluate when representative evidence exists.
- **Decision:** Advance to Evaluate.
- **Receiving owner / acceptance condition:** Evaluation owner accepts the
  slice and baseline evidence.

## Evaluation and release decision (excerpt)

- **Baseline and decision thresholds:** Median 30-day cycle time; 10%
  reduction rule; quality guardrails.
- **Representative evidence:** Workflow sample spanning claim types, channels,
  and processor experience levels.
- **Adversarial or misuse evidence:** Boundary inputs, partial data, and
  worst-case queue conditions.
- **Known constraints and residual risks:** One segment shows 8% adoption;
  support owner not yet named.
- **Rollout / rollback prerequisites:** Authorized change window; recovery
  path tested; verification method named.
- **Release decision:** Conditional — approve with the adoption plan and
  support owner recorded as conditions.

## Adoption scorecard (excerpt)

- **Target workflow and users:** Claims processors in the two busiest teams.
- **Activation event:** First claim completed with the new path.
- **Adoption metric and decision rule:** 60% of eligible processors active
  within 30 days.
- **Outcome metric and decision rule:** Median cycle-time reduction >= 10%
  with quality guardrails intact.
- **Observed:** Team A 64% active; Team B 8% active.
- **Blockers recorded:** Team B workflow-fit and support evidence missing;
  incentive alignment unexamined.
- **Interpretation:** Adoption gap is unexplained; more training or features
  are not prescribed until access, fit, trust, support, and incentives are
  distinguished.

## Outcome measurement record (excerpt)

- **Observed result:** 12% median reduction against the 10% rule.
- **Uncertainty and confounders:** Two-week window; concurrent process
  changes; segment imbalance.
- **Decision:** Continue with the adoption intervention; re-measure at 60
  days.

## Productization record (excerpt)

- **Observed local result:** 12% reduction; adoption strong in one segment,
  weak in another.
- **Reuse hypothesis:** The intervention may transfer to similar
  intake-to-decision workflows.
- **Classification:** Configuration — provisional, local-only. A single
  positive outcome, weak adoption in one segment, and no willing receiving
  owner are insufficient evidence for a reusable-pattern or product-capability
  classification.
- **Reuse boundary:** Restricted to the current authorized context until
  repeated need, transferable constraints, support economics, and a receiving
  owner are evidenced.
- **Recommendation:** Candidate pattern for a pilot transfer; the receiving
  product owner must approve a requirement before implementation-planning is
  routed.
- **Decision authority and decision:** Pending; recommendation is not a
  decision.
- **Field learning returned to:** Internal platform and product owners, with
  the external-sharing gate applied.

## What this example is for

Calibrate the depth and evidence discipline expected of each artifact:
separate observations from inferences, apply the declared decision rule,
record missing evidence as bounded uncertainty, label every material entry,
and keep the classification and recommendation separate from any authorized
decision. Do not copy the illustrative numbers or the synthetic workflow into
a real engagement.
