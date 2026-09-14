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

Retrieval precision/recall, answer relevance, faithfulness, and claim factuality measure different properties. Do not average them into one quality claim without a declared decision rule. A fluent or semantically similar answer is not evidence of factual support.

## Required cases

Include at least one supported claim, an unsupported fluent claim, a retrieval miss, an answer that ignores retrieved evidence, an unauthorized document that must not be used, and a stale/conflicting source. Grade source authorization and side effects separately from answer quality.
