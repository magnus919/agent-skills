# Worked coordination experiment: topology and reuse cost

Use the [coordination experiment](../templates/coordination-experiment.md) when a proposed split promises lower costs, more coverage or faster delivery. This synthetic case compares costs at a common quality threshold. Its figures illustrate a decision and are not measurements from a deployed system.

## Decision and comparison

A support team reviews incoming warranty claims and produces a recommendation for a human. One topology uses a single agent. The second assigns evidence retrieval and policy application to specialists, then integrates their work into one recommendation. Both use the same pinned policy, read-only tools, model revision and held-out roster of 200 claims. The accepted unit is one policy-correct, evidence-backed recommendation delivered on time. Count each claim once. Before running the comparison, require at least 190 accepted recommendations, zero unauthorized actions, and ten denial cases in the roster with an accepted recommendation and supporting evidence for every denial case. The decisive evidence is the integrated recommendation and its trace. A specialist finishing its part is an intermediate outcome.

Compare both variants independently on the same roster with clean state between runs. Preserve outputs, per-call usage, repeated context, handoffs and retries, reviewer time and failures. Keep cost-at-quality separate from a fixed-budget capability test. Compare the same decision horizon and operating scope. Track total setup and recurring costs as well as the cost attributable to this comparison.

| Cost for the same decision horizon | Single agent | Specialists, new components | Specialists, reusable components |
|---|---:|---:|---:|
| Setup and evaluation integration | $200 | $450 | $210 |
| Execution, including tools and repeated context | $240 | $230 | $260 |
| Coordination and integration during runs | $20 | $80 | $80 |
| Human review and governance | $340 | $220 | $220 |
| Total | $800 | $980 | $770 |
| Accepted recommendations | 192 | 194 | 194 |
| Cost per accepted recommendation | $4.17 | $5.05 | $3.97 |

Assume all three clear the stipulated quality and conduct gates in this illustration. With new components, specialists save $120 in review and governance but cost $180 more overall. Keep the single-agent baseline at that horizon if the two additional recommendations have no demonstrated incremental value. With reuse, a compatible connector and evaluation fixture avoid $240 in setup. Operation adds $30 per comparable cohort for the extra context carried by the shared component. Review and integration costs are assumed unchanged across the two specialist variants. Confirm capacity, authorization, version compatibility and regression evidence for the reused component. Charge its relevant support or transition costs when material and allocate shared costs consistently.

For a fresh one-cohort choice, with both setup costs still avoidable, specialists with verified reuse cost $30 less overall. For an existing single-agent deployment, the $200 already spent on setup is sunk. The next cohort costs $600 to continue or $770 to switch, including $210 in remaining specialist setup and $560 in recurring cost. Keep the baseline for that cohort. At the assumed $40 recurring saving per cohort, switching first saves money in the sixth cohort if setup is paid once and there are no additional transition costs. Include any actual switching cost and test the expected volume and review load over the decision horizon.

An additional $40 in recurring specialist context cost erases the recurring advantage. Reopen the decision when prerequisite components become available, expected volume or review load changes, or the old assumptions expire. Verify quality and authority again before switching. Rerun the denial slice when the shared policy component changes and keep the baseline as fallback during the comparison.

## Source and interpretation

Wharton–Accenture discusses how task similarity and shared context affect bundling and how reuse may change upfront and recurring costs. The report notes limited empirical evidence on the shape of complexity and integration costs. Use it to choose scenario inputs and falsifiable hypotheses. Apply local costs, observed quality and an explicit adoption boundary to the disposition. Route the decision and cost boundary to the [AI operating economics skill](../../ai-operating-economics/SKILL.md). [Wharton–Accenture report, pp. 6–8, 11, 17](https://knowledge.wharton.upenn.edu/wp-content/uploads/2026/11/Wharton%E2%80%93Accenture-Agentic-Cost-Framework-2026.pdf)
