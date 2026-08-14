# Evidence Ledger

> One per non-trivial run. Compact: a few lines per field, not a transcript. But
> complete enough that a reviewer can re-run any listed command and reproduce the
> observation.

## Change-request provenance

<!-- Where this change comes from. Same fields and semantics as the delivery
     packet section (a) and the change contract provenance section. -->

- **Change-request URL or number:** <!-- URL or tracker number -->
- **Source type:** <!-- issue / ticket / email / verbal -->
- **Repository:** <!-- repo path or URL -->
- **Base ref:** <!-- branch or ref the change is based on -->

## Intent
<!-- The user-visible problem + change contract in one or two sentences. -->

## Authority
<!-- explore / modify / publish / deploy / merge — which was granted. -->

## Inspected artifacts
<!-- Files, commits, test output, runtime output, docs actually read. With paths
     or identifiers. -->
- 

## Assumptions
<!-- Each unverified assumption, stated explicitly. -->
- 

## Alternatives rejected
<!-- Approaches considered and why each was not chosen. -->
- 

## Files changed
<!-- Every file modified, created, or deleted. -->
- 

## Commands / checks run
<!-- Exact commands or checks executed. -->
- 

## Observed outputs
<!-- What those commands actually returned (not what was expected). -->
- 

## Verification boundary
<!-- Which boundary each check covered: component / integration / end-to-end /
     production. Map each check to its boundary. -->
- 

## Unverified boundaries
<!-- What was NOT checked, and why. -->
- 

## Rollback / follow-up triggers
<!-- Conditions under which this change should be reverted or revisited. -->
- 

## Status
<!-- done (target exercised and passed) / done-with-gap (state the gap) /
     blocked (state the boundary) / no-change-needed (state the evidence). -->

## Skip reason

<!-- If no change was warranted (status above is no-change-needed), record why.
     Same semantics as the delivery packet group (e) skip-reason fields: a
     concrete reason why an expected action was skipped; silent omission is
     prohibited. -->

## Gate verdict

<!-- Framing-gate outcome for this run. Same structure and semantics as the
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
