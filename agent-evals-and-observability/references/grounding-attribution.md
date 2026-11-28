# Claim grounding and retrieval/generation attribution

Evaluate grounded systems at claim level when a response can contain several factual assertions. The goal is to identify which claims are supported by the supplied evidence and which component failed.

## Claim record

For each sampled response, record a minimized claim identifier, claim text only when approved by the data contract, evidence span or source identifier, support status (`supported`, `contradicted`, `not supported`, or `not verifiable`), and reviewer/grader version. Keep source access and sensitive content under the dataset's access and retention controls.

## Attribution sequence

1. Check whether the retrieval set contains sufficient, authorized evidence for the claim.
2. If evidence is absent or irrelevant, classify a retrieval miss or authorization/filtering failure.
3. If evidence is present but the answer contradicts or invents beyond it, classify a generation/grounding failure.
4. If both retrieval and generation are inadequate, retain both labels and avoid forcing a single root cause.
5. If the source itself is stale, conflicting, or unavailable, mark the case inconclusive and record the source limitation.

### Batched authoring

For each finding, compare its attached evidence, the full request the
author received, and the rendered claims and citations. Determine whether
the source establishes the relationship between the named subject and the
reported result. Give separate verdicts for exact quote binding and factual
support. Two accurately cited fragments can still describe different events.

- If the source supports the relationship but the finding's evidence omits
  it, inspect how evidence was attached to that finding. Evidence present
  only in a neighboring record can explain how an author saw it without
  establishing a valid evidence link for the current finding.
- If the finding has sufficient evidence and the rendered text attaches
  the wrong result, inspect generation and citation binding. Restricting
  the author to one record can prevent evidence from leaking across rows.
  Missing support still needs to be attached upstream or treated as missing.
- Allow corroboration across passages when a verified reference joins
  them. Preserve scope and intent, and treat a nearby result as context
  unless it has its own support. Withhold an unsupported claim, including
  anonymous phrasing that would still imply the same unverified result.

Synthetic example. One passage introduces a study and its Orion team.
A later passage explicitly refers back to that study and records a planned
trial, while an adjacent item reports an unrelated team's completed trial.
The two Orion passages support the plan. An accurate quote from the
adjacent item still cannot support an Orion outcome.

Retrieval precision/recall, answer relevance, faithfulness, and claim factuality measure different properties. Do not average them into one quality claim without a declared decision rule. A fluent or semantically similar answer is not evidence of factual support.

## Required cases

Include at least one supported claim, an unsupported fluent claim, a retrieval miss, an answer that ignores retrieved evidence, an unauthorized document that must not be used, and a stale/conflicting source. Grade source authorization and side effects separately from answer quality.

## Accurate citations can still mislead

A supported sentence does not establish a supported recommendation. Check whether the answer drops material qualifications or contrary evidence (completeness), and whether the available evidence is strong and applicable enough for the recommended action (sufficiency). A narrow pilot may support a pilot result while failing to justify population-wide rollout. Keep these findings separate from faithfulness and from retrieval/generation attribution. Use the grounding-probe reference routed from SKILL.md when checks must run during a workflow or feed a linked decision record.
