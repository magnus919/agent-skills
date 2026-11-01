# Review metrics: what to measure, and what will lie to you

Review is expensive, so it should be measured. But almost every metric a team
naturally reaches for measures activity rather than outcome, and every one of them
degrades the moment it becomes a target.

This file gives metrics that diagnose process problems, states how each is gamed,
and describes how to learn from a defect that escaped review.

## Ground rules

1. **Measure the process, never the person.** SmartBear's guidance is explicit that
   defects found in review should never appear in performance reports. The moment
   they do, reviewers stop finding defects and start finding nits.
2. **Cohort before comparing.** A team reviewing 40-line config changes and a team
   reviewing 800-line migrations will have different numbers for reasons that have
   nothing to do with skill. Compare within tier and size band.
3. **Use distributions, not averages.** Review latency is long-tailed; a mean is
   dominated by a handful of stale changes. Report medians and the 90th percentile.
4. **A metric without a decision is decoration.** Before adding one, write down what
   you would change if it moved.

## Metrics worth having

| Metric | Definition | What it diagnoses | How it gets gamed |
|---|---|---|---|
| Time to first response | Time from review request to first substantive reviewer reply | Queueing and reviewer availability | Auto-acknowledgements, "looking" comments |
| Review latency | Request to approval (or merge) | End-to-end friction, including author and CI time | Splitting work into trivially approvable pieces |
| Effective change size | Median added+deleted hand-written lines per review | Whether changes are reviewable at all | Artificial slicing that produces meaningless units |
| Risk-tier coverage | Share of T3/T4 changes with the required reviewer count | Whether sensitive changes get the scrutiny the policy claims | Mis-tiering — a change quietly classified T2 |
| Reviewer concentration | Share of reviews handled by the top reviewer, per area | Bus factor and knowledge silos | None serious; the honest fix is spreading review |
| Review depth proxy | Share of changes where a reviewer recorded at least one substantive finding or verified behavior | Whether review is read-only theatre | Nit-spam to satisfy "substantive" |
| Change failure rate | Share of deployed changes that cause degraded service or require remediation | The outcome review is supposed to influence | Narrow definitions of "failure"; reclassifying incidents |

Change failure rate and lead time are two of the DORA delivery metrics. Use them as
outcome signals with the usual caution: they are lagging, multi-causal, and easy to
narrow until they look good. Review is one control among many — tests, canaries,
feature flags, and rollback capability all move the same number.

## Metrics that mislead

| Metric | Why it misleads |
|---|---|
| Comments per change | Tracks change size, not review quality. At Google, comments per change peak around 1,250 lines and then fall. |
| Approval rate | Measures leniency and queue pressure. A high rate can mean a healthy codebase or an exhausted reviewer. |
| Reviews per reviewer per week | Rewards speed over attention and punishes deep review. |
| Percentage of changes with comments | Most changes at Google have no comments beyond the approval; treating this as a defect rate punishes appropriate approvals. |
| Lines reviewed | Rewards skimming. A reviewer who reads 2,000 lines badly beats one who reads 300 well. |
| Defects found in review | Incentivizes nit-picking and severity inflation; punishes reviewers whose authors write good code. |

## The one number worth defending

If a team tracks a single review metric, make it **time to first response**,
reported as a median and a 90th percentile. It is the metric that most directly
reflects whether review is blocking people, it is hard to fake without being
obvious, and it is actionable: it responds to reviewer rotation, on-call
scheduling, and explicit norms ("one business day maximum", Google's rule).

Pair it with **effective change size**, because a fast response to an unreviewable
change is not progress.

## Reviewing a defect that escaped

When a defect reaches production despite review, the useful question is not "who
approved this" but "which control should have caught it, and why didn't it". Work
through:

| Question | Why it matters |
|---|---|
| Which change introduced the defect? | Locates it in a review scope, with a tier |
| Was that line in the reviewed diff? | If not, this is a coverage problem, not a reviewer problem |
| Which defect class is it? | Determines whether review was the right control at all |
| Did the reviewer have the context to see it? | Understanding is the dominant review bottleneck |
| Was the evidence that would have caught it available? | E.g. a denial test, a boundary test, a load measurement |
| Was the change within the attention budget? | Oversized reviews predict missed findings |
| Did the tier require the reviewer who would have known? | Tiering and assignment, not effort |

Outcomes that are not blame:

- **Add the test that would have caught it.** Most escaped defects are cheaper to
  encode as a regression test than to prevent with more review.
- **Add a review question to the tier checklist** if the class recurs.
- **Change the tier or reviewer if the change should have had specialist eyes.**
- **Reduce the change size norm** if the defect came from an oversized review.

Defect escape analysis belongs with incident learning; keep the review-specific
part factual and short.

## Anti-patterns in measurement

- **The dashboard nobody acts on.** If a metric has been red for a quarter and
  nothing changed, delete it or change the decision it was supposed to inform.
- **Comparing teams.** Different codebases, tiers, and risk profiles make
  cross-team comparison meaningless and political. Compare a team to its own past,
  within cohorts.
- **Measuring only what is convenient.** Review latency is easy to collect because
  the tool records it; whether review found anything is hard. Convenience is not a
  reason to measure the wrong thing.
- **Publishing reviewer-level dashboards.** This is the fastest way to convert
  review into a compliance ritual.

## Minimum viable review health report

For a quarterly review of the review process, four lines are enough:

1. Median and p90 time to first response, by tier.
2. Median effective change size, and share of changes above the oversized band.
3. Share of T3/T4 changes with the required reviewer coverage.
4. Change failure rate, with the review-related escapes classified by defect class.

Anything more should answer a question someone actually asked.
