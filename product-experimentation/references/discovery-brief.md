# Discovery Brief — Product Experimentation

Bounded survey of existing experimentation concepts across the agent-skills catalog. Maps where terminology and guidance already live, defines the ownership boundary for the product-experimentation skill, and specifies routing rules to specialist skills.

## Existing Experimentation Guidance

### Opportunity-solution trees (product-methodology)

The `product-methodology` skill owns opportunity-solution trees through its opportunity-solution-trees reference. This framework connects customer needs to potential solutions without jumping to implementation. It identifies what problems to solve but does not prescribe how to test whether a chosen solution actually works.

**Boundary for this skill:** product-methodology selects the opportunity; product-experimentation tests the chosen solution. The output of an opportunity-solution tree (a prioritized opportunity) is an input to this skill's assumption-mapping step.

### Statistical methods (data-scientist)

The `data-scientist` skill owns statistical design: power analysis, sample-size calculation, estimator selection, hypothesis testing, Bayesian inference, causal identification strategies, and significance testing. It covers the full mathematical machinery of experimental design.

**Boundary for this skill:** product-experimentation frames the business question and selects the method (qualitative, prototype, operational, or quantitative). When the selected method is quantitative (A/B test or feature-flag experiment), it routes statistical design to data-scientist. This skill does not own power analysis, sample-size calculation, or estimator selection.

### Release flags and progressive delivery (release-engineering)

The `release-engineering` skill owns feature-flag lifecycle management: flag creation, guard, rollout, verification, removal, and expiry. Its feature-flag-lifecycle reference covers the full operational lifecycle.

**Boundary for this skill:** product-experimentation defines the experiment design that uses feature flags (allocation, exposure, guardrail metrics, decision criteria). Release-engineering owns the safe delivery mechanics: how the flag is created, how rollout is staged, how rollback is triggered. This skill routes "how do I deploy this experiment safely?" to release-engineering.

### UX research and usability testing (product-design-and-ux)

The `product-design-and-ux` skill owns usability studies: task-based observation, interaction evaluation, interface-contract validation. Its usability-testing-and-privacy reference covers protocol design and synthesis.

**Boundary for this skill:** product-design-and-ux owns interaction-level evaluation (can users complete this task?). Product-experimentation owns product-level evaluation (should we build this at all?). When an experiment's primary question is about usability rather than value or demand, route to product-design-and-ux.

### Pricing tests (financial-modeling)

The `financial-modeling` skill owns pricing strategy: elasticity, willingness-to-pay, price-tier experimentation, and packaging tests. Its pricing-strategy reference covers value-based and competition-based pricing.

**Boundary for this skill:** product-experimentation can frame a pricing hypothesis and select a method, but the domain-specific design of a pricing experiment (conjoint analysis, Van Westendorp, Gabor-Granger) belongs to financial-modeling. Route pricing-specific experiment design there.

## What This Skill Owns

Product-experimentation owns the **end-to-end experiment workflow** that no other skill covers:

1. **Assumption mapping** — surfacing, classifying, and prioritizing assumptions by risk, evidence strength, and testability.
2. **Hypothesis translation** — converting assumptions into falsifiable hypotheses with named variables and predicted effects.
3. **Method selection** — choosing among qualitative, prototype, operational, and quantitative methods based on the question, cost, and required rigor. Explicitly does not default to A/B testing.
4. **Instrumentation planning** — defining what metrics are tracked and that they are measurable (routing measurement contracts to product-analytics-and-measurement).
5. **Guardrail and ethics design** — mandatory safety metrics, ethical boundaries, stopping rules, and decision ownership that apply regardless of the statistical method.
6. **Decision synthesis** — combining statistical evidence, practical significance, guardrail evidence, qualitative signal, and reversibility into a ship/no-ship decision.
7. **Readout and learning** — recording experiment outcomes that update the roadmap, backlog, decision log, or lifecycle evidence.

## Routing Rules

| Concern | Route to | Method |
|---------|----------|--------|
| Statistical design (power, sample size, estimator) | data-scientist | Markdown link to [../data-scientist/SKILL.md](../data-scientist/SKILL.md) |
| Rollout mechanics (flags, canary, progressive delivery) | release-engineering | Markdown link to [../release-engineering/SKILL.md](../release-engineering/SKILL.md) |
| Measurement contracts (event taxonomy, tracking plan) | product-analytics-and-measurement | Prose reference only (skill not yet landed) |
| Roadmap decision impact | product-roadmapping-and-portfolio | Prose reference only (skill not yet landed) |
| Adoption evidence | product-adoption | Prose reference only (skill not yet landed) |
| Retained lifecycle learning | product-lifecycle-learning | Prose reference only (skill not yet landed) |

## Sources

The method ladder (qualitative interviews → prototypes → concierge tests → fake doors → feature flags → A/B tests) synthesizes established product practice from multiple sources including Teresa Torres (Continuous Discovery Habits), the Reforge experimentation program, and industry-standard product management literature. No single source is normative; the ordering by cost and rigor is the skill's own contribution.
