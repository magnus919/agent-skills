# Independent design review

Use this workflow before a phase gate when the design is consequential, uncertain,
crosses important system boundaries, or is difficult to explain from its written
record. Do not run the full review for every small change; select effort according
to risk, uncertainty, and reversibility.

## Prepare the review inputs

1. Freeze the candidate document and name the decision the review should support.
   Record its commit SHA or content hash and the relevant acceptance contract.
2. Select only the standards, project documents, and source areas needed to check
   the design. Read existing project instructions and source-of-truth documents
   first. Do not pass the drafting transcript, private reasoning, or an answer the
   document is supposed to make clear.
3. Where the runtime can create a separate reviewer context, verify the available
   tool schema and use it. Give the reviewer read-only access when supported.
   Record what context remains available, including project instructions, memory
   services, and shared filesystem state. A new agent name or model does not prove
   independence.
4. Record the files supplied with the helper:

   ```sh
   python3 scripts/review_input_manifest.py \
     --target docs/designs/payment-retries.md \
     --context README.md \
     --context docs/architecture.md
   ```

   The JSON records relative paths, byte lengths, per-file SHA-256 values, and a
   stable bundle hash. It never copies file contents. It proves which paths and
   bytes were selected when it ran; it does not prove that a reviewer read them,
   that runtime access was limited to them, or that the review is correct. Rerun
   it after any selected input changes.

5. If the host cannot establish a separate context, either stop the independent
   review or perform a same-context self-review labeled as such. Do not describe
   it as independent.

## Review in two passes

### 1. Reader reconstruction

Before critique, ask the reviewer to state the design's intended outcome,
in-scope and out-of-scope behavior, material constraints, recorded decisions,
assumptions, and unresolved questions. Ask it to point to the supplied sections
or evidence that support each item.

Treat a material omission or incorrect paraphrase as a clarity or intent finding.
Do not treat it as evidence that the underlying architecture is wrong. The
author should add missing context only when a future implementer or reviewer
needs it, not solely to satisfy a reviewer who lacks a necessary source document.

### 2. Targeted critique

Choose the lenses that match the decision. Typical lenses include:

- **Need and simplicity:** Is the problem real? Can existing code or a smaller
  change solve it? Are proposed components and optimizations justified?
- **Architecture and failure:** Do data flows, ownership, error handling,
  security, capacity, and recovery make sense?
- **Compatibility and rollout:** What breaks for current users, stored data,
  interfaces, or partially deployed versions? Can the change be rolled back?
- **Codebase fit:** Does the proposal reuse maintained local capabilities and
  place new behavior at the right boundary?
- **Implementation readiness:** Are the named interfaces, changed files,
  decisions, and verification steps concrete enough for the approved scope?
- **Clarity and structure:** Can a new contributor follow the design, its
  terminology, assumptions, and alternatives?

Run reviewers in parallel only when their scopes are independent and the host
supports useful concurrency. Use the smallest relevant set; multiple reviewers
can repeat the same concern and consume time without adding coverage.
Set a time and round cap before the review starts. If a required reviewer fails,
or the cap is reached with blocking findings open, record the review as incomplete
and route the unresolved decision; do not repeat the loop indefinitely.

## Record findings and make decisions

Each finding should have a stable ID, severity, exact affected scope, the claim
under review, evidence available to the reviewer, the gap or contradiction, and
a proposed next action. Record reviewer completion separately from findings:

- `completed` with no findings means that reviewer returned a report with no
  issues in its scope.
- `not run` means the reviewer timed out, failed, lacked a required tool, or
  could not read required inputs. It is not a clean review.

An orchestrator should record the round cap and actual attempts. A missing result
does not become a clean report, and a retry must use the same declared limit.

For each finding, the author or accountable human should choose and record one
disposition:

- **Fix:** update the design or supporting evidence, then rerun the affected
  review on the new candidate.
- **Contest:** cite material evidence the reviewer could inspect. Disagreement
  alone is not evidence.
- **Escalate:** a required fact or authority is unavailable in the written
  record; ask its owner to decide or provide evidence.
- **Accept or defer:** document the risk, owner, due point, and the boundary
  before which it must be resolved. Do not let a deferred consequential decision
  silently pass its dependency gate.

Do not apply review suggestions automatically. A review can expose a question;
the authorized owner decides the answer. Preserve the original report and
candidate identity. Re-review the changed scope, and retain unaffected evidence
only when its applicability is justified. Use
`references/review-records.md` for follow-up ownership and backlog authority:
reviewers propose changes; the accountable orchestrator owns accept/defer/decline
and deduplication.

## Finish and route

Finish when the required reviewers completed on the current candidate, all
blocking findings have an evidence-backed disposition, and consequential open
decisions have owners and safe decision points. Report unresolved or unavailable
evidence as unresolved; do not call absence of findings proof of quality.

- For source-grounded maps of an existing subsystem, use
  [software-architecture-analysis](../../software-architecture-analysis/SKILL.md).
- For delivery dependencies, rollout, and rollback after approval, use
  [implementation-planning](../../implementation-planning/SKILL.md).
- For dataset, grader, or agent-trajectory evaluation design, use
  [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md).
- For execution and authorized PR delivery, use
  [verified-delivery](../../verified-delivery/SKILL.md).
