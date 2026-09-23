# Performance optimization record

## Journey and decision

- User population / owner:
- Start → usable end event:
- Workload and affected slice:
- Primary metric, unit, target, minimum practical gain:
- Correctness and resource countermetrics:

## Baseline and diagnosis

- Field source, period, build, sample count, distribution, exclusions:
- Lab fixture, command, environment, warmup, repetitions, raw evidence link:
- A/A or stability check (ordinary spread, false alarms, failures/timeouts):
- Trace/profile and bottleneck evidence:
- Measurement gaps, overhead, confounders:

## Experiment

- Hypothesis and predicted mechanism:
- Change and scope:
- Reversible path / rollback target:
- Baseline result (raw runs, summary):
- Candidate result (raw runs, summary):
- Failed, timed-out, and incomplete attempts (counts, rates, timeout rule):
- Absolute and relative difference; uncertainty:
- Comparison design and practical threshold (blocks/interleaving, minimum gain, ordinary noise):
- Correctness and countermetric result:
- Decision: supported in lab / unsupported / inconclusive; reason:
- Proxy calibration domain, improvement/regression examples, exceptions, and field-outcome relationship (or why diagnostic only):

## Review and field check

- Reviewer and accountable owner:
- Rollout scope, success/abort thresholds, observation window:
- Field result by build/platform/slice, with evidence link:
- Cohort, workload/traffic, and time-window matching; assignment and exclusions:
- Decision: field verified / reverted / pending; reason:
- Ratchet stability evidence, threshold vs noise and practical gain, fixture/threshold refresh plan:
- Regression guard and flag cleanup:
- Next bottleneck or stop reason:
