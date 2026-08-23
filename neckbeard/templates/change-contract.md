# Change Contract

> Fill this in at Framing (Stage 1). Keep it short. A contract that needs a page
> is hiding an ambiguity — surface it instead. One standing exception: any
> issue or ticket body this run emits must be self-contained for a cold reader
> (see the Issue/ticket body section). Litmus test: could someone who found the
> body via search act on it without asking anyone anything?

## Change-request provenance

<!-- Where this change comes from. Same fields and semantics as the delivery
     packet section (a) and the evidence ledger provenance section. -->

- **Change-request URL or number:** <!-- URL or tracker number -->
- **Source type:** <!-- issue / ticket / email / verbal -->
- **Repository:** <!-- repo path or URL -->
- **Base ref:** <!-- branch or ref the change is based on -->

## Problem
<!-- The user-visible problem in one or two sentences. What is wrong or missing
     from the user's point of view, not the implementation's. -->

## Authority
<!-- One of: explore / modify / publish / deploy / merge. If unclear, write
     "explore (assumed)" and flag that confirmation is needed. -->

## Constraints
<!-- Platform, compatibility, performance, policy, license. The hard limits. -->

## Affected system boundary
<!-- What system/component this touches and where its edges are. -->

## Risks
<!-- What could go wrong. Blast radius. What else depends on this area. -->

## Non-goals
<!-- What this change will explicitly NOT do. -->

## Acceptance criteria
<!-- Observable conditions that mean "satisfied." Each should be checkable at a
     named boundary (unit / integration / end-to-end / production).
     At least one criterion must trace back to the Problem section above —
     it proves the change solves the requester's actual problem, not just
     that the build matches the spec. -->

## Declared verification target
<!-- The boundary the contract actually cares about. This is what "done" must be
     proven against. -->

## Decision: change warranted?
<!-- yes / no. If no, stop here and record the evidence for "no change needed." -->

## Skip reason

<!-- If no change is warranted (decision above is "no"), record why. Same
     semantics as the delivery packet group (e) skip-reason fields: a concrete
     reason why an expected action was skipped; silent omission is prohibited. -->

## Issue/ticket body (cold-reader requirement)

<!-- Applies to any issue or ticket body emitted from this run — a new tracker
     item or a substantive comment on the source request. The reader has none of
     this session's context and no access to the agent's local artifacts. A
     body that fails any item below is not ready to file: rewrite it before
     submission. Litmus test: could someone who found this issue via search act
     on it without asking anyone anything? -->

- **Background section:** names the investigation — tools used with links,
  date, scope, and a sketch of the method.
- **Complete inline evidence:** the full affected list with `file:line`
  references in the target repository. No samples-plus-"on request": anything
  promised for later must instead be included now.
- **Reproduction commands:** runnable by a stranger on a fresh checkout.
- **Acceptance criteria** as checkable checkboxes.
- **No agent-local paths or private-artifact references** in the public body
  (scratch directories, local evidence ledgers, delivery packets). If evidence
  lives only outside the repository, inline it.

## Gate verdict

<!-- Framing-gate outcome for this contract. Same structure and semantics as the
     delivery packet section (h) gate-verdict fields. -->

- **Gate identifier:** <!-- e.g. framing-gate -->
- **Verdict:** <!-- pass / conditional / blocked -->
- **Evidence:** <!-- path or reference to supporting evidence -->
- **Head SHA:** <!-- SHA at which the verdict was reached -->

## PR / CI status

<!-- Placeholders for delivery tracking. Same semantics as the delivery packet
     section (i) lifecycle fields. -->

- **PR number:** <!-- PR or review-submission number, filled at submission -->
- **CI status:** <!-- passing / failing / pending / not-applicable -->

## Release status

<!-- Release disposition. Same semantics as the delivery packet section (i)
     release-status field. -->
<!-- not-released / release-ready / released / not-applicable -->
