# Harness experiment decision

Decision: **defer adoption of the new harness** pending comparable runs and verification of checkout acceptance. This is a review recommendation; no rollout occurred. Keep the existing harness as the default and preserve both revisions for rollback.

## Recorded observations

| Case | Old harness | New harness | Recorded difference |
|---|---|---|---|
| checkout | rejected; 10 seconds | accepted; 4 seconds | Outcome changed; 6 seconds less elapsed time (60% lower, 2.5x elapsed-time ratio) |
| cost | 1 | 1 | No change; currency/unit unspecified |
| human interventions | 0 | 0 | No change |

These are supplied record observations, not independently verified checkout behavior. Evidence references are `supplied-baseline-report` and `supplied-candidate-report`; their underlying reports, execution traces, verifier results, and timestamps were not supplied. The accepted label does not establish that checkout completed at the user delivery surface.

The strongest supportable claim is: **In one supplied checkout record, the new harness in a different environment was recorded as accepted in 4 seconds, versus a rejected old-harness record in 10 seconds.** Do not claim that the harness caused a 60% speed improvement, higher general success, or readiness for adoption. Time to rejection and time to acceptance are different outcome paths, so this is not an established speedup for equivalent successful work.

## Comparability and uncertainty

Harness revisions are `old` and `new`. Model/configuration, taskset, authority, verifier, checkout case ID, and input hashes match as declared. Environment fingerprints differ: baseline `ba5285161ba6eed0085fb13784ce5c92f70ebc268b94fd66aa1d68a32884204d`; candidate `7b664c6f0733d13c3b75f16eb8704d90553bd0532a916f60df7ac1c5b10940b9`.

The bundled comparator exited 2 with `incompatible run fingerprints; comparison refused`. This refusal is a comparability guard, not evidence that either harness failed. Fingerprints are declarations whose underlying inputs have not been authenticated. There is one case per harness, no repetitions or held-out tasks, no budget/tool-set breakdown, no recovery evidence, and no authority challenge evidence. No recorded acceptance regression appears in this one case; broader regressions remain unknown.

## Bounded next experiment

Hypothesis: changing the harness from old to new improves verified checkout acceptance or latency when all other conditions are held fixed. A disconfirming outcome is failure to reproduce acceptance gains or a consequential regression under identical conditions; equal results would leave the claimed benefit unsupported.

1. An experiment owner designated by the team should inspect the underlying environment configurations and checkout reports. Identify the changed runtime, dependencies, services, initial state, or other factors without altering fingerprint values to bypass refusal.
2. Freeze one reproducible environment, actual initial task/workspace state, model/configuration, tools, authority, verifier, and time/cost budgets. Use the same acceptance oracle for both harness revisions, observing persisted checkout completion at the actual requested surface and rejecting a plausible failed or incomplete checkout.
3. Run three paired checkout attempts in clean isolated starting states, counterbalancing old/new execution order and recording every failure and unknown. Use stable replicate IDs and retain source configuration hashes, raw traces, timestamps, acceptance evidence, latency, cost, interventions, and unauthorized attempts.
4. Include one held-out checkout variant and one interruption/recovery challenge. Keep held-out results out of iterative tuning. If environment and harness must intentionally change together, use a separately framed combined-system experiment or a 2x2 design; this comparator does not support that attribution.
5. Stop after this bounded screen. Adopt only if verified checkout acceptance is reproducible without consequential authority/recovery regressions, and comparable results show a benefit relevant to the team. Otherwise defer or roll back the candidate; do not weaken acceptance to obtain a pass. This screen supports a local decision, not statistical generalization.

Restart/rollback: retain the old harness and pinned environment configuration as the default; revert a later candidate trial to those preserved revisions if acceptance, authority, or recovery checks fail. No deployment target or rollback mechanism was supplied, so production adoption requires the designated owner to identify that concrete path before mutation.

## Checks actually run and usability

Read the skill, verification/improvement reference, script contract, and experiment template. Executed the bundled read-only comparison against the unchanged input files. Its refusal worked as documented. The generic error omits the name and values of the mismatched fingerprint; manual record inspection was needed to identify the environment difference. No additional agent runs, external calls, or mutations were performed. Output artifacts are confined to this directory.
