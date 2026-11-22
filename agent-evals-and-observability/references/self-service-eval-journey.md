# Worked self-service evaluation handoff

Use this example when a domain team needs to submit, rerun and interpret an evaluation without a platform engineer manually rebuilding the evidence. It connects the existing [eval plan](../templates/eval-plan.md), [dataset manifest](../templates/dataset-manifest.md), [run report](../templates/run-report.md) and [release gate](../templates/release-gate.md).

A support team wants to change refund routing. Its domain owner sets the rules and owns the release decision. The platform owner operates the evaluation service and attests to run integrity. The example uses synthetic, read-only cases and a disposable ledger fixture. A test run has no production credentials.

## Submit and run

1. The domain owner freezes the candidate and baseline configuration, dataset bytes and required case IDs, fixture/environment revision, grader revision and the hard authorization rule. Record content digests or immutable references in the plan and dataset manifest. Here the required cases are an eligible refund and a partner refund. The partner case needs a trace showing who was authorized to approve it.
2. The platform accepts the submission and returns an immutable input reference and a run ID. It isolates each attempt's fixtures and result publication. Record the originating run and attempt in every result, along with the actual resolved input reference. A status such as queued or completed describes execution.
3. A rerun pins the same inputs and starts with a clean fixture. A change in inputs creates a separate comparison. Before accepting a retry result, verify its run and attempt association, resolved inputs, and complete required case roster against the submission. Treat a matching display name or version label as insufficient proof of identical inputs.
4. The platform publishes the run report with separate entries for execution status, input and roster verification, and decision evidence. State which evidence is missing, stale, inaccessible or invalid; identify the affected cases. Report privacy limits without copying restricted traces. Store any restricted evidence with its authorized domain custodian and defined retention.

## Decide and recover

| Situation | Report and recovery | Decision responsibility |
|---|---|---|
| Clean run and clean rerun agree | Attach the verified inputs, eligible-case results and trace references. Compare under the frozen rubric. | Domain owner reviews the evidence and records disposition. |
| Runner unavailable | Report a timeout or blocked run and which cases did not complete. The platform owner schedules a retry with pinned inputs or follows an approved equivalent evidence path. | Domain owner holds the release if required evidence is missing. |
| Retry returns an older fixture under the expected dataset label | Mark the result association invalid when the resolved input differs. Keep the receipt for diagnosis and request a clean rerun. | Domain owner cannot count these results toward the gate. |
| Partner trace is unavailable | Report execution and trace coverage separately and mark the hard authorization rule unassessed for that case. Name the custodian and approved means to obtain admissible evidence. | Domain owner holds while the rule remains unverified. |

Use the [platform product evidence contract](../../platform-engineering/references/platform-product-evidence.md) for service ownership, support paths and SLOs. For an adoption pilot, observe the time to first valid report, reproducible rerun completion and reviewer time spent reconstructing evidence. Use [product discovery](../../product-discovery/SKILL.md) when the owning team still needs to find where users get stuck.

## Pilot evidence and limits

A local single-operator exercise ran four synthetic outcomes through two contracts on the same versioned case roster: the existing template fields applied directly with version and roster checks, and those same checks with an explicit frozen-input binding. Clean and repeated runs produced the same review-ready disposition. Both contracts held for timeout and inaccessible trace. The same-label stale result was accepted for domain review by the version-only implementation and held when the additional binding detected different input bytes. This isolates the handoff this example adds. A baseline implementer can already choose stronger provenance checks. The exercise did not measure adoption, operator performance or release effectiveness. No real partner traces or production credentials were used.

American Express's evaluation product role describes shared workflows, adoption and domain release ownership. ServiceNow/Moveworks's evaluation platform role describes versioning, isolation and harness reliability. These are examples of role scope. [American Express requisition](https://egug.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/26016060) · [ServiceNow/Moveworks requisition](https://jobs.smartrecruiters.com/ServiceNow/744000139369551-senior-machine-learning-engineer-agentic-systems-moveworks)
