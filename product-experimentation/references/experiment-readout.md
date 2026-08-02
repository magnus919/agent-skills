# Experiment Readout

How to produce a decision-impact readout from an experiment that updates the product roadmap, decision log, or lifecycle evidence.

## Readout Structure

Every experiment readout must answer these questions:

1. **What was the hypothesis?** Restate the original hypothesis and the method used.
2. **What was the result?** Present the evidence — statistical, qualitative, and guardrail — in plain language.
3. **What did we decide?** The ship/no-ship decision and who made it.
4. **What changed as a result?** Concrete changes to the roadmap, backlog, decision log, or lifecycle evidence.
5. **What did we learn?** Generalized learning that applies beyond this specific experiment.

## Decision-Impact Field

Every readout must record at least one concrete change. The `decision-impact` field captures what changed and where:

| Impact type | Where it is recorded | Example |
|-------------|---------------------|---------|
| **Roadmap change** | Product roadmap (owned by product-roadmapping-and-portfolio) | "Promoted feature X to Q2 commitment based on positive experiment result" |
| **Backlog change** | Backlog (owned by product-methodology) | "Deprioritized feature Y based on null result; removed from backlog" |
| **Decision log entry** | Decision log (owned by product-methodology) | "Decided not to ship variant B despite positive result due to guardrail concern" |
| **Lifecycle evidence** | Lifecycle learning (owned by product-lifecycle-learning) | "Learned that users in segment Z do not respond to social-proof nudges" |
| **Adoption evidence** | Adoption tracking (owned by product-adoption) | "Confirmed that onboarding variant A improves week-1 retention by 8%" |

If the experiment produces no decision-impact — nothing changed as a result — the experiment was not worth running. Record this finding explicitly: "No change: experiment confirmed existing understanding with no new action."

## Routing Output

After recording the readout, route the relevant parts:

- Roadmap updates → product-roadmapping-and-portfolio
- Backlog changes → product-methodology (decision log template)
- Adoption evidence → product-adoption
- Lifecycle learning → product-lifecycle-learning
- Decision records → product-methodology (decision log)

## Readout Quality

A good readout:

- States the decision unambiguously — ship or no-ship, with who decided
- Names at least one concrete change that resulted
- Distinguishes statistical evidence from practical judgment
- Records uncertainty when the evidence is inconclusive
- Is written so a teammate who did not follow the experiment can understand what happened and why
