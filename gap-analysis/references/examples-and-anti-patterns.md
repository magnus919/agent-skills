# Examples and Anti-Patterns

The examples below are hypothetical teaching examples, not observed case studies.

## Capability example

**Question:** Can the incident team restore the payment service within the stated recovery objective?

**Current evidence:** Two tabletop exercises restored service in 75 and 110 minutes; the target is 60 minutes; the runbook has no tested dependency fallback. **Gap:** recovery performance and tested fallback capability. **Cause hypothesis:** the fallback path is unowned and unexercised, not simply “people need training.” **Priority:** high because the consequence is material and evidence is direct. **Closure:** two representative exercises restore within 60 minutes, with named owner and captured logs.

## Process example

**Question:** Does every high-risk model change receive review before release?

Current records show review for 8 of 12 changes, but the target is all changes meeting the defined risk trigger. The gap is a missing or unreliable control path. Possible causes include trigger ambiguity, workflow bypass, and capacity. Do not prescribe training until those causes are tested. The artifact is a requirement-to-record matrix with exceptions and a re-test sample.

## Compliance/readiness example

A launch checklist says “security complete,” but the evidence is a design review and no production-boundary test. The correct state is **implemented but unproven**, not ready. The next action is a named boundary test with acceptance criteria, not a green checkmark.

## Research-evidence example

A review finds studies that estimate an effect, but samples exclude the population affected by the decision and results are inconsistent. Record the gap as “not the right information” and “inconsistent,” state the decision consequence, and propose evidence that includes the relevant population and a design capable of resolving the uncertainty. “More studies” is not an adequate action.

## Common anti-patterns

1. **Vague target:** “Become best in class.” Replace it with an outcome, requirement, measure, horizon, and authority.
2. **Gap-as-cause:** “Lack of training” inferred from poor results. Test process, tooling, incentives, knowledge, and ownership alternatives.
3. **Score theater:** 2.7/5 with no anchors or evidence. Use anchored states or publish the scale and uncertainty.
4. **Evidence laundering:** an interview opinion becomes a fact. Label source type and corroborate when stakes warrant.
5. **Benchmark mismatch:** compare different populations, periods, denominators, or operating modes. Normalize or state the limitation.
6. **Action closure:** a policy is published, so the gap is closed. Require observed adoption or outcome evidence.
7. **Compliance overclaim:** a checklist becomes a legal conclusion. Preserve the requirement source and route interpretation.
8. **Single-template thinking:** use one matrix for capability, readiness, and research without changing the target/evidence fields. Select a variant and link related registers.

## Stakeholder review prompts

Ask the sponsor to challenge the target, operators to challenge the current-state evidence, affected people to challenge consequence and burden, and the accountable owner to challenge feasibility and closure evidence. Record disagreements; consensus is not evidence.
