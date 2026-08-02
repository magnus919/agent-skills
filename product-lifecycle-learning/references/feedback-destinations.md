# Feedback Destinations

Every lifecycle-learning cycle routes its outputs to downstream skills. This reference defines
the contract for each destination: what is routed, when, and in what format.

## Mandatory Destinations (every cycle)

These five destinations must receive learning outputs from every lifecycle cycle, regardless
of the decision outcome.

### 1. Roadmap (product-roadmapping-and-portfolio)

**What is routed:**
- Lifecycle decision (continue/improve/harvest/pivot/pause/retire) with evidence
- Updated assumptions that affect strategic bets
- Feature health assessment summary
- Gap between expected and observed outcomes

**When:** After the lifecycle decision is recorded.

**Format:** A brief evidence update — not a full roadmap reprioritization. The roadmap skill
owns the decision about what to do with the evidence.

**Relative link:** [../../product-roadmapping-and-portfolio/SKILL.md](../../product-roadmapping-and-portfolio/SKILL.md)

### 2. Analytics (product-analytics-and-measurement)

**What is routed:**
- Measurement gaps discovered during outcome review (metrics that could not be observed)
- Metric refinement needs (definitions that were ambiguous or misleading)
- New metrics that would have improved the assessment
- Data-quality issues that affected confidence

**When:** After gap analysis identifies measurement gaps.

**Format:** A measurement-gap report — not a tracking plan. The analytics skill owns tracking-plan
design and instrumentation.

**Relative link:** [../../product-analytics-and-measurement/SKILL.md](../../product-analytics-and-measurement/SKILL.md)

### 3. Adoption (product-adoption)

**What is routed:**
- Adoption pattern changes (activation, retention, feature discovery)
- Cohort-level insights from outcome review
- Behavior-change evidence: what worked and what did not
- Sustained-use signals that inform adoption strategy

**When:** When the outcome review surfaces adoption-relevant patterns.

**Format:** An adoption evidence update — not an adoption plan. The adoption skill owns plan design.

**Relative link:** [../../product-adoption/SKILL.md](../../product-adoption/SKILL.md)

### 4. Experimentation (product-experimentation)

**What is routed:**
- New hypotheses surfaced by the outcome review
- Assumptions that need experimental validation
- Experiment ideas for features that received Improve or Pivot decisions

**When:** When the assumption update surfaces testable hypotheses.

**Format:** Hypothesis briefs — not experiment designs. The experimentation skill owns method
selection and experiment design.

**Relative link:** [../../product-experimentation/SKILL.md](../../product-experimentation/SKILL.md)

### 5. Specifications (spec-driven-development)

**What is routed:**
- Acceptance criteria that were ambiguous, untestable, or missing
- Expected outcomes that were poorly specified (could not be compared against observations)
- Spec improvements for future features based on what was learned

**When:** When the outcome review reveals specification gaps.

**Format:** Spec-improvement recommendations — not revised specs. The specification skill owns
spec authoring.

**Relative link:** [../../spec-driven-development/SKILL.md](../../spec-driven-development/SKILL.md)

## Conditional Destinations

These two destinations receive learning outputs only when the decision or evidence triggers them.

### 6. Customer Success (conditional-customer-success)

**Trigger:** Retirement decision, or outcome review surfaces customer-impacting signals.

**What is routed:**
- Retirement communication plans for customer-facing execution
- Migration support coordination for affected accounts
- Customer treatment strategy during sunset (grace periods, data export, support commitments)
- Customer feedback signals that require account-level follow-up

**Format:** A customer-impact brief — not account-level action plans. The customer-success skill
owns account management and health scoring.

**Routing:** Prose reference to `conditional-customer-success` (skill not yet landed; same-wave
issue #192). When the skill lands, replace with a relative link.

### 7. Incident Learning (incident-learning)

**Trigger:** An incident occurred that is relevant to the feature's lifecycle assessment.

**What is routed:**
- Incident signals that should feed the incident-learning loop
- Feature reliability data relevant to post-incident analysis
- Operational patterns observed during the assessment window

**Format:** An incident-signal summary — not a postmortem or root-cause analysis. The
incident-learning skill owns postmortem methodology.

**Routing:** Prose reference to `incident-learning` (skill not yet landed; later milestone-2 issue).
Also routes to [../../site-reliability-engineering/SKILL.md](../../site-reliability-engineering/SKILL.md)
for operational reliability context.

## Routing Rules

1. **Every cycle routes to all five mandatory destinations.** The outputs may be brief ("no
   adoption-relevant patterns found") but must not be silent omissions.
2. **Learning artifacts are routed, not duplicated.** The retained learning record is the
   canonical artifact; each destination receives the relevant subset or a pointer to it.
3. **The destination skill owns the response.** Lifecycle-learning does not prescribe what the
   roadmap, analytics, adoption, experimentation, or specification skill should do with the
   evidence. It delivers evidence; the destination decides.
4. **Prose references become links when the target skill lands.** `conditional-customer-success`
   and `incident-learning` are prose references until their directories exist on main. At that
   point, replace with relative links.
