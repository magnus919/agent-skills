# Bounded grounding probes

Use when a claim or recommendation affects a consequential answer, publication, release, or authority decision. Reuse the existing claim record, dataset access controls, grader specification, and release gate. This is a methodology pattern, not a production probe implementation.

## Three distinct questions

| Dimension | Examine | Decision-relevant near miss |
|---|---|---|
| Faithfulness | Does the cited span support the claim, including its scope? | The source reports a median; the claim calls it a guarantee. |
| Completeness | Are material qualifications or contrary findings needed to interpret the claim retained? | An accurate speedup quote drops the same report's doubled rework rate. |
| Sufficiency | Does the evidence meet the burden for this recommendation, population, environment, and authority? | A small supervised pilot is used to authorize unattended rollout. |

Completeness does not require reproducing the entire source. Test omissions that could change the decision. Sufficiency depends on the declared decision and risk, not a universal source count. Multiple citations to the same underlying study are not independent corroboration. Do not average a failed material dimension into a passing overall score.

## Placement and evidence

1. Before evaluation, name the supported decision, risk, permitted evidence, freshness requirements, material failure policy, human owner, and probe budget. Use existing task/trajectory contracts; do not invent a second gate.
2. After a claim or recommendation is formed, check it against authorized source spans plus relevant surrounding qualifications and available counterevidence. If policy makes this a prerequisite for publication/action, run before that boundary. A post-hoc check supplies diagnosis only; it cannot retroactively authorize an action.
3. Record claim and recommendation IDs, consulted evidence IDs/versions, known omitted sources with reasons, and visibility limits. Missing access means unknown, not supported. Do not fetch restricted material or retain raw content merely to fill a record.
4. Return a separate result for each dimension: `supported`, `contradicted`, or `insufficient_evidence`; use `error` for failed execution and `not_run` for checks not performed. Include rubric/evaluator version, evidence references, and a short observable rationale. These are findings, not calibrated probabilities or action permissions.
5. Connect findings to the existing release/authority disposition and owner. A material contradiction blocks the proposed recommendation pending correction; insufficient evidence, error, or unresolved disagreement holds that decision or narrows it only to a separately supported scope. Preserve uncertainty even if another dimension passes.

## Bounded repair and disagreement

Default to one repair-and-recheck cycle for the affected claim. A transient execution error may be retried once within the declared budget; repeated errors stop and escalate. Do not rerun until a desired verdict appears. Keep every attempt, the reason for retry, the old/new claim version, and which attempt supports the decision.

For judge disagreement, preserve each verdict and its evidence, mark the affected finding unresolved, and seek the designated reviewer. Do not majority-vote away material counterevidence. If no reviewer or required source is available, return hold/insufficient evidence with a next evidence step. Human labels must name their provenance and calibration limitations; model findings must not be relabeled human review.

## Workflow outcomes remain separate

An agent may close a ticket correctly according to its local checklist while creating repeated contacts or denying needed service. Record local completion and downstream outcome separately, with population, observation window, and measurement source. An unobserved or delayed outcome stays unknown. Existing offline-to-online metric mirrors govern extrapolation; citation probes do not measure business impact.

## Worked decision patterns (synthetic)

- A report states “handling time fell 20%” and “reopened cases doubled.” A recommendation quotes the first accurately and says deploy broadly. Faithfulness of the quote may be supported; completeness fails on omitted rework; sufficiency for broad rollout is insufficient. Hold broad rollout, retain the reported speedup, and investigate net resolution rather than deleting the favorable evidence.
- A supervised pilot with eight trained staff improves completion. All qualifications are accurately represented, but the recommendation grants unattended production access across every team. Faithfulness/completeness can be supported while sufficiency remains insufficient. Limit the recommendation to an appropriately authorized supervised test or hold, pending evidence about unattended operation.

These examples explain decisions; they are not measurements of the skill's effectiveness. Compare old/candidate outputs on frozen cases and preserve false alarms and unchanged dispositions as well as improvements.

## Source and status

Adapted as methodology from NIST's [Building Evaluation Probes into Agentic AI](https://www.nist.gov/programs-projects/building-evaluation-probes-agentic-ai), updated May 5, 2026; accessed 2026-10-08. The research demonstrator uses rubric-based LM judges and structured findings. Its existence does not establish judge accuracy, adversarial coverage, or an assurance standard. Challenge cases that test probe failures are distinct from probes embedded in ordinary workflows.
