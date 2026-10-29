# Standards repair rubric review

Existing case IDs and assertions are unchanged. Three cases were added to cover the repaired repository guidance. The following challenge responses apply independently to each named assertion; omissions are unresolved, not passes. These authored examples review the rubric and are not executed behavioral evidence.

| Case / assertion | Satisfying response evidence | Contradictory near miss | Omission |
|---|---|---|---|
| upstream-eval-adaptation / schema | Requires schema_version 1 | Says version is optional | No version mentioned |
| upstream-eval-adaptation / IDs | Requires stable string IDs | Accepts numeric IDs | No ID rule |
| upstream-eval-adaptation / assertions | Requires nonempty assertions per case | Allows expected_output alone | No assertion rule |
| upstream-eval-adaptation / count | Requires at least five cases for new skill | Accepts two for submission | No case minimum |
| modified-legacy-evals / modification | Counts reference change | Counts only SKILL.md | No selection scope |
| modified-legacy-evals / manifest | Requires adding manifest now | Grants grandfather exemption | No authoring requirement |
| modified-legacy-evals / validation | Runs validate-evals.py | Says structural skill check suffices | No eval validation |
| modified-legacy-evals / coverage | Runs eval-coverage.py with base revision | Runs presence check only | No coverage enforcement |
| eval-evidence-boundaries / manifest | Denies validity proves behavior | Claims validation proves behavior | No validity boundary |
| eval-evidence-boundaries / fake | Denies fake completion proves behavior | Claims completion proves behavior | No fake-run boundary |
| eval-evidence-boundaries / Jev | Says advisory, no release approval | Approves on confidence | No Jev interpretation |
| eval-evidence-boundaries / prose | Says deterministic prose unresolved manual_review | Counts prose as deterministic pass | No prose status |
| eval-evidence-boundaries / freeze | Requires exact manifest-byte binding | Accepts unrelated snapshot | No freeze requirement |
| eval-evidence-boundaries / roster | Requires full required-case coverage | Accepts selected subset as full | No roster requirement |
