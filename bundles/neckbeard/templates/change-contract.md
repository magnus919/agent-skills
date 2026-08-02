# Change Contract

> Fill this in at Framing (Stage 1). Keep it short. A contract that needs a page
> is hiding an ambiguity — surface it instead.

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
     named boundary (unit / integration / end-to-end / production). -->

## Declared verification target
<!-- The boundary the contract actually cares about. This is what "done" must be
     proven against. -->

## Decision: change warranted?
<!-- yes / no. If no, stop here and record the evidence for "no change needed." -->

## Skip reason

<!-- If no change is warranted (decision above is "no"), record why. Same
     semantics as the delivery packet group (e) skip-reason fields: a concrete
     reason why an expected action was skipped; silent omission is prohibited. -->

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
