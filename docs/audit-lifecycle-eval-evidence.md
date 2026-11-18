# Recovery, migration, and incident eval evidence

The cases use synthetic observations. Each evidence contract binds the input
bytes and an authoritative source. Keep the run revision, case ID, reviewed
artifact, reviewer identity, and per-assertion provenance with the verdict.

| Case | Satisfying evidence | Contradiction to catch | Missing evidence |
|---|---|---|---|
| Recovery integrity | The verdict records the observed RTO pass, fingerprint failure, unverified data loss, and a blocked cutover. | Matching record counts are used to approve cutover despite the mismatched fingerprint. | A HOLD labels the risk without identifying the observed mismatch or unmeasured loss. |
| Migration parity | The decision preserves the source writer and calls for content reconciliation with a retry-safety test before cutover. | Equal counts are treated as parity and the target writer is switched. | The plan calls for another check without saying how retry duplication will be detected. |
| Incident follow-up | The acceptance test exercises the retry entry point with the freeze active and checks that nothing was submitted. The follow-up names release engineering as the owner. | An ordinary deployment path is tested and the retry path is declared fixed. | A task names the owner but supplies no observable exit criterion. |

Keep the classification at `not shown` for an assertion whose observation
is missing. Reproducing the case from its fixture demonstrates the evaluation
input. Claims about a successful recovery, cutover, or production control
require the corresponding external evidence.
