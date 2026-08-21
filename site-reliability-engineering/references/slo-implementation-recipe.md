# SLO Implementation Recipe

Use this reference when a team has no SLOs, has metrics but no shared objectives, or needs to turn an SLO discussion into an operating agreement. It complements `references/slo-sli-framework.md`; it does not replace its definitions or formulas.

## Source anchors

Synthesized from *The Site Reliability Workbook*, “Implementing SLOs,” “SLO Engineering Case Studies,” “Alerting on SLOs,” and “Example SLO Document,” and *Seeking SRE*, “The Art and Science of the Service-Level Objective,” “SRE as a Success Culture,” and “Using Incident Metrics to Improve SRE at Scale.”

## The bounded sequence

1. **Choose one service and identify its users.** Include direct users, downstream services, operators, and business processes. State what failure means to each.
2. **Map the important journeys.** Describe the request path, asynchronous path, data path, dependencies, and the point at which users experience success or failure.
3. **Select a small initial set of indicators.** Prefer a few customer-facing indicators for availability, latency, correctness, freshness, or durability. Do not begin by turning every metric into an SLO.
4. **Define good and bad events.** State valid events, exclusions, aggregation, data source, sampling, and measurement boundary. A formula without a measurement boundary is not an SLI.
5. **Measure the baseline.** Use a representative period and record gaps in instrumentation. A target should be feasible and meaningful, not an aspirational number copied from another service.
6. **Propose targets and windows.** Explain the user impact and expected error budget for each target. Use rolling windows when the decision needs a current operating signal; use calendar or contractual windows only when that is the real agreement.
7. **Review with stakeholders.** The product owner, service owner, support or customer-facing team, and reliability operator must be able to explain what the objective protects and what it will cause them to do.
8. **Define the policy before the first breach.** Specify what healthy, at-risk, and exhausted budget states change: release pace, reliability work, incident review, escalation, or scope.
9. **Alert on significant budget consumption.** Use multi-window burn-rate alerts and route pages only when the response is urgent and actionable. Use tickets or review queues for slower repair work.
10. **Run a review cycle.** Revisit targets when user expectations, architecture, traffic, dependencies, or product criticality changes. Record why the target changed and what evidence supported it.

## SLO review questions

- Would a user notice the measured failure, or is it only an internal proxy?
- Can the team take action when the SLO is violated or burning rapidly?
- Does the measurement include dependency and client-side effects that matter to the journey?
- Are exclusions hiding a failure the user still experiences?
- Does the error budget create enough signal before the service becomes unacceptable?
- Is the target tight enough to protect users but loose enough to permit justified change?
- What happens when the team cannot operate within the target and toil constraints?

## What to record

Every approved SLO should link to a declaration containing:

- user journey and service owner;
- SLI good-event definition and measurement boundary;
- data source, query, aggregation, and known blind spots;
- target, window, error budget, and review date;
- alert and escalation behavior;
- release and reliability-work policy;
- dependency treatment and exception process;
- evidence baseline and unresolved instrumentation gaps.

## SLO failure is a decision signal

Do not treat SLOs as a performance score or a punishment mechanism. A budget breach is evidence that the service needs reliability attention, reduced change risk, more capacity, a dependency intervention, an objective revision backed by new user evidence, or a scope decision. Repeatedly overriding the policy without recording the reason turns the SLO into decoration.

## Agent procedure

Load this recipe with `references/slo-sli-framework.md` and `templates/slo-declaration-template.md`. If the user has supplied no service, users, or measurement data, produce a discovery plan and mark assumptions rather than inventing targets.
