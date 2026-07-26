# Dashboard Engineering

Build dashboards to support a named audience and decision. Do not begin with a panel inventory.

## Define the dashboard contract

Record:

- audience and operational decision;
- service or resource scope and owner;
- method: RED, USE, Golden Signals, SLO/error budget, business process, or another declared model;
- expected time horizon, refresh need, and incident workflow;
- data sources and query languages;
- drill-down destinations and access expectations;
- authoritative owner: UI/API, file, Terraform, Git Sync, Operator, or another workflow.

Use `site-reliability-engineering` to define SLOs, page-worthiness, and reliability policy. This reference implements the resulting view in Grafana.

## Design the investigation path

Prefer an overview-to-detail flow:

1. User impact or objective status.
2. Traffic, errors, latency, and saturation appropriate to the system.
3. Scope breakdowns that distinguish widespread from localized impact.
4. Correlated infrastructure or dependency evidence.
5. Links to deeper dashboards, Explore, logs, traces, profiles, runbooks, and change records.

Avoid hard universal panel counts. Review cognitive load, screen size, query fan-out, refresh rate, and whether every panel answers a distinct question.

## Query correctness

Before styling a panel:

1. Run the query in Explore or the data source's native query surface over a representative time range.
2. Confirm metric/log/trace semantics, counter versus gauge behavior, histogram boundaries, sampling, missing data, and time zone.
3. Verify aggregation and denominator. A cumulative error count is not an error rate; averaging histogram buckets is not a latency distribution.
4. Inspect returned labels and series count. Raw paths, request IDs, user IDs, unbounded hostnames, or other high-cardinality values should not become variables, repeated panels, legends, or alert dimensions without a bound.
5. Compare query interval, minimum interval, step, resolution, and refresh rate with source resolution and retention.
6. State the limitation if real data-source access is unavailable. Do not manufacture a final query from a metric name alone.

## Variables and repetition

- Use variables to reduce duplication and preserve a stable dashboard UID.
- Give useful defaults and an explicit All behavior; avoid an unbounded All expansion.
- Test chained variables, URL encoding, multi-value queries, permissions, and empty selections.
- Repeat rows or panels only over bounded, actionable dimensions. Estimate resulting panel/query count.
- Preserve variables and time range in links when the destination understands them; avoid leaking sensitive values in URLs.

## Visualization semantics

- Choose a panel that matches the decision: time series for change, stat/gauge for a bounded current value, table for exact ranked detail, state timeline for transitions, heatmap or histogram view for distributions.
- Set explicit units, decimals, axes, legends, and null behavior. Compare like with like; normalize when capacity differs.
- Derive thresholds from an SLO, capacity limit, safety boundary, or observed baseline. Do not invent red/yellow/green cutoffs because they look plausible.
- Be cautious with stacking, dual axes, truncated axes, interpolation across gaps, transformations, and calculated fields. Each can conceal source behavior.
- Transformations run in order on prior output. Validate raw query frames and each transformation stage.

## Context and reuse

- Add panel descriptions for source, formula, units, owner, and interpretation where not obvious.
- Use annotations for deploys, incidents, configuration changes, or relevant business events.
- Use dashboard, panel, and data links for directed investigation.
- Use library panels only when shared ownership and synchronized change are desired. Review the blast radius before changing one.
- Preserve stable UIDs for durable links. Do not reuse a UID or duplicate a title in the same folder without reconciling existing resources.
- Review dashboard version history before overwrite or rollback; version history does not replace an external source of truth.

## Accessibility and readability

- Do not use color as the only carrier of status. Pair it with text, shape, thresholds, labels, or annotations.
- Use sufficient contrast, legible text, clear titles, consistent units, and non-color status labels.
- Avoid dense legends, flashing behavior, unnecessary animation, and refresh rates that prevent reading or interaction.
- Check keyboard access, focus visibility, zoom/reflow, and screen-reader output in the supported environment when accessibility is an acceptance criterion. Use `web-accessibility` for formal WCAG/assistive-technology work.
- Test a color-vision-deficiency simulation when color encodes categories or severity.

## Review and verification

Verify:

- representative normal, degraded, no-data, delayed-data, and query-error states;
- variables and links with encoded/multi-value selections;
- units, axes, thresholds, legends, and time zone;
- query count, latency, cardinality, and data-source load at expected concurrency;
- intended viewer permissions and lower-privilege denial where relevant;
- persistence through the authoritative reconciliation path;
- accessibility/readability checks required by the audience.

Call the dashboard complete only when it supports the declared decision with validated data and an explicit drill-down or recovery path.
