# Worked example: routing and cadence for a reporting workflow

An operations team uses supplier exception reports to decide which purchase orders to expedite. The operations lead must decide whether to pilot agent-assisted triage and how often to run it. Every cost, count, rate, and threshold below is synthetic. Use the [initiative evidence record](../templates/ai-initiative-evidence-record.md) to replace assumptions with local observations before changing the workflow.

## Compare routing at fixed demand

The unit is one eligible exception over a four-week period. Define acceptance as an accurate, decision-ready exception record delivered by the existing service deadline. Count each eligible exception once, even if it requires retries or manual fallback. Charge all attempts and review to the same cohort. Each option must accept at least 90 of 100 exceptions and pass the same critical-error check. Costs are in USD for the same period.

| Four-week scenario | Eligible | Accepted | Model | Tools, retrieval, telemetry | Human review and rework | Allocated setup, maintenance and governance | Total | Cost per accepted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current analyst workflow | 100 | 96 | $0 | $40 | $820 | $140 | $1,000 | $10.42 |
| Routed agent with analyst review | 100 | 92 | $40 | $80 | $300 | $180 | $600 | $6.52 |
| Routed agent under more exceptions | 100 | 84 | $40 | $80 | $660 | $180 | $960 | $11.43 |

Total divided by accepted outcomes gives the last column. When no outcome is accepted, unit cost is undefined. Record the zero count and investigate the failure before making a value claim. Model spend holds steady across the two routed scenarios. Review and rework raise total cost as acceptance falls. The stressed route costs less over the period than the analyst workflow, yet costs more per accepted exception and fails the quality floor. Check critical errors separately even when aggregate acceptance clears the floor.

For the base routed case, record a bounded pilot with analyst approval retained and the current workflow available as fallback. For the stressed case, constrain routing to the supported task classes or return to the current workflow. Before scale, measure each route's usage, reviewer time, acceptance and critical errors by task class. Review task volume, retry and fallback costs, allocation of shared services and transition costs with their owners. Classify any potential savings by how they could be realized.

## Find the cheap-path break-even point

To isolate routing, compare it with an already acceptable fixed-model path,
not only the prior manual workflow. For the same eligible task mix, let `B`
be fixed-path cost per attempted task, `R` shared router overhead on each
attempt, `C` all-in cost conditional on finishing on the cheap path, and `F`
all-in cost conditional on leaving it. Include spent cheap inference, the
second attempt, cold-cache reprocessing, tool duplication and reviewer time
in the relevant conditional path, not in both it and `R`. Let `p` be the
fraction of eligible attempts that finish on the cheap path. In this simple
two-path model, routed cost is `R + p*C + (1-p)*F`. If `F > C`, it beats
the fixed cost when `p > (R + F - B)/(F - C)`. A threshold at or above 100%
means no strict savings in this scenario; if path costs don't follow this
ordering, compare the actual totals instead.

Synthetic example: `B = $1.00`, `R = $0.05`, `C = $0.30`, `F = $1.25`.
Break-even is about 31.6%; at 25% cheap-path completion it costs about $1.06
per attempt; at 60%, $0.73. This cost screen assumes equal acceptance and
hard-control behavior. If acceptance differs, compare cohort totals divided
by actually accepted outcomes, keep the quality floor binding, and include
unresolved work in attempted costs. Use more paths if direct premium routing
and a premium retry have different costs. Test low-volume, cold-cache and
elevated-fallback scenarios before inferring budget savings.

See [LangChain's Open SWE example](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)
for why losing a prompt cache can change the economics of a mid-thread switch.

## Compare reporting cadence

Assume the base routed workflow meets the case quality floor. Compare four-week scheduling options over the same eligible population. Reports can repeat exceptions, so count unique material decisions changed in time to act. A material decision here means an analyst changed an expedite decision while the supplier could still act. Log overlapping reports, review minutes and which intervention the analyst would have made under the existing schedule. A reviewer can spend at most 120 minutes per period on this scheduling comparison.

| Cadence | Runs | Review minutes | Scheduling and review cost | Material decisions changed in time |
|---|---:|---:|---:|---:|
| Monthly | 1 | 30 | $60 | 1 |
| Weekly | 4 | 90 | $150 | 4 |
| Every business day | 20 | 240 | $360 | 4 |
| Event-triggered | 3 | 75 | $135 | 3 |

These are scheduling scenarios, with the fixed-demand workflow costs outside this comparison. Include any incremental setup, event detection, tool and monitoring expense in the applicable scenario. In this illustration, weekly costs $90 more than monthly for three additional timely decisions, or $30 per additional decision. Compared with weekly, daily costs $210 more, changes no further material decisions, and exceeds review capacity. Compared with event-triggered reporting, weekly costs $15 more for one additional timely decision and requires 15 more minutes of review.

If the operations lead can justify at least $30 per incremental timely decision against monthly and at least $15 for the last decision versus event-triggered, weekly is a candidate for a four-week pilot. Otherwise compare the remaining feasible options against the local value estimate. Track missed expedite windows and alert delay alongside review burden and spend. Keep analyst authority fixed. Revert to the existing schedule if critical errors arise, the review cap is breached, or the pilot fails to demonstrate decision value. Route demand, queue peaks and budget constraints to capacity-and-cost-engineering.

## Source and adaptation

Wharton–Accenture models how the task mix, work volume, model capability and deployment choices change cost. The activity-level scenario is described on pp. 10 and 16, with limits on p. 17. The worked figures, thresholds and outcomes above were created for this example. The report describes a cost floor for mature deployments, with some transformation, enablement and existing infrastructure costs outside its model. Add material local costs and validate incremental decision value separately. [Wharton–Accenture report](https://knowledge.wharton.upenn.edu/wp-content/uploads/2026/11/Wharton%E2%80%93Accenture-Agentic-Cost-Framework-2026.pdf)
