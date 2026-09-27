# Semantic lint feedback evaluation

Use one record for one frozen evaluation. Report detector quality, repair
quality, and end-task outcomes separately. Do not use a detector's own output
to label its correctness or its repair as proof that the task succeeded.

## Study identity and units

- Task population, source repositories, period, and inclusion/exclusion rules:
- Independent unit (repository, change/PR, issue family, or other):
- Group key used to keep related methods, files, patches, and near-duplicates together:
- Source revision, worktree state, parser/graph revision, rule revision, and prompt hash:
- Provider-returned model/checkpoint identity, endpoint, adapter, decoding settings:
- Reviewer identities and blinding; adjudication and not-shown policy:
- Development / threshold-calibration / held-out partition IDs and overlap audit:
- Training-data or model-selection overlap provenance: documented / partial / unknown:
- Raw response, pass/chunk metadata, hashes, retention location, and redaction:

## Scope, freshness, and coverage

- Run type: local post-edit check / scoped graph scan / full declared scan:
- Exact target or path/diff scope and source state (including staged/unstaged):
- `selected`, `examined`, `completed`, `partial`, `skipped`, `failed`, and
  `unexamined` unit counts:
- Search cap, parser exclusions, unresolved graph edges, and chunk/pass limits:
- Cache state and cache-key inputs (source, graph neighbors, rule text, model,
  endpoint, adapter, and any other result-affecting setting):
- Freshness probe: which single input was changed, whether it invalidated reuse,
  and how the returned result was tied to the new state:
- Evidence that a policy-only change recomputed the decision from retained raw
  scores without labeling the cached model response as a fresh model call:
- Explicit stop condition when scope or evidence is incomplete:

Never report selected units as if they were completed. A partial, skipped,
failed, or unexamined unit cannot count as a clean pass. State which results are
fresh model calls and which are exact-input cache reuse.

## Frozen outcome labels and detector results

| Measure | Development | Held out | Uncertainty / slice notes |
|---|---:|---:|---|
| True positive / false positive / false negative / true negative | | | |
| Not shown / abstained / malformed / failed | | | |
| Complete-scope coverage | | | |
| False-pass and false-block rate | | | |
| Probability calibration / risk-coverage, if claimed | | | |
| Results by repository, change type, rule, language, and reviewer disagreement | | | |

- Representative sample versus separate risk-enriched challenge set:
- Baseline (deterministic tests, current review, or no semantic lint):
- Aggregation rule for multiple questions, gates, chunks, and repeated passes:
- Evidence that each probability is calibrated for this event and population;
  if absent, do not interpret products/maxima as calibrated joint confidence:
- Action-specific false-pass/false-block costs and meaningful margin:
- Threshold or `gate` policy selected on development/calibration only:
- Medium-confidence second-look lane: independent eligibility rule, reviewer
  outcome, added misses found, false alarms, coverage, and task-cost effect:

## Repair and end-task outcomes

| Outcome | Existing process | Semantic feedback candidate | Review/test evidence |
|---|---:|---:|---|
| Intended task completed | | | |
| Original issue fixed | | | |
| New regressions introduced | | | |
| Required tests pass | | | |
| Human review or intervention | | | |
| Retries / repair attempts | | | |
| End-to-end latency (cold / warm, p50 / p95) | | | |
| Total model and infrastructure cost | | | |

- Repair attempts allowed (default maximum: 2) and escalation condition:
- Independent verification of patch semantics and unchanged behavior:
- Regression set run after each accepted patch:
- Timing start/end boundary, concurrency, cache/warm state, retries, review,
  test execution, and final task outcome included or excluded:
- Paired unit, grouped uncertainty method, and interval for differences:
- Are the detection labels and repair outcomes based on the same examples? If so,
  explain the dependence and keep confirmatory quality claims on untouched groups:
- Frozen analysis plan, multiple-comparison policy, and any exploratory slices:

## Decision and evidence limits

- Current decision: advisory / investigate / continue shadow / propose gate:
- Accountable owner and rollback/reassessment trigger:
- What the study supports:
- What remains unknown or unmeasured:
- If a holdout miss changed the rule, prompt, threshold, adapter, or repair policy,
  identify a new untouched holdout before making a confirmatory claim:

