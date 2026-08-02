# Epistemic Discipline

Every claim in a product-lifecycle-learning output is classified into exactly one of four
epistemic categories. These categories are never conflated. A comparison is not an observation.
An inference is not a fact. An uncertain claim is not dressed up as a certain one.

## The Four Categories

### Expected

What was intended, predicted, or hypothesized before the feature launched.

**Source:** Specification, roadmap brief, experiment hypothesis, launch document, acceptance criteria.

**Characteristics:**
- States a prediction: "we expected X to happen"
- Has a reference to the source artifact (spec, roadmap, experiment brief)
- Is falsifiable: it can be compared against observed data
- May include a target threshold or range

**Examples:**
- "We expected activation to reach 60% within 30 days of launch."
- "The hypothesis was that the redesigned checkout would increase conversion by at least 5 percentage points."
- "Engineering estimated p99 latency would stay under 200ms under projected load."

### Observed

What actually happened, measured from data collected after launch.

**Source:** Analytics systems, adoption metrics, operational monitoring, user feedback, support data.

**Characteristics:**
- States a measurement: "we observed X"
- Includes a confidence interval or precision estimate when available
- Names the measurement source and window
- Is reproducible: another observer with the same data would see the same thing
- Acknowledges missing or low-quality data explicitly

**Examples:**
- "Activation reached 43% at 30 days (95% CI: 39-47%, measured by Mixpanel activation funnel, N=12,400)."
- "P99 latency averaged 180ms during weekdays and 310ms during weekend peaks (source: Datadog, 90-day window)."
- "Support ticket volume for the feature was 14 tickets/week during the first month, declining to 3/week in month three."

### Uncertain

What is ambiguous, noisy, contested, or genuinely unknown.

**Source:** Confidence intervals that span decision boundaries, conflicting signals from different
sources, data-quality problems, external confounds, small sample sizes, early-stage data.

**Characteristics:**
- Names the specific uncertainty: "we cannot determine X because Y"
- Quantifies the uncertainty when possible (confidence interval, sample size, measurement error)
- Does not pretend certainty when it does not exist
- Distinguishes between aleatory uncertainty (inherent randomness) and epistemic uncertainty (we
  could know with better data)

**Examples:**
- "Attribution is confounded by a simultaneous pricing change; we cannot isolate the feature's effect on retention."
- "The confidence interval for conversion lift spans -1.2% to +4.8%, which crosses zero — the direction of effect is uncertain."
- "Only 3 enterprise customers have adopted the feature so far; the sample is too small to draw conclusions about enterprise adoption patterns."
- "User satisfaction scores improved for power users but worsened for casual users; the aggregate masks opposite effects in different segments."

### Inferred

What is concluded from the evidence, with reasoning made explicit.

**Source:** Comparison of expected and observed, gap analysis, assumption testing, domain expertise.

**Characteristics:**
- States a conclusion: "we infer that X"
- Is supported by evidence from the other three categories
- Makes the reasoning chain explicit: "because A (observed) and B (expected), we infer C"
- Is tagged with the strength of the inference: strong, moderate, tentative
- Is open to revision by new evidence

**Examples:**
- "We infer that the onboarding redesign did not reduce time-to-value as hypothesized, based on the gap between expected activation (60%) and observed activation (43%). The pricing-change confound means this inference is tentative — we cannot rule out an external cause."
- "We infer that the feature addressed a real need for the mid-market segment (strong inference: adoption exceeded expectations in that cohort and qualitative feedback was uniformly positive)."
- "We infer that the feature's value proposition was unclear to enterprise users, based on the combination of low enterprise adoption, high bounce rate on the feature landing page, and support questions about what the feature does."

## Field Guide: Classifying Claims

When writing or reviewing a lifecycle-learning artifact, classify every claim:

1. **Is it a prediction about what would happen?** → Expected
2. **Is it a measurement of what did happen?** → Observed
3. **Is it an acknowledgment of what we cannot determine?** → Uncertain
4. **Is it a conclusion drawn from the evidence?** → Inferred

If a claim does not fit cleanly into one category, it is likely conflating two categories and
should be split. "Adoption was low" conflates observation (the number) with inference (that the
number is low relative to expectations). Split into: "Observed: adoption was 12% at 90 days
(95% CI: 9-15%)" and "Inferred: this is below our 25% threshold for a healthy feature."

## Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| "The feature was successful." | Conflates observation and inference; no evidence cited | State observed outcomes, compare to expectations, then infer success/failure with reasoning |
| "Adoption was 43%." (without confidence interval or source) | Treats a point estimate as certain | Add confidence interval, measurement source, and window |
| "The data shows the feature is working." | Vague; no comparison to expected outcomes | Compare observed against expected; state what "working" means |
| "We think users like it." | Inference presented as fact without evidence chain | Classify as uncertain or inferred; cite supporting observations |
| "The null result proves there is no effect." | Confuses absence of evidence with evidence of absence | State that the effect, if any, is below the detectable threshold; report the minimum detectable effect |
