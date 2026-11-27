# Evidence Standards

## Evidence Levels

| Level | Standard | Example |
|-------|----------|---------|
| **Primary** | Direct observation, original data, reproducible experiment | Test output showing a passing result |
| **Secondary** | Report from a credible source, cited with provenance | Quoting an API documentation reference |
| **Circumstantial** | Indirect evidence that suggests but doesn't prove | Logs showing the system was up, but not that it processed correctly |
| **Assertion** | Claim without supporting evidence | "The system should work" |

## Verification Rules

- Claims require evidence at the level specified by the criteria
- A primary-source criterion cannot be satisfied with secondary evidence
- Missing evidence for a criterion is a HOLD, not a FAIL
- Contradictory evidence (claim says X, evidence shows Y) is a FAIL

## Match the evidence to the claim

For the [saved settings journey](../../spec-driven-development/templates/FEATURE-MAP.md),
match each claim to the cheapest check that can actually falsify it:

| Claim | Evidence that can support it | Inadequate substitute |
|---|---|---|
| The interface shows the requested state | Screenshot or UI assertion from the exact running candidate and setup | An isolated mock or a screenshot of the wrong build |
| The setting persists | Exercise save, reopen the app with the same test profile, and read the value back independently | A screenshot taken before reopening |
| Save behavior is consistent across supported sequences | Generate representative valid sequences, assert the property, and retain seeds and failing traces for replay | One successful journey or examples selected after the fact |
| A consequential transition cannot violate a well-defined invariant | A checked model with explicit assumptions and a separate check that the implementation matches the relevant behavior | Treating a model proof as evidence that the integrated app works |

Use invariants and small models where the added coverage matters. A video,
property test, model check and human judgment can complement one another;
none silently expands the authority to expose a change.

## Uncertainty Handling

When evidence is insufficient:
1. Document what evidence is available
2. Document what evidence would be needed
3. Report as HOLD with a clear description of what would resolve the uncertainty

## Candidate changes and evidence reuse

Record candidate commit/content identity, acceptance contract ID/version/hash,
check procedure, relevant environment/fixture versions, execution time, result,
and durable evidence reference. Preserve old attempts as history, not standing
permission. A relevant code/content, contract, dependency/configuration, fixture,
or environment change invalidates the affected verdict. Identify that scope,
rerun affected checks, and issue a new verdict; document why any reused evidence
remains applicable. Missing fresh evidence is HOLD, not automatic PASS or a claim
that the new implementation failed. The record declares evidence; runtime state
integrity and independent review remain separate requirements.


## Verify the driver and maintain the coverage map

A project-local driver is itself a candidate. Before trusting its evidence,
launch a disposable instance with known fixture data and check that the driver
is addressing the expected build, profile, and state. Exercise one representative
journey end to end using the actual user entry point, independently read back
the effect where relevant, and confirm the evidence still resolves after removing
only the resources the run created. This proves the driver for that exercised
path, not coverage of every feature or deployment environment.

For maintenance, use the project's accepted [feature map](../../spec-driven-development/templates/FEATURE-MAP.md)
and source entry points to account for changed journeys. Check the applicable
paths against the running candidate. Distinguish these outcomes:

| Observation | Disposition |
|---|---|
| The application does what users expect, but the map names an old entry point | Correct map drift, with an observed path. |
| The actual user path works, but the driver controls the wrong instance or cannot reach it | Repair and re-exercise the driver; do not pass the unverified run. |
| A required fixture, permission, or target is missing | Report the attempted path and unmet prerequisite as blocked. |
| The actual user path disagrees with the accepted requirement | Report a product defect. Do not weaken the map, fixture, or oracle to get a pass. |

Example: a skills manager shows a healthy list but misses a tool-specific
installation. Seed a small known inventory across the supported locations and
compare the display with the expected roster by location. An empty result is
not success until you know the driver reached the correct location and completed
the read. A passing browser path does not cover a separate CLI path.

### Worked example: a disposable settings-to-export driver

A project already has a development launcher, an export fixture seeder and
a browser driver. Start with those commands. Allocate a new profile, port and
run directory per candidate. Bind the run to the requested build and confirm
the launcher serves the run-owned instance. Wait for the fixture's two known
rows to be readable in the UI. A successful process health probe while seeding
is still in progress leaves the driver unqualified.

Use the [mapped user journey](../../spec-driven-development/templates/FEATURE-MAP.md#example-settings-to-export).
Capture the save acknowledgement, reopen the same profile, then download and
parse the export outside the profile. Retain the build, target, setup and
command record with the observed values. Clean up only the run's process and
profile. Check that the retained evidence still opens afterward. A wrong build
or profile makes the run unsuitable for a product verdict. An inaccessible
required variant stays HOLD with its missing prerequisite.

For a before/after check, use equivalent isolated profiles and fixtures on both
revisions. Preserve the failing baseline, the candidate outcome and an unaffected
control path. If the baseline cannot run comparably, record the missing comparison
and report the candidate observation at its own scope.

During integration, an unchanged source patch can pick up a different export
serializer. If the new serializer drops a field, the earlier export verdict
no longer covers the landing combination. Rerun the affected download and
parsed-content checks on the intended combination and keep HOLD until evidence
arrives. An independent settings-only observation can carry forward if its
candidate, contract and runtime dependencies are shown unaffected. Required
checks still follow their current-head policy.

Inspired by Lauren Tan's pstack [Create a verification skill](https://github.com/cursor/plugins/blob/b7b93c36be9bcc36a74db438e0fd385d660bc559/pstack/skills/create-verification-skill/SKILL.md)
and [Maintain a verification skill](https://github.com/cursor/plugins/blob/b7b93c36be9bcc36a74db438e0fd385d660bc559/pstack/skills/maintain-verification-skill/SKILL.md).
[Rob Shocks' walkthrough](https://youtu.be/lUhXa8GiXns?t=375) illustrates the
skills-manager coverage failure; it does not establish full test coverage.
