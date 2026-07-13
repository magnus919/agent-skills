# Incident Learning

## Make The Decision Now

After an incident, near miss, or escaped defect, decide what systemic condition allowed it and which engineering artifact must change: requirement, threat model, design constraint, test, review prompt, telemetry, dependency policy, release gate, or operational response.

## Learn Without Replaying Harm

- Preserve minimum necessary facts, timelines, affected boundaries, decisions, and evidence access controls.
- Separate trigger, enabling conditions, detection gap, response effectiveness, and customer impact. Avoid assigning blame in place of identifying a controllable condition.
- Fix the class of defect across comparable paths, not only the observed instance.
- Convert learning into an owned change with acceptance criteria and a verification method. Update the threat model if an assumption failed.
- For AI incidents, include prompt sources, retrieval corpus, model and policy versions, tool authorization, approvals, output handling, and data exposure without retaining unnecessary sensitive content.

## Evidence And Verification

Show the changed control in code, configuration, test, review process, or release evidence. Test the original failure mode and adjacent variants; record residual risk when reproduction is unsafe or access is unavailable. Use [verification-methodology](../../verification-methodology/SKILL.md) for verdicts rather than declaring learning complete from a meeting note.

## Misuse To Avoid

- Calling a root cause a single human mistake and leaving the system condition unchanged.
- Collecting unrestricted incident data that creates a second exposure.
- Adding a permanent control without an owner, effectiveness check, or review date.
