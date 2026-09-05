# Forecasting, cost, and schedule analysis

Use for "when will it finish?", date confidence, critical-path changes, or cost
exposure. S04 supports the need for credible schedule logic and schedule-risk
analysis. The model-selection procedure and calculator are original implementations.

## Match the model to the evidence

- Stable, dependent deliverables: inspect the network and remaining durations.
- Repeated comparable work: use historical throughput/flow forecasting through
  kanban-guru, preserving its assumptions and observation window.
- Novel research or unstable scope: offer scenarios and an early learning gate.
  Do not manufacture probability distributions from guesses.
- Material funding decisions: maintain actual cost plus estimate to complete;
  route model construction to financial-modeling.

Keep **baseline commitment**, **current forecast**, **required deadline**, and
**actual acceptance** separate. A forecast is conditional; a commitment is an
accountable decision. More decimal places do not improve weak inputs.

## Forecast review

Capture as-of date, remaining scope, done criteria, available capacity, exclusions,
model, assumptions, and sources. Review calendar effects, parallelism, scarce
skills, rework, supplier waits, and uncertainty correlations. If all paths depend
on the same test lab, they do not fail independently.

For probabilistic forecasts, state the sample, comparable conditions, simulation
method, confidence level, and events outside the model. Small or changing samples
are limitations, not proof of a precise percentile. Separate forecast calibration
from whether a target was politically accepted. Revisit after material scope or
capacity changes; compare forecast with actual delivery to learn.

For budgets, distinguish approved funding, actuals, committed but uninvoiced spend,
remaining estimate, and contingency. Avoid counting a purchase in both actuals and
commitments. Earned value is useful only with a credible time-phased cost baseline
and objective earning rules; ticket percentages are not automatically earned value.
Do not compare SPI to calendar-day delay. Record financial assumptions for review.

## Read-only schedule helper

Run from the skill root:

```sh
python3 scripts/schedule.py --input templates/schedule-example.json --json
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Input is a JSON object with `schema_version: 1`, `unit: "working_days"`, and
`tasks`: 1–500 objects. Each task has a unique non-empty `id`, nonnegative finite
`duration` (elapsed working days, not person-days), and `depends_on` list. Optional
`resource` identifies a single exclusive resource; it detects overlapping demand
but does not schedule it. Optional `deadline` is a nonnegative working-day offset
from project start. No dates, calendars, lags, partial progress, or unknown fields
are accepted. Use zero-duration tasks for milestones; they occupy no resource time.

The algorithm topologically sorts finish-to-start dependencies, performs a forward
pass for earliest times and a backward pass against the unconstrained finish for
float. It returns all zero-float task IDs (which may span multiple paths), finish
offset, deadline gap, and resource overlaps (first 100 pairs plus total count and truncation flag).
`deadline_gap = finish - deadline`;
positive is late. Float is relative to modeled finish, not the requested deadline.

This is a lower bound under precedence constraints and assumed durations. It is
not a resource-leveled schedule, Monte Carlo model, working-calendar converter,
critical-chain implementation, or completion promise. A resource warning means the
earliest dates conflict; resequence in the source plan and recalculate. Other
resource conflicts can exist even if no resource labels were supplied.

The script performs no network calls and mutates no files. JSON goes to stdout;
invalid input errors go to stderr with exit 2. Success is exit 0, including a late
forecast: lateness is data, not malformed input. Boundaries: 1 MB input, at most
500 tasks, finite aggregate duration no larger than one million working days.

## Interpretation example

Design takes 2 days. Build (3 days) and review preparation (1 day) depend on design.
Acceptance (1 day) requires both. Finish is day 6; design, build, and acceptance
have zero float; review preparation has 2 days float. If build and review preparation
need the same exclusive person, the apparent parallel schedule conflicts. Do not
report day 6 as a feasible commitment without resolving that conflict.

Complete when the forecast and its uncertainty are stated, contradictions are
visible, and the decision-maker understands what must change to meet the target.

For this small example, one exclusive specialist must do build and review
preparation serially: 2 + 3 + 1 + 1 = 7 working days. A second specialist restores
the dependency-only day 6; it cannot by itself achieve day 5. For a small network,
show such a feasible sequence explicitly; do not imply the helper leveled it.
