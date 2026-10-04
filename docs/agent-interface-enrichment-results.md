# Agent interface enrichment: delivery evidence

This change implements the five suggestions in [the preregistered
plan](agent-interface-enrichment-plan.md) across four existing skills. It adds
conditional guidance and reusable contracts, not a Composio integration or a
claim that dashboards are obsolete.

## Grounding and review

The owner reports map existing gaps, hypotheses, primary sources, source dates,
assertion challenges, and evidence limits:

- [Harness: discovery prerequisites and external bulk results](agent-interface-enrichment-harness.md)
- [API: an agent consumer's task path](agent-interface-enrichment-api.md)
- [UX: human delegation through an external agent](agent-interface-enrichment-ux.md)
- [Evals: mechanism-specific comparison and recurrence](agent-interface-enrichment-evals.md)

Root independently checked the MCP tool/resource/authorization documentation,
Anthropic discovery/code-execution/eval guidance, OpenAI tool-search/function
contracts, and Microsoft HAX guidance. Protocol capabilities were kept separate
from proposed completeness, durability, identity, and recovery contracts.
The conference talk remains orientation only; its mockup and unpublished vendor
comparisons are not validation.

Integration review corrected a missing cursor in the partial-artifact example,
the assumption that a fresh query restores an identical expired cohort, compound
eval assertions, unscoped code/transfer authority, and comparison wording that
would incorrectly require the treatment's result transport to stay identical.
A separate Luna reviewer found no material actionable findings at
`2d28be24c89d2d9ba825f4ed28f0326c841dd550`. Model review is advisory and is not
human adjudication or release-gate evidence.

## Matched response screen

The [five frozen tasks](evidence/agent-interface-2026-10-04/tasks.json) have SHA256
`914f9351968a5e0f9c84e43c9208debdcbf2349db4f5dfacbccaa14fe2c847ca`.
Fresh Luna agents used separate worktrees for baseline
`4e843ac9122dbf34a331031ca80d645e26769bf9` and candidate
`2d28be24c89d2d9ba825f4ed28f0326c841dd550`. Both received identical prompts,
resource access rules, and a 400–600 word target with a 700 word ceiling. Neither
was shown eval manifests, expected outcomes, or the comparison rubric.

Actual responses and provenance are retained in
[baseline](evidence/agent-interface-2026-10-04/baseline/provenance.json) and
[candidate](evidence/agent-interface-2026-10-04/candidate/provenance.json).
Root verified every recorded task, output, and read-resource hash against the
declared revisions. Provenance was normalized to relative paths for publication;
response bytes were preserved. Both suites produced all five final responses
without reported runtime errors.

**Scope and deviations:** one fresh session per condition handled the five tasks
in the same order, rather than a separate session per case. Cross-case context is
therefore a confounder. There was one response per case/condition, no stochastic
repeats, held-out run, tool execution, service mutation, user study, or production
sample. Exact backend model revision, provider sampling configuration, token
usage, monetary cost, and live tool latency were unavailable. The timestamps are
agent-reported suite timing, not performance measurements. Available resources
were the corresponding skill versions; the resources actually selected differed
and are recorded. The results assess design advice only.

The [version-blinded advisory review](evidence/agent-interface-2026-10-04/review.json)
uses the [frozen criteria](evidence/agent-interface-2026-10-04/rubric.json);
the [label mapping](evidence/agent-interface-2026-10-04/label-map.json) was withheld
until grading. Root checked the paired responses and every final excerpt.

| Case | Observed difference on the frozen criteria |
|---|---|
| Discovery | Both explain identifier ordering, status distinctions, safe recovery, and outcome comparison. Neither explicitly supplies the small/static alternative; that criterion remains not shown despite the candidate reference containing it. |
| Bulk artifacts | Both address completeness, identity accounting, protected provenance, and expiry. The candidate explicitly exposes bounded page/projection/filter/aggregate operations; the baseline's minimal aggregate output does not show how to inspect underlying records. |
| API consumer | Both provide the five required design details; no discriminating advantage was observed. |
| External delegation | Both handle human review, revocation, partial effects, and recovery. The candidate explicitly distinguishes customer, external host, and authenticated integration principals; the baseline shows per-service authority but omits external actor attribution. |
| Eval design | Both specify matched tasks, correctness/resource measures, adverse slices, and safety limits. The candidate explicitly calls for separate arms/ablations or bundle-only interpretation; the baseline identifies two changes without that separation. |

These are differences in one pair of design responses, not calibrated accuracy,
causal proof, or population performance estimates. The static-alternative gap
remains recorded; neither prompts nor criteria were changed to erase it.
The initial model reviewer over-credited three absent details. Its
[initial report](evidence/agent-interface-2026-10-04/review-initial.json) is retained;
root challenged those labels against actual text and the reviewer corrected them
to `not_shown` using the unchanged criteria. The final excerpts were checked as
verbatim response substrings. This illustrates why model-teacher labels require
review and do not constitute independent ground truth.

## Repository validation

- 183 canonical skills and 183 schema-valid eval manifests; coverage stayed 100%.
- Four changed skills: zero quality errors or warnings; all six added cases keep
  prior case IDs and assertions unchanged.
- 27 eval-validation tests and 41 existing harness script tests passed.
- Bundle, test-discovery, artifact, and generated catalog checks passed.
- Changed-skill selection included all four eligible skills, below the five-skill
  cap, with 54 expected manifest cases. This is selection evidence, not 54 model
  runs or verified semantic passes.
- The initial artifact-check attempt used a restricted sandbox/system Python and
  failed local HTTP fixtures and dependency checks. Rerunning with the repository
  virtualenv and permitted loopback fixture access passed.

Required PR checks and final-head review are recorded on the pull request.
The repository's fake-adapter smoke validates plumbing; prose assertions remain
manual review. Neither is evidence of behavioral uplift.

## Supported decision

The evidence supports publishing these bounded methodology extensions and
contracts with explicit tradeoffs, failure cases, and source boundaries.
Production success, usability benefit, total cost reduction, and cross-model
effectiveness remain unmeasured. A live implementation should use the new
comparison template and verify actual discovery, authorized artifact consumption,
pagination/identity correctness, expiry, revocation, and recovery before claiming
improvement or changing a production release gate.
